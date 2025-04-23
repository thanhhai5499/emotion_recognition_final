import os
import time
import tkinter as tk
from tkinter import Label, Button, Frame
from PIL import Image, ImageTk
import cv2
from src.camera import RealSenseCameraNew
from src.processor import EmotionRecognitionProcessor
from src.face_recognition import FaceRecognition

class FaceRecognitionLoginApp:
    # Các hằng số cho giao diện
    SCREEN_BG = "#f0f0f0"
    TITLE_COLOR = "#3366cc"
    COMPANY_COLOR = "#0066cc"
    TEXT_COLOR = "#333333"
    WARNING_COLOR = "red"
    SUCCESS_COLOR = "green"
    
    def __init__(self, root):
        self.root = root
        self.root.title("Đăng Nhập Hệ Thống")
        self.setup_window()
        self.load_and_setup_logos()
        self.create_labels()
        self.create_video_frame()
        self.create_message_frame()
        self.create_exit_button()
        self.initialize_camera_system()

    def setup_window(self):
        """Thiết lập cửa sổ chính"""
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg=self.SCREEN_BG)
        
    def load_and_setup_logos(self):
        """Tải và thiết lập logo"""
        try:
            # Logo trái
            self.icon_image = Image.open("assets/Logo.png")
            self.icon_image_resized = self.icon_image.resize((250, 250), Image.LANCZOS)
            self.icon_photo = ImageTk.PhotoImage(self.icon_image_resized)
            self.root.iconphoto(False, self.icon_photo)
            
            self.logo_label = Label(self.root, bg=self.SCREEN_BG)
            self.logo_label.pack(side="top", anchor="nw", padx=10, pady=10)
            self.display_large_logo()

            # Logo phải
            self.right_logo_image = Image.open("assets/logo2.png")
            self.right_logo_image_resized = self.right_logo_image.resize((380, 100), Image.LANCZOS)
            self.right_logo_photo = ImageTk.PhotoImage(self.right_logo_image_resized)
            self.right_logo_label = Label(self.root, image=self.right_logo_photo, bg=self.SCREEN_BG)
            self.right_logo_label.place(x=self.root.winfo_screenwidth()-400, y=10)
        except Exception as e:
            print(f"Lỗi khi tải logo: {e}")

    def create_labels(self):
        """Tạo các nhãn văn bản"""
        # Nhãn công ty quản lý
        self.management_company_label = Label(
            self.root,
            text="BAN QUẢN LÝ KHU CÔNG NGHỆ CAO THÀNH PHỐ HỒ CHÍ MINH",
            font=("Helvetica", 26, "bold"),
            fg="#FF0000",
            bg=self.SCREEN_BG
        )
        self.management_company_label.place(relx=0.5, rely=0.05, anchor=tk.CENTER)
        
        # Nhãn trung tâm
        self.company_label = Label(
            self.root,
            text="TRUNG TÂM NGHIÊN CỨU TRIỂN KHAI KHU CÔNG NGHỆ CAO",
            font=("Helvetica", 26, "bold"),
            fg="#FF0000",
            bg=self.SCREEN_BG
        )
        self.company_label.place(relx=0.5, rely=0.1, anchor=tk.CENTER)
        
        # Nhãn tiêu đề
        self.title_label = Label(
            self.root,
            text="HỆ THỐNG GIÁM SÁT QUÁ TRÌNH TẬP LUYỆN",
            font=("Helvetica", 24, "bold"),
            fg=self.TITLE_COLOR,
            bg=self.SCREEN_BG
        )
        self.title_label.place(relx=0.5, rely=0.18, anchor=tk.CENTER)
        
        # Nhãn thông báo
        self.message_label = Label(
            self.root,
            text="Nhận diện khuôn mặt để đăng nhập",
            font=("Helvetica", 20, "bold"),
            fg=self.TEXT_COLOR,
            bg=self.SCREEN_BG
        )
        self.message_label.place(relx=0.5, rely=0.225, anchor=tk.CENTER)

    def create_video_frame(self):
        """Tạo khung video"""
        self.video_container = Frame(self.root, bg="#cccccc", bd=2, relief="raised")
        self.video_container.place(relx=0.5, rely=0.55, anchor=tk.CENTER, relwidth=0.6, relheight=0.6)
        
        self.video_frame = Label(self.video_container, bg="black")
        self.video_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

    def create_message_frame(self):
        """Tạo khung thông báo"""
        self.message_frame = Frame(self.root, bg="#e0e0e0", bd=2, relief="sunken")
        self.message_frame.place(relx=0.5, rely=0.888, relwidth=0.5, relheight=0.06, anchor=tk.CENTER)
        
        self.success_message_label = Label(
            self.message_frame,
            text="",
            font=("Helvetica", 16),
            fg=self.TEXT_COLOR,
            bg="white",
            anchor="center"
        )
        self.success_message_label.pack(fill=tk.BOTH, expand=True)

    def create_exit_button(self):
        """Tạo nút thoát"""
        self.exit_button = Button(
            self.root,
            text="Thoát",
            font=("Helvetica", 14),
            bg="#e74c3c",
            fg="white",
            command=self.exit_full_screen
        )
        self.exit_button.place(relx=0.92, rely=0.92, relwidth=0.06, relheight=0.04)

    def initialize_camera_system(self):
        """Khởi tạo hệ thống camera và xử lý"""
        try:
            self.camera = RealSenseCameraNew()
            self.processor = EmotionRecognitionProcessor()
            self.face_recognition = FaceRecognition()
            self.start_time = time.time()
            self.recognized_user = None
            
            # Kiểm tra mô hình
            if not self.check_models_exist():
                self.show_warning_message("Không tìm thấy dữ liệu khuôn mặt. Cần thu thập dữ liệu.")
                self.root.after(3000, self.start_capture)
            else:
                self.start_camera_preview()
        except Exception as e:
            self.show_warning_message(f"Lỗi khởi tạo camera: {str(e)}")

    def check_models_exist(self):
        """Kiểm tra sự tồn tại của các mô hình"""
        return os.path.exists('models/knn_model.pkl') and os.path.exists('models/svm_model.pkl')

    def display_large_logo(self):
        """Hiển thị logo lớn"""
        try:
            large_logo_image = self.icon_image.resize((250, 250), Image.LANCZOS)
            large_logo_photo = ImageTk.PhotoImage(large_logo_image)
            self.logo_label.config(image=large_logo_photo)
            self.logo_label.image = large_logo_photo
        except Exception as e:
            print(f"Lỗi khi hiển thị logo lớn: {e}")

    def start_camera_preview(self):
        """Khởi động xem trước camera"""
        self.start_time = time.time()
        self.message_label.config(text="NHẬN DIỆN KHUÔN MẶT ĐỂ ĐĂNG NHẬP.")
        self.update_camera_preview()
        self.root.after(8000, self.update_video)

    def update_camera_preview(self):
        """Cập nhật khung hình camera"""
        try:
            ret, color_image, depth_image = self.camera.get_frames()
            if ret:
                self.process_and_display_frame(color_image)
            self.root.after(50, self.update_camera_preview)
        except Exception as e:
            self.show_warning_message(f"Lỗi camera: {str(e)}")

    def process_and_display_frame(self, frame):
        """Xử lý và hiển thị khung hình"""
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)
        
        video_width = self.video_frame.winfo_width()
        video_height = self.video_frame.winfo_height()
        
        if video_width > 10 and video_height > 10:
            img = img.resize((video_width, video_height))
        else:
            img = img.resize((800, 600))
            
        imgtk = ImageTk.PhotoImage(image=img)
        self.video_frame.imgtk = imgtk
        self.video_frame.configure(image=imgtk)

    def update_video(self):
        """Cập nhật video với nhận diện khuôn mặt"""
        if self.check_timeout():
            return
            
        try:
            ret, color_image, depth_image = self.camera.get_frames()
            if ret:
                self.process_face_recognition(color_image)
            self.root.after(50, self.update_video)
        except Exception as e:
            self.show_warning_message(f"Lỗi xử lý video: {str(e)}")

    def check_timeout(self):
        """Kiểm tra thời gian chờ"""
        if time.time() - self.start_time > 10 and self.recognized_user is None:
            self.show_warning_message("Không nhận diện được khuôn mặt. Cần thu thập dữ liệu.")
            self.root.after(1000, self.start_capture)
            return True
        return False

    def process_face_recognition(self, frame):
        """Xử lý nhận diện khuôn mặt"""
        frame_with_landmarks, faces, _ = self.processor.process_frame(frame)
        if faces:
            user = self.face_recognition.recognize_user(frame)
            if user:
                self.recognized_user = user
                self.show_success_message()
                return
        self.process_and_display_frame(frame_with_landmarks)

    def show_warning_message(self, message):
        """Hiển thị cảnh báo"""
        self.success_message_label.config(text=message, fg=self.WARNING_COLOR)

    def show_success_message(self):
        """Hiển thị thông báo thành công"""
        self.success_message_label.config(text="Đăng nhập thành công", fg=self.SUCCESS_COLOR)
        self.root.after(5000, self.navigate_to_emotion_recognition)

    def start_capture(self):
        """Chuyển đến trang thu thập dữ liệu"""
        self.root.destroy()
        from data_collection import UserDataCollectionApp
        data_collection_app = tk.Tk()
        UserDataCollectionApp(data_collection_app)
        data_collection_app.mainloop()

    def navigate_to_emotion_recognition(self):
        """Chuyển đến trang nhận diện cảm xúc"""
        self.root.destroy()
        from gui import EmotionRecognitionApp
        main_app = tk.Tk()
        EmotionRecognitionApp(main_app)
        main_app.mainloop()

    def destroy(self):
        """Giải phóng tài nguyên"""
        if hasattr(self, 'camera'):
            self.camera.release()

    def exit_full_screen(self, event=None):
        """Thoát chương trình"""
        self.destroy()
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = FaceRecognitionLoginApp(root)
    root.mainloop()
