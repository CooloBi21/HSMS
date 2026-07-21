# HSMS - He thong Quan ly Hoc sinh

HSMS la ung dung desktop Python dung de quan ly hoc sinh, lop hoc, giao vien, dashboard thong ke va theo doi nghiep vu tong hop. Du an duoc phat trien ke thua qua nhieu bai thuc hanh:

- BTTH02: thiet ke co so du lieu va CRUD hoc sinh/lop.
- BTTH03: tach model va xu ly form ro rang hon.
- BTTH04: mo rong thanh kien truc 3 lop.
- BTTH05: tach cau hinh CSDL, them provider/factory va `DataLayer` dung chung.
- BTTH06: tong hop 30 yeu cau nghiep vu cot loi, doi chieu hien trang va bo sung module quan ly nghiep vu tong hop.

## Cong nghe

- Python 3.10+
- CustomTkinter cho giao dien desktop
- SQLite mac dinh
- Matplotlib cho bieu do dashboard
- ODBC/pyodbc o muc kien truc mo rong cho SQL Server, Access, Oracle

## Cau truc du an

```text
main.py                      Entry point
config.py                    Cau hinh ung dung va doc database_config.ini
database_config.ini           Provider va connection string ben ngoai code
database/init_db.sql          Schema SQLite va du lieu mau
models/                      Dataclass/DTO
dao/                         Data Access Layer
services/                    Business Layer
ui/                          Presentation Layer
ReportAssets/                Tai lieu va anh minh chung theo bai thuc hanh
```

## Kien truc

Ung dung di theo kien truc phan tang:

```text
UI
  -> Services / Business Layer
    -> DAO
      -> DataLayer
        -> db_provider
          -> SQLite hoac ODBC provider
```

UI khong viet SQL va khong tao connection truc tiep. Service kiem tra nghiep vu, dieu phoi DAO va ghi activity log. DAO chua cau SQL theo tung doi tuong va tai su dung `DataLayer`.

## Chuc nang hien co

| Module | Chuc nang |
|--------|-----------|
| Dashboard | KPI tong quan, bieu do hoc sinh/lop, diem trung binh, phan loai hoc luc, canh bao |
| Hoc sinh | CRUD, tim kiem, loc theo lop, sinh ma hoc sinh, nhap diem trung binh |
| Lop hoc | CRUD, loc theo khoi, theo doi si so, chan xoa lop con hoc sinh |
| Giao vien | CRUD, loc trang thai, loc mon phu trach, kiem tra email/so dien thoai |
| Nghiep vu BTTH06 | Doi chieu 30 yeu cau, loc theo nhom/trang thai, tao/sua/xoa ho so nghiep vu lien quan |
| Activity log | Ghi nhan thao tac them/sua/xoa gan day |
| Cau hinh CSDL | Doi provider va connection string trong `database_config.ini` |

## BTTH05 - Tang du lieu linh hoat

BTTH05 tap trung vao viec tach thong tin ket noi khoi ma nguon va tang kha nang tai su dung tang DAO.

File chinh:

- `database_config.ini`: luu `provider` va `connection_string`.
- `config.py`: doc cau hinh CSDL bang `configparser`.
- `dao/db_provider.py`: tao connection theo provider hien tai.
- `dao/data_layer.py`: gom cac thao tac dung chung nhu `execute_non_query`, `fetch_all`, `fetch_one`, `scalar`.
- `dao/*_dao.py`: cac DAO hoc sinh, lop, giao vien, activity dung lai `DataLayer`.

He thong duoc thiet ke de co the mo rong sang SQL Server, Access va Oracle thong qua ODBC. Trong pham vi hien tai, ung dung da duoc kiem chung chay thuc te voi SQLite.

## BTTH06 - Tong hop nghiep vu

BTTH06 doi chieu 30 yeu cau nghiep vu cot loi voi he thong hien co va bo sung module `Nghiep vu` trong app.

Tai lieu phan tich nam tai:

```text
ReportAssets/BTTH06/BTTH06_requirements_mapping.md
```

Phan code bo sung:

- `models/btth06.py`: model yeu cau va ho so nghiep vu.
- `dao/btth06_dao.py`: truy van danh sach 30 yeu cau va CRUD ho so nghiep vu.
- `services/btth06_service.py`: validate nghiep vu, sinh ma ho so, ghi activity log.
- `ui/views/business_view.py`: man hinh tong hop BTTH06.
- `dao/db.py`: migration tao `BTTH06_REQUIREMENT` va `BTTH06_RECORD`.

Module BTTH06 khong thay the cac module nghiep vu lon nhu hoc phi online, ky tuc xa hay van bang. No dong vai tro lop tong hop de quan ly, theo doi va minh chung xu ly 30 yeu cau trong pham vi du an hien tai.

## Cai dat va chay

```powershell
cd D:\VisualStudioCode\Projects\HSMS
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

Database SQLite local duoc tao trong `data/hsms.db` khi chay ung dung. File nay duoc giu local va khong push len GitHub.

## Ghi chu phat trien

- Khong commit `.venv`, `__pycache__`, database local hoac PDF de bai.
- Khi them nghiep vu moi, giu dung kien truc: `models -> dao -> services -> ui`.
- Neu dung SQL Server/Access/Oracle, can cai them `pyodbc`, driver tuong ung va schema phu hop voi he CSDL do.
