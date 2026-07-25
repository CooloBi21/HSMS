# BTTH06 - Nhom 6: Qu?n l? C?ng t?c sinh vi?n & Ngo?i kh?a

## Pham vi nghiep vu

Nhom nay gom 4 yeu cau:

1. Danh gia ?i?m r?n luy?n theo ky.
2. Qu?n l? k? tuc xa: ph?ng o, dien nuoc, tinh hinh l?u tru.
3. Theo d?i hoat dong ngo?i kh?a: CLB, chien dich, tinh nguyen.
4. Qu?n l? y te h?c ???ng: kham s?c kh?e va bao hiem y te.

Huong thuc hien trong project la th?m module `C?ng t?c SV` rieng, lien ket truc tiep voi danh sach h?c sinh hien co.

## Doi chieu voi project hien co

| Nghiep vu | Trong project ?? c? gi gan giong | Cach xu ly sau cap nhat |
|-----------|----------------------------------|--------------------------|
| ?i?m r?n luy?n | Ch?a co, nhung h?c b?ng c? c?n ?i?m r?n luy?n | Th?m `CONDUCT_SCORE`, tu tinh tong va xep lo?i |
| K? t?c x? | Ch?a c? | Th?m `DORM_ASSIGNMENT` de qu?n l? ph?ng, giuong, dien nuoc, tr?ng th?i |
| Ngo?i kh?a | Ch?a c? | Th?m `EXTRACURRICULAR_ACTIVITY` de ghi nhan CLB/chien dich |
| Y t? h?c ???ng | Ch?a c? | Th?m `HEALTH_RECORD` de l?u kham s?c kh?e va BHYT |

## Phan nao la tinh nang he thong

- Cham ?i?m r?n luy?n theo h?c sinh va hoc ky.
- Tu tinh tong ?i?m r?n luy?n va xep loai.
- Sap xep ph?ng KTX, giuong, ng?y vao o va ti?n dien nuoc.
- Chan mot h?c sinh c? hai ph?ng KTX ?ang o cung luc.
- Ghi nhan hoat dong ngo?i kh?a, vai tro, s? gio tham gia.
- L?u l?ch su kham s?c kh?e, tr?ng th?i s?c kh?e, s? BHYT va han BHYT.

## Phan chu yeu la giay to/quy trinh

- Quy che cham ?i?m r?n luy?n chi tiet cua truong la van ban/quy trinh; app hien tai cu the hoa bang ba ?i?m thanh phan va xep lo?i tu dong.
- Hop dong/giay xac nhan KTX, bien lai dien nuoc la ch?ng t? hanh chinh; app hien tai l?u thong tin l?u tru va chi phi.
- Giay chung nhan tham gia hoat dong, minh chung tinh nguyen la tai lieu ngoai he thong; app hien tai l?u l?ch su tham gia.
- Bao hiem y te bat buoc lien quan don vi bao hiem; app hien tai l?u s? BHYT va han su dung.

## File ?? thay doi/th?m moi

| File | Vai tr? |
|------|---------|
| `models/student_affairs.py` | Model ?i?m r?n luy?n, KTX, ngo?i kh?a, y te |
| `dao/student_affairs_dao.py` | CRUD/truy van cong tac sinh vien |
| `services/student_affairs_service.py` | Validate va tinh diem/xep lo?i |
| `ui/views/student_affairs_view.py` | Man hinh C?ng t?c SV & Ngo?i kh?a |
| `ui/app.py` | Th?m menu `C?ng t?c SV` |
| `dao/db.py` | Migration cac bang cong tac sinh vien |

## Ket luan

Bon nghiep vu nhom 6 c? the dua vao project va ?? ???c cu the hoa thanh module chay ???c. Cac du lieu nay bo sung cho h? s? h?c sinh va c? the dung tiep cho h?c b?ng, canh bao y te, bao cao sinh vien trong cac nhom sau.
