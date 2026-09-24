import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch
import io

st.set_page_config(
    page_title="Piperack Foundation Design App",
    page_icon="🏗️",
    layout="centered",          # Better for iPad / mobile
    initial_sidebar_state="expanded"
)

# ==================== TITLE ====================
st.title("🏗️ Modularized Piperack Foundation Design App")
st.markdown("**Prototype – Isolated Footing + Pedestal (ACI 318 style)**")
st.markdown("Inspired by SARB Field Development Project calculation notes (AD204-601-G-03378)")
st.divider()

# ==================== SIDEBAR INPUTS ====================
st.sidebar.header("📐 Geometry Inputs")

col1, col2 = st.sidebar.columns(2)
with col1:
    Lx = st.number_input("Footing Length Lx (m)", value=3.50, min_value=0.5, step=0.1)
    Ly = st.number_input("Footing Width Ly (m)", value=3.50, min_value=0.5, step=0.1)
    Hf = st.number_input("Footing Thickness Hf (m)", value=0.40, min_value=0.2, step=0.05)
with col2:
    dx = st.number_input("Pedestal dx (m)", value=0.85, min_value=0.3, step=0.05)
    dy = st.number_input("Pedestal dy (m)", value=1.10, min_value=0.3, step=0.05)
    Hp = st.number_input("Pedestal Height Hp (m)", value=1.90, min_value=0.5, step=0.1)

Hs = st.sidebar.number_input("Soil height above footing Hs (m)", value=1.60, min_value=0.0, step=0.1)

st.sidebar.header("🧱 Materials & Soil")
fc = st.sidebar.number_input("Concrete f'c (MPa)", value=35.0, min_value=20.0, step=5.0)
fy = st.sidebar.number_input("Rebar fy (MPa)", value=420.0, min_value=300.0, step=20.0)
gamma_c = st.sidebar.number_input("Concrete unit weight (kN/m³)", value=24.0)
gamma_s = st.sidebar.number_input("Soil unit weight (kN/m³)", value=18.0)
q_all = st.sidebar.number_input("Allowable Bearing Capacity (kN/m²)", value=250.0)
mu = st.sidebar.number_input("Friction coefficient μ", value=0.30, min_value=0.1, max_value=0.6, step=0.05)
FS_req = st.sidebar.number_input("Required FS (Overturning & Sliding)", value=1.50, min_value=1.0, step=0.1)

st.sidebar.header("📥 Applied Loads (at top of pedestal)")
st.sidebar.markdown("**Service / Elastic case (for stability)**")
Fz_s = st.sidebar.number_input("Vertical Force Fz service (kN) ↓ positive", value=135.0)
Fx_s = st.sidebar.number_input("Horizontal Fx service (kN)", value=12.0)
Fy_s = st.sidebar.number_input("Horizontal Fy service (kN)", value=-9.0)
Mx_s = st.sidebar.number_input("Moment Mx service (kN·m)", value=-50.0)
My_s = st.sidebar.number_input("Moment My service (kN·m)", value=30.0)

st.sidebar.markdown("**Ultimate case (for RC design)**")
Fz_u = st.sidebar.number_input("Vertical Force Fz ultimate (kN) ↓ positive", value=200.0)
Fx_u = st.sidebar.number_input("Horizontal Fx ultimate (kN)", value=18.0)
Fy_u = st.sidebar.number_input("Horizontal Fy ultimate (kN)", value=-14.0)
Mx_u = st.sidebar.number_input("Moment Mx ultimate (kN·m)", value=-80.0)
My_u = st.sidebar.number_input("Moment My ultimate (kN·m)", value=50.0)

