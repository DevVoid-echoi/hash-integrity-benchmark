POLY = 0xEDB88320
_MASK = 0xFFFFFFFF


def _make_table():
    table = []
    for n in range (256):
        c = n
        for _ in range(8):
            c = (c >> 1) ^ POLY if c&1 else c >> 1
        table.append(c)
    return tuple(table)

TABLE = _make_table()

def crc32_bitwise(data: bytes) -> int:
    crc = _MASK
    for b in data:
        crc ^= b
        for _ in range (8):
            crc = (crc >> 1) ^ POLY if crc & 1 else crc >> 1
    return crc ^_MASK

def crc32(data: bytes, value: int = 0) -> int:
    crc = value ^ _MASK
    t = TABLE
    for b in data:
        crc = t[(crc ^ b) & 0xFF] ^ (crc >> 8)
    return crc ^ _MASK
