import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- CONFIG ---
st.set_page_config(page_title="Pile Load Analysis", layout="wide")

st.markdown("""
    <style>
    .stMetric { background-color: #f0f2f6; padding: 10px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.title("🏗️ โปรแกรมตรวจสอบแรงเสาเข็มเยื้องศูนย์")
st.info("คำนวณตามวิธี Bakhoum (1992) รองรับทั้งกลุ่มเสาเข็มสมมาตรและไม่สมมาตร")

# --- 1. INPUT SECTION ---
col1, col2 = st.columns([1, 2], gap="large")

with col1:
    st.subheader("1️⃣ ข้อมูลแรงและพิกัด")
    Q = st.number_input("น้ำหนักลงตอหม้อ (Q) [tons/kN]", value=50.0)
    
    st.write("---")
    st.write("📍 **ตารางพิกัดเสาเข็ม**")
    st.caption("กรอกพิกัดตามแบบ (Design) และระยะที่เยื้องจริงจากการก่อสร้าง (Error)")
    
    # ข้อมูลเริ่มต้นตามตัวอย่างในสไลด์
    initial_data = pd.DataFrame({
        'Pile': ['P1', 'P2', 'P3', 'P4'],
        'Design_X': [-50.0, 50.0, -50.0, 50.0],
        'Design_Y': [50.0, 50.0, -50.0, -50.0],
        'Error_X': [0.0, 5.0, 0.0, -2.0],  # ระยะเยื้องที่ตรวจพบจริง
        'Error_Y': [3.0, 0.0, -7.0, 0.0]
    })
    input_df = st.data_editor(initial_data, num_rows="dynamic", use_container_width=True)

# --- 2. CALCULATION LOGIC (ตามขั้นตอนในสไลด์) ---
if not input_df.empty:
    n_piles = len(input_df)
    
    # Step 1: คำนวณพิกัดจริง (Actual Coordinates)
    input_df['Actual_X'] = input_df['Design_X'] + input_df['Error_X']
    input_df['Actual_Y'] = input_df['Design_Y'] + input_df['Error_Y']
    
    # Step 2: หาจุด Centroid ใหม่ (Slide 10)
    x_bar = input_df['Actual_X'].mean()
    y_bar = input_df['Actual_Y'].mean()
    
    # Step 3: หาพิกัดสัมพัทธ์เทียบกับ Centroid ใหม่ (Slide 12)
    input_df['x'] = input_df['Actual_X'] - x_bar
    input_df['y'] = input_df['Actual_Y'] - y_bar
    
    # Step 4: คำนวณคุณสมบัติหน้าตัด (Slide 13)
    sum_x2 = (input_df['x']**2).sum()
    sum_y2 = (input_df['y']**2).sum()
    sum_xy = (input_df['x'] * input_df['y']).sum()
    
    # Step 5: คำนวณโมเมนต์ลัพธ์เทียบจุดหมุนใหม่ (Slide 11)
    Mx = Q * y_bar
    My = Q * x_bar
    
    # Step 6: คำนวณสัมประสิทธิ์ m, n (Bakhoum Formula - Slide 23)
    denom = (sum_x2 * sum_y2) - (sum_xy**2)
    if abs(denom) < 1e-9:
        m, n = 0, 0
    else:
        m = (My * sum_y2 - Mx * sum_xy) / denom
        n = (Mx * sum_x2 - My * sum_xy) / denom
    
    # Step 7: คำนวณแรง Pi = Q/n + mx + ny
    input_df['Force_Pi'] = (Q / n_piles) + (m * input_df['x']) + (n * input_df['y'])
    
    # --- 3. RESULT DISPLAY ---
    with col2:
        st.subheader("2️⃣ ผลการวิเคราะห์")
        
        # ส่วนแสดง Metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("Max Load", f"{input_df['Force_Pi'].max():.2f}")
        m2.metric("Min Load", f"{input_df['Force_Pi'].min():.2f}")
        m3.metric("Sum Pi Check", f"{input_df['Force_Pi'].sum():.1f}")
        
        # ส่วนแสดงพิกัดที่เบี้ยวไป (Centroid)
        st.warning(f"⚠️ จุดศูนย์กลางเปลี่ยนไปที่: X = {x_bar:.2f}, Y = {y_bar:.2f}")

        # ตารางสรุปแรง
        st.dataframe(
            input_df[['Pile', 'Actual_X', 'Actual_Y', 'Force_Pi']].rename(columns={'Force_Pi': 'แรงลงเสาเข็ม (Pi)'}),
            use_container_width=True, hide_index=True
        )

        # กราฟแสดงตำแหน่งเสาเข็ม
        fig, ax = plt.subplots(figsize=(6, 5))
        ax.scatter(input_df['Actual_X'], input_df['Actual_Y'], s=input_df['Force_Pi']*10, c=input_df['Force_Pi'], cmap='RdYlGn_r', edgecolors='k')
        
        # วาดจุด Centroid ใหม่
        ax.scatter(x_bar, y_bar, color='blue', marker='X', s=150, label='New Centroid')
        ax.scatter(0, 0, color='grey', marker='+', s=100, label='Design Center')

        for i, txt in enumerate(input_df['Pile']):
            ax.annotate(f"{txt}\n({input_df['Force_Pi'].iloc[i]:.1f})", (input_df['Actual_X'].iloc[i], input_df['Actual_Y'].iloc[i]+2), ha='center', fontsize=8)

        ax.set_title("ผังเสาเข็มและการกระจายแรงจริง")
        ax.legend(fontsize='small')
        ax.grid(True, linestyle=':', alpha=0.6)
        st.pyplot(fig)

# --- 4. EXPLAINER ---
with st.expander("📝 ดูขั้นตอนการคำนวณตามสไลด์"):
    st.write(f"""
    1. **หาจุด Centroid ใหม่:** $\\bar{{x}} = \\sum(X_{{design}} + e_x)/n$ = {x_bar:.2f}
    2. **คำนวณโมเมนต์:** $M_x = Q \\cdot \\bar{{y}}$ และ $M_y = Q \\cdot \\bar{{x}}$
    3. **พิกัดใหม่:** $x = X_{{actual}} - \\bar{{x}}$ และ $y = Y_{{actual}} - \\bar{{y}}$
    4. **คุณสมบัติกลุ่มเสา:** $\\sum x^2 = {sum_x2:.2f}, \\sum y^2 = {sum_y2:.2f}, \\sum xy = {sum_xy:.2f}$
    5. **สมการ Bakhoum:** ใช้ค่า $m$ และ $n$ เพื่อหาแรงลงเสาเข็มแต่ละต้น
    """)
