import streamlit as st
import math
import pandas as pd
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from translations import LANGUAGES
from storage import init_db, save_entry, load_entries, clear_entries, list_projects

# ─── PAGE CONFIG (must be first Streamlit command) ───────────────────────────
st.set_page_config(page_title="BAEL Structural Design Pro", layout="wide", page_icon="🏗️")

# ─── DATABASE INIT ────────────────────────────────────────────────────────────
init_db()

# ─── STATE INITIALIZATION ─────────────────────────────────────────────────────
if 'lang' not in st.session_state:
    st.session_state.lang = "Français"
if 'project' not in st.session_state:
    st.session_state.project = "default"

# ─── HELPERS ──────────────────────────────────────────────────────────────────
def t(key):
    return LANGUAGES[st.session_state.lang].get(key, f"[{key}]")


def translate_df_columns(df):
    mapping = {
        "Français": {"Selection": "Sélection", "Area (cm²)": "Section (cm²)",
                     "Spacing (cm)": "Espacement (cm)", "Hook (m)": "Crochet (m)"},
        "العربية":  {"Selection": "الاختيار",  "Area (cm²)": "المساحة (سم²)",
                     "Spacing (cm)": "التباعد (سم)",   "Hook (m)": "الخطاف (م)"},
        "English":  {},
    }
    return df.rename(columns=mapping.get(st.session_state.lang, {}))


def slenderness_badge(lam):
    if lam <= 35:
        return "success", t("slenderness_ok"),   f"λ = {lam:.1f}"
    elif lam <= 50:
        return "warning", t("slenderness_warn"), f"λ = {lam:.1f}"
    else:
        return "error",   t("slenderness_err"),  f"λ = {lam:.1f}"


# ─── PDF HELPERS ──────────────────────────────────────────────────────────────
_ACCENT = colors.HexColor("#1E3A5F")

def _pdf_title_style():
    return ParagraphStyle("title", fontSize=16, fontName="Helvetica-Bold",
                          alignment=TA_CENTER, spaceAfter=6)

def _pdf_sub_style():
    return ParagraphStyle("sub", fontSize=11, fontName="Helvetica-Bold",
                          spaceBefore=10, spaceAfter=4)

def _pdf_footer_style():
    return ParagraphStyle("footer", fontSize=7, textColor=colors.grey,
                          alignment=TA_CENTER)

def _build_element_story(entry: dict) -> list:
    """Return a ReportLab story (list of flowables) for one element.
    Used by both the single-element and full-project PDF exports.
    """
    story = []
    story.append(Paragraph(
        f"BAEL Structural Design — {entry.get('Repère', '—')} / {entry.get('Type', '—')}",
        _pdf_title_style()
    ))
    story.append(HRFlowable(width="100%", thickness=2, color=_ACCENT))
    story.append(Spacer(1, 0.4 * cm))

    # ── Meta table ────────────────────────────────────────────────────────────
    meta = [
        ["Repère / Ref", entry.get("Repère", "—"),
         "Type",         entry.get("Type",   "—")],
        ["Nu (MN)",      str(entry.get("Nu (MN)", "—")),
         "Dimensions (m)", str(entry.get("Dimensions (m)", "—"))],
    ]
    meta_table = Table(meta, colWidths=[4 * cm, 5 * cm, 4 * cm, 4 * cm])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (0, -1), _ACCENT),
        ("BACKGROUND",    (2, 0), (2, -1), _ACCENT),
        ("TEXTCOLOR",     (0, 0), (0, -1), colors.white),
        ("TEXTCOLOR",     (2, 0), (2, -1), colors.white),
        ("FONTNAME",      (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE",      (0, 0), (-1, -1), 9),
        ("GRID",          (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("ROWBACKGROUNDS",(1, 0), (1, -1), [colors.HexColor("#F5F7FA"), colors.white]),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 0.5 * cm))

    # ── Reinforcement table ───────────────────────────────────────────────────
    story.append(Paragraph("Reinforcement Summary", _pdf_sub_style()))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.lightgrey))
    story.append(Spacer(1, 0.2 * cm))

    fields_map = {
        "Section Adop. (cm²)": "Longitudinal Steel As (cm²)",
        "Cadres (Φt)":          "Stirrup Diameter Φt (mm)",
        "Espacement (cm)":      "Stirrup Spacing St (cm)",
        "Armatures A (cm²)":   "Steel Along A — Aa (cm²)",
        "Armatures B (cm²)":   "Steel Along B — Ab (cm²)",
    }
    rebar_data = [["Parameter", "Value"]]
    for key, label in fields_map.items():
        val = entry.get(key)
        if val is not None:
            rebar_data.append([label, str(val)])

    if len(rebar_data) > 1:
        rb_table = Table(rebar_data, colWidths=[9 * cm, 8 * cm])
        rb_table.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0), _ACCENT),
            ("TEXTCOLOR",     (0, 0), (-1, 0), colors.white),
            ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME",      (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE",      (0, 0), (-1, -1), 9),
            ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.HexColor("#F5F7FA"), colors.white]),
            ("GRID",          (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING",    (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(rb_table)

    story.append(Spacer(1, 0.8 * cm))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.lightgrey))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(
        "Generated by BAEL Structural Design Pro — For verification purposes only.",
        _pdf_footer_style()
    ))
    return story


