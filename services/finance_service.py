from typing import List, Optional

from dao import exam_dao, finance_dao, student_dao, training_dao
from models.finance import PaymentRecordInfo, ScholarshipReviewInfo, TuitionInvoiceInfo
from services import activity_service

INVOICE_TYPES = ("Theo tín chỉ", "Cố định")
INVOICE_STATUSES = ("Chưa thanh toán", "Thanh toán một phần", "Đã thanh toán", "Quá hạn")
PAYMENT_METHODS = ("Tiền mặt", "Chuyển khoản", "Ví điện tử", "Thẻ ngân hàng")
SCHOLARSHIP_STATUSES = ("Đề xuất", "Duyệt", "Từ chối")


def list_invoices(status: Optional[str] = None, ma_hs: Optional[str] = None) -> List[TuitionInvoiceInfo]:
    return finance_dao.get_invoices(status=status, ma_hs=ma_hs)


def list_debts() -> List[TuitionInvoiceInfo]:
    return [
        invoice for invoice in finance_dao.get_invoices()
        if invoice.status != "Đã thanh toán" and invoice.total_amount > invoice.paid_amount
    ]


def list_payments(invoice_id: Optional[str] = None) -> List[PaymentRecordInfo]:
    return finance_dao.get_payments(invoice_id=invoice_id)


def list_scholarships(status: Optional[str] = None, ma_hs: Optional[str] = None) -> List[ScholarshipReviewInfo]:
    return finance_dao.get_scholarships(status=status, ma_hs=ma_hs)


def summary() -> dict:
    invoices = list_invoices()
    debts = list_debts()
    return {
        "invoices": len(invoices),
        "revenue": round(sum(i.paid_amount for i in invoices), 2),
        "debt": round(sum(max(0, i.total_amount - i.paid_amount) for i in debts), 2),
        "scholarships": len(list_scholarships()),
    }


def next_invoice_id() -> str:
    return f"HD{finance_dao.get_max_num('TUITION_INVOICE', 'InvoiceID', 'HD', 2) + 1:05d}"


def next_payment_id() -> str:
    return f"TT{finance_dao.get_max_num('PAYMENT_RECORD', 'PaymentID', 'TT', 2) + 1:05d}"


def next_scholarship_id() -> str:
    return f"HB{finance_dao.get_max_num('SCHOLARSHIP_REVIEW', 'ScholarshipID', 'HB', 2) + 1:05d}"


def create_invoice(invoice: TuitionInvoiceInfo) -> TuitionInvoiceInfo:
    invoice.invoice_id = invoice.invoice_id.strip()
    invoice.ma_hs = invoice.ma_hs.strip()
    invoice.term = invoice.term.strip()
    invoice.invoice_type = invoice.invoice_type.strip()
    invoice.due_date = _normalize_optional(invoice.due_date)
    invoice.notes = _normalize_optional(invoice.notes)
    if not student_dao.get_by_id(invoice.ma_hs):
        raise ValueError("Học sinh không tồn tại.")
    if invoice.invoice_type not in INVOICE_TYPES:
        raise ValueError("Loại hóa đơn không hợp lệ.")
    if not invoice.term:
        raise ValueError("Học kỳ/nam học không được để trống.")
    invoice.total_amount = calculate_invoice_total(invoice)
    invoice.paid_amount = invoice.paid_amount or 0
    invoice.status = _invoice_status(invoice)
    if finance_dao.get_invoice(invoice.invoice_id):
        raise ValueError(f"Mã hóa đơn '{invoice.invoice_id}' đã tồn tại.")
    finance_dao.insert_invoice(invoice)
    activity_service.log_activity("Lớp hóa đơn học phí", f"Lớp hóa đơn {invoice.invoice_id} cho {invoice.ma_hs}")
    return invoice


def calculate_invoice_total(invoice: TuitionInvoiceInfo) -> float:
    if invoice.invoice_type == "Theo tín chỉ":
        if invoice.credit_count is None or invoice.credit_count <= 0:
            invoice.credit_count = _registered_credit_count(invoice.ma_hs)
        if invoice.unit_price is None or invoice.unit_price <= 0:
            raise ValueError("Đơn giá tin chi phải lớn hơn 0.")
        return round(invoice.credit_count * invoice.unit_price, 2)
    if invoice.fixed_amount is None or invoice.fixed_amount <= 0:
        raise ValueError("Mức thu cố định phải lớn hơn 0.")
    return round(invoice.fixed_amount, 2)


