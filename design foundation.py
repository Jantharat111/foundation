import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- 1. Function คำนวณหลัก ---
def calculate_pile_group(Q, ex, ey, x, y):
    N = len(x)
    Mx = Q * ey
    My = Q * ex
    
    # คำนวณค่าผลรวมต่างๆ
    sum_x2 = np.sum(x**2)
    sum_y2 = np.sum(y**2)
    sum_xy = np.sum(x * y)
    
    # คำนวณ m และ n (สูตรสำหรับหน้าตัดไม่สมมาตร)
    denom = (sum_x2 * sum_y2) - (sum_xy**2)
    
    # ป้องกันการหารด้วยศูนย์
    if abs(denom) < 1e-9:
        m, n = 0, 0
    else:
        m = (My * sum_y2 - Mx * sum_xy) / denom
        n = (Mx * sum_x2 - My * sum_xy) / denom
    
    # คำนวณแรง Pi ในแต่ละต้น
    Pi = (Q / N) + (m * x) + (n * y)
    
    return Pi, m, n, np.sum(Pi)

# --- 2. Streamlit UI ---
st.set_page_config(page_title="Pile Load Calculator", layout="wide")
st.title("🏗️ Pile Group Load Calculator (Unsymmetrical Method)")

# ส่วน Sidebar สำหรับ Input
with st.sidebar:
    st.header("Input Parameters")
    Q = st.number_input("Total Load (Q)", value=1000.0, step=100.0)
    ex = st.number_input("Eccentricity ex", value=0.50, step=0.1)
    ey = st.number_input("Eccentricity ey", value=0.30, step=0.1)
    
    st.divider()
    st.write("ระบุพิกัดเสาเข็ม (x, y)")
    # ค่าเริ่มต้น (ตัวอย่างเสา 4 ต้น)
    default_piles = pd.DataFrame({
        'x': [-1.0, 1.0, -1.0, 1.0],
        'y': [1.2, 1.2, -1.2, -1.2]
    })
    edited_df = st.data_editor(default_piles, num_rows="dynamic")

# --- 3. การประมวลผลและแสดงผล ---
if not edited_df.empty:
    x_coords = edited_df['x'].values
    y_coords = edited_df['y'].values
    
    # รัน function คำนวณ
    Pi, m_val, n_val, total_check = calculate_pile_group(Q, ex, ey, x_coords, y_coords)
    
    # สร้าง DataFrame ผลลัพธ์
    res_df = edited_df.copy()
    res_df['Pile Load (Pi)'] = Pi
    
    # แสดง Metric สำคัญ
    col1, col2, col3 = st.columns(3)
    col1.metric("Max Load", f"{Pi.max():.2f}")
    col2.metric("Min Load", f"{Pi.min():.2f}")
    col3.metric("Sum Pi (Check)", f"{total_check:.2f}")

    # ตารางผลลัพธ์
    st.subheader("Results Table")
    st.dataframe(res_df.style.highlight_max(axis=0, subset=['Pile Load (Pi)'], color='#ff4b4b'))

    # --- 4. การ Plot ด้วย Matplotlib ---
    st.subheader("Pile Layout Visualization")
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Plot ตำแหน่งเสาเข็ม
    sc = ax.scatter(x_coords, y_coords, s=Pi*2, c=Pi, cmap='viridis', edgecolors='black')
    plt.colorbar(sc, label='Load (Pi)')
    
    # ใส่หมายเลขเสาและค่าแรง
    for i, p in enumerate(Pi):
        ax.text(x_coords[i], y_coords[i] + 0.1, f"P{i+1}: {p:.1f}", ha='center', fontsize=9)
        
    # Plot จุดศูนย์กลางแรง (Resultant Load)
    ax.scatter(ex, ey, color='red', marker='X', s=100, label='Resultant Position (ex, ey)')
    
    ax.axhline(0, color='black', lw=0.5)
    ax.axvline(0, color='black', lw=0.5)
    ax.set_xlabel("X-axis")
    ax.set_ylabel("Y-axis")
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend()
    
    st.pyplot(fig)

    # สรุปสูตรที่ใช้
    with st.expander("Show Formulas"):
        st.latex(r"m = \frac{M_y \sum y^2 - M_x \sum xy}{\sum x^2 \sum y^2 - (\sum xy)^2}")
        st.latex(r"n = \frac{M_x \sum x^2 - My \sum xy}{\sum x^2 \sum y^2 - (\sum xy)^2}")
        st.latex(r"P_i = \frac{Q}{N} + m \cdot x + n \cdot y")
else:
    st.error("Please provide pile coordinates.")
