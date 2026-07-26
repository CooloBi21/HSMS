# Phase 8 - Docker hóa HSMS Web

## Mục tiêu

Phase 8 đóng gói HSMS Web thành hệ thống container có thể chạy trong VM, sử dụng PostgreSQL, Nginx reverse proxy, Cloudflare Tunnel và backup định kỳ. Phần này chỉ xử lý triển khai web, không thay đổi nghiệp vụ học sinh/lớp/giáo viên/tuyển sinh/hồ sơ đã làm trước đó.

## Luồng container đã thiết kế

```text
cloudflared
  -> nginx:80
    -> hsms-web:8000
      -> postgres:5432
```

Các kết nối nội bộ dùng Docker service name:

- Nginx proxy đến `hsms-web:8000`.
- HSMS Web kết nối PostgreSQL qua `postgres:5432`.
- Cloudflare Public Hostname cần trỏ origin về `http://nginx:80`.

Không dùng sai kiểu `localhost` giữa container, vì `localhost` bên trong mỗi container chỉ là chính container đó.

## Service đã cấu hình

### hsms-web

- Build từ `Dockerfile`.
- Chạy Flask app bằng Gunicorn trên port `8000`.
- Không dùng Flask development server trong production.
- Chạy bằng user `hsms`, không chạy root.
- Đọc secret qua `.env`, không hard-code trong image.
- Có healthcheck gọi `/health`.
- Entrypoint chạy migration trước khi start app.
- Seed admin nếu có `ADMIN_USERNAME` và `ADMIN_PASSWORD`.

### postgres

- Dùng image `postgres:16-alpine`.
- Dùng named volume `postgres_data`.
- Không publish port `5432` ra host hoặc Internet.
- Chỉ nằm trong private network `hsms-private`.
- Có healthcheck bằng `pg_isready`.

### nginx

- Dùng image `nginx:1.27-alpine`.
- Reverse proxy đến `hsms-web:8000`.
- Chuyển proxy headers: `Host`, `X-Real-IP`, `X-Forwarded-For`, `X-Forwarded-Proto`, `X-Forwarded-Host`.
- Giới hạn upload `10m`.
- Timeout proxy hợp lý.
- Tắt `server_tokens`.
- Publish nội bộ VM qua `127.0.0.1:8080:80` để kiểm tra local, không mở trực tiếp ra Internet.

### cloudflared

- Dùng image `cloudflare/cloudflared`.
- Token đọc từ biến `CLOUDFLARE_TUNNEL_TOKEN` trong `.env`.
- Không commit token.
- `restart: unless-stopped`.
- Cần cấu hình Public Hostname trên Cloudflare trỏ service về `http://nginx:80`.

### backup

- Dùng `pg_dump`.
- Chạy theo vòng lặp định kỳ bằng `BACKUP_INTERVAL_SECONDS`.
- Lưu file vào thư mục `backups/` ngoài container PostgreSQL.
- Xóa backup cũ theo `BACKUP_RETENTION_DAYS`.
- Không commit file backup.

## File đã thêm hoặc chỉnh

- `Dockerfile`
- `docker-compose.yml`
- `.dockerignore`
- `.gitattributes`
- `.env.example`
- `.gitignore`
- `gunicorn.conf.py`
- `docker/entrypoint.sh`
- `docker/backup-postgres.sh`
- `nginx/hsms.conf`
- `app/__init__.py`
- `README.md`

## Cách chạy dự kiến trên VM

1. Tạo file `.env` từ `.env.example`.
2. Điền `SECRET_KEY`, `POSTGRES_PASSWORD`, `ADMIN_PASSWORD`, `CLOUDFLARE_TUNNEL_TOKEN`.
3. Build và chạy:

```bash
docker compose up -d --build
```

4. Kiểm tra container:

```bash
docker compose ps
```

5. Kiểm tra nội bộ VM:

```bash
curl http://127.0.0.1:8080/health
```

## Phần cần user thực hiện trên VM/Cloudflare

Các phần dưới đây cần credential, domain, thiết bị và mạng thật nên agent không tự xác minh đầy đủ trong repo:

- Tạo tunnel thật `hsms-vm-tunnel`.
- Lấy và điền `CLOUDFLARE_TUNNEL_TOKEN` vào `.env`.
- Thêm Public Hostname `hsms.coolobi.id.vn`.
- Cấu hình origin/service của hostname là `http://nginx:80`.
- Bật Cloudflare Access theo chính sách mong muốn.
- Kiểm tra truy cập bằng điện thoại dùng 4G/5G.
- Kiểm tra log Cloudflare Zero Trust nếu tunnel không lên.

## Lưu ý bảo mật

Các file và dữ liệu sau không được commit:

- `.env`
- Tunnel token
- Cloudflare credential
- PostgreSQL data
- Backup database
- Database local
- Secret key
- Log nhạy cảm

Repo đã bổ sung `.dockerignore` và `.gitignore` để giảm nguy cơ đưa nhầm dữ liệu nhạy cảm vào Git hoặc Docker image.
