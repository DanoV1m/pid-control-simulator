import streamlit as st
import numpy as np
from scipy import signal
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Tuple, Dict, Optional, List
import pandas as pd


# ==============================================================================
# 1. LOCALIZATION & DICTIONARIES (Bilingual Support: English & Hebrew)
# ==============================================================================

TRANSLATIONS = {
    "en": {
        "page_title": "Control Systems & PID Simulator | Precision Engineering Dashboard",
        "badge": "LTI CONTROL SYSTEMS // SIMULATION SUITE V2.0",
        "title": "Control Systems & PID Closed-Loop Simulator",
        "subtitle": "High-precision engineering workspace for Linear Time-Invariant (LTI) systems in the time, frequency, and complex s-domains with real-time PID loop compensation.",
        "status_engine": "ENGINE ONLINE // SCIPY KERNEL ACTIVE",
        "sidebar_header": "CONTROL DESK",
        "lang_select": "Interface Language / שפה",
        "section_plant": "01 // PLANT DYNAMICS G(s)",
        "preset_label": "Select Plant Benchmark:",
        "num_label": "Numerator Coefficients (comma-separated):",
        "den_label": "Denominator Coefficients (comma-separated):",
        "num_help": "E.g. '1, 2' represents polynomial s + 2",
        "den_help": "E.g. '1, 2, 10' represents polynomial s² + 2s + 10",
        "section_pid": "02 // PID COMPENSATOR C(s)",
        "quick_modes": "Quick Controller Presets:",
        "kp_label": "Proportional Gain (Kp)",
        "ki_label": "Integral Gain (Ki)",
        "kd_label": "Derivative Gain (Kd)",
        "section_sim": "03 // SIMULATION CONFIGURATION",
        "t_final_label": "Simulation Horizon [seconds]",
        "show_ol_label": "Overlay Open-Loop G(s) Benchmark",
        "diagram_expander": "System Architecture & Control Loop Block Diagram",
        "err_invalid_coeffs": "Input Error: Please provide valid comma-separated numerical coefficients.",
        "err_improper": "Improper System: The degree of the numerator cannot exceed the degree of the denominator.",
        "eq_plant": "PLANT DYNAMICS G(s)",
        "eq_pid": "PID COMPENSATOR C(s)",
        "eq_closed_loop": "CLOSED-LOOP SYSTEM T(s)",
        "metrics_title": "Closed-Loop Dynamic Performance (Time Domain)",
        "unstable_banner": "CRITICAL STABILITY WARNING: Closed-loop poles reside in the Right-Half Plane (RHP). System diverges asymptotically!",
        "open_loop_expander": "Compare with Open-Loop Plant Performance",
        "tab_step": "Step Response (Time Domain)",
        "tab_pz": "s-Plane Pole-Zero Map",
        "tab_bode": "Frequency Response (Bode Plot)",
        "tab_poles": "Pole Telemetry & Damping Analysis",
        "download_csv": "Export Simulation Dataset (CSV for MATLAB / Python)",
        "pz_caption": "BIBO Stability Criterion: All closed-loop poles (×) must reside strictly in the Left-Half Plane (Re(s) < 0, left of the red threshold line).",
        "bode_caption": "Bode Diagram displays frequency response magnitude and phase for stability margins (Gain Margin GM & Phase Margin PM) and bandwidth evaluation.",
        "status_stable": "BIBO STABLE",
        "status_unstable": "UNSTABLE",
        "rise_time": "Rise Time (tr)",
        "settling_time": "Settling Time (ts)",
        "overshoot": "Peak Overshoot (Mp)",
        "steady_state": "Steady State (y_ss)",
        "ess": "Steady-State Error (ess)",
        "peak_time": "Peak Time (tp)",
        "stability_badge": "Stability Status",
        "lhp_label": "Left-Half Plane (Stable Region)",
        "rhp_label": "Right-Half Plane (Unstable Region)",
    },
    "he": {
        "page_title": "סימולטור מערכות בקרה ובקר PID | לוח מחוונים הנדסי מתקדם",
        "badge": "מערכות בקרה ליניאריות // חבילת סימולציה הנדסית V2.0",
        "title": "סימולטור מערכות בקרה ובקר PID אינטראקטיבי",
        "subtitle": "סביבת סימולציה הנדסית מתקדמת לניתוח מערכות ליניאריות (LTI) במישור הזמן, התדר ומישור s המרוכב, וכוונון בקר PID בחוג סגור בזמן אמת.",
        "status_engine": "מנוע חישוב מקוון // ליבת SCIPY פעילה",
        "sidebar_header": "קונסולת בקרה (Control Desk)",
        "lang_select": "שפת ממשק / Interface Language",
        "section_plant": "01 // הגדרת המערכת G(s)",
        "preset_label": "בחר מודל מערכת מוכן מראש:",
        "num_label": "מקדמי המונה (Numerator) - מופרדים בפסיק:",
        "den_label": "מקדמי המכנה (Denominator) - מופרדים בפסיק:",
        "num_help": "למשל: '1, 2' מייצג את הפולינום s + 2",
        "den_help": "למשל: '1, 2, 10' מייצג את הפולינום s² + 2s + 10",
        "section_pid": "02 // כוונון בקר PID C(s)",
        "quick_modes": "תצורות בקר מהירות:",
        "kp_label": "הגבר פרופורציונלי (Kp)",
        "ki_label": "הגבר אינטגרלי (Ki)",
        "kd_label": "הגבר נגזרתי (Kd)",
        "section_sim": "03 // פרמטרי סימולציה",
        "t_final_label": "אופק זמן לסימולציה [שניות]",
        "show_ol_label": "הצג השוואה למערכת בחוג פתוח G(s)",
        "diagram_expander": "דיאגרמת בלוקים של חוג הבקרה הסגור",
        "err_invalid_coeffs": "שגיאה בקלט: אנא הזן מקדמים מספריים חוקיים מופרדים בפסיקים.",
        "err_improper": "מערכת לא סיבתית (Improper TF): דרגת המונה חייבת להיות קטנה או שווה לדרגת המכנה.",
        "eq_plant": "פונקציית התעבורה בחוג פתוח G(s)",
        "eq_pid": "בקר ה-PID C(s)",
        "eq_closed_loop": "פונקציית התעבורה בחוג סגור T(s)",
        "metrics_title": "מדדי ביצועים דינמיים בחוג סגור (Closed-Loop)",
        "unstable_banner": "אזהרת יציבות קריטית: לחוג הסגור יש קטבים בחצי המישור הימני (RHP) – המערכת מתבדרת אסימפטוטית!",
        "open_loop_expander": "הצג השוואה למדדי המערכת בחוג פתוח (Open-Loop)",
        "tab_step": "תגובת מדרגה (Step Response)",
        "tab_pz": "מפת קטבים ואפסים (s-Plane)",
        "tab_bode": "תגובת תדר (Bode Plot)",
        "tab_poles": "טלמטריה מפורטת של קטבי המערכת",
        "download_csv": "הורד נתוני סימולציה לקובץ CSV (עבור MATLAB / Excel)",
        "pz_caption": "תנאי הכרחי ומספיק ליציבות BIBO: כל קטבי החוג הסגור (×) חייבים להימצא בחצי המישור השמאלי (Re(s) < 0, משמאל לקו האדום).",
        "bode_caption": "דיאגרמת בודה מציגה הגבר ומופע בתדר לבחינת שולי יציבות (Gain Margin ו-Phase Margin) ורוחב פס.",
        "status_stable": "יציבה (BIBO)",
        "status_unstable": "לא יציבה",
        "rise_time": "זמן עלייה (tr)",
        "settling_time": "זמן התייצבות (ts)",
        "overshoot": "חריגה מרבית (Mp)",
        "steady_state": "מצב מתמיד (y_ss)",
        "ess": "שגיאת מצב מתמיד (ess)",
        "peak_time": "זמן שיא (tp)",
        "stability_badge": "סטטוס יציבות",
        "lhp_label": "חצי מישור שמאלי (אזור יציב)",
        "rhp_label": "חצי מישור ימני (אזור לא יציב)",
    }
}

