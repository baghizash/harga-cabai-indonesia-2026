# Measure DAX — Harga Cabai 2026

Cara pakai: di Power BI Desktop, klik kanan tabel `fact_harga_cabai` >
**New measure**, lalu tempel (paste) rumus di bawah ini. Semua measure
menggunakan kolom dari `fact_harga_cabai` dan `dim_tanggal`. Pastikan
`dim_tanggal` sudah ditandai sebagai tabel tanggal (Mark as Date Table)
dengan kolom `tanggal` — lihat `build_guide.md`.

> Konvensi: harga dalam Rp/kg. Baris dengan harga kosong (tidak ada
> laporan PIHPS hari itu) tidak masuk ke tabel fakta, jadi AVERAGE
> tidak pernah menghitung hari tanpa laporan sebagai nol.

## 1. Harga dasar

```dax
Harga Rata-Rata =
AVERAGE ( fact_harga_cabai[harga_rp_per_kg] )
```

```dax
Harga Minimum =
MIN ( fact_harga_cabai[harga_rp_per_kg] )
```

```dax
Harga Maksimum =
MAX ( fact_harga_cabai[harga_rp_per_kg] )
```

```dax
Jumlah Hari Pelaporan =
COUNTROWS ( fact_harga_cabai )
```

## 2. Perbandingan waktu (time intelligence)

```dax
Harga Bulan Lalu =
CALCULATE (
    [Harga Rata-Rata],
    DATEADD ( dim_tanggal[tanggal], -1, MONTH )
)
```

```dax
Perubahan MoM % =
DIVIDE (
    [Harga Rata-Rata] - [Harga Bulan Lalu],
    [Harga Bulan Lalu]
)
```

```dax
Harga Tahun Lalu =
CALCULATE (
    [Harga Rata-Rata],
    SAMEPERIODLASTYEAR ( dim_tanggal[tanggal] )
)
```

```dax
Perubahan YoY % =
DIVIDE (
    [Harga Rata-Rata] - [Harga Tahun Lalu],
    [Harga Tahun Lalu]
)
```

## 3. Rata-rata bergerak 7 hari

```dax
MA 7 Hari =
AVERAGEX (
    DATESINPERIOD (
        dim_tanggal[tanggal],
        MAX ( dim_tanggal[tanggal] ),
        -7,
        DAY
    ),
    [Harga Rata-Rata]
)
```

> Catatan: PIHPS hanya melaporkan pada hari kerja pasar (bukan setiap
> hari kalender). Jendela 7 hari kalender ini berisi sekitar 5 hari
> pelaporan. Itulah perilaku yang benar: jangan isi hari kosong dengan
> nol atau interpolasi.

## 4. Volatilitas

```dax
Simpangan Baku =
STDEV.P ( fact_harga_cabai[harga_rp_per_kg] )
```

```dax
Volatilitas (CV %) =
DIVIDE (
    [Simpangan Baku],
    [Harga Rata-Rata]
) * 100
```

```dax
Rentang Harga =
[Harga Maksimum] - [Harga Minimum]
```

## 5. Perbandingan wilayah

```dax
Harga Nasional =
CALCULATE (
    [Harga Rata-Rata],
    ALL ( dim_wilayah[provinsi] )
)
```

```dax
Selisih vs Nasional % =
DIVIDE (
    [Harga Rata-Rata] - [Harga Nasional],
    [Harga Nasional]
)
```

```dax
Peringkat Provinsi =
RANKX (
    ALL ( dim_wilayah[provinsi] ),
    [Harga Rata-Rata],
    ,
    DESC
)
```

## 6. Format tampilan yang disarankan

| Measure | Format |
|---|---|
| Harga Rata-Rata, Min, Maks, MA 7 Hari, Rentang | Currency, Rp, 0 desimal |
| Perubahan MoM %, Perubahan YoY %, Selisih vs Nasional % | Percentage, 1 desimal |
| Volatilitas (CV %) | Percentage atau Decimal, 1 desimal |
| Jumlah Hari Pelaporan, Peringkat Provinsi | Whole number |