def record_payment(payment: PaymentRecordInfo) -> PaymentRecordInfo:
    payment.payment_id = payment.payment_id.strip()
    payment.invoice_id = payment.invoice_id.strip()
    payment.payment_date = payment.payment_date.strip()
    payment.method = payment.method.strip()
    payment.transaction_ref = _normalize_optional(payment.transaction_ref)
    payment.notes = _normalize_optional(payment.notes)
    invoice = finance_dao.get_invoice(payment.invoice_id)
    if not invoice:
        raise ValueError("Hóa đơn không tồn tại.")
    if payment.amount <= 0:
        raise ValueError("Số tiền thanh toán phải lớn hơn 0.")
    if payment.method not in PAYMENT_METHODS:
        raise ValueError("Phương thức thanh toán không hợp lệ.")
    if finance_dao.get_payment(payment.payment_id):
        raise ValueError(f"Mã thanh toán '{payment.payment_id}' đã tồn tại.")
    finance_dao.insert_payment(payment)
    invoice.paid_amount = round(invoice.paid_amount + payment.amount, 2)
    invoice.status = _invoice_status(invoice)
    finance_dao.update_invoice(invoice)
    activity_service.log_activity("Ghi nhận thanh toán", f"Thanh toán {payment.amount:g} cho {invoice.invoice_id}")
    return payment


def scan_scholarships(term: str, min_gpa4: float = 3.2, amount: float = 1000000, conduct_score: float = 90) -> int:
    term = term.strip()
    if not term:
        raise ValueError("Học kỳ/nam học không được để trống.")
    if amount <= 0:
        raise ValueError("Mức học bổng phải lớn hơn 0.")
    created = 0
    for student in student_dao.get_all():
        gpa4, average10 = _student_grade_summary(student.ma_hs)
        if gpa4 is None:
            average10 = student.diem_tb
            gpa4 = round((student.diem_tb or 0) / 10 * 4, 2)
        if gpa4 >= min_gpa4:
            item = ScholarshipReviewInfo(
                scholarship_id=f"{term.replace(' ', '')}-{student.ma_hs}",
                ma_hs=student.ma_hs,
                term=term,
                gpa4=gpa4,
                average10=average10,
                conduct_score=conduct_score,
                amount=amount,
                status="Đề xuất",
                notes=f"Đạt GPA >= {min_gpa4:g}",
            )
            finance_dao.insert_or_update_scholarship(item)
            created += 1
    activity_service.log_activity("Xét học bổng", f"Quét {created} đề xuất học bổng cho {term}")
    return created


def update_scholarship(item: ScholarshipReviewInfo) -> ScholarshipReviewInfo:
    if item.status not in SCHOLARSHIP_STATUSES:
        raise ValueError("Trạng thái học bổng không hợp lệ.")
    if not student_dao.get_by_id(item.ma_hs):
        raise ValueError("Học sinh không tồn tại.")
    finance_dao.insert_or_update_scholarship(item)
    activity_service.log_activity("Cập nhật học bổng", f"Cập nhật {item.scholarship_id}: {item.status}")
    return item


def delete_invoice(invoice_id: str) -> bool:
    return finance_dao.delete_invoice(invoice_id)


def delete_payment(payment_id: str) -> bool:
    return finance_dao.delete_payment(payment_id)


def delete_scholarship(scholarship_id: str) -> bool:
    return finance_dao.delete_scholarship(scholarship_id)


def _registered_credit_count(ma_hs: str) -> int:
    total = 0
    for reg in training_dao.get_registrations(ma_hs=ma_hs):
        section = training_dao.get_section(reg.section_id)
        course = training_dao.get_course(section.course_id) if section else None
        total += course.credits if course else 0
    return total


def _student_grade_summary(ma_hs: str) -> tuple[Optional[float], Optional[float]]:
    grades = [g for g in exam_dao.get_grades(ma_hs=ma_hs) if g.gpa4 is not None]
    if not grades:
        return None, None
    gpa4 = round(sum(g.gpa4 for g in grades) / len(grades), 2)
    avg10_values = [g.average10 for g in grades if g.average10 is not None]
    avg10 = round(sum(avg10_values) / len(avg10_values), 2) if avg10_values else None
    return gpa4, avg10


def _invoice_status(invoice: TuitionInvoiceInfo) -> str:
    if invoice.paid_amount >= invoice.total_amount:
        return "Đã thanh toán"
    if invoice.paid_amount > 0:
        return "Thanh toán một phần"
    return "Chưa thanh toán"


def _normalize_optional(value):
    if value is None:
        return None
    if isinstance(value, str):
        value = value.strip()
        return value or None
    return value
