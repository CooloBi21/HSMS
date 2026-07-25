# BTTH06 - Nhom 1: Qu?n l? Tuy?n sinh & Nh?p h?c

## Pham vi nghiep vu

Nhom nay gom 4 yeu cau:

1. Ti?p nh?n h? s? ?ang k? x?t tuy?n.
2. X?t tuy?n t? ??ng theo tieu chi cai dat san.
3. C?p m? s? HSSV/h?c sinh moi.
4. Ph?n l?p hoac phan nganh cho nguoi hoc moi.

Huong thuc hien trong project HSMS la th?m module `Tuy?n sinh` rieng. H? s? tuy?n sinh ???c l?u rieng trong bang `ADMISSION_APPLICATION`. Khi h? s? dat x?t tuy?n va ???c nh?p h?c, he thong moi tao ban ghi h?c sinh that trong bang `HOCSINH`.

## Doi chieu voi project hien co

| Nghiep vu | Trong project ?? c? gi gan giong | Cach xu ly sau cap nhat |
|-----------|----------------------------------|--------------------------|
| Ti?p nh?n h? s? | Module `H?c sinh` c? form tao h?c sinh, nhung day la sau khi ?? nh?p h?c | Th?m form h? s? tuy?n sinh rieng, ch?a tao h?c sinh ng?y |
| X?t tuy?n t? ??ng | Ch?a c? | Th?m nut x?t tuy?n theo ?i?m chuan mac dinh 5.0 |
| C?p m? s? HSSV | `student_service.generate_next_id()` ?? c? | Tai su dung khi nh?p h?c tu h? s? dat |
| Ph?n l?p/phan nganh | `L?p h?c` va truong `MaLop` cua h?c sinh ?? c? ph?n l?p; ch?a c? phan nganh | Dung l?p hien c? de ph?n l?p; phan nganh/huong hoc l?u trong h? s? tuy?n sinh |

## Phan nao la tinh nang he thong

- Nhap, s?a, x?a h? s? tuy?n sinh.
- L?u thong tin thi sinh, ph? huynh, ?i?m x?t tuy?n, l?p du kien, nganh/huong hoc.
- Loc va tim kiem h? s? theo tr?ng th?i.
- X?t tuy?n t? ??ng dua tren ?i?m chuan.
- Nh?p h?c h? s? dat, tu dong c?p m? h?c sinh va tao ban ghi trong module `H?c sinh`.
- Ghi activity log cho tiep nhan h? s?, x?t tuy?n, nh?p h?c va x?a h? s?.

## Phan chu yeu la giay to/quy trinh

- "Truc tuyen hoac truc tiep" la cach tiep nhan ben ngoai he thong. Trong app desktop hien tai, he thong ho tro nhap truc tiep vao form; tiep nhan truc tuyen c?n cong web/routing rieng.
- "Tieu chi cai dat san" hien ???c cu the hoa bang ?i?m chuan mac dinh 5.0. Neu c?n hoi dong tuy?n sinh phuc tap hon, c?n th?m bang cau hinh tieu chi rieng.
- "Phan nganh" ???c l?u nhu thong tin/huong hoc mong muon. Project hien tai la HSMS theo l?p hoc, ch?a c? module khoa/nganh rieng.

## File ?? thay doi/th?m moi

| File | Vai tr? |
|------|---------|
| `models/admission.py` | Model h? s? tuy?n sinh |
| `dao/admission_dao.py` | CRUD va truy van h? s? tuy?n sinh |
| `services/admission_service.py` | Validate, x?t tuy?n, nh?p h?c, c?p m? HS |
| `ui/views/admissions_view.py` | Man hinh Tuy?n sinh & Nh?p h?c |
| `ui/app.py` | Th?m menu `Tuy?n sinh` |
| `dao/db.py` | Th?m migration bang `ADMISSION_APPLICATION`, go bo schem? BTTH06 tong hop cu |

## Ket luan

Bon nghiep vu dau ti?n c? the dua vao project va ?? ???c cu the hoa thanh module chay ???c. Phan c? san cua project ???c tai su dung lai la c?p m? h?c sinh, danh sach l?p va tao h?c sinh. Phan ch?a c? truoc do la h? s? tuy?n sinh va x?t tuy?n tu dong ?? ???c th?m rieng, kh?ng chen logic moi vao module h?c sinh ?ang hoat dong tot.
