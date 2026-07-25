from typing import List, Optional

from dao.data_layer import DataLayer
from models.account import UserAccountInfo


def _account(row) -> UserAccountInfo:
    return UserAccountInfo(
        row["AccountID"],
        row["Username"],
        row["PasswordHash"],
        row["Role"],
        row["Status"],
        row["MaHS"],
        row["CreatedAt"],
    )


def get_all(role: Optional[str] = None, status: Optional[str] = None) -> List[UserAccountInfo]:
    sql = "SELECT * FROM USER_ACCOUNT WHERE 1=1"
    params: list = []
    if role:
        sql += " AND Role = ?"
        params.append(role)
    if status:
        sql += " AND Status = ?"
        params.append(status)
    sql += " ORDER BY CreatedAt DESC, Username"
    return [_account(row) for row in DataLayer.fetch_all(sql, params)]


def get_by_id(account_id: str) -> Optional[UserAccountInfo]:
    row = DataLayer.fetch_one("SELECT * FROM USER_ACCOUNT WHERE AccountID = ?", (account_id,))
    return _account(row) if row else None


def get_by_username(username: str) -> Optional[UserAccountInfo]:
    row = DataLayer.fetch_one("SELECT * FROM USER_ACCOUNT WHERE Username = ?", (username,))
    return _account(row) if row else None


def get_by_student(ma_hs: str) -> Optional[UserAccountInfo]:
    row = DataLayer.fetch_one("SELECT * FROM USER_ACCOUNT WHERE MaHS = ?", (ma_hs,))
    return _account(row) if row else None


def insert(account: UserAccountInfo) -> None:
    DataLayer.execute_non_query(
        """INSERT INTO USER_ACCOUNT (AccountID, MaHS, Username, PasswordHash, Role, Status)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (account.account_id, account.ma_hs, account.username, account.password_hash, account.role, account.status),
    )


def update_status(account_id: str, status: str) -> bool:
    return DataLayer.execute_non_query(
        "UPDATE USER_ACCOUNT SET Status = ? WHERE AccountID = ?",
        (status, account_id),
    ) > 0


def delete(account_id: str) -> bool:
    return DataLayer.execute_non_query("DELETE FROM USER_ACCOUNT WHERE AccountID = ?", (account_id,)) > 0


def get_max_account_num() -> int:
    max_num = DataLayer.scalar(
        "SELECT MAX(CAST(SUBSTR(AccountID, 3) AS INTEGER)) AS max_num FROM USER_ACCOUNT WHERE AccountID GLOB 'AC[0-9]*'",
        default=0,
    )
    return int(max_num or 0)
