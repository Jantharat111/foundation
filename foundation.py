"""
Pile Group - Eccentric Load Calculator
สูตร: Pi = Q/N + m*xi + n*yi
โดย m, n หาจากระบบสมการกำลังสองน้อยที่สุด (least squares)

  ΣMx = Q*ey  →  n*Σyi² = Q*ey  →  n = Q*ey / Σyi²
  ΣMy = Q*ex  →  m*Σxi² = Q*ex  →  m = Q*ex / Σxi²
"""

import numpy as np

# ─────────────────────────────────────────────
#  ข้อมูลนำเข้า (INPUT)
# ─────────────────────────────────────────────
Q  = 1000.0   # แรงกระทำแนวดิ่งรวม (kN)
ex =    1.0   # ระยะเยื้องศูนย์ในทิศ x (m)
ey =    0.5   # ระยะเยื้องศูนย์ในทิศ y (m)

# พิกัดเสาเข็มแต่ละต้น (x, y) หน่วย เมตร
piles_xy = np.array([
    [-1.5, -1.5],
    [ 0.0, -1.5],
    [ 1.5, -1.5],
    [-1.5,  0.0],
    [ 0.0,  0.0],
    [ 1.5,  0.0],
    [-1.5,  1.5],
    [ 0.0,  1.5],
    [ 1.5,  1.5],
], dtype=float)

# ─────────────────────────────────────────────
#  คำนวณ
# ─────────────────────────────────────────────
N  = len(piles_xy)
xi = piles_xy[:, 0]
yi = piles_xy[:, 1]

sum_x2 = np.sum(xi**2)
sum_y2 = np.sum(yi**2)

# m, n (ความชันโมเมนต์)
#   m*Σxi² = Q*ex  →  m = Q*ex / Σxi²
#   n*Σyi² = Q*ey  →  n = Q*ey / Σyi²
m = Q * ex / sum_x2 if sum_x2 != 0 else 0.0
n = Q * ey / sum_y2 if sum_y2 != 0 else 0.0

# แรงในแต่ละเสาเข็ม
Pi = Q / N + m * xi + n * yi

# ─────────────────────────────────────────────
#  แสดงผล
# ─────────────────────────────────────────────
SEP  = "=" * 58
sep2 = "-" * 58

print(SEP)
print("   PILE GROUP — ECCENTRIC LOAD ANALYSIS")
print(SEP)

print(f"\n{'INPUT':}")
print(f"  {'แรงกระทำรวม  Q':<28} = {Q:>10.2f}  kN")
print(f"  {'ระยะเยื้องศูนย์ ex':<28} = {ex:>10.3f}  m")
print(f"  {'ระยะเยื้องศูนย์ ey':<28} = {ey:>10.3f}  m")
print(f"  {'จำนวนเสาเข็ม  N':<28} = {N:>10d}  ต้น")

print(f"\n{'INTERMEDIATE VALUES':}")
print(f"  {'Σxi²':<28} = {sum_x2:>10.4f}  m²")
print(f"  {'Σyi²':<28} = {sum_y2:>10.4f}  m²")
print(f"  {'m  = Q·ex / Σxi²':<28} = {m:>10.4f}  kN/m")
print(f"  {'n  = Q·ey / Σyi²':<28} = {n:>10.4f}  kN/m")
print(f"  {'Q/N (แรงเฉลี่ย)':<28} = {Q/N:>10.4f}  kN")

print(f"\n{'PILE FORCES   Pi = Q/N + m·xi + n·yi':}")
print(sep2)
print(f"  {'#':<5} {'x (m)':>8} {'y (m)':>8} {'Q/N':>10} {'m·xi':>10} {'n·yi':>10} {'Pi (kN)':>10}")
print(sep2)
for i in range(N):
    qn   = Q / N
    mxi  = m * xi[i]
    nyi  = n * yi[i]
    print(f"  {i+1:<5} {xi[i]:>8.3f} {yi[i]:>8.3f} {qn:>10.2f} {mxi:>10.2f} {nyi:>10.2f} {Pi[i]:>10.2f}")
print(sep2)

print(f"\n{'SUMMARY':}")
print(f"  {'แรงสูงสุด  P_max':<28} = {Pi.max():>10.2f}  kN  (เสาต้นที่ {Pi.argmax()+1})")
print(f"  {'แรงต่ำสุด  P_min':<28} = {Pi.min():>10.2f}  kN  (เสาต้นที่ {Pi.argmin()+1})")
print(f"  {'แรงเฉลี่ย':<28} = {Pi.mean():>10.2f}  kN")
print(f"  {'ΣPi (ต้องเท่ากับ Q)':<28} = {Pi.sum():>10.2f}  kN")

# ตรวจสอบสมดุล
ok_force  = np.isclose(Pi.sum(),        Q,     atol=1e-6)
ok_mom_x  = np.isclose(np.sum(Pi * yi), Q * ey, atol=1e-6)
ok_mom_y  = np.isclose(np.sum(Pi * xi), Q * ex, atol=1e-6)

print(f"\n{'EQUILIBRIUM CHECK':}")
print(f"  {'ΣPi = Q':<35} {'✓ OK' if ok_force else '✗ FAIL'}")
print(f"  {'ΣPi·yi = Q·ey (โมเมนต์รอบแกน x)':<35} {'✓ OK' if ok_mom_x else '✗ FAIL'}")
print(f"  {'ΣPi·xi = Q·ex (โมเมนต์รอบแกน y)':<35} {'✓ OK' if ok_mom_y else '✗ FAIL'}")
print(SEP)
