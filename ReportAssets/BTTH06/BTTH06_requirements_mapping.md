# BTTH06 - Tong hop nghiep vu HSMS

## Muc tieu tong hop

BTTH06 la moc tong hop cuoi cua du an HSMS. Phan nay ke thua BTTH02, BTTH03, BTTH04 va BTTH05, sau do doi chieu 30 yeu cau nghiep vu cot loi voi he thong hien co. Huong thuc hien trong repo la giu cac module dang chay tot, bo sung module `Nghiep vu` de quan ly danh muc 30 yeu cau va ghi nhan ho so xu ly cho tung yeu cau.

## Phan code da bo sung cho BTTH06

| Lop | File/module | Vai tro |
|-----|-------------|---------|
| Database | `dao/db.py` | Tao migration `BTTH06_REQUIREMENT`, `BTTH06_RECORD` va seed 30 yeu cau |
| Model | `models/btth06.py` | Dinh nghia `BusinessRequirementInfo`, `BusinessRecordInfo` |
| DAO | `dao/btth06_dao.py` | Loc, truy van, them, sua, xoa ho so nghiep vu |
| Service | `services/btth06_service.py` | Validate du lieu, sinh ma ho so, ghi activity log |
| UI | `ui/views/business_view.py` | Man hinh tong hop 30 yeu cau va quan ly ho so nghiep vu |
| App shell | `ui/app.py` | Them menu `Nghiep vu` vao ung dung chinh |
| Tai lieu | `README.md` | Cap nhat mo ta BTTH06 va kien truc hien tai |

## Doi chieu 30 yeu cau voi project sau cap nhat

