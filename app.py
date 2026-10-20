import streamlit as st
import numpy as np
from scipy import signal
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Tuple, Dict, Optional


# ==========================================
# 1. שכבת ליבה מתמטית והנדסית (Control Engine)
# ==========================================

def parse_coefficients(coeff_str: str) -> Optional[np.ndarray]:
    """ממיר מחרוזת מקדמים מופרדת בפסיקים למערך NumPy מנורמל."""
    try:
        coeffs = [float(x.strip()) for x in coeff_str.split(",") if x.strip() != ""]
        if not coeffs:
            return None
        arr = np.trim_zeros(np.array(coeffs, dtype=float), trim="f")
        return arr if len(arr) > 0 else None
    except ValueError:
        return None


def poly_to_latex(coeffs: np.ndarray) -> str:
    """ממיר מערך מקדמים של פולינום למחרוזת LaTeX תקנית."""
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
    מחשב את פונקציית התעבורה של החוג הפתוח הכולל L(s) = C(s)G(s)
    ושל החוג הסגור עם משוב יחידה T(s) = L(s) / (1 + L(s)).
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
    """מחשב מדדי ביצועים של תגובת מדרגה: יציבות, זמן עלייה, זמן התייצבות, חריגה מרבית ושגיאת מצב מתמיד."""
    is_stable = bool(np.all(np.real(poles) < 1e-7))

    if not is_stable or len(y) == 0:
        return {
            "stable": False,
            "rise_time": None,
            "settling_time": None,
            "overshoot": None,
            "steady_state": None,
            "ess": None,
        }

    y_ss = float(y[-1])
    ess = abs(setpoint - y_ss)

    if abs(y_ss) > 1e-6 and y_ss > 0:
        y_max = float(np.max(y))
        overshoot = max(0.0, ((y_max - y_ss) / abs(y_ss)) * 100.0)
    else:
        overshoot = 0.0

    rise_time = None
    if y_ss > 1e-6:
        idx_10 = np.where(y >= 0.1 * y_ss)[0]
        idx_90 = np.where(y >= 0.9 * y_ss)[0]
        if len(idx_10) > 0 and len(idx_90) > 0 and idx_90[0] >= idx_10[0]:
            rise_time = float(t[idx_90[0]] - t[idx_10[0]])

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
        "steady_state": y_ss,
        "ess": ess,
    }


def generate_csv_data(t: np.ndarray, y_ol: np.ndarray, y_cl: np.ndarray) -> str:
    """מייצר מחרוזת CSV להורדת נתוני הסימולציה עבור MATLAB / Excel."""
    header = "Time_sec,Open_Loop_Response,Closed_Loop_PID_Response,Tracking_Error\n"
    error = 1.0 - y_cl
    rows = [f"{t[i]:.4f},{y_ol[i]:.6f},{y_cl[i]:.6f},{error[i]:.6f}" for i in range(len(t))]
    return header + "\n".join(rows)


# ==========================================
# 2. שכבת ויזואליזציה (Plotly Engineering Charts)
# ==========================================

def create_step_response_figure(
    t_ol: np.ndarray, y_ol: np.ndarray,
    t_cl: np.ndarray, y_cl: np.ndarray,
    show_ol: bool = True
) -> go.Figure:
    """בונה גרף תגובת מדרגה אינטראקטיבי."""
    fig = go.Figure()
    t_max = max(float(t_cl[-1]), float(t_ol[-1])) if show_ol else float(t_cl[-1])

    fig.add_hline(
        y=1.0, line_dash="dash", line_color="#10B981",
        annotation_text="Setpoint (r = 1.0)", annotation_position="top left"
    )
    fig.add_hrect(
        y0=0.98, y1=1.02, fillcolor="#10B981", opacity=0.1,
        line_width=0, annotation_text="±2% Settling Band"
    )

    if show_ol:
        fig.add_trace(go.Scatter(
            x=t_ol, y=y_ol,
            mode="lines",
            name="Open-Loop G(s)",
            line=dict(color="#94A3B8", width=2.2, dash="dot")
        ))

    fig.add_trace(go.Scatter(
        x=t_cl, y=y_cl,
        mode="lines",
        name="Closed-Loop PID T(s)",
        line=dict(color="#2563EB", width=3.2)
    ))

    fig.update_layout(
        title="Unit Step Response Comparison — Time Domain",
        xaxis_title="Time [sec]",
        yaxis_title="Amplitude y(t)",
        template="plotly_white",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=60, b=40),
        height=460
    )
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="#E2E8F0", range=[0, t_max])
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="#E2E8F0")
    return fig


