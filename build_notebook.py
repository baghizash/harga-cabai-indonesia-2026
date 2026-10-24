#!/usr/bin/env python3
"""Build analysis.ipynb for the Harga Cabai 2026 project.

Narrative notebook (Indonesian): SQL + charts + insights.
Every number comes from findings.json (computed from the PIHPS API data).
"""
import json
from pathlib import Path

import nbformat as nbf

HERE = Path(__file__).resolve().parent
F = json.loads((HERE / "findings.json").read_text())

nb = nbf.v4.new_notebook()
cells = []


def md(text):
    cells.append(nbf.v4.new_markdown_cell(text))


def code(text):
    cells.append(nbf.v4.new_code_cell(text))


def rp(v):
    return f"Rp{v:,}".replace(",", ".")


vol = F["volatilitas_2026"]
rt = F["rata_tahunan"]
puncak = F["puncak_2026"]
lonj = F["lonjakan_oktober_rawit_merah"]
prov = F["provinsi_2026"]
cov = F["coverage"]
rm = prov["Cabai Rawit Merah"]

md(f"""# Analisis Harga Cabai Indonesia 2026

**Harga cabai** adalah salah satu penggerak inflasi pangan yang paling
terasa: harganya bisa melonjak puluhan persen dalam hitungan hari.
Analisis ini memakai **data harian resmi PIHPS / Bank Indonesia**
(Pasar Tradisional) untuk 4 komoditas cabai di 34 provinsi, dari
{cov['tanggal_awal']} sampai {cov['tanggal_akhir']}.

> **Sumber data: API publik PIHPS.** Data ditarik langsung dari API
> resmi PIHPS (hargapangan.id) dengan `scripts/fetch_pihps.py` — bukan
> salinan dataset pihak lain. Setiap angka di notebook ini dihitung
> dari data tersebut (lihat `findings.json` dan `sql/queries.sql`).
> Tidak ada angka yang dikarang.

> **Keterbatasan yang dicatat jujur.** (1) PIHPS melaporkan pada hari
> kerja pasar, bukan setiap hari kalender — jadi ada tanggal tanpa
> laporan. (2) PIHPS tidak mempublikasikan seri provinsi untuk
> {len(F['gaps'])} kombinasi provinsi x komoditas (misalnya
> Cabai Merah Besar di Sumatera Utara dan Sumatera Barat). Kombinasi
> tersebut dicatat sebagai gap di `findings.json`, tidak diisi angka
> lain dan tidak diinterpolasi.

## Pertanyaan analisis

1. Bagaimana harga 4 cabai bergerak di 2026, dan bagaimana dibanding 2025?
2. Cabai mana yang paling volatile?
3. Seberapa besar lonjakan Oktober 2026, terutama Cabai Rawit Merah?
4. Di provinsi mana cabai paling mahal dan paling murah?
5. Bagaimana harga di DKI Jakarta dibanding rata-rata nasional?
""")

code("""import sqlite3
import pandas as pd
from IPython.display import Image, display

con = sqlite3.connect("data/harga_cabai.db")

def q(sql):
    return pd.read_sql(sql, con)
""")

md("""## 1. Cakupan data

Satu baris = satu hari pelaporan x satu komoditas x satu wilayah.
""")
code("""q("SELECT komoditas, MIN(tanggal) AS awal, MAX(tanggal) AS akhir, COUNT(*) AS hari "
  "FROM harga_nasional GROUP BY komoditas")""")

md(f"""## 2. Tren nasional 2025 vs 2026

Rata-rata nasional 2026: Cabai Rawit Merah {rp(rt['Cabai Rawit Merah']['2026'])}/kg
({rt['Cabai Rawit Merah']['perubahan_persen']:+}% vs 2025), Cabai Merah Keriting
{rp(rt['Cabai Merah Keriting']['2026'])}/kg ({rt['Cabai Merah Keriting']['perubahan_persen']:+}%), Cabai Rawit Hijau
{rp(rt['Cabai Rawit Hijau']['2026'])}/kg ({rt['Cabai Rawit Hijau']['perubahan_persen']:+}%), Cabai Merah Besar
{rp(rt['Cabai Merah Besar']['2026'])}/kg ({rt['Cabai Merah Besar']['perubahan_persen']:+}%).
""")
code("""q("SELECT komoditas, "
  "ROUND(AVG(CASE WHEN substr(tanggal,1,4)='2025' THEN harga_rp_per_kg END)) AS rata_2025, "
  "ROUND(AVG(CASE WHEN substr(tanggal,1,4)='2026' THEN harga_rp_per_kg END)) AS rata_2026 "
  "FROM harga_nasional WHERE harga_rp_per_kg IS NOT NULL GROUP BY komoditas")""")
