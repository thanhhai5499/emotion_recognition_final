from flask import Flask, render_template, Response, jsonify, request, redirect, url_for, session
import cv2
import numpy as np
import threading
import time
import sys
import os
import json
import base64
from datetime import datetime
from src.camera import RealSenseCamera
from src.processor import EmotionRecognitionProcessor
import serial.tools.list_ports
import random

# Thêm đường dẫn gốc vào sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'emotion_recognition_secret_key'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False

# Đảm bảo thư mục static tồn tại
static_dir = os.path.join(os.path.dirname(__file__), 'static')
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

# Đảm bảo các thư mục css và js tồn tại
css_dir = os.path.join(static_dir, 'css')
if not os.path.exists(css_dir):
    os.makedirs(css_dir)

js_dir = os.path.join(static_dir, 'js')
if not os.path.exists(js_dir):
    os.makedirs(js_dir)

# Tạo placeholder image nếu chưa có
placeholder_path = os.path.join(static_dir, 'placeholder.jpg')
if not os.path.exists(placeholder_path):
    try:
        from web.create_placeholder import create_placeholder
        create_placeholder()
    except Exception as e:
        print(f"Lỗi khi tạo placeholder image: {e}")

# Biến toàn cục cho camera và processor
camera = None
processor = None
emotion_data = {
    'emotion': 'Bình thường',
    'emotion_color': '#4CAF50',
    'rest_message': '',
    'rest_color': '#333333'
}
heartrate_data = {
    'value': '80',
    'color': '#4CAF50'
}
arduino_status = {
    'connected': False,
    'message': 'Chưa kết nối',
    'color': '#FF9800'
}
arduino_reader = None
serial_lock = threading.Lock()

# Các hằng số màu
COLORS = {
    'success': '#4CAF50',
    'error': '#FF0000',
    'warning': '#FF9800',
    'normal': '#333333',
    'abnormal': '#FF5722'
}

# Login status
login_status = {
    'is_authenticated': False,
    'user_name': None,
    'needs_data_collection': False,
    'face_detected': False,
    'recognition_message': 'Nhận diện khuôn mặt để đăng nhập'
}

def initialize_camera():
    """Khởi tạo camera và processor"""
    global camera, processor
    try:
        camera = RealSenseCamera()
        processor = EmotionRecognitionProcessor()
        return True
    except Exception as e:
        print(f"Lỗi khi khởi tạo camera: {e}")
        return False

def get_com_ports():
    """Lấy danh sách các cổng COM"""
    try:
        ports = serial.tools.list_ports.comports()
        return [{'device': port.device, 'description': port.description} for port in ports]
    except Exception as e:
        print(f"Lỗi khi lấy danh sách cổng COM: {e}")
        return []

def close_arduino_connection():
    """Đóng kết nối Arduino hiện tại"""
    global arduino_reader, arduino_status
    with serial_lock:
        try:
            if arduino_reader and hasattr(arduino_reader, 'serial_connection'):
                arduino_reader.serial_connection.close()
        except Exception as e:
            print(f"Lỗi khi đóng kết nối Arduino: {e}")
        finally:
            arduino_reader = None
            arduino_status = {
                'connected': False,
                'message': 'Đã ngắt kết nối',
                'color': '#FF9800'
            }

def connect_arduino(port):
    """Kết nối Arduino với cổng COM được chọn"""
    global arduino_reader, arduino_status
    
    # Đóng kết nối hiện tại nếu có
    close_arduino_connection()
    
    if not port:
        arduino_status = {
            'connected': False,
            'message': 'Không có cổng COM nào được chọn!',
            'color': COLORS['error']
        }
        return False
    
    try:
        from src.arduino_reader import ArduinoReader
        with serial_lock:
            arduino_reader = ArduinoReader(port=port)
            arduino_status = {
                'connected': True,
                'message': 'Arduino đã được kết nối',
                'color': COLORS['success']
            }
        return True
    except Exception as e:
        arduino_status = {
            'connected': False,
            'message': f'Không thể kết nối Arduino! {str(e)}',
            'color': COLORS['error']
        }
        return False