def generate_element_pdf(entry: dict) -> bytes:
    """Single-element PDF sheet."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            topMargin=1.5 * cm, bottomMargin=1.5 * cm,
                            leftMargin=2 * cm, rightMargin=2 * cm)
    doc.build(_build_element_story(entry))
    buf.seek(0)
    return buf.read()


def generate_project_pdf(entries: list[dict]) -> bytes:
    """Full-project PDF — one page per element, reusing _build_element_story."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            topMargin=1.5 * cm, bottomMargin=1.5 * cm,
                            leftMargin=2 * cm, rightMargin=2 * cm)
    story = []
    for i, entry in enumerate(entries):
        if i > 0:
            story.append(PageBreak())
        story.extend(_build_element_story(entry))
    doc.build(story)
    buf.seek(0)
    return buf.read()


# ─── ENGINEERING ENGINES ──────────────────────────────────────────────────────
class ColumnsSystem:
    def __init__(self):
        self.standard_diameters = [12, 14, 16, 20]
        self.min_spacing = 0.05
        self.max_spacing = 0.40

    def pre_design(self, Nu, Lf, Yb=1.5, landa=35, alpha=0.708, fc28=25, st_type="rect"):
        if Nu <= 0:
            raise ValueError("Nu must be > 0")
        if Lf <= 0:
            raise ValueError("Lf must be > 0")
        Br = ((0.9 * Yb) / alpha) * (Nu / fc28)
        if st_type == "rect":
            a = math.ceil(((math.sqrt(12) * Lf) / landa) * 20) / 20
            a = max(a, 0.25)
            b_calc = math.ceil(((Br / (a - 0.02)) + 0.02) * 20) / 20
            b = a if b_calc < a else b_calc
            return {"type": "rect", "a": a, "b": b, "D": None, "Br_pre": round(Br, 4)}
        else:
            D1 = (2 * math.sqrt(Br / math.pi)) + 0.02
            D2 = ((4 * Lf) / landa)
            D = math.ceil(max(D1, D2) * 20) / 20
            return {"type": "circ", "a": None, "b": None, "D": D, "Br_pre": round(Br, 4)}

    def generate_column_options(self, required_area_cm2, perimeter_m, is_circular=False):
        possible_counts = [4, 6, 8, 10, 12, 14, 16, 20]
        if is_circular:
            possible_counts = [c for c in possible_counts if c >= 6]
        viable = []
        for count in possible_counts:
            for phi in self.standard_diameters:
                area = count * ((math.pi * (phi / 10) ** 2) / 4)
                if area >= required_area_cm2:
                    spacing = perimeter_m / count
                    if self.min_spacing <= spacing <= self.max_spacing:
                        viable.append({
                            "Selection":    f"{count} HA {phi}",
                            "Area (cm²)":   round(area, 2),
                            "Spacing (cm)": round(spacing * 100, 1),
                            "Excess":       round(area - required_area_cm2, 2)
                        })
        viable.sort(key=lambda x: x["Excess"])
        return viable[:5]

    def design(self, Nu, Lf, geometry, Yb=1.5, Ys=1.15, fe=500, fc28=25, charge="autre cas"):
        st_type = geometry["type"]
        a, b, D = geometry["a"], geometry["b"], geometry["D"]
        if st_type == "rect":
            landa = (math.sqrt(12) * Lf) / a
            Br = (a - 0.02) * (b - 0.02)
            B_area = a * b
            perimeter_u = 2 * (a + b)
        else:
            landa = (4 * Lf) / D
            Br = (math.pi * ((D - 0.02) ** 2)) / 4
            B_area = (math.pi * (D ** 2)) / 4
            perimeter_u = math.pi * D

        if landa <= 50:
            alpha = 0.85 / (1 + (0.2 * ((landa / 35) ** 2)))
        elif 50 < landa <= 70:
            alpha = 0.6 * ((50 / landa) ** 2)
        else:
            raise ValueError(f"Lambda = {landa:.1f} > 70 — Column too slender, redesign required.")

        divisor = {"avant 90j": 1.10, "avant 28j": 1.20, "autre cas": 1.0}.get(charge, 1.0)
        alpha /= divisor

        As_calc = ((Nu / alpha) - ((Br * fc28) / (0.9 * Yb))) * (Ys / fe) * 10000
        Amin = max(4 * perimeter_u, (0.2 / 100) * B_area * 10000)
        As_final = max(As_calc, Amin)

        options = self.generate_column_options(As_final, perimeter_u, is_circular=(st_type == "circ"))
        return {
            "factors":      {"Lambda": round(landa, 3), "Alpha": round(alpha, 3), "Br_reel_m2": round(Br, 4)},
            "sections_cm2": {"As_theoretical": round(As_calc, 2), "As_min": round(Amin, 2), "As_final": round(As_final, 2)},
            "options":      options,
            "lambda":       landa,
        }

    def design_transverse(self, phi_l_max, phi_l_min, a_m):
        phi_t = math.ceil((phi_l_max / 3))
        if phi_t <= 6:   phi_t = 6
        elif phi_t <= 8: phi_t = 8
        else:            phi_t = 10
        st_max_m = min(15 * (phi_l_min / 1000), 0.40, a_m + 0.10)
        st_final = math.floor(st_max_m * 100)
        return {"phi_t": phi_t, "st": st_final, "st_recouv": math.floor(st_final / 1.5)}


