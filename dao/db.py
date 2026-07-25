from pathlib import Path

from config import DATA_DIR, DB_SETTINGS, INIT_SQL
from dao.db_provider import create_connection


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
        _remove_btth06_aggregate_schema(conn)
        _ensure_admission_schema(conn)
        _ensure_student_profile_schema(conn)
        _ensure_training_schema(conn)
        _ensure_exam_schema(conn)
        _ensure_finance_schema(conn)
        _ensure_student_affairs_schema(conn)
        _ensure_graduation_schema(conn)
        _ensure_account_schema(conn)


def _remove_btth06_aggregate_schema(conn) -> None:
    conn.execute("DROP TABLE IF EXISTS BTTH06_RECORD")
    conn.execute("DROP TABLE IF EXISTS BTTH06_REQUIREMENT")
    conn.commit()


def _ensure_admission_schema(conn) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS ADMISSION_APPLICATION (
            ApplicationID TEXT PRIMARY KEY,
            FullName TEXT NOT NULL,
            Gender INTEGER,
            DOB TEXT,
            Address TEXT,
            Phone TEXT,
            ParentName TEXT,
            ParentPhone TEXT,
            AdmissionScore REAL,
            DesiredClass TEXT,
            DesiredMajor TEXT,
            Status TEXT NOT NULL,
            StudentCode TEXT,
            Notes TEXT,
            CreatedAt TEXT DEFAULT (datetime('now', 'localtime')),
            UpdatedAt TEXT,
            FOREIGN KEY (DesiredClass) REFERENCES LOP(MaLop) ON DELETE SET NULL,
            FOREIGN KEY (StudentCode) REFERENCES HOCSINH(MaHS) ON DELETE SET NULL
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS IDX_ADMISSION_STATUS ON ADMISSION_APPLICATION(Status)")
    conn.execute("CREATE INDEX IF NOT EXISTS IDX_ADMISSION_CLASS ON ADMISSION_APPLICATION(DesiredClass)")
    conn.commit()


def _ensure_student_profile_schema(conn) -> None:
    existing_columns = {
        row[1] for row in conn.execute("PRAGMA table_info(HOCSINH)").fetchall()
    }
    columns = {
        "HoKhau": "TEXT",
        "ParentName": "TEXT",
        "ParentPhone": "TEXT",
        "LearningStatus": "TEXT DEFAULT 'Đang học'",
        "PolicyType": "TEXT",
    }
    for column_name, column_type in columns.items():
        if column_name not in existing_columns:
            conn.execute(f"ALTER TABLE HOCSINH ADD COLUMN {column_name} {column_type}")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS STUDENT_DECISION (
            DecisionID TEXT PRIMARY KEY,
            MaHS TEXT NOT NULL,
            DecisionType TEXT NOT NULL,
            DecisionDate TEXT NOT NULL,
            Title TEXT NOT NULL,
            Description TEXT,
            Issuer TEXT,
            CreatedAt TEXT DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (MaHS) REFERENCES HOCSINH(MaHS) ON DELETE CASCADE
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS IDX_STUDENT_DECISION_MAHS ON STUDENT_DECISION(MaHS)")
    conn.execute("CREATE INDEX IF NOT EXISTS IDX_STUDENT_DECISION_TYPE ON STUDENT_DECISION(DecisionType)")
    conn.commit()


def _ensure_training_schema(conn) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS COURSE (
            CourseID TEXT PRIMARY KEY,
            CourseName TEXT NOT NULL,
            Credits INTEGER NOT NULL,
            GradeLevel TEXT,
            PrerequisiteID TEXT,
            Description TEXT,
            FOREIGN KEY (PrerequisiteID) REFERENCES COURSE(CourseID) ON DELETE SET NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS CURRICULUM_ITEM (
            ItemID TEXT PRIMARY KEY,
            CourseID TEXT NOT NULL,
            GradeLevel TEXT NOT NULL,
            Semester TEXT NOT NULL,
            SequenceNo INTEGER,
            Notes TEXT,
            FOREIGN KEY (CourseID) REFERENCES COURSE(CourseID) ON DELETE CASCADE
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS COURSE_SECTION (
            SectionID TEXT PRIMARY KEY,
            CourseID TEXT NOT NULL,
            ClassCode TEXT,
            TeacherID TEXT,
            Capacity INTEGER,
            Status TEXT NOT NULL,
            FOREIGN KEY (CourseID) REFERENCES COURSE(CourseID) ON DELETE CASCADE,
            FOREIGN KEY (ClassCode) REFERENCES LOP(MaLop) ON DELETE SET NULL,
            FOREIGN KEY (TeacherID) REFERENCES GIAOVIEN(TeacherID) ON DELETE SET NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS COURSE_REGISTRATION (
            RegistrationID TEXT PRIMARY KEY,
            SectionID TEXT NOT NULL,
            MaHS TEXT NOT NULL,
            Status TEXT NOT NULL,
            RegisteredAt TEXT DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (SectionID) REFERENCES COURSE_SECTION(SectionID) ON DELETE CASCADE,
            FOREIGN KEY (MaHS) REFERENCES HOCSINH(MaHS) ON DELETE CASCADE
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS CLASS_SCHEDULE (
            ScheduleID TEXT PRIMARY KEY,
            SectionID TEXT NOT NULL,
            Weekday TEXT NOT NULL,
            StartPeriod INTEGER NOT NULL,
            EndPeriod INTEGER NOT NULL,
            Room TEXT NOT NULL,
            FOREIGN KEY (SectionID) REFERENCES COURSE_SECTION(SectionID) ON DELETE CASCADE
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS ATTENDANCE_RECORD (
            AttendanceID TEXT PRIMARY KEY,
            SectionID TEXT NOT NULL,
            MaHS TEXT NOT NULL,
            AttendanceDate TEXT NOT NULL,
            Status TEXT NOT NULL,
            Notes TEXT,
            FOREIGN KEY (SectionID) REFERENCES COURSE_SECTION(SectionID) ON DELETE CASCADE,
            FOREIGN KEY (MaHS) REFERENCES HOCSINH(MaHS) ON DELETE CASCADE
        )
    """)
    conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS UQ_COURSE_REGISTRATION ON COURSE_REGISTRATION(SectionID, MaHS)")
    conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS UQ_ATTENDANCE_RECORD ON ATTENDANCE_RECORD(SectionID, MaHS, AttendanceDate)")
    conn.execute("CREATE INDEX IF NOT EXISTS IDX_SECTION_COURSE ON COURSE_SECTION(CourseID)")
    conn.execute("CREATE INDEX IF NOT EXISTS IDX_SCHEDULE_SECTION ON CLASS_SCHEDULE(SectionID)")
    conn.execute("CREATE INDEX IF NOT EXISTS IDX_ATTENDANCE_SECTION ON ATTENDANCE_RECORD(SectionID)")
    conn.commit()


def _ensure_exam_schema(conn) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS EXAM_SCHEDULE (
            ExamID TEXT PRIMARY KEY,
            SectionID TEXT NOT NULL,
            ExamDate TEXT NOT NULL,
            Shift TEXT NOT NULL,
            Room TEXT NOT NULL,
            ExamType TEXT NOT NULL,
            FOREIGN KEY (SectionID) REFERENCES COURSE_SECTION(SectionID) ON DELETE CASCADE
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS EXAM_ELIGIBILITY (
            EligibilityID TEXT PRIMARY KEY,
            ExamID TEXT NOT NULL,
            MaHS TEXT NOT NULL,
            CandidateNo TEXT,
            AttendanceEligible INTEGER NOT NULL DEFAULT 1,
            TuitionEligible INTEGER NOT NULL DEFAULT 1,
            Status TEXT NOT NULL,
            Notes TEXT,
            FOREIGN KEY (ExamID) REFERENCES EXAM_SCHEDULE(ExamID) ON DELETE CASCADE,
            FOREIGN KEY (MaHS) REFERENCES HOCSINH(MaHS) ON DELETE CASCADE
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS GRADE_RECORD (
            GradeID TEXT PRIMARY KEY,
            SectionID TEXT NOT NULL,
            MaHS TEXT NOT NULL,
            ComponentScore REAL,
            MidtermScore REAL,
            FinalScore REAL,
            Average10 REAL,
            GPA4 REAL,
            LetterGrade TEXT,
            UpdatedAt TEXT DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (SectionID) REFERENCES COURSE_SECTION(SectionID) ON DELETE CASCADE,
            FOREIGN KEY (MaHS) REFERENCES HOCSINH(MaHS) ON DELETE CASCADE
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS GRADE_REVIEW (
            ReviewID TEXT PRIMARY KEY,
            GradeID TEXT NOT NULL,
            RequestDate TEXT NOT NULL,
            Reason TEXT NOT NULL,
            Status TEXT NOT NULL,
            AdjustedScore REAL,
            ResolutionNotes TEXT,
            FOREIGN KEY (GradeID) REFERENCES GRADE_RECORD(GradeID) ON DELETE CASCADE
        )
    """)
    conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS UQ_EXAM_ELIGIBILITY ON EXAM_ELIGIBILITY(ExamID, MaHS)")
    conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS UQ_GRADE_RECORD ON GRADE_RECORD(SectionID, MaHS)")
    conn.execute("CREATE INDEX IF NOT EXISTS IDX_EXAM_SECTION ON EXAM_SCHEDULE(SectionID)")
    conn.execute("CREATE INDEX IF NOT EXISTS IDX_GRADE_SECTION ON GRADE_RECORD(SectionID)")
    conn.execute("CREATE INDEX IF NOT EXISTS IDX_REVIEW_STATUS ON GRADE_REVIEW(Status)")
    conn.commit()


def _ensure_finance_schema(conn) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS TUITION_INVOICE (
            InvoiceID TEXT PRIMARY KEY,
            MaHS TEXT NOT NULL,
            Term TEXT NOT NULL,
            InvoiceType TEXT NOT NULL,
            CreditCount INTEGER,
            UnitPrice REAL,
            FixedAmount REAL,
            TotalAmount REAL NOT NULL,
            PaidAmount REAL NOT NULL DEFAULT 0,
            Status TEXT NOT NULL,
            DueDate TEXT,
            Notes TEXT,
            CreatedAt TEXT DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (MaHS) REFERENCES HOCSINH(MaHS) ON DELETE CASCADE
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS PAYMENT_RECORD (
            PaymentID TEXT PRIMARY KEY,
            InvoiceID TEXT NOT NULL,
            PaymentDate TEXT NOT NULL,
            Amount REAL NOT NULL,
            Method TEXT NOT NULL,
            TransactionRef TEXT,
            Notes TEXT,
            FOREIGN KEY (InvoiceID) REFERENCES TUITION_INVOICE(InvoiceID) ON DELETE CASCADE
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS SCHOLARSHIP_REVIEW (
            ScholarshipID TEXT PRIMARY KEY,
            MaHS TEXT NOT NULL,
            Term TEXT NOT NULL,
            GPA4 REAL,
            Average10 REAL,
            ConductScore REAL,
            Amount REAL,
            Status TEXT NOT NULL,
            Notes TEXT,
            CreatedAt TEXT DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (MaHS) REFERENCES HOCSINH(MaHS) ON DELETE CASCADE
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS IDX_TUITION_MAHS ON TUITION_INVOICE(MaHS)")
    conn.execute("CREATE INDEX IF NOT EXISTS IDX_TUITION_STATUS ON TUITION_INVOICE(Status)")
    conn.execute("CREATE INDEX IF NOT EXISTS IDX_PAYMENT_INVOICE ON PAYMENT_RECORD(InvoiceID)")
    conn.execute("CREATE INDEX IF NOT EXISTS IDX_SCHOLARSHIP_STATUS ON SCHOLARSHIP_REVIEW(Status)")
    conn.commit()


def _ensure_student_affairs_schema(conn) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS CONDUCT_SCORE (
            ConductID TEXT PRIMARY KEY,
            MaHS TEXT NOT NULL,
            Term TEXT NOT NULL,
            AwarenessScore REAL,
            DisciplineScore REAL,
            ActivityScore REAL,
            TotalScore REAL NOT NULL,
            Rating TEXT NOT NULL,
            Notes TEXT,
            CreatedAt TEXT DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (MaHS) REFERENCES HOCSINH(MaHS) ON DELETE CASCADE
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS DORM_ASSIGNMENT (
            DormID TEXT PRIMARY KEY,
            MaHS TEXT NOT NULL,
            Building TEXT NOT NULL,
            Room TEXT NOT NULL,
            Bed TEXT,
            StartDate TEXT NOT NULL,
            EndDate TEXT,
            ElectricWaterFee REAL DEFAULT 0,
            Status TEXT NOT NULL,
            Notes TEXT,
            FOREIGN KEY (MaHS) REFERENCES HOCSINH(MaHS) ON DELETE CASCADE
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS EXTRACURRICULAR_ACTIVITY (
            ActivityID TEXT PRIMARY KEY,
            MaHS TEXT NOT NULL,
            ActivityName TEXT NOT NULL,
            ActivityType TEXT NOT NULL,
            JoinDate TEXT NOT NULL,
            Role TEXT,
            Hours REAL DEFAULT 0,
            Status TEXT NOT NULL,
            Notes TEXT,
            FOREIGN KEY (MaHS) REFERENCES HOCSINH(MaHS) ON DELETE CASCADE
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS HEALTH_RECORD (
            HealthID TEXT PRIMARY KEY,
            MaHS TEXT NOT NULL,
            CheckupDate TEXT NOT NULL,
            HeightCm REAL,
            WeightKg REAL,
            HealthStatus TEXT NOT NULL,
            InsuranceNo TEXT,
            InsuranceExpiry TEXT,
            Notes TEXT,
            FOREIGN KEY (MaHS) REFERENCES HOCSINH(MaHS) ON DELETE CASCADE
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS IDX_CONDUCT_MAHS ON CONDUCT_SCORE(MaHS)")
    conn.execute("CREATE INDEX IF NOT EXISTS IDX_DORM_STATUS ON DORM_ASSIGNMENT(Status)")
    conn.execute("CREATE INDEX IF NOT EXISTS IDX_ACTIVITY_MAHS ON EXTRACURRICULAR_ACTIVITY(MaHS)")
    conn.execute("CREATE INDEX IF NOT EXISTS IDX_HEALTH_MAHS ON HEALTH_RECORD(MaHS)")
    conn.commit()


def _ensure_graduation_schema(conn) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS GRADUATION_CHECK (
            CheckID TEXT PRIMARY KEY,
            MaHS TEXT NOT NULL,
            CheckDate TEXT NOT NULL,
            RequiredCredits INTEGER NOT NULL,
            EarnedCredits INTEGER NOT NULL,
            InformaticsCert INTEGER NOT NULL DEFAULT 0,
            LanguageCert INTEGER NOT NULL DEFAULT 0,
            DefenseCert INTEGER NOT NULL DEFAULT 0,
            Status TEXT NOT NULL,
            Notes TEXT,
            FOREIGN KEY (MaHS) REFERENCES HOCSINH(MaHS) ON DELETE CASCADE
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS DIPLOMA_RECORD (
            DiplomaID TEXT PRIMARY KEY,
            MaHS TEXT NOT NULL,
            GraduationCheckID TEXT,
            RegistryNo TEXT NOT NULL,
            DiplomaNo TEXT NOT NULL,
            IssueDate TEXT NOT NULL,
            Status TEXT NOT NULL,
            Notes TEXT,
            FOREIGN KEY (MaHS) REFERENCES HOCSINH(MaHS) ON DELETE CASCADE,
            FOREIGN KEY (GraduationCheckID) REFERENCES GRADUATION_CHECK(CheckID) ON DELETE SET NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS DOCUMENT_REQUEST (
            RequestID TEXT PRIMARY KEY,
            MaHS TEXT NOT NULL,
            DocumentType TEXT NOT NULL,
            RequestDate TEXT NOT NULL,
            Status TEXT NOT NULL,
            OutputPath TEXT,
            Notes TEXT,
            FOREIGN KEY (MaHS) REFERENCES HOCSINH(MaHS) ON DELETE CASCADE
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS ALUMNI_EMPLOYMENT (
            AlumniID TEXT PRIMARY KEY,
            MaHS TEXT NOT NULL,
            SurveyDate TEXT NOT NULL,
            EmploymentStatus TEXT NOT NULL,
            Company TEXT,
            Position TEXT,
            Salary REAL,
            Notes TEXT,
            FOREIGN KEY (MaHS) REFERENCES HOCSINH(MaHS) ON DELETE CASCADE
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS IDX_GRAD_CHECK_MAHS ON GRADUATION_CHECK(MaHS)")
    conn.execute("CREATE INDEX IF NOT EXISTS IDX_DIPLOMA_MAHS ON DIPLOMA_RECORD(MaHS)")
    conn.execute("CREATE INDEX IF NOT EXISTS IDX_DOCUMENT_TYPE ON DOCUMENT_REQUEST(DocumentType)")
    conn.execute("CREATE INDEX IF NOT EXISTS IDX_ALUMNI_STATUS ON ALUMNI_EMPLOYMENT(EmploymentStatus)")
    conn.commit()


def _ensure_account_schema(conn) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS USER_ACCOUNT (
            AccountID TEXT PRIMARY KEY,
            MaHS TEXT,
            Username TEXT NOT NULL UNIQUE,
            PasswordHash TEXT NOT NULL,
            Role TEXT NOT NULL,
            Status TEXT NOT NULL,
            CreatedAt TEXT DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (MaHS) REFERENCES HOCSINH(MaHS) ON DELETE CASCADE
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS IDX_ACCOUNT_ROLE ON USER_ACCOUNT(Role)")
    conn.execute("CREATE INDEX IF NOT EXISTS IDX_ACCOUNT_STUDENT ON USER_ACCOUNT(MaHS)")
    conn.commit()
