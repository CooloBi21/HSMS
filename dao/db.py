from pathlib import Path

from config import DATA_DIR, DB_SETTINGS, INIT_SQL
from dao.db_provider import create_connection

BTTH06_REQUIREMENTS = [
    ("ADM01", "Tuyen sinh & Nhap hoc", "Tiep nhan ho so", "Nhap thong tin dang ky xet tuyen truc tuyen hoac truc tiep.", "Planned", "Admissions"),
    ("ADM02", "Tuyen sinh & Nhap hoc", "Xet tuyen tu dong", "Sang loc va phe duyet danh sach trung tuyen theo tieu chi cai dat san.", "Planned", "Admissions"),
    ("ADM03", "Tuyen sinh & Nhap hoc", "Cap ma so HSSV", "Tu dong tao ma dinh danh duy nhat cho hoc sinh, sinh vien moi.", "Implemented", "Students"),
    ("ADM04", "Tuyen sinh & Nhap hoc", "Phan lop/phan nganh", "Xep HSSV vao lop sinh hoat, khoi nganh hoac chuyen nganh cu the.", "Partial", "Classes"),
    ("PRO01", "Ho so & Thong tin ca nhan", "Cap nhat ly lich", "Luu tru thong tin ca nhan, ho khau, lien lac phu huynh.", "Partial", "Students"),
    ("PRO02", "Ho so & Thong tin ca nhan", "Quan ly trang thai", "Theo doi Dang hoc, Bao luu, Thoi hoc, Tot nghiep.", "Planned", "Students"),
    ("PRO03", "Ho so & Thong tin ca nhan", "Khen thuong/Ky luat", "Ghi nhan quyet dinh tuyen duong hoac xu ly vi pham.", "Planned", "Student affairs"),
    ("PRO04", "Ho so & Thong tin ca nhan", "Dien chinh sach", "Phan loai mien giam hoc phi, ho ngheo, vung sau vung xa.", "Planned", "Student affairs"),
    ("TRN01", "Dao tao & Xep lich", "Khung chuong trinh", "Thiet ke tien trinh hoc tap, mon tien quyet theo khoa.", "Planned", "Training"),
    ("TRN02", "Dao tao & Xep lich", "Dang ky hoc phan", "Sinh vien chon mon hoc, lop hoc va giang vien.", "Planned", "Training"),
    ("TRN03", "Dao tao & Xep lich", "Xep thoi khoa bieu", "Sap xep lich hoc, phong hoc de tranh trung lich.", "Planned", "Scheduling"),
    ("TRN04", "Dao tao & Xep lich", "Diem danh & Chuyen can", "Ghi nhan nghi hoc, di muon hang ngay.", "Planned", "Attendance"),
    ("EXM01", "Khao thi & Diem so", "Lap lich thi", "Chia ca thi, xep phong thi va so bao danh.", "Planned", "Exams"),
    ("EXM02", "Khao thi & Diem so", "Nhap & Quan ly diem", "Cap nhat diem thanh phan, giua ky va cuoi ky.", "Partial", "Students"),
    ("EXM03", "Khao thi & Diem so", "Tinh diem trung binh", "Quy doi va tinh GPA theo thang 4 hoac 10.", "Partial", "Dashboard"),
    ("EXM04", "Khao thi & Diem so", "Xet dieu kien thi", "Khoa quyen du thi neu khong du chuyen can hoac hoc phi.", "Planned", "Exams"),
    ("EXM05", "Khao thi & Diem so", "Phuc khao", "Tiep nhan yeu cau phuc khao va cap nhat diem.", "Planned", "Exams"),
    ("FIN01", "Tai chinh & Hoc phi", "Tinh toan hoc phi", "Lap hoa don dua tren tin chi hoac muc thu co dinh.", "Planned", "Finance"),
    ("FIN02", "Tai chinh & Hoc phi", "Thu phi truc tuyen", "Tich hop cong thanh toan ngan hang, vi dien tu.", "Planned", "Finance"),
    ("FIN03", "Tai chinh & Hoc phi", "Quan ly cong no", "Theo doi HSSV chua hoan thanh nghia vu tai chinh.", "Planned", "Finance"),
    ("FIN04", "Tai chinh & Hoc phi", "Xet duyet hoc bong", "Quet diem so va ren luyen de cap hoc bong.", "Planned", "Scholarship"),
    ("STU01", "Cong tac sinh vien & Ngoai khoa", "Diem ren luyen", "Cham diem y thuc, dao duc theo ky.", "Planned", "Student affairs"),
    ("STU02", "Cong tac sinh vien & Ngoai khoa", "Ky tuc xa", "Sap xep phong o, quan ly dien nuoc va luu tru.", "Planned", "Dormitory"),
    ("STU03", "Cong tac sinh vien & Ngoai khoa", "Hoat dong ngoai khoa", "Ghi nhan tham gia CLB, chien dich tinh nguyen.", "Planned", "Activities"),
    ("STU04", "Cong tac sinh vien & Ngoai khoa", "Y te hoc duong", "Luu lich su kham suc khoe va bao hiem y te.", "Planned", "Health"),
    ("GRD01", "Tot nghiep & Bao cao", "Xet dieu kien tot nghiep", "Kiem tra chung chi dau ra va tich luy tin chi.", "Planned", "Graduation"),
    ("GRD02", "Tot nghiep & Bao cao", "Cap phat van bang", "Quan ly so goc, so hieu bang va phoi bang.", "Planned", "Graduation"),
    ("GRD03", "Tot nghiep & Bao cao", "Xuat bang diem/Giay chung nhan", "In bang diem toan khoa va giay xac nhan HSSV.", "Planned", "Reports"),
    ("GRD04", "Tot nghiep & Bao cao", "Bao cao thong ke", "Thong ke EMIS, hoc luc, thoi hoc.", "Partial", "Dashboard"),
    ("GRD05", "Tot nghiep & Bao cao", "Viec lam cuu sinh vien", "Khao sat tinh trang viec lam sau khi ra truong.", "Planned", "Alumni"),
]


