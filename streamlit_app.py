import streamlit as st
import math
import pandas as pd

# --- TRANSLATION DICTIONARY ---
LANGUAGES = {
    "Français": {
        "app_title": "Dimensionnement BAEL Pro",
        "nav_title": "Navigation",
        "select_module": "Sélectionnez le Module :",
        "col_design": "Dimensionnement Poteau",
        "foot_design": "Dimensionnement Semelles",
        "lang_selector": "🌍 Langue",
        # UI Base
        "input_params": "1. Paramètres d'Entrée",
        "geom_type": "Type de Géométrie",
        "loads_dur": "Charges et Durée",
        "mat_const": "Contraintes Matériaux",
        "concrete_fc28": "Béton fc28 (MPa)",
        "steel_fe": "Acier Fe (MPa)",
        # Column UI
        "col_desc": "Outil de dimensionnement BAEL automatisé pour coffrage et ferraillage longitudinal et transversal.",
        "col_shape": "Forme du Poteau",
        "shape_rect": "Rectangulaire",
        "shape_circ": "Circulaire",
        "buckling_len": "Longueur de flambement Lf (m)",
        "load_app": "Application de la charge",
        "charge_autre_cas": "Autre cas (> 90 jours)",
        "charge_avant_90j": "Avant 90 jours",
        "charge_avant_28j": "Avant 28 jours",
        "long_rebar": "Barres Longitudinales (Prévues)",
        "phi_max": "Diamètre Max (Φ mm)",
        "phi_min": "Diamètre Min (Φ mm)",
        "res_formwork": "1. Dimensions du Coffrage",
        "width": "Largeur (a)",
        "length": "Longueur (b)",
        "diameter": "Diamètre (D)",
        "theo_br": "Section Br Théorique",
        "res_steel": "2. Ferraillage Longitudinal",
        "theo_sec": "Section Théorique",
        "min_sec": "Section Minimale",
        "final_sec": "Section Finale Adoptée",
        "exec_val": "Valeur d'exécution",
        "rebar_options": "Options de Ferraillage (Longitudinal)",
        "res_transverse": "3. Ferraillage Transversal",
        "phi_t_label": "Diamètre des Cadres (Φt)",
        "spacing": "Espacement courant (St)",
        "spacing_crit": "Espacement zone de recouvrement",
        "res_factors": "Facteurs de Vérification",
        "design_err": "Erreur de conception :",
        # Footing UI
        "foot_desc": "Outil professionnel BAEL pour semelles isolées (poteaux) et filantes (murs).",
        "foot_cat": "Catégorie de Semelle",
        "cat_iso": "Isolée (Sous Poteau)",
        "cat_cont": "Filante (Sous Mur)",
        "foot_type": "Position de la Charge",
        "type_centree": "Centrée",
        "type_excentree": "Excentrée (Rive)",
        "col_dims": "Dimensions du Porteur (m)",
        "width_a": "Épaisseur/Largeur (a) - Axe x",
        "length_b": "Longueur (b) - Axe y",
        "loads_soil": "Charges et Sol (MN ou MN/ml)",
        "soil_cap": "Contrainte du Sol (MPa)",
        "crack_risk": "Fissuration",
        "fiss_peu": "Peu préjudiciable",
        "fiss_prejudiciable": "Préjudiciable",
        "fiss_tres_prejudiciable": "Très préjudiciable",
        # Footing Results
        "res_footing": "Résultats :",
        "height_h": "Hauteur (h)",
        "rebar_b": "Armatures Principales (Transversales // à B)",
        "rebar_a": "Armatures (Longitudinales // à A)",
        "req_area": "Section requise",
        "no_rebar": "Aucune armature viable trouvée.",
        "strategy_note": "**Stratégie :** Les options minimisent les pertes matérielles. 'Crochet (m)' indique l'ancrage requis."
    },
    "English": {
        "app_title": "Structural Design Pro",
        "nav_title": "Navigation",
        "select_module": "Select Module:",
        "col_design": "Column Designer",
        "foot_design": "Footing Designer",
        "lang_selector": "🌍 Language",
        # UI Base
        "input_params": "1. Input Parameters",
        "geom_type": "Geometry Type",
        "loads_dur": "Loads & Duration",
        "mat_const": "Material Constraints",
        "concrete_fc28": "Concrete fc28 (MPa)",
        "steel_fe": "Steel Fe (MPa)",
        # Column UI
        "col_desc": "Automated BAEL formwork sizing, longitudinal, and transverse steel calculation.",
        "col_shape": "Column Shape",
        "shape_rect": "Rectangular",
        "shape_circ": "Circular",
        "buckling_len": "Buckling Length Lf (m)",
        "load_app": "Load Application",
        "charge_autre_cas": "Other (> 90 days)",
        "charge_avant_90j": "Before 90 days",
        "charge_avant_28j": "Before 28 days",
        "long_rebar": "Planned Longitudinal Rebar",
        "phi_max": "Max Diameter (Φ mm)",
        "phi_min": "Min Diameter (Φ mm)",
        "res_formwork": "1. Formwork Dimensions",
        "width": "Width (a)",
        "length": "Length (b)",
        "diameter": "Diameter (D)",
        "theo_br": "Theoretical Br Section",
        "res_steel": "2. Longitudinal Reinforcement",
        "theo_sec": "Theoretical Area",
        "min_sec": "Minimum Area",
        "final_sec": "Final Adopted Area",
        "exec_val": "Execution Value",
        "rebar_options": "Reinforcement Options (Longitudinal)",
        "res_transverse": "3. Transverse Reinforcement",
        "phi_t_label": "Stirrup Diameter (Φt)",
        "spacing": "Standard Spacing (St)",
        "spacing_crit": "Overlap Zone Spacing",
        "res_factors": "Verification Factors",
        "design_err": "Design Error:",
        # Footing UI
        "foot_desc": "Professional BAEL tool for isolated (columns) and continuous (walls) footings.",
        "foot_cat": "Footing Category",
        "cat_iso": "Isolated (Column)",
        "cat_cont": "Continuous (Wall)",
        "foot_type": "Load Position",
        "type_centree": "Centered",
        "type_excentree": "Eccentric (Edge)",
        "col_dims": "Support Dimensions (m)",
        "width_a": "Thickness/Width (a) - X axis",
        "length_b": "Length (b) - Y axis",
        "loads_soil": "Loads & Soil (MN or MN/m)",
        "soil_cap": "Soil Capacity (MPa)",
        "crack_risk": "Cracking Risk",
        "fiss_peu": "Not Harmful (Peu)",
        "fiss_prejudiciable": "Harmful",
        "fiss_tres_prejudiciable": "Highly Harmful",
        # Footing Results
        "res_footing": "Results:",
        "height_h": "Height (h)",
        "rebar_b": "Main Rebar (Transverse // to B)",
        "rebar_a": "Rebar (Longitudinal // to A)",
        "req_area": "Required Area",
        "no_rebar": "No viable rebar found.",
        "strategy_note": "**Strategy:** Options minimize steel waste. 'Hook (m)' denotes required anchorage."
    },
    "العربية": {
        "app_title": "التصميم الإنشائي الاحترافي",
        "nav_title": "التنقل",
        "select_module": "اختر الوحدة:",
        "col_design": "تصميم الأعمدة",
        "foot_design": "تصميم القواعد",
        "lang_selector": "🌍 اللغة",
        # UI Base
        "input_params": "1. معلمات الإدخال",
        "geom_type": "نوع الهندسة",
        "loads_dur": "الأحمال والمدة",
        "mat_const": "قيود المواد",
        "concrete_fc28": "مقاومة الخرسانة fc28 (MPa)",
        "steel_fe": "إجهاد الخضوع للصلب Fe (MPa)",
        # Column UI
        "col_desc": "أداة آلية لحساب أبعاد القوالب وحديد التسليح الطولي والعرضي وفقاً لكود BAEL.",
        "col_shape": "شكل العمود",
        "shape_rect": "مستطيل",
        "shape_circ": "دائري",
        "buckling_len": "طول الانبعاج Lf (م)",
        "load_app": "تطبيق الحمل",
        "charge_autre_cas": "حالات أخرى (> 90 يوم)",
        "charge_avant_90j": "قبل 90 يوم",
        "charge_avant_28j": "قبل 28 يوم",
        "long_rebar": "التسليح الطولي المخطط",
        "phi_max": "أقصى قطر (Φ مم)",
        "phi_min": "أدنى قطر (Φ مم)",
        "res_formwork": "1. أبعاد القالب",
        "width": "العرض (a)",
        "length": "الطول (b)",
        "diameter": "القطر (D)",
        "theo_br": "المقطع النظري Br",
        "res_steel": "2. التسليح الطولي",
        "theo_sec": "المساحة النظرية",
        "min_sec": "المساحة الدنيا",
        "final_sec": "المساحة النهائية المعتمدة",
        "exec_val": "قيمة التنفيذ",
        "rebar_options": "خيارات التسليح (الطولي)",
        "res_transverse": "3. التسليح العرضي",
        "phi_t_label": "قطر الكانات (Φt)",
        "spacing": "التباعد العادي (St)",
        "spacing_crit": "التباعد في منطقة التراكب",
        "res_factors": "عوامل التحقق",
        "design_err": "خطأ في التصميم:",
        # Footing UI
        "foot_desc": "أداة احترافية لحساب القواعد المنفصلة (الأعمدة) والمستمرة (الجدران).",
        "foot_cat": "فئة القاعدة",
        "cat_iso": "منفصلة (لعمود)",
        "cat_cont": "مستمرة (لجدار)",
        "foot_type": "موضع الحمل",
        "type_centree": "مركزية",
        "type_excentree": "لامركزية (طرفية)",
        "col_dims": "أبعاد العنصر الحامل (م)",
        "width_a": "السماكة/العرض (a) - محور X",
        "length_b": "الطول (b) - محور Y",
        "loads_soil": "الأحمال والتربة (MN أو MN/m)",
        "soil_cap": "قدرة تحمل التربة (MPa)",
        "crack_risk": "خطر التشققات",
        "fiss_peu": "غير ضار (Peu)",
        "fiss_prejudiciable": "ضار",
        "fiss_tres_prejudiciable": "ضار جداً",
        # Footing Results
        "res_footing": "النتائج:",
        "height_h": "الارتفاع (h)",
        "rebar_b": "التسليح الرئيسي (عرضي // لـ B)",
        "rebar_a": "التسليح (طولي // لـ A)",
        "req_area": "المساحة المطلوبة",
        "no_rebar": "لم يتم العثور على تسليح مناسب.",
        "strategy_note": "**الاستراتيجية:** تقلل الخيارات من هدر الصلب. يشير 'الخطاف (م)' إلى طول التثبيت المطلوب."
    }
}

