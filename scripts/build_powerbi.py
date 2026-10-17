#!/usr/bin/env python3
"""Build the Power BI star-schema kit from the raw PIHPS CSVs.

Input : data/raw/harga_cabai_harian.csv, data/raw/harga_cabai_nasional.csv
Output: powerbi/fact_harga_cabai.csv, dim_komoditas.csv, dim_wilayah.csv,
        dim_tanggal.csv

Rules:
- Fact rows only exist where PIHPS published a price (no zero-filling,
  no interpolation). Missing province x commodity combinations simply
  have no rows — PIHPS does not publish a provincial series for them.
- dim_tanggal is a full calendar (every calendar day) so DAX time
  intelligence (DATEADD / SAMEPERIODLASTYEAR) works.
"""
import pandas as pd
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
RAW = HERE / "data" / "raw"
OUT = HERE / "powerbi"
OUT.mkdir(exist_ok=True)

JAWA = {"Banten", "Jawa Barat", "DKI Jakarta", "Jawa Tengah", "DI Yogyakarta", "Jawa Timur"}
KATEGORI = {
    "Cabai Merah Besar": "Cabai Merah",
    "Cabai Merah Keriting": "Cabai Merah",
    "Cabai Rawit Hijau": "Cabai Rawit",
    "Cabai Rawit Merah": "Cabai Rawit",
}


def main():
    prov = pd.read_csv(RAW / "harga_cabai_harian.csv")
    nas = pd.read_csv(RAW / "harga_cabai_nasional.csv")

    # ---- fact: provincial + national rows, only published prices ----
    fact = pd.concat([
        prov[["tanggal", "komoditas_id", "provinsi_id", "harga_rp_per_kg"]],
        nas[["tanggal", "komoditas_id", "provinsi_id", "harga_rp_per_kg"]],
    ]).dropna(subset=["harga_rp_per_kg"])
    fact["harga_rp_per_kg"] = fact["harga_rp_per_kg"].astype(int)
    fact = fact.sort_values(["tanggal", "komoditas_id", "provinsi_id"])
    fact.to_csv(OUT / "fact_harga_cabai.csv", index=False)
    print(f"fact_harga_cabai.csv: {len(fact)} rows")

    # ---- dim_komoditas ----
    dim_k = pd.DataFrame([
        {"komoditas_id": cid, "komoditas": name, "kategori": KATEGORI[name], "satuan": "Rp/kg"}
        for cid, name in [("com_13", "Cabai Merah Besar"), ("com_14", "Cabai Merah Keriting"),
                          ("com_15", "Cabai Rawit Hijau"), ("com_16", "Cabai Rawit Merah")]
    ])
    dim_k.to_csv(OUT / "dim_komoditas.csv", index=False)
    print(f"dim_komoditas.csv: {len(dim_k)} rows")

    # ---- dim_wilayah ----
    provs = prov[["provinsi_id", "provinsi"]].drop_duplicates().sort_values("provinsi_id")
    dim_w = pd.DataFrame([{"provinsi_id": 0, "provinsi": "Nasional", "pulau": "Nasional"}] + [
        {"provinsi_id": int(r.provinsi_id), "provinsi": r.provinsi,
         "pulau": "Pulau Jawa" if r.provinsi in JAWA else "Luar Jawa"}
        for r in provs.itertuples()
    ])
    dim_w.to_csv(OUT / "dim_wilayah.csv", index=False)
    print(f"dim_wilayah.csv: {len(dim_w)} rows")

    # ---- dim_tanggal: full calendar ----
    cal = pd.date_range(prov["tanggal"].min(), prov["tanggal"].max(), freq="D")
    nama_bulan = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli",
                  "Agustus", "September", "Oktober", "November", "Desember"]
    nama_hari = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
    dim_t = pd.DataFrame({
        "tanggal": cal.strftime("%Y-%m-%d"),
        "tahun": cal.year,
        "kuartal": cal.quarter,
        "bulan": cal.month,
        "nama_bulan": [nama_bulan[m - 1] for m in cal.month],
        "minggu_iso": cal.isocalendar().week.astype(int),
        "nama_hari": [nama_hari[d] for d in cal.dayofweek],
        "is_weekend": (cal.dayofweek >= 5).astype(int),
    })
    dim_t.to_csv(OUT / "dim_tanggal.csv", index=False)
    print(f"dim_tanggal.csv: {len(dim_t)} rows ({dim_t['tanggal'].iloc[0]} to {dim_t['tanggal'].iloc[-1]})")


if __name__ == "__main__":
    main()
