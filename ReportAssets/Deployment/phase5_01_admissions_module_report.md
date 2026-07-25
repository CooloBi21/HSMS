# GIAI ĐOẠN 5.1: Module Tuyển sinh

## MỤC TIÊU

Chuyển module Tuyển sinh sang web theo đúng thứ tự đầu tiên của Giai đoạn 5. Module phải có model, migration, repository, service, blueprint, route, template, validation, phân quyền, transaction, activity log, unit test, integration test và tài liệu.

## PHẠM VI ĐÃ THỰC HIỆN

- Tiếp nhận hồ sơ tuyển sinh.
- Tìm kiếm và lọc hồ sơ theo trạng thái.
- Xét tuyển tự động theo điểm chuẩn.
- Nhập học hồ sơ đã trúng tuyển.
- Tự động cấp mã học sinh.
- Phân lớp theo lớp dự kiến.
- Chặn nhập học hồ sơ chưa trúng tuyển.
- Chặn xóa hồ sơ đã nhập học.

## MODEL

Sử dụng `AdmissionApplication` trong `app/models/operations.py`.

Các quan hệ chính:

- `AdmissionApplication.desired_class_id -> SchoolClass.id`
- `AdmissionApplication.student_id -> Student.id`

## MIGRATION

Không tạo migration mới cho module Tuyển sinh vì bảng `admission_applications` đã được tạo ở Giai đoạn 3 trong revision:

- `migrations/versions/4d3bebc7115c_create_core_postgres_schema.py`

Migration hiện có đã bao gồm:

- Primary key.
- Unique constraint cho `application_code`.
- Foreign key đến lớp dự kiến.
- Foreign key đến học sinh sau nhập học.
- Index theo trạng thái và lớp dự kiến.
- `created_at`, `updated_at`.

## REPOSITORY

File:

- `app/repositories/admission_repository.py`

Chức năng:

- Danh sách hồ sơ.
- Tìm kiếm theo mã, họ tên, số điện thoại.
- Lọc trạng thái.
- Lấy hồ sơ theo id/code.
- Sinh mã hồ sơ.
- Sinh mã học sinh.

## SERVICE

File:

- `app/services/admission_web_service.py`

Chức năng:

- `receive_application`: tiếp nhận/cập nhật hồ sơ.
- `auto_screen`: xét tuyển tự động theo điểm chuẩn.
- `enroll`: nhập học, cấp mã học sinh và phân lớp.
- `delete`: xóa hồ sơ chưa nhập học.

## BLUEPRINT, ROUTE, TEMPLATE

File route:

- `app/blueprints/admissions/routes.py`

Template:

- `app/templates/admissions/index.html`
- `app/templates/admissions/form.html`

Route:

- `GET /admissions/`
- `GET, POST /admissions/new`
- `GET, POST /admissions/<id>/edit`
- `POST /admissions/<id>/screen`
- `POST /admissions/<id>/enroll`
- `POST /admissions/<id>/delete`

## VALIDATION

- Họ tên thí sinh bắt buộc.
- Điểm xét tuyển phải là số từ 0 đến 10.
- Ngày sinh phải đúng định dạng ngày.
- Lớp dự kiến phải tồn tại nếu được chọn.
- Mã hồ sơ không được trùng.
- Hồ sơ đã nhập học không được sửa/xóa.
- Chỉ hồ sơ `approved` mới được nhập học.

## PHÂN QUYỀN

Tất cả route Tuyển sinh dùng:

- `@permission_required("admissions:access")`

Người dùng không đủ quyền nhận HTTP 403.

## TRANSACTION

Luồng nhập học dùng transaction qua:

- `BusinessTransactionService.enroll_admission`

Trong cùng một transaction:

- Tạo `Student`.
- Gán mã học sinh.
- Gán lớp dự kiến.
- Cập nhật hồ sơ sang `enrolled`.
- Ghi `student_id`.
- Ghi activity log.

## ACTIVITY LOG

Các thao tác được ghi log:

- Tiếp nhận/cập nhật hồ sơ.
- Xét tuyển tự động.
- Nhập học.
- Xóa hồ sơ.

## UNIT TEST VÀ INTEGRATION TEST

File:

- `tests/test_admissions_web.py`

Đã kiểm tra:

- Tạo hồ sơ.
- Validation backend.
- Xét tuyển đạt.
- Xét tuyển không đạt.
- Nhập học tạo học sinh thật.
- Cập nhật trạng thái hồ sơ sau nhập học.
- Gán lớp dự kiến cho học sinh.
- Activity log.
- Route tìm kiếm/lọc.
- Chặn xóa hồ sơ đã nhập học.
- Student không có quyền truy cập module Tuyển sinh nhận HTTP 403.

## LỆNH ĐÃ CHẠY

```powershell
python -m pytest -p no:cacheprovider tests
$env:PYTHONDONTWRITEBYTECODE='1'; python -c "from pathlib import Path; files=[p for p in Path('.').rglob('*.py') if '.venv' not in p.parts and '__pycache__' not in p.parts]; [compile(p.read_text(encoding='utf-8'), str(p), 'exec') for p in files]; print('syntax ok', len(files))"
flask --app run:app routes
```

## TEST

- PASS: 135 file Python compile cú pháp thành công.
- PASS: 24 test chạy thành công.
- PASS: Module Tuyển sinh có luồng nghiệp vụ thực tế, không chỉ CRUD/giao diện.

## RỦI RO CÒN LẠI

- Chưa có upload file hồ sơ đính kèm.
- Chưa có cấu hình điểm chuẩn theo từng ngành/lớp; hiện dùng điểm chuẩn mặc định trong service hoặc truyền vào service test.
- Chưa chuyển sang màn hình public cho thí sinh tự nộp hồ sơ, hiện là nghiệp vụ nội bộ sau đăng nhập.

## TIÊU CHÍ HOÀN THÀNH

- Đạt: Model.
- Đạt: Migration.
- Đạt: Repository.
- Đạt: Service.
- Đạt: Blueprint/route.
- Đạt: Template.
- Đạt: Validation.
- Đạt: Phân quyền.
- Đạt: Transaction.
- Đạt: Activity log.
- Đạt: Unit/integration test.
- Đạt: Tài liệu.

## BƯỚC TIẾP THEO

Tiếp tục module thứ hai của Giai đoạn 5: Hồ sơ học sinh.