def create_pole_zero_figure(
    ol_poles: np.ndarray, ol_zeros: np.ndarray,
    cl_poles: np.ndarray, cl_zeros: np.ndarray
) -> go.Figure:
    """בונה מפת קטבים ואפסים במישור s."""
    fig = go.Figure()

    fig.add_vline(x=0, line_dash="dash", line_color="#EF4444", line_width=1.5)

    fig.add_trace(go.Scatter(
        x=np.real(ol_poles), y=np.imag(ol_poles),
        mode="markers", name="Open-Loop Poles (×)",
        marker=dict(symbol="x", size=11, color="#64748B")
    ))

    if len(ol_zeros) > 0:
        fig.add_trace(go.Scatter(
            x=np.real(ol_zeros), y=np.imag(ol_zeros),
            mode="markers", name="Open-Loop Zeros (○)",
            marker=dict(symbol="circle-open", size=10, color="#64748B", line=dict(width=2))
        ))

    fig.add_trace(go.Scatter(
        x=np.real(cl_poles), y=np.imag(cl_poles),
        mode="markers", name="Closed-Loop PID Poles (×)",
        marker=dict(symbol="x", size=13, color="#2563EB", line=dict(width=2))
    ))

    if len(cl_zeros) > 0:
        fig.add_trace(go.Scatter(
            x=np.real(cl_zeros), y=np.imag(cl_zeros),
            mode="markers", name="Closed-Loop Zeros (○)",
            marker=dict(symbol="circle-open", size=11, color="#10B981", line=dict(width=2))
        ))

    fig.update_layout(
        title="s-Plane Pole-Zero Map (Stability Analysis)",
        xaxis_title="Real Axis (σ) [sec⁻¹]",
        yaxis_title="Imaginary Axis (jω) [rad/sec]",
        template="plotly_white",
        height=440,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig.update_xaxes(showgrid=True, gridcolor="#E2E8F0", zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="#E2E8F0", zeroline=True)
    return fig


def create_bode_figure(ol_sys: signal.TransferFunction, l_sys: signal.TransferFunction) -> go.Figure:
    """בונה דיאגרמת בודה (Magnitude & Phase) עבור המערכת בחוג פתוח ועם בקר ה-PID."""
    w = np.logspace(-2, 2, 600)
    w_ol, mag_ol, phase_ol = signal.bode(ol_sys, w=w)
    w_l, mag_l, phase_l = signal.bode(l_sys, w=w)

    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True,
        vertical_spacing=0.1,
        subplot_titles=("Magnitude [dB]", "Phase [degrees]")
    )

    fig.add_trace(go.Scatter(
        x=w_ol, y=mag_ol, mode="lines", name="Plant G(jω)",
        line=dict(color="#94A3B8", width=2, dash="dot")
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=w_l, y=mag_l, mode="lines", name="Compensated Loop L(jω) = C(jω)G(jω)",
        line=dict(color="#2563EB", width=2.8)
    ), row=1, col=1)

    fig.add_hline(y=0.0, line_dash="dash", line_color="#10B981", row=1, col=1)

    fig.add_trace(go.Scatter(
        x=w_ol, y=phase_ol, mode="lines", name="Plant Phase",
        line=dict(color="#94A3B8", width=2, dash="dot"), showlegend=False
    ), row=2, col=1)

    fig.add_trace(go.Scatter(
        x=w_l, y=phase_l, mode="lines", name="Compensated Phase",
        line=dict(color="#2563EB", width=2.8), showlegend=False
    ), row=2, col=1)

    fig.add_hline(y=-180.0, line_dash="dash", line_color="#EF4444", row=2, col=1)

    fig.update_xaxes(type="log", showgrid=True, gridcolor="#E2E8F0", row=1, col=1)
    fig.update_xaxes(type="log", title_text="Frequency ω [rad/sec]", showgrid=True, gridcolor="#E2E8F0", row=2, col=1)
    fig.update_yaxes(title_text="Magnitude (dB)", showgrid=True, gridcolor="#E2E8F0", row=1, col=1)
    fig.update_yaxes(title_text="Phase (deg)", showgrid=True, gridcolor="#E2E8F0", row=2, col=1)

    fig.update_layout(
        template="plotly_white",
        height=520,
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.06, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=70, b=40)
    )
    return fig


