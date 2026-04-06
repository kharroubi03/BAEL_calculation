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
        "foot_design": "Dimensionnement Semelle Isolée",
        "lang_selector": "🌍 Langue",
        # Column UI
        "col_desc": "Outil de dimensionnement BAEL automatisé pour coffrage et ferraillage longitudinal.",
        "input_params": "1. Paramètres d'Entrée",
        "geom_type": "Type de Géométrie",
        "col_shape": "Forme du Poteau",
        "shape_rect": "Rectangulaire",
        "shape_circ": "Circulaire",
        "buckling_len": "Longueur de flambement Lf (m)",
        "loads_dur": "Charges et Durée",
        "load_app": "Application de la charge",
        "charge_autre_cas": "Autre cas (> 90 jours)",
        "charge_avant_90j": "Avant 90 jours",
        "charge_avant_28j": "Avant 28 jours",
        "mat_const": "Contraintes Matériaux",
        "concrete_fc28": "Béton fc28 (MPa)",
        "steel_fe": "Acier Fe (MPa)",
        # Column Results
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
        "res_factors": "3. Facteurs de Vérification",
        "design_err": "Erreur de conception :",
        "rebar_options": "Options de Ferraillage (Longitudinal)",
        # Footing UI
        "foot_desc": "Outil professionnel BAEL pour le dimensionnement rapide et l'optimisation des armatures.",
        "foot_type": "Type de Semelle",
        "type_centree": "Centrée",
        "type_excentree": "Excentrée (Rive)",
        "col_dims": "Dimensions du Poteau (m)",
        "width_a": "Largeur (a) - parallèle à A",
        "length_b": "Longueur (b) - parallèle à B",
        "loads_soil": "Charges et Sol",
        "soil_cap": "Contrainte du Sol (MPa)",
        "crack_risk": "Fissuration",
        "fiss_peu": "Peu préjudiciable",
        "fiss_prejudiciable": "Préjudiciable",
        "fiss_tres_prejudiciable": "Très préjudiciable",
        # Footing Results
        "res_footing": "Résultats : Semelle",
        "height_h": "Hauteur (h)",
        "rebar_b": "Ferraillage parallèle à B",
        "rebar_a": "Ferraillage parallèle à A",
        "req_area": "Section requise",
        "no_rebar": "Aucune armature viable trouvée.",
        "strategy_note": "**Stratégie :** Les options sont classées par efficacité de l'acier (moins de pertes matérielles). La colonne 'Crochet (m)' indique la longueur d'ancrage standard requise."
    },
    "English": {
        "app_title": "Structural Design Pro",
        "nav_title": "Navigation",
        "select_module": "Select Module:",
        "col_design": "Column Designer",
        "foot_design": "Isolated Footing Designer",
        "lang_selector": "🌍 Language",
        # Column UI
        "col_desc": "Automated BAEL formwork sizing and longitudinal steel calculation.",
        "input_params": "1. Input Parameters",
        "geom_type": "Geometry Type",
        "col_shape": "Column Shape",
        "shape_rect": "Rectangular",
        "shape_circ": "Circular",
        "buckling_len": "Buckling Length Lf (m)",
        "loads_dur": "Loads & Duration",
        "load_app": "Load Application",
        "charge_autre_cas": "Other (> 90 days)",
        "charge_avant_90j": "Before 90 days",
        "charge_avant_28j": "Before 28 days",
        "mat_const": "Material Constraints",
        "concrete_fc28": "Concrete fc28 (MPa)",
        "steel_fe": "Steel Fe (MPa)",
        # Column Results
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
        "res_factors": "3. Verification Factors",
        "design_err": "Design Error:",
        "rebar_options": "Reinforcement Options (Longitudinal)",
        # Footing UI
        "foot_desc": "Professional BAEL tool for rapid dimensioning and rebar optimization.",
        "foot_type": "Footing Type",
        "type_centree": "Centered",
        "type_excentree": "Eccentric (Edge)",
        "col_dims": "Column Dimensions (m)",
        "width_a": "Width (a) - parallel to A",
        "length_b": "Length (b) - parallel to B",
        "loads_soil": "Loads & Soil",
        "soil_cap": "Soil Capacity (MPa)",
        "crack_risk": "Cracking Risk",
        "fiss_peu": "Not Harmful (Peu)",
        "fiss_prejudiciable": "Harmful",
        "fiss_tres_prejudiciable": "Highly Harmful",
        # Footing Results
        "res_footing": "Results: Footing",
        "height_h": "Height (h)",
        "rebar_b": "Reinforcement parallel to B",
        "rebar_a": "Reinforcement parallel to A",
        "req_area": "Required Area",
        "no_rebar": "No viable rebar found.",
        "strategy_note": "**Strategy:** Options are ranked by steel efficiency (least waste). The 'Hook (m)' column indicates the standard anchorage length required."
    },
    "العربية": {
        "app_title": "التصميم الإنشائي الاحترافي",
        "nav_title": "التنقل",
        "select_module": "اختر الوحدة:",
        "col_design": "تصميم الأعمدة",
        "foot_design": "تصميم القواعد المنفصلة",
        "lang_selector": "🌍 اللغة",
        # Column UI
        "col_desc": "أداة آلية لحساب أبعاد القوالب وحديد التسليح الطولي وفقاً لكود BAEL.",
        "input_params": "1. معلمات الإدخال",
        "geom_type": "نوع الهندسة",
        "col_shape": "شكل العمود",
        "shape_rect": "مستطيل",
        "shape_circ": "دائري",
        "buckling_len": "طول الانبعاج Lf (م)",
        "loads_dur": "الأحمال والمدة",
        "load_app": "تطبيق الحمل",
        "charge_autre_cas": "حالات أخرى (> 90 يوم)",
        "charge_avant_90j": "قبل 90 يوم",
        "charge_avant_28j": "قبل 28 يوم",
        "mat_const": "قيود المواد",
        "concrete_fc28": "مقاومة الخرسانة fc28 (MPa)",
        "steel_fe": "إجهاد الخضوع للصلب Fe (MPa)",
        # Column Results
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
        "res_factors": "3. عوامل التحقق",
        "design_err": "خطأ في التصميم:",
        "rebar_options": "خيارات التسليح (الطولي)",
        # Footing UI
        "foot_desc": "أداة احترافية لحساب الأبعاد السريع وتحسين التسليح وفقاً لكود BAEL.",
        "foot_type": "نوع القاعدة",
        "type_centree": "مركزية",
        "type_excentree": "لامركزية (طرفية)",
        "col_dims": "أبعاد العمود (م)",
        "width_a": "العرض (a) - موازي لـ A",
        "length_b": "الطول (b) - موازي لـ B",
        "loads_soil": "الأحمال والتربة",
        "soil_cap": "قدرة تحمل التربة (MPa)",
        "crack_risk": "خطر التشققات",
        "fiss_peu": "غير ضار (Peu)",
        "fiss_prejudiciable": "ضار",
        "fiss_tres_prejudiciable": "ضار جداً",
        # Footing Results
        "res_footing": "النتائج: قاعدة",
        "height_h": "الارتفاع (h)",
        "rebar_b": "التسليح الموازي لـ B",
        "rebar_a": "التسليح الموازي لـ A",
        "req_area": "المساحة المطلوبة",
        "no_rebar": "لم يتم العثور على تسليح مناسب.",
        "strategy_note": "**الاستراتيجية:** يتم ترتيب الخيارات حسب كفاءة الصلب (أقل هدر). يشير عمود 'الخطاف (م)' إلى طول التثبيت القياسي المطلوب."
    }
}

