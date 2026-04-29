import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- 1. Function สำหรับคำนวณตามวิธี Bakhoum (1992) ---
def calculate_pile_loads(Q, ex, ey, x, y):
    N = len(x)
    Mx = Q * ey  # โมเมนต์รอบแกน X
    My = Q * ex  # โมเมนต์รอบแกน Y
    
    # คำนวณค่าผลรวมทางสถิติของพิกัด
    sum_x2 = np.sum(x**2)
    sum_y2 = np.sum(y**2)
    sum_xy = np.sum(x * y)
    
    # คำนวณ m และ n ตามสูตรในเอกสารหน้า 23
    # m = (My*sum_y2 - Mx*sum_xy) / (sum_x2*sum_y2 - sum_xy^2)
    # n = (Mx*sum_x2 - My*sum_xy) / (sum_x2*sum_y2 - sum_xy^2)
    denom = (sum_x2 * sum_y2) - (sum_xy**2)
    
    if abs(denom) < 1e-9: # ป้องกันกรณีหารด้วยศูนย์
        m, n = 0, 0
    else:
        m = (My * sum_y2 - Mx * sum_xy) / denom
        n = (Mx * sum_x2 - My * sum_xy) / denom
    
    # คำนวณแรง Pi ในเสาเข็มแต่ละต้น
    Pi = (Q / N) + (m * x) + (n * y)
    
    return Pi, np.sum(Pi)

# --- 2. Streamlit UI Design ---
st.set_page_config(page_title="Pile Analysis Pro", layout="wide")
st.title("🏗️ Pile Group Load Analysis (Bakhoum Method)")
st.markdown("คำนวณแรงลงเสาเข็มรายต้น กรณีรับแรงเยื้องศูนย์แบบไม่สมมาตร")

# ส่วนรับ Input
col_input, col_result = st.columns([1, 2], gap="large")

with col_input:
    st.subheader("📥 ข้อมูลนำเข้า")
    Q = st.number_input("แรงทั้งหมด (Q) [kN/Tons]", value=1000.0, step=100.0)
    ex = st.number_input("ระยะเยื้อง ex [m]", value=0.40, step=0.05)
    ey = st.number_input("ระยะเยื้อง ey [m]", value=0.20, step=0.05)
    
    st.divider()
    st.write("📍 **พิกัดเสาเข็ม (x, y)** วัดจาก Centroid")
    # ตัวอย่างข้อมูลเริ่มต้น (4 ต้น)
    default_data = pd.DataFrame({
        'x': [-1.0, 1.0, -1.0, 1.0],
        'y': [1.2, 1.2, -1.2, -1.2]
    })
    edited_df = st.data_editor(default_data, num_rows="dynamic", use_container_width=True)

# --- 3. การประมวลผล ---
if not edited_df.empty:
    x_coords = edited_df['x'].values
    y_coords = edited_df['y'].values
    
    # คำนวณผลลัพธ์
    Pi_array, total_check = calculate_pile_loads(Q, ex, ey, x_coords, y_coords)
    
    # จัดเตรียม DataFrame แสดงผล
    res_df = edited_df.copy()
    res_df.insert(0, "Pile No.", [f"P{i+1}" for i in range(len(x_coords))])
    res_df['Load (Pi)'] = np.round(Pi_array, 2)

    with col_result:
        st.subheader("✅ สรุปผลการคำนวณ")
        
        # แสดง Metric สำคัญ
        m1, m2, m3 = st.columns(3)
        m1.metric("Max Load", f"{Pi_array.max():.2f}")
        m2.metric("Min Load", f"{Pi_array.min():.2f}")
        m3.metric("Sum Check", f"{total_check:.2f}", delta=f"{total_check-Q:.2f} (Error)")

        # ตารางผลลัพธ์พร้อม Highlight ตัวที่รับแรงสูงสุด
        st.dataframe(
            res_df.style.highlight_max(axis=0, subset=['Load (Pi)'], color='#FF4B4B'),
            use_container_width=True, hide_index=True
        )

        # --- 4. การ Plot ด้วย Matplotlib ---
        st.subheader("📍 Pile Layout & Distribution")
        fig, ax = plt.subplots(figsize=(7, 5))
        
        # วาดตำแหน่งเสาเข็ม
        scatter = ax.scatter(x_coords, y_coords, s=Pi_array*5, c=Pi_array, cmap='YlOrRd', edgecolors='black', alpha=0.8)
        
        # ใส่ชื่อและค่าแรงกำกับที่เสา
        for i, val in enumerate(Pi_array):
            ax.text(x_coords[i], y_coords[i] + 0.15, f"P{i+1}\n({val:.1f})", ha='center', fontsize=9, fontweight='bold')
            
        # วาดจุดแรงลง (Resultant Point)
        ax.scatter(ex, ey, color='blue', marker='X', s=200, label='Resultant (ex, ey)')
        
        # ตกแต่งกราฟ
        ax.axhline(0, color='grey', lw=0.8, ls='--')
        ax.axvline(0, color='grey', lw=0.8, ls='--')
        ax.set_xlabel("X-Axis (m)")
        ax.set_ylabel("Y-Axis (m)")
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        st.pyplot(fig)

else:
    st.info("กรุณาป้อนข้อมูลพิกัดในตารางฝั่งซ้าย")
