import argparse
import csv
import os
import platform
import statistics
import time

from hashing import METHODS, file_digest, output_bits

DEFAULT_FILES = [f"data/random_{mb}MB.bin" for mb in (1, 10, 50, 100)]


def measure(method, path, repeats, warmup=1):
    for _ in range(warmup):
        file_digest(path, method)
    times = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        file_digest(path, method)
        times.append(time.perf_counter() - t0)
    return times


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repeats", type=int, default=10)
    ap.add_argument("--warmup", type=int, default=1)
    ap.add_argument("--methods", nargs="+", default=list(METHODS))
    ap.add_argument("--files", nargs="+", default=DEFAULT_FILES)
    ap.add_argument("--out", default="results/benchmark.csv")
    args = ap.parse_args()

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    print(f"May: {platform.platform()} | Python {platform.python_version()}")
    with open(args.out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["method", "file", "size_bytes", "run", "seconds",
                    "throughput_mb_s", "output_bits"])
        for path in args.files:
            size = os.path.getsize(path)
            for m in args.methods:
                times = measure(m, path, args.repeats, args.warmup)
                for i, t in enumerate(times, 1):
                    w.writerow([m, os.path.basename(path), size, i, f"{t:.6f}",
                                f"{size / 2**20 / t:.2f}", output_bits(m)])
                mean = statistics.mean(times)
                sd = statistics.stdev(times) if len(times) > 1 else 0.0
                print(f"{os.path.basename(path):<18} {m:<13} "
                      f"{mean:.4f}s ± {sd:.4f}  ({size / 2**20 / mean:.1f} MB/s)")
    print(f"Da ghi {args.out}")


if __name__ == "__main__":
    main()