# ==================== CALCULATIONS ====================
def calculate_foundation():
    # Areas and weights
    A_footing = Lx * Ly
    A_ped = dx * dy
    A_soil = A_footing - A_ped

    W_footing = A_footing * Hf * gamma_c
    W_ped = A_ped * Hp * gamma_c
    W_soil = A_soil * Hs * gamma_s
    W_total_dead = W_footing + W_ped + W_soil

    # Service total vertical
    Fz_total_s = Fz_s + W_total_dead

    # Moments at bottom of footing (service)
    # Moment due to horizontal forces: H * (Hp + Hf)
    Mxs_bottom = Mx_s + Fy_s * (Hp + Hf)
    Mys_bottom = My_s + Fx_s * (Hp + Hf)

    # Eccentricity
    ex = Mys_bottom / Fz_total_s if Fz_total_s != 0 else 0
    ey = Mxs_bottom / Fz_total_s if Fz_total_s != 0 else 0

    # Bearing pressures (service)
    # σ = Fz/A ± Mx*y/I ± My*x/I
    # Simplified: σ_max/min = Fz/A * (1 ± 6*ex/Lx ± 6*ey/Ly)
    term_x = 6 * abs(ex) / Lx
    term_y = 6 * abs(ey) / Ly
    sigma_avg = Fz_total_s / A_footing
    sigma_max = sigma_avg * (1 + term_x + term_y)
    sigma_min = sigma_avg * (1 - term_x - term_y)

    # Overturning FS
    # Resisting moment about edges
    # About X-edge (for My)
    MR_x = Fz_total_s * (Lx / 2)
    MO_x = abs(Mys_bottom)
    FS_ot_x = MR_x / MO_x if MO_x > 0 else 999

    # About Y-edge (for Mx)
    MR_y = Fz_total_s * (Ly / 2)
    MO_y = abs(Mxs_bottom)
    FS_ot_y = MR_y / MO_y if MO_y > 0 else 999

    FS_ot = min(FS_ot_x, FS_ot_y)

    # Sliding FS
    H_total = np.sqrt(Fx_s**2 + Fy_s**2)
    R_friction = mu * Fz_total_s
    FS_slide = R_friction / H_total if H_total > 0 else 999

    # Ultimate vertical
    Fz_total_u = Fz_u + W_total_dead  # note: usually self-weight factored differently, simplified here

    # Ultimate moments at bottom
    Mxu_bottom = Mx_u + Fy_u * (Hp + Hf)
    Myu_bottom = My_u + Fx_u * (Hp + Hf)

    # Design moments for footing (simplified: at face of pedestal)
    # Critical section for flexure ≈ at face of pedestal
    # Lever arm from edge of pedestal to edge of footing
    proj_x = (Lx - dx) / 2
    proj_y = (Ly - dy) / 2

    # Approximate design moment (conservative using total moment + redistribution)
    # Better approximation: moment = pressure * projection * (projection/2) * width
    # Using average pressure for simplicity in prototype
    q_u = Fz_total_u / A_footing
    Mu_x = q_u * Ly * proj_x * (proj_x / 2)   # moment about Y (for bars // X)
    Mu_y = q_u * Lx * proj_y * (proj_y / 2)   # moment about X (for bars // Y)

    # Required reinforcement (simplified ACI)
    # As = Mu / (φ * fy * 0.9 * d)   φ=0.9, jd≈0.9d
    d_eff = Hf - 0.075  # assume 75 mm cover + half bar
    phi = 0.90
    As_x = (Mu_x * 1e6) / (phi * fy * 0.9 * d_eff * 1000) if d_eff > 0 else 0  # mm²
    As_y = (Mu_y * 1e6) / (phi * fy * 0.9 * d_eff * 1000) if d_eff > 0 else 0

    # Minimum steel
    As_min = 0.0018 * 1000 * Hf * 1000  # mm² per m width (simplified)

    return {
        "A_footing": A_footing,
        "W_footing": W_footing,
        "W_ped": W_ped,
        "W_soil": W_soil,
        "W_total_dead": W_total_dead,
        "Fz_total_s": Fz_total_s,
        "ex": ex,
        "ey": ey,
        "sigma_avg": sigma_avg,
        "sigma_max": sigma_max,
        "sigma_min": sigma_min,
        "FS_ot": FS_ot,
        "FS_slide": FS_slide,
        "H_total": H_total,
        "Fz_total_u": Fz_total_u,
        "Mu_x": Mu_x,
        "Mu_y": Mu_y,
        "As_x": As_x,
        "As_y": As_y,
        "As_min": As_min,
        "d_eff": d_eff,
        "proj_x": proj_x,
        "proj_y": proj_y,
    }