PRESETS = {
    "en": {
        "Underdamped 2nd-Order System": ("1", "1, 2, 10"),
        "DC Motor Speed Control (Armature)": ("2", "0.5, 2.5, 2"),
        "Series RLC Resonant Circuit": ("10", "1, 4, 25"),
        "3rd-Order Industrial System": ("1", "1, 6, 11, 6"),
        "Open-Loop Unstable System (Inverted Pendulum)": ("1", "1, -1, 2"),
        "Custom Configuration": ("1", "1, 3, 2"),
    },
    "he": {
        "מערכת סדר שני (תת-מרוסנת)": ("1", "1, 2, 10"),
        "מודל מנוע DC (בקרת מהירות)": ("2", "0.5, 2.5, 2"),
        "מעגל RLC טורי": ("10", "1, 4, 25"),
        "מערכת סדר שלישי": ("1", "1, 6, 11, 6"),
        "מערכת בלתי יציבה ב-Open-Loop (מטוטלת הפוכה)": ("1", "1, -1, 2"),
        "הגדרה ידנית חופשית": ("1", "1, 3, 2"),
    }
}


# ==============================================================================
# 2. CONTROL SYSTEMS MATHEMATICAL ENGINE
# ==============================================================================

def parse_coefficients(coeff_str: str) -> Optional[np.ndarray]:
    """Converts a comma-separated string of coefficients into a normalized NumPy array."""
    try:
        coeffs = [float(x.strip()) for x in coeff_str.split(",") if x.strip() != ""]
        if not coeffs:
            return None
        arr = np.trim_zeros(np.array(coeffs, dtype=float), trim="f")
        return arr if len(arr) > 0 else None
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
        cl_den = np.array([1.0])

    return cl_num, cl_den, l_num, l_den


def calculate_step_metrics(
    t: np.ndarray, y: np.ndarray, poles: np.ndarray, setpoint: float = 1.0
) -> Dict[str, Optional[float]]:
    """Calculates comprehensive step response performance metrics."""
    is_stable = bool(np.all(np.real(poles) < 1e-7))

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

    y_ss = float(y[-1])
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
        if len(outside_band) == 0:
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


def analyze_poles(poles: np.ndarray) -> List[Dict]:
    """Provides detailed mechanical & damping analysis for each pole in s-plane."""
    results = []
    for i, p in enumerate(poles):
        sigma = float(np.real(p))
        omega_d = float(np.imag(p))
        wn = float(np.abs(p))
        zeta = float(-sigma / wn) if wn > 1e-9 else 0.0

        if sigma > 1e-6:
            classification = "Unstable (RHP)"
        elif abs(sigma) <= 1e-6:
            classification = "Marginally Stable (Imag Axis)"
        elif abs(omega_d) < 1e-6:
            classification = "Real Non-oscillatory"
        elif zeta < 1.0:
            classification = f"Underdamped (ζ = {zeta:.3f})"
        elif abs(zeta - 1.0) < 1e-3:
            classification = "Critically Damped"
        else:
            classification = "Overdamped"

        results.append({
            "Index": f"p_{i+1}",
            "Real [σ]": f"{sigma:.4f}",
            "Imag [jω]": f"{omega_d:+.4f}j",
            "Natural Freq [ωn]": f"{wn:.4f} rad/s",
            "Damping Ratio [ζ]": f"{zeta:.4f}" if wn > 1e-9 else "N/A",
            "Dynamic Mode": classification,
        })
    return results


def generate_csv_data(t: np.ndarray, y_ol: np.ndarray, y_cl: np.ndarray) -> str:
    """Generates an RFC-compliant CSV dataset for external validation in MATLAB / Python."""
    header = "Time_sec,Open_Loop_Response,Closed_Loop_PID_Response,Tracking_Error\n"
    error = 1.0 - y_cl
    rows = [f"{t[i]:.4f},{y_ol[i]:.6f},{y_cl[i]:.6f},{error[i]:.6f}" for i in range(len(t))]
    return header + "\n".join(rows)


# ==============================================================================
# 3. HIGH-END MODERN DARK THEME & GLASSMORPHISM CSS
# ==============================================================================

