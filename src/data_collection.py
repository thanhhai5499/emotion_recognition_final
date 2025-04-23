import os
import time
import tkinter as tk
from tkinter import Label, Entry, Button, Frame
from PIL import Image, ImageTk
import cv2
from threading import Thread
from src.camera import RealSenseCameraNew
from src.processor import EmotionRecognitionProcessor

class UserDataCollectionApp:
    # Định nghĩa các hằng số màu và thiết kế
    BG_COLOR = "#f0f0f0"
    BORDER_COLOR = "#cccccc"
    LABEL_BG = "#0088d1"
    LABEL_FG = "white"
    VALUE_BG = "white"
    VALUE_FG = "#333333"
    BUTTON_GREEN = "#4CAF50"
    BUTTON_GREEN_ACTIVE = "#388E3C"
    BUTTON_RED = "#f44336"
    BUTTON_RED_ACTIVE = "#d32f2f"
    SUCCESS_COLOR = "#4CAF50"
    ERROR_COLOR = "#ff0000"
    TITLE_COLOR = "#3366cc"
    COMPANY_COLOR = "#FF0000"
    TEXT_COLOR = "#333333"
    INPUT_BG = "#f5f5f5"
    
    # Thời gian thu thập dữ liệu (giây)
    CAPTURE_DURATION = 5
    
    def __init__(self, root):
        """Khởi tạo ứng dụng thu thập dữ liệu người dùng"""
        self.root = root
        self.root.title("Thu Thập Dữ Liệu")
        
        # Khởi tạo biến thành viên
        self.camera = None
        self.processor = None
        self.capturing = False
        
        # Thiết lập giao diện
        self._configure_window()
        self._create_logo_and_title()
        self._create_video_frame()
        self._create_user_info_frame()
        self._create_message_frame()
        self._create_control_buttons()
        
        # Khởi tạo camera và bộ xử lý
        self._initialize_camera_system()
        
        # Bắt đầu cập nhật video
        if self.camera and self.processor:
            self.update_video()
            
    def _configure_window(self):
        """Cấu hình cửa sổ chính của ứng dụng"""
        # Thiết lập chế độ full-screen
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg=self.BG_COLOR)
        
        # Lưu kích thước màn hình để sử dụng sau này
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        
    def _create_logo_and_title(self):
        """Tạo logo và tiêu đề ứng dụng"""
        # Logo trái
        try:
            self.icon_image = Image.open("assets/Logo.png")
            self.icon_image_resized = self.icon_image.resize((250, 250), Image.LANCZOS)
            self.icon_photo = ImageTk.PhotoImage(self.icon_image_resized)
            self.root.iconphoto(False, self.icon_photo)

            self.logo_label = Label(self.root, image=self.icon_photo, bg=self.BG_COLOR)
            self.logo_label.place(x=20, y=20)

        except Exception as e:
            print(f"Lỗi khi tải logo: {e}")


        
        self.company_label = Label(
            self.root, 
            text="TRƯỜNG TRUNG HỌC PHỔ THÔNG CHUYÊN TRẦN ĐẠI NGHĨA", 
            font=("Helvetica", 26, "bold"), 
            fg=self.COMPANY_COLOR, 
            bg=self.BG_COLOR
        )
        self.company_label.place(relx=0.5, rely=0.1, anchor=tk.CENTER)
        
        self.title_label = Label(
            self.root, 
            text="HỆ THỐNG GIÁM SÁT QUÁ TRÌNH TẬP LUYỆN", 
            font=("Helvetica", 24, "bold"), 
            fg=self.TITLE_COLOR, 
            bg=self.BG_COLOR
        )
        self.title_label.place(relx=0.5, rely=0.18, anchor=tk.CENTER)
        
        self.subtitle_label = Label(
            self.root, 
            text="Thu Thập Dữ Liệu", 
            font=("Helvetica", 20, "bold"), 
            fg=self.TEXT_COLOR, 
            bg=self.BG_COLOR
        )
        self.subtitle_label.place(relx=0.5, rely=0.225, anchor=tk.CENTER)
    
    def _create_video_frame(self):
        """Tạo khung hiển thị video camera"""
        # Tính tỉ lệ 16:9 cho camera
        camera_width = int(self.screen_width * 0.55)
        camera_height = int(camera_width * 9 / 16)
        
        # Lưu kích thước cho sử dụng sau này
        self.camera_width = camera_width
        self.camera_height = camera_height
        
        # Phần chứa camera (bên trái, tỉ lệ 16:9)
        self.video_container = Frame(
            self.root, 
            bg=self.BORDER_COLOR, 
            bd=1, 
            relief="solid"
        )
        self.video_container.place(
            x=50, 
            y=int(self.screen_height * 0.25), 
            width=camera_width, 
            height=camera_height
        )
        
        self.video_frame = Label(self.video_container, bg="black")
        self.video_frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
    
    def _create_user_info_frame(self):
        """Tạo khung nhập thông tin người dùng"""
        # Vị trí và kích thước khung thông tin
        info_x = 50 + self.camera_width + 50
        info_width = self.screen_width - info_x - 50
        
        # Frame thông tin người dùng
        self.info_frame = Frame(
            self.root, 
            bg=self.VALUE_BG, 
            bd=1, 
            relief="solid"
        )
        self.info_frame.place(
            x=info_x, 
            y=int(self.screen_height * 0.25), 
            width=info_width, 
            height=int(self.camera_height * 0.8)
        )

        # Tiêu đề frame thông tin
        self.info_title = Label(
            self.info_frame, 
            text="THÔNG TIN NGƯỜI DÙNG", 
            font=("Helvetica", 18, "bold"), 
            fg=self.LABEL_FG, 
            bg=self.LABEL_BG,
            padx=10, 
            pady=10
        )
        self.info_title.pack(fill="x")

        # Container cho nhập liệu
        self.input_container = Frame(
            self.info_frame, 
            bg=self.VALUE_BG, 
            padx=30, 
            pady=30
        )
        self.input_container.pack(fill="both", expand=True)
        
        # Tạo các trường nhập liệu
        self._create_input_fields()
        
    def _create_input_fields(self):
        """Tạo các trường nhập liệu thông tin người dùng"""
        # Nhập tên
        self.name_label = Label(
            self.input_container, 
            text="Tên:", 
            font=("Helvetica", 16, "bold"), 
            bg=self.VALUE_BG, 
            fg=self.TEXT_COLOR
        )
        self.name_label.pack(anchor="w", pady=(0, 5))
        
        self.name_entry = Entry(
            self.input_container, 
            font=("Helvetica", 16), 
            relief="flat", 
            bg=self.INPUT_BG, 
            fg=self.TEXT_COLOR, 
            bd=0, 
            insertbackground=self.TEXT_COLOR
        )
        self.name_entry.pack(fill="x", pady=(0, 20), ipady=8)
        self.name_entry.config(highlightbackground=self.BORDER_COLOR, highlightthickness=1)

        # Nhập tuổi
        self.age_label = Label(
            self.input_container, 
            text="Tuổi:", 
            font=("Helvetica", 16, "bold"), 
            bg=self.VALUE_BG, 
            fg=self.TEXT_COLOR
        )
        self.age_label.pack(anchor="w", pady=(0, 5))
        
        self.age_entry = Entry(
            self.input_container, 
            font=("Helvetica", 16), 
            relief="flat", 
            bg=self.INPUT_BG, 
            fg=self.TEXT_COLOR, 
            bd=0, 
            insertbackground=self.TEXT_COLOR
        )
        self.age_entry.pack(fill="x", pady=(0, 30), ipady=8)
        self.age_entry.config(highlightbackground=self.BORDER_COLOR, highlightthickness=1)

        # Nút bắt đầu quay
        self.capture_button = Button(
            self.input_container, 
            text="Bắt Đầu Thu Thập", 
            font=("Helvetica", 16, "bold"), 
            bg=self.BUTTON_GREEN, 
            fg=self.LABEL_FG, 
            activebackground=self.BUTTON_GREEN_ACTIVE, 
            relief="flat", 
            command=self.start_capture, 
            bd=0,
            cursor="hand2", 
            padx=20, 
            pady=12
        )
        self.capture_button.pack(fill="x", pady=(0, 0))
        
    def _create_message_frame(self):
        """Tạo khung hiển thị thông báo"""
        self.message_frame = Frame(
            self.root, 
            bg=self.VALUE_BG, 
            bd=1, 
            relief="solid"
        )
        self.message_frame.place(
            x=50, 
            y=int(self.screen_height * 0.25) + self.camera_height + 20, 
            width=self.camera_width, 
            height=50
        )
        
        self.message_label = Label(
            self.message_frame, 
            text="Vui lòng nhập thông tin và nhấn 'Bắt Đầu Thu Thập'", 
            font=("Helvetica", 14), 
            fg=self.TEXT_COLOR, 
            bg=self.VALUE_BG, 
            anchor="center"
        )
        self.message_label.pack(fill=tk.BOTH, expand=True)
        
    def _create_control_buttons(self):
        """Tạo các nút điều khiển"""
        self.exit_button = Button(
            self.root, 
            text="Thoát", 
            font=("Helvetica", 14, "bold"), 
            bg=self.BUTTON_RED, 
            fg=self.LABEL_FG, 
            activebackground=self.BUTTON_RED_ACTIVE,
            relief="flat", 
            command=self.exit_full_screen, 
            bd=0,
            cursor="hand2"
        )
        self.exit_button.place(
            x=self.screen_width-120, 
            y=self.screen_height-70, 
            width=100, 
            height=50
        )
        
    def _initialize_camera_system(self):
        """Khởi tạo camera và bộ xử lý video"""
        try:
            self.camera = RealSenseCameraNew()
            self.processor = EmotionRecognitionProcessor()
        except Exception as e:
            print(f"Lỗi khởi tạo camera: {e}")
            self.show_message(f"Không thể khởi tạo camera: {str(e)}", self.ERROR_COLOR)
            self.camera = None
            self.processor = None

    def update_video(self):
        """Cập nhật hiển thị video từ camera"""
        if not self.capturing and self.camera and self.processor:
            try:
                ret, color_image, depth_image = self.camera.get_frames()
                if ret:
                    # Xử lý và hiển thị khung hình
                    self._process_and_display_frame(color_image)
            except Exception as e:
                print(f"Lỗi khi cập nhật video: {e}")
                
        # Lên lịch cập nhật tiếp theo
        self.root.after(50, self.update_video)
        
    def _process_and_display_frame(self, color_image):
        """Xử lý và hiển thị khung hình từ camera"""
        try:
            # Xử lý khung hình
            frame_with_landmarks, _, _ = self.processor.process_frame(color_image)
            cv2image = cv2.cvtColor(frame_with_landmarks, cv2.COLOR_BGR2RGBA)
            img = Image.fromarray(cv2image)
            
            # Lấy kích thước hiện tại của frame
            video_width = self.video_frame.winfo_width()
            video_height = self.video_frame.winfo_height()
            
            # Resize ảnh theo tỉ lệ 16:9
            if video_width > 10 and video_height > 10:
                img = img.resize((video_width, video_height), Image.LANCZOS)
            else:
                # Kích thước mặc định 16:9
                img = img.resize((800, 450), Image.LANCZOS)
                
            # Hiển thị ảnh
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_frame.imgtk = imgtk
            self.video_frame.configure(image=imgtk)
        except Exception as e:
            print(f"Lỗi khi xử lý khung hình: {e}")

    def start_capture(self):
        """Bắt đầu quá trình thu thập dữ liệu khuôn mặt"""
        # Kiểm tra thông tin đầu vào
        name = self.name_entry.get().strip()
        age = self.age_entry.get().strip()
        
        if not self._validate_user_input(name, age):
            return

        # Chuẩn bị thu thập dữ liệu
        self.capturing = True
        self.capture_button.config(state="disabled")
        
        # Tạo thư mục lưu dữ liệu
        user_folder = f'{name}_{age}'
        user_data_dir = os.path.join('data', 'users', user_folder)
        
        try:
            os.makedirs(user_data_dir, exist_ok=True)
            
            # Hiển thị thông báo và bắt đầu thu thập
            self.show_message("Đang thu thập dữ liệu khuôn mặt...", self.LABEL_BG)
            capture_thread = Thread(target=self._capture_video_thread, args=(user_data_dir,))
            capture_thread.daemon = True  # Đảm bảo thread kết thúc khi chương trình tắt
            capture_thread.start()
        except Exception as e:
            print(f"Lỗi khi tạo thư mục lưu dữ liệu: {e}")
            self.show_message(f"Không thể tạo thư mục lưu dữ liệu: {str(e)}", self.ERROR_COLOR)
            self.reset_capture()
            
    def _validate_user_input(self, name, age):
        """Kiểm tra hợp lệ của thông tin đầu vào"""
        if not name or not age:
            self.show_message("Tên và tuổi không được để trống!", self.ERROR_COLOR)
            return False
            
        # Kiểm tra tuổi có phải là số không
        try:
            int(age)
        except ValueError:
            self.show_message("Tuổi phải là số nguyên!", self.ERROR_COLOR)
            return False
            
        return True

    def _capture_video_thread(self, user_data_dir):
        """Thread xử lý việc thu thập khung hình từ camera"""
        try:
            start_time = time.time()
            frame_count = 0
            # Thu thập dữ liệu trong khoảng thời gian xác định
            while time.time() - start_time < self.CAPTURE_DURATION:
                ret, color_image, depth_image = self.camera.get_frames()
                if ret:
                    # Lưu khung hình xám để huấn luyện
                    gray_frame = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)
                    frame_path = os.path.join(user_data_dir, f'frame_{frame_count}.png')
                    cv2.imwrite(frame_path, gray_frame)
                    frame_count += 1
                    
                    # Cập nhật thông báo tiến trình
                    progress = int(((time.time() - start_time) / self.CAPTURE_DURATION) * 100)
                    self.root.after(0, lambda p=progress: self.show_message(
                        f"Đang thu thập dữ liệu: {p}%", self.LABEL_BG))
                    
                    # Ngừng chốc lát để tránh quá nhiều khung hình
                    time.sleep(0.1)
            
            # Hiển thị số lượng khung hình đã thu thập
            self.root.after(0, lambda c=frame_count: self.show_message(
                f"Đã thu thập {c} khung hình. Đang xử lý...", self.LABEL_BG))
                
            # Giải phóng camera sau khi thu thập xong
            if self.camera:
                self.camera.release()
                
            # Chuyển sang bước huấn luyện
            self.root.after(0, lambda: self._train_and_return())
        except Exception as e:
            print(f"Lỗi trong quá trình thu thập dữ liệu: {e}")
            self.root.after(0, lambda: self.show_message(
                f"Lỗi thu thập dữ liệu: {str(e)}", self.ERROR_COLOR))
            self.root.after(3000, self.reset_capture)

    def _train_and_return(self):
        """Huấn luyện mô hình và quay lại trang đăng nhập"""
        training_thread = Thread(target=self._train_model_thread)
        training_thread.daemon = True
        training_thread.start()

    def _train_model_thread(self):
        """Thread xử lý việc huấn luyện mô hình"""
        try:
            # Import trong hàm để tránh lỗi circular import
            from src.face_recognition import FaceRecognition
            
            # Hiển thị thông báo đang huấn luyện
            self.root.after(0, lambda: self.show_message(
                "Đang huấn luyện mô hình nhận diện khuôn mặt...", self.LABEL_BG))
                
            # Huấn luyện mô hình
            FaceRecognition.train_face_recognition_model('data/users', 'models')
            
            # Hiển thị thông báo thành công
            self.root.after(0, lambda: self.show_message(
                "Thu thập dữ liệu thành công!", self.SUCCESS_COLOR))
                
            # Chuyển về trang đăng nhập sau 3 giây
            self.root.after(3000, self._navigate_to_login)
        except Exception as e:
            print(f"Lỗi khi huấn luyện mô hình: {e}")
            self.root.after(0, lambda: self.show_message(
                f"Thu thập thất bại: {str(e)}", self.ERROR_COLOR))
            self.root.after(3000, self.reset_capture)

    def show_message(self, message, color):
        """Hiển thị thông báo với màu sắc"""
        self.message_label.config(text=message, fg=color)

    def reset_capture(self):
        """Reset lại giao diện để người dùng có thể thu thập lại dữ liệu"""
        self.capturing = False
        self.capture_button.config(state="normal")
        self.show_message("Vui lòng nhập thông tin và nhấn 'Bắt Đầu Thu Thập'", self.TEXT_COLOR)
        
        # Khởi tạo lại camera nếu cần
        if not self.camera:
            self._initialize_camera_system()

    def _navigate_to_login(self):
        """Chuyển về trang đăng nhập"""
        try:
            self.root.destroy()
            # Import trong hàm để tránh lỗi circular import
            from src.login import FaceRecognitionLoginApp
            login_app = tk.Tk()
            FaceRecognitionLoginApp(login_app)
            login_app.mainloop()
        except Exception as e:
            print(f"Lỗi khi chuyển về trang đăng nhập: {e}")

    def exit_full_screen(self, event=None):
        """Thoát khỏi ứng dụng"""
        # Giải phóng tài nguyên
        if hasattr(self, 'camera') and self.camera:
            try:
                self.camera.release()
            except Exception as e:
                print(f"Lỗi khi giải phóng camera: {e}")
                
        # Thoát ứng dụng
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = UserDataCollectionApp(root)
    root.mainloop()
