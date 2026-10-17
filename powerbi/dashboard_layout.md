# Layout Dashboard Power BI — Harga Cabai 2026

Dashboard 4 halaman. Semua visual memakai tabel star schema di folder ini
(`fact_harga_cabai`, `dim_komoditas`, `dim_wilayah`, `dim_tanggal`) dan
measure dari `measures_dax.md`.

## Slicer global (di semua halaman)

| Slicer | Sumber | Catatan |
|---|---|---|
| Komoditas | `dim_komoditas[komoditas]` | 4 cabai, multi-select |
| Provinsi | `dim_wilayah[provinsi]` | 34 provinsi + Nasional |
| Periode | `dim_tanggal[tanggal]` | Range slicer |

## Halaman 1 — Overview

Judul: **Harga Cabai Nasional 2026 — Sekilas**

| Visual | Isi |
|---|---|
| 4 kartu KPI | Harga Rata-Rata, Harga Maksimum, Perubahan MoM %, Volatilitas (CV %) — satu kartu per komoditas via filter halaman, atau 4 kartu terpisah |
| Line chart | Harga harian nasional, 4 komoditas, Jan 2025 – Okt 2026. Sumbu X `dim_tanggal[tanggal]`, legend `dim_komoditas[komoditas]`, values `[Harga Rata-Rata]` |
| Bar chart | Rata-rata 2025 vs 2026 per komoditas (clustered column, legend tahun) |
| Tabel kecil | 5 provinsi termahal + 5 termurah 2026 (Cabai Rawit Merah) |

**Insight yang ditonjolkan:** lonjakan Oktober 2026 dan komoditas paling volatile.

## Halaman 2 — Per Komoditas

Judul: **Per Komoditas — Tren, Volatilitas, Lonjakan**

| Visual | Isi |
|---|---|
| Line chart + MA | Harga harian + `[MA 7 Hari]` (2 seri, satu komoditas terpilih via slicer) |
| Bar chart | Volatilitas (CV %) per komoditas 2026, urut menurun |
| Column chart | Rata-rata bulanan 2026 per komoditas (clustered, legend komoditas) |
| Tabel | Harga puncak 2026: nilai + tanggal, per komoditas |

**Insight yang ditonjolkan:** komoditas mana yang paling liar dan kapan
puncaknya terjadi.

## Halaman 3 — Per Wilayah

Judul: **Per Wilayah — Di Mana Cabai Paling Mahal?**

| Visual | Isi |
|---|---|
| Bar chart horizontal | Rata-rata 2026 per provinsi (satu komoditas terpilih), urut menurun, top 15 |
| Bar chart horizontal | Selisih provinsi termahal vs termurah per komoditas |
| Tabel | Rata-rata 2026 semua provinsi per komoditas + `[Peringkat Provinsi]` + `[Selisih vs Nasional %]` |
| KPI | Rata-rata Pulau Jawa vs Luar Jawa (`dim_wilayah[pulau]`) |

**Insight yang ditonjolkan:** disparitas harga antar provinsi dan posisi
DKI Jakarta terhadap rata-rata nasional.

## Halaman 4 — Volatilitas

Judul: **Volatilitas — Seberapa Liar Harga Cabai?**

| Visual | Isi |
|---|---|
| Bar chart | CV % per komoditas 2026 (nasional) |
| Bar chart | CV % per provinsi, Cabai Rawit Merah, top 10 |
| Line chart | Perubahan day-over-day % (gunakan kolom `perubahan_dod_persen` dari tabel fakta bila tersedia, atau hitung di visual) |
| Tabel | 10 lonjakan harian terbesar 2026 (tanggal, komoditas, % perubahan) |

**Insight yang ditonjolkan:** cabai mana dan provinsi mana yang harganya
paling tidak bisa diprediksi.

## Tips format

- Skema warna: merah cabai (`#C0392B`) untuk Rawit Merah, oranye
  (`#E67E22`) untuk Merah Keriting, hijau (`#27AE60`) untuk Rawit Hijau,
  merah tua (`#922B21`) untuk Merah Besar. Konsisten di semua halaman.
- Sumbu harga: format Rp, 0 desimal, mulai dari 0.
- Judul tiap visual: kalimat insight, bukan nama kolom
  (contoh: "Cabai Rawit Merah paling volatile di 2026", bukan "CV %").
