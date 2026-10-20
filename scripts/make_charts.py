#!/usr/bin/env python3
"""Build the 10 charts for the Harga Cabai 2026 project.

Reads data/raw/*.csv (fetched from the PIHPS public API). All numbers
come from the data; nothing is hardcoded.
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
RAW = HERE / "data" / "raw"
CHARTS = HERE / "charts"
CHARTS.mkdir(exist_ok=True)

# Tema T1: marine / bright red / butter di atas ground krem
GROUND = "#F7F4EE"
INK = "#0B2A44"
MARINE = "#0E4D7A"
RED = "#E5322D"
BUTTER = "#F5C542"
GRAYNEUT = "#9AA3AD"

COLORS = {
    "Cabai Merah Besar": INK,
    "Cabai Merah Keriting": MARINE,
    "Cabai Rawit Hijau": BUTTER,
    "Cabai Rawit Merah": RED,
}
ORDER = ["Cabai Merah Besar", "Cabai Merah Keriting", "Cabai Rawit Hijau", "Cabai Rawit Merah"]

plt.rcParams.update({
    "font.family": "Noto Sans", "font.size": 11,
    "axes.titlesize": 14, "axes.titleweight": "bold",
    "axes.labelsize": 11, "figure.dpi": 150,
    "figure.facecolor": GROUND, "axes.facecolor": GROUND,
    "savefig.facecolor": GROUND,
    "text.color": INK, "axes.edgecolor": INK, "axes.unicode_minus": False,
    "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
})


def rp(x, _pos=None):
    return f"Rp{x:,.0f}".replace(",", ".")


def style(ax):
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.3)
    ax.set_axisbelow(True)


def main():
    nas = pd.read_csv(RAW / "harga_cabai_nasional.csv", parse_dates=["tanggal"])
    prov = pd.read_csv(RAW / "harga_cabai_harian.csv", parse_dates=["tanggal"])
    nas = nas.dropna(subset=["harga_rp_per_kg"])
    prov = prov.dropna(subset=["harga_rp_per_kg"])
    nas["tahun"] = nas["tanggal"].dt.year
    piv = nas.pivot(index="tanggal", columns="komoditas", values="harga_rp_per_kg")

    # 01 - Tren nasional 4 cabai, periode penuh
    fig, ax = plt.subplots(figsize=(12, 5.5))
    for c in ORDER:
        ax.plot(piv.index, piv[c], color=COLORS[c], label=c, lw=1.6)
    ax.set_title("Harga Cabai Nasional per Hari (PIHPS, Jan 2025 - Okt 2026)")
    ax.set_ylabel("Rp/kg"); ax.yaxis.set_major_formatter(mticker.FuncFormatter(rp))
    ax.legend(frameon=False, ncol=2); style(ax); fig.tight_layout()
    fig.savefig(CHARTS / "01_tren_nasional_4cabai.png"); plt.close(fig)

    # 02 - Zoom 2026 + anotasi lonjakan Oktober
    d26 = piv[piv.index >= "2026-01-01"]
    fig, ax = plt.subplots(figsize=(12, 5.5))
    for c in ORDER:
        ax.plot(d26.index, d26[c], color=COLORS[c], label=c, lw=1.6)
    ax.set_title("Harga Cabai Nasional 2026 - Lonjakan Oktober")
    ax.set_ylabel("Rp/kg"); ax.yaxis.set_major_formatter(mticker.FuncFormatter(rp))
    ax.legend(frameon=False, ncol=2); style(ax)
    ax.axhline(100000, color="gray", ls="--", lw=1)
    ax.text(d26.index[5], 102000, "Rp100.000/kg", color="gray", fontsize=10)
    fig.tight_layout(); fig.savefig(CHARTS / "02_tren_2026_zoom.png"); plt.close(fig)

    # 03 - Volatilitas 2026 (CV)
    s26 = nas[nas["tahun"] == 2026]
    cv = s26.groupby("komoditas")["harga_rp_per_kg"].agg(
        lambda s: 100 * s.std(ddof=0) / s.mean()).reindex(ORDER)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(cv.index, cv.values, color=[COLORS[c] for c in cv.index])
    for i, v in enumerate(cv.values):
        ax.text(i, v + 0.5, f"{v:.1f}%", ha="center", fontsize=11, fontweight="bold")
    ax.set_title("Volatilitas Harga 2026 (Koefisien Variasi)")
    ax.set_ylim(0, cv.max() * 1.22)
    ax.set_ylabel("CV (%)"); style(ax); fig.tight_layout()
    fig.savefig(CHARTS / "03_volatilitas.png"); plt.close(fig)

    # 04 - Rata-rata bulanan 2026
    m = s26.copy()
    m["bulan"] = m["tanggal"].dt.strftime("%Y-%m")
    mb = m.groupby(["bulan", "komoditas"])["harga_rp_per_kg"].mean().unstack()
    fig, ax = plt.subplots(figsize=(12, 5.5))
    x = np.arange(len(mb))
    w = 0.2
    for i, c in enumerate(ORDER):
        ax.bar(x + (i - 1.5) * w, mb[c], width=w, color=COLORS[c], label=c)
    ax.set_xticks(x); ax.set_xticklabels([b[5:] for b in mb.index], rotation=0)
    ax.set_title("Rata-Rata Harga Bulanan 2026 per Komoditas")
    ax.set_ylabel("Rp/kg"); ax.yaxis.set_major_formatter(mticker.FuncFormatter(rp))
    ax.legend(frameon=False, ncol=2); style(ax); fig.tight_layout()
    fig.savefig(CHARTS / "04_rata_rata_bulanan.png"); plt.close(fig)

    # 05 - Lonjakan Sep-Okt 2026 (harian)
    win = piv[(piv.index >= "2026-09-15") & (piv.index <= "2026-10-16")]
    fig, ax = plt.subplots(figsize=(12, 5.5))
    for c in ORDER:
        ax.plot(win.index, win[c], color=COLORS[c], label=c, lw=1.8, marker="o", ms=3)
    ax.set_title("Lonjakan Harga Cabai, 15 Sep - 16 Okt 2026")
    ax.set_ylabel("Rp/kg"); ax.yaxis.set_major_formatter(mticker.FuncFormatter(rp))
    ax.legend(frameon=False, ncol=2); style(ax)
    ax.axhline(105000, color="gray", ls="--", lw=1)
    ax.text(win.index[2], 107000, "Rp105.000/kg", color="gray", fontsize=10)
    fig.tight_layout(); fig.savefig(CHARTS / "05_lonjakan_oktober.png"); plt.close(fig)

    # 06 - 10 provinsi termahal 2026, Cabai Rawit Merah
    p26 = prov[(prov["tanggal"].dt.year == 2026) & (prov["komoditas"] == "Cabai Rawit Merah")]
    pr = p26.groupby("provinsi")["harga_rp_per_kg"].mean().sort_values(ascending=False)
    top10 = pr.head(10).iloc[::-1]
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.barh(top10.index, top10.values, color=COLORS["Cabai Rawit Merah"])
    for i, v in enumerate(top10.values):
        ax.text(v + 1500, i, rp(v), va="center", fontsize=10)
    ax.set_title("10 Provinsi Termahal 2026 - Cabai Rawit Merah (rata-rata)")
    ax.set_xlabel("Rp/kg"); ax.xaxis.set_major_formatter(mticker.FuncFormatter(rp))
    style(ax); fig.tight_layout()
    fig.savefig(CHARTS / "06_provinsi_termahal.png"); plt.close(fig)

    # 07 - Disparitas provinsi 2026 (termahal vs termurah) per komoditas
    p26all = prov[prov["tanggal"].dt.year == 2026]
    g = p26all.groupby(["komoditas", "provinsi"])["harga_rp_per_kg"].mean().unstack(0)
    rows = []
    for c in ORDER:
        s = g[c].dropna()
        rows.append((c, s.max(), s.min(), s.max() - s.min()))
    d = pd.DataFrame(rows, columns=["komoditas", "maks", "min", "selisih"]).set_index("komoditas")
    fig, ax = plt.subplots(figsize=(10, 5.5))
    x = np.arange(len(d))
    ax.bar(x - 0.2, d["maks"], width=0.4, color=RED, label="Provinsi termahal")
    ax.bar(x + 0.2, d["min"], width=0.4, color=MARINE, label="Provinsi termurah")
    ax.set_xticks(x); ax.set_xticklabels(d.index, rotation=15, ha="right")
    ax.set_title("Disparitas Harga Antar Provinsi 2026 (rata-rata provinsi)")
    ax.set_ylabel("Rp/kg"); ax.yaxis.set_major_formatter(mticker.FuncFormatter(rp))
    ax.legend(frameon=False); style(ax); fig.tight_layout()
    fig.savefig(CHARTS / "07_disparitas_provinsi.png"); plt.close(fig)

    # 08 - Rata-rata 2025 vs 2026
    y = nas.groupby(["tahun", "komoditas"])["harga_rp_per_kg"].mean().unstack(0)
    fig, ax = plt.subplots(figsize=(10, 5.5))
    x = np.arange(len(ORDER))
    ax.bar(x - 0.2, [y.loc[c, 2025] for c in ORDER], width=0.4, color=GRAYNEUT, label="2025")
    ax.bar(x + 0.2, [y.loc[c, 2026] for c in ORDER], width=0.4,
           color=[COLORS[c] for c in ORDER], label="2026")
    ax.set_xticks(x); ax.set_xticklabels(ORDER, rotation=15, ha="right")
    ax.set_title("Rata-Rata Harga Nasional: 2025 vs 2026")
    ax.set_ylabel("Rp/kg"); ax.yaxis.set_major_formatter(mticker.FuncFormatter(rp))
    ax.legend(frameon=False); style(ax); fig.tight_layout()
    fig.savefig(CHARTS / "08_banding_2025_2026.png"); plt.close(fig)

    # 09 - MoM Cabai Rawit Merah 2026
    rm = s26[s26["komoditas"] == "Cabai Rawit Merah"].copy()
    rm["bulan"] = rm["tanggal"].dt.strftime("%Y-%m")
    mb2 = rm.groupby("bulan")["harga_rp_per_kg"].mean()
    mom = 100 * mb2.pct_change().dropna()
    fig, ax = plt.subplots(figsize=(10, 5))
    cols = [RED if v >= 0 else MARINE for v in mom.values]
    ax.bar(mom.index, mom.values, color=cols)
    for i, v in enumerate(mom.values):
        ax.text(i, v + (1 if v >= 0 else -2), f"{v:+.1f}%", ha="center", fontsize=10, fontweight="bold")
    ax.axhline(0, color="black", lw=0.8)
    ax.set_title("Perubahan Month-over-Month 2026 - Cabai Rawit Merah")
    ax.set_ylabel("MoM (%)"); style(ax); fig.tight_layout()
    fig.savefig(CHARTS / "09_mom_rawit_merah.png"); plt.close(fig)

    # 10 - Distribusi harga harian 2026 (boxplot)
    fig, ax = plt.subplots(figsize=(10, 5.5))
    data = [s26[s26["komoditas"] == c]["harga_rp_per_kg"].values for c in ORDER]
    bp = ax.boxplot(data, tick_labels=ORDER, patch_artist=True, widths=0.55)
    for patch, c in zip(bp["boxes"], ORDER):
        patch.set_facecolor(COLORS[c]); patch.set_alpha(0.75)
    ax.set_title("Distribusi Harga Harian 2026 per Komoditas")
    ax.set_ylabel("Rp/kg"); ax.yaxis.set_major_formatter(mticker.FuncFormatter(rp))
    style(ax); fig.tight_layout()
    fig.savefig(CHARTS / "10_distribusi_harga.png"); plt.close(fig)

    print("10 charts written to", CHARTS)


if __name__ == "__main__":
    main()