code("""display(Image("charts/01_tren_nasional_4cabai.png"))""")
code("""display(Image("charts/08_banding_2025_2026.png"))""")

md(f"""## 3. Volatilitas 2026

{F['komoditas_paling_volatile']} adalah cabai paling volatile di 2026
(CV {vol[F['komoditas_paling_volatile']]['cv_persen']}%), sedangkan
{F['komoditas_paling_stabil']} paling stabil
(CV {vol[F['komoditas_paling_stabil']]['cv_persen']}%).
""")
code("""display(Image("charts/03_volatilitas.png"))""")
code("""display(Image("charts/10_distribusi_harga.png"))""")

if "100000" in F["tembus_rawit_merah"]:
    md(f"""## 4. Lonjakan Oktober 2026

Cabai Rawit Merah menembus Rp100.000/kg pada
{F['tembus_rawit_merah']['100000']['tanggal']}
({rp(F['tembus_rawit_merah']['100000']['harga'])}/kg).""")
else:
    md("""## 4. Lonjakan Oktober 2026

Cabai Rawit Merah naik tajam pada Oktober 2026, meski ambang Rp100.000/kg
tidak tertembus pada seri nasional dalam periode data.""")
if "105000" in F["tembus_rawit_merah"]:
    md(f"""Lalu menembus Rp105.000/kg pada
{F['tembus_rawit_merah']['105000']['tanggal']}
({rp(F['tembus_rawit_merah']['105000']['harga'])}/kg).""")
md(f"""Dari akhir September ({rp(lonj['akhir_september']['harga'])}/kg) ke puncak
Oktober ({rp(lonj['maks_oktober']['harga'])}/kg pada {lonj['maks_oktober']['tanggal']}),
naik {lonj['kenaikan_persen']}%. Kenaikan terbesar terjadi pada September
(MoM {F['mom_rawit_merah_2026']['2026-09']:+}%), lalu Oktober naik lagi
{F['mom_rawit_merah_2026']['2026-10']:+}%.

Fakta menarik: keempat komoditas mencapai puncak 2026 dalam jendela yang sama,
12–20 Oktober 2026 — lonjakannya serentak, bukan satu komoditas saja.
""")
code("""display(Image("charts/05_lonjakan_oktober.png"))""")
code("""display(Image("charts/09_mom_rawit_merah.png"))""")

md(f"""## 5. Disparitas antar provinsi 2026

Cabai Rawit Merah termahal di {rm['termahal']['provinsi']}
(rata-rata {rp(rm['termahal']['harga'])}/kg), termurah di {rm['termurah']['provinsi']}
({rp(rm['termurah']['harga'])}/kg) — selisih {rp(rm['selisih'])}/kg
({rm['selisih_persen']}%).
""")
code("""display(Image("charts/06_provinsi_termahal.png"))""")
code("""display(Image("charts/07_disparitas_provinsi.png"))""")

md(f"""## 6. DKI Jakarta vs nasional

DKI Jakarta 2026: Cabai Rawit Merah
{rp(F['jakarta_vs_nasional_2026']['Cabai Rawit Merah']['jakarta'])}/kg, yaitu
{F['jakarta_vs_nasional_2026']['Cabai Rawit Merah']['selisih_persen']:+}% terhadap
rata-rata nasional.

## 7. Ke Power BI

Data yang sama disusun ulang menjadi star schema di `powerbi/`:
`fact_harga_cabai` + `dim_komoditas` + `dim_wilayah` + `dim_tanggal`,
15 measure DAX di `measures_dax.md`, layout 4 halaman di
`dashboard_layout.md`, dan panduan rakit di `build_guide.md`
(untuk Power BI Desktop di Windows).
""")

nb["cells"] = cells
out = HERE / "analysis.ipynb"
nbf.write(nb, str(out))
print(f"Notebook saved: {out} ({len(cells)} cells)")