# --- STATE INITIALIZATION & HELPER ---
if 'lang' not in st.session_state:
    st.session_state.lang = "Français"
if 'project_log' not in st.session_state:
    st.session_state.project_log = []

def t(key):
    return LANGUAGES[st.session_state.lang].get(key, f"Missing translation: {key}")

def translate_df_columns(df):
    if st.session_state.lang == "العربية":
        return df.rename(columns={"Selection": "الاختيار", "Area (cm²)": "المساحة (سم²)", "Spacing (cm)": "التباعد (سم)", "Excess": "الفائض", "Hook (m)": "الخطاف (م)"})
    elif st.session_state.lang == "Français":
        return df.rename(columns={"Selection": "Sélection", "Area (cm²)": "Section (cm²)", "Spacing (cm)": "Espacement (cm)", "Excess": "Excès", "Hook (m)": "Crochet (m)"})
    return df

# --- LOGIC ENGINES ---
class ColumnsSystem:
    def __init__(self):
        self.standard_diameters = [12, 14, 16, 20]
        self.min_spacing = 0.05
        self.max_spacing = 0.40
        
    def pre_design(self, Nu, Lf, Yb=1.5, landa=35, alpha=0.708, fc28=25, st_type="rect"):
        Br = ((0.9 * Yb) / alpha) * (Nu / fc28)
        if st_type == "rect":
            a = math.ceil(((math.sqrt(12) * Lf) / landa) * 20) / 20
            b_calc = math.ceil(((Br / (a - 0.02)) + 0.02) * 20) / 20
            b = a if b_calc < a else b_calc
            return {"type": "rect", "a": a, "b": b, "D": None, "Br_pre": round(Br, 4)}
        elif st_type == "circ":
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
                area = count * ((math.pi * (phi / 10)**2) / 4)
                if area >= required_area_cm2:
                    spacing = perimeter_m / count
                    if self.min_spacing <= spacing <= self.max_spacing:
                        viable.append({
                            "Selection": f"{count} HA {phi}",
                            "Area (cm²)": round(area, 2),
                            "Spacing (cm)": round(spacing * 100, 1),
                            "Excess": round(area - required_area_cm2, 2)
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
            Br = (math.pi * ((D - 0.02)**2)) / 4
            B_area = (math.pi * (D**2)) / 4
            perimeter_u = math.pi * D

        if landa <= 50:
            alpha = 0.85 / (1 + (0.2 * ((landa / 35)**2)))
        elif 50 < landa <= 70:
            alpha = 0.6 * ((50 / landa)**2)
        else:
            raise ValueError("Lambda > 70")

        divisor = {"avant 90j": 1.10, "avant 28j": 1.20, "autre cas": 1.0}.get(charge, 1.0)
        alpha /= divisor

        As_calc = ((Nu / alpha) - ((Br * fc28) / (0.9 * Yb))) * (Ys / fe) * 10000
        Amin = max(4 * perimeter_u, (0.2 / 100) * B_area * 10000)
        As_final = max(As_calc, Amin)

        options = self.generate_column_options(As_final, perimeter_u, is_circular=(st_type == "circ"))

        return {
            "factors": {"Landa": round(landa, 3), "Alpha": round(alpha, 3), "Br_reel_m2": round(Br, 4)},
            "sections_cm2": {"As_theoretical": round(As_calc, 2), "As_min": round(Amin, 2), "As_final": round(As_final, 2)},
            "options": options
        }

    def design_transverse(self, phi_l_max, phi_l_min, a_m):
        phi_t = math.ceil((phi_l_max / 3))
        if phi_t <= 6: phi_t = 6
        elif phi_t <= 8: phi_t = 8
        else: phi_t = 10
        st_max_m = min(15 * (phi_l_min / 1000), 0.40, a_m + 0.10)
        st_final = math.floor(st_max_m * 100)
        return {"phi_t": phi_t, "st": st_final, "st_recouv": math.floor(st_final / 1.5)}

class IsolatedFootingSystem:
    def __init__(self):
        self.standard_diameters = [8, 10, 12, 14, 16, 20]

    def generate_options(self, required_area_cm2, dimension_m):
        max_spacing_m = 0.20
        baseline_count = math.ceil(dimension_m / max_spacing_m) + 1
        allowed_counts = list(set([max(2, baseline_count - 1), baseline_count, baseline_count + 1]))
        viable_options = []

        for count in allowed_counts:
            for phi in self.standard_diameters:
                actual_area = count * ((math.pi * (phi / 10)**2) / 4)
                if actual_area >= required_area_cm2:
                    actual_spacing = dimension_m / (count - 1)
                    if actual_spacing <= max_spacing_m:
                        hook_e_m = max(0.15, 12 * (phi / 1000) + 0.06)
                        viable_options.append({
                            "Selection": f"{count} HA {phi}",
                            "Area (cm²)": round(actual_area, 2),
                            "Spacing (cm)": round(actual_spacing * 100, 1),
                            "Hook (m)": round(hook_e_m, 2),
                            "Excess": round(actual_area - required_area_cm2, 2)
                        })
        viable_options.sort(key=lambda x: x["Excess"])
        return viable_options[:5]

    def design_centered(self, a, b, Nu, Nser, Fe, Ys, Gama_sol, fissuration="peu"):
        B = math.ceil(math.sqrt((b/a) * (Nser/Gama_sol)) * 20) / 20
        A = math.ceil(math.sqrt((a/b) * (Nser/Gama_sol)) * 20) / 20
        return self._compute_reinforcement(a, b, A, B, Nu, Fe, Ys, fissuration, "centree")

    def design_eccentric(self, a, b, Nu, Nser, Fe, Ys, Gama_sol, fissuration="peu"):
        c = - (Nser / Gama_sol)
        b_quad = b - (2 * a)
        delta = (b_quad**2) - (4 * 2 * c)
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
            "Type": f"Isolée ({footing_type})",
            "Geometry": {"A": A, "B": B, "h": h, "d": d},
            "Ab_req": round(Ab_req, 2),
            "Aa_req": round(Aa_req, 2),
            "options_B": self.generate_options(Ab_req, B),
            "options_A": self.generate_options(Aa_req, A)
        }

class ContinuedFootingSystem(IsolatedFootingSystem):
    def design_centered(self, a, Nu, Nser, Fe, Ys, Gama_sol, fissuration="peu"):
        B = math.ceil((Nser / Gama_sol) * 20) / 20
        return self._compute_reinforcement(a, 1.0, B, Nu, Fe, Ys, fissuration, "centree")

    def design_eccentric(self, a, Nu, Nser, Fe, Ys, Gama_sol, fissuration="peu"):
        B = math.ceil((Nser / Gama_sol) * 20) / 20
        return self._compute_reinforcement(a, 1.0, B, Nu, Fe, Ys, fissuration, "excentree")

    def _compute_reinforcement(self, a, A, B, Nu, Fe, Ys, fissuration, footing_type):
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
            "Type": f"Filante ({footing_type})",
            "Geometry": {"A": A, "B": B, "h": h, "d": d},
            "Ab_req": round(As_req, 2), 
            "Aa_req": round(Ar_req, 2), 
            "options_B": self.generate_options(As_req, 1.0), 
            "options_A": self.generate_options(Ar_req, B)    
        }

