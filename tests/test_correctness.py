import hashlib
import random
import zlib

import pytest

from crc32 import TABLE, crc32, crc32_bitwise
from hashing import METHODS, bytes_digest, file_digest, output_bits

CRC32_VECTORS = [
    (b"", 0x00000000),
    (b"123456789", 0xCBF43926),
    (b"The quick brown fox jumps over the lazy dog", 0x414FA339),
]
MD5_VECTORS = [  # RFC 1321, phụ lục A.5
    (b"", "d41d8cd98f00b204e9800998ecf8427e"),
    (b"a", "0cc175b9c0f1b6a831c399e269772661"),
    (b"abc", "900150983cd24fb0d6963f7d28e17f72"),
    (b"message digest", "f96b697d7cb7938d525a2f31aaf161d0"),
]
SHA256_VECTORS = [  # FIPS 180-4 / NIST
    (b"", "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
    (b"abc", "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"),
    (b"abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq",
     "248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1"),
]
EMPTY_DIGESTS = {
    "crc32_custom": "00000000",
    "crc32_zlib": "00000000",
    "md5": MD5_VECTORS[0][1],
    "sha256": SHA256_VECTORS[0][1],
}


# ---------------- CRC32 ----------------

def test_table():
    assert len(TABLE) == 256
    assert TABLE[0] == 0x00000000
    assert TABLE[1] == 0x77073096
    assert TABLE[255] == 0x2D02EF8D

@pytest.mark.parametrize("func", [crc32, crc32_bitwise], ids=["table", "bitwise"])
@pytest.mark.parametrize("data, expected", CRC32_VECTORS, ids=["empty", "123456789", "The quick brown fox jumps over the lazy dog"])
def test_crc32_vectors(func, data, expected):
    assert func(data) == expected

@pytest.mark.parametrize("n", [0, 1, 2, 3, 255, 256, 1000, 4096, 65537])
def test_crc32_vs_zlib(n):
    data = random.Random(n).randbytes(n)
    assert crc32(data) == zlib.crc32(data)

@pytest.mark.parametrize("cut", [0, 1, 4999, 9999, 10_000])
def test_crc32_incremental(cut):
    data = random.Random(2).randbytes(10_000)
    assert crc32(data[cut:], crc32(data[:cut])) == crc32(data)


# ---------------- MD5 / SHA-256 ----------------

@pytest.mark.parametrize("data, expected", MD5_VECTORS)
def test_md5_vectors(data, expected):
    assert bytes_digest(data, "md5") == expected

@pytest.mark.parametrize("data, expected", SHA256_VECTORS)
def test_sha256_vectors(data, expected):
    assert bytes_digest(data, "sha256") == expected

@pytest.mark.parametrize("method", METHODS)
def test_output_length(method):
    assert len(bytes_digest(b"abc", method)) * 4 == output_bits(method)

def test_unknown_method():
    with pytest.raises(ValueError):
        bytes_digest(b"abc", "sha224")


# ---------------- Tính trên file ----------------

@pytest.fixture(scope = "module")
def sample_file(tmp_path_factory):
    data = random.Random(3).randbytes(3 * 1024 * 1024 + 123)
    path = tmp_path_factory.mktemp("data") / "sample.bin"
    path.write_bytes(data)
    expected = {
        "crc32_custom": format(zlib.crc32(data), "08x"),
        "crc32_zlib": format(zlib.crc32(data), "08x"),
        "md5": hashlib.md5(data).hexdigest(),
        "sha256": hashlib.sha256(data).hexdigest(),
    }
    return path, expected

@pytest.mark.parametrize("chunk_size", [1000, 4096, 1 << 20])
@pytest.mark.parametrize("method", METHODS)
def test_file_digest_chunk_sizes(sample_file, method, chunk_size):
    path, expected = sample_file
    assert file_digest(path, method, chunk_size) == expected[method]

@pytest.mark.parametrize("method", METHODS)
def test_empty_file(tmp_path, method):
    path = tmp_path / "empty.bin"
    path.write_bytes(b"")
    assert file_digest(path, method) == EMPTY_DIGESTS[method]