# --- STATE INITIALIZATION & HELPER ---
if 'lang' not in st.session_state:
    st.session_state.lang = "Français"

def t(key):
    return LANGUAGES[st.session_state.lang].get(key, f"Missing translation: {key}")

def translate_df_columns(df):
    """Utility to translate DataFrame headers dynamically"""
    if st.session_state.lang == "العربية":
        return df.rename(columns={"Selection": "الاختيار", "Area (cm²)": "المساحة (سم²)", "Spacing (cm)": "التباعد (سم)", "Excess": "الفائض", "Hook (m)": "الخطاف (م)"})
    elif st.session_state.lang == "Français":
        return df.rename(columns={"Selection": "Sélection", "Area (cm²)": "Section (cm²)", "Spacing (cm)": "Espacement (cm)", "Excess": "Excès", "Hook (m)": "Crochet (m)"})
    return df

# --- LOGIC ENGINES ---
class ColumnsSystem:
    def __init__(self):
        self.standard_diameters = [12, 14, 16, 20]
        self.min_spacing = 0.05 # 5 cm minimum spacing
        self.max_spacing = 0.40 # 40 cm maximum spacing
        
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
            # BAEL requires at least 6 bars for a circular column
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
            "factors": {"Landa": round(landa, 3), "Alpha": round(alpha, 3), "Br_m²": round(Br, 4)},
            "sections_cm2": {"As_theoretical": round(As_calc, 2), "As_min": round(Amin, 2), "As_final": round(As_final, 2)},
            "options": options
        }
    