# --- STREAMLIT UI ---
st.set_page_config(page_title=t("app_title"), layout="wide")

if st.session_state.lang == "العربية":
    st.markdown("""
        <style>
            body, .stApp { direction: rtl; text-align: right; }
            .st-emotion-cache-1kyxreq { justify-content: flex-end; }
        </style>
    """, unsafe_allow_html=True)

st.sidebar.selectbox(t("lang_selector"), options=["Français", "English", "العربية"], key="lang")
st.sidebar.divider()
st.sidebar.title(t("nav_title"))
app_mode = st.sidebar.radio(t("select_module"), [t("col_design"), t("foot_design")])
st.sidebar.divider()

if app_mode == t("col_design"):
    st.title(f"🏛️ {t('col_design')}")
    st.markdown(t("col_desc"))

    with st.sidebar:
        st.header(t("input_params"))
        element_id = st.text_input("Repère (ex: P(A:1))", value="P(A:1)")
        
        with st.expander(t("geom_type"), expanded=True):
            st_type = st.selectbox(t("col_shape"), ["rect", "circ"], format_func=lambda x: t(f"shape_{x}"))
            lf_val = st.number_input(t("buckling_len"), value=3.00, step=0.10)
        
        with st.expander(t("loads_dur"), expanded=True):
            nu_col = st.number_input("Nu (MN)", value=0.640, format="%.3f")
            charge_duration = st.selectbox(t("load_app"), ["autre_cas", "avant_90j", "avant_28j"], format_func=lambda x: t(f"charge_{x}"))
            charge_engine = charge_duration.replace("_", " ") 
            
        with st.expander(t("mat_const"), expanded=False):
            fc28_val = st.number_input(t("concrete_fc28"), value=25, step=5)
            fe_col = st.selectbox(t("steel_fe"), [400, 500], index=1)
            yb_val = st.number_input("Gamma_b", value=1.50)
            ys_col = st.number_input("Gamma_s", value=1.15)
            
        with st.expander(t("long_rebar"), expanded=False):
            phi_l_max = st.selectbox(t("phi_max"), [12, 14, 16, 20, 25], index=1)
            phi_l_min = st.selectbox(t("phi_min"), [12, 14, 16, 20, 25], index=0)

    col_engine = ColumnsSystem()
    try:
        geom = col_engine.pre_design(Nu=nu_col, Lf=lf_val, Yb=yb_val, fc28=fc28_val, st_type=st_type)
        steel = col_engine.design(Nu=nu_col, Lf=lf_val, geometry=geom, Yb=yb_val, Ys=ys_col, fe=fe_col, fc28=fc28_val, charge=charge_engine)
        a_m = min(geom['a'], geom['b']) if st_type == 'rect' else geom['D']
        trans_steel = col_engine.design_transverse(phi_l_max, phi_l_min, a_m)

        st.subheader(t("res_formwork"))
        c1, c2, c3 = st.columns(3)
        if st_type == "rect":
            c1.metric(t("width"), f"{geom['a']:.2f} m")
            c2.metric(t("length"), f"{geom['b']:.2f} m")
        else:
            c1.metric(t("diameter"), f"{geom['D']:.2f} m")
        c3.metric(t("theo_br"), f"{geom['Br_pre']:.4f} m²")
        st.divider()

        st.subheader(t("res_steel"))
        sc1, sc2, sc3 = st.columns(3)
        sc1.metric(t("theo_sec"), f"{steel['sections_cm2']['As_theoretical']} cm²")
        sc2.metric(t("min_sec"), f"{steel['sections_cm2']['As_min']} cm²")
        sc3.metric(t("final_sec"), f"{steel['sections_cm2']['As_final']} cm²", delta=t("exec_val"), delta_color="off")
        
        st.caption(t("rebar_options"))
        if steel['options']:
            df_col = pd.DataFrame(steel['options'])
            st.dataframe(translate_df_columns(df_col), use_container_width=True, hide_index=True)
        else:
            st.warning(t("no_rebar"))
        st.divider()
        
        st.subheader(t("res_transverse"))
        tc1, tc2, tc3 = st.columns(3)
        tc1.metric(t("phi_t_label"), f"{trans_steel['phi_t']} mm")
        tc2.metric(t("spacing"), f"{trans_steel['st']} cm")
        tc3.metric(t("spacing_crit"), f"{trans_steel['st_recouv']} cm")
        st.divider()
        
        with st.expander(t("res_factors")):
            st.json(steel['factors'])

        if st.button("💾 Enregistrer dans le projet / Save to Project", key="save_col"):
            dim_str = f"{geom['a']:.2f} x {geom['b']:.2f}" if st_type == "rect" else f"∅ {geom['D']:.2f}"
            log_entry = {
                "Repère": element_id,
                "Type": "Poteau",
                "Nu (MN)": nu_col,
                "Section Adop. (cm²)": steel['sections_cm2']['As_final'],
                "Cadres (Φt)": trans_steel['phi_t'],
                "Espacement (cm)": trans_steel['st'],
                "Dimensions (m)": dim_str,
                "Armatures A (cm²)": None,
                "Armatures B (cm²)": None
            }
            st.session_state.project_log.append(log_entry)
            st.success(f"Élément {element_id} ajouté au journal.")

    except ValueError as e:
        st.error(f"{t('design_err')} {e}")