CUSTOM_CSS = """
<style>
/* -------------------------------------------------------------------------
   1. GOOGLE FONTS & GLOBAL TYPOGRAPHY
   ------------------------------------------------------------------------- */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: #E2E8F0;
    -webkit-font-smoothing: antialiased;
}

/* -------------------------------------------------------------------------
   2. APP BACKGROUND & RADIAL GRADIENT MESH
   ------------------------------------------------------------------------- */
.stApp {
    background-color: #0A0E17 !important;
    background-image: 
        radial-gradient(circle at 15% 10%, rgba(0, 210, 255, 0.05) 0%, transparent 45%),
        radial-gradient(circle at 85% 15%, rgba(99, 102, 241, 0.05) 0%, transparent 45%),
        radial-gradient(circle at 50% 90%, rgba(16, 185, 129, 0.03) 0%, transparent 50%) !important;
    background-attachment: fixed !important;
}

/* -------------------------------------------------------------------------
   3. AVIONICS / CONTROL DESK SIDEBAR STYLING
   ------------------------------------------------------------------------- */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(13, 19, 33, 0.96) 0%, rgba(10, 14, 23, 0.98) 100%) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.07) !important;
    backdrop-filter: blur(24px) !important;
    -webkit-backdrop-filter: blur(24px) !important;
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {
    color: #F8FAFC !important;
    letter-spacing: 0.04em;
    font-weight: 700;
}

.sidebar-section-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(0, 210, 255, 0.08);
    border: 1px solid rgba(0, 210, 255, 0.25);
    border-radius: 6px;
    padding: 3px 8px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    font-weight: 600;
    color: #00D2FF;
    letter-spacing: 0.06em;
    margin-bottom: 8px;
}

/* -------------------------------------------------------------------------
   4. HERO HEADER BANNER & BADGES
   ------------------------------------------------------------------------- */
.hero-container {
    background: linear-gradient(135deg, rgba(18, 26, 44, 0.75) 0%, rgba(12, 17, 30, 0.85) 100%);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 24px 28px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 12px 36px 0 rgba(0, 0, 0, 0.35);
}

.hero-container::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, #00D2FF, #3B82F6, #10B981, transparent);
}

.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(0, 210, 255, 0.1);
    border: 1px solid rgba(0, 210, 255, 0.3);
    border-radius: 20px;
    padding: 4px 12px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    font-weight: 600;
    color: #00D2FF;
    letter-spacing: 0.08em;
    margin-bottom: 12px;
}

.hero-title {
    font-size: 2.1rem;
    font-weight: 800;
    color: #F8FAFC;
    letter-spacing: -0.03em;
    margin: 0 0 8px 0;
    line-height: 1.2;
}

.hero-subtitle {
    font-size: 0.95rem;
    color: #94A3B8;
    line-height: 1.5;
    margin: 0;
    max-width: 900px;
}

.hero-telemetry-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(16, 185, 129, 0.1);
    border: 1px solid rgba(16, 185, 129, 0.3);
    border-radius: 6px;
    padding: 2px 8px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: #10B981;
    font-weight: 600;
    margin-top: 12px;
}

/* -------------------------------------------------------------------------
   5. GLASSMORPHISM MATHEMATICAL EQUATION CARDS
   ------------------------------------------------------------------------- */
.math-card {
    background: linear-gradient(135deg, rgba(19, 27, 45, 0.65) 0%, rgba(12, 17, 30, 0.8) 100%);
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 14px;
    padding: 16px 18px;
    box-shadow: 0 8px 28px rgba(0, 0, 0, 0.3);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    height: 100%;
}

.math-card:hover {
    border-color: rgba(0, 210, 255, 0.3);
    box-shadow: 0 12px 36px rgba(0, 210, 255, 0.1), 0 8px 24px rgba(0,0,0,0.4);
    transform: translateY(-2px);
}

.math-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
    padding-bottom: 8px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.math-card-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    color: #00D2FF;
}

.math-card-badge {
    background: rgba(255, 255, 255, 0.06);
    border-radius: 4px;
    padding: 2px 6px;
    font-size: 0.7rem;
    color: #94A3B8;
    font-family: 'JetBrains Mono', monospace;
}

/* Stylize Streamlit's native LaTeX block */
[data-testid="stLatex"] {
    background: rgba(10, 14, 24, 0.7) !important;
    border: 1px solid rgba(255, 255, 255, 0.06) !important;
    border-radius: 8px !important;
    padding: 12px 8px !important;
    margin: 8px 0 !important;
    overflow-x: auto !important;
}

/* -------------------------------------------------------------------------
   6. GLASSMORPHISM PERFORMANCE METRICS CARDS (CLOSED-LOOP DASHBOARD)
   ------------------------------------------------------------------------- */
.metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 14px;
    margin: 16px 0 24px 0;
}

.metric-glass-card {
    background: linear-gradient(135deg, rgba(20, 29, 48, 0.65) 0%, rgba(12, 17, 30, 0.8) 100%);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 16px 18px;
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    position: relative;
    overflow: hidden;
}

.metric-glass-card:hover {
    border-color: rgba(0, 210, 255, 0.35);
    box-shadow: 0 10px 32px rgba(0, 210, 255, 0.12), 0 6px 20px rgba(0, 0, 0, 0.4);
    transform: translateY(-2px);
}

.metric-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}

.metric-title {
    font-size: 0.74rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    color: #94A3B8;
}

.metric-number {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.6rem;
    font-weight: 700;
    color: #F8FAFC;
    letter-spacing: -0.02em;
    line-height: 1.1;
    margin: 4px 0;
}

.metric-subtext {
    font-size: 0.72rem;
    color: #64748B;
    margin-top: 4px;
    display: flex;
    align-items: center;
    gap: 4px;
}

/* Pulsing Status Badges */
.pulse-dot-green {
    width: 8px;
    height: 8px;
    background-color: #10B981;
    border-radius: 50%;
    display: inline-block;
    box-shadow: 0 0 10px #10B981;
    animation: pulseGreen 2s infinite;
}

.pulse-dot-red {
    width: 8px;
    height: 8px;
    background-color: #EF4444;
    border-radius: 50%;
    display: inline-block;
    box-shadow: 0 0 10px #EF4444;
    animation: pulseRed 1.5s infinite;
}

@keyframes pulseGreen {
    0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
    70% { transform: scale(1.1); box-shadow: 0 0 0 7px rgba(16, 185, 129, 0); }
    100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
}

@keyframes pulseRed {
    0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }
    70% { transform: scale(1.15); box-shadow: 0 0 0 8px rgba(239, 68, 68, 0); }
    100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
}

/* Tag Pills */
.pill-optimal {
    background: rgba(16, 185, 129, 0.15);
    color: #10B981;
    border: 1px solid rgba(16, 185, 129, 0.35);
    padding: 2px 8px;
    border-radius: 6px;
    font-size: 0.68rem;
    font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
}

.pill-warning {
    background: rgba(245, 158, 11, 0.15);
    color: #F59E0B;
    border: 1px solid rgba(245, 158, 11, 0.35);
    padding: 2px 8px;
    border-radius: 6px;
    font-size: 0.68rem;
    font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
}

.pill-danger {
    background: rgba(239, 68, 68, 0.15);
    color: #EF4444;
    border: 1px solid rgba(239, 68, 68, 0.35);
    padding: 2px 8px;
    border-radius: 6px;
    font-size: 0.68rem;
    font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
}

.pill-info {
    background: rgba(0, 210, 255, 0.12);
    color: #00D2FF;
    border: 1px solid rgba(0, 210, 255, 0.3);
    padding: 2px 8px;
    border-radius: 6px;
    font-size: 0.68rem;
    font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
}

/* -------------------------------------------------------------------------
   7. INTERACTIVE TABS & CONTROLS POLISH
   ------------------------------------------------------------------------- */
[data-baseweb="tab-list"] {
    gap: 8px;
    background-color: rgba(13, 19, 33, 0.5) !important;
    padding: 6px;
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.06);
}

[data-baseweb="tab"] {
    background-color: transparent !important;
    border-radius: 8px !important;
    color: #94A3B8 !important;
    font-size: 0.88rem !important;
    font-weight: 600 !important;
    padding: 8px 16px !important;
    border: 1px solid transparent !important;
    transition: all 0.2s ease !important;
}

[data-baseweb="tab"]:hover {
    color: #F8FAFC !important;
    background-color: rgba(255, 255, 255, 0.04) !important;
}

[aria-selected="true"] {
    background: linear-gradient(135deg, rgba(0, 210, 255, 0.15) 0%, rgba(59, 130, 246, 0.15) 100%) !important;
    border: 1px solid rgba(0, 210, 255, 0.35) !important;
    color: #00D2FF !important;
}

/* -------------------------------------------------------------------------
   8. SYSTEM ARCHITECTURE BLOCK DIAGRAM
   ------------------------------------------------------------------------- */
.block-diagram-container {
    background: linear-gradient(135deg, rgba(16, 23, 40, 0.7) 0%, rgba(10, 14, 25, 0.85) 100%);
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 12px;
    padding: 16px 20px;
    margin: 12px 0;
    text-align: center;
}
</style>
"""


