import csv
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from hashing import file_digest

FILES = [f"data/random_{mb}MB.bin" for mb in (1, 10, 50, 100)]
OUT = "results/week2_digests.csv"


def main():
    os.makedirs("results", exist_ok=True)
    rows = []
    all_ok = True
    for path in FILES:
        if not os.path.exists(path):
            sys.exit(f"Thiếu {path}. Hãy chạy: python scripts/gen_files.py")
        d = {m: file_digest(path, m) for m in ("crc32_custom", "crc32_zlib", "md5", "sha256")}
        ok = d["crc32_custom"] == d["crc32_zlib"]
        all_ok &= ok
        rows.append({"file": os.path.basename(path), "size_bytes": os.path.getsize(path),
                     **d, "crc_match": ok})
        print(f"{os.path.basename(path):<18} crc_custom={d['crc32_custom']} "
              f"crc_zlib={d['crc32_zlib']} {'KHOP' if ok else 'LECH'}")
        print(f"{'':<18} md5={d['md5']}")
        print(f"{'':<18} sha256={d['sha256']}")

    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    print(f"\nDa ghi {OUT}. CRC32 tu cai khop zlib tren ca 4 file: {all_ok}")


if __name__ == "__main__":
    main()