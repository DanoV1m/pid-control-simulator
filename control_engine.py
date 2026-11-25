from typing import Dict, Optional, Tuple
import numpy as np
from scipy import signal

def parse_coefficients(coeff_str: str) -> Optional[np.ndarray]:
    """Converts a comma-separated string of coefficients into a normalized NumPy array."""
    try:
        coeffs = [float(x.strip()) for x in coeff_str.split(",") if x.strip() != ""]
        if not coeffs:
            return None
        arr = np.array(coeffs, dtype=float)
        if not np.all(np.isfinite(arr)):
            return None
        arr = np.trim_zeros(arr, trim="f")
        return arr if len(arr) > 0 else np.array([0.0])
    except ValueError:
        return None


def poly_to_latex(coeffs: np.ndarray) -> str:
    """Converts polynomial coefficients into clean LaTeX notation."""
    terms = []
    degree = len(coeffs) - 1
    for i, c in enumerate(coeffs):
        power = degree - i
        if abs(c) < 1e-12:
            continue

        sign = " + " if c > 0 and terms else (" - " if c < 0 and terms else ("-" if c < 0 else ""))
        abs_c = abs(c)
        coeff_str = "" if (abs(abs_c - 1.0) < 1e-9 and power > 0) else f"{abs_c:g}"
        s_str = "" if power == 0 else ("s" if power == 1 else f"s^{{{power}}}")
        terms.append(f"{sign}{coeff_str}{s_str}")

    return "".join(terms) if terms else "0"


