import streamlit as st
import math
import pandas as pd

# --- LOGIC ENGINES ---

class ColumnsSystem:
    def pre_design(self, Nu, Lf, Yb=1.5, landa=35, alpha=0.708, fc28=25, st_type="rect"):
        Br = ((0.9 * Yb) / alpha) * (Nu / fc28)

        if st_type == "rect":
            a = math.ceil(((math.sqrt(12) * Lf) / landa) * 20) / 20
            b_calc = math.ceil(((Br / (a - 0.02)) + 0.02) * 20) / 20
            b = a if b_calc < a else b_calc
            return {
                "type": "rect",
                "a": a, 
                "b": b, 
                "D": None,
                "Br_pre": round(Br, 4) 
            }
        
        elif st_type == "circ":
            D1 = (2 * math.sqrt(Br / math.pi)) + 0.02
            D2 = ((4 * Lf) / landa)
            D_calc = max(D1, D2) 
            D = math.ceil(D_calc * 20) / 20
            return {
                "type": "circ",
                "a": None, 
                "b": None, 
                "D": D,
                "Br_pre": round(Br, 4)
            }

    def design(self, Nu, Lf, geometry, Yb=1.5, Ys=1.15, fe=500, fc28=25, charge="autre cas"):
        st_type = geometry["type"]
        a = geometry["a"]
        b = geometry["b"]
        D = geometry["D"]

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
            raise ValueError("Lambda exceeds 70. Column is too slender.")

        divisor = {"avant 90j": 1.10, "avant 28j": 1.20, "autre cas": 1.0}.get(charge, 1.0)
        alpha /= divisor

        As_calc = ((Nu / alpha) - ((Br * fc28) / (0.9 * Yb))) * (Ys / fe) * 10000
        Amin = max(4 * perimeter_u, (0.2 / 100) * B_area * 10000)
        As_final = max(As_calc, Amin)

        return {
            "factors": {"Landa": round(landa, 3), "Alpha": round(alpha, 3), "Br_reel_m2": round(Br, 4)},
            "sections_cm2": {
                "As_theoretical": round(As_calc, 2), 
                "As_min": round(Amin, 2), 
                "As_final": round(As_final, 2)
            }
        }


