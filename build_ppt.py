#!/usr/bin/env python3
"""Build Portofolio-Analisis-Harga-Cabai.pptx (16:9, 10 slides, ID).

Reads findings.json — every number comes from the PIHPS data.
"""
import json
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn

HERE = Path(__file__).resolve().parent
F = json.loads((HERE / "findings.json").read_text())
CHARTS = HERE / "charts"
OUT = Path.home() / "workspace" / "your_files" / "Portofolio-Analisis-Harga-Cabai.pptx"

NAVY = RGBColor(0x1E, 0x3A, 0x8A)
TEAL = RGBColor(0x0D, 0x94, 0x88)
RED = RGBColor(0xC0, 0x39, 0x2B)
DARK = RGBColor(0x1F, 0x29, 0x37)
GRAY = RGBColor(0x6B, 0x72, 0x80)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank = prs.slide_layouts[6]


def rp(v):
    return f"Rp{v:,}".replace(",", ".")


def solid_bg(slide, color):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


def textbox(slide, l, t, w, h):
    tx = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = tx.text_frame
    tf.word_wrap = True
    return tf


def add_par(tf, text, size, color, bold=False, italic=False, first=False, align=None):
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    p.space_after = Pt(8)
    if align is not None:
        p.alignment = align
    r = p.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.italic = italic
    r.font.color.rgb = color
    return p


def add_bullet(tf, text, size=17, first=False):
    p = add_par(tf, text, size, DARK, first=first)
    pPr = p._p.get_or_add_pPr()
    pPr.append(pPr.makeelement(qn("a:buChar"), {"char": "\u2022"}))
    pPr.set("marL", "171450")
    pPr.set("indent", "-171450")
    p.space_after = Pt(10)
    p.space_before = Pt(2)
    return p


def content_title(slide, text):
    tf = textbox(slide, 0.7, 0.3, 11.9, 0.9)
    add_par(tf, text, 30, NAVY, bold=True, first=True)
    bar = slide.shapes.add_shape(1, Inches(0.7), Inches(1.15), Inches(1.5), Inches(0.06))
    bar.fill.solid()
    bar.fill.fore_color.rgb = TEAL
    bar.line.fill.background()


def content_slide(title, bullets, chart=None, caption=None, full_width=False):
    s = prs.slides.add_slide(blank)
    solid_bg(s, WHITE)
    content_title(s, title)
    bw = 11.9 if full_width else 5.6
    tf = textbox(s, 0.7, 1.5, bw, 5.2)
    for i, b in enumerate(bullets):
        add_bullet(tf, b, first=(i == 0))
    if chart:
        s.shapes.add_picture(str(CHARTS / f"{chart}.png"), Inches(6.8), Inches(1.5), width=Inches(5.8))
    if caption:
        tf2 = textbox(s, 0.7, 6.7, 11.9, 0.5)
        add_par(tf2, caption, 11, GRAY, italic=True, first=True)
    return s


vol = F["volatilitas_2026"]
rt = F["rata_tahunan"]
puncak = F["puncak_2026"]
lonj = F["lonjakan_oktober_rawit_merah"]
prov = F["provinsi_2026"]
most_vol = F["komoditas_paling_volatile"]
rm = prov["Cabai Rawit Merah"]

# ---- Slide 1: Title ----
s = prs.slides.add_slide(blank)
solid_bg(s, NAVY)
tf = textbox(s, 0.9, 1.1, 11.5, 1.2)
add_par(tf, "ANALISIS HARGA CABAI INDONESIA 2026", 40, WHITE, bold=True, first=True)
tf = textbox(s, 0.9, 2.5, 11.5, 1.0)
add_par(tf, "Lonjakan Oktober, Volatilitas, dan Disparitas Antar Provinsi", 22, WHITE, first=True)
tf = textbox(s, 0.9, 3.8, 11.5, 2.0)
add_par(tf, "Data harian PIHPS / Bank Indonesia — 4 komoditas cabai, 34 provinsi, "
            "Januari 2025 sampai Oktober 2026", 16, WHITE, first=True)
add_par(tf, "Plus: paket dashboard Power BI (star schema, DAX, panduan rakit)", 16, WHITE)
tf = textbox(s, 0.9, 6.0, 11.5, 0.8)
add_par(tf, "BAGHIZ ASSHIDDIQIE ARASYA", 20, WHITE, bold=True, first=True)

