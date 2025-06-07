#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import rospy
from std_msgs.msg import Float64
from sensor_msgs.msg import Image
import numpy as np
import cv2
from cv_bridge import CvBridge

class DepthSubscriber:
    def __init__(self):
        rospy.init_node('depth_subscriber', anonymous=True)
        self.bridge = CvBridge()
        self.sub = rospy.Subscriber('/camera/depth/image_rect_raw', Image, self.depth_callback)
        self.pub = rospy.Publisher('center_depth', Float64, queue_size=10) 
        rospy.spin()

    def depth_callback(self, msg):
        # 深度画像を取得
        depth_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding="passthrough")

        # 画像のサイズ
        height, width = depth_image.shape

        # 画像の中心座標
        center_x, center_y = width // 2, height // 2

        # 画像の中心ピクセルの深度値を取得（単位はmmまたはm）
        depth_value = depth_image[center_y, center_x]

        # 深度値が無効な場合（0のとき）、周囲の平均を使用
        if depth_value == 0:
            depth_value = np.mean(depth_image[center_y-2:center_y+3, center_x-2:center_x+3])

        # mm単位からm単位に変換
        depth_value_m = depth_value / 1000.0

        rospy.loginfo(f"Center Depth: {depth_value_m:.2f} meters")
        self.pub.publish(depth_value_m)

if __name__ == '__main__':
    DepthSubscriber()
