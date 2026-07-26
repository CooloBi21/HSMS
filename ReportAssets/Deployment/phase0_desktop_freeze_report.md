# GIAI ĐOẠN 0: Khảo sát, đóng băng bản desktop và chuẩn bị nhánh cloud

## MỤC TIÊU

Giai đoạn 0 dùng để kiểm tra hiện trạng dự án HSMS trước khi chuyển đổi sang web/cloud, đồng thời tạo mốc khôi phục an toàn cho bản desktop hiện tại. Giai đoạn này không thay đổi DNS, không tạo Cloudflare Tunnel mới và không chỉnh sửa `my-todo-tunnel`.

## HIỆN TRẠNG ĐÃ KIỂM TRA

- Branch ban đầu: `main`
- Commit desktop hiện tại: `0404f7f Complete BTTH06 HSMS workflows and evidence`
- Working tree trước khi tạo nhánh: sạch
- Remote GitHub: `https://github.com/CooloBi21/HSMS.git`
- Entry point: `main.py`
- App desktop chính: `ui/app.py`
- Cấu hình CSDL: `database_config.ini`
- Provider/DataLayer: `dao/db_provider.py`, `dao/data_layer.py`
- Schema SQLite nền: `database/init_db.sql`
- Model: `models/`
- Service: `services/`
- DAO: `dao/`
- UI desktop: `ui/views/`, `ui/components/`
- Minh chứng/báo cáo cũ: `ReportAssets/`

## FILE ĐÃ TẠO

- `ReportAssets/Deployment/phase0_desktop_freeze_report.md`

## FILE ĐÃ SỬA

- `README.md`

## CODE CŨ ĐÃ TÁI SỬ DỤNG

- `models/`: có thể tái sử dụng ý nghĩa nghiệp vụ và cấu trúc dữ liệu khi thiết kế ORM web.
- `services/`: có thể tái sử dụng quy tắc nghiệp vụ, kiểm tra dữ liệu, luồng thao tác.
- `dao/data_layer.py`: là cơ sở tham chiếu cho lớp truy cập dữ liệu dùng chung.
- `dao/db_provider.py`: là cơ sở tham chiếu cho tư tưởng tách provider kết nối.
- `database/init_db.sql`: là cơ sở đọc schema hiện có, nhưng cần thay thế bằng migration PostgreSQL cho web.
- `ui/views/`: không tái sử dụng trực tiếp cho web, nhưng dùng để đối chiếu nghiệp vụ và luồng màn hình.
- `ReportAssets/`: giữ nguyên làm minh chứng báo cáo các giai đoạn trước.

## PHẦN BẮT BUỘC THAY THẾ KHI LÊN WEB

- CustomTkinter UI sẽ được thay bằng Flask route, Jinja template và Bootstrap.
- SQLite local sẽ được thay bằng PostgreSQL trong Docker.
- DAO SQL trực tiếp cần được chuyển sang SQLAlchemy model/repository hoặc service tương thích PostgreSQL.
- `database/init_db.sql` chỉ phù hợp SQLite nền, không dùng làm script triển khai PostgreSQL chính thức.
- Cơ chế đăng nhập desktop cần chuyển sang Flask-Login/session cho web.

## LỆNH ĐÃ CHẠY

```powershell
git branch --show-current
git status -sb
git log --oneline --decorate -5
rg --files
$env:PYTHONDONTWRITEBYTECODE='1'; python -c "from pathlib import Path; files=[p for p in Path('.').rglob('*.py') if '.venv' not in p.parts and '__pycache__' not in p.parts]; [compile(p.read_text(encoding='utf-8'), str(p), 'exec') for p in files]; print('syntax ok', len(files))"
python -c "from ui.app import HSMSApp; print('app import ok')"
$env:PYTHONDONTWRITEBYTECODE='1'; python -c "from dao.db import init_database_if_needed; init_database_if_needed(); from ui.app import HSMSApp; app=HSMSApp(); app.update_idletasks(); app.update(); print('desktop window ok', app.winfo_width(), app.winfo_height()); app.quit(); app.destroy()"
git tag desktop-v1.0
git branch desktop-final
git switch -c cloud-deployment
```

## TEST

- PASS: 77 file Python compile cú pháp thành công.
- PASS: Import `HSMSApp` thành công.
- PASS: Desktop app khởi tạo cửa sổ thành công với kích thước `1600x1000`.
- PASS: Tạo tag `desktop-v1.0`.
- PASS: Tạo branch `desktop-final`.
- PASS: Tạo và chuyển sang branch `cloud-deployment`.
- FAIL: Chưa có lỗi runtime desktop được ghi nhận trong Giai đoạn 0.

## RỦI RO CÒN LẠI

- README và một số file tiếng Việt có thể hiển thị sai dấu nếu console Windows không dùng UTF-8, nhưng nội dung file vẫn được đọc bằng UTF-8 trong Python.
- Schema web chưa có PostgreSQL migration.
- Docker, Nginx, Cloudflare Tunnel và Cloudflare Access chưa thực hiện ở Giai đoạn 0.

## TIÊU CHÍ HOÀN THÀNH

- Đạt: Desktop hiện tại vẫn chạy.
- Đạt: Có tag khôi phục `desktop-v1.0`.
- Đạt: Có branch ổn định `desktop-final`.
- Đạt: Có branch triển khai `cloud-deployment`.
- Đạt: Có báo cáo liệt kê phần tái sử dụng và phần cần thay thế.

## COMMIT

Commit tài liệu Giai đoạn 0 được thực hiện trên branch `cloud-deployment`.

## BƯỚC TIẾP THEO

Sau khi push mốc Giai đoạn 0, bắt đầu Giai đoạn xây dựng HSMS Web trên branch `cloud-deployment`.
