from typing import List, Optional

from dao.data_layer import DataLayer
from models.finance import PaymentRecordInfo, ScholarshipReviewInfo, TuitionInvoiceInfo


def _invoice(row) -> TuitionInvoiceInfo:
    return TuitionInvoiceInfo(
        row["InvoiceID"],
        row["MaHS"],
        row["Term"],
        row["InvoiceType"],
        row["CreditCount"],
        row["UnitPrice"],
        row["FixedAmount"],
        row["TotalAmount"],
        row["PaidAmount"],
        row["Status"],
        row["DueDate"],
        row["Notes"],
        row["CreatedAt"],
    )


def _payment(row) -> PaymentRecordInfo:
    return PaymentRecordInfo(
        row["PaymentID"],
        row["InvoiceID"],
        row["PaymentDate"],
        row["Amount"],
        row["Method"],
        row["TransactionRef"],
        row["Notes"],
    )


def _scholarship(row) -> ScholarshipReviewInfo:
    return ScholarshipReviewInfo(
        row["ScholarshipID"],
        row["MaHS"],
        row["Term"],
        row["GPA4"],
        row["Average10"],
        row["ConductScore"],
        row["Amount"],
        row["Status"],
        row["Notes"],
        row["CreatedAt"],
    )


def get_invoices(status: Optional[str] = None, ma_hs: Optional[str] = None) -> List[TuitionInvoiceInfo]:
    sql = "SELECT * FROM TUITION_INVOICE WHERE 1=1"
    params: list = []
    if status:
        sql += " AND Status = ?"
        params.append(status)
    if ma_hs:
        sql += " AND MaHS = ?"
        params.append(ma_hs)
    sql += " ORDER BY CreatedAt DESC, InvoiceID DESC"
    return [_invoice(row) for row in DataLayer.fetch_all(sql, params)]


def get_invoice(invoice_id: str) -> Optional[TuitionInvoiceInfo]:
    row = DataLayer.fetch_one("SELECT * FROM TUITION_INVOICE WHERE InvoiceID = ?", (invoice_id,))
    return _invoice(row) if row else None


def insert_invoice(invoice: TuitionInvoiceInfo) -> None:
    DataLayer.execute_non_query(
        """INSERT INTO TUITION_INVOICE
           (InvoiceID, MaHS, Term, InvoiceType, CreditCount, UnitPrice, FixedAmount,
            TotalAmount, PaidAmount, Status, DueDate, Notes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            invoice.invoice_id,
            invoice.ma_hs,
            invoice.term,
            invoice.invoice_type,
            invoice.credit_count,
            invoice.unit_price,
            invoice.fixed_amount,
            invoice.total_amount,
            invoice.paid_amount,
            invoice.status,
            invoice.due_date,
            invoice.notes,
        ),
    )


def update_invoice(invoice: TuitionInvoiceInfo) -> bool:
    return DataLayer.execute_non_query(
        """UPDATE TUITION_INVOICE
           SET MaHS=?, Term=?, InvoiceType=?, CreditCount=?, UnitPrice=?, FixedAmount=?,
               TotalAmount=?, PaidAmount=?, Status=?, DueDate=?, Notes=?
           WHERE InvoiceID=?""",
        (
            invoice.ma_hs,
            invoice.term,
            invoice.invoice_type,
            invoice.credit_count,
            invoice.unit_price,
            invoice.fixed_amount,
            invoice.total_amount,
            invoice.paid_amount,
            invoice.status,
            invoice.due_date,
            invoice.notes,
            invoice.invoice_id,
        ),
    ) > 0


def delete_invoice(invoice_id: str) -> bool:
    return DataLayer.execute_non_query("DELETE FROM TUITION_INVOICE WHERE InvoiceID = ?", (invoice_id,)) > 0


def get_payments(invoice_id: Optional[str] = None) -> List[PaymentRecordInfo]:
    sql = "SELECT * FROM PAYMENT_RECORD WHERE 1=1"
    params: list = []
    if invoice_id:
        sql += " AND InvoiceID = ?"
        params.append(invoice_id)
    sql += " ORDER BY PaymentDate DESC"
    return [_payment(row) for row in DataLayer.fetch_all(sql, params)]


def get_payment(payment_id: str) -> Optional[PaymentRecordInfo]:
    row = DataLayer.fetch_one("SELECT * FROM PAYMENT_RECORD WHERE PaymentID = ?", (payment_id,))
    return _payment(row) if row else None


def insert_payment(payment: PaymentRecordInfo) -> None:
    DataLayer.execute_non_query(
        """INSERT INTO PAYMENT_RECORD
           (PaymentID, InvoiceID, PaymentDate, Amount, Method, TransactionRef, Notes)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            payment.payment_id,
            payment.invoice_id,
            payment.payment_date,
            payment.amount,
            payment.method,
            payment.transaction_ref,
            payment.notes,
        ),
    )


def delete_payment(payment_id: str) -> bool:
    return DataLayer.execute_non_query("DELETE FROM PAYMENT_RECORD WHERE PaymentID = ?", (payment_id,)) > 0


def get_scholarships(status: Optional[str] = None, ma_hs: Optional[str] = None) -> List[ScholarshipReviewInfo]:
    sql = "SELECT * FROM SCHOLARSHIP_REVIEW WHERE 1=1"
    params: list = []
    if status:
        sql += " AND Status = ?"
        params.append(status)
    if ma_hs:
        sql += " AND MaHS = ?"
        params.append(ma_hs)
    sql += " ORDER BY CreatedAt DESC, ScholarshipID DESC"
    return [_scholarship(row) for row in DataLayer.fetch_all(sql, params)]


def get_scholarship(scholarship_id: str) -> Optional[ScholarshipReviewInfo]:
    row = DataLayer.fetch_one("SELECT * FROM SCHOLARSHIP_REVIEW WHERE ScholarshipID = ?", (scholarship_id,))
    return _scholarship(row) if row else None


def insert_or_update_scholarship(item: ScholarshipReviewInfo) -> None:
    DataLayer.execute_non_query(
        """INSERT OR REPLACE INTO SCHOLARSHIP_REVIEW
           (ScholarshipID, MaHS, Term, GPA4, Average10, ConductScore, Amount, Status, Notes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            item.scholarship_id,
            item.ma_hs,
            item.term,
            item.gpa4,
            item.average10,
            item.conduct_score,
            item.amount,
            item.status,
            item.notes,
        ),
    )


def delete_scholarship(scholarship_id: str) -> bool:
    return DataLayer.execute_non_query("DELETE FROM SCHOLARSHIP_REVIEW WHERE ScholarshipID = ?", (scholarship_id,)) > 0


def get_max_num(table: str, id_column: str, prefix: str, prefix_len: int) -> int:
    max_num = DataLayer.scalar(
        f"SELECT MAX(CAST(SUBSTR({id_column}, {prefix_len + 1}) AS INTEGER)) AS max_num "
        f"FROM {table} WHERE {id_column} GLOB '{prefix}[0-9]*'",
        default=0,
    )
    return int(max_num or 0)
