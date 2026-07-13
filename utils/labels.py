STATUS_VI = {
    "Active": "Đang giảng dạy",
    "Inactive": "Tạm nghỉ / ngừng giảng dạy",
}

STATUS_FILTER_VI = {
    "Tất cả": None,
    "Đang giảng dạy": "Active",
    "Tạm nghỉ": "Inactive",
}


def teacher_status_vi(status: str | None) -> str:
    if not status:
        return "—"
    return STATUS_VI.get(status, status)


def teacher_status_db(label: str) -> str:
    for vi, db in STATUS_FILTER_VI.items():
        if vi == label:
            return db or ""
    return label
