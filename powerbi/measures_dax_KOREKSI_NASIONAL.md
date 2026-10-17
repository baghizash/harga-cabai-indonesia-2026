# KOREKSI DAX — Pisahkan Seri Nasional dari Provinsi

Baca ini SEBELUM merakit dashboard. File `measures_dax.md` yang asli
punya satu jebakan: tabel fakta berisi BOTH baris Nasional
(`provinsi_id = 0`, 1 baris per tanggal x komoditas) DAN baris 34
provinsi. Kalau sebuah visual dibiarkan tanpa filter provinsi,
measure aslinya menghitung SEMUA baris itu sekaligus, sehingga:

- Harga rata-rata: masih benar (selisih cuma ~Rp5, karena seri
  Nasional pada dasarnya rata-rata provinsi).
- Harga maksimum dan volatilitas: SALAH. Contoh Cabai Rawit Merah 2026:
  measure asli memberi maks Rp175.000 dan CV 34,5%, padahal angka
  README yang benar adalah maks Rp105.300 (12 Okt 2026) dan CV 18,8%.
  Rp175.000 itu harga di satu provinsi pada Maret 2026, bukan harga
  nasional.
- Peringkat provinsi: baris Nasional ikut diperingkatkan sebagai
  seolah-olah provinsi ke-35.

Angka verifikasi di bawah dihitung langsung dari CSV di folder ini
pada 2026-10-17. Dua cara memakai yang benar, pilih salah satu
per visual: (A) pakai measure `Nasional` di bawah ini, ATAU
(B) set slicer Provinsi = Nasional. Jangan andalkan keduanya
kosong (slicer All + measure asli).

## Angka yang harus muncul di visual nasional 2026

| Komoditas | Rata-rata Nasional | Maks Nasional | CV Nasional |
|---|---|---|---|
| Cabai Rawit Merah | Rp74.530 | Rp105.300 (12 Okt 2026) | 18,8% |
| Cabai Merah Keriting | Rp53.277 | Rp88.350 | 20,0% |
| Cabai Merah Besar | Rp51.706 | Rp76.450 | 16,1% |
| Cabai Rawit Hijau | Rp56.578 | Rp79.750 | 12,3% |

Cek per provinsi (pakai filter provinsi, buang Nasional): Rawit Merah
termahal Maluku Utara Rp113.213, termurah Sumatera Utara Rp46.494,
DKI Jakarta Rp78.792. Ketiganya cocok dengan README.

Yang measure asli berikan kalau slicer dibiarkan All (SALAH untuk
tampilan nasional): Rawit Merah maks Rp175.000, CV 34,5%; Keriting
maks Rp156.900, CV 36,0%; Merah Besar maks Rp155.000, CV 35,1%;
Rawit Hijau maks Rp185.000, CV 35,0%. Kalau kamu melihat angka-angka
itu di dashboard, itu bug ini, bukan salah data.

## Measure Nasional (pakai untuk halaman Overview + Per Komoditas)

```dax
Harga Rata-Rata Nasional =
CALCULATE (
    AVERAGE ( fact_harga_cabai[harga_rp_per_kg] ),
    dim_wilayah[provinsi] = "Nasional"
)
```

```dax
Harga Minimum Nasional =
CALCULATE (
    MIN ( fact_harga_cabai[harga_rp_per_kg] ),
    dim_wilayah[provinsi] = "Nasional"
)
```

```dax
Harga Maksimum Nasional =
CALCULATE (
    MAX ( fact_harga_cabai[harga_rp_per_kg] ),
    dim_wilayah[provinsi] = "Nasional"
)
```

```dax
Simpangan Baku Nasional =
CALCULATE (
    STDEV.P ( fact_harga_cabai[harga_rp_per_kg] ),
    dim_wilayah[provinsi] = "Nasional"
)
```

```dax
Volatilitas Nasional (CV %) =
DIVIDE (
    [Simpangan Baku Nasional],
    [Harga Rata-Rata Nasional]
) * 100
```

```dax
MA 7 Hari Nasional =
AVERAGEX (
    DATESINPERIOD (
        dim_tanggal[tanggal],
        MAX ( dim_tanggal[tanggal] ),
        -7,
        DAY
    ),
    [Harga Rata-Rata Nasional]
)
```