# ==============================================================================
# 4. PLOTLY VISUALIZATION ENGINE (DARK RADAR & CYBER PALETTE)
# ==============================================================================

def create_step_response_figure(
    t_ol: np.ndarray, y_ol: np.ndarray,
    t_cl: np.ndarray, y_cl: np.ndarray,
    metrics: Dict[str, Optional[float]],
    show_ol: bool = True,
    lang: str = "en"
) -> go.Figure:
    """Builds a high-precision, dark cyber themed step response chart."""
    t_dict = TRANSLATIONS[lang]
    fig = go.Figure()
    t_max = max(float(t_cl[-1]), float(t_ol[-1])) if show_ol else float(t_cl[-1])

    # Reference Setpoint r(t) = 1.0
    fig.add_hline(
        y=1.0,
        line=dict(color="#10B981", width=1.8, dash="dash"),
        annotation=dict(
            text="Setpoint r(t) = 1.0",
            font=dict(color="#10B981", size=11, family="JetBrains Mono"),
            bgcolor="rgba(10, 14, 23, 0.8)",
            bordercolor="rgba(16, 185, 129, 0.4)",
            borderwidth=1,
            xanchor="left"
        )
    )

    # ±2% Settling Tolerance Envelope
    fig.add_hrect(
        y0=0.98, y1=1.02,
        fillcolor="rgba(16, 185, 129, 0.08)",
        line_width=0,
        annotation=dict(
            text="±2% Settling Band",
            font=dict(color="rgba(16, 185, 129, 0.8)", size=10, family="JetBrains Mono"),
            xanchor="right"
        )
    )

    # Open-Loop Benchmark Curve
    if show_ol:
        fig.add_trace(go.Scatter(
            x=t_ol, y=y_ol,
            mode="lines",
            name="Open-Loop Plant G(s)",
            line=dict(color="#64748B", width=2.0, dash="dot"),
            hovertemplate="Open-Loop: <b>%{y:.4f}</b> at %{x:.3f}s<extra></extra>"
        ))

    # Closed-Loop PID Curve
    fig.add_trace(go.Scatter(
        x=t_cl, y=y_cl,
        mode="lines",
        name="Closed-Loop PID T(s)",
        line=dict(color="#00D2FF", width=3.2),
        hovertemplate="Closed-Loop PID: <b>%{y:.4f}</b> at %{x:.3f}s<extra></extra>"
    ))

    # Dynamic Markers: Peak Overshoot & Rise Time Crossings
    if metrics["stable"] and metrics["peak_val"] is not None and metrics["peak_time"] is not None:
        if metrics["overshoot"] is not None and metrics["overshoot"] > 0.5:
            fig.add_trace(go.Scatter(
                x=[metrics["peak_time"]],
                y=[metrics["peak_val"]],
                mode="markers+text",
                name="Peak Value (Mp)",
                marker=dict(symbol="star", size=12, color="#F59E0B", line=dict(color="#FFFFFF", width=1.5)),
                text=[f" Mp: +{metrics['overshoot']:.1f}% (tp={metrics['peak_time']:.2f}s)"],
                textposition="top right",
                textfont=dict(color="#F59E0B", size=11, family="JetBrains Mono"),
                hoverinfo="skip"
            ))

    if metrics["stable"] and metrics["t_10"] is not None and metrics["t_90"] is not None and metrics["steady_state"] is not None:
        y_ss = metrics["steady_state"]
        fig.add_trace(go.Scatter(
            x=[metrics["t_10"], metrics["t_90"]],
            y=[0.1 * y_ss, 0.9 * y_ss],
            mode="markers",
            name="Rise Time (10%-90%)",
            marker=dict(symbol="diamond", size=8, color="#38BDF8"),
            hoverinfo="skip",
            showlegend=False
        ))

    fig.update_layout(
        title=dict(
            text="Unit Step Response Comparison — Time Domain",
            font=dict(size=15, color="#F8FAFC", family="Inter")
        ),
        xaxis=dict(
            title="Time [seconds]",
            showgrid=True,
            gridcolor="#1E293B",
            zerolinecolor="#334155",
            range=[0, t_max],
            color="#94A3B8"
        ),
        yaxis=dict(
            title="System Amplitude y(t)",
            showgrid=True,
            gridcolor="#1E293B",
            zerolinecolor="#334155",
            color="#94A3B8"
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(12, 17, 29, 0.75)",
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="#111827",
            font_size=12,
            font_family="JetBrains Mono",
            bordercolor="rgba(0, 210, 255, 0.4)"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color="#CBD5E1", size=11)
        ),
        margin=dict(l=45, r=40, t=65, b=45),
        height=480
    )
    return fig


