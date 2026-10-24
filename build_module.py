#!/usr/bin/env python3
"""Build Modul-Analisis-Harga-Cabai.pdf (A4 landscape, beginner-friendly ID).

Reads findings.json — every number comes from the PIHPS API data.
"""
import json
from pathlib import Path
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle,
    PageBreak,
)

HERE = Path(__file__).resolve().parent
F = json.loads((HERE / "findings.json").read_text())
OUT = str(Path.home() / "workspace" / "coursera-modules" / "Modul-Analisis-Harga-Cabai.pdf")
CHARTS = HERE / "charts"
W, H = landscape(A4)
NAVY = HexColor("#1E3A8A")
TEAL = HexColor("#0D9488")
DARK = HexColor("#1F2937")
GRAY = HexColor("#6B7280")
LIGHT = HexColor("#EFF6FF")

styles = {
    "cover": ParagraphStyle("cover", fontName="Helvetica-Bold", fontSize=30, leading=36,
                            textColor=NAVY, alignment=TA_LEFT),
    "coversub": ParagraphStyle("coversub", fontName="Helvetica", fontSize=16, leading=22,
                               textColor=DARK, alignment=TA_LEFT),
    "h1": ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=22, leading=27,
                         textColor=NAVY, spaceBefore=6, spaceAfter=8),
    "h2": ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=16, leading=20,
                         textColor=TEAL, spaceBefore=8, spaceAfter=6),
    "body": ParagraphStyle("body", fontName="Helvetica", fontSize=12.5, leading=18,
                           textColor=DARK, spaceAfter=7),
    "bullet": ParagraphStyle("bullet", parent=ParagraphStyle("b", fontName="Helvetica",
                             fontSize=12.5, leading=18, textColor=DARK, spaceAfter=5,
                             leftIndent=16, bulletIndent=6)),
    "code": ParagraphStyle("code", fontName="Courier", fontSize=10.5, leading=15,
                          textColor=DARK, backColor=LIGHT, spaceAfter=8,
                          leftIndent=8, borderPadding=(6, 6, 6)),
    "caption": ParagraphStyle("caption", fontName="Helvetica-Oblique", fontSize=10.5,
                              leading=14, textColor=GRAY, alignment=TA_CENTER,
                              spaceBefore=4, spaceAfter=10),
    "warn": ParagraphStyle("warn", fontName="Helvetica", fontSize=12.5, leading=18,
                           textColor=HexColor("#92400E"), backColor=HexColor("#FEF3C7"),
                           borderPadding=(8, 8, 8), spaceAfter=8),
}
story = []


def P(text, style="body"):
    story.append(Paragraph(text, styles[style]))


def B(text):
    story.append(Paragraph(text, styles["bullet"], bulletText="•"))


def CODE(text):
    story.append(Paragraph(text.replace(" ", "&nbsp;").replace("\n", "<br/>"), styles["code"]))


def CHART(fname, caption, width=21 * cm):
    story.append(Image(str(CHARTS / fname), width=width, height=width * 0.58))
    P(caption, "caption")


def TABLE(data, widths=None):
    t = Table([[Paragraph(str(c), styles["body"]) for c in row] for row in data],
              colWidths=widths)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#FFFFFF")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("GRID", (0, 0), (-1, -1), 0.5, GRAY),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor("#FFFFFF"), LIGHT]),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))


def rp(v):
    return f"Rp{v:,}".replace(",", ".")


vol = F["volatilitas_2026"]
rt = F["rata_tahunan"]
puncak = F["puncak_2026"]
lonj = F["lonjakan_oktober_rawit_merah"]
prov = F["provinsi_2026"]
cov = F["coverage"]
rm = prov["Cabai Rawit Merah"]

