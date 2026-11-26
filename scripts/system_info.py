import hashlib
import json
import os
import platform
import ssl
import subprocess
import zlib


def sh(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=10).stdout.strip()
    except Exception:
        return ""


def macos_info():
    keys = {
        "cpu": "machdep.cpu.brand_string",
        "cores_total": "hw.ncpu",
        "cores_performance": "hw.perflevel0.physicalcpu",
        "cores_efficiency": "hw.perflevel1.physicalcpu",
        "ram_bytes": "hw.memsize",
        # Có lệnh phần cứng hay không (1 = có, 0 = không)
        "hw_crc32": "hw.optional.armv8_crc32",
        "hw_sha256": "hw.optional.arm.FEAT_SHA256",
        "hw_sha512": "hw.optional.arm.FEAT_SHA512",
        "hw_pmull": "hw.optional.arm.FEAT_PMULL",
    }
    info = {k: sh(["sysctl", "-n", v]) for k, v in keys.items()}
    info["macos_version"] = sh(["sw_vers", "-productVersion"])
    return info

def linux_info():
    flags = ""
    model = ""
    try:
        with open("/proc/cpuinfo") as f:
            for line in f:
                if line.startswith("model name") and not model:
                    model = line.split(":", 1)[1].strip()
                if line.startswith(("flags", "Features")) and not flags:
                    flags = line.split(":", 1)[1].split()
    except OSError:
        pass
    return {"cpu": model, "cores_total": os.cpu_count(),
            "hw_crc32": "sse4_2" in flags or "crc32" in flags,
            "hw_sha256": "sha_ni" in flags or "sha2" in flags,
            "hw_pclmul": "pclmulqdq" in flags or "pmull" in flags}


def main():
    info = {
        "platform": platform.platform(),
        "machine": platform.machine(),
        "python": platform.python_version(),
        "python_impl": platform.python_implementation(),
        "zlib_compile_version": zlib.ZLIB_VERSION,
        "zlib_runtime_version": zlib.ZLIB_RUNTIME_VERSION,
        "openssl_version": ssl.OPENSSL_VERSION,
        # Cho biết hashlib dùng OpenSSL ("_hashlib") hay bản cài sẵn của Python
        "md5_backend": type(hashlib.md5()).__module__ or repr(hashlib.md5()),
        "sha256_backend": type(hashlib.sha256()).__module__ or repr(hashlib.sha256()),
        "md5_repr": repr(hashlib.md5()),
        "sha256_repr": repr(hashlib.sha256()),
    }
    info.update(macos_info() if platform.system() == "Darwin" else linux_info())

    os.makedirs("results", exist_ok=True)
    with open("results/system_info.json", "w") as f:
        json.dump(info, f, indent=2, ensure_ascii=False)
    for k, v in info.items():
        print(f"{k:<22} {v}")
    print("\nDa ghi results/system_info.json")


if __name__ == "__main__":
    main()