#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ultralytics import YOLOWorld
import cv2
import rclpy
import rospy
from cv_bridge import CvBridge, CvBridgeError
#対応するサービス型を..
from happymimi_msgs.srv import SetFloat, SetFloatResponse
from sensor_msgs.msg import Image
import numpy


    
class Center():
    def __init__(self):
        rospy.init_node('obj_node', anonymous=True)  # ノードの初期化
        self.model = YOLOWorld("yolov8l-world.pt")
        rospy.Subscriber('/camera/color/image_raw', Image, self.img_listener)
        rospy.Subscriber('/camera/depth/image_rect_raw', Image, self.depth_img)
        self.bridge = CvBridge()
        self.current_frame = None
        rospy.Service("obj_center", SetFloat, self.obj_srv)  # サービスを設定
        rospy.loginfo("Seevice ready!!")

        # クラス名のリストを読み込む
        # self.classes = {}
        # with open(class_file_path, 'r') as f:
        #     for line in f.readlines():
        #         mods = line.strip().split(":")
        #         self.classes[int(mods[0])] = mods[1]

    def img_listener(self, img):
        try:
            # 画像データを受け取り、OpenCV形式に変換
            self.current_frame = self.bridge.imgmsg_to_cv2(img, "bgr8")  # ROSイメージメッセージをOpenCV画像に変換
        except CvBridgeError as e:
            rospy.logerr(f"Failed to convert image: {e}")
    
    def depth_img(self, img):
        try:
            # 画像データを受け取り、OpenCV形式に変換
            self.depth_info = self.bridge.imgmsg_to_cv2(img, "bgr8")  # ROSイメージメッセージをOpenCV画像に変換
        except CvBridgeError as e:
            rospy.logerr(f"Failed to convert image: {e}")
    
    def all_finisher(self, x, y):
        depth_value = self.depth_info[y, x]
        if depth_value == 0:
            depth_value = numpy.mean(self.depth_info[y-2:y+3, x-2:x+3])
        depth_value_m = depth_value / 1000.0
        rospy.loginfo(f"Center Depth: {depth_value_m:.2f} meters")
        return depth_value_m


    def get_dist(self):
        if self.current_frame is None:
            rospy.logerr("No image.")
            return 0, 0
        
        try:
            results = self.model.predict(self.current_frame, conf=0.4)
        except Exception as e:
            rospy.logerr(f"Model prediction failed: {e}")
            return 0, 0

        for box in results[0].boxes:
            x1, y1, x2, y2 = [int(i) for i in box.xyxy[0]]
            cls = int(box.cls[0])
            
            if cls: 
                cv2.rectangle(self.current_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                x = (x1 + x2) // 2
                y = (y1 + y2) // 2
                break
        return x, y


    
    def obj_srv(self, req):
            # サービスリクエストを処理
            x, y = self.get_dist()
            result = self.all_finisher(x, y)
            return SetFloatResponse(data=result)  # サービス応答として座標を返す
    
        

if __name__ == '__main__':
    try:
        Center()  # SeatFinderクラスのインスタンスを作成
        rospy.spin()  # ノードが終了するまで待機
    except rospy.ROSInitException:
        print('Shutting down')  # 初期化エラーが発生した場合、メッセージを出力
        cv2.destroyAllWindows()  # OpenCVのウィンドウをすべて閉じる