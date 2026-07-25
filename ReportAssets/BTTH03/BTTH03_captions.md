# Chú thích hình BTTH03 — Mô hình 2 lớp

## Hình minh chứng code / sơ đồ (chỉ BTTH03 — theme tím)

| File | Chú thích Word |
|------|----------------|
| `BTTH03_01_two_layer_diagram.png` | Hình 1. Sơ đồ mô hình 2 lớp: lớp giao diện (StudentsView) và lớp xử lý đối tượng HocSinh/Lop. |
| `BTTH03_02_form_event_flow.png` | Hình 2. Luồng sự kiện: load danh sách, lọc theo lớp, chọn dòng, nạp form, lưu/xóa. |
| `BTTH03_03_model_hocsinh.png` | Hình 3. Lớp HocSinhInfo — đại diện thuộc tính học sinh. |
| `BTTH03_04_model_lop.png` | Hình 4. Lớp LopInfo — đại diện thuộc tính lớp học. |
| `BTTH03_05_service_hocsinh.png` | Hình 5. Lớp xử lý student_service: lấy danh sách, thêm, sửa, xóa. |
| `BTTH03_06_form_calls_service.png` | Hình 6. Form gọi service khi chọn dòng và refresh danh sách. |

## Ảnh giao diện dùng chung — caption BTTH03 (KHÁC BTTH02)

| Ảnh | Caption BTTH03 |
|-----|----------------|
| `02_students_overview.png` | FormHocSinh: giao diện gọi HocSinhInfo và school_class_service để hiển thị danh sách và ComboBox lớp. |
| `04_students_select_edit.png` | Sự kiện chọn dòng trên lưới (SelectionChanged): dữ liệu HocSinhInfo được nạp lên form. |
| `05_students_search_filter.png` | Lọc học sinh theo lớp — gọi list_students(ma_lop=...) từ lớp xử lý HocSinh. |
| `06_classes_overview.png` | Quản lý lớp Lop riêng biệt — lớp giao diện làm việc với LopInfo qua school_class_service. |

## Không dùng ở BTTH03

Dashboard, Giáo viên, Dark mode → để dành BTTH04.

## Ghi chú cuối bài (1 câu)

> So với BTTH02 tập trung CSDL/CRUD, BTTH03 minh chứng việc tách Form và lớp xử lý đối tượng HocSinh/Lop theo mô hình 2 lớp.
