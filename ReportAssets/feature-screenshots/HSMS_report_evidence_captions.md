# Chú thích ảnh minh chứng theo bài thực hành

## Bài thực hành 2 - Database và CRUD

1. `BTTH02_01_database_schema_hocsinh_lop.png` - Hình minh chứng cấu trúc cơ sở dữ liệu với hai bảng chính `LOP` và `HOCSINH`, khóa chính và khóa ngoại đúng theo yêu cầu quản lý học sinh theo lớp.
2. `BTTH02_02_student_dao_crud_sql.png` - Hình minh chứng các thao tác CRUD ở tầng DAO: thêm, cập nhật và xóa học sinh bằng câu lệnh SQL có tham số.
3. `BTTH02_03_crud_flow.png` - Sơ đồ mô tả luồng CRUD cơ bản: người dùng nhập form, hệ thống kiểm tra dữ liệu, DAO ghi xuống bảng và danh sách được tải lại.

## Bài thực hành 3 - Tách đối tượng và xử lý form

4. `BTTH03_01_models_hocsinh_lop.png` - Hình minh chứng lớp đối tượng `HocSinhInfo` và `LopInfo`, dùng để đóng gói dữ liệu thay vì truyền rời rạc từng biến.
5. `BTTH03_02_form_to_objects_flow.png` - Sơ đồ mô tả luồng từ màn hình quản lý học sinh sang object, service và danh sách hiển thị.
6. `BTTH03_03_students_form_handling_code.png` - Hình minh chứng phần xử lý form: chuyển dữ liệu form thành `HocSinhInfo`, chọn dòng để sửa và lưu dữ liệu.

## Bài thực hành 4 - Kiến trúc 3 lớp và mở rộng hệ thống

7. `BTTH04_01_project_3layer_tree.png` - Hình minh chứng cấu trúc thư mục đã tách thành `ui`, `services`, `dao`, `models`, `database`.
8. `BTTH04_02_architecture_3layer_diagram.png` - Sơ đồ kiến trúc 3 lớp của hệ thống: giao diện, xử lý nghiệp vụ, truy cập dữ liệu và database.
9. `BTTH04_03_service_dao_example.png` - Hình minh chứng service kiểm tra nghiệp vụ và gọi DAO, trong khi DAO chịu trách nhiệm làm việc trực tiếp với SQL/database.
