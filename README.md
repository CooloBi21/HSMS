# HSMS - Hệ thống quản lý học sinh

HSMS là ứng dụng desktop dùng để quản lý toàn bộ quy trình vận hành học sinh trong nhà trường: tuyển sinh, hồ sơ, đào tạo, khảo thí, tài chính, công tác sinh viên, tốt nghiệp, tài khoản người dùng và các danh mục nền như lớp học, giáo viên.

Ứng dụng được xây dựng bằng Python, CustomTkinter và SQLite. Kiến trúc chính đi theo mô hình phân tầng để giao diện, nghiệp vụ và truy cập dữ liệu tách biệt rõ ràng.

## Công nghệ sử dụng

- Python 3.10+
- CustomTkinter cho giao diện desktop
- SQLite làm cơ sở dữ liệu mặc định
- Matplotlib cho biểu đồ dashboard
- `configparser` để đọc cấu hình hệ thống
- Kiến trúc provider/data layer để có thể mở rộng kết nối CSDL

## Định hướng phiên bản

### Desktop

Phiên bản desktop hiện tại là bản ổn định của HSMS, chạy bằng CustomTkinter và SQLite. Bản này được giữ lại để phục vụ báo cáo, kiểm thử nghiệp vụ và làm mốc khôi phục khi triển khai web/cloud.

Mốc bảo vệ:

- Tag khôi phục: `desktop-v1.0`
- Nhánh desktop ổn định: `desktop-final`

### Web

Phiên bản web sẽ được xây dựng kế thừa nghiệp vụ đã có từ desktop, ưu tiên tái sử dụng model, service, quy tắc kiểm tra dữ liệu và cấu trúc phân tầng. Phần giao diện CustomTkinter sẽ được thay bằng Flask/Jinja/Bootstrap. CSDL triển khai web dự kiến chuyển sang PostgreSQL thông qua SQLAlchemy.

### Deployment

Các công việc Docker, PostgreSQL, Nginx, Cloudflare Tunnel và Cloudflare Access được thực hiện trên nhánh `cloud-deployment`. Nhánh này là nơi phát triển triển khai cloud, không sửa trực tiếp vào `desktop-final`.

## Cấu trúc dự án

```text
main.py                      Điểm chạy ứng dụng
config.py                    Cấu hình ứng dụng, đường dẫn dữ liệu, cấu hình CSDL
database_config.ini           Provider và connection string
database/init_db.sql          Schema và dữ liệu mẫu ban đầu
models/                      Dataclass/DTO của hệ thống
dao/                         Tầng truy cập dữ liệu
services/                    Tầng nghiệp vụ
ui/                          Giao diện người dùng
ui/views/                    Các màn hình nghiệp vụ
ui/components/               Component dùng chung
ReportAssets/                Tài liệu phân tích và minh chứng báo cáo
```

## Kiến trúc hệ thống

Luồng xử lý chính:

```text
UI
  -> Service
    -> DAO
      -> DataLayer
        -> DbProvider
          -> SQLite hoặc provider khác
```

Tầng UI chỉ nhận dữ liệu nhập và hiển thị kết quả. Tầng service chịu trách nhiệm kiểm tra nghiệp vụ, tính toán, điều phối các DAO và ghi activity log. Tầng DAO chỉ thao tác với câu SQL và ánh xạ dữ liệu về model.

## Cấu hình cơ sở dữ liệu

Thông tin kết nối được đặt trong `database_config.ini`:

```ini
[database]
provider = sqlite
connection_string = data/hsms.db
```

Hệ thống mặc định chạy với SQLite. Các lớp `dao/db_provider.py` và `dao/data_layer.py` giữ vai trò tách thông tin kết nối khỏi logic nghiệp vụ, giúp dự án có nền tảng mở rộng sang provider khác khi cần.

## Các module chính

### Tổng quan

Màn hình `Tổng quan` hiển thị các chỉ số vận hành chính:

- Tổng số học sinh, lớp học, giáo viên.
- Điểm trung bình toàn trường.
- Phân bố học lực.
- Số học sinh theo lớp.
- Cảnh báo dữ liệu cần theo dõi.
- Hoạt động gần đây.

### Tuyển sinh

Module `Tuyển sinh` quản lý quy trình từ hồ sơ đăng ký đến nhập học:

- Tiếp nhận hồ sơ xét tuyển.
- Lưu thông tin thí sinh, phụ huynh, điểm xét tuyển, lớp dự kiến và hướng học.
- Xét tuyển tự động theo điểm chuẩn.
- Chuyển hồ sơ đạt sang học sinh chính thức.
- Tự động cấp mã học sinh.
- Phân lớp khi nhập học.

### Học sinh

Module `Học sinh` quản lý danh sách học sinh chính thức:

- Thêm, sửa, xóa học sinh.
- Tìm kiếm theo mã hoặc họ tên.
- Lọc theo lớp.
- Sinh mã học sinh tự động.
- Quản lý điểm trung bình cơ bản.

### Tài khoản

Module `Tài khoản` tạo nền tảng phân quyền người dùng:

- Tạo tài khoản học sinh gắn với mã học sinh.
- Lưu mật khẩu ở dạng hash.
- Quản lý vai trò tài khoản.
- Khóa, mở khóa hoặc xóa tài khoản.

Phần này là nền tảng để phát triển luồng học sinh tự đăng nhập và tự đăng ký học phần. Hiện tại ứng dụng desktop vẫn cho phép admin thao tác nghiệp vụ nội bộ.

### Hồ sơ cá nhân

Module `Hồ sơ` mở rộng thông tin học sinh:

- Cập nhật lý lịch.
- Lưu hộ khẩu.
- Lưu thông tin liên hệ phụ huynh.
- Quản lý trạng thái học tập: đang học, bảo lưu, thôi học, tốt nghiệp.
- Quản lý diện chính sách: miễn giảm học phí, hộ nghèo, vùng sâu vùng xa.
- Ghi nhận khen thưởng và kỷ luật.

### Đào tạo và xếp lịch

Module `Đào tạo` quản lý quá trình học tập theo học phần:

- Quản lý môn học.
- Quản lý tín chỉ.
- Khai báo môn học tiên quyết.
- Thiết kế khung chương trình theo khối/kỳ.
- Mở lớp học phần theo môn, giáo viên, lớp sinh hoạt và sĩ số.
- Đăng ký học sinh vào học phần.
- Xếp thời khóa biểu.
- Chặn trùng phòng, trùng giáo viên và trùng lớp trong cùng khung thời gian.
- Ghi nhận điểm danh, đi muộn, vắng học và có phép.

### Khảo thí và điểm số

Module `Khảo thí` quản lý thi và điểm:

- Lập lịch thi theo học phần.
- Chia ca thi, phòng thi và loại kỳ thi.
- Đánh số báo danh.
- Xét điều kiện dự thi dựa trên chuyên cần và điều kiện học phí.
- Nhập điểm thành phần, giữa kỳ, cuối kỳ.
- Tự động tính điểm trung bình thang 10.
- Quy đổi GPA thang 4.
- Xếp loại chữ.
- Tiếp nhận và xử lý phúc khảo.
- Cập nhật lại điểm sau phúc khảo.

### Tài chính và học phí

Module `Tài chính` quản lý nghĩa vụ tài chính của học sinh:

- Lập hóa đơn học phí.
- Tính học phí theo số tín chỉ.
- Tính học phí theo mức thu cố định.
- Ghi nhận thanh toán.
- Quản lý phương thức thanh toán: tiền mặt, chuyển khoản, ví điện tử, thẻ ngân hàng.
- Theo dõi công nợ.
- Quét dữ liệu điểm/GPA để đề xuất học bổng.

Việc kết nối thật với ngân hàng hoặc ví điện tử cần API thanh toán và môi trường tích hợp riêng. Ứng dụng hiện quản lý dữ liệu giao dịch và mã tham chiếu nội bộ.

### Công tác sinh viên và ngoại khóa

Module `Công tác SV` quản lý các hoạt động ngoài học tập chính khóa:

- Chấm điểm rèn luyện theo kỳ.
- Tự động tính tổng điểm và xếp loại rèn luyện.
- Quản lý ký túc xá.
- Lưu thông tin tòa, phòng, giường, ngày vào ở và chi phí điện nước.
- Ghi nhận hoạt động ngoại khóa, CLB, chiến dịch tình nguyện.
- Lưu vai trò và số giờ tham gia.
- Quản lý hồ sơ y tế học đường.
- Lưu lịch khám sức khỏe, trạng thái sức khỏe, số BHYT và hạn BHYT.