def create_pole_zero_figure(
    ol_poles: np.ndarray, ol_zeros: np.ndarray,
    cl_poles: np.ndarray, cl_zeros: np.ndarray,
    lang: str = "en"
) -> go.Figure:
    """Builds an avionics-inspired complex s-plane pole-zero radar map."""
    t_dict = TRANSLATIONS[lang]
    fig = go.Figure()

    # Determine axis boundaries
    all_re = np.concatenate([np.real(ol_poles), np.real(cl_poles), [0.0]])
    all_im = np.concatenate([np.imag(ol_poles), np.imag(cl_poles), [0.0]])
    if len(ol_zeros) > 0:
        all_re = np.concatenate([all_re, np.real(ol_zeros)])
        all_im = np.concatenate([all_im, np.imag(ol_zeros)])
    if len(cl_zeros) > 0:
        all_re = np.concatenate([all_re, np.real(cl_zeros)])
        all_im = np.concatenate([all_im, np.imag(cl_zeros)])

    max_re = max(2.0, float(np.max(np.abs(all_re))) * 1.3)
    max_im = max(3.0, float(np.max(np.abs(all_im))) * 1.3)
    limit = max(max_re, max_im)

    # Shaded Stability Regions: LHP (Stable) & RHP (Unstable)
    fig.add_shape(
        type="rect",
        x0=-limit, x1=0, y0=-limit, y1=limit,
        fillcolor="rgba(16, 185, 129, 0.04)",
        line_width=0,
        layer="below"
    )
    fig.add_shape(
        type="rect",
        x0=0, x1=limit, y0=-limit, y1=limit,
        fillcolor="rgba(239, 68, 68, 0.04)",
        line_width=0,
        layer="below"
    )

    # Imaginary Stability Boundary (Re(s) = 0)
    fig.add_vline(
        x=0,
        line=dict(color="#EF4444", width=2.0, dash="dash"),
        annotation=dict(
            text="Stability Boundary (σ = 0)",
            font=dict(color="#EF4444", size=10, family="JetBrains Mono"),
            bgcolor="rgba(10, 14, 23, 0.8)",
            bordercolor="rgba(239, 68, 68, 0.4)",
            borderwidth=1,
            xanchor="left"
        )
    )

    # Constant Damping Ratio Lines (ζ = 0.707)
    zeta_x = np.linspace(-limit, 0, 50)
    zeta_y_pos = -zeta_x  # tan(45°) = 1 for ζ = 0.707
    zeta_y_neg = zeta_x
    fig.add_trace(go.Scatter(
        x=np.concatenate([zeta_x, [0], zeta_x]),
        y=np.concatenate([zeta_y_pos, [0], zeta_y_neg]),
        mode="lines",
        line=dict(color="#334155", width=1.0, dash="dot"),
        hoverinfo="skip",
        name="ζ = 0.707 Damping Line",
        showlegend=False
    ))

    # Open-Loop Poles (×)
    fig.add_trace(go.Scatter(
        x=np.real(ol_poles), y=np.imag(ol_poles),
        mode="markers",
        name="Open-Loop Poles (×)",
        marker=dict(symbol="x", size=11, color="#64748B", line=dict(width=2)),
        hovertemplate="<b>Open-Loop Pole:</b> %{x:.3f} + %{y:.3f}j<extra></extra>"
    ))

    # Open-Loop Zeros (○)
    if len(ol_zeros) > 0:
        fig.add_trace(go.Scatter(
            x=np.real(ol_zeros), y=np.imag(ol_zeros),
            mode="markers",
            name="Open-Loop Zeros (○)",
            marker=dict(symbol="circle-open", size=10, color="#64748B", line=dict(width=2)),
            hovertemplate="<b>Open-Loop Zero:</b> %{x:.3f} + %{y:.3f}j<extra></extra>"
        ))

    # Closed-Loop PID Poles (×) - Glowing Neon Cyan
    fig.add_trace(go.Scatter(
        x=np.real(cl_poles), y=np.imag(cl_poles),
        mode="markers",
        name="Closed-Loop PID Poles (×)",
        marker=dict(symbol="x", size=14, color="#00D2FF", line=dict(width=2.8)),
        hovertemplate="<b>Closed-Loop Pole:</b> %{x:.4f} + %{y:.4f}j<extra></extra>"
    ))

    # Closed-Loop Zeros (○) - Glowing Emerald
    if len(cl_zeros) > 0:
        fig.add_trace(go.Scatter(
            x=np.real(cl_zeros), y=np.imag(cl_zeros),
            mode="markers",
            name="Closed-Loop Zeros (○)",
            marker=dict(symbol="circle-open", size=11, color="#10B981", line=dict(width=2.5)),
            hovertemplate="<b>Closed-Loop Zero:</b> %{x:.4f} + %{y:.4f}j<extra></extra>"
        ))

    fig.update_layout(
        title=dict(
            text="s-Plane Complex Pole-Zero Map (Stability Architecture)",
            font=dict(size=15, color="#F8FAFC", family="Inter")
        ),
        xaxis=dict(
            title="Real Axis (σ) [sec⁻¹]",
            showgrid=True,
            gridcolor="#1E293B",
            zerolinecolor="#334155",
            range=[-limit, limit * 0.4],
            color="#94A3B8"
        ),
        yaxis=dict(
            title="Imaginary Axis (jω) [rad/sec]",
            showgrid=True,
            gridcolor="#1E293B",
            zerolinecolor="#334155",
            range=[-limit * 0.9, limit * 0.9],
            color="#94A3B8"
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(12, 17, 29, 0.75)",
        hoverlabel=dict(
            bgcolor="#111827",
            font_size=12,
            font_family="JetBrains Mono",
            bordercolor="rgba(0, 210, 255, 0.4)"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color="#CBD5E1", size=11)
        ),
        margin=dict(l=45, r=40, t=65, b=45),
        height=480
    )
    return fig


