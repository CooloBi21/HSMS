from dataclasses import dataclass
from typing import Optional


@dataclass
class TuitionInvoiceInfo:
    invoice_id: str
    ma_hs: str
    term: str
    invoice_type: str
    credit_count: Optional[int] = None
    unit_price: Optional[float] = None
    fixed_amount: Optional[float] = None
    total_amount: float = 0
    paid_amount: float = 0
    status: str = "Chua thanh toan"
    due_date: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[str] = None


@dataclass
class PaymentRecordInfo:
    payment_id: str
    invoice_id: str
    payment_date: str
    amount: float
    method: str
    transaction_ref: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class ScholarshipReviewInfo:
    scholarship_id: str
    ma_hs: str
    term: str
    gpa4: Optional[float] = None
    average10: Optional[float] = None
    conduct_score: Optional[float] = None
    amount: Optional[float] = None
    status: str = "De xuat"
    notes: Optional[str] = None
    created_at: Optional[str] = None