# ---------- COVER ----------
story.append(Spacer(1, 3 * cm))
P("MODUL BELAJAR", "cover")
P("Modul Analisis Harga Cabai Indonesia 2026", "cover")
P("Dari API PIHPS sampai Dashboard Power BI: Studi Kasus Nyata untuk Pemula", "coversub")
story.append(Spacer(1, 0.6 * cm))
P("Modul ini mengajak kamu membangun satu project analisis data nyata dari nol: "
  "harga cabai di Indonesia pada 2026. Kamu akan belajar mengambil data dari API "
  "resmi PIHPS / Bank Indonesia, menyimpannya ke SQLite, menjawab pertanyaan "
  "dengan SQL, memvisualisasikan dengan Python, lalu menyusun dashboard Power BI. "
  "Semua angka di modul ini dihitung dari data — tidak ada yang dikarang.", "coversub")
story.append(Spacer(1, 0.5 * cm))
P("Sumber data: API publik PIHPS / Bank Indonesia (hargapangan.id), Pasar Tradisional. "
  "Periode: Januari 2025 sampai Oktober 2026. 4 komoditas cabai, 34 provinsi.", "warn")
story.append(PageBreak())

# ---------- BAB 1 ----------
P("Bab 1 — Kenalan dengan Project Ini", "h1")
P("Kenapa cabai? Karena cabai adalah komoditas pangan yang harganya paling "
  "sulit ditebak. Harganya bisa melonjak puluhan persen dalam hitungan hari, "
  "dan lonjakan itu langsung terasa di belanja harian dan inflasi. Kalau kamu "
  "bisa menganalisis cabai, kamu bisa menganalisis komoditas apa pun.", "body")
P("Pertanyaan yang dijawab project ini:", "h2")
B("Bagaimana harga 4 cabai bergerak di 2026, dan bagaimana dibanding 2025?")
B("Cabai mana yang paling volatile (paling liar harganya)?")
B("Seberapa besar lonjakan Oktober 2026, terutama Cabai Rawit Merah?")
B("Di provinsi mana cabai paling mahal dan paling murah?")
B("Bagaimana cara menyajikan semua ini dalam dashboard Power BI?")
P("Empat komoditas yang dianalisis: Cabai Merah Besar, Cabai Merah Keriting, "
  "Cabai Rawit Hijau, dan Cabai Rawit Merah. Semua harga dalam Rp per kilogram.", "body")
story.append(PageBreak())

# ---------- BAB 2 ----------
P("Bab 2 — Datanya dari Mana? Mengenal API PIHPS", "h1")
P("PIHPS (Pusat Informasi Harga Pangan Strategis) adalah layanan Bank Indonesia "
  "yang mempublikasikan harga pangan strategis setiap hari. Datanya bisa diakses "
  "lewat API publik tanpa login. Project ini mengambil data lewat endpoint:", "body")
CODE("GET https://www.bi.go.id/hargapangan/WebSite/TabelHarga/GetGridDataKomoditas\n"
     "?price_type_id=1 (Pasar Tradisional)\n"
     "&comcat_id=com_13 / com_14 / com_15 / com_16 (4 komoditas cabai)\n"
     "&province_id=<id provinsi> &showKota=false &tipe_laporan=1 (harian)")
P("Satu panggilan mengembalikan satu provinsi x satu komoditas, dengan satu kolom "
  "per tanggal pelaporan. Untuk 4 komoditas x 34 provinsi, script "
  "scripts/fetch_pihps.py melakukan 136 panggilan dan merapikannya menjadi "
  "tabel panjang (satu baris per tanggal x komoditas x provinsi).", "body")
P(f"Cakupan data yang berhasil ditarik: {cov['tanggal_awal']} sampai "
  f"{cov['tanggal_akhir']}, {cov['baris_nasional']:,} baris nasional dan "
  f"{cov['baris_provinsi_total']:,} baris provinsi "
  f"({cov['baris_provinsi']:,} dengan harga).", "body")
P("Dua keterbatasan yang harus kamu pahami (dan dicatat jujur di README):", "h2")
B("PIHPS melaporkan pada hari kerja pasar, bukan setiap hari kalender. Jadi ada "
  "tanggal tanpa laporan — itu normal, bukan data hilang.")
B(f"PIHPS tidak mempublikasikan seri provinsi untuk {len(F['gaps'])} kombinasi "
  "provinsi x komoditas. Kombinasi itu dicatat sebagai gap, tidak diisi angka lain "
  "dan tidak diinterpolasi. Seri nasional lengkap untuk keempat komoditas.")
