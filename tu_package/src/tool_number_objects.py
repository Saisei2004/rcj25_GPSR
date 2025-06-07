#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import rospy
import json

from happymimi_recognition_msgs.srv import StrInt, StrIntResponse
from happymimi_msgs.srv import SetStr


class RecognitionService:
    def __init__(self):
        rospy.init_node('recognition_service_node')    
        self.yolo_info = rospy.ServiceProxy('/recognition/yolo_info', SetStr)
        
        # サービスサーバーの作成
        self.service = rospy.Service('target_check', StrInt, self.handle_service)
        rospy.loginfo("サーバーを起動しました")
    
    def handle_service(self, req):
        target = req.request
        rospy.loginfo(f"リクエストを受け付けました: {target}")
        result = json.loads(self.yolo_info().result)
        print(result)
        number = 0
        
        for item in result:
            for key, value in item.items():
                if key == target:
                    number += 1
        if number == 0:
            rospy.loginfo(f"対象物 {target} は見つかりませんでした")
            return StrIntResponse(result=0)
        
        return StrIntResponse(result=number)
        
def main():
    try:
        #変数に入れなくても良かったかも
        recognition_service = RecognitionService()
        rospy.spin()
    except rospy.ROSInitException:
        print('Shutting down')  # 初期化エラーが発生した場合、メッセージを出力

if __name__ == '__main__':
    main()