# ==========================================
# 3. שכבת ממשק משתמש (Streamlit Dashboard)
# ==========================================

def render_metrics_row(metrics: Dict[str, Optional[float]]) -> None:
    """מציג שורת מדדי ביצועים הנדסיים."""
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        status = "✅ יציבה (Stable)" if metrics["stable"] else "⚠️ לא יציבה"
        st.metric("סטטוס יציבות", status)
    with col2:
        tr = f"{metrics['rise_time']:.3f} s" if metrics["rise_time"] is not None else "N/A"
        st.metric("זמן עלייה (Rise Time)", tr)
    with col3:
        ts = f"{metrics['settling_time']:.3f} s" if metrics["settling_time"] is not None else "לא התייצב"
        st.metric("זמן התייצבות (2%)", ts)
    with col4:
        mp = f"{metrics['overshoot']:.1f}%" if metrics["overshoot"] is not None else "N/A"
        st.metric("חריגה מרבית (Mp)", mp)
    with col5:
        ess = f"{metrics['ess']:.4f}" if metrics["ess"] is not None else "N/A"
        st.metric("שגיאת מצב מתמיד (ess)", ess)


def main():
    st.set_page_config(
        page_title="Control Systems & PID Simulator",
        page_icon="🎛️",
        layout="wide"
    )

    st.title("🎛️ סימולטור מערכות בקרה ובקר PID אינטראקטיבי")
    st.markdown(
        "סביבת סימולציה הנדסית לניתוח מערכות ליניאריות (LTI) במישור הזמן והתדר, בדיקת יציבות במישור $s$, וכוונון בקר **PID** בחוג סגור."
    )

    # --- סרגל צד: הגדרות המערכת והבקר ---
    with st.sidebar:
        st.header("1. הגדרת המערכת G(s)")
        presets = {
            "מערכת סדר שני (תת-מרוסנת)": ("1", "1, 2, 10"),
            "מודל מנוע DC (בקרת מהירות)": ("2", "0.5, 2.5, 2"),
            "מעגל RLC טורי": ("10", "1, 4, 25"),
            "מערכת סדר שלישי": ("1", "1, 6, 11, 6"),
            "מערכת בלתי יציבה ב-Open-Loop": ("1", "1, -1, 2"),
            "הגדרה ידנית חופשית": ("1", "1, 3, 2"),
        }
        selected_preset = st.selectbox("בחר מודל מערכת:", list(presets.keys()))
        default_num, default_den = presets[selected_preset]

        num_str = st.text_input(
            "מקדמי המונה (Numerator) - מופרדים בפסיק:",
            value=default_num,
            help="למשל: '1, 2' מייצג את הפולינום s + 2"
        )
        den_str = st.text_input(
            "מקדמי המכנה (Denominator) - מופרדים בפסיק:",
            value=default_den,
            help="למשל: '1, 2, 10' מייצג את הפולינום s^2 + 2s + 10"
        )

        st.divider()
        st.header("2. כוונון בקר PID")
        kp = st.slider("הגבר פרופורציונלי (Kp)", min_value=0.0, max_value=50.0, value=8.0, step=0.1)
        ki = st.slider("הגבר אינטגרלי (Ki)", min_value=0.0, max_value=50.0, value=12.0, step=0.1)
        kd = st.slider("הגבר נגזרתי (Kd)", min_value=0.0, max_value=20.0, value=1.5, step=0.05)

        st.divider()
        st.header("3. פרמטרי סימולציה")
        t_final = st.slider("אופק זמן לסימולציה [שניות]", min_value=2.0, max_value=60.0, value=12.0, step=1.0)
        show_ol_curve = st.checkbox("הצג השוואה לחוג פתוח בגרף", value=True)

    # --- בדיקות תקינות קלט ---
    num = parse_coefficients(num_str)
    den = parse_coefficients(den_str)

    if num is None or den is None:
        st.error("שגיאה בקלט: אנא הזן מקדמים מספריים חוקיים מופרדים בפסיקים.")
        st.stop()

    if len(num) > len(den):
        st.error("מערכת לא סיבתית (Improper Transfer Function): דרגת המונה חייבת להיות קטנה או שווה לדרגת המכנה.")
        st.stop()

    # --- חישוב מערכות ותגובות ---
    ol_sys = signal.TransferFunction(num, den)
    cl_num, cl_den, l_num, l_den = compute_closed_loop_tf(num, den, kp, ki, kd)
    cl_sys = signal.TransferFunction(cl_num, cl_den)
    l_sys = signal.TransferFunction(l_num, l_den)

    t_axis = np.linspace(0, t_final, 1200)
    t_ol, y_ol = signal.step(ol_sys, T=t_axis)
    t_cl, y_cl = signal.step(cl_sys, T=t_axis)

    ol_poles = np.roots(den)
    ol_zeros = np.roots(num) if len(num) > 1 else np.array([])
    cl_poles = np.roots(cl_den)
    cl_zeros = np.roots(cl_num) if len(cl_num) > 1 else np.array([])

    ol_metrics = calculate_step_metrics(t_ol, y_ol, ol_poles)
    cl_metrics = calculate_step_metrics(t_cl, y_cl, cl_poles)

    # --- תצוגת משוואות המערכת ---
    col_eq1, col_eq2, col_eq3 = st.columns(3)
    with col_eq1:
        st.markdown("**פונקציית התעבורה בחוג פתוח $G(s)$:**")
        st.latex(rf"G(s) = \frac{{{poly_to_latex(num)}}}{{{poly_to_latex(den)}}}")
    with col_eq2:
        st.markdown("**בקר $C(s)$ (PID Controller):**")
        st.latex(rf"C(s) = {kp:g} + \frac{{{ki:g}}}{{s}} + {kd:g}s")
    with col_eq3:
        st.markdown("**פונקציית התעבורה בחוג סגור $T(s)$:**")
        st.latex(rf"T(s) = \frac{{{poly_to_latex(cl_num)}}}{{{poly_to_latex(cl_den)}}}")

    st.divider()

    # --- מדדי ביצועים ---
    st.subheader("📊 מדדי ביצועים בחוג סגור (Closed-Loop Performance)")
    if not cl_metrics["stable"]:
        st.warning("⚠️ אזהרת יציבות: לחוג הסגור יש קטבים בחצי המישור הימני (RHP) – המערכת מתבדרת!")
    render_metrics_row(cl_metrics)

    with st.expander("הצג השוואה למדדי המערכת בחוג פתוח (Open-Loop Metrics)"):
        render_metrics_row(ol_metrics)

    # --- לשוניות גרפים וייצוא ---
    tab1, tab2, tab3 = st.tabs([
        "📈 תגובת מדרגה (Step Response)",
        "🎯 מפת קטבים ואפסים (s-Plane)",
        "🌊 תגובת תדר (Bode Plot)"
    ])

    with tab1:
        fig_step = create_step_response_figure(t_ol, y_ol, t_cl, y_cl, show_ol=show_ol_curve)
        st.plotly_chart(fig_step, use_container_width=True)

        csv_data = generate_csv_data(t_axis, y_ol, y_cl)
        st.download_button(
            label="📥 הורד נתוני סימולציה לקובץ CSV (עבור MATLAB / Excel)",
            data=csv_data,
            file_name="pid_simulation_results.csv",
            mime="text/csv"
        )

    with tab2:
        fig_pz = create_pole_zero_figure(ol_poles, ol_zeros, cl_poles, cl_zeros)
        st.plotly_chart(fig_pz, use_container_width=True)
        st.caption(
            "תנאי הכרחי ומספיק ליציבות BIBO: כל קטבי החוג הסגור (× כחול) חייבים להימצא בחצי המישור השמאלי (Re(s) < 0, משמאל לקו האדום)."
        )

    with tab3:
        fig_bode = create_bode_figure(ol_sys, l_sys)
        st.plotly_chart(fig_bode, use_container_width=True)
        st.caption(
            "דיאגרמת בודה מציגה את תגובת התדר של החוג הפתוח G(jω) מול החוג המפוצה L(jω) = C(jω)G(jω) לבחינת רוחב פס ושולי יציבות."
        )


if __name__ == "__main__":
    main()
