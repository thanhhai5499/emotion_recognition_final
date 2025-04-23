#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tập tin chạy chính cho ứng dụng nhận diện cảm xúc web.
Cung cấp giao diện dòng lệnh để khởi chạy ứng dụng với các tùy chọn
và cấu hình khác nhau.
"""

import os
import sys
import argparse
import webbrowser
import threading
import time
from pathlib import Path

# Thêm đường dẫn gốc của dự án vào sys.path
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
sys.path.append(str(PROJECT_ROOT))

def parse_arguments():
    """Phân tích các đối số dòng lệnh."""
    parser = argparse.ArgumentParser(
        description="Ứng dụng nhận diện cảm xúc web"
    )
    
    parser.add_argument(
        "-p", "--port", 
        type=int, 
        default=5000, 
        help="Cổng để chạy máy chủ web (mặc định: 5000)"
    )
    
    parser.add_argument(
        "-H", "--host", 
        type=str, 
        default="127.0.0.1", 
        help="Địa chỉ máy chủ (mặc định: 127.0.0.1, sử dụng 0.0.0.0 để truy cập từ xa)"
    )
    
    parser.add_argument(
        "--debug", 
        action="store_true", 
        help="Chạy ứng dụng trong chế độ gỡ lỗi"
    )
    
    parser.add_argument(
        "--no-browser", 
        action="store_true", 
        help="Không tự động mở trình duyệt khi khởi động"
    )
    
    return parser.parse_args()

def open_browser(host, port):
    """Mở trình duyệt sau khi máy chủ đã khởi động."""
    # Chờ một chút cho máy chủ khởi động
    time.sleep(1.5)
    
    # Xác định URL để mở
    if host == "0.0.0.0":
        url = f"http://localhost:{port}"
    else:
        url = f"http://{host}:{port}"
    
    print(f"Mở trình duyệt tại: {url}")
    webbrowser.open(url)

def run_app():
    """Khởi chạy ứng dụng Flask."""
    args = parse_arguments()
    
    try:
        from web.app import app
        
        # Hiển thị thông tin khởi động
        print("=" * 60)
        print("Ứng dụng Nhận Diện Cảm Xúc Web")
        print("=" * 60)
        print(f"* Máy chủ đang chạy tại http://{args.host}:{args.port}")
        
        if args.host == "0.0.0.0":
            print("* Ứng dụng có thể truy cập từ các thiết bị khác trong mạng LAN")
        
        print(f"* Chế độ gỡ lỗi: {'Bật' if args.debug else 'Tắt'}")
        print("* Nhấn CTRL+C để thoát")
        print("=" * 60)
        
        # Mở trình duyệt nếu không có tùy chọn --no-browser
        if not args.no_browser:
            # Chạy trong một luồng mới để không chặn máy chủ
            browser_thread = threading.Thread(
                target=open_browser, 
                args=(args.host, args.port)
            )
            browser_thread.daemon = True
            browser_thread.start()
        
        # Khởi chạy ứng dụng Flask
        app.run(
            host=args.host, 
            port=args.port, 
            debug=args.debug,
            use_reloader=args.debug
        )
        
    except ImportError as e:
        print(f"Lỗi: Không thể nhập mô-đun. Chi tiết: {e}")
        print("Vui lòng đảm bảo rằng bạn đang chạy lệnh từ thư mục gốc của dự án.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nMáy chủ đã bị dừng bởi người dùng.")
    except Exception as e:
        print(f"Lỗi không mong muốn: {e}")
        if args.debug:
            # Hiển thị đầy đủ lỗi trong chế độ gỡ lỗi
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    run_app() 