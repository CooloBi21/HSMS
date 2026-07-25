# GIAI ĐOẠN 4: Xây dựng MVP Web

## MỤC TIÊU

Chuyển các module nền sang web trước: đăng nhập, dashboard, học sinh, lớp học, giáo viên, tài khoản và activity log. MVP phải có xác thực, phân quyền server-side, activity log, test, giao diện responsive và không phụ thuộc CustomTkinter trong package web.

## HIỆN TRẠNG ĐÃ KIỂM TRA

- Branch thực hiện: `cloud-deployment`
- Nền SQLAlchemy/migration từ Giai đoạn 3 đã được dùng cho MVP.
- Các module MVP chạy qua Flask route/template/service/repository.
- Web package `app/` không import `customtkinter`, `CTk` hoặc `tkinter`.

## FILE ĐÃ TẠO

- `app/repositories/mvp_repository.py`
- `app/services/mvp_service.py`
- `app/templates/auth/accounts.html`
- `app/templates/classes/index.html`
- `app/templates/classes/form.html`
- `app/templates/students/index.html`
- `app/templates/students/form.html`
- `app/templates/teachers/index.html`
- `app/templates/teachers/form.html`
- `app/templates/components/table_actions.html`
- `tests/test_mvp_web.py`

## FILE ĐÃ SỬA

- `app/blueprints/auth/routes.py`
- `app/blueprints/dashboard/routes.py`
- `app/blueprints/students/routes.py`
- `app/blueprints/classes/routes.py`
- `app/blueprints/teachers/routes.py`
- `app/static/css/app.css`
- `app/templates/components/nav.html`
- `app/templates/dashboard/index.html`
- `README.md`

## CODE CŨ ĐÃ TÁI SỬ DỤNG

- Nghiệp vụ nền từ desktop được chuyển theo các module quen thuộc: học sinh, lớp học, giáo viên, tài khoản, dashboard.
- RBAC và activity log từ Giai đoạn 2 được dùng lại trong toàn bộ route MVP.
- SQLAlchemy model/migration từ Giai đoạn 3 được dùng làm lớp dữ liệu web.

## LỆNH ĐÃ CHẠY

```powershell
python -m pytest -p no:cacheprovider tests
flask --app run:app routes
python -c "from app import create_app; app=create_app('testing'); client=app.test_client(); print('/health', client.get('/health').status_code)"
rg "customtkinter|CTk|tkinter" app tests
docker --version
psql --version
```

## TEST

- PASS: 132 file Python compile cú pháp thành công.
- PASS: 19 test chạy thành công.
- PASS: Đăng nhập và session admin.
- PASS: Dashboard render dữ liệu tổng quan.
- PASS: Activity log ghi thao tác đăng nhập và thao tác CRUD.
- PASS: Học sinh có danh sách, thêm, sửa/xóa service, tìm kiếm, lọc lớp, phân trang và validation backend.
- PASS: Lớp học có danh sách, thêm, sửa/xóa service, lọc khối, sĩ số và chặn xóa lớp còn học sinh.
- PASS: Giáo viên có danh sách, thêm, sửa/xóa service, lọc trạng thái, kiểm tra email và số điện thoại.
- PASS: Tài khoản có danh sách, tạo tài khoản, hash mật khẩu và cập nhật trạng thái.
- PASS: Route nhạy cảm dùng RBAC phía server.
- PASS: Giao diện dùng Bootstrap responsive.
- PASS: Package web không phụ thuộc CustomTkinter.

## RỦI RO CÒN LẠI

- Chưa kiểm chứng trực tiếp trên PostgreSQL trong môi trường hiện tại vì `docker` và `psql` không khả dụng trong PATH.
- Cấu hình `DATABASE_URL` và Docker Compose đã sẵn sàng cho PostgreSQL, nhưng test container sẽ thực hiện trên VM có Docker ở giai đoạn chạy Docker/PostgreSQL/Nginx.
- MVP mới chuyển module nền, chưa chuyển các module nghiệp vụ sâu như tuyển sinh, đào tạo, khảo thí, tài chính, công tác sinh viên và tốt nghiệp.

## TIÊU CHÍ HOÀN THÀNH

- Đạt: Có xác thực.
- Đạt: Có phân quyền.
- Đạt: Có activity log.
- Đạt: Có test.
- Đạt: Responsive.
- Đạt: Web app không phụ thuộc CustomTkinter.
- Đạt ở mức cấu hình/code: dùng SQLAlchemy và `DATABASE_URL` cho PostgreSQL.
- Chưa kiểm chứng runtime trực tiếp: PostgreSQL container do thiếu Docker/psql trong môi trường hiện tại.

## COMMIT

Commit Giai đoạn 4 được thực hiện trên branch `cloud-deployment`.

## BƯỚC TIẾP THEO

Chạy MVP trên VM có Docker/PostgreSQL, cấu hình Nginx nội bộ và kiểm tra truy cập trong VM.
