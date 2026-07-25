# BTTH06 - Nhom 3: Qu?n l? ??o t?o & Xep lich

## Pham vi nghiep vu

Nhom nay gom 4 yeu cau:

1. Qu?n l? khung chuong trinh: m?n hoc, ti?n trinh h?c t?p, m?n ti?n quyet.
2. ??ng k? h?c ph?n: h?c sinh/sinh vien ch?n l?p h?c ph?n.
3. Xep thoi khoa bieu: sap xep l?ch hoc, ph?ng hoc va tranh trung lich.
4. ?i?m danh & qu?n l? chuyen can: ghi nhan vang, di muon, c? mat hang ng?y.

Huong thuc hien trong project la th?m module `??o t?o` rieng. Module nay dung cac du lieu san c? cua project: h?c sinh, l?p hoc va giao vien.

## Doi chieu voi project hien co

| Nghiep vu | Trong project ?? c? gi gan giong | Cach xu ly sau cap nhat |
|-----------|----------------------------------|--------------------------|
| Khung chuong trinh | Gi?o vi?n c? m?n phu trach, h?c sinh c? ?i?m TB; ch?a c? bang m?n hoc | Th?m `COURSE` va `CURRICULUM_ITEM` |
| ??ng k? h?c ph?n | Ch?a c? h?c ph?n/?ang k? | Th?m `COURSE_SECTION` va `COURSE_REGISTRATION` |
| Xep thoi khoa bieu | Ch?a c? l?ch hoc/ph?ng hoc | Th?m `CLASS_SCHEDULE` va validate trung ph?ng, trung giao vien, trung l?p |
| ?i?m danh/chuyen c?n | Ch?a c? bang ?i?m danh | Th?m `ATTENDANCE_RECORD` voi C? m?t, V?ng, ?i mu?n, C? ph?p |

## Phan nao la tinh nang he thong

- Tao m?n hoc va khai bao m?n ti?n quyet.
- Th?m m?n h?c vao khung chuong trinh theo khoi/khoa va hoc ky.
- M? l?p h?c ph?n theo mon, l?p sinh hoat, giao vien va si s? toi da.
- ??ng k? h?c sinh vao l?p h?c ph?n.
- Chan ?ang k? trung va chan vuot si so.
- X?p l?ch h?c theo thu, tiet, ph?ng.
- Chan trung ph?ng, trung giao vien va trung l?p sinh hoat trong cung khung gio.
- Ghi nhan ?i?m danh tung h?c sinh theo l?p h?c ph?n va ng?y.

## Phan chu yeu la giay to/quy trinh

- "??ng k? truc tuyen" la kenh trien khai. Trong app desktop hien tai, tinh nang ?ang k? ???c cu the hoa bang form noi bo; cong web/portal sinh vien la huong mo rong.
- "Tu dong xep thoi khoa bieu" hoan toan c?n thuat toan toi uu va nhieu rang buoc hon. Hien tai project lam muc ban tu dong: nguoi dung nhap lich, he thong tu kiem tra va chan trung lich.
- Khung chuong trinh ngoai thuc te c? the c?n phe duyet, phien ban chuong trinh va van ban dao tao. App hien tai l?u cau truc du lieu cot loi de qu?n l? va minh chung.

## File ?? thay doi/th?m moi

| File | Vai tr? |
|------|---------|
| `models/training.py` | Model m?n hoc, khung CT, h?c ph?n, ?ang ky, l?ch hoc, ?i?m danh |
| `dao/training_dao.py` | CRUD/truy van cac bang dao tao |
| `services/training_service.py` | Validate nghiep vu dao tao va xep l?ch |
| `ui/views/training_view.py` | Man hinh ??o t?o & Xep l?ch |
| `ui/app.py` | Th?m menu `??o t?o` |
| `dao/db.py` | Migration cac bang dao tao |

## Ket luan

Bon nghiep vu nhom 3 c? the dua vao project va ?? ???c cu the hoa thanh module chay ???c. Phan moi nay kh?ng thay doi logic h?c sinh/lop/giao vien cu, m? dung lai cac module do lam du lieu nen cho dao tao, ?ang ky, xep l?ch va ?i?m danh.
