# Hash Integrity Benchmark

So sánh các phương pháp kiểm tra tính toàn vẹn dữ liệu: **CRC32**, **MD5** và **SHA-256**.

> Đề tài 10, Nhóm 2 (Xử lý chuỗi, tập tin và dữ liệu)
> Học phần Project 1, Trường Công nghệ Thông tin và Truyền thông, Đại học Bách khoa Hà Nội
> Sinh viên: Nguyễn Việt Dũng

## Mục tiêu

- Cài đặt CRC32 bằng phương pháp bảng tra và đối chiếu với `zlib.crc32`.
- Tính MD5 và SHA-256 cho file bằng `hashlib`, đọc file theo khối.
- Đo thời gian, thông lượng và độ dài đầu ra trên các file 1, 10, 50 và 100 MB.
- Đánh giá khả năng phát hiện thay đổi khi sửa 1 byte, nhiều byte hoặc nhiều vị trí trong file.
- Phân tích mục đích sử dụng và giới hạn bảo mật của từng phương pháp.

## Cấu trúc thư mục

```
hash-integrity-benchmark/
├── data/            # file thử nghiệm, sinh bằng script (không đưa lên Git)
├── src/             # mã nguồn: crc32.py, hashing.py, benchmark.py
├── scripts/         # gen_files.py: sinh dữ liệu thử nghiệm
├── results/         # file CSV số liệu đo
├── tests/           # kiểm thử tính đúng đắn (test vector)
├── reports/         # báo cáo tiến độ hằng tuần
├── requirements.txt
└── README.md
```

## Cài đặt

Yêu cầu Python 3.9 trở lên, vì script dùng `random.randbytes`. Dự án được phát triển trên Python 3.14.

```bash
git clone <link-repo>
cd hash-integrity-benchmark
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Sinh dữ liệu thử nghiệm

Chạy lệnh dưới đây **từ thư mục gốc** của repo:

```bash
python scripts/gen_files.py
```

Script tạo 4 file nhị phân ngẫu nhiên trong `data/`. Seed được cố định (`SEED = 2026`) nên lần chạy nào cũng cho ra đúng cùng một nội dung. Có thể kiểm tra bằng `shasum -a 256 data/*.bin` (Linux: `sha256sum`):

| File | Kích thước (byte) | SHA-256 |
|---|---:|---|
| `random_1MB.bin` | 1,048,576 | `e894549bc7f7e90258d3e7693797286f60b2f4f6bc0110188f069bd857a39e6a` |
| `random_10MB.bin` | 10,485,760 | `b9fb25de3c38acb68e12eefe8ceb46ea8a9a021522d20cad05f91f7700092f85` |
| `random_50MB.bin` | 52,428,800 | `8111ebd50f447a44425b2521072a871ee3e15fb2b8fd79f938973e00d294b0d2` |
| `random_100MB.bin` | 104,857,600 | `8891b6d9ee4d4be896101814e7250815a9735bd4395a288535d54009dd4374c1` |

## Test vector chuẩn

| Thuật toán | Đầu vào | Kết quả chuẩn |
|---|---|---|
| CRC32 | `"123456789"` | `cbf43926` |
| MD5 | `""` (chuỗi rỗng) | `d41d8cd98f00b204e9800998ecf8427e` |
| SHA-256 | `"abc"` | `ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad` |

```python
>>> import zlib, hashlib
>>> format(zlib.crc32(b"123456789"), "08x")
'cbf43926'
>>> hashlib.md5(b"").hexdigest()
'd41d8cd98f00b204e9800998ecf8427e'
>>> hashlib.sha256(b"abc").hexdigest()
'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'
```

## Tiến độ

- [x] Tuần 1: phân tích đề, tìm hiểu lý thuyết, thiết lập môi trường, sinh dữ liệu thử nghiệm
- [ ] Tuần 2: tự cài đặt CRC32, viết mô-đun MD5/SHA-256, viết bộ kiểm thử tự động
- [ ] Tuần 3: đo thời gian và thông lượng, ghi kết quả ra CSV
- [ ] Tuần 4: thực nghiệm sửa đổi dữ liệu
- [ ] Tuần 5–6: phân tích bảo mật, bản cài đặt C/C++, tổng hợp báo cáo

## Tài liệu tham khảo

1. R. Rivest, *RFC 1321: The MD5 Message-Digest Algorithm*, 1992.
2. NIST, *FIPS 180-4: Secure Hash Standard*, 2015.
3. D. Sarwate, "Computation of Cyclic Redundancy Checks via Table Look-Up", *Comm. ACM*, 1988.
4. P. Deutsch, *RFC 1952: GZIP File Format Specification*, 1996.
5. X. Wang, H. Yu, "How to Break MD5 and Other Hash Functions", *EUROCRYPT 2005*.
6. S. Turner, L. Chen, *RFC 6151: Updated Security Considerations for MD5*, 2011.
