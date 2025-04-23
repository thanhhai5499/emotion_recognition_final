import sys
import os
import threading
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import tkinter as tk
from tkinter import Label, Button, ttk
from PIL import Image, ImageTk
import cv2
import time
import serial.tools.list_ports
from src.camera import RealSenseCamera
from src.processor import EmotionRecognitionProcessor
from src.arduino_reader import ArduinoReader
from src.virtual_assistant import VirtualAssistant

class EmotionRecognitionApp:
    # Định nghĩa các hằng số màu và thiết kế
    BG_COLOR = "#f0f0f0"
    BORDER_COLOR = "#cccccc"
    LABEL_BG = "#0288d1"
    LABEL_FG = "white"
    VALUE_BG = "white"
    VALUE_FG = "#333333"
    BUTTON_GREEN = "#4CAF50"
    BUTTON_GREEN_ACTIVE = "#388E3C"
    BUTTON_RED = "#f44336"
    BUTTON_RED_ACTIVE = "#d32f2f"
    BUTTON_BLUE = "#2196F3"
    WARNING_COLOR = "#FF9800"
    ERROR_COLOR = "#FF0000"
    SUCCESS_COLOR = "#4CAF50"
    TITLE_COLOR = "#3366cc"
    COMPANY_COLOR = "#FF4040"
    ABNORMAL_COLOR = "#FF5722"
    
    def __init__(self, root):
        """Khởi tạo ứng dụng nhận diện cảm xúc"""
        self.root = root
        self.root.title("Nhận Diện Tình Trạng")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg=self.BG_COLOR)

        # Khởi tạo biến thành viên
        self.camera = None
        self.processor = None
        self.arduino_reader = None
        self.arduino_connected = False
        
        # Thiết lập giao diện
        self._setup_styles()
        self._create_logo_and_title()
        self._create_video_frames()
        self._create_info_frames()
        self._create_control_buttons()
        
        # Áp dụng bo tròn góc và kiểu dáng
        self.root.update()
        self._apply_frame_styling()
        
        # Khởi tạo và chạy trợ lý ảo
        self._initialize_virtual_assistant()
        
        # Khởi tạo hệ thống camera và bộ xử lý
        self._initialize_camera_system()
        
        # Bắt đầu cập nhật video nếu camera và bộ xử lý khả dụng
        if self.camera and self.processor:
            self.update_video()

    def _setup_styles(self):
        """Thiết lập style cho các thành phần giao diện"""
        self.style = ttk.Style()
        self.style.configure("TCombobox", 
                            padding=5, 
                            borderwidth=2, 
                            font=("Helvetica", 16))
        self.style.map("TCombobox", 
                      fieldbackground=[("readonly", "#ffffff")])

    def _create_logo_and_title(self):
        """Tạo logo và tiêu đề ứng dụng"""
        # Logo trái
        try:
            self.icon_image = Image.open("assets/Logo.png")
            self.icon_image_resized = self.icon_image.resize((200, 200), Image.LANCZOS)
            self.icon_photo = ImageTk.PhotoImage(self.icon_image_resized)
            self.root.iconphoto(False, self.icon_photo)
            
            self.logo_label = Label(self.root, bg=self.BG_COLOR)
            self.logo_label.pack(side="top", anchor="nw", padx=10, pady=2)
            self._display_large_logo()
            
            # Logo phải
            self.right_logo_image = Image.open("assets/logo2.png")
            self.right_logo_image_resized = self.right_logo_image.resize((380, 100), Image.LANCZOS)
            self.right_logo_photo = ImageTk.PhotoImage(self.right_logo_image_resized)
            self.right_logo_label = Label(self.root, image=self.right_logo_photo, bg=self.BG_COLOR)
            self.right_logo_label.place(x=self.root.winfo_screenwidth()-400, y=10)
        except Exception as e:
            print(f"Lỗi khi tải logo: {e}")
            
        # Tiêu đề và tên công ty
        self.management_company_label = Label(
            self.root, 
            text="BAN QUẢN LÝ KHU CÔNG NGHỆ CAO THÀNH PHỐ HỒ CHÍ MINH", 
            font=("Helvetica", 26, "bold"), 
            fg=self.COMPANY_COLOR, 
            bg=self.BG_COLOR
        )
        self.management_company_label.place(relx=0.5, rely=0.05, anchor=tk.CENTER)
        
        self.company_label = Label(
            self.root, 
            text="TRUNG TÂM NGHIÊN CỨU TRIỂN KHAI KHU CÔNG NGHỆ CAO", 
            font=("Helvetica", 26, "bold"), 
            fg=self.COMPANY_COLOR, 
            bg=self.BG_COLOR
        )
        self.company_label.place(relx=0.5, rely=0.095, anchor=tk.CENTER)
        
        self.title_label = Label(
            self.root, 
            text="HỆ THỐNG GIÁM SÁT QUÁ TRÌNH TẬP LUYỆN", 
            font=("Helvetica", 24, "bold"), 
            fg=self.TITLE_COLOR, 
            bg=self.BG_COLOR
        )
        self.title_label.place(relx=0.5, rely=0.145, anchor=tk.CENTER)
        
        # Thông báo
        self.message_frame = tk.Frame(self.root, bg=self.BORDER_COLOR, bd=2, relief="groove")
        self.message_frame.place(relx=0.78, rely=0.12, relwidth=0.2, relheight=0.05)
        
        self.special_message = Label(
            self.message_frame, 
            text="Thông báo", 
            font=("Helvetica", 18), 
            fg=self.VALUE_FG, 
            bg=self.VALUE_BG, 
            anchor="center"
        )
        self.special_message.pack(fill=tk.BOTH, expand=True)

    def _create_video_frames(self):
        """Tạo khung hiển thị video và depth map"""
        # Frame chứa video
        self.video_container = tk.Frame(
            self.root, 
            bg=self.BORDER_COLOR, 
            bd=1, 
            relief="solid"
        )
        self.video_container.place(relx=0.02, rely=0.18, relwidth=0.47, relheight=0.6)
        
        self.video_frame = Label(self.video_container, bg="black")
        self.video_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Frame chứa depth map
        self.depth_container = tk.Frame(
            self.root, 
            bg=self.BORDER_COLOR, 
            bd=1, 
            relief="solid"
        )
        self.depth_container.place(relx=0.51, rely=0.18, relwidth=0.47, relheight=0.6)
        
        self.depth_frame = Label(self.depth_container, bg="black")
        self.depth_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

    def _create_info_frames(self):
        """Tạo các khung hiển thị thông tin"""
        # Frame hiển thị cảm xúc
        self.emotion_frame = tk.Frame(self.root, bg=self.BORDER_COLOR, relief="solid", bd=1)
        self.emotion_frame.place(relx=0.02, rely=0.81, relwidth=0.47, relheight=0.05)
        
        self.emotion_label = Label(
            self.emotion_frame, 
            text="Cảm Xúc:", 
            font=("Helvetica", 18, "bold"), 
            fg=self.LABEL_FG, 
            bg=self.LABEL_BG, 
            anchor="w", 
            padx=10
        )
        self.emotion_label.place(relx=0, rely=0, relwidth=0.5, relheight=1)
        
        self.emotion_value = Label(
            self.emotion_frame, 
            text="", 
            font=("Helvetica", 18), 
            fg=self.VALUE_FG, 
            bg=self.VALUE_BG, 
            anchor="center"
        )
        self.emotion_value.place(relx=0.5, rely=0, relwidth=0.5, relheight=1)
        
        # Frame hiển thị cảnh báo
        self.rest_frame = tk.Frame(self.root, bg=self.BORDER_COLOR, relief="solid", bd=1)
        self.rest_frame.place(relx=0.02, rely=0.88, relwidth=0.47, relheight=0.05)
        
        self.rest_message = Label(
            self.rest_frame, 
            text="Cảnh Báo:", 
            font=("Helvetica", 18, "bold"), 
            fg=self.LABEL_FG, 
            bg=self.LABEL_BG, 
            anchor="w", 
            padx=10
        )
        self.rest_message.place(relx=0, rely=0, relwidth=0.5, relheight=1)
        
        self.rest_value = Label(
            self.rest_frame, 
            text="", 
            font=("Helvetica", 18), 
            fg=self.ERROR_COLOR, 
            bg=self.VALUE_BG, 
            anchor="center"
        )
        self.rest_value.place(relx=0.5, rely=0, relwidth=0.5, relheight=1)
        
        # Frame hiển thị nhịp tim
        self.heart_frame = tk.Frame(self.root, bg=self.BORDER_COLOR, relief="solid", bd=1)
        self.heart_frame.place(relx=0.51, rely=0.81, relwidth=0.47, relheight=0.05)
        
        self.heart_rate_label = Label(
            self.heart_frame, 
            text="Nhịp Tim:", 
            font=("Helvetica", 18, "bold"), 
            fg=self.LABEL_FG, 
            bg=self.LABEL_BG, 
            anchor="w", 
            padx=10
        )
        self.heart_rate_label.place(relx=0, rely=0, relwidth=0.5, relheight=1)
        
        self.heart_rate_value = Label(
            self.heart_frame, 
            text="Đang đọc...", 
            font=("Helvetica", 18), 
            fg=self.VALUE_FG, 
            bg=self.VALUE_BG, 
            anchor="center"
        )
        self.heart_rate_value.place(relx=0.5, rely=0, relwidth=0.5, relheight=1)
        
        # Frame chọn cổng COM
        self.com_frame = tk.Frame(self.root, bg=self.BORDER_COLOR, relief="solid", bd=1)
        self.com_frame.place(relx=0.51, rely=0.88, relwidth=0.47, relheight=0.05)
        
        self.com_label = Label(
            self.com_frame, 
            text="COM:", 
            font=("Helvetica", 18, "bold"), 
            fg=self.LABEL_FG, 
            bg=self.LABEL_BG, 
            anchor="w", 
            padx=10
        )
        self.com_label.place(relx=0, rely=0, relwidth=0.3, relheight=1)
        
        # Combobox chọn cổng COM
        self.combobox = ttk.Combobox(
            self.com_frame, 
            font=("Helvetica", 16), 
            state="readonly"
        )
        self.combobox.place(relx=0.31, rely=0.1, relwidth=0.35, relheight=0.8)
        self.populate_com_ports()
        
        # Nút xác nhận cổng COM
        self.connect_button = Button(
            self.com_frame, 
            text="Xác Nhận", 
            font=("Helvetica", 14, "bold"), 
            bg=self.BUTTON_GREEN, 
            fg=self.LABEL_FG, 
            activebackground=self.BUTTON_GREEN_ACTIVE,
            relief="flat", 
            command=self.connect_arduino, 
            bd=1
        )
        self.connect_button.place(relx=0.67, rely=0.1, relwidth=0.30, relheight=0.8)

    def _create_control_buttons(self):
        """Tạo các nút điều khiển"""
        # Nút thoát
        self.exit_button = Button(
            self.root, 
            text="Thoát", 
            font=("Helvetica", 16, "bold"), 
            bg=self.BUTTON_RED, 
            fg=self.LABEL_FG, 
            activebackground=self.BUTTON_RED_ACTIVE,
            relief="flat", 
            command=self.close_app, 
            bd=1
        )
        self.exit_button.place(relx=0.92, rely=0.94, relwidth=0.06, relheight=0.04)

    def _apply_frame_styling(self):
        """Áp dụng kiểu dáng cho các frame"""
        frames = [
            self.video_container, self.depth_container, self.message_frame,
            self.emotion_frame, self.rest_frame, self.heart_frame, self.com_frame
        ]
        
        for frame in frames:
            frame.config(
                highlightthickness=1, 
                highlightbackground=self.BORDER_COLOR, 
                relief="solid", 
                bd=1
            )

    def _display_large_logo(self):
        """Hiển thị logo lớn ở góc trên trái"""
        try:
            large_logo_image = self.icon_image.resize((200, 200), Image.LANCZOS)
            large_logo_photo = ImageTk.PhotoImage(large_logo_image)
            self.logo_label.config(image=large_logo_photo)
            self.logo_label.image = large_logo_photo
        except Exception as e:
            print(f"Lỗi khi hiển thị logo lớn: {e}")

    def _initialize_virtual_assistant(self):
        """Khởi tạo và chạy trợ lý ảo"""
        try:
            self.assistant = VirtualAssistant(self.heart_rate_value, self.emotion_value)
            assistant_thread = threading.Thread(target=self.assistant.start_listening, daemon=True)
            assistant_thread.start()
        except Exception as e:
            print(f"Lỗi khi khởi tạo trợ lý ảo: {e}")
            self.special_message.config(text="Lỗi trợ lý ảo", bg=self.ERROR_COLOR, fg=self.LABEL_FG)

    def _initialize_camera_system(self):
        """Khởi tạo hệ thống camera và bộ xử lý"""
        try:
            self.camera = RealSenseCamera()
            self.processor = EmotionRecognitionProcessor()
            self.special_message.config(text="")
        except Exception as e:
            print(f"Lỗi khi khởi tạo camera: {e}")
            self.special_message.config(text="Không tìm thấy camera!", bg=self.ERROR_COLOR, fg=self.LABEL_FG)
            self.camera = None
            self.processor = None

    def populate_com_ports(self):
        """Lấy danh sách các cổng COM và điền vào combobox"""
        try:
            ports = serial.tools.list_ports.comports()
            com_list = [port.device for port in ports]
            if com_list:
                self.combobox['values'] = com_list
                self.combobox.current(0)  # Chọn cổng COM đầu tiên làm mặc định
        except Exception as e:
            print(f"Lỗi khi lấy danh sách cổng COM: {e}")
            self.special_message.config(
                text="Không thể lấy danh sách COM", 
                bg=self.WARNING_COLOR, 
                fg=self.LABEL_FG
            )

    def connect_arduino(self):
        """Kết nối Arduino với cổng COM được chọn và bắt đầu đọc dữ liệu"""
        # Đóng kết nối hiện tại nếu có
        if self.arduino_reader:
            self._close_arduino_connection()
        
        selected_port = self.combobox.get()
        if not selected_port:
            self.special_message.config(
                text="Không có cổng COM nào được chọn!", 
                bg=self.ERROR_COLOR, 
                fg=self.LABEL_FG
            )
            return
            
        try:
            self.arduino_reader = ArduinoReader(port=selected_port)
            self.arduino_connected = True
            self.special_message.config(
                text="Arduino đã được kết nối.", 
                bg=self.SUCCESS_COLOR, 
                fg=self.LABEL_FG
            )
            self.connect_button.config(
                bg=self.SUCCESS_COLOR, 
                activebackground=self.BUTTON_GREEN_ACTIVE
            )
            # Lên lịch cập nhật nhịp tim
            self.schedule_heart_rate_update()
        except Exception as e:
            self.special_message.config(
                text=f"Không thể kết nối Arduino! {str(e)}", 
                bg=self.ERROR_COLOR, 
                fg=self.LABEL_FG
            )
            self.connect_button.config(
                bg=self.BUTTON_BLUE, 
                activebackground=self.BUTTON_GREEN_ACTIVE
            )
            self.arduino_connected = False
            self.arduino_reader = None

    def _close_arduino_connection(self):
        """Đóng kết nối Arduino hiện tại"""
        try:
            if self.arduino_reader and hasattr(self.arduino_reader, 'serial_connection'):
                self.arduino_reader.serial_connection.close()
        except Exception as e:
            print(f"Lỗi khi đóng kết nối Arduino: {e}")
        finally:
            self.arduino_reader = None
            self.arduino_connected = False
            
    def schedule_heart_rate_update(self):
        """Lên lịch cập nhật nhịp tim để tránh nhiều lần cập nhật chạy đồng thời"""
        if not self.arduino_connected or not self.arduino_reader:
            return
            
        # Hủy tất cả các lịch cập nhật nhịp tim đang chờ (nếu có)
        try:
            for after_id in self.root.tk.call('after', 'info'):
                if 'update_heart_rate' in self.root.tk.call('after', 'info', after_id):
                    self.root.after_cancel(int(after_id))
        except Exception as e:
            print(f"Lỗi khi hủy lịch cập nhật nhịp tim: {e}")
            
        # Bắt đầu cập nhật nhịp tim
        self.update_heart_rate()

    def update_heart_rate(self):
        """Cập nhật nhịp tim từ Arduino"""
        if not self.arduino_connected or not self.arduino_reader:
            return
            
        try:
            heart_rate = self.arduino_reader.read_data()
            if heart_rate is not None:
                # Thay đổi màu sắc dựa trên nhịp tim
                color = self._get_heart_rate_color(heart_rate)
                self.heart_rate_value.config(text=str(heart_rate), fg=color)
        except Exception as e:
            print(f"Lỗi khi đọc nhịp tim: {e}")
            self.heart_rate_value.config(text="Lỗi kết nối", fg=self.ERROR_COLOR)
            self.arduino_connected = False
            
        # Lên lịch cập nhật tiếp theo chỉ khi vẫn còn kết nối
        if self.arduino_connected and self.arduino_reader:
            self.root.after(1000, self.update_heart_rate)

    def _get_heart_rate_color(self, heart_rate):
        """Xác định màu hiển thị dựa trên nhịp tim"""
        if heart_rate > 100:
            return self.ERROR_COLOR  # Màu đỏ cho nhịp tim cao
        elif heart_rate < 60:
            return self.WARNING_COLOR  # Màu cam cho nhịp tim thấp
        else:
            return self.SUCCESS_COLOR  # Màu xanh lá cho nhịp tim bình thường

    def update_video(self):
        """Cập nhật hiển thị video và xử lý nhận diện cảm xúc"""
        if self.camera is None or self.processor is None:
            return

        try:
            ret, color_image, depth_image = self.camera.get_frames()
            if ret:
                self._process_video_frame(color_image, depth_image)
                
            # Kiểm tra trạng thái từ trợ lý ảo
            if hasattr(self, 'assistant'):
                self.assistant.check_heart_rate()
                self.assistant.check_conditions()
        except Exception as e:
            print(f"Lỗi khi cập nhật video: {e}")
            self.special_message.config(text="Lỗi camera", bg=self.ERROR_COLOR, fg=self.LABEL_FG)
        
        # Lưu ID của after để có thể hủy nó khi cần
        self._after_id = self.root.after(50, self.update_video)

    def _process_video_frame(self, color_image, depth_image):
        """Xử lý khung hình video và cập nhật hiển thị"""
        current_time = time.time()
        if current_time - self.processor.last_update_time >= 0.05:
            # Xử lý khung hình và nhận diện khuôn mặt
            frame_with_landmarks, faces, landmarks = self.processor.process_frame1(color_image)
            
            # Kiểm tra khuôn mặt và cập nhật thông báo
            if len(faces) == 0:
                self.special_message.config(
                    text="Không tìm thấy khuôn mặt!", 
                    bg=self.WARNING_COLOR, 
                    fg=self.LABEL_FG
                )
            else:
                self.special_message.config(text="", bg=self.VALUE_BG, fg=self.VALUE_FG)
                self._process_emotion(color_image)
                
            self.processor.last_update_time = current_time
            
            # Cập nhật hiển thị video
            self._update_video_display(frame_with_landmarks, depth_image)

    def _process_emotion(self, color_image):
        """Xử lý và cập nhật trạng thái cảm xúc"""
        emotion = self.processor.predict_emotion(color_image)
        if emotion is not None:
            emotion_text = self.processor.get_emotion_text(emotion)
            
            # Kiểm tra trạng thái cảm xúc
            if emotion_text == "Bất thường":
                if self.processor.current_emotion == emotion_text:
                    emotion_duration = time.time() - self.processor.emotion_start_time
                    if emotion_duration >= 3:
                        # Cảm xúc bất thường kéo dài trên 3 giây
                        self.emotion_value.config(text="Bất thường", fg=self.ABNORMAL_COLOR)
                        self.rest_value.config(
                            text="Cần nghỉ ngơi", 
                            fg=self.ERROR_COLOR, 
                            font=("Helvetica", 18, "bold")
                        )
                    elif emotion_duration < 2:
                        # Cảm xúc bất thường xuất hiện dưới 2 giây
                        self.emotion_value.config(text="Bình thường", fg=self.SUCCESS_COLOR)
                else:
                    # Cảm xúc bất thường mới xuất hiện, bắt đầu đếm thời gian
                    self.processor.current_emotion = emotion_text
                    self.processor.emotion_start_time = time.time()
            else:
                # Cảm xúc bình thường
                self.processor.current_emotion = None
                self.processor.emotion_start_time = None
                self.emotion_value.config(text="Bình thường", fg=self.SUCCESS_COLOR)
                self.rest_value.config(text="", fg=self.ERROR_COLOR)

    def _update_video_display(self, frame_with_landmarks, depth_image):
        """Cập nhật hiển thị video và depth map"""
        try:
            # Xử lý và hiển thị video màu
            cv2image_color = cv2.cvtColor(frame_with_landmarks, cv2.COLOR_BGR2RGBA)
            img_color = Image.fromarray(cv2image_color)
            
            # Tính toán kích thước mới
            new_width = int(0.47 * self.root.winfo_width() - 10)
            new_height = int(0.6 * self.root.winfo_height() - 10)
            
            # Resize và hiển thị video
            img_color = img_color.resize((new_width, new_height))
            imgtk_color = ImageTk.PhotoImage(image=img_color)
            self.video_frame.imgtk = imgtk_color
            self.video_frame.configure(image=imgtk_color)
            
            # Xử lý và hiển thị depth map
            depth_colormap = cv2.applyColorMap(
                cv2.convertScaleAbs(depth_image, alpha=0.03), 
                cv2.COLORMAP_JET
            )
            cv2image_depth = cv2.cvtColor(depth_colormap, cv2.COLOR_BGR2RGBA)
            img_depth = Image.fromarray(cv2image_depth)
            
            # Resize và hiển thị depth map
            img_depth = img_depth.resize((new_width, new_height))
            imgtk_depth = ImageTk.PhotoImage(image=img_depth)
            self.depth_frame.imgtk = imgtk_depth
            self.depth_frame.configure(image=imgtk_depth)
        except Exception as e:
            print(f"Lỗi khi cập nhật hiển thị video: {e}")

    def close_app(self):
        """Đóng ứng dụng và giải phóng tài nguyên"""
        try:
            # Dừng cập nhật video
            if hasattr(self, '_after_id'):
                self.root.after_cancel(self._after_id)
            
            # Giải phóng tài nguyên camera
            if hasattr(self, 'camera') and self.camera:
                try:
                    self.camera.release()
                except Exception as e:
                    print(f"Lỗi khi giải phóng camera: {e}")
            
            # Đóng kết nối Arduino
            if hasattr(self, 'arduino_reader') and self.arduino_reader:
                try:
                    if hasattr(self.arduino_reader, 'serial_connection'):
                        self.arduino_reader.serial_connection.close()
                except Exception as e:
                    print(f"Lỗi khi đóng kết nối Arduino: {e}")
        except Exception as e:
            print(f"Lỗi khi đóng tài nguyên: {e}")
        finally:
            # Hủy tất cả các after đang chờ
            for after_id in self.root.tk.call('after', 'info'):
                self.root.after_cancel(int(after_id))
                
            # Đóng cửa sổ và kết thúc chương trình
            self.root.destroy()
            sys.exit(0)

if __name__ == "__main__":
    root = tk.Tk()
    app = EmotionRecognitionApp(root)
    root.mainloop()