results = calculate_foundation()

# ==================== MAIN DISPLAY ====================
tab1, tab2, tab3, tab4 = st.tabs(["📊 Summary Results", "⚖️ Stability Checks", "🧱 RC Design", "📐 Sketch"])

with tab1:
    st.subheader("Self-Weight Summary")
    col_a, col_b, col_c, col_d = st.columns(4)
    col_a.metric("Footing Weight", f"{results['W_footing']:.1f} kN")
    col_b.metric("Pedestal Weight", f"{results['W_ped']:.1f} kN")
    col_c.metric("Soil Weight", f"{results['W_soil']:.1f} kN")
    col_d.metric("Total Dead Load", f"{results['W_total_dead']:.1f} kN")

    st.subheader("Geometry Summary")
    geo_df = pd.DataFrame({
        "Parameter": ["Footing Lx × Ly", "Footing Thickness Hf", "Pedestal dx × dy", "Pedestal Height Hp", "Soil Cover Hs", "Footing Area"],
        "Value": [f"{Lx:.2f} × {Ly:.2f} m", f"{Hf:.2f} m", f"{dx:.2f} × {dy:.2f} m", f"{Hp:.2f} m", f"{Hs:.2f} m", f"{results['A_footing']:.2f} m²"]
    })
    st.dataframe(geo_df, use_container_width=True, hide_index=True)

with tab2:
    st.subheader("Service / Elastic Condition – Stability")

    st.markdown(f"**Total Vertical Load (service)** = {results['Fz_total_s']:.1f} kN")
    st.markdown(f"**Eccentricity**  ex = {results['ex']:.3f} m   |   ey = {results['ey']:.3f} m")

    # Bearing
    st.markdown("### Soil Bearing Pressure")
    bcol1, bcol2, bcol3 = st.columns(3)
    bcol1.metric("σ average", f"{results['sigma_avg']:.1f} kN/m²")
    bcol2.metric("σ max", f"{results['sigma_max']:.1f} kN/m²", 
                 delta="OK" if results['sigma_max'] <= q_all else "EXCEED",
                 delta_color="normal" if results['sigma_max'] <= q_all else "inverse")
    bcol3.metric("σ min", f"{results['sigma_min']:.1f} kN/m²",
                 delta="OK" if results['sigma_min'] >= 0 else "UPLIFT",
                 delta_color="normal" if results['sigma_min'] >= 0 else "inverse")

    st.progress(min(results['sigma_max'] / q_all, 1.0), text=f"Utilization: {results['sigma_max']/q_all*100:.0f}% of allowable")

    # FS
    st.markdown("### Factors of Safety")
    fcol1, fcol2 = st.columns(2)
    fcol1.metric("Overturning FS", f"{results['FS_ot']:.2f}",
                 delta="OK" if results['FS_ot'] >= FS_req else "NG",
                 delta_color="normal" if results['FS_ot'] >= FS_req else "inverse")
    fcol2.metric("Sliding FS", f"{results['FS_slide']:.2f}",
                 delta="OK" if results['FS_slide'] >= FS_req else "NG",
                 delta_color="normal" if results['FS_slide'] >= FS_req else "inverse")

    if results['FS_ot'] >= FS_req and results['FS_slide'] >= FS_req and results['sigma_max'] <= q_all and results['sigma_min'] >= 0:
        st.success("✅ All stability checks PASSED")
    else:
        st.error("❌ Some stability checks FAILED – review geometry or loads")