### Tốt nghiệp và báo cáo

Module `Tốt nghiệp` quản lý giai đoạn cuối vòng đời học sinh:

- Xét điều kiện tốt nghiệp.
- Kiểm tra chứng chỉ tin học, ngoại ngữ, giáo dục quốc phòng.
- Kiểm tra tín chỉ tích lũy.
- Cấp phát văn bằng.
- Quản lý số hiệu sổ gốc và số hiệu bằng.
- Ghi nhận yêu cầu bảng điểm, giấy xác nhận và báo cáo.
- Tổng hợp thống kê nội bộ phục vụ báo cáo.
- Khảo sát việc làm cựu sinh viên.

Việc in phôi bằng, xuất biểu mẫu có chữ ký số hoặc báo cáo EMIS chuẩn Bộ cần mẫu biểu chính thức và quy trình tích hợp riêng.

### Lớp học

Module `Lớp học` quản lý danh mục lớp:

- Thêm, sửa, xóa lớp.
- Lọc theo khối.
- Theo dõi sĩ số.
- Không cho xóa lớp còn học sinh.

### Giáo viên

Module `Giáo viên` quản lý hồ sơ giáo viên:

- Thêm, sửa, xóa giáo viên.
- Lưu thông tin cá nhân, liên hệ, môn phụ trách.
- Lọc theo trạng thái.
- Kiểm tra email và số điện thoại.

## Quy ước đặt tên file

Các file nghiệp vụ được đặt tên bằng tiếng Anh để thống nhất:

- `student.py`, `student_dao.py`, `student_service.py`
- `school_class.py`, `school_class_dao.py`, `school_class_service.py`
- `teacher.py`, `teacher_dao.py`, `teacher_service.py`
- `admission.py`, `admission_dao.py`, `admission_service.py`
- `training.py`, `training_dao.py`, `training_service.py`
- `exam.py`, `exam_dao.py`, `exam_service.py`
- `finance.py`, `finance_dao.py`, `finance_service.py`
- `graduation.py`, `graduation_dao.py`, `graduation_service.py`

Tên class/model có thể vẫn giữ một số tên đã tồn tại để bảo toàn tương thích logic trong code.

## Tài liệu phân tích nghiệp vụ

Các tài liệu phân tích chi tiết từng nhóm nghiệp vụ nằm trong:

```text
ReportAssets/BTTH06/
```

Các file chính:

- `BTTH06_admissions_analysis.md`
- `BTTH06_student_profiles_analysis.md`
- `BTTH06_training_analysis.md`
- `BTTH06_exams_analysis.md`
- `BTTH06_finance_analysis.md`
- `BTTH06_student_affairs_analysis.md`
- `BTTH06_graduation_analysis.md`

## Cài đặt

Tạo môi trường ảo:

```powershell
python -m venv .venv
```

Kích hoạt môi trường:

```powershell
.venv\Scripts\Activate.ps1
```

Cài thư viện:

```powershell
pip install -r requirements.txt
```

## Chạy ứng dụng

```powershell
cd D:\VisualStudioCode\Projects\HSMS
.venv\Scripts\Activate.ps1
python main.py
```

Khi chạy lần đầu, SQLite database được tạo trong:

```text
data/hsms.db
```

## Kiểm tra nhanh

Kiểm tra cú pháp toàn bộ file Python:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -c "from pathlib import Path; files=[p for p in Path('.').rglob('*.py') if '.venv' not in p.parts and '__pycache__' not in p.parts]; [compile(p.read_text(encoding='utf-8'), str(p), 'exec') for p in files]; print('syntax ok', len(files))"
```

Kiểm tra import app:

```powershell
python -c "from ui.app import HSMSApp; print('app import ok')"
```

## Ghi chú phát triển

- Không commit `.venv`, `__pycache__`, database local hoặc file tạm.
- Khi thêm nghiệp vụ mới, giữ đúng cấu trúc `models -> dao -> services -> ui`.
- Không viết SQL trực tiếp trong UI.
- Không tạo kết nối CSDL trực tiếp trong service.
- Các module mới nên dùng tên file tiếng Anh để thống nhất với cấu trúc hiện tại.
- Các tích hợp ngoài như thanh toán thật, in phôi bằng, chữ ký số, email/SMS hoặc cổng học sinh online cần được tách thành module tích hợp riêng.
