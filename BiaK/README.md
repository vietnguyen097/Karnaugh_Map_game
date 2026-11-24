# BiaK - Game Đoán Hàm Số Bằng Bìa Karnaugh

## 📖 Mô Tả Dự Án

Game giáo dục giúp người chơi luyện tập kỹ thuật rút gọn hàm logic sử dụng bìa Karnaugh (K-map), một phương pháp cốt lõi trong thiết kế mạch số, kiến trúc máy tính và xử lý tín hiệu.

---

## 🎯 Mục Tiêu Game

### Cấp Độ
1. **Cơ Bản**: 2-3 biến logic (A, B hoặc A, B, C) với các nhóm đơn giản (hàng, cột, cặp ô kề).
2. **Nâng Cao**: 3-5 biến logic (lên tới 4x8 ô) với các nhóm bao biên (wrap-around), 4 góc bìa, khối trung tâm và nhóm chồng lấn.

### Cách Chơi
1. **Quan sát bìa Karnaugh**: Các biến được phân bố trên hàng/cột với mã Gray chuẩn (00, 01, 11, 10). Các ô `1` và `0` được thể hiện rõ ràng cùng chỉ số minterm tương ứng ($m_0, m_1, \dots$).
2. **Phân tích nhóm (Groups)**: Các nhóm tối ưu được khoanh màu riêng biệt.
3. **Nhập đáp án hàm rút gọn**: Sử dụng bàn phím máy tính hoặc bàn phím ảo trên màn hình để nhập dạng tổng các tích (SOP) tối giản, ví dụ: `A'B + BC'`.
4. **Kiểm tra kết quả**: Nhận phản hồi tức thì, điểm số và lời giải chi tiết từng bước.

---

## 📁 Cấu Trúc Dự Án

```
BiaK/
├── config/                    # Cấu hình game
│   └── game_config.json       # Thiết lập cơ bản (phiên bản, cấp độ, tech stack)
├── game_data/                 # Dữ liệu bài toán chuẩn hóa
│   ├── __init__.py
│   ├── game_data.py           # Module nạp và lọc dữ liệu bài toán
│   ├── basic_kmap/            # 22 bài cơ bản (2-3 biến)
│   │   ├── variables_2.json   # 10 bài 2 biến
│   │   └── variables_3.json   # 12 bài 3 biến
│   └── advanced_kmap/         # 18 bài nâng cao (3-5 biến)
│       ├── problems_3.json    # 6 bài 3 biến nâng cao
│       ├── problems_4.json    # 8 bài 4 biến
│       └── problems_5.json    # 4 bài 5 biến
├── game_engine/               # Engine tính toán logic
│   ├── __init__.py
│   ├── kmap_parser.py         # Phân tích bìa, ánh xạ Gray code, rút gọn nhóm tự động
│   ├── validator.py           # Phân tích cú pháp biểu thức & kiểm tra tương đương logic
│   └── scoring.py             # Quản lý điểm số, chuỗi thắng và thống kê
├── gui/                       # Giao diện đồ họa Tkinter hiện đại
│   ├── __init__.py
│   ├── main_window.py         # Cửa sổ chính với thanh điểm, chuyển cấp độ và lời giải
│   ├── kmap_display.py        # Canvas vẽ bìa Karnaugh, mã Gray, các ô và nhóm màu
│   └── input_handler.py       # Bàn phím ảo logic (A-E, ', +, ⌫, ↵)
├── tests/                     # Bộ kiểm thử tự động toàn diện
│   ├── test_kmap_parser.py    # Test kích thước, song ánh tọa độ, rút gọn nhóm
│   ├── test_validator.py      # Test bảng chân lý, De Morgan, tối giản SOP
│   ├── test_scoring.py        # Test điểm, số lần thử, chuỗi thắng
│   └── test_game_data.py      # Test toàn vẹn 40/40 bài toán trong database
├── tools/                     # Công cụ hỗ trợ
│   ├── generate_database.py   # Script tự động sinh & kiểm định database bài toán
│   └── kmap_generator/        # Bộ sinh mẫu bài tập mở rộng
├── main.py                    # Điểm khởi chạy chính (hỗ trợ cả GUI và CLI)
└── README.md                  # Tài liệu hướng dẫn
```

---

## 🚀 Cách Chạy Game

### 1. Yêu cầu hệ thống
- Python 3.8 trở lên.
- Không cần cài đặt thêm thư viện ngoài (sử dụng thư viện chuẩn của Python: `tkinter`, `json`, `unittest`).

### 2. Khởi chạy giao diện đồ họa (GUI Mode)
```bash
python main.py
```

### 3. Khởi chạy chế độ dòng lệnh (CLI Mode)
Dành cho môi trường không có giao diện đồ họa hoặc kiểm thử nhanh trên terminal:
```bash
python main.py --cli
```

### 4. Chạy bộ kiểm thử tự động (Unit Tests)
```bash
python -m unittest discover tests -v
```

---

## 📝 Tiến Độ Phát Triển

