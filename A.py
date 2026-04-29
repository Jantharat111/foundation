import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- ฟังก์ชันคำนวณ (General Case) ---
def calculate_pile_loads(Q, ex, ey, x, y):
    N = len(x)
    Mx = Q * ey  # Moment รอบแกน X
    My = Q * ex  # Moment รอบแกน Y
    
    # คำนวณค่าทางสถิติ
    sum_x2 = np.sum(x**2)
    sum_y2 = np.sum(y**2)
    sum_xy = np.sum(x * y)
    
    # ตัวหาร (Denominator) ตามวิธี Bakhoum
    denom = (sum_x2 * sum_y2) - (sum_xy**2)
    
    if abs(denom) < 1e-9:
        return np.full(N, Q/N), 0, 0, sum_xy # กรณีเสาอยู่ที่จุดเดียวซ้อนกัน
    
    # คำนวณสัมประสิทธิ์ m และ n (ซ่อนไว้เบื้องหลัง)
    m = (My * sum_y2 - Mx * sum_xy) / denom
    n = (Mx * sum_x2 - My * sum_xy) / denom
    
    # แรงในเสาแต่ละต้น Pi = Q/N + mx + ny
    Pi = (Q / N) + (m * x) + (n * y)
    
    return Pi, m, n, sum_xy

# --- ส่วนการแสดงผลบน Streamlit ---
st.set_page_config(page_title="Pile Group Analysis", layout="wide")
st.title("🏗️ วิเคราะห์แรงเสาเข็ม (Symmetric & Unsymmetrical)")
st.info("โปรแกรมใช้สมการทั่วไปของ Bakhoum (1992) ซึ่งรองรับทั้งกลุ่มเสาเข็มแบบสมมาตรและไม่สมมาตร")

# Sidebar Input
with st.sidebar:
    st.header("1. ข้อมูลแรงที่ลงฐานราก")
    Q = st.number_input("แรงทั้งหมด (Q)", value=1200.0, step=100.0)
    ex = st.number_input("ระยะเยื้องแกน X (ex)", value=0.45, step=0.05)
    ey = st.number_input("ระยะเยื้องแกน Y (ey)", value=0.30, step=0.05)
    
    st.header("2. พิกัดเสาเข็ม (x, y)")
    # ตัวอย่าง: ลองเปลี่ยนค่า x, y ให้ไม่สมมาตรเพื่อทดสอบ
    default_piles = pd.DataFrame({
        'x': [-0.8, 0.8, -0.8, 1.2], # เสาต้นที่ 4 เบี้ยวไปทางขวา (ไม่สมมาตร)
        'y': [1.0, 1.0, -1.0, -1.0]
    })
    pile_input = st.data_editor(default_piles, num_rows="dynamic", use_container_width=True)

# ส่วนคำนวณและแสดงผล
if not pile_input.empty:
    x_val = pile_input['x'].values
    y_val = pile_input['y'].values
    
    # คำนวณ
    loads, m_val, n_val, s_xy = calculate_pile_loads(Q, ex, ey, x_val, y_val)
    
    # ผลลัพธ์
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📊 สรุปผลแรงในเสาเข็ม")
        
        # แสดงสถานะความสมมาตร
        if abs(s_xy) < 1e-5:
            st.success("สถานะ: กลุ่มเสาเข็มแบบสมมาตร (Symmetric)")
        else:
            st.warning(f"สถานะ: กลุ่มเสาเข็มแบบไม่สมมาตร (Unsymmetrical) [Σxy = {s_xy:.2f}]")

        res_df = pile_input.copy()
        res_df.insert(0, "Pile", [f"P{i+1}" for i in range(len(x_val))])
        res_df['Force (Pi)'] = np.round(loads, 2)
        
        st.table(res_df.style.highlight_max(axis=0, subset=['Force (Pi)'], color='#ffcccc'))
        
        st.metric("Total Sum Check", f"{np.sum(loads):.2f}", delta=f"Gap: {np.sum(loads)-Q:.4f}")

    with col2:
        st.subheader("📍 ผังการกระจายแรง")
        fig, ax = plt.subplots(figsize=(6, 5))
        
        # วาดเสาเข็ม
        # ปรับขนาดจุดตามแรง (ให้เห็นความต่างชัดเจน)
        sc = ax.scatter(x_val, y_val, s=loads*2, c=loads, cmap='autumn_r', edgecolors='black', zorder=3)
        plt.colorbar(sc, label='Load')

        # ใส่เลขเสาและค่าแรง
        for i, (xi, yi) in enumerate(zip(x_val, y_val)):
            ax.text(xi, yi+0.15, f"P{i+1}\n({loads[i]:.1f})", ha='center', fontsize=9, fontweight='bold')

        # จุดแรงลงจริง
        ax.scatter(ex, ey, color='blue', marker='X', s=150, label='Resultant Load', zorder=4)
        
        ax.axhline(0, color='black', lw=0.5); ax.axvline(0, color='black', lw=0.5)
        ax.grid(True, linestyle=':', alpha=0.6)
        ax.set_xlabel("X-coord"); ax.set_ylabel("Y-coord")
        ax.legend()
        st.pyplot(fig)

else:
    st.error("กรุณากรอกพิกัดเสาเข็ม")
