# BTTH06 - Nhom 2: Qu?n l? H? s? & Th?ng tin ca nhan

## Pham vi nghiep vu

Nhom nay gom 4 yeu cau:

1. C?p nh?t ly lich: thong tin ca nhan, ho khau, lien lac ph? huynh.
2. Qu?n l? tr?ng th?i h?c t?p: ?ang h?c, B?o l?u, Th?i h?c, T?t nghi?p.
3. Qu?n l? khen thuong/k? luat.
4. Qu?n l? dien chinh sach: mien giam h?c ph?, ho ngheo, vung sau vung xa.

Huong thuc hien trong project la mo rong h? s? h?c sinh hien c? va th?m module `H? s?` rieng. Cac nghiep vu lien quan truc tiep den h?c sinh ???c l?u tren bang `HOCSINH`; cac quyet dinh khen thuong/k? luat ???c l?u rieng trong bang `STUDENT_DECISION`.

## Doi chieu voi project hien co

| Nghiep vu | Trong project ?? c? gi gan giong | Cach xu ly sau cap nhat |
|-----------|----------------------------------|--------------------------|
| C?p nh?t ly l?ch | `HocSinhInfo`, `StudentsView` ?? c? ho ten, gi?i t?nh, ng?y sinh, ??a ch? | Th?m ho khau, ph? huynh, s? dien thoai ph? huynh va man hinh `H? s?` |
| Qu?n l? tr?ng th?i | Ch?a c? | Th?m `LearningStatus` voi cac tr?ng th?i ?ang h?c, B?o l?u, Th?i h?c, T?t nghi?p |
| Khen th??ng/K? lu?t | Ch?a c? | Th?m bang `STUDENT_DECISION` va CRUD quyet dinh theo h?c sinh |
| Di?n ch?nh s?ch | Ch?a c? | Th?m `PolicyType` de phan lo?i Kh?ng, Mi?n gi?m h?c ph?, H? ngh?o, V?ng s?u v?ng xa |

## Phan nao la tinh nang he thong

- C?p nh?t ly l?ch h?c sinh tren man hinh `H? s?`.
- L?u ho khau va thong tin lien lac ph? huynh.
- Doi tr?ng th?i h?c t?p cua h?c sinh.
- Gan dien chinh sach cho h?c sinh.
- Tao, s?a, x?a quyet dinh khen thuong/k? luat.
- Loc/tim quyet dinh theo h?c sinh, lo?i quyet dinh va tu khoa.
- Ghi activity log khi cap nhat ly l?ch va thay doi quyet dinh.

## Phan chu yeu la giay to/quy trinh

- Ban sc?n h? s?, s? ho khau, quyet dinh c? dau/moc do la tai lieu hanh chinh. App hien tai l?u thong tin nghiep vu va noi dung quyet dinh, ch?a qu?n l? file dinh kem.
- Viec phe duyet dien chinh sach ngoai doi thuc te c?n minh chung va quy trinh xac nhan. Trong app, phan nay ???c cu the hoa bang truong phan lo?i de phuc vu qu?n l?.
- Khen th??ng/k? luat trong app la ghi nhan quyet dinh; neu c?n quy trinh k? duyet nhieu cap thi se la module mo rong sau.

## File ?? thay doi/th?m moi

| File | Vai tr? |
|------|---------|
| `models/hoc_sinh.py` | Mo rong model h?c sinh voi ho khau, ph? huynh, tr?ng th?i, dien chinh sach |
| `dao/student_dao.py` | Doc/ghi cac truong h? s? mo rong |
| `services/student_service.py` | Validate tr?ng th?i h?c t?p va dien chinh sach |
| `models/student_decision.py` | Model quyet dinh khen thuong/k? luat |
| `dao/student_decision_dao.py` | CRUD quyet dinh h?c sinh |
| `services/student_decision_service.py` | Validate va ghi log quyet dinh |
| `ui/views/student_profiles_view.py` | Man hinh H? s? & Th?ng tin ca nhan |
| `ui/app.py` | Th?m menu `H? s?` |
| `dao/db.py` | Migration cot h? s? mo rong va bang `STUDENT_DECISION` |

## Ket luan

Bon nghiep vu nhom 2 c? the dua vao project va ?? ???c cu the hoa thanh tinh nang. Phan ?? c? san la h? s? h?c sinh c? ban. Phan moi th?m la ly l?ch mo rong, tr?ng th?i h?c t?p, dien chinh sach va quyet dinh khen thuong/k? luat. Cac module cu van ???c giu luong CRUD chinh; phan h? s? mo rong c? man hinh rieng de tranh pha logic ?ang chay.