story.append(PageBreak())

# ---------- BAB 3 ----------
P("Bab 3 — Menjawab Pertanyaan dengan SQL", "h1")
P("Data dimuat ke SQLite dengan scripts/load_to_sqlite.py menjadi dua tabel: "
  "harga_nasional dan harga_provinsi. Lalu setiap pertanyaan dijawab dengan query "
  "SQL (file lengkapnya: sql/queries.sql). Contoh: rata-rata 2025 vs 2026.", "body")
CODE("SELECT komoditas,\n"
     "  ROUND(AVG(CASE WHEN substr(tanggal,1,4)='2025' THEN harga_rp_per_kg END)) AS rata_2025,\n"
     "  ROUND(AVG(CASE WHEN substr(tanggal,1,4)='2026' THEN harga_rp_per_kg END)) AS rata_2026\n"
     "FROM harga_nasional WHERE harga_rp_per_kg IS NOT NULL GROUP BY komoditas;")
TABLE([["Komoditas", "Rata-rata 2025", "Rata-rata 2026", "Perubahan"],
       *[[c, rp(rt[c]["2025"]), rp(rt[c]["2026"]), f"{rt[c]['perubahan_persen']:+}%"]
         for c in ["Cabai Merah Besar", "Cabai Merah Keriting", "Cabai Rawit Hijau", "Cabai Rawit Merah"]]])
P("Perhatikan: query selalu menyaring harga_rp_per_kg IS NOT NULL, supaya hari "
  "tanpa laporan tidak dihitung sebagai harga nol. Ini kesalahan pemula yang "
  "paling sering terjadi.", "body")
story.append(PageBreak())

# ---------- BAB 4 ----------
P("Bab 4 — Tren dan Volatilitas", "h1")
P(f"Grafik tren nasional menunjukkan keempat cabai bergerak searah pada lonjakan "
  "besar, tapi dengan amplitudo berbeda. Cabai Rawit Merah memimpin: rata-rata "
  f"2026 {rp(rt['Cabai Rawit Merah']['2026'])}/kg.", "body")
CHART("01_tren_nasional_4cabai.png", "Gambar 1 — Harga harian nasional, 4 komoditas, Jan 2025 – Okt 2026.")
P("Volatilitas diukur dengan koefisien variasi (CV): simpangan baku dibagi "
  "rata-rata, dikali 100%. Makin besar CV, makin liar harganya.", "body")
TABLE([["Komoditas", "Rata-rata 2026", "CV 2026", "Terendah", "Tertinggi"],
       *[[c, rp(vol[c]["rata"]), f"{vol[c]['cv_persen']}%", rp(vol[c]["min"]), rp(vol[c]["maks"])]
         for c in ["Cabai Merah Besar", "Cabai Merah Keriting", "Cabai Rawit Hijau", "Cabai Rawit Merah"]]])
CHART("03_volatilitas.png", "Gambar 2 — Volatilitas (CV) 2026 per komoditas.")
story.append(PageBreak())

# ---------- BAB 5 ----------
P("Bab 5 — Studi Kasus: Lonjakan Oktober 2026", "h1")
if "100000" in F["tembus_rawit_merah"]:
    P(f"Pada pertengahan Oktober 2026, harga cabai menjadi berita utama. Data PIHPS "
      f"menunjukkan Cabai Rawit Merah menembus Rp100.000/kg pada "
      f"{F['tembus_rawit_merah']['100000']['tanggal']} "
      f"({rp(F['tembus_rawit_merah']['100000']['harga'])}/kg).", "body")
else:
    P("Pada pertengahan Oktober 2026, harga cabai menjadi berita utama. Data PIHPS "
      "menunjukkan Cabai Rawit Merah naik tajam, meski ambang Rp100.000/kg tidak "
      "tertembus pada seri nasional dalam periode data.", "body")
