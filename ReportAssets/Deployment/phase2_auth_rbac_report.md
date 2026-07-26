# GIAI ĐOẠN 2: Xác thực và phân quyền

## MỤC TIÊU

Xây dựng nền xác thực web cho HSMS gồm đăng nhập, đăng xuất, session, đổi mật khẩu, trạng thái tài khoản, role-based access control, activity log kèm người thực hiện và seed admin ban đầu.

## HIỆN TRẠNG ĐÃ KIỂM TRA

- Branch thực hiện: `cloud-deployment`
- Web app Flask từ Giai đoạn 1 vẫn khởi động bằng application factory.
- Desktop app cũ không bị chỉnh sửa logic.
- Các route nghiệp vụ web skeleton đã được bảo vệ bằng kiểm tra quyền phía server.

## FILE ĐÃ TẠO

- `app/models/auth.py`
- `app/repositories/auth_repository.py`
- `app/services/auth_service.py`
- `app/security.py`
- `app/blueprints/auth/forms.py`
- `app/templates/auth/login.html`
- `app/templates/auth/change_password.html`
- `app/templates/auth/activity_log.html`
- `app/templates/components/flash.html`
- `app/templates/errors/403.html`
- `tests/test_auth.py`

## FILE ĐÃ SỬA

- `app/__init__.py`
- `app/extensions.py`
- `app/commands.py`
- `app/blueprints/auth/routes.py`
- `app/blueprints/dashboard/routes.py`
- `app/blueprints/students/routes.py`
- `app/blueprints/classes/routes.py`
- `app/blueprints/teachers/routes.py`
- `app/blueprints/admissions/routes.py`
- `app/blueprints/profiles/routes.py`
- `app/blueprints/training/routes.py`
- `app/blueprints/exams/routes.py`
- `app/blueprints/finance/routes.py`
- `app/blueprints/affairs/routes.py`
- `app/blueprints/graduation/routes.py`
- `app/blueprints/errors/handlers.py`
- `app/templates/components/nav.html`
- `app/static/css/app.css`
- `.env.example`
- `README.md`

## CODE CŨ ĐÃ TÁI SỬ DỤNG

- Chưa chuyển trực tiếp tài khoản desktop sang web.
- Vẫn giữ định hướng phân tầng từ dự án cũ: model, repository, service, route/template.
- Activity log web được thiết kế cùng tinh thần với log nghiệp vụ desktop nhưng có thêm `actor_id`, IP và user-agent.

## LỆNH ĐÃ CHẠY

```powershell
python -m pytest -p no:cacheprovider tests
python -c "from app import create_app; app=create_app('testing'); client=app.test_client(); print(client.get('/health').status_code)"
flask --app run:app routes
```

## TEST

- PASS: 122 file Python compile cú pháp thành công.
- PASS: 10 test chạy thành công.
- PASS: Login tạo session và ghi activity log.
- PASS: Logout hoạt động bằng `POST`.
- PASS: Tài khoản bị khóa không đăng nhập được.
- PASS: Route nhạy cảm yêu cầu đăng nhập.
- PASS: Student truy cập route quản trị nhận HTTP 403.
- PASS: Admin truy cập route quản trị thành công.
- PASS: Teacher chỉ vào route phạm vi được phân công.
- PASS: Student chỉ vào route self.
- PASS: Service scope check chặn truy cập sai học sinh/giáo viên.
- PASS: User không đủ quyền không thể đổi role qua service.
- PASS: CLI `seed-admin` tạo tài khoản admin.
- PASS: Mật khẩu được hash bằng Werkzeug, không lưu mật khẩu thô và không dùng SHA-256 đơn thuần.

## RỦI RO CÒN LẠI

- Chưa có màn hình quản lý tài khoản đầy đủ cho admin.
- Chưa có migration Alembic chính thức cho bảng auth.
- Scope dữ liệu teacher/student hiện mới là guard nền; các module nghiệp vụ thật sẽ dùng guard này khi chuyển đổi dữ liệu ở các giai đoạn sau.

## TIÊU CHÍ HOÀN THÀNH

- Đạt: Đăng nhập.
- Đạt: Đăng xuất.
- Đạt: Session.
- Đạt: Đổi mật khẩu.
- Đạt: Trạng thái tài khoản.
- Đạt: Role-based access control.
- Đạt: Activity log kèm người thực hiện.
- Đạt: Route nhạy cảm kiểm tra quyền phía server.
- Đạt: Không đủ quyền nhận HTTP 403.
- Đạt: Seed admin bằng CLI/env.

## COMMIT

Commit Giai đoạn 2 được thực hiện trên branch `cloud-deployment`.

## BƯỚC TIẾP THEO

Giai đoạn tiếp theo sẽ chuyển dần dữ liệu/nghiệp vụ cốt lõi sang web và gắn các service scope guard vào module thật.
