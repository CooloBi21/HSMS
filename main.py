"""HSMS — Hệ thống Quản lý Học sinh (CustomTkinter + SQLite)."""

from dao.db import init_database_if_needed
from ui.app import HSMSApp


def main() -> None:
    init_database_if_needed()
    app = HSMSApp()
    app.mainloop()


if __name__ == "__main__":
    main()
