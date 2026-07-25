# GIAI ĐOẠN 1: Tạo cấu trúc HSMS Web App

## MỤC TIÊU

Tạo nền Flask web app có tổ chức, tách rõ application factory, blueprint, extension initialization, cấu hình theo môi trường, error handler và logging tập trung. Giai đoạn này chưa chuyển toàn bộ nghiệp vụ desktop sang web.

## HIỆN TRẠNG ĐÃ KIỂM TRA

- Branch thực hiện: `cloud-deployment`
- Bản desktop vẫn được giữ ở tag `desktop-v1.0` và branch `desktop-final`.
- Web app mới được đặt trong `app/`, tách riêng khỏi UI CustomTkinter cũ.
- Entry point web: `run.py`
- Healthcheck: `/health`
- Trang tổng quan nền: `/`

## FILE ĐÃ TẠO

- `app/__init__.py`
- `app/config.py`
- `app/extensions.py`
- `app/commands.py`
- `app/logging_config.py`
- `app/models/__init__.py`
- `app/repositories/__init__.py`
- `app/services/__init__.py`
- `app/blueprints/*`
- `app/templates/*`
- `app/static/*`
- `run.py`
- `gunicorn.conf.py`
- `Dockerfile`
- `docker-compose.yml`
- `.env.example`
- `tests/test_health.py`
- `migrations/.gitkeep`
- `scripts/.gitkeep`
- `docker/.gitkeep`
- `nginx/.gitkeep`
- `backups/.gitkeep`

## FILE ĐÃ SỬA

- `requirements.txt`
- `.gitignore`
- `README.md`

## CODE CŨ ĐÃ TÁI SỬ DỤNG

- Chưa tái sử dụng trực tiếp logic nghiệp vụ trong web ở Giai đoạn 1.
- Giữ nguyên code desktop để các giai đoạn sau đối chiếu và chuyển từng module.
- Cấu trúc blueprint đã bám theo các module nghiệp vụ hiện có: tuyển sinh, học sinh, lớp học, giáo viên, hồ sơ, đào tạo, khảo thí, tài chính, công tác sinh viên, tốt nghiệp.

## LỆNH ĐÃ CHẠY

```powershell
git status -sb
python -c "from pathlib import Path; files=[p for p in Path('.').rglob('*.py') if '.venv' not in p.parts and '__pycache__' not in p.parts]; [compile(p.read_text(encoding='utf-8'), str(p), 'exec') for p in files]; print('syntax ok', len(files))"
python -c "from app import create_app; app=create_app('testing'); client=app.test_client(); response=client.get('/health'); print(response.status_code, response.get_json())"
python -c "from app import create_app; app=create_app('testing'); client=app.test_client(); print(client.get('/').status_code)"
python -m pytest -p no:cacheprovider tests/test_health.py
```

## TEST

- PASS: Flask app import và khởi tạo bằng application factory.
- PASS: Healthcheck `/health` trả về JSON `status=ok`.
- PASS: Layout Bootstrap cơ bản render được qua trang `/`.
- PASS: Các blueprint nền được đăng ký.
- PASS: `tests/test_health.py` chạy thành công.

## RỦI RO CÒN LẠI

- Chưa có model SQLAlchemy nghiệp vụ.
- Chưa có migration PostgreSQL.
- Chưa chuyển service/DAO desktop sang repository web.
- Docker Compose mới là khung nền, chưa kiểm thử container ở Giai đoạn 1.

## TIÊU CHÍ HOÀN THÀNH

- Đạt: Flask app khởi động được.
- Đạt: Có trang healthcheck.
- Đạt: Có layout Bootstrap cơ bản.
- Đạt: Web app không phụ thuộc CustomTkinter.
- Đạt: Chưa gom ứng dụng vào một file.
- Đạt: Chưa chuyển toàn bộ module ngoài phạm vi Giai đoạn 1.

## COMMIT

Commit Giai đoạn 1 được thực hiện trên branch `cloud-deployment`.

## BƯỚC TIẾP THEO

Giai đoạn tiếp theo sẽ bắt đầu chuyển đổi dữ liệu/nghiệp vụ cốt lõi sang web theo từng module, ưu tiên cấu trúc database PostgreSQL và migration.