class FootingSystem:
    def __init__(self):
        self.standard_diameters = [8, 10, 12, 14, 16, 20]

    def generate_options(self, required_area_cm2, dimension_m):
        max_spacing_m = 0.20
        baseline_count = math.ceil(dimension_m / max_spacing_m) + 1
        
        allowed_counts = list(set([
            max(2, baseline_count - 1), 
            baseline_count, 
            baseline_count + 1
        ]))

        viable_options = []

        for count in allowed_counts:
            for phi in self.standard_diameters:
                area_per_bar = (math.pi * (phi / 10)**2) / 4 
                actual_area = count * area_per_bar
                
                if actual_area >= required_area_cm2:
                    excess_cm2 = actual_area - required_area_cm2
                    actual_spacing = dimension_m / (count - 1)
                    
                    if actual_spacing <= max_spacing_m:
                        phi_m = phi / 1000
                        hook_e_m = max(0.15, 12 * phi_m + 0.06)
                        
                        viable_options.append({
                            "Selection": f"{count} HA {phi}",
                            "Area (cm²)": round(actual_area, 2),
                            "Spacing (cm)": round(actual_spacing * 100, 1),
                            "Hook (m)": round(hook_e_m, 2),
                            "Excess": round(excess_cm2, 2)
                        })
        
        viable_options.sort(key=lambda x: x["Excess"])
        return viable_options[:3]

    def design_centered(self, a, b, Nu, Nser, Fe, Ys, Gama_sol, fissuration="peu"):
        B = math.ceil(math.sqrt((b/a) * (Nser/Gama_sol)) * 20) / 20
        A = math.ceil(math.sqrt((a/b) * (Nser/Gama_sol)) * 20) / 20
        
        return self._compute_reinforcement(a, b, A, B, Nu, Fe, Ys, fissuration, footing_type="Centered")

    def design_eccentric(self, a, b, Nu, Nser, Fe, Ys, Gama_sol, fissuration="peu"):
        """
        Solves for A using the quadratic: 2A^2 + A(b - 2a) - Nser/Gama_sol = 0
        Assumes footing is flush with the column on side A (Semelle de rive).
        """
        c = - (Nser / Gama_sol)
        b_quad = b - (2 * a)
        
        delta = (b_quad**2) - (4 * 2 * c)
        A_calc = (-b_quad + math.sqrt(delta)) / (2 * 2)
        
        A = math.ceil(A_calc * 20) / 20
        B_calc = (2 * A) - (2 * a) + b
        B = math.ceil(B_calc * 20) / 20
        
        return self._compute_reinforcement(a, b, A, B, Nu, Fe, Ys, fissuration, footing_type="Eccentric")

    def _compute_reinforcement(self, a, b, A, B, Nu, Fe, Ys, fissuration, footing_type):
        """
        Shared logic engine for both centered and eccentric footings.
        Calculates depth (h) and steel sections dynamically based on physical overhangs.
        """
        # Calculate functional overhangs (débords)
        overhang_A = (A - a) if footing_type == "Eccentric" else (A - a) / 2
        overhang_B = (B - b) / 2

        # Depth constraint: h >= max_overhang / 2 + 0.05
        h_min = max(overhang_A, overhang_B) / 2 + 0.05
        h = math.ceil(h_min * 20) / 20
        h = max(h, 0.20) 
        d = h - 0.05

        Gama_su = Fe / Ys
        
        # Bielle Method: Section = (Nu * Overhang) / (4 * d * fsu)
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
st.set_page_config(page_title="Structural Design Pro", layout="wide")

# Sidebar Navigation
st.sidebar.title("Navigation")
app_mode = st.sidebar.radio("Select Module:", ["Column Designer", "Isolated Footing Designer"])
st.sidebar.divider()

if app_mode == "Column Designer":
    st.title("🏛️ Column Designer")
    st.markdown("Automated BAEL formwork sizing and longitudinal steel calculation.")

    with st.sidebar:
        st.header("1. Input Parameters")
        
        with st.expander("Geometry Type", expanded=True):
            shape = st.selectbox("Column Shape", ["Rectangular", "Circular"])
            st_type = "rect" if shape == "Rectangular" else "circ"
            lf_val = st.number_input("Buckling Length Lf (m)", value=3.00, step=0.10)
        
        with st.expander("Loads", expanded=True):
            nu_col = st.number_input("Nu (MN)", value=0.640, format="%.3f")
            charge_duration = st.selectbox("Load Application", ["autre cas", "avant 90j", "avant 28j"])
            
        with st.expander("Constrains", expanded=False):
            fc28_val = st.number_input("Concrete fc28 (MPa)", value=25, step=5)
            fe_col = st.selectbox("Steel Fe (MPa) ", [400, 500], index=1)
            yb_val = st.number_input("Gamma_b", value=1.50)
            ys_col = st.number_input("Gamma_s ", value=1.15)

    # Column Computation
    col_engine = ColumnsSystem()
    
    try:
        # Pre-design for formwork dimensions
        geom = col_engine.pre_design(Nu=nu_col, Lf=lf_val, Yb=yb_val, fc28=fc28_val, st_type=st_type)
        
        # Design for steel
        steel = col_engine.design(Nu=nu_col, Lf=lf_val, geometry=geom, Yb=yb_val, Ys=ys_col, fe=fe_col, fc28=fc28_val, charge=charge_duration)

        # Column Dashboard
        st.subheader("1. Formwork Dimensions")
        c1, c2, c3 = st.columns(3)
        if st_type == "rect":
            c1.metric("Width (a)", f"{geom['a']:.2f} m")
            c2.metric("Length (b)", f"{geom['b']:.2f} m")
        else:
            c1.metric("Diameter (D)", f"{geom['D']:.2f} m")
            
        c3.metric("Theoretical Br", f"{geom['Br_pre']:.4f} m²")

        st.divider()

        st.subheader("2. Steel Reinforcement")
        sc1, sc2, sc3 = st.columns(3)
        sc1.metric("Theoretical Area", f"{steel['sections_cm2']['As_theoretical']} cm²")
        sc2.metric("Minimum Area", f"{steel['sections_cm2']['As_min']} cm²")
        sc3.metric("Final Adopted Area", f"{steel['sections_cm2']['As_final']} cm²", delta="Execution Value", delta_color="off")

        st.divider()
        
        st.subheader("3. Verification Factors")
        st.json(steel['factors'])

    except ValueError as e:
        st.error(f"Design Error: {e}")

