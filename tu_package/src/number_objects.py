#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import rospy
from sensor_msgs.msg import Image
from ultralytics import YOLOWorld
import sys
import roslib
from cv_bridge import CvBridge, CvBridgeError

from happymimi_recognition_msgs.srv import StrInt, StrIntResponse
#NONONONONONONNONONONOONONOONONONONOONONONONONONONONONONONONONONONONONONONONONONONONONONONONONONONONONONONONONONONONONO
#warning warning warning warning warning warning warning warning warning warning warning warning warning warning warning!!!!!!!!!!!!
class RecognitionService:
    def __init__(self):
        rospy.init_node('recognition_service_node')
        try:
            # YOLOモデルのロード
            self.model = YOLOWorld("yolov8l-world.pt")  # YOLOモデルをロード
            # 初期クラスは空に設定　未検証
            self.model.set_classes([])
            # CvBridgeの初期化
            self.bridge = CvBridge()
        except Exception as e:
            rospy.logerr(f"Failed to load YOLO model: {e}")
            rospy.signal_shutdown("Failed to load YOLO model")
            
        
        rospy.Subscriber('/camera/color/image_raw', Image, self.img_listener)
        
        # サービスサーバーの作成
        self.service = rospy.Service('target_check', StrInt, self.handle_service)
        rospy.loginfo("これは使わないでください")
        rospy.loginfo("tool_number_objects.pyを使ってください")
        
        # 現在の画像を保持する変数
        self.current_image = None
        
    def img_listener(self, img):
        try:
            # 画像データを受け取り、OpenCV形式に変換
            self.current_image = self.bridge.imgmsg_to_cv2(img, "bgr8")  # ROSイメージメッセージをOpenCV画像に変換
        except CvBridgeError as e:
            rospy.logerr(f"Failed to convert image: {e}")
        
    def check_target(self, target):
        try:
            # リクエストから受け取ったターゲットを検出クラスとして設定
            self.model.set_classes([target])
            
            if self.current_image is None:
                rospy.logwarn("画像が受信されていません")
                return 0
            
            # YOLOで物体検出を実行
            results = self.model(self.current_image)
            
            # 検出された物体の数をカウント
            detection_count = 0
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    # 信頼度が0.5以上の検出結果のみをカウント　しきい値
                    if box.conf.item() > 0.5:
                        detection_count += 1
            
            rospy.loginfo(f"検出された{target}の数: {detection_count}")
            return detection_count
            
        except Exception as e:
            rospy.logerr(f"物体検出中にエラーが発生しました: {e}")
            return 0
    
    def handle_service(self, req):
        try:
            # リクエストの処理
            rospy.loginfo(f"リクエストを受け付けました: {req.request}")
            target = req.request
            result = self.check_target(target)   
            
            return StrIntResponse(result=result)
        except Exception as e:
            rospy.logerr(f"エラーが発生しました: {e}")
            return StrIntResponse(result=0)

def main():
    try:
        #変数に入れなくても良かったかも
        recognition_service = RecognitionService()
        rospy.spin()
    except rospy.ROSInitException:
        print('Shutting down')  # 初期化エラーが発生した場合、メッセージを出力

if __name__ == '__main__':
    main()