class FootingSystem:
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
            "Type": footing_type,
            "Geometry": {"A": A, "B": B, "h": h, "d": d},
            "Ab_req": round(Ab_req, 2),
            "Aa_req": round(Aa_req, 2),
            "options_B": self.generate_options(Ab_req, B),
            "options_A": self.generate_options(Aa_req, A)
        }

# --- STREAMLIT UI ---
st.set_page_config(page_title=t("app_title"), layout="wide")

# RTL CSS Injection for Arabic
if st.session_state.lang == "العربية":
    st.markdown("""
        <style>
            body, .stApp { direction: rtl; text-align: right; }
            .st-emotion-cache-1kyxreq { justify-content: flex-end; }
        </style>
    """, unsafe_allow_html=True)

# Sidebar Navigation
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

    # Calculation
    col_engine = ColumnsSystem()
    try:
        geom = col_engine.pre_design(Nu=nu_col, Lf=lf_val, Yb=yb_val, fc28=fc28_val, st_type=st_type)
        steel = col_engine.design(Nu=nu_col, Lf=lf_val, geometry=geom, Yb=yb_val, Ys=ys_col, fe=fe_col, fc28=fc28_val, charge=charge_engine)

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
        
        # --- NEW UI FOR COLUMN REBAR OPTIONS ---
        st.caption(t("rebar_options"))
        if steel['options']:
            df_col = pd.DataFrame(steel['options'])
            df_col = translate_df_columns(df_col)
            st.dataframe(df_col, use_container_width=True, hide_index=True)
        else:
            st.warning(t("no_rebar"))

        st.divider()
        
        st.subheader(t("res_factors"))
        st.json(steel['factors'])

    except ValueError as e:
        st.error(f"{t('design_err')} {e}")

elif app_mode == t("foot_design"):
    st.title(f"🏗️ {t('foot_design')}")
    st.markdown(t("foot_desc"))

    with st.sidebar:
        st.header(t("input_params"))
        
        type_semelle = st.radio(t("foot_type"), ["centree", "excentree"], format_func=lambda x: t(f"type_{x}"))
        
        with st.expander(t("col_dims"), expanded=True):
            col_a = st.number_input(t("width_a"), value=0.30, step=0.05)
            col_b = st.number_input(t("length_b"), value=0.40, step=0.05)
        
        with st.expander(t("loads_soil"), expanded=True):
            nu = st.number_input("Nu (MN)", value=0.462, format="%.3f")
            nser = st.number_input("Nser (MN)", value=0.334, format="%.3f")
            sigma_sol = st.number_input(t("soil_cap"), value=0.25, step=0.05)
        
        with st.expander(t("mat_const"), expanded=False):
            fe = st.selectbox(t("steel_fe"), [400, 500], index=1)
            ys = st.number_input("Gamma_s", value=1.15)
            fiss = st.selectbox(t("crack_risk"), ["peu", "prejudiciable", "tres_prejudiciable"], format_func=lambda x: t(f"fiss_{x}"))

    # Calculation
    engine = FootingSystem()
    if type_semelle == "centree":
        res = engine.design_centered(col_a, col_b, nu, nser, fe, ys, sigma_sol, fiss)
    else:
        res = engine.design_eccentric(col_a, col_b, nu, nser, fe, ys, sigma_sol, fiss)

    st.subheader(f"{t('res_footing')} {t(f'type_{res['Type']}')}")
    c1, c2, c3 = st.columns(3)
    c1.metric(t("width").replace("(a)", "(A)"), f"{res['Geometry']['A']:.2f} m")
    c2.metric(t("length").replace("(b)", "(B)"), f"{res['Geometry']['B']:.2f} m")
    c3.metric(t("height_h"), f"{res['Geometry']['h']:.2f} m")
    st.divider()

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader(f"{t('rebar_b')} ({res['Geometry']['B']:.2f}m)")
        st.caption(f"{t('req_area')} : {res['Ab_req']:.2f} cm²")
        if res['options_B']:
            df_b = pd.DataFrame(res['options_B'])
            df_b = translate_df_columns(df_b)
            st.dataframe(df_b.drop(columns=[df_b.columns[-1]]), use_container_width=True, hide_index=True) # Drops Excess dynamically
        else:
            st.error(t("no_rebar"))

    with col_right:
        st.subheader(f"{t('rebar_a')} ({res['Geometry']['A']:.2f}m)")
        st.caption(f"{t('req_area')} : {res['Aa_req']:.2f} cm²")
        if res['options_A']:
            df_a = pd.DataFrame(res['options_A'])
            df_a = translate_df_columns(df_a)
            st.dataframe(df_a.drop(columns=[df_a.columns[-1]]), use_container_width=True, hide_index=True) # Drops Excess dynamically
        else:
            st.error(t("no_rebar"))

    st.info(t("strategy_note"))