elif app_mode == "Isolated Footing Designer":
    st.title("🏗️ Isolated Footing Designer")
    st.markdown("Professional BAEL tool for rapid dimensioning and rebar optimization (Centered and Edge/Eccentric footings).")

    with st.sidebar:
        st.header("1. Input Parameters")
        
        footing_type = st.radio("Footing Type", ["Centered", "Eccentric (Edge)"])
        
        with st.expander("Column Dimensions (m)", expanded=True):
            col_a = st.number_input("Width (a) - parallel to A", value=0.30, step=0.05)
            col_b = st.number_input("Length (b) - parallel to B", value=0.40, step=0.05)
        
        with st.expander("Loads & Soil", expanded=True):
            nu = st.number_input("Nu (MN)", value=0.462, format="%.3f")
            nser = st.number_input("Nser (MN)", value=0.334, format="%.3f")
            sigma_sol = st.number_input("Soil Capacity (MPa)", value=0.25, step=0.05)
        
        with st.expander("Constrains", expanded=False):
            fe = st.selectbox("Steel Fe (MPa)", [400, 500], index=1)
            ys = st.number_input("Gamma_s", value=1.15)
            fiss = st.selectbox("Cracking Risk", ["peu", "prejudiciable", "tres_prejudiciable"])

    # Footing Computation
    engine = FootingSystem()
    
    if footing_type == "Centered":
        res = engine.design_centered(col_a, col_b, nu, nser, fe, ys, sigma_sol, fiss)
    else:
        res = engine.design_eccentric(col_a, col_b, nu, nser, fe, ys, sigma_sol, fiss)

    # Footing Dashboard
    st.subheader(f"Results: {res['Type']} Footing")
    c1, c2, c3 = st.columns(3)
    c1.metric("Width (A)", f"{res['Geometry']['A']:.2f} m")
    c2.metric("Length (B)", f"{res['Geometry']['B']:.2f} m")
    c3.metric("Height (h)", f"{res['Geometry']['h']:.2f} m")

    st.divider()

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader(f"Parallel to B ({res['Geometry']['B']:.2f}m)")
        st.caption(f"Required Area: {res['Ab_req']:.2f} cm²")
        if res['options_B']:
            df_b = pd.DataFrame(res['options_B'])
            st.dataframe(df_b.drop(columns=['Excess']), use_container_width=True, hide_index=True)
        else:
            st.error("No viable rebar found for B.")

    with col_right:
        st.subheader(f"Parallel to A ({res['Geometry']['A']:.2f}m)")
        st.caption(f"Required Area: {res['Aa_req']:.2f} cm²")
        if res['options_A']:
            df_a = pd.DataFrame(res['options_A'])
            st.dataframe(df_a.drop(columns=['Excess']), use_container_width=True, hide_index=True)
        else:
            st.error("No viable rebar found for A.")

    st.info("**Strategy:** Options are ranked by steel efficiency (least waste). The 'Hook' column indicates the standard anchorage length required.")