# ---- Slide 2: Latar belakang ----
content_slide("Kenapa Cabai?", [
    "Cabai adalah komoditas pangan paling volatile di Indonesia: harganya bisa "
    "melonjak puluhan persen dalam hitungan hari dan langsung terasa di inflasi.",
    "Analisis ini memakai 4 komoditas PIHPS: Cabai Merah Besar, Cabai Merah Keriting, "
    "Cabai Rawit Hijau, dan Cabai Rawit Merah.",
    "Pertanyaan: bagaimana harga bergerak di 2026, cabai mana yang paling liar, "
    "di provinsi mana harganya paling mahal, dan seberapa besar lonjakan Oktober 2026?",
    "Jawaban dicari dari data harian resmi, bukan dari perkiraan.",
], full_width=True, caption="Sumber data: API publik PIHPS / Bank Indonesia (hargapangan.id), Pasar Tradisional.")

# ---- Slide 3: Data & metode ----
cov = F["coverage"]
content_slide("Data dan Metode", [
    f"Data harian API PIHPS: {cov['tanggal_awal']} sampai {cov['tanggal_akhir']}, "
    f"{cov['baris_nasional']:,} baris nasional + {cov['baris_provinsi_total']:,} baris provinsi "
    f"({cov['baris_provinsi']:,} dengan harga).",
    "Setiap pertanyaan dijawab dengan query SQL (sql/queries.sql) dan divisualisasikan "
    "dalam 10 chart dari data yang sama.",
    "Untuk Power BI, data disusun ulang menjadi star schema: 1 tabel fakta + "
    "3 tabel dimensi, lengkap dengan measure DAX dan panduan merakit dashboard.",
    "Catatan jujur: PIHPS tidak mempublikasikan seri provinsi untuk beberapa kombinasi "
    f"provinsi x komoditas ({len(F['gaps'])} kombinasi) — dicatat sebagai gap, tidak diisi angka lain.",
], full_width=True)

# ---- Slide 4: Tren nasional ----
content_slide("Tren Nasional 2025–2026", [
    f"Rata-rata nasional 2026 tertinggi: Cabai Rawit Merah {rp(rt['Cabai Rawit Merah']['2026'])}/kg, "
    f"naik {rt['Cabai Rawit Merah']['perubahan_persen']}% dibanding 2025.",
    f"Cabai Merah Besar rata-rata {rp(rt['Cabai Merah Besar']['2026'])}/kg "
    f"({rt['Cabai Merah Besar']['perubahan_persen']:+}% vs 2025); Keriting "
    f"{rp(rt['Cabai Merah Keriting']['2026'])}/kg ({rt['Cabai Merah Keriting']['perubahan_persen']:+}%); "
    f"Rawit Hijau {rp(rt['Cabai Rawit Hijau']['2026'])}/kg ({rt['Cabai Rawit Hijau']['perubahan_persen']:+}%).",
    "Keempat komoditas bergerak searah pada lonjakan besar, tapi dengan amplitudo berbeda.",
], chart="01_tren_nasional_4cabai")

# ---- Slide 5: Lonjakan Oktober ----
content_slide("Lonjakan Oktober 2026", [
    (f"Cabai Rawit Merah menembus Rp100.000/kg pada {F['tembus_rawit_merah']['100000']['tanggal']} "
     f"({rp(F['tembus_rawit_merah']['100000']['harga'])}/kg).") if "100000" in F["tembus_rawit_merah"]
    else "Ambang Rp100.000/kg tidak tertembus pada seri nasional dalam periode data.",
    (f"Dan menembus Rp105.000/kg pada {F['tembus_rawit_merah']['105000']['tanggal']} "
     f"({rp(F['tembus_rawit_merah']['105000']['harga'])}/kg).") if "105000" in F["tembus_rawit_merah"]
    else "Ambang Rp105.000/kg tidak tertembus pada seri nasional dalam periode data.",
    f"Dari akhir September ({rp(lonj['akhir_september']['harga'])}/kg) ke puncak Oktober "
    f"({rp(lonj['maks_oktober']['harga'])}/kg pada {lonj['maks_oktober']['tanggal']}), "
    f"naik {lonj['kenaikan_persen']}%.",
    f"Kenaikan terbesar terjadi pada September: rata-rata bulanan naik "
    f"{F['mom_rawit_merah_2026']['2026-09']:+}% dibanding Agustus, lalu Oktober naik lagi "
    f"{F['mom_rawit_merah_2026']['2026-10']:+}%.",
    "Lonjakan ini yang membuat cabai menjadi berita utama pertengahan Oktober 2026.",
], chart="05_lonjakan_oktober")