def _ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_connection():
    return create_connection()


def init_database() -> None:
    if DB_SETTINGS["provider"] != "sqlite":
        return

    _ensure_data_dir()
    if not INIT_SQL.exists():
        raise FileNotFoundError(f"Missing init script: {INIT_SQL}")

    sql = INIT_SQL.read_text(encoding="utf-8")
    with get_connection() as conn:
        conn.executescript(sql)
        conn.commit()


def init_database_if_needed() -> None:
    if DB_SETTINGS["provider"] != "sqlite":
        return

    _ensure_data_dir()
    db_file = Path(DB_SETTINGS["connection_string"])
    if not db_file.exists():
        init_database()
    else:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='HOCSINH'"
            ).fetchone()
            if not row:
                init_database()
    _ensure_migrations()


def _ensure_migrations() -> None:
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ACTIVITY_LOG (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                CreatedAt TEXT DEFAULT (datetime('now', 'localtime')),
                Action TEXT NOT NULL,
                Detail TEXT NOT NULL
            )
        """)
        conn.commit()
        # Xóa dữ liệu demo cũ (seed tĩnh) nếu còn
        conn.execute("""
            DELETE FROM ACTIVITY_LOG WHERE Detail IN (
                'Thêm học sinh Nguyễn Văn An vào lớp 10A1',
                'Nhập điểm TB cho lớp 10A1',
                'Cập nhật thông tin lớp 11B2',
                'Thêm giáo viên Lê Thị Hương — môn Toán'
            )
        """)
        conn.commit()
        _ensure_btth06_schema(conn)
        _seed_btth06_requirements(conn)


def _ensure_btth06_schema(conn) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS BTTH06_REQUIREMENT (
            Code TEXT PRIMARY KEY,
            GroupName TEXT NOT NULL,
            Title TEXT NOT NULL,
            Description TEXT,
            Status TEXT NOT NULL,
            ModuleHint TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS BTTH06_RECORD (
            RecordID TEXT PRIMARY KEY,
            RequirementCode TEXT NOT NULL,
            StudentCode TEXT,
            Title TEXT NOT NULL,
            Status TEXT NOT NULL,
            EventDate TEXT,
            NumericValue REAL,
            Amount REAL,
            Notes TEXT,
            CreatedAt TEXT DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (RequirementCode) REFERENCES BTTH06_REQUIREMENT(Code) ON DELETE CASCADE
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS IDX_BTTH06_RECORD_REQ ON BTTH06_RECORD(RequirementCode)")
    conn.execute("CREATE INDEX IF NOT EXISTS IDX_BTTH06_RECORD_STATUS ON BTTH06_RECORD(Status)")
    conn.commit()


def _seed_btth06_requirements(conn) -> None:
    conn.executemany(
        """INSERT OR IGNORE INTO BTTH06_REQUIREMENT
           (Code, GroupName, Title, Description, Status, ModuleHint)
           VALUES (?, ?, ?, ?, ?, ?)""",
        BTTH06_REQUIREMENTS,
    )
    conn.commit()
