import argparse
import csv
import os
import platform
import subprocess
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from benchmark import DEFAULT_FILES, MIB, run_once

METHODS = ["read_only", "crc32_zlib", "md5", "sha256"]


def drop_cache():
    if platform.system() == "Darwin":
        subprocess.run(["sudo", "purge"], check=True)
    else:
        subprocess.run(["sync"], check=True)
        subprocess.run(["sudo", "sh", "-c", "echo 3 > /proc/sys/vm/drop_caches"], check=True)
    time.sleep(0.5)

def timed(method, path):
    t0 = time.perf_counter()
    run_once(method, path)
    return time.perf_counter() - t0

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rounds", type=int, default=5)
    ap.add_argument("--files", nargs="+", default=DEFAULT_FILES)
    ap.add_argument("--out", default="results/cold_cache.csv")
    args = ap.parse_args()

    subprocess.run(["sudo", "-v"], check=True)
    os.makedirs("results", exist_ok=True)
    with open(args.out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["method", "file", "size_bytes", "round", "state", "seconds", "throughput_mib_s"])
        for r in range(1, args.rounds + 1):
            for path in args.files:
                size = os.path.getsize(path)
                for m in METHODS:
                    drop_cache()
                    cold = timed(m, path)
                    warm = timed(m, path)
                    for state, t in (("cold", cold), ("warm", warm)):
                        w.writerow([m, os.path.basename(path), size, r, state,
                                    f"{t:.9f}", f"{size / MIB / t:.2f}"])
                    print(f"vong {r} {os.path.basename(path):<18} {m:<11} "
                          f"cold {cold * 1000:9.2f} ms | warm {warm * 1000:9.2f} ms "
                          f"| x{cold / warm:5.1f}")
                    f.flush()
    print(f"\nDa ghi {args.out}")

if __name__ == "__main__":
    main()