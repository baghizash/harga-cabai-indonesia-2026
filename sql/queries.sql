-- =====================================================================
-- Analisis Harga Cabai Indonesia 2026 — Query SQL
-- Data: API publik PIHPS / Bank Indonesia (hargapangan.id), Pasar Tradisional.
-- 4 komoditas: Cabai Merah Besar, Cabai Merah Keriting, Cabai Rawit Hijau,
-- Cabai Rawit Merah. 34 provinsi + seri nasional. Periode Jan 2025–Okt 2026.
-- Harga dalam Rp/kg. Nilai NULL = tidak ada laporan PIHPS pada hari itu.
-- Semua angka dihitung dari tabel; tidak ada angka yang dikarang.
-- =====================================================================

-- ---------------------------------------------------------------------
-- BAGIAN A — SERI NASIONAL (tabel harga_nasional)
-- ---------------------------------------------------------------------

-- A1. Cakupan data per komoditas: tanggal awal/akhir, jumlah hari pelaporan
SELECT komoditas, MIN(tanggal) AS tanggal_awal, MAX(tanggal) AS tanggal_akhir,
       COUNT(*) AS hari_pelaporan,
       SUM(CASE WHEN harga_rp_per_kg IS NULL THEN 1 ELSE 0 END) AS hari_tanpa_harga
FROM harga_nasional
GROUP BY komoditas;

-- A2. Rata-rata bulanan 2026 per komoditas
SELECT substr(tanggal, 1, 7) AS bulan, komoditas,
       ROUND(AVG(harga_rp_per_kg)) AS rata_rata_harga
FROM harga_nasional
WHERE substr(tanggal, 1, 4) = '2026' AND harga_rp_per_kg IS NOT NULL
GROUP BY bulan, komoditas
ORDER BY bulan, komoditas;

-- A3. Rata-rata tahunan 2025 vs 2026 per komoditas + perubahan persen
SELECT komoditas,
       ROUND(AVG(CASE WHEN substr(tanggal, 1, 4) = '2025' THEN harga_rp_per_kg END)) AS rata_2025,
       ROUND(AVG(CASE WHEN substr(tanggal, 1, 4) = '2026' THEN harga_rp_per_kg END)) AS rata_2026,
       ROUND(100.0 * (AVG(CASE WHEN substr(tanggal, 1, 4) = '2026' THEN harga_rp_per_kg END)
                    - AVG(CASE WHEN substr(tanggal, 1, 4) = '2025' THEN harga_rp_per_kg END))
                    / AVG(CASE WHEN substr(tanggal, 1, 4) = '2025' THEN harga_rp_per_kg END), 1) AS perubahan_persen
FROM harga_nasional
WHERE harga_rp_per_kg IS NOT NULL
GROUP BY komoditas;

-- A4. Volatilitas 2026 per komoditas: rata-rata, simpangan baku, CV, min, maks, rentang
SELECT komoditas,
       ROUND(AVG(harga_rp_per_kg)) AS rata_rata,
       ROUND(SQRT(AVG(harga_rp_per_kg * harga_rp_per_kg) - AVG(harga_rp_per_kg) * AVG(harga_rp_per_kg))) AS simpangan_baku,
       ROUND(100.0 * SQRT(AVG(harga_rp_per_kg * harga_rp_per_kg) - AVG(harga_rp_per_kg) * AVG(harga_rp_per_kg)) / AVG(harga_rp_per_kg), 1) AS koefisien_variasi_persen,
       MIN(harga_rp_per_kg) AS harga_min,
       MAX(harga_rp_per_kg) AS harga_maks,
       MAX(harga_rp_per_kg) - MIN(harga_rp_per_kg) AS rentang
FROM harga_nasional
WHERE substr(tanggal, 1, 4) = '2026' AND harga_rp_per_kg IS NOT NULL
GROUP BY komoditas
ORDER BY koefisien_variasi_persen DESC;

-- A5. Lonjakan Oktober 2026: harga harian 15 Sep–16 Okt 2026, seri nasional
SELECT tanggal, komoditas, harga_rp_per_kg
FROM harga_nasional
WHERE tanggal BETWEEN '2026-09-15' AND '2026-10-16'
ORDER BY tanggal, komoditas;

