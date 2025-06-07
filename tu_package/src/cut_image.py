#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import rospy
from std_msgs.msg import Float64
from sensor_msgs.msg import Image
import numpy as np
import cv2
from cv_bridge import CvBridge, CvBridgeError
from ultralytics import YOLO
from happymimi_voice_msgs.srv import YesNo, YesNoResponse
import os

class CutService:
    def __init__(self):
        rospy.init_node('cut_image_node')
        try:
            self.model = YOLO("/home/mimi/main_ws/src/rcj25_master/rcj_super.pt")  # YOLOモデルロード
            self.bridge = CvBridge()
            self.current_image = None
            self.save_dir = '/home/mimi/main_ws/src/rcj25_master/tu_package/cut_images'  # 保存先フォルダ
            os.makedirs(self.save_dir, exist_ok=True)
        except Exception as e:
            rospy.logerr(f"Failed to load YOLO model: {e}")
            rospy.signal_shutdown("Failed to load YOLO model")
        
        rospy.Subscriber('/camera/color/image_raw', Image, self.img_listener)
        self.service = rospy.Service('cut_image', YesNo, self.cut_srv)
        
        rospy.loginfo("Cut image service is ready.")
    
    def img_listener(self, img_msg):
        try:
            self.current_image = self.bridge.imgmsg_to_cv2(img_msg, "bgr8")
        except CvBridgeError as e:
            rospy.logerr(f"Failed to convert image: {e}")

    def cut_srv(self, req):
        if self.current_image is None:
            rospy.logwarn("No image received yet.")
            return YesNoResponse(result=False)

        try:
            results = self.model(self.current_image)
            boxes = results[0].boxes.xyxy  # [N, 4] (x1, y1, x2, y2)

            if len(boxes) == 0:
                rospy.loginfo("No detections.")
                return YesNoResponse(result=False)

            img_center = np.array([self.current_image.shape[1] / 2, self.current_image.shape[0] / 2])  # (cx, cy)

            # 中心に一番近いbboxを探す
            min_dist = float('inf')
            best_box = None
            for box in boxes:
                x1, y1, x2, y2 = box.tolist()
                bbox_center = np.array([(x1 + x2) / 2, (y1 + y2) / 2])
                dist = np.linalg.norm(img_center - bbox_center)
                if dist < min_dist:
                    min_dist = dist
                    best_box = [int(x1), int(y1), int(x2), int(y2)]

            if best_box is None:
                rospy.logwarn("Failed to find best box.")
                return YesNoResponse(result=False)

            x1, y1, x2, y2 = best_box
            cropped_img = self.current_image[y1:y2, x1:x2]

            save_path = os.path.join(self.save_dir, f"cut_obj.jpg")
            cv2.imwrite(save_path, cropped_img)
            rospy.loginfo(f"Saved cropped image: {save_path}")

            return YesNoResponse(result=True)

        except Exception as e:
            rospy.logerr(f"Error during cut service: {e}")
            return YesNoResponse(result=False)

def main():
    try:
        node = CutService()
        rospy.spin()
    except rospy.ROSInitException:
        print('Shutting down')

if __name__ == '__main__':
    main()
