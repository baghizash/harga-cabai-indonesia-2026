#!/usr/bin/env python3
"""Compute every key finding from the PIHPS cabai data into findings.json.

Reads data/raw/*.csv. Nothing is hardcoded: every number in README, PPT,
and module must come from findings.json (or be recomputed from the CSVs).
"""
import json
import pandas as pd
import numpy as np
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
RAW = HERE / "data" / "raw"

ORDER = ["Cabai Merah Besar", "Cabai Merah Keriting", "Cabai Rawit Hijau", "Cabai Rawit Merah"]
JAWA = {"Banten", "Jawa Barat", "DKI Jakarta", "Jawa Tengah", "DI Yogyakarta", "Jawa Timur"}
ALL_PROV = ["Aceh", "Sumatera Utara", "Sumatera Barat", "Riau", "Kepulauan Riau", "Jambi",
            "Bengkulu", "Sumatera Selatan", "Kepulauan Bangka Belitung", "Lampung", "Banten",
            "Jawa Barat", "DKI Jakarta", "Jawa Tengah", "DI Yogyakarta", "Jawa Timur", "Bali",
            "Nusa Tenggara Barat", "Nusa Tenggara Timur", "Kalimantan Barat", "Kalimantan Selatan",
            "Kalimantan Tengah", "Kalimantan Timur", "Kalimantan Utara", "Gorontalo",
            "Sulawesi Selatan", "Sulawesi Tenggara", "Sulawesi Tengah", "Sulawesi Utara",
            "Sulawesi Barat", "Maluku", "Maluku Utara", "Papua", "Papua Barat"]


def rp(v):
    return int(round(v)) if v is not None and not (isinstance(v, float) and np.isnan(v)) else None