class IsolatedFootingSystem:
    def __init__(self):
        self.standard_diameters = [8, 10, 12, 14, 16, 20]

    def _validate_inputs(self, Nu, Nser):
        if Nu <= 0 or Nser <= 0:
            raise ValueError("Nu and Nser must be > 0")
        if Nser > Nu * 1.5:
            raise ValueError("Nser seems larger than expected relative to Nu — please check loads.")

    def design_custom(self, a, b, A, B, Nu, Nser, Fe, Ys, Gama_sol, fissuration="peu", footing_type="centree"):
        self._validate_inputs(Nu, Nser)
        actual_sigma = Nser / (A * B)
        if actual_sigma > Gama_sol:
            raise ValueError(f"Soil capacity exceeded! Actual: {actual_sigma:.3f} MPa > Limit: {Gama_sol} MPa")
        return self._compute_reinforcement(a, b, A, B, Nu, Fe, Ys, fissuration, footing_type)

    def generate_options(self, required_area_cm2, dimension_m):
        max_spacing_m = 0.20
        baseline_count = math.ceil(dimension_m / max_spacing_m) + 1
        allowed_counts = list(set([max(2, baseline_count - 1), baseline_count, baseline_count + 1]))
        viable_options = []
        for count in allowed_counts:
            for phi in self.standard_diameters:
                actual_area = count * ((math.pi * (phi / 10) ** 2) / 4)
                if actual_area >= required_area_cm2:
                    actual_spacing = dimension_m / (count - 1)
                    if actual_spacing <= max_spacing_m:
                        hook_e_m = max(0.15, 12 * (phi / 1000) + 0.06)
                        viable_options.append({
                            "Selection":    f"{count} HA {phi}",
                            "Area (cm²)":   round(actual_area, 2),
                            "Spacing (cm)": round(actual_spacing * 100, 1),
                            "Hook (m)":     round(hook_e_m, 2),
                            "Excess":       round(actual_area - required_area_cm2, 2)
                        })
        viable_options.sort(key=lambda x: x["Excess"])
        return viable_options[:5]

    def design_centered(self, a, b, Nu, Nser, Fe, Ys, Gama_sol, fissuration="peu"):
        self._validate_inputs(Nu, Nser)
        B = math.ceil(math.sqrt((b / a) * (Nser / Gama_sol)) * 20) / 20
        A = math.ceil(math.sqrt((a / b) * (Nser / Gama_sol)) * 20) / 20
        return self._compute_reinforcement(a, b, A, B, Nu, Fe, Ys, fissuration, "centree")

    def design_eccentric(self, a, b, Nu, Nser, Fe, Ys, Gama_sol, fissuration="peu"):
        self._validate_inputs(Nu, Nser)
        c = -(Nser / Gama_sol)
        b_quad = b - (2 * a)
        delta = (b_quad ** 2) - (4 * 2 * c)
        A = math.ceil(((-b_quad + math.sqrt(delta)) / 4) * 20) / 20
        B = math.ceil(((2 * A) - (2 * a) + b) * 20) / 20
        return self._compute_reinforcement(a, b, A, B, Nu, Fe, Ys, fissuration, "excentree")

    def _compute_reinforcement(self, a, b, A, B, Nu, Fe, Ys, fissuration, footing_type):
        overhang_A = (A - a) if footing_type == "excentree" else (A - a) / 2
        overhang_B = (B - b) / 2
        h = max(math.ceil((max(overhang_A, overhang_B) / 2 + 0.05) * 20) / 20, 0.20)
        d = h - 0.05
        Gama_su = Fe / Ys
        Aa_req = ((Nu * overhang_A) / (4 * d * Gama_su)) * 10000
        Ab_req = ((Nu * overhang_B) / (4 * d * Gama_su)) * 10000
        mult = {"peu": 1.0, "prejudiciable": 1.10, "tres_prejudiciable": 1.50}.get(fissuration, 1.0)
        Ab_req *= mult
        Aa_req *= mult
        return {
            "Type":     f"Isolée ({footing_type})",
            "Geometry": {"A": A, "B": B, "h": h, "d": d},
            "Ab_req":   round(Ab_req, 2),
            "Aa_req":   round(Aa_req, 2),
            "options_B": self.generate_options(Ab_req, B),
            "options_A": self.generate_options(Aa_req, A),
        }


