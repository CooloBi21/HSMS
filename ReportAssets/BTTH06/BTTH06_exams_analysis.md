# BTTH06 - Nhom 4: Qu?n l? Kh?o th? & ?i?m so

## Pham vi nghiep vu

Nhom nay gom 5 yeu cau:

1. L?p l?ch thi: ca thi, ph?ng thi, s? bao danh.
2. Nhap va qu?n l? diem: ?i?m thanh phan, giua ky, cuoi ky.
3. Tinh ?i?m trung binh/GPA theo thang 10 va thang 4.
4. Xet ?i?u ki?n thi: khoa quyen du thi neu kh?ng du chuyen c?n hoac h?c ph?.
5. Qu?n l? ph?c kh?o: tiep nhan yeu cau va cap nhat ?i?m sau dieu chinh.

Huong thuc hien trong project la th?m module `Kh?o th?` rieng, dung du lieu h?c ph?n va ?ang k? tu module `??o t?o`.

## Doi chieu voi project hien co

| Nghiep vu | Trong project ?? c? gi gan giong | Cach xu ly sau cap nhat |
|-----------|----------------------------------|--------------------------|
| L?p l?ch thi | `??o t?o` ?? c? h?c ph?n va l?ch hoc | Th?m `EXAM_SCHEDULE` de lap ng?y thi, ca thi, ph?ng thi, lo?i thi |
| Nhap & Qu?n l? ?i?m | `H?c sinh` c? ?i?m trung binh tong quat | Th?m `GRADE_RECORD` theo h?c ph?n, gom ?i?m thanh phan, giua ky, cuoi k? |
| Tinh ?i?m TB/GPA | Dashboard ?? th?ng k? ?i?m TB c? ban | Service tinh `Average10`, `GPA4`, `LetterGrade` tu ?i?m h?c ph?n |
| Xet ?i?u ki?n thi | `??o t?o` ?? c? ?i?m danh; ch?a c? h?c ph? | Th?m `EXAM_ELIGIBILITY`, tu tinh chuyen c?n va c? c? `TuitionEligible` cho h?c ph? |
| Ph?c kh?o | Ch?a c? | Th?m `GRADE_REVIEW`, neu ph?c kh?o ?? dieu chinh thi cap nhat lai ?i?m cuoi k? |

## Phan nao la tinh nang he thong

- L?p l?ch thi theo h?c ph?n, ng?y thi, ca thi, ph?ng thi.
- Chan trung ph?ng thi trong cung ng?y va ca thi.
- Tao danh sach du thi va s? bao danh tu danh sach ?ang k? h?c ph?n.
- Khoa du thi neu kh?ng dat ?i?u ki?n chuyen can.
- L?u c? ?i?u ki?n h?c ph? o bang du thi de sau nay noi voi module tai chinh.
- Nhap ?i?m thanh phan, giua ky, cuoi ky.
- Tu dong tinh ?i?m trung binh thang 10, GPA thang 4 va xep lo?i chu.
- Ti?p nh?n va xu ly ph?c kh?o.
- C?p nh?t lai ?i?m sau khi ph?c kh?o ???c dieu chinh.

## Phan chu yeu la giay to/quy trinh

- Bien ban coi thi, tui bai thi, phieu cham thi va quyet dinh hoi dong thi la tai lieu hanh chinh; app hien tai l?u l?ch thi, ph?ng thi va du lieu diem.
- ?i?u ki?n h?c ph? ch?a the tu dong lay tu c?ng n? vi module T?i ch?nh ch?a ???c trien khai. Trong giai do nay he thong c? truong `TuitionEligible` de ghi nhan ?i?u ki?n h?c ph?.
- Quy trinh ph?c kh?o ngoai doi c? the c?n bien ban, nguoi cham lai va phe duyet nhieu cap. App hien tai cu the hoa bang yeu cau ph?c kh?o, tr?ng th?i va ?i?m dieu chinh.

## File ?? thay doi/th?m moi

| File | Vai tr? |
|------|---------|
| `models/exam.py` | Model l?ch thi, ?i?u ki?n thi, diem, ph?c kh?o |
| `dao/exam_dao.py` | CRUD/truy van cac bang khao thi |
| `services/exam_service.py` | Validate l?ch thi, tinh diem/GPA, xet ?i?u ki?n, xu ly ph?c kh?o |
| `ui/views/exams_view.py` | Man hinh Kh?o th? & ?i?m s? |
| `ui/app.py` | Th?m menu `Kh?o th?` |
| `dao/db.py` | Migration cac bang khao thi |

## Ket luan

Nam nghiep vu nhom 4 c? the dua vao project va ?? ???c cu the hoa thanh module chay ???c. Phan moi nay ke thua module `??o t?o`, vi l?ch thi, ?i?m va ?i?u ki?n thi deu gan voi h?c ph?n va danh sach ?ang k? h?c ph?n.
