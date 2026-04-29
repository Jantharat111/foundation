import streamlit as st
import pandas as pd
import numpy as np

# ตั้งค่าหัวข้อ
st.set_page_config(page_title="Pile Group Analysis", layout="wide")
st.title("🏗️ Pile Group Load Calculation (Eccentric Load)")
st.write("คำนวณแรงในเสาเข็มแต่ละต้นด้วยวิธี $P_i = Q/N + m \cdot x + n \cdot y$")

# ส่วนรับ Input จากผู้ใช้
with st.sidebar:
    st.header("📥 Input Parameters")
    Q = st.number_input("Total Load (Q)", value=100.0, step=10.0)
    ex = st.number_input("Eccentricity in X-axis (ex)", value=0.5, step=0.1)
    ey = st.number_input("Eccentricity in Y-axis (ey)", value=0.3, step=0.1)
    
    st.divider()
    st.write("ระบุพิกัดเสาเข็ม (x, y) วัดจาก Centroid")
    # ตัวอย่างข้อมูลเริ่มต้น
    default_piles = pd.DataFrame({
        'x': [-1.0, 1.0, -1.0, 1.0],
        'y': [1.0, 1.0, -1.0, -1.0]
    })
    edited_piles = st.data_editor(default_piles, num_rows="dynamic")

# การคำนวณ
if not edited_piles.empty:
    x_coords = edited_piles['x'].values
    y_coords = edited_piles['y'].values
    N = len(x_coords)
    
    # 1. คำนวณค่า Sum of Squares
    sum_x2 = np.sum(x_coords**2)
    sum_y2 = np.sum(y_coords**2)
    
    # 2. หาค่า m และ n
    # m = Mx / Sum(x^2) โดยที่ Mx = Q * ex
    # n = My / Sum(y^2) โดยที่ My = Q * ey
    m = (Q * ex) / sum_x2 if sum_x2 != 0 else 0
    n = (Q * ey) / sum_y2 if sum_y2 != 0 else 0
    
    # 3. คำนวณ Pi สำหรับเสาเข็มแต่ละต้น
    piles_res = []
    for i in range(N):
        xi = x_coords[i]
        yi = y_coords[i]
        Pi = (Q / N) + (m * xi) + (n * yi)
        piles_res.append({
            "Pile No.": i + 1,
            "x": xi,
            "y": yi,
            "Load (Pi)": round(Pi, 4)
        })
    
    df_res = pd.DataFrame(piles_res)

    # แสดงผลลัพธ์
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📊 Result Table")
        st.table(df_res)
        
        st.info(f"""
        **Parameters Found:**
        - จำนวนเสาเข็ม ($N$): {N} ต้น
        - $m = (Q \\cdot e_x) / \\sum x^2$: {m:.4f}
        - $n = (Q \\cdot e_y) / \\sum y^2$: {n:.4f}
        """)

    with col2:
        st.subheader("📍 Pile Layout & Load")
        # แสดงกราฟตำแหน่งเสาเข็ม
        st.scatter_chart(
            df_res,
            x='x',
            y='y',
            size='Load (Pi)',
            color='Load (Pi)'
        )
        st.caption("ขนาดและสีของจุดแสดงถึงปริมาณแรงที่ลงเสาเข็ม")

else:
    st.warning("กรุณาใส่ข้อมูลพิกัดเสาเข็มในตารางด้านซ้าย")

# ส่วนแสดงสูตรที่ใช้
with st.expander("ดูสูตรที่ใช้คำนวณ"):
    st.latex(r"P_i = \frac{Q}{N} + \left( \frac{Q \cdot e_x}{\sum x^2} \right) x_i + \left( \frac{Q \cdot e_y}{\sum y^2} \right) y_i")
    st.write("โดยที่:")
    st.write("- $Q$: น้ำหนักรวมที่ลงฐานราก")
    st.write("- $e_x, e_y$: ระยะเยื้องศูนย์จากจุด Centroid")
    st.write("- $x_i, y_i$: พิกัดเสาเข็มต้นที่ $i$ วัดจากจุด Centroid")