def create_bode_figure(
    ol_sys: signal.TransferFunction,
    l_sys: signal.TransferFunction,
    margins: Dict[str, Optional[float]],
    lang: str = "en"
) -> go.Figure:
    """Builds an engineering frequency response Bode diagram with stability margins."""
    w = np.logspace(-2, 3, 800)
    w_ol, mag_ol, phase_ol = signal.bode(ol_sys, w=w)
    w_l, mag_l, phase_l = signal.bode(l_sys, w=w)

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.12,
        subplot_titles=("Magnitude Response |L(jω)| [dB]", "Phase Response ∠L(jω) [degrees]")
    )

    # 1. Magnitude Subplot: Plant G(jω) & Loop L(jω)
    fig.add_trace(go.Scatter(
        x=w_ol, y=mag_ol,
        mode="lines",
        name="Plant G(jω)",
        line=dict(color="#64748B", width=1.8, dash="dot"),
        hovertemplate="Plant Mag: <b>%{y:.2f} dB</b> at %{x:.2f} rad/s<extra></extra>"
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=w_l, y=mag_l,
        mode="lines",
        name="Compensated Loop L(jω) = C(jω)G(jω)",
        line=dict(color="#00D2FF", width=2.8),
        hovertemplate="Loop Mag: <b>%{y:.2f} dB</b> at %{x:.2f} rad/s<extra></extra>"
    ), row=1, col=1)

    # 0 dB Reference line
    fig.add_hline(
        y=0.0,
        line=dict(color="#10B981", width=1.5, dash="dash"),
        row=1, col=1
    )

    # 2. Phase Subplot: Plant Phase & Loop Phase
    fig.add_trace(go.Scatter(
        x=w_ol, y=phase_ol,
        mode="lines",
        name="Plant Phase",
        line=dict(color="#64748B", width=1.8, dash="dot"),
        showlegend=False,
        hovertemplate="Plant Phase: <b>%{y:.1f}°</b> at %{x:.2f} rad/s<extra></extra>"
    ), row=2, col=1)

    fig.add_trace(go.Scatter(
        x=w_l, y=phase_l,
        mode="lines",
        name="Compensated Phase",
        line=dict(color="#00D2FF", width=2.8),
        showlegend=False,
        hovertemplate="Loop Phase: <b>%{y:.1f}°</b> at %{x:.2f} rad/s<extra></extra>"
    ), row=2, col=1)

    # -180° Critical Phase Margin reference line
    fig.add_hline(
        y=-180.0,
        line=dict(color="#EF4444", width=1.5, dash="dash"),
        row=2, col=1
    )

    # Margin Annotations if crossover exists
    if margins["pm"] is not None and margins["w_gc"] is not None:
        fig.add_vline(
            x=margins["w_gc"],
            line=dict(color="#10B981", width=1.2, dash="dot"),
            annotation=dict(
                text=f" PM = {margins['pm']:.1f}° (@ {margins['w_gc']:.2f} rad/s)",
                font=dict(color="#10B981", size=10, family="JetBrains Mono"),
                xanchor="left"
            ),
            row=2, col=1
        )

    if margins["gm"] is not None and margins["w_pc"] is not None and not np.isinf(margins["gm"]):
        fig.add_vline(
            x=margins["w_pc"],
            line=dict(color="#F59E0B", width=1.2, dash="dot"),
            annotation=dict(
                text=f" GM = {margins['gm']:.1f} dB (@ {margins['w_pc']:.2f} rad/s)",
                font=dict(color="#F59E0B", size=10, family="JetBrains Mono"),
                xanchor="left"
            ),
            row=1, col=1
        )

    fig.update_xaxes(type="log", showgrid=True, gridcolor="#1E293B", zerolinecolor="#334155", color="#94A3B8", row=1, col=1)
    fig.update_xaxes(type="log", title_text="Frequency ω [rad/sec]", showgrid=True, gridcolor="#1E293B", zerolinecolor="#334155", color="#94A3B8", row=2, col=1)
    fig.update_yaxes(title_text="Magnitude (dB)", showgrid=True, gridcolor="#1E293B", zerolinecolor="#334155", color="#94A3B8", row=1, col=1)
    fig.update_yaxes(title_text="Phase (deg)", showgrid=True, gridcolor="#1E293B", zerolinecolor="#334155", color="#94A3B8", row=2, col=1)

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(12, 17, 29, 0.75)",
        height=540,
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="#111827",
            font_size=12,
            font_family="JetBrains Mono",
            bordercolor="rgba(0, 210, 255, 0.4)"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.06,
            xanchor="right",
            x=1,
            font=dict(color="#CBD5E1", size=11)
        ),
        margin=dict(l=45, r=40, t=75, b=45)
    )
    return fig


# ==============================================================================
# 5. UI COMPONENTS (GLASSMORPHIC CARDS & DIAGRAMS)
# ==============================================================================

def render_glass_metric_cards(metrics: Dict[str, Optional[float]], lang: str = "en") -> None:
    """Renders sleek glassmorphic metric cards with status indicators."""
    t_dict = TRANSLATIONS[lang]

    # Stability Card Values
    if metrics["stable"]:
        stability_html = f"""
        <div class="metric-glass-card">
            <div class="metric-header">
                <span class="metric-title">{t_dict['stability_badge']}</span>
                <span class="pulse-dot-green"></span>
            </div>
            <div class="metric-number" style="color: #10B981; font-size: 1.35rem;">{t_dict['status_stable']}</div>
            <div class="metric-subtext"><span class="pill-optimal">LHP Poles</span></div>
        </div>
        """
    else:
        stability_html = f"""
        <div class="metric-glass-card" style="border-color: rgba(239, 68, 68, 0.4);">
            <div class="metric-header">
                <span class="metric-title">{t_dict['stability_badge']}</span>
                <span class="pulse-dot-red"></span>
            </div>
            <div class="metric-number" style="color: #EF4444; font-size: 1.35rem;">{t_dict['status_unstable']}</div>
            <div class="metric-subtext"><span class="pill-danger">RHP Poles Detected</span></div>
        </div>
        """

    # Rise Time
    tr_val = f"{metrics['rise_time']:.3f} s" if metrics["rise_time"] is not None else "N/A"
    tr_html = f"""
    <div class="metric-glass-card">
        <div class="metric-header">
            <span class="metric-title">{t_dict['rise_time']}</span>
            <span class="pill-info">10% → 90%</span>
        </div>
        <div class="metric-number">{tr_val}</div>
        <div class="metric-subtext">Transient Response</div>
    </div>
    """

    # Settling Time
    ts_val = f"{metrics['settling_time']:.3f} s" if metrics["settling_time"] is not None else "Not Settled"
    ts_pill = "pill-optimal" if metrics["settling_time"] is not None else "pill-warning"
    ts_html = f"""
    <div class="metric-glass-card">
        <div class="metric-header">
            <span class="metric-title">{t_dict['settling_time']}</span>
            <span class="{ts_pill}">±2% Band</span>
        </div>
        <div class="metric-number">{ts_val}</div>
        <div class="metric-subtext">Target Tolerance</div>
    </div>
    """

    # Overshoot
    if metrics["overshoot"] is not None:
        mp_val = f"{metrics['overshoot']:.1f}%"
        if metrics["overshoot"] <= 5.0:
            mp_pill = '<span class="pill-optimal">Optimal</span>'
        elif metrics["overshoot"] <= 20.0:
            mp_pill = '<span class="pill-warning">Moderate</span>'
        else:
            mp_pill = '<span class="pill-danger">High Peak</span>'
    else:
        mp_val = "N/A"
        mp_pill = '<span class="pill-danger">Unbounded</span>'

    mp_html = f"""
    <div class="metric-glass-card">
        <div class="metric-header">
            <span class="metric-title">{t_dict['overshoot']}</span>
            {mp_pill}
        </div>
        <div class="metric-number">{mp_val}</div>
        <div class="metric-subtext">Peak Deviation</div>
    </div>
    """

    # Steady-State Error
    if metrics["ess"] is not None:
        ess_val = f"{metrics['ess']:.4f}"
        ess_pill = '<span class="pill-optimal">Zero Error</span>' if metrics['ess'] < 0.001 else '<span class="pill-warning">Offset</span>'
    else:
        ess_val = "N/A"
        ess_pill = '<span class="pill-danger">Divergent</span>'

    ess_html = f"""
    <div class="metric-glass-card">
        <div class="metric-header">
            <span class="metric-title">{t_dict['ess']}</span>
            {ess_pill}
        </div>
        <div class="metric-number">{ess_val}</div>
        <div class="metric-subtext">|r(t) - y(∞)|</div>
    </div>
    """

    # Assemble HTML Grid
    full_html = f"""
    <div class="metrics-grid">
        {stability_html}
        {tr_html}
        {ts_html}
        {mp_html}
        {ess_html}
    </div>
    """
    st.markdown(full_html, unsafe_allow_html=True)


