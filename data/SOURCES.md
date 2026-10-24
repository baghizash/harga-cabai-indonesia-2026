# Sumber Data

Semua angka berasal dari **API publik PIHPS / Bank Indonesia (hargapangan.id)**,
diambil pada 17 Oktober 2026 dengan `scripts/fetch_pihps.py`, lalu diperbarui
pada 24 Oktober 2026 dengan fetch inkremental jendela 2026-10-17 s.d.
2026-10-24 (respons inkremental digabung ke file chunk yang sama).

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

- Periode: 2025-01-01 s.d. 2026-10-23 (473 hari pelaporan; 24 Okt 2026 hari
  Sabtu, PIHPS tidak menerbitkan laporan pada hari itu).
- Nasional: 1,892 baris (4 komoditas x 473 hari), tanpa nilai kosong.
- Provinsi: 60,061 baris, 58,874 dengan harga.
- Respons mentah API: `data/raw/pihps_chunks/` (127 file JSON).
- Gap (kombinasi tanpa seri provinsi di API): 9 kombinasi —
  Aceh — Cabai Rawit Merah; Gorontalo — Cabai Merah Besar; Gorontalo — Cabai Rawit Hijau; Kepulauan Bangka Belitung — Cabai Merah Besar; Kepulauan Riau — Cabai Merah Besar; Sulawesi Utara — Cabai Merah Besar; Sumatera Barat — Cabai Merah Besar; Sumatera Barat — Cabai Rawit Merah; Sumatera Utara — Cabai Merah Besar.

## Catatan

Tidak ada angka yang dikarang. Angka kunci diverifikasi ulang dengan query SQL
independen terhadap `data/harga_cabai.db` (lihat `sql/queries.sql`).

Catatan refresh 24 Okt 2026: pada jendela 17–24 Okt, API tidak mengembalikan
baris provinsi untuk Cabai Merah Besar — Maluku dan Cabai Rawit Hijau —
Papua Barat (konsisten pada percobaan berulang; seri provinsi keduanya memang
jarang melapor sepanjang 2026), dan Sumatera Selatan tidak melapor pada
20 Okt 2026 untuk keempat komoditas. Ketiganya dicatat apa adanya, tidak
diisi angka lain.
