# HSMS — Hệ thống Quản lý Học sinh

Ứng dụng desktop Python theo mô hình **3 lớp** (UI → Service/BO → DAO → SQLite), kế thừa yêu cầu BTTH02–04.

## Công nghệ

- **Python 3.10+**
- **CustomTkinter** — giao diện desktop hiện đại (không WinForms)
- **SQLite** (`sqlite3` stdlib)
- **Matplotlib** — biểu đồ thống kê trên Dashboard

## Cấu trúc

```
main.py                 # Entry point
config.py               # Cấu hình
database/init_db.sql    # Schema + dữ liệu mẫu
models/                 # DTO (HocSinhInfo, LopInfo, GiaoVienInfo)
dao/                    # Data Access Layer
services/               # Business Layer
ui/                     # Presentation Layer
data/hsms.db            # SQLite (tự tạo khi chạy)
```

## Cài đặt & chạy

```powershell
cd d:\VisualStudioCode\Projects\HSMS
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

## Chức năng

| Module | Mô tả |
|--------|--------|
| **Học sinh** | CRUD, lọc theo lớp, tìm kiếm, chọn dòng → sửa |
| **Lớp học** | CRUD, hiển thị số HS, chặn xóa lớp còn học sinh |
| **Giáo viên** | Mở rộng BTTH04 — CRUD đầy đủ, lọc trạng thái |
| **Dashboard** | Thống kê + 4 biểu đồ (HS/lớp, điểm TB, giới tính, môn dạy) |
| **Theme** | Chuyển sáng/tối |

## Kiến trúc 3 lớp

| PDF (C#) | Project (Python) |
|----------|------------------|
| HocSinhInfo | `models/hoc_sinh.py` |
| DAOHocSinh | `dao/hoc_sinh_dao.py` |
| BOHocSinh | `services/hoc_sinh_service.py` |
| Form | `ui/views/*.py` |

## BTTH05 - Cau hinh CSDL va tai su dung DAO

- Thay doi ket noi CSDL trong `database_config.ini`, khong can sua code Python.
- `dao/db_provider.py` tao connection theo provider hien tai.
- `dao/data_layer.py` gom cac thao tac dung chung: `fetch_all`, `fetch_one`, `scalar`, `execute_non_query`.
- Cac DAO `hoc_sinh_dao`, `lop_dao`, `giao_vien_dao`, `activity_dao` giu nguyen API cu nhung dung `DataLayer` de giam lap lai logic truy cap du lieu.