if "105000" in F["tembus_rawit_merah"]:
    P(f"Lalu menembus Rp105.000/kg pada {F['tembus_rawit_merah']['105000']['tanggal']} "
      f"({rp(F['tembus_rawit_merah']['105000']['harga'])}/kg).", "body")
P(f"Dari akhir September ({rp(lonj['akhir_september']['harga'])}/kg) ke puncak Oktober "
  f"({rp(lonj['maks_oktober']['harga'])}/kg pada {lonj['maks_oktober']['tanggal']}), "
  f"harganya naik {lonj['kenaikan_persen']}%. Kenaikan terbesar sebenarnya terjadi "
  f"pada September: rata-rata bulanan naik "
  f"{F['mom_rawit_merah_2026']['2026-09']:+}% dibanding Agustus, lalu Oktober naik lagi "
  f"{F['mom_rawit_merah_2026']['2026-10']:+}%.", "body")
CHART("05_lonjakan_oktober.png", "Gambar 3 — Lonjakan harga harian, 15 Sep – 24 Okt 2026.")
P("Pelajaran untuk analis: jangan hanya melihat harga hari ini. Bandingkan dengan "
  "rata-rata bergerak 7 hari (MA 7) dan perubahan month-over-month (MoM) — "
  "keduanya memberi sinyal lebih awal daripada harga harian mentah.", "body")
CHART("09_mom_rawit_merah.png", "Gambar 4 — Perubahan month-over-month 2026, Cabai Rawit Merah.")
story.append(PageBreak())

# ---------- BAB 6 ----------
P("Bab 6 — Disparitas Antar Provinsi", "h1")
P(f"Harga cabai tidak sama di seluruh Indonesia. Pada 2026, Cabai Rawit Merah "
  f"termahal di {rm['termahal']['provinsi']} (rata-rata {rp(rm['termahal']['harga'])}/kg) "
  f"dan termurah di {rm['termurah']['provinsi']} ({rp(rm['termurah']['harga'])}/kg) — "
  f"selisih {rp(rm['selisih'])}/kg ({rm['selisih_persen']}%).", "body")
CHART("06_provinsi_termahal.png", "Gambar 5 — 10 provinsi termahal 2026, Cabai Rawit Merah.")
P("Pola umumnya: provinsi timur dan kepulauan cenderung lebih mahal karena biaya "
  "logistik dan rantai pasok yang lebih panjang. DKI Jakarta sendiri "
  f"{F['jakarta_vs_nasional_2026']['Cabai Rawit Merah']['selisih_persen']:+}% terhadap "
  "rata-rata nasional untuk Cabai Rawit Merah.", "body")
CHART("07_disparitas_provinsi.png", "Gambar 6 — Provinsi termahal vs termurah 2026 per komoditas.")
story.append(PageBreak())

# ---------- BAB 7 ----------
P("Bab 7 — Membangun Dashboard Power BI", "h1")
P("Analisis Python menjawab pertanyaan, tapi dashboard Power BI membuat hasilnya "
  "bisa dipantau setiap hari. Langkah besarnya ada tiga: susun star schema, "
  "buat measure DAX, lalu rakit visual.", "body")
P("1. Star schema", "h2")
P("Satu tabel fakta di tengah, tabel dimensi di sekelilingnya. Fakta berisi "
  "angka yang diukur (harga), dimensi berisi konteks (komoditas, wilayah, tanggal).", "body")
TABLE([["Tabel", "Isi", "Kunci"],
       ["fact_harga_cabai", "Satu baris per tanggal x komoditas x provinsi + harga", "tanggal, komoditas_id, provinsi_id"],
       ["dim_komoditas", "4 komoditas + kategori (Cabai Merah / Cabai Rawit)", "komoditas_id"],
       ["dim_wilayah", "34 provinsi + Nasional + kolom pulau", "provinsi_id"],
       ["dim_tanggal", "Kalender harian lengkap (tahun, bulan, kuartal, hari)", "tanggal"]])
P("Kenapa kalender harus lengkap, padahal PIHPS tidak lapor tiap hari? Karena "
  "fungsi waktu DAX (DATEADD, SAMEPERIODLASTYEAR) butuh kalender tanpa lubang. "
  "Hari tanpa laporan tidak masuk tabel fakta — tidak pernah diisi nol.", "body")
