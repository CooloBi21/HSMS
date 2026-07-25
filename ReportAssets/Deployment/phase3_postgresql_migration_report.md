# GIAI ĐOẠN 3: PostgreSQL và migration

## MỤC TIÊU

Thiết kế SQLAlchemy model, tạo migration Alembic/Flask-Migrate, chuẩn hóa khóa chính, khóa ngoại, index, unique constraint, timestamp và quan hệ lõi giữa tài khoản, học sinh, giáo viên và lớp. Đồng thời chuẩn bị script chuyển dữ liệu SQLite sang database đích qua `DATABASE_URL`.

## HIỆN TRẠNG ĐÃ KIỂM TRA

- Branch thực hiện: `cloud-deployment`
- Migration Alembic được tạo trong `migrations/`.
- Revision đầu tiên: `4d3bebc7115c_create_core_postgres_schema.py`
- Script chuyển dữ liệu: `scripts/migrate_sqlite_to_postgres.py`
- SQLite source dry-run: `LOP=14`, `HOCSINH=1007`, `GIAOVIEN=8`, reject `0`.
- Apply thử trên database development local: target sau migrate `school_classes=14`, `students=1007`, `teachers=8`, reject `0`.

## FILE ĐÃ TẠO

- `app/models/academic.py`
- `app/models/operations.py`
- `app/services/transaction_service.py`
- `migrations/`
- `scripts/migrate_sqlite_to_postgres.py`
- `tests/test_database_schema.py`

## FILE ĐÃ SỬA

- `.env.example`
- `app/__init__.py`
- `app/config.py`
- `app/models/__init__.py`
- `app/models/auth.py`
- `app/services/auth_service.py`

## CODE CŨ ĐÃ TÁI SỬ DỤNG

- Dữ liệu desktop SQLite được ánh xạ từ `LOP`, `HOCSINH`, `GIAOVIEN`.
- Tinh thần phân tầng cũ được giữ: model, service, script chuyển dữ liệu.
- Activity log từ Giai đoạn 2 được điều chỉnh để hoạt động đúng bên trong transaction.

## LỆNH ĐÃ CHẠY

```powershell
flask --app run:app db init
flask --app run:app db migrate -m "create core postgres schema"
flask --app run:app db upgrade
python scripts\migrate_sqlite_to_postgres.py --sqlite-path data\hsms.db
python scripts\migrate_sqlite_to_postgres.py --sqlite-path data\hsms.db --apply
python -m pytest -p no:cacheprovider tests
```

## TEST

- PASS: 129 file Python compile cú pháp thành công.
- PASS: 14 test chạy thành công.
- PASS: Có primary key chuẩn dạng integer identity cho web schema.
- PASS: Có foreign key giữa user, student, teacher, class và các bảng nghiệp vụ.
- PASS: Có unique constraint cho code/email/scope nghiệp vụ.
- PASS: Có index cho trường tìm kiếm/lọc chính.
- PASS: Có `created_at` và `updated_at` ở các model nghiệp vụ chính.
- PASS: Script chuyển dữ liệu có dry-run/apply và log reject.
- PASS: Các luồng nhiều bước có transaction service.

## RỦI RO CÒN LẠI

- Chưa chạy trực tiếp trên PostgreSQL container ở Giai đoạn 3.
- Script migration mới chuyển nhóm dữ liệu nền: lớp, học sinh, giáo viên.
- Các module nghiệp vụ sâu sẽ được chuyển tiếp trong các giai đoạn sau.

## TIÊU CHÍ HOÀN THÀNH

- Đạt: SQLAlchemy model.
- Đạt: Alembic/Flask-Migrate migration.
- Đạt: Khóa chính, khóa ngoại, index, unique constraint.
- Đạt: Timestamp phù hợp.
- Đạt: Quan hệ tài khoản, học sinh, giáo viên, lớp.
- Đạt: Script chuyển SQLite sang database đích qua `DATABASE_URL`.
- Đạt: Kiểm tra count/null/FK nền bằng test và dry-run.
- Đạt: Không hard-code secret, password, connection string hay Cloudflare credential.

## COMMIT

Commit Giai đoạn 3 được thực hiện trên branch `cloud-deployment`.

## BƯỚC TIẾP THEO

Giai đoạn 4 xây dựng MVP Web cho đăng nhập, dashboard, học sinh, lớp học, giáo viên, tài khoản và activity log.
