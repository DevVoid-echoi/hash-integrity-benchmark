import os

import pandas as pd

MIB = 2**20
ORDER = ["read_only", "crc32_custom", "crc32_zlib", "md5", "sha256"]
SIZES = ["random_1MB.bin", "random_10MB.bin", "random_50MB.bin", "random_100MB.bin"]


def label(f):
    return f.replace("random_", "").replace(".bin", "")

def show(title, df, fmt):
    print(f"\n== {title} ==")
    print(df.to_string(float_format=fmt))

def main():
    df = pd.read_csv("results/benchmark.csv")
    g = df.groupby(["method", "file"])
    s = g["seconds"].agg(n="count", mean_s="mean", std_s="std", median_s="median",
                         min_s="min", max_s="max").reset_index()
    s["size_bytes"] = g["size_bytes"].first().values
    s["cv_pct"] = s["std_s"] / s["mean_s"] * 100
    s["throughput_mib_s"] = s["size_bytes"] / MIB / s["mean_s"]
    s["method"] = pd.Categorical(s["method"], ORDER, ordered=True)
    s["file"] = pd.Categorical(s["file"], SIZES, ordered=True)
    s = s.sort_values(["method", "file"])
    s.to_csv("results/summary.csv", index=False)

    def pivot(col, scale=1.0):
        p = s.pivot(index="method", columns="file", values=col) * scale
        p.columns = [label(c) for c in p.columns]
        return p.dropna(how="all")

    show("Thoi gian trung binh (ms)", pivot("mean_s", 1000), "{:,.3f}".format)
    show("Do lech chuan (ms)", pivot("std_s", 1000), "{:,.4f}".format)
    show("He so bien thien CV (%)", pivot("cv_pct"), "{:.1f}".format)
    show("Thong luong (MiB/s)", pivot("throughput_mib_s"), "{:,.1f}".format)

    t = pivot("mean_s")
    ratios = pd.DataFrame({
        "custom / zlib (lan)": t.loc["crc32_custom"] / t.loc["crc32_zlib"],
        "md5 / sha256 (lan)": t.loc["md5"] / t.loc["sha256"],
    }) if {"crc32_custom", "crc32_zlib", "md5", "sha256"} <= set(t.index) else None
    if ratios is not None:
        show("Ty le thoi gian", ratios.T, "{:,.1f}".format)
    if "read_only" in t.index:
        share = (t.loc["read_only"] / t.drop(index="read_only") * 100)
        show("Thoi gian doc file chiem bao nhieu % tong thoi gian", share, "{:.1f}".format)

    if os.path.exists("results/cold_cache.csv"):
        c = pd.read_csv("results/cold_cache.csv")
        cs = (c.groupby(["method", "file", "state"])["seconds"].mean()
              .unstack("state").reset_index())
        cs["cold_over_warm"] = cs["cold"] / cs["warm"]
        cs.to_csv("results/summary_cold.csv", index=False)
        p = cs.pivot(index="method", columns="file", values="cold_over_warm")
        p = p[[f for f in SIZES if f in p.columns]]
        p.columns = [label(x) for x in p.columns]
        show("Cache lanh / cache am (lan)", p, "{:.2f}".format)
        pc = cs.pivot(index="method", columns="file", values="cold") * 1000
        pc = pc[[f for f in SIZES if f in pc.columns]]
        pc.columns = [label(x) for x in pc.columns]
        show("Thoi gian cache lanh (ms)", pc, "{:,.2f}".format)

    print("\nDa ghi results/summary.csv")

if __name__ == "__main__":
    main()