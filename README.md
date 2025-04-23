# Emotion Recognition using Intel® RealSense™ Depth Camera D435i

Dự án này nhằm mục đích nhận diện cảm xúc của người dùng sử dụng Intel® RealSense™ Depth Camera D435i. Hệ thống sử dụng kỹ thuật phát hiện điểm đặc trưng khuôn mặt và mô hình đã được huấn luyện trước để nhận diện cảm xúc.

## Cải tiến mới

- **Tối ưu hóa giao diện người dùng**: Giao diện hiện đại hơn, dễ sử dụng, hỗ trợ hiển thị thông tin rõ ràng.
- **Cải thiện hiệu suất**: Cải thiện việc xử lý video và nhận diện cảm xúc trong thời gian thực.
- **Tổ chức mã nguồn tốt hơn**: Cấu trúc mã nguồn được tổ chức lại để dễ đọc, dễ bảo trì.
- **Xử lý lỗi mạnh mẽ**: Bổ sung xử lý lỗi để hệ thống vận hành ổn định hơn.

## Cấu trúc thư mục

- `data/`: Chứa dữ liệu và mô hình đã huấn luyện sẵn.
- `src/`: Chứa mã nguồn của dự án.
  - `login.py`: Quản lý đăng nhập bằng nhận diện khuôn mặt.
  - `data_collection.py`: Thu thập dữ liệu khuôn mặt người dùng.
  - `gui.py`: Giao diện chính của ứng dụng giám sát.
  - `camera.py`: Quản lý kết nối và luồng video từ camera RealSense.
  - `processor.py`: Xử lý hình ảnh và nhận diện cảm xúc.
  - `face_recognition.py`: Nhận diện khuôn mặt.
  - `arduino_reader.py`: Đọc dữ liệu từ Arduino (nhịp tim).
  - `virtual_assistant.py`: Trợ lý ảo hỗ trợ người dùng.
- `models/`: Chứa các mô hình nhận diện cảm xúc đã được huấn luyện.
- `assets/`: Chứa hình ảnh và tài nguyên của ứng dụng.
- `requirements.txt`: Danh sách các gói Python cần thiết.

## Cài đặt

1. Cài đặt các gói cần thiết:

   ```bash
   pip install -r requirements.txt
   ```

2. Kết nối camera Intel RealSense D435i với máy tính.

3. (Tùy chọn) Kết nối Arduino hoặc thiết bị đo nhịp tim nếu có.

4. Chạy chương trình chính:
   ```bash
   python src/main.py
   ```

## Hướng dẫn sử dụng

1. **Đăng nhập**: Hệ thống sẽ nhận diện khuôn mặt để đăng nhập. Nếu chưa có dữ liệu, bạn sẽ được chuyển đến trang thu thập dữ liệu.

2. **Thu thập dữ liệu**: Nhập tên và tuổi, sau đó nhấn "Bắt Đầu Thu Thập" để chụp các khung hình khuôn mặt. Hệ thống sẽ tự động huấn luyện mô hình.

3. **Giao diện chính**: Sau khi đăng nhập, bạn sẽ thấy giao diện giám sát với:

   - Hiển thị video camera chính và bản đồ độ sâu
   - Thông tin cảm xúc và cảnh báo
   - Thông tin nhịp tim (nếu có kết nối Arduino)
   - Chọn cổng COM để kết nối Arduino

4. **Điều chỉnh kết nối**: Chọn cổng COM phù hợp và nhấn "Xác Nhận" để kết nối với Arduino đo nhịp tim.

## Yêu cầu hệ thống

- Python 3.7 trở lên
- Camera Intel RealSense D435i
- Arduino (tùy chọn) để đo nhịp tim
- Windows 10/11 hoặc Linux
- Ít nhất 8GB RAM
- GPU (khuyến nghị) để cải thiện hiệu suất