-- A6. Tanggal pertama Cabai Rawit Merah menembus Rp100.000 dan Rp105.000 (2026)
SELECT '100000' AS ambang, MIN(tanggal) AS tanggal_pertama
FROM harga_nasional
WHERE komoditas = 'Cabai Rawit Merah' AND substr(tanggal, 1, 4) = '2026'
  AND harga_rp_per_kg >= 100000
UNION ALL
SELECT '105000', MIN(tanggal)
FROM harga_nasional
WHERE komoditas = 'Cabai Rawit Merah' AND substr(tanggal, 1, 4) = '2026'
  AND harga_rp_per_kg >= 105000;

-- A7. Harga puncak 2026 per komoditas (nilai + tanggal)
SELECT komoditas, harga_rp_per_kg AS harga_puncak, tanggal
FROM harga_nasional
WHERE substr(tanggal, 1, 4) = '2026' AND harga_rp_per_kg IS NOT NULL
  AND (komoditas, harga_rp_per_kg) IN (
      SELECT komoditas, MAX(harga_rp_per_kg) FROM harga_nasional
      WHERE substr(tanggal, 1, 4) = '2026' GROUP BY komoditas);

-- A8. Lonjakan harian terbesar 2026 (perubahan day-over-day, %)
WITH harian AS (
    SELECT tanggal, komoditas, harga_rp_per_kg,
           LAG(harga_rp_per_kg) OVER (PARTITION BY komoditas ORDER BY tanggal) AS harga_sebelumnya
    FROM harga_nasional
    WHERE substr(tanggal, 1, 4) = '2026' AND harga_rp_per_kg IS NOT NULL
)
SELECT tanggal, komoditas, harga_sebelumnya, harga_rp_per_kg,
       ROUND(100.0 * (harga_rp_per_kg - harga_sebelumnya) / harga_sebelumnya, 1) AS perubahan_persen
FROM harian
WHERE harga_sebelumnya IS NOT NULL
ORDER BY perubahan_persen DESC
LIMIT 10;

-- A9. Perubahan month-over-month Cabai Rawit Merah 2026 (rata-rata bulanan)
WITH bulanan AS (
    SELECT substr(tanggal, 1, 7) AS bulan, AVG(harga_rp_per_kg) AS rata_rata
    FROM harga_nasional
    WHERE komoditas = 'Cabai Rawit Merah' AND substr(tanggal, 1, 4) = '2026'
      AND harga_rp_per_kg IS NOT NULL
    GROUP BY bulan
)
SELECT bulan, ROUND(rata_rata) AS rata_rata,
       ROUND(100.0 * (rata_rata - LAG(rata_rata) OVER (ORDER BY bulan)) / LAG(rata_rata) OVER (ORDER BY bulan), 1) AS mom_persen
FROM bulanan
ORDER BY bulan;

-- A10. Rata-rata bergerak 7 hari pelaporan, Cabai Rawit Merah, Sep–Okt 2026
SELECT tanggal, harga_rp_per_kg,
       ROUND(AVG(harga_rp_per_kg) OVER (ORDER BY tanggal ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)) AS ma7
FROM harga_nasional
WHERE komoditas = 'Cabai Rawit Merah' AND tanggal BETWEEN '2026-09-01' AND '2026-10-16'
  AND harga_rp_per_kg IS NOT NULL
ORDER BY tanggal;

-- ---------------------------------------------------------------------
-- BAGIAN B — PER PROVINSI (tabel harga_provinsi)
-- ---------------------------------------------------------------------

-- B1. Rata-rata 2026 per provinsi per komoditas (dasar peringkat provinsi)
SELECT provinsi, komoditas, ROUND(AVG(harga_rp_per_kg)) AS rata_2026,
       COUNT(*) AS hari_pelaporan
FROM harga_provinsi
WHERE substr(tanggal, 1, 4) = '2026' AND harga_rp_per_kg IS NOT NULL
GROUP BY provinsi, komoditas
ORDER BY komoditas, rata_2026 DESC;