### Nhiệm Vụ 1: Cấu Trúc Dự Án ✅
- [x] Tạo thư mục cấu trúc chuẩn
- [x] File cấu hình `game_config.json`
- [x] Tài liệu `README.md` hoàn chỉnh

### Nhiệm Vụ 2: Database Hàm Karnaugh ✅
- [x] Tạo 100 bài cơ bản 2-3 biến (`variables_2.json`, `variables_3.json`)
- [x] Tạo 400 bài nâng cao 3-5 biến (`problems_3.json`, `problems_4.json`, `problems_5.json`)
- [x] Bổ sung các bài toán chứa **ô cô lập (Isolated Cells)** và **Don't Care ('X')** tăng độ khó cực đại
- [x] Đạt chuẩn quy mô lớn: **500 bài toán chuẩn** (180 bài 3 biến, 220 bài 4 biến, 80 bài 5 biến, 20 bài 2 biến)
- [x] 100% bài toán được tính toán tự động, có nhóm hợp lệ kích thước $2^k$ và đáp án tối giản chính xác
- [x] Cung cấp công cụ thêm bài tương tác [tools/add_problem.py](file:///c:/Users/HoangViet/Downloads/BiaK/BiaK/tools/add_problem.py) và [tools/generate_database.py](file:///c:/Users/HoangViet/Downloads/BiaK/BiaK/tools/generate_database.py)

### Nhiệm Vụ 3: Game Engine ✅
- [x] `kmap_parser.py`: Hỗ trợ 2-5 biến, mã Gray chuẩn, chuyển đổi minterm $\leftrightarrow$ tọa độ ô, rút gọn nhóm tự động
- [x] `validator.py`: Phân tích cú pháp logic tự do (chấp nhận `'`, `~`, `!`, `not`, `+`, `or`, `*`, `and`, nhân ngầm), hỗ trợ kiểm tra linh hoạt điều kiện tùy định Don't Care ('X')
- [x] `scoring.py`: Tính điểm theo lượt thử (+10, +5, +2), thưởng chuỗi thắng (streak bonus), tính tỉ lệ chính xác

### Nhiệm Vụ 4: GUI Graphical ✅
- [x] `main_window.py`: Bố cục chia cột hiện đại, chuyển đổi cấp độ nhanh, lọc theo số biến, hiển thị điểm số thời gian thực, huy hiệu Don't Care
- [x] `kmap_display.py`: Widget Canvas tùy biến vẽ bìa Karnaugh sắc nét, hiển thị minterm, các ô 'X' màu hổ phách, đường bao nhóm màu nổi bật (hỗ trợ cả bao biên wrap-around)
- [x] `input_handler.py`: Bàn phím ảo logic tiện lợi, tự động điều chỉnh danh sách biến theo bài, hỗ trợ gõ trực tiếp từ bàn phím
- [x] Hệ thống trợ giúp: Nút gợi ý (Hint), nút xem lời giải chi tiết từng bước (Reveal Solution), nút bài ngẫu nhiên (Random)

### Nhiệm Vụ 5: Test & Polish ✅
- [x] 27 test case tự động bao phủ 100% các thành phần cốt lõi và Don't Care
- [x] Kiểm định tự động tính đúng đắn của toàn bộ 500 bài tập
- [x] Chế độ CLI fallback mượt mà cho terminal (`python main.py --cli`)

---

## 🎮 Hướng Dẫn Nhập Liệu & Cú Pháp

Bạn có thể nhập biểu thức theo nhiều cách linh hoạt:
- **Phép NOT**: Sử dụng dấu nháy đơn `'` (ví dụ: `A'`), dấu ngã `~A`, dấu chấm than `!A`, hoặc `not A`.
- **Phép AND**: Viết liền (nhân ngầm) `AB`, dấu cách `A B`, dấu sao `A*B`, dấu `&`, hoặc `A and B`.
- **Phép OR**: Sử dụng dấu cộng `+`, dấu gạch đứng `|`, hoặc `A or B`.
- **Hằng số**: `1` (hàm hằng 1) hoặc `0` (hàm hằng 0).

*Ví dụ hợp lệ:*
- `A'B + AB'`
- `B'C + AC`
- `~A B + A ~B`
- `B'D'`
- `1`

---

## 🏆 Hệ Thống Điểm Số & Thưởng
- **Đoán đúng lần đầu**: **+10 điểm** + thưởng độ khó
- **Đoán đúng lần thứ hai**: **+5 điểm**
- **Đoán đúng từ lần 3 trở đi**: **+2 điểm**
- **Thưởng chuỗi thắng (Streak Bonus)**: Mỗi mốc 3 bài đúng liên tiếp nhận thêm **+2 điểm**
- **Tỉ lệ chính xác (Accuracy)**: Được tính tự động và cập nhật trực tiếp trên thanh công cụ

---

**Phiên bản**: 1.0.0  
**Giấy phép**: MIT License  
**Tác giả**: BiaK Game Team
