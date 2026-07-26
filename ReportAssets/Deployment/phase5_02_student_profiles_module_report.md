# GIAI ĐOẠN 5.2: Module Hồ sơ học sinh

## MỤC TIÊU

Chuyển module Hồ sơ học sinh sang web theo đúng thứ tự Giai đoạn 5, bao gồm cập nhật lý lịch, hộ khẩu, thông tin phụ huynh, trạng thái học tập và diện chính sách.

## PHẠM VI ĐÃ THỰC HIỆN

- Danh sách hồ sơ học sinh.
- Tìm kiếm theo mã hoặc họ tên.
- Lọc theo trạng thái học tập.
- Lọc theo diện chính sách.
- Cập nhật lý lịch cơ bản.
- Cập nhật hộ khẩu, địa chỉ liên hệ.
- Cập nhật thông tin phụ huynh.
- Cập nhật trạng thái học tập.
- Cập nhật diện chính sách.
- Học sinh xem hồ sơ của chính mình.

Không đưa khen thưởng/kỷ luật vào 5.2 vì đó là module kế tiếp riêng trong Giai đoạn 5.

## MODEL

Sử dụng `Student` trong `app/models/academic.py`.

Các trường liên quan:

- `full_name`
- `gender`
- `address`
- `class_id`
- `household`
- `parent_name`
- `parent_phone`
- `learning_status`
- `policy_type`

## MIGRATION

Không tạo migration mới cho 5.2 vì các trường hồ sơ học sinh đã có trong migration nền Giai đoạn 3.

## REPOSITORY

File:

- `app/repositories/profile_repository.py`

Chức năng:

- Danh sách hồ sơ.
- Tìm kiếm.
- Lọc trạng thái.
- Lọc diện chính sách.
- Lấy hồ sơ theo id.

## SERVICE

File:

- `app/services/profile_service.py`

Chức năng:

- `list`
- `get`
- `update_profile`
- `get_self_profile`

## BLUEPRINT, ROUTE, TEMPLATE

File route:

- `app/blueprints/profiles/routes.py`

Template:

- `app/templates/profiles/index.html`
- `app/templates/profiles/form.html`
- `app/templates/profiles/detail.html`

Route:

- `GET /profiles/`
- `GET, POST /profiles/<student_id>/edit`
- `GET /profiles/me`

## VALIDATION

- Họ tên bắt buộc.
- Trạng thái học tập chỉ nhận: `Đang học`, `Bảo lưu`, `Thôi học`, `Tốt nghiệp`.
- Diện chính sách chỉ nhận danh mục hợp lệ.
- Số điện thoại phụ huynh phải đúng dạng số điện thoại cơ bản.
- Lớp học phải tồn tại nếu được chọn.

## PHÂN QUYỀN

- Admin dùng quyền `profiles:access` để quản lý hồ sơ học sinh.
- Student dùng quyền `profile:self:view` để xem hồ sơ chính mình.
- Student không được truy cập danh sách quản trị `/profiles/`.

## TRANSACTION

`StudentProfileService.update_profile` dùng transaction khi cập nhật hồ sơ, đặc biệt với thay đổi lớp hoặc trạng thái học tập.

## ACTIVITY LOG

Ghi log cho:

- Cập nhật hồ sơ học sinh.
- Thay đổi lớp/trạng thái học tập.

## UNIT TEST VÀ INTEGRATION TEST

File:

- `tests/test_profiles_web.py`

Đã kiểm tra:

- Service cập nhật hồ sơ.
- Validation trạng thái học tập.
- Validation số điện thoại phụ huynh.
- Route danh sách/filter.
- Route cập nhật hồ sơ.
- Học sinh xem hồ sơ của chính mình.
- Học sinh bị chặn khỏi route quản trị bằng HTTP 403.

## LỆNH ĐÃ CHẠY

```powershell
python -m pytest -p no:cacheprovider tests
$env:PYTHONDONTWRITEBYTECODE='1'; python -c "from pathlib import Path; files=[p for p in Path('.').rglob('*.py') if '.venv' not in p.parts and '__pycache__' not in p.parts]; [compile(p.read_text(encoding='utf-8'), str(p), 'exec') for p in files]; print('syntax ok', len(files))"
flask --app run:app routes
```

## TEST

- PASS: 141 file Python compile cú pháp thành công.
- PASS: 33 test chạy thành công.
- PASS: Module Hồ sơ học sinh có luồng nghiệp vụ thực tế, không chỉ giao diện.

## RỦI RO CÒN LẠI

- Chưa có lịch sử thay đổi hồ sơ dạng audit chi tiết từng trường.
- Chưa có upload giấy tờ/hồ sơ đính kèm.
- Khen thưởng/kỷ luật sẽ được xử lý ở module tiếp theo.

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

## COMMIT

Commit local Giai đoạn 5.2 được thực hiện trên branch `cloud-deployment`. Không push GitHub theo nhắc nhở của người dùng.

## BƯỚC TIẾP THEO

Tiếp tục module kế tiếp của Giai đoạn 5: Khen thưởng và kỷ luật.
