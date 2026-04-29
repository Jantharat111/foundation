"""
Pile Group — Eccentric Load Analysis (General Case)
=====================================================
สูตรทั่วไปรองรับกรณีที่ sum_xy ≠ 0 (กลุ่มเสาไม่สมมาตร)

  Mx = Q * ey,  My = Q * ex
  det = sum_x2 * sum_y2 - sum_xy²
  m   = (My*sum_y2 - Mx*sum_xy) / det
  n   = (Mx*sum_x2 - My*sum_xy) / det
  Pi  = Q/N + m*xi + n*yi
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable


# ═══════════════════════════════════════════════════════════════
#  FUNCTION
# ═══════════════════════════════════════════════════════════════

def pile_group_eccentric(Q: float, ex: float, ey: float,
                          coords: np.ndarray) -> dict:
    """
    คำนวณแรงในเสาเข็มกลุ่มแบบเยื้องศูนย์ (general case)

    Parameters
    ----------
    Q      : แรงกระทำแนวดิ่งรวม (kN)
    ex     : ระยะเยื้องศูนย์ทิศ x (m)  → ก่อโมเมนต์รอบแกน y
    ey     : ระยะเยื้องศูนย์ทิศ y (m)  → ก่อโมเมนต์รอบแกน x
    coords : array shape (N, 2) พิกัด (x, y) เสาแต่ละต้น (m)

    Returns
    -------
    dict ที่มีกุญแจ: N, Mx, My, sum_x2, sum_y2, sum_xy,
                     det, m, n, Pi, idx_max, idx_min
    """
    coords = np.asarray(coords, dtype=float)
    xi, yi = coords[:, 0], coords[:, 1]
    N = len(xi)

    # โมเมนต์
    Mx = Q * ey          # โมเมนต์รอบแกน x
    My = Q * ex          # โมเมนต์รอบแกน y

    # ผลรวมกำลังสองและคูณไขว้ของพิกัด
    sum_x2 = np.sum(xi ** 2)
    sum_y2 = np.sum(yi ** 2)
    sum_xy = np.sum(xi * yi)

    # determinant
    det = sum_x2 * sum_y2 - sum_xy ** 2
    if np.isclose(det, 0):
        raise ValueError(
            "det = 0 → ระบบสมการไม่มีคำตอบเอกลักษณ์ "
            "(เสาเข็มทั้งหมดอยู่บนเส้นตรงเดียวกัน)"
        )

    # ค่าสัมประสิทธิ์ m, n
    m = (My * sum_y2 - Mx * sum_xy) / det
    n = (Mx * sum_x2 - My * sum_xy) / det

    # แรงในแต่ละเสาเข็ม
    Pi = Q / N + m * xi + n * yi

    return {
        "N": N, "xi": xi, "yi": yi,
        "Mx": Mx, "My": My,
        "sum_x2": sum_x2, "sum_y2": sum_y2, "sum_xy": sum_xy,
        "det": det, "m": m, "n": n,
        "Pi": Pi,
        "idx_max": int(np.argmax(Pi)),
        "idx_min": int(np.argmin(Pi)),
    }


# ═══════════════════════════════════════════════════════════════
#  PRINT REPORT
# ═══════════════════════════════════════════════════════════════

def print_report(Q: float, ex: float, ey: float, r: dict) -> None:
    """พิมพ์รายงานผลการคำนวณ"""
    W = 62
    SEP  = "═" * W
    sep2 = "─" * W

    print(f"\n{SEP}")
    print(f"{'PILE GROUP — ECCENTRIC LOAD ANALYSIS':^{W}}")
    print(SEP)

    # ─ Input ─
    print(f"\n  INPUT")
    print(f"  {'Q (แรงรวม)':<30} = {Q:>10.2f}  kN")
    print(f"  {'ex (เยื้องศูนย์ทิศ x)':<30} = {ex:>10.4f}  m")
    print(f"  {'ey (เยื้องศูนย์ทิศ y)':<30} = {ey:>10.4f}  m")
    print(f"  {'N (จำนวนเสาเข็ม)':<30} = {r['N']:>10d}  ต้น")

    # ─ Intermediate ─
    print(f"\n  MOMENT")
    print(f"  {'Mx = Q·ey':<30} = {r['Mx']:>10.2f}  kN·m")
    print(f"  {'My = Q·ex':<30} = {r['My']:>10.2f}  kN·m")

    print(f"\n  SECOND MOMENTS OF AREA")
    print(f"  {'Σxi²':<30} = {r['sum_x2']:>10.4f}  m²")
    print(f"  {'Σyi²':<30} = {r['sum_y2']:>10.4f}  m²")
    print(f"  {'Σxi·yi':<30} = {r['sum_xy']:>10.4f}  m²")
    print(f"  {'det = Σxi²·Σyi² − (Σxi·yi)²':<30} = {r['det']:>10.4f}  m⁴")

    print(f"\n  COEFFICIENTS")
    print(f"  {'m = (My·Σyi²−Mx·Σxy)/det':<30} = {r['m']:>10.4f}  kN/m")
    print(f"  {'n = (Mx·Σxi²−My·Σxy)/det':<30} = {r['n']:>10.4f}  kN/m")
    print(f"  {'Q/N (แรงเฉลี่ย)':<30} = {Q/r['N']:>10.4f}  kN")

    # ─ Pile table ─
    print(f"\n  PILE FORCES   Pi = Q/N + m·xi + n·yi")
    print(f"  {sep2}")
    hdr = f"  {'#':>4}  {'x(m)':>7}  {'y(m)':>7}  {'Q/N':>9}  {'m·xi':>9}  {'n·yi':>9}  {'Pi(kN)':>9}"
    print(hdr)
    print(f"  {sep2}")

    qn = Q / r['N']
    for i in range(r['N']):
        mxi = r['m'] * r['xi'][i]
        nyi = r['n'] * r['yi'][i]
        tag = "  ← MAX" if i == r['idx_max'] else ("  ← MIN" if i == r['idx_min'] else "")
        print(f"  {i+1:>4}  {r['xi'][i]:>7.3f}  {r['yi'][i]:>7.3f}  "
              f"{qn:>9.2f}  {mxi:>9.2f}  {nyi:>9.2f}  {r['Pi'][i]:>9.2f}{tag}")

    print(f"  {sep2}")

    # ─ Summary ─
    print(f"\n  SUMMARY")
    print(f"  {'P_max':<30} = {r['Pi'].max():>10.2f}  kN  (เสาต้นที่ {r['idx_max']+1})")
    print(f"  {'P_min':<30} = {r['Pi'].min():>10.2f}  kN  (เสาต้นที่ {r['idx_min']+1})")
    print(f"  {'P_mean':<30} = {r['Pi'].mean():>10.2f}  kN")
    print(f"  {'ΣPi':<30} = {r['Pi'].sum():>10.2f}  kN")

    # ─ Equilibrium check ─
    ck_sum = np.isclose(r['Pi'].sum(),              Q,        atol=1e-6)
    ck_mx  = np.isclose(np.sum(r['Pi'] * r['yi']), r['Mx'],  atol=1e-6)
    ck_my  = np.isclose(np.sum(r['Pi'] * r['xi']), r['My'],  atol=1e-6)
    print(f"\n  EQUILIBRIUM CHECK")
    print(f"  {'ΣPi = Q':<45} {'✓' if ck_sum else '✗'}")
    print(f"  {'ΣPi·yi = Mx  (โมเมนต์รอบแกน x)':<45} {'✓' if ck_mx  else '✗'}")
    print(f"  {'ΣPi·xi = My  (โมเมนต์รอบแกน y)':<45} {'✓' if ck_my  else '✗'}")
    print(f"\n{SEP}\n")


# ═══════════════════════════════════════════════════════════════
#  PLOT
# ═══════════════════════════════════════════════════════════════

def plot_pile_group(Q: float, ex: float, ey: float, r: dict,
                    title: str = "Pile Group — Eccentric Load") -> None:
    """วาดแผนผังกลุ่มเสาเข็มพร้อม color map ตามขนาดแรง"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6),
                              gridspec_kw={"width_ratios": [1.6, 1]})
    fig.patch.set_facecolor("#1a1a2e")
    ax, ax2 = axes

    # ── แผนผัง ──────────────────────────────────────────────
    ax.set_facecolor("#16213e")
    Pi   = r["Pi"]
    xi, yi = r["xi"], r["yi"]

    norm = Normalize(vmin=Pi.min(), vmax=Pi.max())
    cmap = plt.cm.RdYlGn           # แดง=แรงน้อย, เขียว=แรงมาก

    pile_r = 0.18                  # รัศมีวงกลมเสาเข็ม

    for i in range(r["N"]):
        color = cmap(norm(Pi[i]))
        circle = plt.Circle((xi[i], yi[i]), pile_r,
                             color=color, zorder=3, ec="white", lw=0.8)
        ax.add_patch(circle)
        ax.text(xi[i], yi[i] + pile_r + 0.12, f"P{i+1}",
                ha="center", va="bottom", fontsize=7.5,
                color="white", fontweight="bold")
        ax.text(xi[i], yi[i], f"{Pi[i]:.1f}",
                ha="center", va="center", fontsize=7,
                color="black" if norm(Pi[i]) > 0.35 else "white",
                fontweight="bold")

    # จุดศูนย์ถ่วงและจุดแรงกระทำ
    ax.scatter(0, 0, s=120, color="cyan", zorder=5, label="จุดศูนย์กลาง (0,0)")
    ax.scatter(ex, ey, s=150, marker="*", color="yellow",
               zorder=6, label=f"จุดแรงกระทำ ({ex},{ey})")
    ax.annotate("", xy=(ex, ey), xytext=(0, 0),
                arrowprops=dict(arrowstyle="->", color="yellow",
                                lw=1.5, linestyle="dashed"))

    # ตาราง grid
    pad = 0.8
    ax.set_xlim(xi.min() - pad, xi.max() + pad)
    ax.set_ylim(yi.min() - pad, yi.max() + pad)
    ax.set_aspect("equal")
    ax.set_xlabel("x (m)", color="white")
    ax.set_ylabel("y (m)", color="white")
    ax.set_title(title, color="white", fontsize=12, fontweight="bold", pad=10)
    ax.tick_params(colors="white")
    for spine in ax.spines.values():
        spine.set_edgecolor("#444")
    ax.grid(True, color="#334", linewidth=0.5, linestyle="--")
    ax.legend(fontsize=8, facecolor="#111", labelcolor="white",
              loc="upper left", framealpha=0.7)

    # colorbar
    sm = ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax, shrink=0.8, pad=0.02)
    cbar.set_label("Pi (kN)", color="white")
    cbar.ax.yaxis.set_tick_params(color="white")
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color="white")

    # ── แผนภูมิแท่ง ─────────────────────────────────────────
    ax2.set_facecolor("#16213e")
    colors_bar = [cmap(norm(p)) for p in Pi]
    labels = [f"P{i+1}" for i in range(r["N"])]
    bars = ax2.bar(labels, Pi, color=colors_bar, edgecolor="white", linewidth=0.6)

    # เส้น Q/N
    ax2.axhline(Q / r["N"], color="cyan", linestyle="--", linewidth=1.2,
                label=f"Q/N = {Q/r['N']:.1f} kN")
    ax2.axhline(0, color="white", linestyle="-", linewidth=0.5)

    # ป้ายค่าบนแท่ง
    for bar, val in zip(bars, Pi):
        ypos = val + (Pi.max() - Pi.min()) * 0.02 if val >= 0 else val - (Pi.max() - Pi.min()) * 0.05
        ax2.text(bar.get_x() + bar.get_width() / 2, ypos,
                 f"{val:.1f}", ha="center", va="bottom",
                 fontsize=7.5, color="white", fontweight="bold")

    ax2.set_xlabel("เสาเข็ม", color="white")
    ax2.set_ylabel("Pi (kN)", color="white")
    ax2.set_title("แรงในแต่ละเสาเข็ม", color="white", fontsize=11, fontweight="bold")
    ax2.tick_params(colors="white")
    ax2.legend(fontsize=8, facecolor="#111", labelcolor="white", framealpha=0.7)
    for spine in ax2.spines.values():
        spine.set_edgecolor("#444")
    ax2.grid(axis="y", color="#334", linewidth=0.5, linestyle="--")

    plt.tight_layout(pad=2)
    out = "pile_group_plot.png"
    plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    print(f"  [บันทึกภาพ → {out}]")
    plt.show()


