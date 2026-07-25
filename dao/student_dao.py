from typing import List, Optional

from dao.data_layer import DataLayer
from models.student import HocSinhInfo


def _row_to_info(row) -> HocSinhInfo:
    return HocSinhInfo(
        ma_hs=row["MaHS"],
        ho_ten=row["HoTen"],
        gioi_tinh=row["GioiTinh"],
        ngay_sinh=row["NgaySinh"],
        dia_chi=row["DiaChi"],
        diem_tb=row["DiemTB"],
        ma_lop=row["MaLop"],
        ho_khau=row.get("HoKhau"),
        parent_name=row.get("ParentName"),
        parent_phone=row.get("ParentPhone"),
        learning_status=row.get("LearningStatus") or "Đang học",
        policy_type=row.get("PolicyType"),
    )


def get_all(ma_lop: Optional[str] = None, search: Optional[str] = None) -> List[HocSinhInfo]:
    sql = "SELECT * FROM HOCSINH WHERE 1=1"
    params: list = []

    if ma_lop:
        sql += " AND MaLop = ?"
        params.append(ma_lop)
    if search:
        sql += " AND (HoTen LIKE ? OR MaHS LIKE ?)"
        term = f"%{search}%"
        params.extend([term, term])

    sql += " ORDER BY HoTen"
    rows = DataLayer.fetch_all(sql, params)
    return [_row_to_info(r) for r in rows]


def get_by_id(ma_hs: str) -> Optional[HocSinhInfo]:
    row = DataLayer.fetch_one("SELECT * FROM HOCSINH WHERE MaHS = ?", (ma_hs,))
    return _row_to_info(row) if row else None


def insert(hs: HocSinhInfo) -> None:
    DataLayer.execute_non_query(
        """INSERT INTO HOCSINH
           (MaHS, HoTen, GioiTinh, NgaySinh, DiaChi, DiemTB, MaLop,
            HoKhau, ParentName, ParentPhone, LearningStatus, PolicyType)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            hs.ma_hs,
            hs.ho_ten,
            hs.gioi_tinh,
            hs.ngay_sinh,
            hs.dia_chi,
            hs.diem_tb,
            hs.ma_lop,
            hs.ho_khau,
            hs.parent_name,
            hs.parent_phone,
            hs.learning_status,
            hs.policy_type,
        ),
    )


def update(hs: HocSinhInfo) -> bool:
    rowcount = DataLayer.execute_non_query(
        """UPDATE HOCSINH SET HoTen=?, GioiTinh=?, NgaySinh=?, DiaChi=?, DiemTB=?, MaLop=?
           WHERE MaHS=?""",
        (hs.ho_ten, hs.gioi_tinh, hs.ngay_sinh, hs.dia_chi, hs.diem_tb, hs.ma_lop, hs.ma_hs),
    )
    return rowcount > 0


def update_profile(hs: HocSinhInfo) -> bool:
    rowcount = DataLayer.execute_non_query(
        """UPDATE HOCSINH
           SET HoTen=?, GioiTinh=?, NgaySinh=?, DiaChi=?, MaLop=?,
               HoKhau=?, ParentName=?, ParentPhone=?, LearningStatus=?, PolicyType=?
           WHERE MaHS=?""",
        (
            hs.ho_ten,
            hs.gioi_tinh,
            hs.ngay_sinh,
            hs.dia_chi,
            hs.ma_lop,
            hs.ho_khau,
            hs.parent_name,
            hs.parent_phone,
            hs.learning_status,
            hs.policy_type,
            hs.ma_hs,
        ),
    )
    return rowcount > 0


def delete(ma_hs: str) -> bool:
    return DataLayer.execute_non_query("DELETE FROM HOCSINH WHERE MaHS = ?", (ma_hs,)) > 0


def count_by_class(ma_lop: str) -> int:
    count = DataLayer.scalar("SELECT COUNT(*) AS c FROM HOCSINH WHERE MaLop = ?", (ma_lop,), 0)
    return int(count or 0)


def get_max_ma_hs() -> int:
    """Trả về số thứ tự lớn nhất của MaHS dạng S###. Dùng để sinh mã mới."""
    max_num = DataLayer.scalar(
        "SELECT MAX(CAST(SUBSTR(MaHS, 2) AS INTEGER)) AS max_num "
        "FROM HOCSINH WHERE MaHS GLOB 'S[0-9]*'",
        default=0,
    )
    return int(max_num or 0)
