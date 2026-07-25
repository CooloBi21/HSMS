# BTTH06 - Nhom 5: Qu?n l? T?i ch?nh & H?c ph?

## Pham vi nghiep vu

Nhom nay gom 4 yeu cau:

1. Tinh toan h?c ph?: lap h?a ??n theo tin chi hoac muc thu c? dinh.
2. Th? phi truc tuyen: ghi nhan thanh to?n qua ngan hang/vi dien tu.
3. Qu?n l? c?ng n?: theo d?i h?c sinh ch?a hoan thanh nghia vu tai chinh.
4. Xet duyet h?c b?ng: quet ?i?m s? va r?n luy?n de de xuat h?c b?ng.

Huong thuc hien trong project la th?m module `T?i ch?nh` rieng, dung lai du lieu h?c sinh, h?c ph?n/?ang k? va ?i?m so.

## Doi chieu voi project hien co

| Nghiep vu | Trong project ?? c? gi gan giong | Cach xu ly sau cap nhat |
|-----------|----------------------------------|--------------------------|
| Tinh h?c ph? | `??o t?o` c? ?ang k? h?c ph?n va tin chi | Th?m `TUITION_INVOICE`, tinh theo tin chi hoac muc c? dinh |
| Th? phi truc tuyen | Ch?a c? cong thanh to?n | Th?m `PAYMENT_RECORD` de ghi nhan thanh to?n, phuong thuc va m? giao dich |
| C?ng n? | Ch?a c? | Tinh c?ng n? tu h?a ??n ch?a thanh to?n du |
| H?c b?ng | `Kh?o th?` c? diem/GPA, `H? s?` c? quyet dinh | Th?m `SCHOLARSHIP_REVIEW`, quet GPA/?i?m de tao de xuat |

## Phan nao la tinh nang he thong

- L?p h?a ??n h?c ph? theo s? tin chi x don gia.
- L?p h?a ??n h?c ph? theo muc thu c? dinh.
- Tu tinh tong ti?n h?a ??n.
- Ghi nh?n thanh to?n theo ti?n mat, chuyen khoan, vi dien tu, the ngan hang.
- C?p nh?t tr?ng th?i h?a ??n: ch?a thanh to?n, thanh to?n mot phan, ?? thanh to?n.
- Liet ke c?ng n? con lai.
- Quet du lieu diem/GPA de de xuat h?c b?ng.
- L?u muc h?c b?ng, ?i?m r?n luy?n mac dinh va tr?ng th?i xet duyet.

## Phan chu yeu la giay to/tich hop ben ngoai

- Th? phi truc tuyen dung nghia c?n cong thanh to?n ngan hang/vi dien tu, API, m? merchant va xac thuc giao dich. App hien tai chi ghi nhan giao dich va m? tham chieu/ch?ng t?.
- Gui thong bao c?ng n? qua SMS/email/app la tich hop ngoai. Hien tai app tao danh sach c?ng n? de nguoi dung theo d?i.
- H?c b?ng ngoai thuc te c?n quyet dinh, ngan sach, hoi dong xet duyet. App hien tai tao de xuat dua tren diem/GPA va l?u tr?ng th?i.

## File ?? thay doi/th?m moi

| File | Vai tr? |
|------|---------|
| `models/finance.py` | Model h?a ??n, thanh to?n, h?c b?ng |
| `dao/finance_dao.py` | CRUD/truy van du lieu tai chinh |
| `services/finance_service.py` | Tinh h?c ph?, ghi nhan thanh to?n, c?ng n?, h?c b?ng |
| `ui/views/finance_view.py` | Man hinh T?i ch?nh & H?c ph? |
| `ui/app.py` | Th?m menu `T?i ch?nh` |
| `dao/db.py` | Migration cac bang tai chinh |

## Ket luan

Bon nghiep vu nhom 5 c? the dua vao project va ?? ???c cu the hoa thanh module chay ???c. Phan tich hop thanh to?n that ???c ghi nhan la pham vi he thong ngoai, con project hien tai qu?n l? du lieu tai chinh noi bo, c?ng n? va h?c b?ng.