class ContinuedFootingSystem(IsolatedFootingSystem):
    """Continuous (strip) footing under walls. Per-metre-length design."""

    def design_centered(self, a, Nu, Nser, Fe, Ys, Gama_sol, fissuration="peu"):
        self._validate_inputs(Nu, Nser)
        B = math.ceil((Nser / Gama_sol) * 20) / 20
        return self._compute_reinforcement(a, B, Nu, Fe, Ys, fissuration, "centree")

    def design_eccentric(self, a, Nu, Nser, Fe, Ys, Gama_sol, fissuration="peu"):
        self._validate_inputs(Nu, Nser)
        B = math.ceil((Nser / Gama_sol) * 20) / 20
        return self._compute_reinforcement(a, B, Nu, Fe, Ys, fissuration, "excentree")

    def _compute_reinforcement(self, a, B, Nu, Fe, Ys, fissuration, footing_type):
        overhang_B = (B - a) if footing_type == "excentree" else (B - a) / 2
        h = max(math.ceil((overhang_B / 2 + 0.05) * 20) / 20, 0.20)
        d = h - 0.05
        Gama_su = Fe / Ys
        As_req = ((Nu * overhang_B) / (4 * d * Gama_su)) * 10000
        Ar_req = max(As_req / 4, 2.0)
        mult = {"peu": 1.0, "prejudiciable": 1.10, "tres_prejudiciable": 1.50}.get(fissuration, 1.0)
        As_req *= mult
        Ar_req *= mult
        return {
            "Type":     f"Filante ({footing_type})",
            "Geometry": {"A": 1.0, "B": B, "h": h, "d": d},
            "Ab_req":   round(As_req, 2),
            "Aa_req":   round(Ar_req, 2),
            "options_B": self.generate_options(As_req, 1.0),
            "options_A": self.generate_options(Ar_req, B),
        }