def compute_closed_loop_tf(
    num: np.ndarray, den: np.ndarray, kp: float, ki: float, kd: float
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Computes open-loop compensated L(s) = C(s)G(s) and closed-loop unity feedback T(s) = L(s) / (1 + L(s)).
    Handles pure PD / P when Ki is zero to avoid zero pole/zero cancellation at origin.
    """
    if abs(ki) < 1e-12:
        c_num = np.array([kd, kp], dtype=float)
        c_den = np.array([1.0], dtype=float)
    else:
        c_num = np.array([kd, kp, ki], dtype=float)
        c_den = np.array([1.0, 0.0], dtype=float)

    l_num = np.trim_zeros(np.polymul(c_num, num), trim="f")
    l_den = np.trim_zeros(np.polymul(c_den, den), trim="f")

    if len(l_num) == 0:
        l_num = np.array([0.0])
    if len(l_den) == 0:
        raise ValueError('Invalid plant denominator')

    cl_num = l_num.copy()
    cl_den = np.trim_zeros(np.polyadd(l_den, l_num), trim="f")
    if len(cl_den) == 0:
        raise ValueError('Singular feedback denominator')

    return cl_num, cl_den, l_num, l_den


def calculate_step_metrics(
    t: np.ndarray, y: np.ndarray, poles: np.ndarray, setpoint: float = 1.0, final_value: Optional[float] = None
) -> Dict[str, Optional[float]]:
    """Calculates comprehensive step response performance metrics."""
    is_stable = bool(np.all(np.real(poles) < 0.0))

    if not is_stable or len(y) == 0:
        return {
            "stable": False,
            "rise_time": None,
            "settling_time": None,
            "overshoot": None,
            "peak_val": None,
            "peak_time": None,
            "steady_state": None,
            "ess": None,
            "t_10": None,
            "t_90": None,
        }

    y_ss = float(final_value) if final_value is not None else float(y[-1])
    ess = abs(setpoint - y_ss)

    y_max = float(np.max(y))
    idx_max = int(np.argmax(y))
    t_peak = float(t[idx_max]) if idx_max < len(t) else None

    if abs(y_ss) > 1e-6 and y_ss > 0:
        overshoot = max(0.0, ((y_max - y_ss) / abs(y_ss)) * 100.0)
    else:
        overshoot = 0.0

    rise_time = None
    t_10 = None
    t_90 = None
    if y_ss > 1e-6:
        idx_10 = np.where(y >= 0.1 * y_ss)[0]
        idx_90 = np.where(y >= 0.9 * y_ss)[0]
        if len(idx_10) > 0 and len(idx_90) > 0 and idx_90[0] >= idx_10[0]:
            t_10 = float(t[idx_10[0]])
            t_90 = float(t[idx_90[0]])
            rise_time = float(t_90 - t_10)

    settling_time = None
    if abs(y_ss) > 1e-6:
        tolerance = 0.02 * abs(y_ss)
        outside_band = np.where(np.abs(y - y_ss) > tolerance)[0]
        if abs(float(y[-1]) - y_ss) > tolerance:
            settling_time = None
        elif len(outside_band) == 0:
            settling_time = 0.0
        elif outside_band[-1] < len(t) - 1:
            settling_time = float(t[outside_band[-1] + 1])

    return {
        "stable": True,
        "rise_time": rise_time,
        "settling_time": settling_time,
        "overshoot": overshoot,
        "peak_val": y_max,
        "peak_time": t_peak,
        "steady_state": y_ss,
        "ess": ess,
        "t_10": t_10,
        "t_90": t_90,
    }


def calculate_frequency_margins(l_sys: signal.TransferFunction) -> Dict[str, Optional[float]]:
    """Estimate the closest-to-zero signed margins at sampled crossings.
    Log-frequency interpolation; tangencies and out-of-band crossings are not guaranteed.
    A missing crossing is reported as None, not infinite stability margin.
    """
    empty = {"pm": None, "w_gc": None, "gm": None, "w_pc": None}
    try:
        logw = np.linspace(-3, 3, 2401)
        w = 10**logw
        _, mag, phase = signal.bode(l_sys, w=w)
        def crossings(values, target, other):
            for i in range(len(values)-1):
                a,b = values[i]-target,values[i+1]-target
                if not np.all(np.isfinite([a,b,other[i],other[i+1]])) or a==b:
                    continue
                if a*b<=0:
                    f = -a/(b-a)
                    yield float(10**(logw[i]+f*(logw[i+1]-logw[i]))), float(other[i]+f*(other[i+1]-other[i]))
        pm_candidates = [(float((p+360)%360-180), freq) for freq,p in crossings(mag,0,phase)]
        finite_phase=phase[np.isfinite(phase)]
        gm_candidates=[]
        if len(finite_phase):
            for k in range(int(np.floor((min(finite_phase)+180)/360)),int(np.ceil((max(finite_phase)+180)/360))+1):
                gm_candidates.extend([(-m,freq) for freq,m in crossings(phase,-180+360*k,mag)])
        pm,w_gc=min(pm_candidates,key=lambda x:abs(x[0])) if pm_candidates else (None,None)
        gm,w_pc=min(gm_candidates,key=lambda x:abs(x[0])) if gm_candidates else (None,None)
        return {"pm":pm,"w_gc":w_gc,"gm":gm,"w_pc":w_pc}
    except (ValueError, ArithmeticError):
        return empty


def dc_gain(num: np.ndarray, den: np.ndarray) -> Optional[float]:
    if den[-1] == 0:
        return None
    value = float(num[-1] / den[-1])
    return value if np.isfinite(value) else None

def root_locus_samples(num, den, gains):
    """Roots of D(s)+k N(s) for nonnegative gain samples."""
    result = []
    for gain in gains:
        if not np.isfinite(gain) or gain < 0:
            raise ValueError("Gain must be finite and nonnegative")
        characteristic = np.trim_zeros(np.polyadd(den, gain * np.asarray(num)), "f")
        if not len(characteristic):
            raise ValueError("Singular characteristic polynomial")
        result.append(np.roots(characteristic))
    return result


def nyquist_samples(num, den, omega):
    """Sample L(jw) and conjugate mirror; not a full Nyquist contour."""
    omega = np.asarray(omega, dtype=float)
    if np.any(omega <= 0) or not np.all(np.isfinite(omega)):
        raise ValueError("Frequencies must be positive and finite")
    with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
        response = np.polyval(num, 1j * omega) / np.polyval(den, 1j * omega)
    response = np.where(np.isfinite(response), response, np.nan + 1j * np.nan)
    return response, np.conjugate(response[::-1])

def simulate_saturated_pid(kp, ki, kd, tau, limit, dt=0.01, duration=10.0, anti_windup=True, reference=1.0):
    """Discrete PID on a unit-gain first-order plant; derivative on measurement.
    Exact zero-order-hold plant update, rectangular integral, conditional integration.
    """
    if not np.all(np.isfinite([kp, ki, kd, tau, limit, dt, duration, reference])):
        raise ValueError("All parameters must be finite")
    if min(kp,ki,kd) < 0 or min(tau,limit,dt,duration) <= 0 or duration/dt > 200000:
        raise ValueError("Invalid simulation parameters")
    t = np.arange(int(np.floor(duration/dt))+1)*dt
    y, u, integ = np.zeros_like(t), np.zeros_like(t), np.zeros_like(t)
    decay = np.exp(-dt/tau)
    integral = 0.0
    previous = 0.0
    for i in range(len(t)):
        error = reference-y[i]
        derivative = -(y[i]-previous)/dt
        candidate = integral+error*dt
        raw = kp*error+ki*candidate+kd*derivative
        if not anti_windup or abs(raw)<=limit or (raw>limit and error<0) or (raw<-limit and error>0):
            integral=candidate
        u[i]=np.clip(kp*error+ki*integral+kd*derivative,-limit,limit)
        integ[i]=integral
        previous=y[i]
        if i+1<len(t): y[i+1]=decay*y[i]+(1-decay)*u[i]
    return t,y,u,integ