def render_block_diagram_svg() -> None:
    """Renders a clean SVG control loop block diagram."""
    svg_code = """
    <div class="block-diagram-container">
        <svg viewBox="0 0 740 120" width="100%" height="90" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                    <path d="M 0 1 L 8 5 L 0 9 z" fill="#00D2FF"/>
                </marker>
                <marker id="arrow-green" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                    <path d="M 0 1 L 8 5 L 0 9 z" fill="#10B981"/>
                </marker>
            </defs>
            <!-- Reference Input -->
            <text x="25" y="45" fill="#94A3B8" font-family="JetBrains Mono" font-size="12" font-weight="600">r(t)</text>
            <path d="M 50 48 L 115 48" stroke="#00D2FF" stroke-width="2" marker-end="url(#arrow)"/>
            
            <!-- Summing Junction -->
            <circle cx="130" cy="48" r="14" fill="#111827" stroke="#00D2FF" stroke-width="2"/>
            <text x="126" y="52" fill="#00D2FF" font-family="JetBrains Mono" font-size="14" font-weight="700">+</text>
            <text x="127" y="74" fill="#EF4444" font-family="JetBrains Mono" font-size="14" font-weight="700">−</text>
            
            <!-- Error Signal -->
            <path d="M 144 48 L 205 48" stroke="#00D2FF" stroke-width="2" marker-end="url(#arrow)"/>
            <text x="155" y="38" fill="#94A3B8" font-family="JetBrains Mono" font-size="10">e(t)</text>
            
            <!-- PID Controller C(s) -->
            <rect x="210" y="24" width="120" height="48" rx="8" fill="#162035" stroke="#38BDF8" stroke-width="1.5"/>
            <text x="232" y="45" fill="#F8FAFC" font-family="Inter" font-size="11" font-weight="700">PID Controller</text>
            <text x="255" y="60" fill="#00D2FF" font-family="JetBrains Mono" font-size="11">C(s)</text>
            
            <!-- Control Signal u(t) -->
            <path d="M 330 48 L 395 48" stroke="#00D2FF" stroke-width="2" marker-end="url(#arrow)"/>
            <text x="345" y="38" fill="#94A3B8" font-family="JetBrains Mono" font-size="10">u(t)</text>
            
            <!-- Plant G(s) -->
            <rect x="400" y="24" width="130" height="48" rx="8" fill="#162035" stroke="#10B981" stroke-width="1.5"/>
            <text x="430" y="45" fill="#F8FAFC" font-family="Inter" font-size="11" font-weight="700">LTI Plant</text>
            <text x="450" y="60" fill="#10B981" font-family="JetBrains Mono" font-size="11">G(s)</text>
            
            <!-- Output y(t) -->
            <path d="M 530 48 L 650 48" stroke="#00D2FF" stroke-width="2" marker-end="url(#arrow)"/>
            <circle cx="580" cy="48" r="4" fill="#00D2FF"/>
            <text x="660" y="52" fill="#F8FAFC" font-family="JetBrains Mono" font-size="12" font-weight="700">y(t)</text>
            
            <!-- Unity Negative Feedback Loop -->
            <path d="M 580 48 L 580 100 L 130 100 L 130 64" fill="none" stroke="#64748B" stroke-width="1.8" stroke-dasharray="4,4" marker-end="url(#arrow)"/>
            <text x="330" y="94" fill="#64748B" font-family="JetBrains Mono" font-size="10">Negative Unity Feedback [ -1 ]</text>
        </svg>
    </div>
    """
    st.markdown(svg_code, unsafe_allow_html=True)


# ==============================================================================
# 6. APPLICATION CONTROLLER & MAIN UI
# ==============================================================================