# ─── GLOBAL STYLES ────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #1E3A5F 0%, #2E5090 100%);
        border-radius: 10px; padding: 12px 16px; margin-bottom: 8px; color: white;
    }
    .section-header {
        font-size: 1.1rem; font-weight: 700; color: #1E3A5F;
        border-left: 4px solid #1E3A5F; padding-left: 10px; margin: 14px 0 8px 0;
    }
</style>
""", unsafe_allow_html=True)

if st.session_state.lang == "العربية":
    st.markdown("""
    <style>
        body, .stApp { direction: rtl; text-align: right; }
        .st-emotion-cache-1kyxreq { justify-content: flex-end; }
    </style>
    """, unsafe_allow_html=True)

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
st.sidebar.selectbox(t("lang_selector"), options=["Français", "English", "العربية"], key="lang")
st.sidebar.divider()
st.sidebar.title(t("nav_title"))
app_mode = st.sidebar.radio(t("select_module"), [t("col_design"), t("foot_design")])

# ── Project selector ──────────────────────────────────────────────────────────
st.sidebar.divider()
st.sidebar.subheader("📁 Project")
existing_projects = list_projects()
new_project = st.sidebar.text_input("Project name", value=st.session_state.project)
if new_project and new_project != st.session_state.project:
    st.session_state.project = new_project
    st.rerun()

if existing_projects:
    chosen = st.sidebar.selectbox("Load project", ["— new —"] + existing_projects)
    if chosen != "— new —" and chosen != st.session_state.project:
        st.session_state.project = chosen
        st.rerun()

st.sidebar.divider()


# ══════════════════════════════════════════════════════════════════════════════
# COLUMN DESIGNER
# ══════════════════════════════════════════════════════════════════════════════
if app_mode == t("col_design"):
    st.title(f"🏛️ {t('col_design')}")
    st.markdown(t("col_desc"))

    with st.sidebar:
        st.header(t("input_params"))
        element_id = st.text_input(t("element_ref"), value="P(A:1)")

        with st.expander(t("geom_type"), expanded=True):
            st_type = st.selectbox(t("col_shape"), ["rect", "circ"],
                                   format_func=lambda x: t(f"shape_{x}"))
            lf_val = st.number_input(t("buckling_len"), value=3.00, step=0.10, min_value=0.10)

        with st.expander(t("loads_dur"), expanded=True):
            nu_col = st.number_input("Nu (MN)", value=0.640, format="%.3f", min_value=0.001)
            charge_duration = st.selectbox(
                t("load_app"),
                ["autre_cas", "avant_90j", "avant_28j"],
                format_func=lambda x: t(f"charge_{x}")
            )
            charge_engine = charge_duration.replace("_", " ")

        with st.expander(t("mat_const"), expanded=False):
            fc28_val = st.number_input(t("concrete_fc28"), value=25, step=5, min_value=15)
            fe_col   = st.selectbox(t("steel_fe"), [400, 500], index=1)
            yb_val   = st.number_input("Gamma_b", value=1.50)
            ys_col   = st.number_input("Gamma_s", value=1.15)

        with st.expander(t("long_rebar"), expanded=False):
            phi_l_max = st.selectbox(t("phi_max"), [12, 14, 16, 20, 25], index=1)
            phi_l_min = st.selectbox(t("phi_min"), [12, 14, 16, 20, 25], index=0)

    col_engine = ColumnsSystem()
    try:
        geom        = col_engine.pre_design(Nu=nu_col, Lf=lf_val, Yb=yb_val, fc28=fc28_val, st_type=st_type)
        steel       = col_engine.design(Nu=nu_col, Lf=lf_val, geometry=geom, Yb=yb_val,
                                        Ys=ys_col, fe=fe_col, fc28=fc28_val, charge=charge_engine)
        a_m         = min(geom['a'], geom['b']) if st_type == 'rect' else geom['D']
        trans_steel = col_engine.design_transverse(phi_l_max, phi_l_min, a_m)

        # ── Slenderness badge ──────────────────────────────────────────────────
        lam = steel["lambda"]
        badge_type, badge_label, badge_val = slenderness_badge(lam)
        getattr(st, badge_type)(f"{badge_label} — {badge_val}")

        # ── Formwork ──────────────────────────────────────────────────────────
        st.markdown(f"<div class='section-header'>{t('res_formwork')}</div>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        if st_type == "rect":
            c1.metric(t("width"),  f"{geom['a']:.2f} m")
            c2.metric(t("length"), f"{geom['b']:.2f} m")
        else:
            c1.metric(t("diameter"), f"{geom['D']:.2f} m")
        c3.metric(t("theo_br"), f"{geom['Br_pre']:.4f} m²")
        st.divider()

        # ── Longitudinal steel ────────────────────────────────────────────────
        st.markdown(f"<div class='section-header'>{t('res_steel')}</div>", unsafe_allow_html=True)
        sc1, sc2, sc3 = st.columns(3)
        sc1.metric(t("theo_sec"),  f"{steel['sections_cm2']['As_theoretical']} cm²")
        sc2.metric(t("min_sec"),   f"{steel['sections_cm2']['As_min']} cm²")
        sc3.metric(t("final_sec"), f"{steel['sections_cm2']['As_final']} cm²",
                   delta=t("exec_val"), delta_color="off")
        st.caption(t("rebar_options"))
        if steel['options']:
            df_col = pd.DataFrame(steel['options']).drop(columns=["Excess"])
            st.dataframe(translate_df_columns(df_col), use_container_width=True, hide_index=True)
        else:
            st.warning(t("no_rebar"))
        st.divider()

        # ── Transverse steel ──────────────────────────────────────────────────
        st.markdown(f"<div class='section-header'>{t('res_transverse')}</div>", unsafe_allow_html=True)
        tc1, tc2, tc3 = st.columns(3)
        tc1.metric(t("phi_t_label"),  f"{trans_steel['phi_t']} mm")
        tc2.metric(t("spacing"),      f"{trans_steel['st']} cm")
        tc3.metric(t("spacing_crit"), f"{trans_steel['st_recouv']} cm")
        st.divider()

        with st.expander(t("res_factors")):
            st.json(steel['factors'])

        # ── Save & Export ─────────────────────────────────────────────────────
        dim_str = (f"{geom['a']:.2f} x {geom['b']:.2f}" if st_type == "rect"
                   else f"∅ {geom['D']:.2f}")
        log_entry = {
            "Repère":              element_id,
            "Type":                "Poteau",
            "Nu (MN)":             nu_col,
            "Section Adop. (cm²)": steel['sections_cm2']['As_final'],
            "Cadres (Φt)":         trans_steel['phi_t'],
            "Espacement (cm)":     trans_steel['st'],
            "Dimensions (m)":      dim_str,
            "Armatures A (cm²)":   None,
            "Armatures B (cm²)":   None,
        }

        save_col, pdf_col = st.columns(2)
        with save_col:
            if st.button(t("save_project"), key="save_col"):
                save_entry(log_entry, project=st.session_state.project)
                st.success(t("saved_ok").format(element_id))
        with pdf_col:
            st.download_button(
                label=t("export_pdf_btn"),
                data=generate_element_pdf(log_entry),
                file_name=f"BAEL_{element_id.replace('/', '-')}.pdf",
                mime="application/pdf",
                key="pdf_col"
            )

    except ValueError as e:
        st.error(f"{t('design_err')} {e}")


# ══════════════════════════════════════════════════════════════════════════════
# FOOTING DESIGNER
# ══════════════════════════════════════════════════════════════════════════════
elif app_mode == t("foot_design"):
    st.title(f"🏗️ {t('foot_design')}")
    st.markdown(t("foot_desc"))

    with st.sidebar:
        st.header(t("input_params"))
        element_id   = st.text_input(t("element_ref"), value="S(A:1)")
        cat_semelle  = st.radio(t("foot_cat"), ["iso", "cont"],
                                format_func=lambda x: t(f"cat_{x}"))
        type_semelle = st.radio(t("foot_type"), ["centree", "excentree"],
                                format_func=lambda x: t(f"type_{x}"))
        st.divider()

        if cat_semelle == "iso":
            st.subheader(t("design_mode"))
            calc_mode = st.radio(t("method"), ["Auto (Homothétique)", "Manuel (Imposé)"])
            if calc_mode == "Manuel (Imposé)":
                with st.expander(t("imposed_dims"), expanded=True):
                    custom_A = st.number_input(t("footing_width"), value=1.50, step=0.05)
                    custom_B = st.number_input(t("footing_length"), value=1.50, step=0.05)
        else:
            calc_mode = "Auto (Homothétique)"

        with st.expander(t("col_dims"), expanded=True):
            col_a = st.number_input(t("width_a"), value=0.20, step=0.05, min_value=0.10)
            if cat_semelle == "iso":
                col_b = st.number_input(t("length_b"), value=0.40, step=0.05, min_value=0.10)
            else:
                col_b = 1.0

        with st.expander(t("loads_soil"), expanded=True):
            nu    = st.number_input("Nu",   value=0.462, format="%.3f", min_value=0.001)
            nser  = st.number_input("Nser", value=0.334, format="%.3f", min_value=0.001)
            sigma_sol = st.number_input(t("soil_cap"), value=0.25, step=0.05, min_value=0.05)

        with st.expander(t("mat_const"), expanded=False):
            fe   = st.selectbox(t("steel_fe"), [400, 500], index=1)
            ys   = st.number_input("Gamma_s", value=1.15)
            fiss = st.selectbox(t("crack_risk"),
                                ["peu", "prejudiciable", "tres_prejudiciable"],
                                format_func=lambda x: t(f"fiss_{x}"))

    engine = IsolatedFootingSystem() if cat_semelle == "iso" else ContinuedFootingSystem()

    try:
        if cat_semelle == "iso":
            if calc_mode == "Auto (Homothétique)":
                if type_semelle == "centree":
                    res = engine.design_centered(col_a, col_b, nu, nser, fe, ys, sigma_sol, fiss)
                else:
                    res = engine.design_eccentric(col_a, col_b, nu, nser, fe, ys, sigma_sol, fiss)
            else:
                res = engine.design_custom(col_a, col_b, custom_A, custom_B,
                                           nu, nser, fe, ys, sigma_sol, fiss, type_semelle)
        else:
            if type_semelle == "centree":
                res = engine.design_centered(col_a, nu, nser, fe, ys, sigma_sol, fiss)
            else:
                res = engine.design_eccentric(col_a, nu, nser, fe, ys, sigma_sol, fiss)

        # ── Geometry results ──────────────────────────────────────────────────
        st.markdown(f"<div class='section-header'>{t('res_footing')} {res['Type']}</div>",
                    unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        dim_a_label = (t("width").replace("(a)", "(A = 1.0ml)") if cat_semelle == "cont"
                       else t("width").replace("(a)", "(A)"))
        c1.metric(dim_a_label,                      f"{res['Geometry']['A']:.2f} m")
        c2.metric(t("length").replace("(b)", "(B)"), f"{res['Geometry']['B']:.2f} m")
        c3.metric(t("height_h"),                     f"{res['Geometry']['h']:.2f} m")
        st.divider()

        # ── Rebar tables ──────────────────────────────────────────────────────
        col_left, col_right = st.columns(2)
        with col_left:
            st.subheader(f"{t('rebar_b')} ({res['Geometry']['B']:.2f}m)")
            st.caption(f"{t('req_area')} : {res['Ab_req']:.2f} cm²"
                       + ("/ml" if cat_semelle == "cont" else ""))
            if res['options_B']:
                df_b = pd.DataFrame(res['options_B']).drop(columns=["Excess"])
                st.dataframe(translate_df_columns(df_b), use_container_width=True, hide_index=True)
            else:
                st.error(t("no_rebar"))

        with col_right:
            st.subheader(f"{t('rebar_a')} ({res['Geometry']['A']:.2f}m)")
            st.caption(f"{t('req_area')} : {res['Aa_req']:.2f} cm²"
                       + (" (Répartition)" if cat_semelle == "cont" else ""))
            if res['options_A']:
                df_a = pd.DataFrame(res['options_A']).drop(columns=["Excess"])
                st.dataframe(translate_df_columns(df_a), use_container_width=True, hide_index=True)
            else:
                st.error(t("no_rebar"))

        st.info(t("strategy_note"))
        st.divider()

        # ── Save & Export ─────────────────────────────────────────────────────
        log_entry = {
            "Repère":              element_id,
            "Type":                res['Type'],
            "Nu (MN)":             nu,
            "Section Adop. (cm²)": None,
            "Cadres (Φt)":         None,
            "Espacement (cm)":     None,
            "Dimensions (m)":      f"{res['Geometry']['A']:.2f} x {res['Geometry']['B']:.2f}",
            "Armatures A (cm²)":   res['Aa_req'],
            "Armatures B (cm²)":   res['Ab_req'],
        }

        save_col, pdf_col = st.columns(2)
        with save_col:
            if st.button(t("save_project"), key="save_foot"):
                save_entry(log_entry, project=st.session_state.project)
                st.success(t("saved_ok").format(element_id))
        with pdf_col:
            st.download_button(
                label=t("export_pdf_btn"),
                data=generate_element_pdf(log_entry),
                file_name=f"BAEL_{element_id.replace('/', '-')}.pdf",
                mime="application/pdf",
                key="pdf_foot"
            )

    except ValueError as e:
        st.error(f"⚠️ {e}")


# ─── PROJECT LOG & EXPORT ─────────────────────────────────────────────────────
st.divider()
st.header(f"{t('project_log')} — {st.session_state.project}")

project_entries = load_entries(project=st.session_state.project)

if project_entries:
    log_df = pd.DataFrame(project_entries)
    st.dataframe(log_df, use_container_width=True)

    dl1, dl2, dl3 = st.columns([2, 2, 1])
    with dl1:
        csv = log_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label=t("export_csv"),
            data=csv,
            file_name=f"bael_{st.session_state.project}.csv",
            mime="text/csv"
        )
    with dl2:
        st.download_button(
            label="📄 Export Full Project PDF",
            data=generate_project_pdf(project_entries),
            file_name=f"BAEL_{st.session_state.project}.pdf",
            mime="application/pdf",
            key="pdf_project"
        )
    with dl3:
        if st.button(t("clear_log")):
            clear_entries(project=st.session_state.project)
            st.rerun()
else:
    st.caption(t("no_elements"))
