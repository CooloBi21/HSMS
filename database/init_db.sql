PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS LOP (
    MaLop   TEXT PRIMARY KEY,
    TenLop  TEXT NOT NULL,
    Khoi    TEXT
);

CREATE INDEX IF NOT EXISTS IDX_LOP_KHOI ON LOP(Khoi);

CREATE TABLE IF NOT EXISTS HOCSINH (
    MaHS      TEXT PRIMARY KEY,
    HoTen     TEXT NOT NULL,
    GioiTinh  INTEGER,
    NgaySinh  TEXT,
    DiaChi    TEXT,
    DiemTB    REAL,
    MaLop     TEXT,
    FOREIGN KEY (MaLop) REFERENCES LOP(MaLop) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS IDX_HOCSINH_MALOP ON HOCSINH(MaLop);

CREATE TABLE IF NOT EXISTS GIAOVIEN (
    TeacherID   TEXT PRIMARY KEY,
    TeacherCode TEXT NOT NULL UNIQUE,
    FullName    TEXT NOT NULL,
    Gender      INTEGER,
    DOB         TEXT,
    Phone       TEXT,
    Email       TEXT,
    Address     TEXT,
    Subject     TEXT,
    Status      TEXT
);

CREATE INDEX IF NOT EXISTS IDX_GIAOVIEN_SUBJECT ON GIAOVIEN(Subject);

CREATE TABLE IF NOT EXISTS ACTIVITY_LOG (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    CreatedAt TEXT DEFAULT (datetime('now', 'localtime')),
    Action TEXT NOT NULL,
    Detail TEXT NOT NULL
);

INSERT OR IGNORE INTO LOP (MaLop, TenLop, Khoi) VALUES
    ('C01', 'Lớp 10A1', '10'),
    ('C02', 'Lớp 10A2', '10'),
    ('C03', 'Lớp 11B1', '11'),
    ('C04', 'Lớp 11B2', '11'),
    ('C05', 'Lớp 12C1', '12'),
    ('C06', 'Lớp 12C2', '12');

INSERT OR IGNORE INTO HOCSINH (MaHS, HoTen, GioiTinh, NgaySinh, DiaChi, DiemTB, MaLop) VALUES
    ('S001', 'Nguyễn Văn An', 1, '2008-05-10', '123 Nguyễn Trãi, Hà Nội', 8.5, 'C01'),
    ('S002', 'Trần Thị Bình', 0, '2008-08-20', '456 Lê Lợi, TP.HCM', 9.0, 'C02'),
    ('S003', 'Phạm Minh Châu', 1, '2008-03-15', '789 Hoàng Văn Thụ, Đà Nẵng', 7.8, 'C01'),
    ('S004', 'Vũ Thị Dương', 0, '2008-11-08', '321 Tôn Đức Thắng, Hà Nội', 8.2, 'C02'),
    ('S005', 'Lê Xuân Đạt', 1, '2008-01-25', '654 Nguyễn Huệ, TP.HCM', 8.8, 'C01'),
    ('S006', 'Hoàng Thị Gia', 0, '2008-06-12', '987 Trần Phú, Hải Phòng', 9.2, 'C03'),
    ('S007', 'Đặng Văn Hùng', 1, '2007-09-18', '147 Lý Thái Tổ, Hà Nội', 7.5, 'C03'),
    ('S008', 'Bùi Thị Hương', 0, '2008-04-22', '258 Cầu Giấy, Hà Nội', 8.9, 'C04'),
    ('S009', 'Trịnh Xuân Ích', 1, '2007-12-05', '369 Tân Kỳ Tân Quý, TP.HCM', 8.1, 'C04'),
    ('S010', 'Ngô Thị Khánh', 0, '2008-07-30', '741 Lê Văn Lương, Hà Nội', 8.6, 'C05'),
    ('S011', 'Tô Văn Linh', 1, '2007-02-14', '852 Hoàng Mai, Hà Nội', 7.9, 'C05'),
    ('S012', 'Cao Thị Mỹ', 0, '2008-10-03', '963 Quang Trung, TP.HCM', 9.1, 'C06'),
    ('S013', 'Mạc Văn Nam', 1, '2007-08-28', '159 Ngô Gia Tự, Hải Phòng', 8.3, 'C06'),
    ('S014', 'Vương Thị Oanh', 0, '2008-05-11', '357 Thái Hà, Hà Nội', 8.7, 'C02'),
    ('S015', 'Sơn Văn Phương', 1, '2008-09-07', '468 Bà Triệu, Hà Nội', 8.4, 'C01');

INSERT OR IGNORE INTO GIAOVIEN (TeacherID, TeacherCode, FullName, Gender, DOB, Phone, Email, Address, Subject, Status) VALUES
    ('T001', 'GV001', 'Lê Thị Hương', 0, '1985-03-15', '0912345678', 'huong@school.edu.vn', 'Hà Nội', 'Toán', 'Active'),
    ('T002', 'GV002', 'Nguyễn Văn Bình', 1, '1980-07-02', '0987654321', 'binh@school.edu.vn', 'TP.HCM', 'Tiếng Anh', 'Active'),
    ('T003', 'GV003', 'Phạm Thị Cẩm', 0, '1988-11-22', '0934567890', 'cam@school.edu.vn', 'Đà Nẵng', 'Vật lý', 'Active'),
    ('T004', 'GV004', 'Trần Minh Đức', 1, '1982-05-30', '0923456789', 'duc@school.edu.vn', 'Hà Nội', 'Hóa học', 'Active'),
    ('T005', 'GV005', 'Vũ Thị Erano', 0, '1990-01-12', '0945678901', 'era@school.edu.vn', 'TP.HCM', 'Sinh học', 'Active'),
    ('T006', 'GV006', 'Hoàng Văn Phúc', 1, '1983-08-18', '0956789012', 'phuc@school.edu.vn', 'Hải Phòng', 'Lịch sử', 'Active'),
    ('T007', 'GV007', 'Đặng Thị Giang', 0, '1987-04-25', '0967890123', 'giang@school.edu.vn', 'Hà Nội', 'Địa lý', 'Active'),
    ('T008', 'GV008', 'Bùi Văn Hải', 1, '1981-09-09', '0978901234', 'hai@school.edu.vn', 'TP.HCM', 'Tin học', 'Inactive');
