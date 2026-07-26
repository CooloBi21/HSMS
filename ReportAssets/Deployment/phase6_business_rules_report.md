# GIAI ĐOẠN 6: Sửa các lỗi nghiệp vụ quan trọng

## MỤC TIÊU

Đặt các chốt nghiệp vụ quan trọng ở tầng service/transaction để hệ thống web không chỉ đúng ở giao diện mà còn đúng ở server-side business logic.

## PHẠM VI ĐÃ THỰC HIỆN

### Tuyển sinh

- Chỉ hồ sơ `approved` mới được nhập học.
- Không nhập học hai lần.
- Tạo học sinh và cập nhật hồ sơ trong một transaction.
- Kiểm tra lớp dự kiến tồn tại.
- Kiểm tra sĩ số nếu lớp có cấu hình `capacity`.

### Đào tạo

- Chặn đăng ký trùng học phần.
- Bản ghi `canceled` không được tính như đăng ký đang hoạt động.
- Chặn vượt sĩ số học phần.
- Chặn trùng phòng.
- Chặn trùng giáo viên.
- Chặn trùng lớp.

### Khảo thí

- Điểm phải nằm trong miền 0 đến 10.
- Không nhập điểm cho học sinh không thuộc lớp hoặc học phần.
- Phúc khảo cập nhật lại điểm cuối kỳ, điểm trung bình, GPA và xếp loại chữ.
- Trọng số điểm nhận qua service config, không cố định trong route/UI.

### Tài chính

- Không thanh toán số âm hoặc bằng 0.
- Không thanh toán vượt số còn nợ.
- Xóa thanh toán tính lại hóa đơn qua transaction service hiện có.
- Trạng thái quá hạn xét theo ngày đến hạn.
- Không xóa hóa đơn đã có thanh toán nếu chưa xử lý thanh toán liên quan.
- Học bổng lấy điểm thực tế từ `GradeRecord`.

### Tốt nghiệp

- Không cấp bằng cho học sinh chưa đạt.
- Số bằng và số sổ gốc được kiểm tra unique trước khi cấp.
- Cấp bằng cập nhật trạng thái xét tốt nghiệp sang `graduated`.

### Báo cáo

- Khi xuất biểu mẫu, không chấp nhận đường dẫn giả nếu chưa có mẫu thật.

## FILE ĐÃ TẠO

- `app/services/business_rule_service.py`
- `tests/test_phase6_business_rules.py`
- `migrations/versions/dde19db034b4_add_phase_6_business_constraints.py`

## FILE ĐÃ SỬA

- `README.md`
- `app/models/academic.py`
- `app/models/operations.py`
- `app/models/__init__.py`
- `app/services/admission_web_service.py`

## MIGRATION

Revision mới:

- `dde19db034b4_add_phase_6_business_constraints.py`

Thay đổi schema:

- Thêm `school_classes.capacity`.
- Thêm bảng `course_registrations`.
- Thêm bảng `class_schedules`.
- Thêm `tuition_invoices.due_date`.
- Thêm `payment_records.payment_date`.

## LỆNH ĐÃ CHẠY

```powershell
flask --app run:app db migrate -m "add phase 6 business constraints"
flask --app run:app db upgrade
python -m pytest -p no:cacheprovider tests
$env:PYTHONDONTWRITEBYTECODE='1'; python -c "from pathlib import Path; files=[p for p in Path('.').rglob('*.py') if '.venv' not in p.parts and '__pycache__' not in p.parts]; [compile(p.read_text(encoding='utf-8'), str(p), 'exec') for p in files]; print('syntax ok', len(files))"
```

## TEST

- PASS: 138 file Python compile cú pháp thành công.
- PASS: 29 test chạy thành công.
- PASS: Các lỗi nghiệp vụ Phase 6 có test trực tiếp ở service layer.
- PASS: Migration Phase 6 apply được trên database development local.

## RỦI RO CÒN LẠI

- Một số module sâu chưa có UI web hoàn chỉnh, nhưng guard nghiệp vụ đã được đặt trước ở service.
- Chưa kiểm chứng PostgreSQL container do môi trường hiện tại chưa có Docker/psql.
- Xuất biểu mẫu thật cần template/file chuẩn ở giai đoạn báo cáo/export sau.

## TIÊU CHÍ HOÀN THÀNH

- Đạt: Tuyển sinh.
- Đạt: Đào tạo.
- Đạt: Khảo thí.
- Đạt: Tài chính.
- Đạt: Tốt nghiệp.
- Đạt: Báo cáo không dùng đường dẫn giả.
- Đạt: Có migration, service guard và test.

## COMMIT

Commit local Giai đoạn 6 được thực hiện trên branch `cloud-deployment`. Không push GitHub theo nhắc nhở của người dùng.

## BƯỚC TIẾP THEO

Tiếp tục các module còn lại của Giai đoạn 5 hoặc chuyển sang giai đoạn Docker/PostgreSQL/Nginx khi người dùng yêu cầu.