```dax
Harga Bulan Lalu Nasional =
CALCULATE (
    [Harga Rata-Rata Nasional],
    DATEADD ( dim_tanggal[tanggal], -1, MONTH )
)
```

```dax
Perubahan MoM Nasional % =
DIVIDE (
    [Harga Rata-Rata Nasional] - [Harga Bulan Lalu Nasional],
    [Harga Bulan Lalu Nasional]
)
```

```dax
Harga Tahun Lalu Nasional =
CALCULATE (
    [Harga Rata-Rata Nasional],
    SAMEPERIODLASTYEAR ( dim_tanggal[tanggal] )
)
```

```dax
Perubahan YoY Nasional % =
DIVIDE (
    [Harga Rata-Rata Nasional] - [Harga Tahun Lalu Nasional],
    [Harga Tahun Lalu Nasional]
)
```

Catatan: `Harga Nasional` versi asli (`CALCULATE([Harga Rata-Rata],
ALL(dim_wilayah[provinsi]))`) jangan dipakai lagi. Gantinya adalah
`[Harga Rata-Rata Nasional]` di atas. Syarat `dim_tanggal` ditandai
sebagai date table tetap berlaku untuk MoM / YoY / MA.

## Measure per provinsi (pakai untuk halaman Per Wilayah + Volatilitas per provinsi)

Measure asli (`Harga Rata-Rata`, `Simpangan Baku`,
`Volatilitas (CV %)`, dan kawan-kawan) SUDAH benar di sini, karena
filter konteksnya satu provinsi. Dua perbaikan:

1. Buang Nasional dari semua visual per provinsi: filter halaman
   `dim_wilayah[provinsi] <> "Nasional"`, atau jangan pilih Nasional
   di slicer provinsi pada halaman ini.
2. Ganti `Peringkat Provinsi` dengan versi ini, supaya Nasional tidak
   ikut diperingkatkan:

```dax
Peringkat Provinsi =
RANKX (
    FILTER (
        ALL ( dim_wilayah[provinsi] ),
        dim_wilayah[provinsi] <> "Nasional"
    ),
    [Harga Rata-Rata],
    ,
    DESC
)
```

Dan ganti `Selisih vs Nasional %` dengan versi ini (pembandingnya
seri Nasional yang benar, bukan rata-rata semua baris):

```dax
Selisih vs Nasional % =
DIVIDE (
    [Harga Rata-Rata] - [Harga Rata-Rata Nasional],
    [Harga Rata-Rata Nasional]
)
```

## Dua catatan kecil lain

1. Nilai kolom `dim_wilayah[pulau]` yang sebenarnya adalah
   `"Pulau Jawa"`, `"Luar Jawa"`, dan `"Nasional"`, bukan `"Jawa"`.
   Untuk KPI Jawa vs Luar Jawa pakai persis string itu:

```dax
Harga Rata-Rata Jawa =
CALCULATE (
    AVERAGE ( fact_harga_cabai[harga_rp_per_kg] ),
    dim_wilayah[pulau] = "Pulau Jawa"
)
```

```dax
Harga Rata-Rata Luar Jawa =
CALCULATE (
    AVERAGE ( fact_harga_cabai[harga_rp_per_kg] ),
    dim_wilayah[pulau] = "Luar Jawa"
)
```

   Ini rata-rata dari provinsi-provinsi di kelompok tersebut, bukan
   seri Nasional.

2. Kolom `perubahan_dod_persen` TIDAK ADA di `fact_harga_cabai.csv`,
   jadi jangan dicari di Power BI. Kalau perlu perubahan day-over-day
   untuk seri Nasional, pakai `DATEADD ( dim_tanggal[tanggal], -1,
   DAY )` pada `[Harga Rata-Rata Nasional]`, dengan catatan PIHPS
   hanya melapor ~207 hari di 2026 (hari kerja pasar), jadi Senin
   dibandingkan ke Jumat sebelumnya, bukan ke hari kalender
   sebelumnya yang kosong.

## Cek akhir sebelum publish

Dengan measure koreksi di atas, tiga angka di Langkah 6
`build_guide.md` harus cocok dengan README: rata-rata nasional 2026
Rawit Merah Rp74.530, puncak Rp105.300 tanggal 12 Okt 2026, provinsi
termahal Maluku Utara. Kalau masih beda, cek filter halaman/slicer
provinsi dulu sebelum mengira datanya salah.
