# Ứng Dụng Web Nhận Diện Cảm Xúc

Ứng dụng web này là phiên bản web của hệ thống giám sát quá trình tập luyện, sử dụng Flask làm backend và HTML/CSS/JavaScript với Tailwind CSS làm frontend.

## Tính năng

- Hiển thị video từ camera thời gian thực
- Hiển thị bản đồ độ sâu từ camera RealSense
- Nhận diện cảm xúc từ khuôn mặt
- Theo dõi nhịp tim thông qua kết nối Arduino
- Phát hiện các trạng thái cảm xúc bất thường và cảnh báo
- Giao diện responsive, hoạt động trên nhiều thiết bị
- Thông báo trạng thái thời gian thực

## Cài đặt

### Yêu cầu hệ thống

- Python 3.7+
- Camera Intel RealSense
- Arduino (tùy chọn, để đọc nhịp tim)
- Các thư viện Python:
  - Flask
  - OpenCV
  - NumPy
  - PySerial

### Bước cài đặt

1. Cài đặt các thư viện Python cần thiết:

```bash
pip install flask opencv-python numpy pyserial pyrealsense2
```

2. Clone hoặc tải xuống repository:

```bash
git clone <repository-url>
cd <repository-folder>
```

3. Khởi động ứng dụng:

```bash
python web/app.py
```

4. Mở trình duyệt web và truy cập:

```
http://localhost:5000
```

## Cấu trúc thư mục

```
web/
├── app.py              # Ứng dụng Flask chính
├── static/             # Tài nguyên tĩnh
│   ├── css/
│   │   └── style.css   # File CSS chính
│   └── js/
│       └── main.js     # JavaScript chính
├── templates/          # Templates HTML
│   └── index.html      # Trang chủ
└── README.md           # Tài liệu này
```

## Sử dụng

1. **Khởi động ứng dụng**: Chạy `python web/app.py` để khởi động máy chủ Flask.

2. **Xem luồng video**: Khi ứng dụng khởi động, bạn sẽ thấy hai luồng video - một cho camera màu và một cho bản đồ độ sâu.

3. **Kết nối Arduino**:

   - Chọn cổng COM từ danh sách thả xuống.
   - Nhấn "Xác Nhận" để kết nối.
   - Trạng thái kết nối sẽ được hiển thị trong phần "Trạng thái".

4. **Giám sát**:

   - "Cảm Xúc" hiển thị cảm xúc được phát hiện (Bình thường/Bất thường).
   - "Cảnh Báo" hiển thị thông báo cảnh báo nếu cần nghỉ ngơi.
   - "Nhịp Tim" hiển thị nhịp tim từ Arduino.

5. **Thoát ứng dụng**: Nhấn nút "Thoát" để đóng ứng dụng và giải phóng tài nguyên.

## Hướng dẫn phát triển

### Thêm cảm xúc mới

Để thêm loại cảm xúc mới cần được nhận diện:

1. Cập nhật mô hình trong thư mục `src`.
2. Sửa hàm `predict_emotion` và `get_emotion_text` trong class `EmotionRecognitionProcessor`.
3. Cập nhật điều kiện xử lý cảm xúc trong hàm `generate_frames` trong `app.py`.

### Tùy chỉnh giao diện

- Các thành phần giao diện sử dụng Tailwind CSS và CSS tùy chỉnh.
- Sửa đổi file `static/css/style.css` để thay đổi kiểu dáng.
- Sửa đổi file `templates/index.html` để thay đổi cấu trúc HTML.

### Thêm chức năng mới

1. Thêm route mới trong `app.py`:

```python
@app.route('/new-feature')
def new_feature():
    # Logic của chức năng mới
    return render_template('new_feature.html')
```

2. Tạo template HTML mới trong thư mục `templates`.
3. Thêm JavaScript để xử lý chức năng mới trong `static/js/`.

## Xử lý sự cố

### Camera không hoạt động

- Đảm bảo camera RealSense được kết nối đúng cách.
- Kiểm tra xem SDK RealSense đã được cài đặt.
- Khởi động lại ứng dụng.

### Kết nối Arduino thất bại

- Kiểm tra xem cổng COM đã chọn có chính xác không.
- Đảm bảo Arduino đã được nạp code đúng.
- Kiểm tra dây nối giữa Arduino và máy tính.

### Lỗi server

- Kiểm tra log console để xem thông báo lỗi.
- Đảm bảo tất cả các thư viện Python cần thiết đã được cài đặt.
- Kiểm tra xem cổng 5000 đã được sử dụng bởi ứng dụng khác chưa.

## Đóng góp

Nếu bạn muốn đóng góp cho dự án, hãy làm theo các bước sau:

1. Fork repository
2. Tạo branch mới (`git checkout -b feature/amazing-feature`)
3. Commit các thay đổi (`git commit -m 'Add some amazing feature'`)
4. Push lên branch (`git push origin feature/amazing-feature`)
5. Mở Pull Request

## Giấy phép

Dự án này được phân phối dưới giấy phép [MIT](LICENSE).

## Liên hệ

Nếu bạn có bất kỳ câu hỏi nào, vui lòng liên hệ [email@example.com].

---

Phát triển bởi [Tên của bạn] - © 2023