# ═══════════════════════════════════════════════════════════════
#  MAIN — ตัวอย่าง 2 กรณี
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":

    # ── ตัวอย่างที่ 1: กลุ่มเสา 3×3 สมมาตร ──────────────────
    print("\n" + "▓" * 62)
    print("  ตัวอย่างที่ 1 : กลุ่มเสา 3×3 (สมมาตร)")
    print("▓" * 62)

    coords1 = np.array([
        [-1.5, -1.5], [0.0, -1.5], [1.5, -1.5],
        [-1.5,  0.0], [0.0,  0.0], [1.5,  0.0],
        [-1.5,  1.5], [0.0,  1.5], [1.5,  1.5],
    ])
    r1 = pile_group_eccentric(Q=1000, ex=1.0, ey=0.5, coords=coords1)
    print_report(Q=1000, ex=1.0, ey=0.5, r=r1)
    plot_pile_group(Q=1000, ex=1.0, ey=0.5, r=r1,
                    title="Example 1 — 3×3 Symmetric Pile Group")

    # ── ตัวอย่างที่ 2: กลุ่มเสาไม่สมมาตร (sum_xy ≠ 0) ───────
    print("\n" + "▓" * 62)
    print("  ตัวอย่างที่ 2 : กลุ่มเสาไม่สมมาตร (sum_xy ≠ 0)")
    print("▓" * 62)

    coords2 = np.array([
        [0.0,  0.0],
        [2.0,  0.0],
        [3.0,  1.5],
        [1.0,  2.0],
        [0.5,  1.0],
    ])
    r2 = pile_group_eccentric(Q=800, ex=0.3, ey=0.4, coords=coords2)
    print_report(Q=800, ex=0.3, ey=0.4, r=r2)
    plot_pile_group(Q=800, ex=0.3, ey=0.4, r=r2,
                    title="Example 2 — Asymmetric Pile Group")