def read_heart_rate():
    """Đọc dữ liệu nhịp tim từ Arduino"""
    global arduino_reader, heartrate_data, arduino_status
    
    while arduino_status.get('connected', False):
        try:
            with serial_lock:
                if not arduino_reader:
                    time.sleep(1)
                    continue
                    
                heart_rate = arduino_reader.read_data()
                
                if heart_rate is not None:
                    # Xác định màu dựa trên nhịp tim
                    if heart_rate > 100:
                        color = COLORS['error']  # Màu đỏ cho nhịp tim cao
                    elif heart_rate < 60:
                        color = COLORS['warning']  # Màu cam cho nhịp tim thấp
                    else:
                        color = COLORS['success']  # Màu xanh lá cho nhịp tim bình thường
                    
                    heartrate_data = {
                        'value': str(heart_rate),
                        'color': color
                    }
                
            time.sleep(1)  # Đọc dữ liệu mỗi giây
        except Exception as e:
            print(f"Lỗi khi đọc nhịp tim: {e}")
            heartrate_data = {
                'value': 'Lỗi kết nối',
                'color': COLORS['error']
            }
            with serial_lock:
                arduino_status['connected'] = False
            time.sleep(2)

def generate_frames():
    """Tạo luồng khung hình từ camera"""
    # Đường dẫn đến placeholder image
    placeholder_path = os.path.join(static_dir, 'placeholder.jpg')
    if not os.path.exists(placeholder_path):
        try:
            from web.create_placeholder import create_placeholder
            placeholder_path = create_placeholder()
        except Exception as e:
            print(f"Lỗi khi tạo placeholder image: {e}")
            # Tạo một khung hình đen đơn giản
            error_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(error_frame, "Camera not available", (50, 240), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            while True:
                ret, buffer = cv2.imencode('.jpg', error_frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                time.sleep(1)
    
    while True:
        try:
            # Đọc placeholder image thay vì sử dụng camera thật
            if os.path.exists(placeholder_path):
                frame = cv2.imread(placeholder_path)
                
                # Thêm timestamp và một số hiệu ứng giả lập
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                cv2.putText(frame, timestamp, (10, 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # Thêm một chữ "DEMO" vào góc
                cv2.putText(frame, "DEMO", (frame.shape[1] - 120, 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                
                # Vẽ một vài đường viền giả lập khuôn mặt
                center_x, center_y = frame.shape[1] // 2, frame.shape[0] // 2
                cv2.rectangle(frame, (center_x - 100, center_y - 100), 
                              (center_x + 100, center_y + 100), (0, 255, 0), 2)
                
                # Chuyển đổi sang JPEG
                ret, buffer = cv2.imencode('.jpg', frame)
                frame_bytes = buffer.tobytes()
                
                # Trả về khung hình
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            else:
                # Tạo một khung hình đen nếu không tìm thấy placeholder
                error_frame = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(error_frame, "Camera not available", (50, 240), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                ret, buffer = cv2.imencode('.jpg', error_frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            
            # Tạm dừng để giả lập tốc độ khung hình
            time.sleep(0.1)
                       
        except Exception as e:
            print(f"Lỗi khi tạo khung hình: {e}")
            # Tạo khung hình lỗi
            error_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(error_frame, f"Error: {str(e)}", (50, 240), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            ret, buffer = cv2.imencode('.jpg', error_frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(1)

def generate_depth_frames():
    """Tạo luồng khung hình độ sâu từ camera"""
    # Đường dẫn đến placeholder image
    placeholder_path = os.path.join(static_dir, 'placeholder.jpg')
    if not os.path.exists(placeholder_path):
        try:
            from web.create_placeholder import create_placeholder
            placeholder_path = create_placeholder()
        except Exception as e:
            print(f"Lỗi khi tạo placeholder image: {e}")
            # Tạo một khung hình đen đơn giản
            error_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(error_frame, "Depth camera not available", (50, 240), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            while True:
                ret, buffer = cv2.imencode('.jpg', error_frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                time.sleep(1)
    
    while True:
        try:
            # Đọc placeholder image thay vì sử dụng camera thật
            if os.path.exists(placeholder_path):
                frame = cv2.imread(placeholder_path)
                
                # Tạo hiệu ứng giả lập bản đồ độ sâu
                # Chuyển thành ảnh xám
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Áp dụng bản đồ màu để tạo hiệu ứng bản đồ độ sâu
                depth_colormap = cv2.applyColorMap(gray, cv2.COLORMAP_JET)
                
                # Thêm timestamp
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                cv2.putText(depth_colormap, timestamp, (10, 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # Thêm chữ "DEPTH DEMO"
                cv2.putText(depth_colormap, "DEPTH DEMO", (depth_colormap.shape[1] - 200, 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                
                # Chuyển đổi sang JPEG
                ret, buffer = cv2.imencode('.jpg', depth_colormap)
                frame_bytes = buffer.tobytes()
                
                # Trả về khung hình
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            else:
                # Tạo một khung hình đen nếu không tìm thấy placeholder
                error_frame = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(error_frame, "Depth camera not available", (50, 240), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                ret, buffer = cv2.imencode('.jpg', error_frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            
            # Tạm dừng để giả lập tốc độ khung hình
            time.sleep(0.1)
                   
        except Exception as e:
            print(f"Lỗi khi tạo khung hình độ sâu: {e}")
            # Tạo khung hình lỗi
            error_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(error_frame, f"Error: {str(e)}", (50, 240), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            ret, buffer = cv2.imencode('.jpg', error_frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(1)

@app.route('/')
def index():
    """Trang chủ - Kiểm tra trạng thái đăng nhập và chuyển hướng"""
    if session.get('is_authenticated', False):
        return redirect(url_for('main_app'))
    else:
        return redirect(url_for('login'))

@app.route('/login')
def login():
    """Trang đăng nhập - Tương tự FaceRecognitionLoginApp"""
    return render_template('login.html', 
                          title="Đăng Nhập - Hệ Thống Giám Sát Quá Trình Tập Luyện",
                          message=login_status['recognition_message'])

@app.route('/login_feed')
def login_feed():
    """Luồng video cho trang đăng nhập"""
    return Response(generate_login_frames(), 
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/data_collection')
def data_collection():
    """Trang thu thập dữ liệu - Tương tự UserDataCollectionApp"""
    return render_template('data_collection.html',
                          title="Thu Thập Dữ Liệu - Hệ Thống Giám Sát Quá Trình Tập Luyện")

@app.route('/data_collection_feed')
def data_collection_feed():
    """Luồng video cho trang thu thập dữ liệu"""
    return Response(generate_data_collection_frames(), 
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/main_app')
def main_app():
    """Trang ứng dụng chính - Giám sát quá trình tập luyện"""
    if not session.get('is_authenticated', False):
        return redirect(url_for('login'))
    return render_template('main.html', 
                           title="Hệ Thống Giám Sát Quá Trình Tập Luyện")

@app.route('/video_feed')
def video_feed():
    """Luồng video chính"""
    return Response(generate_frames(), 
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/depth_feed')
def depth_feed():
    """Luồng video độ sâu"""
    return Response(generate_depth_frames(), 
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/com_ports')
def api_com_ports():
    """API trả về danh sách cổng COM"""
    return jsonify(get_com_ports())

@app.route('/api/connect_arduino', methods=['POST'])
def api_connect_arduino():
    """API kết nối Arduino với cổng COM được chọn"""
    data = request.get_json()
    port = data.get('port')
    
    if connect_arduino(port):
        # Bắt đầu thread đọc nhịp tim
        heart_rate_thread = threading.Thread(target=read_heart_rate, daemon=True)
        heart_rate_thread.start()
        
        return jsonify({
            'success': True,
            'message': arduino_status['message']
        })
    else:
        return jsonify({
            'success': False,
            'message': arduino_status['message']
        })

@app.route('/api/disconnect_arduino', methods=['POST'])
def api_disconnect_arduino():
    """API ngắt kết nối Arduino"""
    close_arduino_connection()
    return jsonify({
        'success': True,
        'message': 'Đã ngắt kết nối Arduino'
    })

@app.route('/api/status')
def api_status():
    """API trả về trạng thái của hệ thống"""
    # Giả lập thay đổi cảm xúc
    if random.random() < 0.1:  # 10% cơ hội thay đổi cảm xúc
        if emotion_data["emotion"] == "Bình thường":
            emotion_data["emotion"] = "Bất thường"
            emotion_data["emotion_color"] = "#FF5722"
            emotion_data["rest_message"] = "Cần nghỉ ngơi"
            emotion_data["rest_color"] = "#FF0000"
        else:
            emotion_data["emotion"] = "Bình thường"
            emotion_data["emotion_color"] = "#4CAF50"
            emotion_data["rest_message"] = ""
            emotion_data["rest_color"] = "#333333"
    
    # Giả lập thay đổi nhịp tim
    value = random.randint(60, 100)
    heartrate_data["value"] = str(value)
    if value > 90:
        heartrate_data["color"] = "#FF0000"
    elif value < 70:
        heartrate_data["color"] = "#FF9800"
    else:
        heartrate_data["color"] = "#4CAF50"
    
    return jsonify({
        'emotion': emotion_data,
        'heartrate': heartrate_data,
        'arduino': arduino_status,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

@app.route('/api/shutdown', methods=['POST'])
def shutdown():
    """Tắt ứng dụng và giải phóng tài nguyên"""
    # Giải phóng tài nguyên camera
    global camera
    if camera:
        try:
            camera.release()
        except Exception as e:
            print(f"Lỗi khi giải phóng camera: {e}")
    
    # Đóng kết nối Arduino
    close_arduino_connection()
    
    return jsonify({'success': True, 'message': 'Ứng dụng đã tắt'})

@app.route('/api/check_login_status')
def api_check_login_status():
    """API kiểm tra trạng thái đăng nhập"""
    # Giả lập logic xác thực 
    if login_status['face_detected'] and random.random() < 0.2:
        # 20% cơ hội xác thực thành công khi phát hiện khuôn mặt
        login_status['is_authenticated'] = True
        login_status['user_name'] = 'Người dùng'
        session['is_authenticated'] = True
        session['user_name'] = 'Người dùng'
        return jsonify({
            'authenticated': True,
            'redirect': url_for('main_app'),
            'message': 'Đăng nhập thành công'
        })
    elif login_status['face_detected'] and random.random() < 0.3:
        # 30% cơ hội cần thu thập dữ liệu khi phát hiện khuôn mặt
        login_status['needs_data_collection'] = True
        login_status['recognition_message'] = 'Không nhận diện được khuôn mặt. Cần thu thập dữ liệu.'
        return jsonify({
            'authenticated': False,
            'redirect': url_for('data_collection'),
            'message': 'Không nhận diện được khuôn mặt. Chuyển hướng đến thu thập dữ liệu.'
        })
    else:
        # Chưa xác thực
        return jsonify({
            'authenticated': False,
            'message': 'Đang nhận diện khuôn mặt...'
        })

@app.route('/api/logout', methods=['POST'])
def api_logout():
    """API đăng xuất"""
    session.pop('is_authenticated', None)
    session.pop('user_name', None)
    login_status['is_authenticated'] = False
    login_status['user_name'] = None
    return jsonify({
        'success': True,
        'message': 'Đã đăng xuất',
        'redirect': url_for('login')
    })

@app.route('/api/save_user_data', methods=['POST'])
def api_save_user_data():
    """API lưu dữ liệu người dùng từ trang thu thập dữ liệu"""
    data = request.get_json()
    user_name = data.get('user_name', '')
    
    # Giả lập lưu dữ liệu
    if user_name:
        session['is_authenticated'] = True
        session['user_name'] = user_name
        return jsonify({
            'success': True,
            'message': f'Đã lưu dữ liệu cho người dùng {user_name}',
            'redirect': url_for('main_app')
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Tên người dùng không hợp lệ'
        })

def generate_login_frames():
    """Tạo luồng khung hình cho trang đăng nhập với nhận diện khuôn mặt"""
    while True:
        try:
            # Placeholder for real face recognition
            frame = cv2.imread(os.path.join(static_dir, 'placeholder.jpg'))
            if frame is None:
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(frame, "Camera not available", (50, 240), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            # Simulate face recognition
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cv2.putText(frame, timestamp, (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Draw face detection rectangle occasionally
            if random.random() < 0.3:
                login_status['face_detected'] = True
                center_x, center_y = frame.shape[1] // 2, frame.shape[0] // 2
                cv2.rectangle(frame, (center_x - 100, center_y - 100), 
                              (center_x + 100, center_y + 100), (0, 255, 0), 2)
            else:
                login_status['face_detected'] = False
            
            # Chuyển đổi sang JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            
            # Trả về khung hình
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
            time.sleep(0.1)
        except Exception as e:
            print(f"Lỗi khi tạo khung hình đăng nhập: {e}")
            time.sleep(1)

def generate_data_collection_frames():
    """Tạo luồng khung hình cho trang thu thập dữ liệu"""
    while True:
        try:
            # Placeholder for data collection frames
            frame = cv2.imread(os.path.join(static_dir, 'placeholder.jpg'))
            if frame is None:
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(frame, "Camera not available", (50, 240), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            # Add data collection overlay
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cv2.putText(frame, "Thu thập dữ liệu khuôn mặt", (50, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, timestamp, (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Draw face detection guidance
            center_x, center_y = frame.shape[1] // 2, frame.shape[0] // 2
            cv2.rectangle(frame, (center_x - 150, center_y - 150), 
                          (center_x + 150, center_y + 150), (0, 255, 0), 2)
            cv2.putText(frame, "Đặt khuôn mặt vào khung", (center_x - 140, center_y - 170), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Chuyển đổi sang JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            
            # Trả về khung hình
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
            time.sleep(0.1)
        except Exception as e:
            print(f"Lỗi khi tạo khung hình thu thập dữ liệu: {e}")
            time.sleep(1)

@app.route('/api/check_authentication')
def api_check_authentication():
    """API kiểm tra trạng thái xác thực của người dùng"""
    authenticated = session.get('is_authenticated', False)
    return jsonify({
        'authenticated': authenticated,
        'user_name': session.get('user_name', None)
    })

if __name__ == '__main__':
    # Khởi tạo camera và processor
    initialize_camera()
    app.run(debug=True, host='0.0.0.0', port=5000) 