P("2. Measure DAX (contoh)", "h2")
CODE("Harga Rata-Rata = AVERAGE ( fact_harga_cabai[harga_rp_per_kg] )\n\n"
     "Perubahan MoM % =\n"
     "DIVIDE ( [Harga Rata-Rata] - [Harga Bulan Lalu], [Harga Bulan Lalu] )\n\n"
     "MA 7 Hari = AVERAGEX (\n"
     "  DATESINPERIOD ( dim_tanggal[tanggal], MAX ( dim_tanggal[tanggal] ), -7, DAY ),\n"
     "  [Harga Rata-Rata] )")
P("Daftar lengkap 15 measure ada di powerbi/measures_dax.md — tinggal tempel.", "body")
P("3. Rakit di Power BI Desktop (Windows)", "h2")
B("Import 4 file CSV dari folder powerbi/.")
B("Buat 3 relasi: dim_tanggal → fakta, dim_komoditas → fakta, dim_wilayah → fakta.")
B("Tandai dim_tanggal sebagai tabel tanggal (Mark as Date Table).")
B("Tempel 15 measure DAX, lalu bangun 4 halaman sesuai powerbi/dashboard_layout.md: "
  "Overview, Per Komoditas, Per Wilayah, Volatilitas.")
B("Verifikasi 3 angka di dashboard dengan README sebelum publish.")
P("Panduan langkah demi langkah lengkap: powerbi/build_guide.md.", "body")
story.append(PageBreak())

# ---------- BAB 8 ----------
P("Bab 8 — Interpretasi, Rekomendasi, dan Penutup", "h1")
P("Tiga pesan utama dari data:", "h2")
B(f"1. Rawit Merah adalah komoditas yang paling perlu dipantau karena paling mahal "
  f"(rata-rata 2026 {rp(rt['Cabai Rawit Merah']['2026'])}/kg). Untuk volatilitas, "
  f"Keriting juaranya: CV {vol['Cabai Merah Keriting']['cv_persen']}% dibanding "
  f"Rawit Merah {vol['Cabai Rawit Merah']['cv_persen']}%.")
top_jump = F["lonjakan_harian_terbesar_2026"][0]
B(f"2. Lonjakan bisa terjadi dalam sehari: lonjakan harian terbesar 2026 adalah "
  f"{top_jump['perubahan_persen']:+}% ({top_jump['komoditas']}, {top_jump['tanggal']}). "
  "Pemantauan harian dengan MA 7 hari memberi sinyal lebih awal.")
B(f"3. Disparitas wilayah itu nyata: selisih provinsi termahal vs termurah untuk "
  f"Cabai Rawit Merah mencapai {rm['selisih_persen']}%. Distribusi dan logistik "
  "adalah bagian dari masalah, bukan hanya produksi.")
P("Cara mereproduksi project ini:", "h2")
CODE("python scripts/fetch_pihps.py        # tarik data dari API PIHPS\n"
     "python scripts/load_to_sqlite.py    # muat ke SQLite\n"
     "python scripts/analyze.py          # hitung findings.json\n"
     "python scripts/make_charts.py      # buat 10 chart\n"
     "python scripts/build_powerbi.py    # bangun kit Power BI\n"
     "python build_notebook.py build_ppt.py build_module.py")
P("Keterbatasan: PIHPS melaporkan pada hari kerja pasar; beberapa kombinasi "
  "provinsi x komoditas tidak dipublikasikan (dicatat sebagai gap); analisis ini "
  "tidak mengklaim penyebab lonjakan (misalnya cuaca atau pasokan) karena data "
  "harga saja tidak cukup membuktikannya. Terima kasih sudah belajar sampai habis!", "body")

doc = SimpleDocTemplate(OUT, pagesize=landscape(A4),
                        leftMargin=2 * cm, rightMargin=2 * cm,
                        topMargin=1.8 * cm, bottomMargin=1.8 * cm)
doc.build(story)
print(f"Module saved: {OUT}")