with tab3:
    st.subheader("Ultimate Condition – Reinforced Concrete Design (Simplified ACI 318)")

    st.markdown(f"**Total Vertical Load (ultimate)** ≈ {results['Fz_total_u']:.1f} kN")
    st.markdown(f"**Effective depth d** ≈ {results['d_eff']*1000:.0f} mm (assuming 75 mm cover)")

    st.markdown("### Design Moments at critical section (face of pedestal)")
    mcol1, mcol2 = st.columns(2)
    mcol1.metric("Mu (about Y – bars // X)", f"{results['Mu_x']:.1f} kN·m")
    mcol2.metric("Mu (about X – bars // Y)", f"{results['Mu_y']:.1f} kN·m")

    st.markdown("### Required Flexural Reinforcement")
    rcol1, rcol2, rcol3 = st.columns(3)
    rcol1.metric("As required (X-dir)", f"{results['As_x']:.0f} mm²")
    rcol2.metric("As required (Y-dir)", f"{results['As_y']:.0f} mm²")
    rcol3.metric("As minimum (0.0018bh)", f"{results['As_min']:.0f} mm² / m")

    st.info("Note: This is a simplified prototype calculation. For production use, include full load combinations, exact critical sections, shear/punching checks, development length, and crack-width verification per ACI 318.")

with tab4:
    st.subheader("Foundation Sketch (Plan + Section)")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Plan view
    ax1.set_aspect('equal')
    ax1.add_patch(Rectangle((-Lx/2, -Ly/2), Lx, Ly, fill=True, facecolor='lightgray', edgecolor='black', linewidth=2, label='Footing'))
    ax1.add_patch(Rectangle((-dx/2, -dy/2), dx, dy, fill=True, facecolor='dimgray', edgecolor='black', linewidth=2, label='Pedestal'))
    ax1.plot(0, 0, 'r+', markersize=12, label='Center')
    ax1.set_xlim(-Lx/2 - 0.5, Lx/2 + 0.5)
    ax1.set_ylim(-Ly/2 - 0.5, Ly/2 + 0.5)
    ax1.set_xlabel("X (m)")
    ax1.set_ylabel("Y (m)")
    ax1.set_title("PLAN VIEW")
    ax1.legend(loc='upper right')
    ax1.grid(True, linestyle='--', alpha=0.5)
    ax1.axhline(0, color='blue', linewidth=0.8, linestyle=':')
    ax1.axvline(0, color='blue', linewidth=0.8, linestyle=':')

    # Section view
    ax2.add_patch(Rectangle((-Lx/2, -Hf), Lx, Hf, fill=True, facecolor='lightgray', edgecolor='black', linewidth=2))
    ax2.add_patch(Rectangle((-dx/2, 0), dx, Hp, fill=True, facecolor='dimgray', edgecolor='black', linewidth=2))
    # Soil line
    ax2.axhline(Hs, color='brown', linewidth=1.5, linestyle='--', label='Ground Level')
    ax2.set_xlim(-Lx/2 - 0.5, Lx/2 + 0.5)
    ax2.set_ylim(-Hf - 0.3, Hp + 0.5)
    ax2.set_xlabel("X (m)")
    ax2.set_ylabel("Z (m)")
    ax2.set_title("SECTION VIEW")
    ax2.legend(loc='upper right')
    ax2.grid(True, linestyle='--', alpha=0.5)

    st.pyplot(fig)

    # Simple text dimensions
    st.markdown(f"""
    **Dimensions used:**
    - Footing: **{Lx:.2f} m × {Ly:.2f} m × {Hf:.2f} m** thick
    - Pedestal: **{dx:.2f} m × {dy:.2f} m × {Hp:.2f} m** high
    - Soil cover: **{Hs:.2f} m**
    """)

# ==================== FOOTER ====================
st.divider()
st.caption("Prototype app for educational / demonstration purposes. Always verify results with a licensed structural engineer and full code compliance checks. Based on typical oil & gas modular piperack foundation calculation methodology.")