| Ma | Nhom | Yeu cau nghiep vu | Module lien quan | Trang thai sau BTTH06 |
|----|------|-------------------|------------------|-----------------------|
| ADM01 | Tuyen sinh & Nhap hoc | Tiep nhan ho so dang ky | `BusinessView`, `BTTH06_RECORD` | Co noi ghi nhan ho so; chua co module tuyen sinh rieng |
| ADM02 | Tuyen sinh & Nhap hoc | Xet tuyen tu dong | `BusinessView`, `BTTH06_RECORD` | Co noi theo doi; chua co engine xet tuyen tu dong |
| ADM03 | Tuyen sinh & Nhap hoc | Cap ma so HSSV | `hoc_sinh_service.generate_next_id`, `hoc_sinh_dao.get_max_ma_hs` | Da co trong module hoc sinh |
| ADM04 | Tuyen sinh & Nhap hoc | Phan lop/phan nganh | `StudentsView`, `lop_service` | Da co phan lop; phan nganh ghi nhan qua module BTTH06 |
| PRO01 | Ho so & Thong tin ca nhan | Cap nhat ly lich | `HocSinhInfo`, `StudentsView`, `BusinessView` | Da co ho so co ban; BTTH06 ghi nhan bo sung |
| PRO02 | Ho so & Thong tin ca nhan | Quan ly trang thai hoc tap | `BusinessView`, `BTTH06_RECORD` | Co noi ghi nhan trang thai; chua gan truc tiep vao bang `HOCSINH` |
| PRO03 | Ho so & Thong tin ca nhan | Khen thuong/Ky luat | `BusinessView`, `BTTH06_RECORD` | Co ho so nghiep vu cho quyet dinh |
| PRO04 | Ho so & Thong tin ca nhan | Dien chinh sach | `BusinessView`, `BTTH06_RECORD` | Co ho so nghiep vu cho dien chinh sach |
| TRN01 | Dao tao & Xep lich | Khung chuong trinh | `BusinessView`, `BTTH06_RECORD` | Co noi quan ly o muc tong hop |
| TRN02 | Dao tao & Xep lich | Dang ky hoc phan | `BusinessView`, `BTTH06_RECORD` | Co noi quan ly o muc tong hop |
| TRN03 | Dao tao & Xep lich | Xep thoi khoa bieu | `BusinessView`, `BTTH06_RECORD` | Co noi quan ly o muc tong hop |
| TRN04 | Dao tao & Xep lich | Diem danh & Chuyen can | `BusinessView`, `BTTH06_RECORD` | Co noi ghi nhan; chua co bang diem danh rieng |
| EXM01 | Khao thi & Diem so | Lap lich thi | `BusinessView`, `BTTH06_RECORD` | Co noi quan ly o muc tong hop |
| EXM02 | Khao thi & Diem so | Nhap & Quan ly diem | `StudentsView`, `HocSinhInfo.diem_tb`, `BusinessView` | Da co diem TB; diem thanh phan ghi nhan qua BTTH06 |
| EXM03 | Khao thi & Diem so | Tinh diem trung binh/GPA | `dashboard_service`, `DashboardView` | Da co diem TB thang 10; GPA thang 4 la huong mo rong |
| EXM04 | Khao thi & Diem so | Xet dieu kien thi | `BusinessView`, `BTTH06_RECORD` | Co noi theo doi dieu kien; chua tu dong khoa du thi |
| EXM05 | Khao thi & Diem so | Phuc khao | `BusinessView`, `BTTH06_RECORD` | Co ho so nghiep vu cho yeu cau phuc khao |
| FIN01 | Tai chinh & Hoc phi | Tinh toan hoc phi | `BusinessView`, `BTTH06_RECORD.Amount` | Co noi ghi nhan so tien; chua co cong thuc hoc phi rieng |
| FIN02 | Tai chinh & Hoc phi | Thu phi truc tuyen | `BusinessView`, `BTTH06_RECORD` | Co noi theo doi; tich hop cong thanh toan ngoai pham vi app hien tai |
| FIN03 | Tai chinh & Hoc phi | Quan ly cong no | `BusinessView`, `BTTH06_RECORD.Amount` | Co noi ghi nhan cong no/so tien |
| FIN04 | Tai chinh & Hoc phi | Xet duyet hoc bong | `dashboard_service`, `BusinessView` | Co du lieu diem dau vao va ho so xet duyet |
| STU01 | Cong tac sinh vien & Ngoai khoa | Diem ren luyen | `BusinessView`, `BTTH06_RECORD.NumericValue` | Co noi ghi nhan diem ren luyen |
| STU02 | Cong tac sinh vien & Ngoai khoa | Ky tuc xa | `BusinessView`, `BTTH06_RECORD` | Co noi quan ly o muc tong hop |
| STU03 | Cong tac sinh vien & Ngoai khoa | Hoat dong ngoai khoa | `BusinessView`, `BTTH06_RECORD` | Co noi ghi nhan tham gia hoat dong |
| STU04 | Cong tac sinh vien & Ngoai khoa | Y te hoc duong | `BusinessView`, `BTTH06_RECORD` | Co noi ghi nhan ho so y te |
| GRD01 | Tot nghiep & Bao cao | Xet dieu kien tot nghiep | `BusinessView`, `BTTH06_RECORD.NumericValue` | Co noi theo doi tich luy/chung chi |
| GRD02 | Tot nghiep & Bao cao | Cap phat van bang | `BusinessView`, `BTTH06_RECORD` | Co noi quan ly so hieu/ghi chu van bang |
| GRD03 | Tot nghiep & Bao cao | Xuat bang diem/Giay chung nhan | `BusinessView`, `DashboardView` | Co noi ghi nhan yeu cau bieu mau; chua co in file rieng |
| GRD04 | Tot nghiep & Bao cao | Bao cao thong ke | `dashboard_service`, `DashboardView` | Da co thong ke noi bo co ban |
| GRD05 | Tot nghiep & Bao cao | Viec lam cuu sinh vien | `BusinessView`, `BTTH06_RECORD` | Co noi ghi nhan thong tin cuu sinh vien |

## Ket luan ky thuat

Sau cap nhat BTTH06, project co them mot lop tong hop nghiep vu de bao phu 30 yeu cau ma khong pha cac module da hoat dong: hoc sinh, lop hoc, giao vien, dashboard va tang data access cua BTTH05. Cac yeu cau da co san van duoc giu nguyen luong xu ly cu. Cac yeu cau chua co module rieng duoc dua vao `BTTH06_RECORD` de co the tao ho so, lien ket hoc sinh, nhap ngay phat sinh, gia tri so, so tien, ghi chu va trang thai xu ly.

Pham vi nay phu hop voi tinh chat bai tong hop: he thong co diem doi chieu ro rang, co man hinh thao tac thuc te, co database luu tru rieng va van giu kien truc 3 lop `models -> dao -> services -> ui`.
