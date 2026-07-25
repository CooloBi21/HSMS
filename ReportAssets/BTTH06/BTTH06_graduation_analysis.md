# BTTH06 - Nhom 7: T?t nghi?p & Bi?u m?u bao cao

## Pham vi nghiep vu

Nhom nay gom 5 yeu cau:

1. Xet ?i?u ki?n t?t nghi?p: chung chi tin hoc, ngoai ngu, GDQP va tin chi tich luy.
2. Cap phat v?n b?ng: s? goc, s? hieu bang, ng?y cap.
3. Xuat bang diem/giay chung nhan.
4. Bao cao th?ng k?: EMIS, hoc luc, thoi hoc.
5. Qu?n l? vi?c l?m c?u sinh vi?n.

Huong thuc hien trong project la th?m module `T?t nghi?p`, lien ket voi h?c sinh, ?i?m so, h?c ph?n va dashboard.

## Doi chieu voi project hien co

| Nghiep vu | Trong project ?? c? gi gan giong | Cach xu ly sau cap nhat |
|-----------|----------------------------------|--------------------------|
| X?t t?t nghi?p | `Kh?o th?` c? diem, `??o t?o` c? tin chi | Th?m `GRADUATION_CHECK`, tu tinh tin chi dat neu c?n |
| Cap v?n b?ng | Ch?a c? | Th?m `DIPLOMA_RECORD` qu?n l? s? goc/s? bang |
| B?ng ?i?m/Giay xac nhan | Dashboard c? th?ng k?, ch?a c? bi?u m?u | Th?m `DOCUMENT_REQUEST` ghi nhan yeu cau va duong dan xuat |
| Bao cao th?ng k? | `DashboardView` c? KPI noi bo | Th?m ham `emis_report()` tong hop ty le thoi hoc/t?t nghi?p |
| Viec lam c?u sinh vi?n | Ch?a c? | Th?m `ALUMNI_EMPLOYMENT` de khao sat vi?c l?m |

## Phan nao la tinh nang he thong

- Xet ?i?u ki?n t?t nghi?p theo tin chi va chung chi dau ra.
- Tu tinh tin chi dat tu ?i?m h?c ph?n neu nguoi dung nhap `-1`.
- L?u tr?ng th?i dat/ch?a dat t?t nghi?p.
- Qu?n l? s? hieu s? goc, s? hieu bang, ng?y cap v?n b?ng.
- Tao yeu cau bang diem/giay xac nhan/bao cao th?ng k?.
- Tong hop th?ng k? EMIS noi bo: tong h?c sinh, ty le thoi hoc, ty le t?t nghi?p, ?i?m TB.
- L?u khao sat vi?c l?m c?u sinh vi?n: cong ty, vi tri, luong, tr?ng th?i.

## Phan chu yeu la giay to/quy trinh

- In phoi bang t?t nghi?p that c?n mau phoi, may in, s? cap phoi va quy trinh bao mat. App hien tai qu?n l? thong tin v?n b?ng.
- B?ng ?i?m/giay xac nhan neu c?n file PDF/Word k? t?n dong dau thi la phan bi?u m?u xuat file nang cao. App hien tai l?u yeu cau va duong dan du kien.
- Bao cao EMIS chuan Bo Giao duc c? dinh dang/m? bieu rieng. App hien tai tong hop s? lieu noi bo de lam nen cho bao cao.
- Kh?o s?t vi?c l?m c?u sinh vi?n ngoai thuc te c? the qua form online/phone/email; app hien tai l?u ket qua khao sat.

## File ?? thay doi/th?m moi

| File | Vai tr? |
|------|---------|
| `models/graduation.py` | Model xet t?t nghi?p, v?n b?ng, bi?u m?u, cuu SV |
| `dao/graduation_dao.py` | CRUD/truy van du lieu t?t nghi?p |
| `services/graduation_service.py` | Xet ?i?u ki?n, th?ng k? EMIS, qu?n l? v?n b?ng/bi?u m?u/cuu SV |
| `ui/views/graduation_view.py` | Man hinh T?t nghi?p & Bao cao |
| `ui/app.py` | Th?m menu `T?t nghi?p` |
| `dao/db.py` | Migration cac bang t?t nghi?p |

## Ket luan

Nam nghiep vu nhom 7 c? the dua vao project va ?? ???c cu the hoa thanh module chay ???c. Cac phan lien quan in an/bi?u m?u chinh thuc ???c tach ro la quy trinh/tich hop ngoai, con he thong ?? c? du lieu nen de qu?n l? va bao cao.