def main():
    nas = pd.read_csv(RAW / "harga_cabai_nasional.csv", parse_dates=["tanggal"])
    prov = pd.read_csv(RAW / "harga_cabai_harian.csv", parse_dates=["tanggal"])
    nas_n = nas.dropna(subset=["harga_rp_per_kg"]).copy()
    prov_n = prov.dropna(subset=["harga_rp_per_kg"]).copy()
    nas_n["tahun"] = nas_n["tanggal"].dt.year
    prov_n["tahun"] = prov_n["tanggal"].dt.year
    f = {}

    # ---- coverage ----
    f["coverage"] = {
        "tanggal_awal": str(nas_n["tanggal"].min().date()),
        "tanggal_akhir": str(nas_n["tanggal"].max().date()),
        "hari_pelaporan_nasional": {c: int((nas_n["komoditas"] == c).sum()) for c in ORDER},
        "baris_provinsi": int(len(prov_n)),
        "baris_provinsi_total": int(len(prov)),
        "baris_nasional": int(len(nas_n)),
        "hari_tanpa_harga_nasional": {c: int(nas[nas["komoditas"] == c]["harga_rp_per_kg"].isna().sum()) for c in ORDER},
    }
    # gaps: province x commodity combos with no series at all
    have = set(zip(prov["provinsi"], prov["komoditas"]))
    f["gaps"] = sorted([f"{p} — {c}" for p in ALL_PROV for c in ORDER if (p, c) not in have])

    # ---- yearly averages ----
    y = nas_n.groupby(["tahun", "komoditas"])["harga_rp_per_kg"].mean().unstack(0)
    f["rata_tahunan"] = {c: {"2025": rp(y.loc[c, 2025]), "2026": rp(y.loc[c, 2026]),
                             "perubahan_persen": round(100 * (y.loc[c, 2026] - y.loc[c, 2025]) / y.loc[c, 2025], 1)}
                         for c in ORDER}

    # ---- monthly 2026 ----
    m26 = nas_n[nas_n["tahun"] == 2026].copy()
    m26["bulan"] = m26["tanggal"].dt.strftime("%Y-%m")
    mb = m26.groupby(["bulan", "komoditas"])["harga_rp_per_kg"].mean().unstack()
    f["bulanan_2026"] = {b: {c: rp(mb.loc[b, c]) for c in ORDER} for b in mb.index}

    # ---- volatility 2026 ----
    vol = {}
    for c in ORDER:
        s = m26[m26["komoditas"] == c]["harga_rp_per_kg"]
        vol[c] = {"rata": rp(s.mean()), "std": rp(s.std(ddof=0)),
                  "cv_persen": round(100 * s.std(ddof=0) / s.mean(), 1),
                  "min": int(s.min()), "maks": int(s.max()), "rentang": int(s.max() - s.min())}
    f["volatilitas_2026"] = vol
    f["komoditas_paling_volatile"] = max(vol, key=lambda c: vol[c]["cv_persen"])
    f["komoditas_paling_stabil"] = min(vol, key=lambda c: vol[c]["cv_persen"])

    # ---- peaks 2026 ----
    peaks = {}
    for c in ORDER:
        s = m26[m26["komoditas"] == c].sort_values("harga_rp_per_kg").iloc[-1]
        peaks[c] = {"harga": int(s["harga_rp_per_kg"]), "tanggal": str(s["tanggal"].date())}
    f["puncak_2026"] = peaks

    # ---- threshold crossings, rawit merah 2026 ----
    rm26 = m26[m26["komoditas"] == "Cabai Rawit Merah"].sort_values("tanggal")
    cross = {}
    for ambang in (100000, 105000):
        hit = rm26[rm26["harga_rp_per_kg"] >= ambang]
        if len(hit):
            r = hit.iloc[0]
            cross[str(ambang)] = {"tanggal": str(r["tanggal"].date()), "harga": int(r["harga_rp_per_kg"])}
    f["tembus_rawit_merah"] = cross

    # ---- October spike: rawit merah, last Sep value vs max in Oct ----
    rm = nas_n[nas_n["komoditas"] == "Cabai Rawit Merah"].sort_values("tanggal")
    sep = rm[(rm["tanggal"] >= "2026-09-01") & (rm["tanggal"] < "2026-10-01")]
    okt = rm[(rm["tanggal"] >= "2026-10-01") & (rm["tanggal"] <= "2026-10-16")]
    last_sep = sep.iloc[-1]
    max_okt = okt.sort_values("harga_rp_per_kg").iloc[-1]
    f["lonjakan_oktober_rawit_merah"] = {
        "akhir_september": {"tanggal": str(last_sep["tanggal"].date()), "harga": int(last_sep["harga_rp_per_kg"])},
        "maks_oktober": {"tanggal": str(max_okt["tanggal"].date()), "harga": int(max_okt["harga_rp_per_kg"])},
        "kenaikan_persen": round(100 * (max_okt["harga_rp_per_kg"] - last_sep["harga_rp_per_kg"]) / last_sep["harga_rp_per_kg"], 1),
        "nilai_14_okt": rp(rm[rm["tanggal"] == "2026-10-14"]["harga_rp_per_kg"].iloc[0])
                     if (rm["tanggal"] == "2026-10-14").any() else None,
    }

    # ---- biggest single-day jumps 2026 (all commodities) ----
    jumps = []
    for c in ORDER:
        s = m26[m26["komoditas"] == c].sort_values("tanggal").copy()
        s["prev"] = s["harga_rp_per_kg"].shift(1)
        s["pct"] = 100 * (s["harga_rp_per_kg"] - s["prev"]) / s["prev"]
        top = s.sort_values("pct", ascending=False).head(3)
        for r in top.itertuples():
            jumps.append({"tanggal": str(r.tanggal.date()), "komoditas": c,
                          "dari": int(r.prev), "ke": int(r.harga_rp_per_kg),
                          "perubahan_persen": round(r.pct, 1)})
    f["lonjakan_harian_terbesar_2026"] = sorted(jumps, key=lambda j: -j["perubahan_persen"])[:5]

    # ---- MoM rawit merah 2026 ----
    mb_rm = mb["Cabai Rawit Merah"]
    f["mom_rawit_merah_2026"] = {b: round(100 * mb_rm.pct_change().loc[b], 1)
                                 for b in mb_rm.index[1:]}

    # ---- provincial 2026 ----
    p26 = prov_n[prov_n["tahun"] == 2026]
    g = p26.groupby(["komoditas", "provinsi"])["harga_rp_per_kg"].mean().unstack(0)
    prov_stats = {}
    for c in ORDER:
        s = g[c].dropna().sort_values(ascending=False)
        prov_stats[c] = {
            "termahal": {"provinsi": s.index[0], "harga": rp(s.iloc[0])},
            "termurah": {"provinsi": s.index[-1], "harga": rp(s.iloc[-1])},
            "selisih": rp(s.iloc[0] - s.iloc[-1]),
            "selisih_persen": round(100 * (s.iloc[0] - s.iloc[-1]) / s.iloc[-1], 1),
            "n_provinsi": int(len(s)),
            "top5": [{"provinsi": p, "harga": rp(v)} for p, v in s.head(5).items()],
        }
    f["provinsi_2026"] = prov_stats

    # Jawa vs luar Jawa
    jawa_luar = {}
    for c in ORDER:
        sub = p26[p26["komoditas"] == c]
        j = sub[sub["provinsi"].isin(JAWA)]["harga_rp_per_kg"].mean()
        l = sub[~sub["provinsi"].isin(JAWA)]["harga_rp_per_kg"].mean()
        jawa_luar[c] = {"jawa": rp(j), "luar_jawa": rp(l)}
    f["jawa_vs_luar_2026"] = jawa_luar

    # Jakarta vs nasional 2026
    jkt = {}
    for c in ORDER:
        pj = p26[(p26["komoditas"] == c) & (p26["provinsi"] == "DKI Jakarta")]["harga_rp_per_kg"].mean()
        pn = m26[m26["komoditas"] == c]["harga_rp_per_kg"].mean()
        jkt[c] = {"jakarta": rp(pj), "nasional": rp(pn),
                  "selisih_persen": round(100 * (pj - pn) / pn, 1)}
    f["jakarta_vs_nasional_2026"] = jkt

    # Provincial volatility, rawit merah 2026
    prm = p26[p26["komoditas"] == "Cabai Rawit Merah"]
    cvp = prm.groupby("provinsi")["harga_rp_per_kg"].agg(lambda s: 100 * s.std(ddof=0) / s.mean()).sort_values(ascending=False)
    f["cv_provinsi_rawit_merah_2026"] = [{"provinsi": p, "cv_persen": round(v, 1)} for p, v in cvp.head(10).items()]

    out = HERE / "findings.json"
    out.write_text(json.dumps(f, indent=2, ensure_ascii=False))
    print(f"findings.json written: {out}")
    print(json.dumps(f, indent=2, ensure_ascii=False)[:6000])


if __name__ == "__main__":
    main()
