#!/usr/bin/env python3
"""Load PIHPS cabai CSVs into data/harga_cabai.db (SQLite).

The dataset is fetched from the official PIHPS / Bank Indonesia public API
(see scripts/fetch_pihps.py). This script only loads the CSVs and verifies
row counts - it invents nothing.
"""
import csv
import os
import sqlite3

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(HERE, "data", "raw")
DB = os.path.join(HERE, "data", "harga_cabai.db")

TABLES = {
    "harga_provinsi": "harga_cabai_harian.csv",
    "harga_nasional": "harga_cabai_nasional.csv",
}


def main():
    if os.path.exists(DB):
        os.remove(DB)
    con = sqlite3.connect(DB)
    cur = con.cursor()
    for table, fname in TABLES.items():
        path = os.path.join(RAW, fname)
        with open(path, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        cur.execute(
            f"""CREATE TABLE {table} (
                tanggal TEXT,
                komoditas_id TEXT,
                komoditas TEXT,
                provinsi_id INTEGER,
                provinsi TEXT,
                level INTEGER,
                harga_rp_per_kg INTEGER
            )"""
        )
        cur.executemany(
            f"INSERT INTO {table} VALUES (?, ?, ?, ?, ?, ?, ?)",
            [[r["tanggal"], r["komoditas_id"], r["komoditas"],
              int(r["provinsi_id"]), r["provinsi"], int(r["level"]),
              int(r["harga_rp_per_kg"]) if r["harga_rp_per_kg"] else None]
             for r in rows],
        )
        print(f"{table}: {len(rows)} rows")
    con.commit()
    # Verification: distinct dates / commodities / provinces actually loaded
    n_dates = cur.execute("SELECT COUNT(DISTINCT tanggal) FROM harga_provinsi").fetchone()[0]
    n_com = cur.execute("SELECT COUNT(DISTINCT komoditas) FROM harga_provinsi").fetchone()[0]
    n_prov = cur.execute("SELECT COUNT(DISTINCT provinsi) FROM harga_provinsi").fetchone()[0]
    print(f"distinct dates: {n_dates}, commodities: {n_com}, provinces: {n_prov}")
    assert n_com == 4, "must have exactly 4 cabai commodities"
    assert n_prov == 34, "must have all 34 PIHPS provinces"
    con.close()
    print(f"Database written: {DB}")


if __name__ == "__main__":
    main()
