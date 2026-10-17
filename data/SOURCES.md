# Sumber Data

Semua angka berasal dari **API publik PIHPS / Bank Indonesia (hargapangan.id)**,
diambil pada 17 Oktober 2026 dengan `scripts/fetch_pihps.py`.

## Endpoint

- Grid data: `GET /hargapangan/WebSite/TabelHarga/GetGridDataKomoditas`
  (parameter: `price_type_id=1` Pasar Tradisional, `comcat_id` komoditas,
  `province_id` provinsi, `showKota=false`, `showPasar=false`,
  `tipe_laporan=1` harian, `start_date`, `end_date`).
- Referensi komoditas: `GET /hargapangan/WebSite/TabelHarga/GetRefCommodityAndCategory`
  (4 komoditas cabai: `com_13` Cabai Merah Besar, `com_14` Cabai Merah Keriting,
  `com_15` Cabai Rawit Hijau, `com_16` Cabai Rawit Merah).
- Referensi provinsi: `GET /hargapangan/WebSite/TabelHarga/GetRefProvince`
  (34 provinsi; PIHPS tidak mencakup provinsi hasil pemekaran Papua terbaru).
- Referensi jenis harga: `GET /hargapangan/WebSite/TabelHarga/GetRefPriceType`
  (dipakai: `id=1` Pasar Tradisional).

## Cakupan dan verifikasi

- Periode: 2025-01-01 s.d. 2026-10-16 (468 hari pelaporan).
- Nasional: 1,872 baris (4 komoditas x 468 hari), tanpa nilai kosong.
- Provinsi: 59,436 baris, 58,253 dengan harga.
- Respons mentah API: `data/raw/pihps_chunks/` (127 file JSON).
- Gap (kombinasi tanpa seri provinsi di API): 9 kombinasi —
  Aceh — Cabai Rawit Merah; Gorontalo — Cabai Merah Besar; Gorontalo — Cabai Rawit Hijau; Kepulauan Bangka Belitung — Cabai Merah Besar; Kepulauan Riau — Cabai Merah Besar; Sulawesi Utara — Cabai Merah Besar; Sumatera Barat — Cabai Merah Besar; Sumatera Barat — Cabai Rawit Merah; Sumatera Utara — Cabai Merah Besar.

## Catatan

Tidak ada angka yang dikarang. Angka kunci diverifikasi ulang dengan query SQL
independen terhadap `data/harga_cabai.db` (lihat `sql/queries.sql`).
