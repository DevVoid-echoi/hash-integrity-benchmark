import hashlib
import zlib

try:
    from . import crc32 as _crc
except ImportError:
    import crc32 as _crc

CHUNK_SIZE = 1 << 20
METHODS = ("crc32_custom", "crc32_zlib", "md5", "sha256")


def _checksum(update, path, chunk_size):
    value = 0
    with open (path, "rb") as f:
        while chunk := f.read(chunk_size):
            value = update(chunk, value)
    return format(value, "08x")

def _hash(name, path, chunk_size):
    h = hashlib.new(name)
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            h.update(chunk)
    return h.hexdigest()

def file_digest(path, method, chunk_size = CHUNK_SIZE) -> str:
    if method == "crc32_custom":
        return _checksum(_crc.crc32, path, chunk_size)
    if method == "crc32_zlib":
        return _checksum(zlib.crc32, path, chunk_size)
    if method in ("md5", "sha256"):
        return _hash(method, path, chunk_size)
    raise ValueError(f"Phương pháp không hỗ trợ: {method}")

def bytes_digest(data: bytes, method) -> str:
    if method == "crc32_custom":
        return format(_crc.crc32(data), "08x")
    if method == "crc32_zlib":
        return format(zlib.crc32(data), "08x")
    if method in ("md5", "sha256"):
        return hashlib.new(method, data).hexdigest()
    raise ValueError(f"Phương pháp không hỗ trợ: {method}")

def output_bits(method) -> int:
    return {"crc32_custom": 32, "crc32_zlib": 32, "md5": 128, "sha256": 256}[method]