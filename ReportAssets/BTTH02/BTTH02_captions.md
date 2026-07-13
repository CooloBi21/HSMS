# Chú thích hình BTTH02 — CSDL & CRUD

Dùng kèm ảnh giao diện từ `feature-screenshots/` nhưng **caption phải nhấn CSDL/CRUD**, không nhấn kiến trúc 3 lớp.

## Hình minh chứng code / CSDL (chỉ BTTH02)

| File | Chú thích đề xuất (Word) |
|------|--------------------------|
| `BTTH02_01_er_diagram_lop_hocsinh.png` | Hình 1. Sơ đồ quan hệ hai bảng LOP và HOCSINH trong CSDL QLHOCSINH (SQLite), thể hiện khóa chính MaLop/MaHS và khóa ngoại MaLop. |
| `BTTH02_02_schema_init_db.png` | Hình 2. Đoạn mã SQL khai báo bảng LOP và HOCSINH trong file `database/init_db.sql`. |
| `BTTH02_03_dao_crud_hocsinh.png` | Hình 3. Đoạn xử lý thêm mới (INSERT), cập nhật (UPDATE) và xóa (DELETE) dữ liệu học sinh trên bảng HOCSINH. |
| `BTTH02_04_load_combobox_lop.png` | Hình 4. Đoạn đọc danh sách lớp từ CSDL và nạp vào ComboBox trên form nhập học sinh (tương đương Form_Load trong bài thực hành). |

## Gợi ý caption khi dùng lại ảnh giao diện chung

| Ảnh giao diện | Caption BTTH02 (khác BTTH03/04) |
|---------------|----------------------------------|
| `02_students_overview.png` | Màn hình nhập và quản lý dữ liệu học sinh: các trường MaHS, HoTen, GioiTinh, NgaySinh, DiaChi, DiemTB, MaLop và lưới danh sách. |
| `03_students_add_new_autocode.png` | Thao tác thêm mới học sinh — dữ liệu được ghi vào bảng HOCSINH. |
| `04_students_select_edit.png` | Chọn dòng trên lưới để nạp dữ liệu lên form và thực hiện UPDATE. |
| `05_students_search_filter.png` | Tìm kiếm/lọc danh sách học sinh theo lớp (truy vấn có điều kiện trên HOCSINH). |
| `06_classes_overview.png` | Quản lý bảng LOP — dữ liệu lớp phục vụ ComboBox chọn lớp cho học sinh. |

## Câu ghi chú kiến trúc (1 dòng cuối bài)

> Trong phiên bản hiện tại, hệ thống đã được nâng cấp kiến trúc để dễ bảo trì hơn; phần minh chứng BTTH02 tập trung vào CSDL và các thao tác CRUD cơ bản.
