# Phase 7 - Responsive và truy cập nhiều thiết bị

## Mục tiêu

Phase 7 tập trung làm cho phiên bản HSMS Web sử dụng được trên nhiều kích thước màn hình và nhiều nhóm thiết bị: điện thoại, tablet, laptop và desktop. Phần này không thay đổi logic nghiệp vụ, không thay đổi dữ liệu, chỉ gia cố giao diện, khả năng truy cập và kiểm tra phân quyền khi truy cập từ thiết bị nhỏ.

## Phần đã thực hiện trong code

1. Thanh điều hướng đã chuyển sang off-canvas trên màn hình nhỏ.

   Trước đây thanh menu dùng `collapse` nên khi số lượng module nhiều, các mục có thể bị chèn ép. Hiện tại `app/templates/components/nav.html` đã dùng Bootstrap off-canvas, giúp menu tách khỏi vùng nội dung trên mobile và tablet.

2. Bổ sung kích thước thao tác cảm ứng.

   Các nút chính và liên kết trong thanh điều hướng có `min-height: 44px`, giúp dễ thao tác trên điện thoại và tablet.

3. Chặn tràn ngang toàn trang.

   `html` và `body` đã được cấu hình `max-width: 100%` và `overflow-x: hidden`. Các bảng dữ liệu vẫn giữ khả năng cuộn bên trong wrapper thay vì làm cả trang bị cuộn ngang.

4. Bảng dữ liệu có wrapper responsive.

   Các màn hình nền như học sinh, lớp học, giáo viên, tài khoản, activity log, tuyển sinh và hồ sơ học sinh đã dùng `table-responsive`. CSS bổ sung `max-width: 100%` và `min-width` hợp lý cho bảng để dữ liệu không bị vỡ layout.

5. Form và bộ lọc co giãn tốt hơn.

   `filter-bar`, `form-grid`, `page-header`, panel và metric card được bổ sung giới hạn responsive để tránh hiện tượng ô nhập, select hoặc button chen lấn nhau ở màn hình nhỏ.

6. Modal không vượt chiều cao màn hình.

   Modal được giới hạn bằng `max-height: calc(100vh - 1rem)` và phần thân modal có cuộn dọc nội bộ.

7. Biểu đồ và danh sách dashboard co giãn.

   Kích thước số liệu trên dashboard dùng `clamp()`, danh sách biểu đồ và activity log có `overflow-wrap` để không tràn khi nội dung dài.

8. Kiểm tra phân quyền khi truy cập bằng mobile route.

   Test mới xác nhận tài khoản học sinh chỉ xem hồ sơ của chính mình qua `/profiles/me` và bị chặn `403` khi truy cập danh sách quản trị `/students/`.

## File đã thay đổi

- `app/templates/components/nav.html`
- `app/templates/layouts/base.html`
- `app/static/css/app.css`
- `tests/test_responsive_access.py`
- `README.md`

## Kiểm tra tự động đã chạy

```text
python -m pytest -p no:cacheprovider tests
Kết quả: 36 passed
```

```text
python -m compileall app tests
Kết quả: compile thành công
```

```text
rg "customtkinter|CTk|tkinter" app tests
Kết quả: không phát hiện phụ thuộc CustomTkinter/tkinter trong web app
```

## Phần cần kiểm thử thủ công trên thiết bị thật

Các mục dưới đây không thể được xác nhận hoàn toàn trong môi trường agent vì cần trình duyệt, thiết bị và mạng thật:

- Chrome hoặc Edge trên Windows.
- Trình duyệt Android thật.
- iPhone hoặc iPad thật.
- Truy cập bằng mạng 4G/5G.
- Hai thiết bị đăng nhập đồng thời.

Checklist kiểm thử thủ công:

1. Mở web ở độ rộng 360 px, kiểm tra menu chuyển thành off-canvas, form không tràn, button đủ lớn.
2. Mở web ở độ rộng 768 px, kiểm tra bảng nằm trong vùng cuộn riêng, không làm toàn trang cuộn ngang.
3. Mở web ở độ rộng 1024 px, kiểm tra layout dashboard, form và bảng vẫn cân đối.
4. Mở web ở độ rộng 1280 px trở lên, kiểm tra menu desktop hiển thị đầy đủ.
5. Đăng nhập admin trên máy tính, đăng nhập student/teacher trên điện thoại, xác nhận session độc lập.
6. Dùng tài khoản student thử truy cập URL quản trị như `/students/`, hệ thống phải trả `403`.
7. Dùng tài khoản teacher kiểm tra chỉ thấy phạm vi được phân công.
8. Dùng điện thoại bật 4G/5G truy cập domain triển khai sau khi hoàn thành tunnel và Cloudflare Access.

## Kết luận

Phase 7 đã hoàn thành phần code-side: responsive layout, off-canvas navigation, bảng/form/modal an toàn hơn trên màn hình nhỏ, kiểm tra quyền phía server và test tự động. Phần kiểm thử thiết bị thật sẽ được thực hiện sau khi web được chạy trong môi trường VM/Docker và có URL truy cập qua Cloudflare.
