import argparse
import csv
import os
import platform
import statistics
import time

from hashing import CHUNK_SIZE, METHODS, file_digest, output_bits

DEFAULT_FILES = [f"data/random_{mb}MB.bin" for mb in (1, 10, 50, 100)]
ALL_METHODS = ("read_only",) + METHODS
MIB = 2**20


def read_only(path, chunk_size=CHUNK_SIZE):
    n = 0
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            n += len(chunk)
    return n

def run_once(method, path):
    if method == "read_only":
        return read_only(path)
    return file_digest(path, method)

def measure(method, path, repeats, warmup=1):
    for _ in range(warmup):
        run_once (method, path)
    times = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        run_once(method, path)
        times.append(time.perf_counter() - t0)
    return times

def fmt_time(t):
    return f"{t * 1000:9.3f} ms" if t < 1 else f"{t:9.4f} s"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repeats", type=int, default=10)
    ap.add_argument("--warmup", type=int, default=1)
    ap.add_argument("--methods", nargs="+", default=list(ALL_METHODS))
    ap.add_argument("--files", nargs="+", default=DEFAULT_FILES)
    ap.add_argument("--out", default="results/benchmark.csv")
    args = ap.parse_args()

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    print(f"May: {platform.platform()} | Python {platform.python_version()}")
    print(f"Lap {args.repeats} lan, warm-up {args.warmup} lan, khoi doc {CHUNK_SIZE // 1024} KiB\n")
    with open(args.out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["method", "file", "size_bytes", "run", "seconds",
                    "throughput_mib_s", "output_bits"])
        for path in args.files:
            size = os.path.getsize(path)
            for m in args.methods:
                times = measure(m, path, args.repeats, args.warmup)
                bits = 0 if m == "read_only" else output_bits(m)
                for i, t in enumerate(times, 1):
                    w.writerow([m, os.path.basename(path), size, i, f"{t:.9f}",
                                f"{size / MIB / t:.2f}", bits])
                mean = statistics.mean(times)
                sd = statistics.stdev(times) if len(times) > 1 else 0.0
                cv = sd / mean * 100
                print(f"{os.path.basename(path):<18} {m:<13} {fmt_time(mean)} "
                      f"± {sd * 1000:8.3f} ms (CV {cv:4.1f}%)  "
                      f"{size / MIB / mean:10.1f} MiB/s")
                f.flush()
    print(f"\nDa ghi {args.out}")


if __name__ == "__main__":
    main()