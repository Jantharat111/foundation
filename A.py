import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Pile Analysis (Bakhoum Method)", layout="wide")
st.title("🏗️ โปรแกรมวิเคราะห์แรงเสาเข็มตามขั้นตอนในสไลด์")
st.caption("อ้างอิงวิธีคำนวณ: รศ.ดร.อิทธิพล มีผล (Bakhoum, 1992)")

# --- Input Section ---
with st.sidebar:
    st.header("ข้อมูลพื้นฐาน")
    Q = st.number_input("แรงทั้งหมดที่ลงฐานราก (Q) [ton]", value=50.0)
    
    st.header("พิกัดการออกแบบและระยะเยื้อง")
    # ตัวอย่างข้อมูลจาก Slide 12-13
    data = {
        'Pile': ['P1', 'P2'],
        'Design_X': [-37.5, 37.5],  # พิกัดตามแบบ
        'Design_Y': [0.0, 0.0],
        'error_x': [0.0, 7.0],      # ระยะเยื้องที่ตรวจพบ (ex)
        'error_y': [5.0, -10.0]     # ระยะเยื้องที่ตรวจพบ (ey)
    }
    df_input = st.data_editor(pd.DataFrame(data), num_rows="dynamic")

if not df_input.empty:
    n = len(df_input)
    
    # --- STEP 1: หาจุด Centroid ใหม่ (Slide 5, 10) ---
    st.subheader("Step 1: คำนวณจุด Centroid ใหม่")
    centroid_x = df_input['error_x'].sum() / n
    centroid_y = df_input['error_y'].sum() / n
    
    col_c1, col_c2 = st.columns(2)
    col_c1.metric("Centroid X (X_bar)", f"{centroid_x:.3f} cm")
    col_c2.metric("Centroid Y (Y_bar)", f"{centroid_y:.3f} cm")

    # --- STEP 2: คำนวณโมเมนต์ (Slide 11) ---
    st.subheader("Step 2: คำนวณโมเมนต์จาก Centroid ใหม่")
    Mx = Q * centroid_y  # ในสไลด์ใช้ Q * Y_bar
    My = Q * centroid_x  # ในสไลด์ใช้ Q * X_bar
    
    col_m1, col_m2 = st.columns(2)
    col_m1.write(f"**Mx** = Q × Y_bar = {Q} × {centroid_y} = **{Mx:.2f} ton-cm**")
    col_m2.write(f"**My** = Q × X_bar = {Q} × {centroid_x} = **{My:.2f} ton-cm**")

    # --- STEP 3 & 4: คำนวณพิกัดใหม่และค่าผลรวม (Slide 12, 13) ---
    st.subheader("Step 3 & 4: คำนวณพิกัดใหม่เทียบกับ Centroid และค่า Summation")
    
    # พิกัดใหม่ = พิกัดเดิม + ระยะเยื้อง - Centroid
    df_input['x'] = df_input['Design_X'] + df_input['error_x'] - centroid_x
    df_input['y'] = df_input['Design_Y'] + df_input['error_y'] - centroid_y
    
    df_input['x2'] = df_input['x']**2
    df_input['y2'] = df_input['y']**2
    df_input['xy'] = df_input['x'] * df_input['y']
    
    st.dataframe(df_input[['Pile', 'x', 'y', 'x2', 'y2', 'xy']], use_container_width=True)
    
    sum_x2 = df_input['x2'].sum()
    sum_y2 = df_input['y2'].sum()
    sum_xy = df_input['xy'].sum()

    # --- STEP 5: คำนวณ m และ n (Slide 14, 15) ---
    st.subheader("Step 5: คำนวณสัมประสิทธิ์ m และ n (Bakhoum Equation)")
    
    denom = (sum_x2 * sum_y2) - (sum_xy**2)
    
    if abs(sum_xy) < 1e-5:
        st.success("กลุ่มเสาเข็มสมมาตร (Symmetric): ใช้สูตรอย่างง่าย")
        m = My / sum_x2
        n_coeff = Mx / sum_y2
    else:
        st.warning("กลุ่มเสาเข็มไม่สมมาตร (Unsymmetrical): ใช้สูตรเต็มของ Bakhoum")
        m = (My * sum_y2 - Mx * sum_xy) / denom
        n_coeff = (Mx * sum_x2 - My * sum_xy) / denom

    st.write(f"ค่า **m** = {m:.6f} | ค่า **n** = {n_coeff:.6f}")

    # --- STEP 6: คำนวณแรงในเสาแต่ละต้น (Slide 14) ---
    st.subheader("Step 6: สรุปแรงปฏิกิริยาในเสาเข็ม (Pi)")
    
    # Pi = Q/n + mx + ny
    df_input['Pi'] = (Q/n) + (m * df_input['x']) + (n_coeff * df_input['y'])
    
    st.table(df_input[['Pile', 'x', 'y', 'Pi']].rename(columns={'Pi': 'Force (ton)'}))
    
    # ตรวจสอบสมดุล
    st.write(f"**ตรวจสอบผลรวมแรง:** ΣPi = {df_input['Pi'].sum():.2f} ton (ต้องเท่ากับ Q = {Q})")

else:
    st.info("กรุณากรอกข้อมูลพิกัดเสาเข็มในแถบด้านข้าง")