elif app_mode == t("foot_design"):
    st.title(f"🏗️ {t('foot_design')}")
    st.markdown(t("foot_desc"))

    with st.sidebar:
        st.header(t("input_params"))
        element_id = st.text_input("Repère (ex: S(A:1))", value="S(A:1)")
        
        cat_semelle = st.radio(t("foot_cat"), ["iso", "cont"], format_func=lambda x: t(f"cat_{x}"))
        type_semelle = st.radio(t("foot_type"), ["centree", "excentree"], format_func=lambda x: t(f"type_{x}"))
        
        with st.expander(t("col_dims"), expanded=True):
            col_a = st.number_input(t("width_a"), value=0.20, step=0.05)
            # Hide length 'b' for continuous walls (implicitly infinite/1m)
            if cat_semelle == "iso":
                col_b = st.number_input(t("length_b"), value=0.40, step=0.05)
        
        with st.expander(t("loads_soil"), expanded=True):
            nu = st.number_input("Nu", value=0.462, format="%.3f")
            nser = st.number_input("Nser", value=0.334, format="%.3f")
            sigma_sol = st.number_input(t("soil_cap"), value=0.25, step=0.05)
        
        with st.expander(t("mat_const"), expanded=False):
            fe = st.selectbox(t("steel_fe"), [400, 500], index=1)
            ys = st.number_input("Gamma_s", value=1.15)
            fiss = st.selectbox(t("crack_risk"), ["peu", "prejudiciable", "tres_prejudiciable"], format_func=lambda x: t(f"fiss_{x}"))

    if cat_semelle == "iso":
        engine = IsolatedFootingSystem()
        if type_semelle == "centree":
            res = engine.design_centered(col_a, col_b, nu, nser, fe, ys, sigma_sol, fiss)
        else:
            res = engine.design_eccentric(col_a, col_b, nu, nser, fe, ys, sigma_sol, fiss)
    else:
        engine = ContinuedFootingSystem()
        if type_semelle == "centree":
            res = engine.design_centered(col_a, nu, nser, fe, ys, sigma_sol, fiss)
        else:
            res = engine.design_eccentric(col_a, nu, nser, fe, ys, sigma_sol, fiss)

    st.subheader(f"{t('res_footing')} {res['Type']}")
    c1, c2, c3 = st.columns(3)
    dim_a_label = t("width").replace("(a)", "(A = 1.0ml)") if cat_semelle == "cont" else t("width").replace("(a)", "(A)")
    c1.metric(dim_a_label, f"{res['Geometry']['A']:.2f} m")
    c2.metric(t("length").replace("(b)", "(B)"), f"{res['Geometry']['B']:.2f} m")
    c3.metric(t("height_h"), f"{res['Geometry']['h']:.2f} m")
    st.divider()

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader(f"{t('rebar_b')} ({res['Geometry']['B']:.2f}m)")
        st.caption(f"{t('req_area')} : {res['Ab_req']:.2f} cm²" + ("/ml" if cat_semelle=="cont" else ""))
        if res['options_B']:
            df_b = pd.DataFrame(res['options_B'])
            st.dataframe(translate_df_columns(df_b).drop(columns=[df_b.columns[-1]]), use_container_width=True, hide_index=True)
        else:
            st.error(t("no_rebar"))

    with col_right:
        st.subheader(f"{t('rebar_a')} ({res['Geometry']['A']:.2f}m)")
        st.caption(f"{t('req_area')} : {res['Aa_req']:.2f} cm²" + (" (Répartition)" if cat_semelle=="cont" else ""))
        if res['options_A']:
            df_a = pd.DataFrame(res['options_A'])
            st.dataframe(translate_df_columns(df_a).drop(columns=[df_a.columns[-1]]), use_container_width=True, hide_index=True)
        else:
            st.error(t("no_rebar"))

    st.info(t("strategy_note"))

    st.divider()
    if st.button("💾 Enregistrer dans le projet / Save to Project", key="save_foot"):
        log_entry = {
            "Repère": element_id,
            "Type": res['Type'],
            "Nu (MN)": nu,
            "Section Adop. (cm²)": None,
            "Cadres (Φt)": None,
            "Espacement (cm)": None,
            "Dimensions (m)": f"{res['Geometry']['A']:.2f} x {res['Geometry']['B']:.2f}",
            "Armatures A (cm²)": res['Aa_req'],
            "Armatures B (cm²)": res['Ab_req']
        }
        st.session_state.project_log.append(log_entry)
        st.success(f"Élément {element_id} ajouté au journal.")

# --- PROJECT LOG & EXPORT SYSTEM ---
st.divider()
st.header("📁 Journal du Projet / Project Log")

if st.session_state.project_log:
    log_df = pd.DataFrame(st.session_state.project_log)
    st.dataframe(log_df, use_container_width=True)
    csv = log_df.to_csv(index=False).encode('utf-8')
    st.download_button(label="📥 Exporter vers CSV / Export to CSV", data=csv, file_name='bael_project_log.csv', mime='text/csv')
    if st.button("🗑️ Vider le journal / Clear Log"):
        st.session_state.project_log = []
        st.rerun()
else:
    st.caption("Aucun élément enregistré. / No elements saved yet.")
