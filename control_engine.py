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
        l_den = np.array([1.0])

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
    """Calculates Gain Margin (GM) and Phase Margin (PM) from frequency response."""
    try:
        w = np.logspace(-3, 3, 1200)
        _, mag, phase = signal.bode(l_sys, w=w)

        # Gain Crossover Frequency (where magnitude crosses 0 dB)
        idx_gc = np.where(np.diff(np.sign(mag)))[0]
        pm, w_gc = None, None
        if len(idx_gc) > 0:
            i = idx_gc[0]
            w_gc = float(w[i])
            phase_at_gc = float(phase[i])
            pm = 180.0 + phase_at_gc
            while pm > 180.0:
                pm -= 360.0
            while pm < -180.0:
                pm += 360.0

        # Phase Crossover Frequency (where phase crosses -180 degrees)
        phase_shifted = phase - (-180.0)
        idx_pc = np.where(np.diff(np.sign(phase_shifted)))[0]
        gm, w_pc = None, None
        if len(idx_pc) > 0:
            i = idx_pc[0]
            w_pc = float(w[i])
            mag_at_pc = float(mag[i])
            gm = -mag_at_pc

        return {
            "pm": pm,
            "w_gc": w_gc,
            "gm": gm,
            "w_pc": w_pc,
        }
    except Exception:
        return {"pm": None, "w_gc": None, "gm": None, "w_pc": None}


def dc_gain(num: np.ndarray, den: np.ndarray) -> Optional[float]:
    if den[-1] == 0:
        return None
    value = float(num[-1] / den[-1])
    return value if np.isfinite(value) else None