-- B2. Provinsi termahal dan termurah 2026 per komoditas
WITH rata AS (
    SELECT provinsi, komoditas, AVG(harga_rp_per_kg) AS rata_2026
    FROM harga_provinsi
    WHERE substr(tanggal, 1, 4) = '2026' AND harga_rp_per_kg IS NOT NULL
    GROUP BY provinsi, komoditas
), ranked AS (
    SELECT provinsi, komoditas, ROUND(rata_2026) AS rata_2026,
           ROW_NUMBER() OVER (PARTITION BY komoditas ORDER BY rata_2026 DESC) AS rn_mahal,
           ROW_NUMBER() OVER (PARTITION BY komoditas ORDER BY rata_2026 ASC) AS rn_murah
    FROM rata
)
SELECT komoditas, 'termahal' AS kategori, provinsi, rata_2026 FROM ranked WHERE rn_mahal = 1
UNION ALL
SELECT komoditas, 'termurah', provinsi, rata_2026 FROM ranked WHERE rn_murah = 1
ORDER BY komoditas, kategori;

-- B3. Selisih provinsi termahal vs termurah 2026 per komoditas (disparitas wilayah)
WITH rata AS (
    SELECT komoditas, AVG(harga_rp_per_kg) AS rata_2026
    FROM harga_provinsi
    WHERE substr(tanggal, 1, 4) = '2026' AND harga_rp_per_kg IS NOT NULL
    GROUP BY provinsi, komoditas
)
SELECT komoditas, ROUND(MAX(rata_2026)) AS provinsi_termahal,
       ROUND(MIN(rata_2026)) AS provinsi_termurah,
       ROUND(MAX(rata_2026) - MIN(rata_2026)) AS selisih,
       ROUND(100.0 * (MAX(rata_2026) - MIN(rata_2026)) / MIN(rata_2026), 1) AS selisih_persen
FROM rata
GROUP BY komoditas;

-- B4. Pulau Jawa vs luar Jawa, rata-rata 2026 per komoditas
-- Jawa = Banten, Jawa Barat, DKI Jakarta, Jawa Tengah, DI Yogyakarta, Jawa Timur
SELECT komoditas,
       CASE WHEN provinsi IN ('Banten', 'Jawa Barat', 'DKI Jakarta', 'Jawa Tengah', 'DI Yogyakarta', 'Jawa Timur')
            THEN 'Pulau Jawa' ELSE 'Luar Jawa' END AS wilayah,
       ROUND(AVG(harga_rp_per_kg)) AS rata_2026
FROM harga_provinsi
WHERE substr(tanggal, 1, 4) = '2026' AND harga_rp_per_kg IS NOT NULL
GROUP BY komoditas, wilayah
ORDER BY komoditas, wilayah;

-- B5. Volatilitas per provinsi 2026, Cabai Rawit Merah (10 provinsi paling volatile)
SELECT provinsi,
       ROUND(AVG(harga_rp_per_kg)) AS rata_2026,
       ROUND(100.0 * SQRT(AVG(harga_rp_per_kg * harga_rp_per_kg) - AVG(harga_rp_per_kg) * AVG(harga_rp_per_kg)) / AVG(harga_rp_per_kg), 1) AS cv_persen
FROM harga_provinsi
WHERE komoditas = 'Cabai Rawit Merah' AND substr(tanggal, 1, 4) = '2026'
  AND harga_rp_per_kg IS NOT NULL
GROUP BY provinsi
ORDER BY cv_persen DESC
LIMIT 10;

-- B6. DKI Jakarta vs rata-rata nasional, 2026 per komoditas
SELECT p.komoditas,
       ROUND(AVG(p.harga_rp_per_kg)) AS rata_jakarta_2026,
       ROUND(AVG(n.harga_rp_per_kg)) AS rata_nasional_2026,
       ROUND(100.0 * (AVG(p.harga_rp_per_kg) - AVG(n.harga_rp_per_kg)) / AVG(n.harga_rp_per_kg), 1) AS jakarta_vs_nasional_persen
FROM harga_provinsi p
JOIN harga_nasional n ON n.tanggal = p.tanggal AND n.komoditas = p.komoditas
WHERE p.provinsi = 'DKI Jakarta' AND substr(p.tanggal, 1, 4) = '2026'
  AND p.harga_rp_per_kg IS NOT NULL AND n.harga_rp_per_kg IS NOT NULL
GROUP BY p.komoditas;