# ---- Slide 6: Volatilitas ----
content_slide("Volatilitas: Cabai Mana yang Paling Liar?", [
    f"{most_vol} paling volatile di 2026: koefisien variasi {vol[most_vol]['cv_persen']}%, "
    f"rentang {rp(vol[most_vol]['min'])}/kg sampai {rp(vol[most_vol]['maks'])}/kg.",
    f"Yang paling stabil: {F['komoditas_paling_stabil']} (CV {vol[F['komoditas_paling_stabil']]['cv_persen']}%).",
    "Volatilitas tinggi berarti harga sulit diprediksi: pedagang dan konsumen "
    "sama-sama menanggung ketidakpastian.",
    "Lonjakan harian terbesar 2026: "
    + ", ".join(f"{j['komoditas']} {j['perubahan_persen']:+}% pada {j['tanggal']}"
                for j in F["lonjakan_harian_terbesar_2026"][:2]) + ".",
], chart="03_volatilitas")

# ---- Slide 7: Disparitas provinsi ----
content_slide("Disparitas Antar Provinsi", [
    f"2026, Cabai Rawit Merah termahal di {rm['termahal']['provinsi']} "
    f"(rata-rata {rp(rm['termahal']['harga'])}/kg), termurah di {rm['termurah']['provinsi']} "
    f"({rp(rm['termurah']['harga'])}/kg) — selisih {rp(rm['selisih'])}/kg "
    f"({rm['selisih_persen']}%).",
    f"DKI Jakarta {rp(F['jakarta_vs_nasional_2026']['Cabai Rawit Merah']['jakarta'])}/kg, "
    f"{F['jakarta_vs_nasional_2026']['Cabai Rawit Merah']['selisih_persen']:+}% "
    "terhadap rata-rata nasional.",
    "Harga di provinsi timur dan kepulauan cenderung lebih mahal: biaya logistik "
    "dan rantai pasok yang lebih panjang.",
], chart="06_provinsi_termahal")

# ---- Slide 8: Power BI ----
content_slide("Paket Dashboard Power BI", [
    "Star schema siap import: fact_harga_cabai + dim_komoditas + dim_wilayah + dim_tanggal.",
    "15 measure DAX siap tempel: rata-rata, MoM %, YoY %, MA 7 hari, volatilitas (CV %), "
    "peringkat provinsi, selisih vs nasional.",
    "Layout 4 halaman: Overview, Per Komoditas, Per Wilayah, Volatilitas — lengkap "
    "dengan spesifikasi tiap visual.",
    "Panduan rakit langkah demi langkah untuk Power BI Desktop di Windows: import, "
    "relasi, mark date table, tempel DAX, bangun visual, publish.",
], full_width=True)

# ---- Slide 9: Insight & rekomendasi ----
top_jump = F["lonjakan_harian_terbesar_2026"][0]
content_slide("Insight dan Rekomendasi", [
    f"1. Pantau Rawit Merah (paling mahal, rata-rata 2026 {rp(rt['Cabai Rawit Merah']['2026'])}/kg) "
    f"dan Keriting (paling volatile, CV {vol['Cabai Merah Keriting']['cv_persen']}%).",
    f"2. Siapkan skenario lonjakan: lonjakan harian terbesar {top_jump['perubahan_persen']:+}% "
    f"({top_jump['komoditas']}, {top_jump['tanggal']}) menunjukkan harga bisa melonjak dalam sehari.",
    "3. Fokus ke provinsi timur: disparitas harga antar provinsi mencapai puluhan persen — "
    "distribusi dan logistik adalah bagian dari masalah.",
    "4. Gunakan dashboard Power BI untuk pemantauan harian: MA 7 hari dan MoM % memberi "
    "sinyal lebih awal daripada harga harian mentah.",
], full_width=True)

# ---- Slide 10: Penutup ----
content_slide("Penutup", [
    "Semua angka di deck ini dihitung dari data harian API PIHPS / Bank Indonesia — "
    "dapat direproduksi dengan menjalankan scripts/fetch_pihps.py lalu scripts/analyze.py.",
    "Struktur proyek: analysis.ipynb, data/raw, sql/queries.sql, scripts, charts, "
    "powerbi/ (kit dashboard), findings.json.",
    "Keterbatasan: PIHPS melaporkan pada hari kerja pasar (bukan setiap hari kalender); "
    "beberapa kombinasi provinsi x komoditas tidak dipublikasikan dan dicatat sebagai gap.",
    "Terima kasih.",
], full_width=True)

OUT.parent.mkdir(parents=True, exist_ok=True)
prs.save(str(OUT))
print(f"PPT saved: {OUT}")
