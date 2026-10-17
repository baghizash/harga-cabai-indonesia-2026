# Panduan Merakit Dashboard — Power BI Desktop (Windows)

> **Penting:** perakitan dashboard dilakukan di **Power BI Desktop di
> Windows** (Baghiz memakai dual boot, jadi buka Windows untuk langkah
> ini). File di folder ini hanya bahan mentah siap import — bukan file
> `.pbix`. Ikuti langkah di bawah dan dashboard jadi dalam ±30 menit.

## Langkah 0 — Siapkan file

Folder `powerbi/` berisi:

| File | Isi |
|---|---|
| `fact_harga_cabai.csv` | Tabel fakta: satu baris per tanggal x komoditas x provinsi, harga Rp/kg |
| `dim_komoditas.csv` | 4 baris: 4 komoditas cabai |
| `dim_wilayah.csv` | 35 baris: 34 provinsi + Nasional, kolom pulau (Jawa / Luar Jawa) |
| `dim_tanggal.csv` | Kalender harian Jan 2025 – Okt 2026 (tahun, bulan, nama bulan, kuartal, minggu, hari, akhir pekan) |
| `measures_dax.md` | Rumus DAX siap tempel |
| `dashboard_layout.md` | Spesifikasi 4 halaman dashboard |

## Langkah 1 — Import data

1. Buka **Power BI Desktop** > **Get Data** > **Text/CSV**.
2. Import keempat file CSV di atas, satu per satu. Klik **Load**.
3. Di **Model view**, pastikan tipe kolom:
   - `fact_harga_cabai[tanggal]` → Date, `harga_rp_per_kg` → Whole Number
   - `dim_tanggal[tanggal]` → Date; kolom `tahun`, `bulan`, `kuartal` → Whole Number

## Langkah 2 — Relasi (Model view)

Buat 3 relasi, semua **single direction** dari dimensi ke fakta:

| Dari | Ke |
|---|---|
| `dim_tanggal[tanggal]` | `fact_harga_cabai[tanggal]` |
| `dim_komoditas[komoditas_id]` | `fact_harga_cabai[komoditas_id]` |
| `dim_wilayah[provinsi_id]` | `fact_harga_cabai[provinsi_id]` |

Relasi harus **one-to-many** (dimensi = sisi one). Jika Power BI membuat
relasi otomatis yang salah, hapus dan buat manual.

## Langkah 3 — Tandai tabel tanggal

1. Klik tabel `dim_tanggal` di panel Fields.
2. **Table tools** > **Mark as date table** > pilih kolom `tanggal`.
3. Ini wajib agar measure `DATEADD` / `SAMEPERIODLASTYEAR` bekerja.

## Langkah 4 — Buat measure DAX

1. Klik kanan tabel `fact_harga_cabai` > **New measure**.
2. Tempel satu per satu rumus dari `measures_dax.md`:
   `Harga Rata-Rata`, `Harga Minimum`, `Harga Maksimum`,
   `Jumlah Hari Pelaporan`, `Harga Bulan Lalu`, `Perubahan MoM %`,
   `Harga Tahun Lalu`, `Perubahan YoY %`, `MA 7 Hari`,
   `Simpangan Baku`, `Volatilitas (CV %)`, `Rentang Harga`,
   `Harga Nasional`, `Selisih vs Nasional %`, `Peringkat Provinsi`.
3. Atur format tiap measure sesuai tabel di akhir `measures_dax.md`.

## Langkah 5 — Bangun 4 halaman

Ikuti `dashboard_layout.md` halaman per halaman:
**Overview → Per Komoditas → Per Wilayah → Volatilitas**.
Tambahkan slicer global (komoditas, provinsi, periode) di tiap halaman.

## Langkah 6 — Cek hasil

Sebelum publish, verifikasi 3 angka ini di dashboard (harus sama dengan
README proyek):

1. Harga rata-rata nasional 2026 Cabai Rawit Merah.
2. Harga puncak Cabai Rawit Merah 2026 (nilai + tanggal).
3. Provinsi termahal 2026 untuk Cabai Rawit Merah.

Jika ada yang beda, cek dulu: filter halaman, relasi, dan apakah
`tanggal` sudah ditandai sebagai tabel tanggal.

## Langkah 7 — Publish (opsional)

**File** > **Publish** > **Publish to Power BI** > pilih workspace.
Dashboard bisa dibagikan via link Power BI Service.

## Troubleshooting

| Gejala | Penyebab umum |
|---|---|
| MoM / YoY kosong | `dim_tanggal` belum di-mark sebagai date table, atau tanggal fakta di luar rentang kalender |
| Harga rata-rata terlalu kecil | Ada baris harga 0/null ikut terhitung — pastikan kolom harga bertipe Whole Number dan baris kosong tidak ada di fakta |
| Relasi many-to-many | Duplikat kunci di tabel dimensi (cek `dim_tanggal` tidak ada tanggal ganda) |
| MA 7 Hari datar di awal | Normal: 7 hari pertama belum punya jendela penuh |