def main():
    st.set_page_config(
        page_title="Control Systems & PID Simulator | SaaS Dashboard",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Inject Modern Dark Theme & Glassmorphism CSS
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    # --- SIDEBAR: CONTROL DESK ---
    with st.sidebar:
        st.markdown(
            """
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 14px;">
                <div style="width: 32px; height: 32px; border-radius: 8px; background: linear-gradient(135deg, rgba(0, 210, 255, 0.25) 0%, rgba(59, 130, 246, 0.25) 100%); border: 1px solid rgba(0, 210, 255, 0.45); display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 13px; color: #00D2FF; font-family: 'JetBrains Mono', monospace;">CS</div>
                <div>
                    <div style="font-weight: 800; font-size: 1.15rem; color: #F8FAFC; letter-spacing: -0.01em;">CONTROL DESK</div>
                    <div style="font-size: 0.7rem; color: #00D2FF; font-family: 'JetBrains Mono';">AUTONOMOUS LTI ENGINE</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Language Selector
        lang_choice = st.radio(
            "Interface Language / שפה",
            options=["English", "עברית"],
            index=0,
            horizontal=True
        )
        current_lang = "en" if lang_choice == "English" else "he"
        t_dict = TRANSLATIONS[current_lang]

        st.divider()

        # Section 1: Plant Dynamics G(s)
        st.markdown(f'<div class="sidebar-section-badge">{t_dict["section_plant"]}</div>', unsafe_allow_html=True)
        preset_options = list(PRESETS[current_lang].keys())
        selected_preset = st.selectbox(t_dict["preset_label"], preset_options)
        default_num, default_den = PRESETS[current_lang][selected_preset]

        num_str = st.text_input(
            t_dict["num_label"],
            value=default_num,
            help=t_dict["num_help"]
        )
        den_str = st.text_input(
            t_dict["den_label"],
            value=default_den,
            help=t_dict["den_help"]
        )

        st.divider()

        # Section 2: PID Controller Tuning
        st.markdown(f'<div class="sidebar-section-badge">{t_dict["section_pid"]}</div>', unsafe_allow_html=True)
        
        # Controller Mode Presets
        pid_mode = st.radio(
            t_dict["quick_modes"],
            options=["Full PID", "PI (Kd = 0)", "PD (Ki = 0)", "P-Only"],
            index=0,
            horizontal=True
        )

        # Base default values according to mode
        val_kp = 8.0
        val_ki = 12.0 if pid_mode in ["Full PID", "PI (Kd = 0)"] else 0.0
        val_kd = 1.5 if pid_mode in ["Full PID", "PD (Ki = 0)"] else 0.0

        kp = st.slider(t_dict["kp_label"], min_value=0.0, max_value=60.0, value=val_kp, step=0.1)
        ki = st.slider(
            t_dict["ki_label"],
            min_value=0.0, max_value=50.0,
            value=val_ki, step=0.1,
            disabled=(pid_mode in ["PD (Ki = 0)", "P-Only"])
        )
        kd = st.slider(
            t_dict["kd_label"],
            min_value=0.0, max_value=20.0,
            value=val_kd, step=0.05,
            disabled=(pid_mode in ["PI (Kd = 0)", "P-Only"])
        )

        st.divider()

        # Section 3: Simulation Parameters
        st.markdown(f'<div class="sidebar-section-badge">{t_dict["section_sim"]}</div>', unsafe_allow_html=True)
        t_final = st.slider(t_dict["t_final_label"], min_value=2.0, max_value=60.0, value=12.0, step=1.0)
        show_ol_curve = st.checkbox(t_dict["show_ol_label"], value=True)

    # --- TOP HERO BANNER ---
    st.markdown(
        f"""
        <div class="hero-container">
            <div class="hero-badge">● {t_dict['badge']}</div>
            <h1 class="hero-title">{t_dict['title']}</h1>
            <p class="hero-subtitle">{t_dict['subtitle']}</p>
            <div class="hero-telemetry-pill">● {t_dict['status_engine']}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # System Architecture Block Diagram Expander
    with st.expander(t_dict["diagram_expander"], expanded=False):
        render_block_diagram_svg()

    # --- INPUT VALIDATION & CONTROL ENGINE COMPUTATION ---
    num = parse_coefficients(num_str)
    den = parse_coefficients(den_str)

    if num is None or den is None:
        st.error(t_dict["err_invalid_coeffs"])
        st.stop()

    if len(num) > len(den):
        st.error(t_dict["err_improper"])
        st.stop()

    # Compute Systems
    ol_sys = signal.TransferFunction(num, den)
    cl_num, cl_den, l_num, l_den = compute_closed_loop_tf(num, den, kp, ki, kd)
    cl_sys = signal.TransferFunction(cl_num, cl_den)
    l_sys = signal.TransferFunction(l_num, l_den)

    t_axis = np.linspace(0, t_final, 1400)
    t_ol, y_ol = signal.step(ol_sys, T=t_axis)
    t_cl, y_cl = signal.step(cl_sys, T=t_axis)

    ol_poles = np.roots(den)
    ol_zeros = np.roots(num) if len(num) > 1 else np.array([])
    cl_poles = np.roots(cl_den)
    cl_zeros = np.roots(cl_num) if len(cl_num) > 1 else np.array([])

    ol_metrics = calculate_step_metrics(t_ol, y_ol, ol_poles)
    cl_metrics = calculate_step_metrics(t_cl, y_cl, cl_poles)
    margins = calculate_frequency_margins(l_sys)

    # System Characteristics
    plant_order = len(den) - 1
    plant_type = int(np.sum(np.isclose(den[::-1].cumsum() == 0, False) == False)) if den[-1] == 0 else 0

    # --- MATHEMATICAL TRANSFER FUNCTION CONTAINERS ---
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.markdown(
            f"""
            <div class="math-card">
                <div class="math-card-header">
                    <span class="math-card-tag">{t_dict['eq_plant']}</span>
                    <span class="math-card-badge">Order: {plant_order}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.latex(rf"G(s) = \frac{{{poly_to_latex(num)}}}{{{poly_to_latex(den)}}}")

    with col_m2:
        st.markdown(
            f"""
            <div class="math-card">
                <div class="math-card-header">
                    <span class="math-card-tag">{t_dict['eq_pid']}</span>
                    <span class="math-card-badge">Mode: {pid_mode}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        if abs(ki) < 1e-12:
            st.latex(rf"C(s) = {kp:g} + {kd:g}s")
        else:
            st.latex(rf"C(s) = {kp:g} + \frac{{{ki:g}}}{{s}} + {kd:g}s")

    with col_m3:
        cl_order = len(cl_den) - 1
        st.markdown(
            f"""
            <div class="math-card">
                <div class="math-card-header">
                    <span class="math-card-tag">{t_dict['eq_closed_loop']}</span>
                    <span class="math-card-badge">Order: {cl_order}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.latex(rf"T(s) = \frac{{{poly_to_latex(cl_num)}}}{{{poly_to_latex(cl_den)}}}")

    st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)

    # --- GLASSMORPHISM METRICS DASHBOARD ---
    st.markdown(f"### {t_dict['metrics_title']}")
    if not cl_metrics["stable"]:
        st.error(t_dict["unstable_banner"])

    render_glass_metric_cards(cl_metrics, lang=current_lang)

    with st.expander(t_dict["open_loop_expander"], expanded=False):
        render_glass_metric_cards(ol_metrics, lang=current_lang)

    # --- INTERACTIVE ENGINEERING TABS ---
    tab1, tab2, tab3, tab4 = st.tabs([
        t_dict["tab_step"],
        t_dict["tab_pz"],
        t_dict["tab_bode"],
        t_dict["tab_poles"]
    ])

    with tab1:
        fig_step = create_step_response_figure(t_ol, y_ol, t_cl, y_cl, cl_metrics, show_ol=show_ol_curve, lang=current_lang)
        st.plotly_chart(fig_step, use_container_width=True)

        csv_data = generate_csv_data(t_axis, y_ol, y_cl)
        st.download_button(
            label=t_dict["download_csv"],
            data=csv_data,
            file_name="pid_simulation_dataset.csv",
            mime="text/csv"
        )

    with tab2:
        fig_pz = create_pole_zero_figure(ol_poles, ol_zeros, cl_poles, cl_zeros, lang=current_lang)
        st.plotly_chart(fig_pz, use_container_width=True)
        st.caption(t_dict["pz_caption"])

    with tab3:
        fig_bode = create_bode_figure(ol_sys, l_sys, margins, lang=current_lang)
        st.plotly_chart(fig_bode, use_container_width=True)
        st.caption(t_dict["bode_caption"])

    with tab4:
        st.markdown("#### Closed-Loop Pole Eigenvalue & Damping Decomposition")
        pole_data = analyze_poles(cl_poles)
        df_poles = pd.DataFrame(pole_data)
        st.dataframe(df_poles, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
