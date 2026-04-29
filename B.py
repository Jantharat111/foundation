import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# --- CONFIGURATION ---
st.set_page_config(page_title="Pile Group Pro", layout="wide", page_icon="🏗️")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stNumberInput, .stDataEditor { border-radius: 10px !important; }
    .metric-card {
        background-color: white; padding: 20px; border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-left: 5px solid #007bff;
    }
    h1, h2, h3 { color: #1e3d59; font-family: 'Helvetica Neue', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.title("🏗️ Advanced Pile Group Analysis")
st.markdown("ระบบคำนวณแรงเสาเข็มเยื้องศูนย์แม่นยำสูง ด้วยวิธี **m, n coefficients**")
st.divider()

# --- SIDEBAR INPUTS ---
with st.sidebar:
    st.header("📋 ข้อมูลนำเข้า (Inputs)")
    with st.expander("แรงและระยะเยื้องศูนย์", expanded=True):
        Q = st.number_input("แรงทั้งหมด (Q) [kN]", value=1500.0, step=100.0)
        ex = st.number_input("ระยะเยื้องศูนย์ ex [m]", value=0.45, step=0.05)
        ey = st.number_input("ระยะเยื้องศูนย์ ey [m]", value=0.20, step=0.05)
    
    st.header("📍 พิกัดเสาเข็ม (Coordinates)")
    st.caption("ระบุพิกัด x, y ของเสาเข็มแต่ละต้นจากจุด Centroid")
    
    # พิกัดเริ่มต้น (4 ต้น)
    initial_data = pd.DataFrame({
        'x': [-0.8, 0.8, -0.8, 0.8],
        'y': [0.8, 0.8, -0.8, -0.8]
    })
    coords = st.data_editor(initial_data, num_rows="dynamic", use_container_width=True)

# --- CALCULATION LOGIC ---
if not coords.empty:
    x = coords['x'].values
    y = coords['y'].values
    N = len(x)
    
    # คำนวณหา m และ n ตามโจทย์
    sum_x2 = np.sum(x**2)
    sum_y2 = np.sum(y**2)
    
    # m = Q*ex / Sum(x^2), n = Q*ey / Sum(y^2)
    m = (Q * ex) / sum_x2 if sum_x2 != 0 else 0
    n = (Q * ey) / sum_y2 if sum_y2 != 0 else 0
    
    # คำนวณ Pi = Q/N + m*x + n*y
    pi_values = (Q / N) + (m * x) + (n * y)
    
    # เตรียม DataFrame ผลลัพธ์
    results_df = coords.copy()
    results_df['Pile No.'] = [f"P{i+1}" for i in range(N)]
    results_df['Load (Pi)'] = np.round(pi_values, 2)
    
    # --- DASHBOARD LAYOUT ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="metric-card"><h3>Q Total</h3><h2>{Q:,.0f} <small>kN</small></h2></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><h3>Coefficient m</h3><h2>{m:.2f}</h2></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><h3>Coefficient n</h3><h2>{n:.2f}</h2></div>', unsafe_allow_html=True)

    st.write("")
    
    tab1, tab2 = st.tabs(["📊 ผลการคำนวณและกราฟ", "📝 รายละเอียดการคำนวณ"])
    
    with tab1:
        c1, c2 = st.columns([0.4, 0.6])
        with c1:
            st.subheader("ตารางแรงในเสาเข็ม")
            st.dataframe(results_df[['Pile No.', 'x', 'y', 'Load (Pi)']], 
                         hide_index=True, use_container_width=True)
            
            max_load = results_df['Load (Pi)'].max()
            min_load = results_df['Load (Pi)'].min()
            st.success(f"แรงสูงสุด: **{max_load} kN**")
            st.warning(f"แรงต่ำสุด: **{min_load} kN**")

        with c2:
            st.subheader("ผังการกระจายแรง (Spatial Distribution)")
            fig = px.scatter(results_df, x='x', y='y', 
                             size='Load (Pi)', color='Load (Pi)',
                             hover_name='Pile No.', text='Pile No.',
                             color_continuous_scale='Reds',
                             size_max=40)
            fig.update_traces(textposition='top center')
            fig.update_layout(plot_bgcolor="white", height=450)
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("Mathematical Summary")
        st.latex(r"P_i = \frac{Q}{N} + \left( \frac{Q \cdot e_x}{\sum x^2} \right) x_i + \left( \frac{Q \cdot e_y}{\sum y^2} \right) y_i")
        st.markdown(f"""
        - **Number of Piles (N):** {N}
        - **Sum of x²:** {sum_x2:.4f}
        - **Sum of y²:** {sum_y2:.4f}
        - **Calculation Path:**  
          $P_i = ({Q}/{N}) + ({m:.2f} \cdot x) + ({n:.2f} \cdot y)$
        """)

else:
    st.error("กรุณาเพิ่มข้อมูลพิกัดเสาเข็มอย่างน้อย 1 ต้น")
