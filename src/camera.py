import pyrealsense2 as rs
import numpy as np
import cv2

# camera.py
import pyrealsense2 as rs

class RealSenseCamera:
    def __init__(self):
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self.config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        self.config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        self.pipeline.start(self.config)

    def get_frames(self):
        frames = self.pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        depth_frame = frames.get_depth_frame()
        if not color_frame or not depth_frame:
            return False, None, None
        color_image = np.asanyarray(color_frame.get_data())
        depth_image = np.asanyarray(depth_frame.get_data())

        # Tăng độ sáng và độ tương phản cho color_image (nếu cần)
        color_image = cv2.convertScaleAbs(color_image, alpha=1.2, beta=30)  # Điều chỉnh độ tương phản và sáng

        return True, color_image, depth_image
    

    def release(self):
        self.pipeline.stop()

class RealSenseCameraNew:
    def __init__(self):
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self.config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)
        self.config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
        self.pipeline.start(self.config)

    def get_frames(self):
        frames = self.pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        depth_frame = frames.get_depth_frame()
        if not color_frame or not depth_frame:
            return False, None, None
        color_image = np.asanyarray(color_frame.get_data())
        depth_image = np.asanyarray(depth_frame.get_data())

        # Tăng độ sáng và độ tương phản cho color_image (nếu cần)
        color_image = cv2.convertScaleAbs(color_image, alpha=1.2, beta=30)  # Điều chỉnh độ tương phản và sáng

        return True, color_image, depth_image

    def release(self):
        self.pipeline.stop()
