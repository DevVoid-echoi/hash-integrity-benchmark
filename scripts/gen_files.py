import os, random, hashlib
 
SIZES_MB = [1, 10, 50, 100]
SEED = 2026
os.makedirs("data", exist_ok=True)
 
for mb in SIZES_MB:
    rng = random.Random(SEED + mb)      # seed cố định -> tái lập được
    data = rng.randbytes(mb * 1024 * 1024)
    path = f"data/random_{mb}MB.bin"
    with open(path, "wb") as f:
        f.write(data)
    print(f"{path:<24} {len(data):>11,} B  "
          f"sha256={hashlib.sha256(data).hexdigest()[:16]}...")
