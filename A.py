import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- CONFIG ---
st.set_page_config(page_title="Bakhoum Pile Analysis", layout="wide")

# --- UI STYLING ---
st.markdown("""
    <style>
    .reportview-container { background: #f5f7f9; }
    .stMetric { background-color: #ffffff; border: 1px solid #e0e0e0; padding: 15px; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏗️ โปรแกรมวิเคราะห์แรงเสาเข็ม (Bakhoum Method)")
st.caption("อ้างอิงขั้นตอนจากสไลด์ รศ.ดร.อิทธิพล มีผล - มจพ.")

# --- 1. INPUT SECTION ---
col_in, col_graph = st.columns([1, 1.2], gap="large")

with col_in:
    st.subheader("📋 1. ป้อนข้อมูลนำเข้า")
    Q = st.number_input("น้ำหนักบรรทุกทั้งหมด (Q) [tons]", value=50.0, step=1.0)
    
    st.write("📍 **ตารางตำแหน่งและระยะเยื้องเสาเข็ม**")
    st.caption("Design X, Y (cm) และระยะเยื้องที่ตรวจพบ Error X, Y (cm)")
    
    # ตัวอย่างข้อมูลเริ่มต้น (ตาม Slide 12)
    initial_data = pd.DataFrame({
        'No.': ['P1', 'P2', 'P3', 'P4'],
        'Design_X': [-37.5, 37.5, -37.5, 37.5],
        'Design_Y': [37.5, 37.5, -37.5, -37.5],
        'error_x': [0.0, 7.0, 0.0, 0.0],  # ex ในสไลด์
        'error_y': [5.0, -10.0, 0.0, 0.0]  # ey ในสไลด์
    })
    df = st.data_editor(initial_data, num_rows="dynamic", use_container_width=True)

# --- 2. CALCULATION (STEP-BY-STEP AS PER SLIDES) ---
if not df.empty:
    n = len(df)
    
    # Step 1: คำนวณพิกัดจริง (Actual Coordinates)
    df['Actual_X'] = df['Design_X'] + df['error_x']
    df['Actual_Y'] = df['Design_Y'] + df['error_y']
    
    # Step 2: หา Centroid ใหม่ (X_bar, Y_bar) - Slide 10
    X_bar = df['Actual_X'].mean()
    Y_bar = df['Actual_Y'].mean()
    
    # Step 3: คำนวณพิกัดสัมพัทธ์ (x, y) เทียบ Centroid - Slide 12
    df['x'] = df['Actual_X'] - X_bar
    df['y'] = df['Actual_Y'] - Y_bar
    
    # Step 4: คำนวณผลรวมกำลังสอง (Summation) - Slide 13
    df['x2'] = df['x']**2
    df['y2'] = df['y']**2
    df['xy'] = df['x'] * df['y']
    
    sum_x2 = df['x2'].sum()
    sum_y2 = df['y2'].sum()
    sum_xy = df['xy'].sum()
    
    # Step 5: คำนวณโมเมนต์ดัด (Mx, My) - Slide 11
    Mx = Q * Y_bar
    My = Q * X_bar
    
    # Step 6: คำนวณค่า m, n Coefficients - Slide 23
    # สูตร Bakhoum สำหรับกรณีทั่วไป (Unsymmetrical)
    denom = (sum_x2 * sum_y2) - (sum_xy**2)
    
    if abs(denom) < 1e-9:
        m, n_coeff = 0, 0
    else:
        m = (My * sum_y2 - Mx * sum_xy) / denom
        n_coeff = (Mx * sum_x2 - My * sum_xy) / denom
    
    # Step 7: คำนวณแรงในเสาเข็มแต่ละต้น (Pi) - Slide 23
    df['Pi'] = (Q / n) + (m * df['x']) + (n_coeff * df['y'])

    # --- 3. OUTPUT & VISUALIZATION ---
    with col_graph:
        st.subheader("📊 2. ผลการวิเคราะห์และการกระจายแรง")
        
        # แสดงค่า Centroid ใหม่ที่เลื่อนไป
        c1, c2 = st.columns(2)
        c1.metric("Centroidใหม่ X̄", f"{X_bar:.2f} cm")
        c2.metric("Centroidใหม่ Ȳ", f"{Y_bar:.2f} cm")

        # กราฟแสดงผล (ใช้ตัวแปรตามสไลด์)
        fig, ax = plt.subplots(figsize=(7, 6))
        
        # จุดเสาเข็ม (ขนาดแปรผันตามแรง Pi)
        norm_size = (df['Pi'] / df['Pi'].max()) * 800 + 200
        scatter = ax.scatter(df['Actual_X'], df['Actual_Y'], s=norm_size, 
                            c=df['Pi'], cmap='Reds', edgecolors='black', linewidth=1.5, zorder=3)
        
        # เส้นกริดและแกน 0,0
        ax.axhline(0, color='black', lw=1, ls='--')
        ax.axvline(0, color='black', lw=1, ls='--')
        
        # จุด Centroid ใหม่ (สัญลักษณ์ X)
        ax.scatter(X_bar, Y_bar, color='blue', marker='X', s=200, label=f'New Centroid (X̄,Ȳ)', zorder=4)
        
        # ใส่ชื่อเสาและค่า Pi
        for i, row in df.iterrows():
            ax.text(row['Actual_X'], row['Actual_Y'] + 4, 
                    f"{row['No.']}\nPi={row['Pi']:.2f}", 
                    ha='center', fontsize=9, fontweight='bold')

        ax.set_xlabel("Actual Coordinate X (cm)")
        ax.set_ylabel("Actual Coordinate Y (cm)")
        ax.set_title(f"Pile Load Distribution (Q = {Q} tons)")
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)
        
        st.pyplot(fig)

    # --- 4. DATA SUMMARY TABLE ---
    st.subheader("📑 3. ตารางสรุปค่าตามขั้นตอนคำนวณ")
    output_display = df[['No.', 'Actual_X', 'Actual_Y', 'x', 'y', 'Pi']]
    st.dataframe(output_display.rename(columns={
        'Actual_X': 'X_act', 'Actual_Y': 'Y_act', 
        'x': 'x (relative)', 'y': 'y (relative)', 'Pi': 'Force Pi (tons)'
    }).style.highlight_max(subset=['Force Pi (tons)'], color='#ffcccc'), use_container_width=True)

    # --- 5. MATHEMATICAL STEPS (EXPANDABLE) ---
    with st.expander("🔍 ดูรายละเอียดการคำนวณรายขั้นตอน (Detailed Formulas)"):
        st.latex(r"\bar{X} = \frac{\sum X_{act}}{n}, \quad \bar{Y} = \frac{\sum Y_{act}}{n}")
        st.latex(r"M_x = Q \cdot \bar{Y}, \quad M_y = Q \cdot \bar{X}")
        st.latex(r"m = \frac{M_y \sum y^2 - M_x \sum xy}{\sum x^2 \sum y^2 - (\sum xy)^2}")
        st.latex(r"n = \frac{M_x \sum x^2 - M_y \sum xy}{\sum x^2 \sum y^2 - (\sum xy)^2}")
        st.latex(r"P_i = \frac{Q}{n} + m \cdot x_i + n \cdot y_i")
        
        st.write(f"**ค่าที่คำนวณได้:**")
        st.write(f"- Σx² = {sum_x2:.2f} | Σy² = {sum_y2:.2f} | Σxy = {sum_xy:.2f}")
        st.write(f"- m = {m:.6f} | n = {n_coeff:.6f}")
        st.write(f"- ตรวจสอบสมดุลแรง: ΣPi = {df['Pi'].sum():.2f} (ต้องเท่ากับ {Q})")

else:
    st.warning("กรุณากรอกข้อมูลในตารางพิกัด")
