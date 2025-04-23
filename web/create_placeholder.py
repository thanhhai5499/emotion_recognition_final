import os
import cv2
import numpy as np

def create_placeholder():
    """
    Tạo hình ảnh placeholder cho trường hợp không có camera
    """
    # Đường dẫn đến thư mục static
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    
    # Đảm bảo thư mục static tồn tại
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)
    
    # Tạo một hình ảnh đen với văn bản
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Thêm text
    font = cv2.FONT_HERSHEY_SIMPLEX
    text = "Camera không khả dụng"
    textsize = cv2.getTextSize(text, font, 1, 2)[0]
    
    # Đặt text vào giữa hình ảnh
    textX = (img.shape[1] - textsize[0]) // 2
    textY = (img.shape[0] + textsize[1]) // 2
    
    cv2.putText(img, text, (textX, textY), font, 1, (255, 255, 255), 2)
    
    # Lưu file
    img_path = os.path.join(static_dir, 'placeholder.jpg')
    cv2.imwrite(img_path, img)
    print(f"Đã tạo placeholder image tại: {img_path}")
    
    return img_path

if __name__ == "__main__":
    create_placeholder() 