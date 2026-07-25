from typing import List, Optional

from dao.data_layer import DataLayer
from models.school_class import LopInfo


def _row_to_info(row) -> LopInfo:
    return LopInfo(ma_lop=row["MaLop"], ten_lop=row["TenLop"], khoi=row["Khoi"])


def get_all() -> List[LopInfo]:
    rows = DataLayer.fetch_all("SELECT * FROM LOP ORDER BY Khoi, TenLop")
    return [_row_to_info(r) for r in rows]


def get_by_id(ma_lop: str) -> Optional[LopInfo]:
    row = DataLayer.fetch_one("SELECT * FROM LOP WHERE MaLop = ?", (ma_lop,))
    return _row_to_info(row) if row else None


def insert(lop: LopInfo) -> None:
    DataLayer.execute_non_query(
        "INSERT INTO LOP (MaLop, TenLop, Khoi) VALUES (?, ?, ?)",
        (lop.ma_lop, lop.ten_lop, lop.khoi),
    )


def update(lop: LopInfo) -> bool:
    rowcount = DataLayer.execute_non_query(
        "UPDATE LOP SET TenLop=?, Khoi=? WHERE MaLop=?",
        (lop.ten_lop, lop.khoi, lop.ma_lop),
    )
    return rowcount > 0


def delete(ma_lop: str) -> bool:
    return DataLayer.execute_non_query("DELETE FROM LOP WHERE MaLop = ?", (ma_lop,)) > 0


def get_max_ma_lop_num() -> int:
    max_num = DataLayer.scalar(
        "SELECT MAX(CAST(SUBSTR(MaLop, 2) AS INTEGER)) AS max_num "
        "FROM LOP WHERE MaLop GLOB 'C[0-9]*'",
        default=0,
    )
    return int(max_num or 0)
