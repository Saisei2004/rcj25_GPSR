#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rospy
import roslib
import sys
import math

from sensor_msgs.msg import LaserScan
from fmm24.srv import Distance, DistanceResponse

file_path = roslib.packages.get_pkg_dir('happymimi_teleop') + '/src/'
sys.path.insert(0, file_path)
from base_control import BaseControl
from simple_base_control import SimpleBaseControl

dis = 0

class person_distance:
    def __init__(self):
        # rospy.init_node("distance_node")
        rospy.loginfo("Start")
        self.distance = 0

        if hasattr(self, 'has_scanned') and self.has_scanned:
            return 

        rospy.Subscriber('/scan', LaserScan, self.scan_callback) #ここで2D-LiDARで取ったデータをすべて入手する


        # self.distance_service = rospy.Service('/get_distance_info', Distance, self.get_distance_info) #ここでこのモジュールのアドレス名などを決めている
        #distance_service = rospy.Service('/get_distance_info', Distance, self.get_distance_info)

        self.bc = BaseControl()
        self.bc = SimpleBaseControl()
        
        self.count = 0

        # self.distance = float("inf")
        
        # self.distance = 0
        rospy.loginfo(f"last{self.distance}")

        #rospy.Subscriber('/scan', LaserScan, self.scan_callback) #ここで2D-LiDARで取ったデータをすべて入手する

    def scan_callback(self, msg: LaserScan) -> None:
        
        if self.count == 1:
            exit()
        # print(f"スキャン開始角度：{msg.angle_min}")
        # print(f"スキャン終了角度：{msg.angle_max}")
        # print(f"1つのデータ間の角度差：{msg.angle_increment}")
        # print(f"1測距点間の取得時間：{msg.time_increment}")
        # print(f"1スキャンにかかる総時間：{msg.scan_time}")
        # print(f"測定可能な最小距離：{msg.range_min}")
        # print(f"測定可能な最大距離：{msg.range_max}")
        # print(f"距離データサイズ：{len(msg.ranges)}")
        #print(f"初期位置の距離データ：{msg.range[0]} m")

        self.ranges = msg.ranges
        self.angle_increment = msg.angle_increment

        self.center_index = len(msg.ranges) // 2 #ここで丁度真ん中のインデックス値を出している

        total_angle = 270.0 * math.pi / 180.0

        indexes_per_degree = int(len(msg.ranges) / total_angle * (math.pi / 180))

        #中心から＋ー30度のデータを取得
        start_index = max(self.center_index - 30 * indexes_per_degree, 0)
        end_index = min(self.center_index + 30 * indexes_per_degree, len(msg.ranges) - 1)

        #1度ごとのデータを取得
        self.ranges_60_deg = [msg.ranges[i] for i in range(start_index, end_index + 1, indexes_per_degree)]
        self.ranges_60_data = [(i-20, r) for i, r in enumerate(self.ranges_60_deg) if r > 0.2]

        self.has_scanned = True

        self.indexes_def, self.distances_def = zip(*self.ranges_60_data) if self.ranges_60_data else ([], [])

        if not self.distances_def:
            rospy.logerr(f"404 : distances data")
            return DistanceResponse(result=float("inf"))

        min_distance = min(self.distances_def) #距離データの中で最も小さい値を取得

        try:
            min_index = self.indexes_def[self.distances_def.index(min_distance)]
        except ValueError:
            rospy.logwarn(f"Could not find exact match for min_distance {min_distance}. Using approximate match.")
            min_index = self.indexes_def[min(range(len(self.distances_def)), key=lambda i: abs(self.distances_def[i] - min_distance))]

        angle_to = min_index
        trigonometric_distance = min_distance * math.cos(math.radians(angle_to)) #角度から直線距離を求めた

        distance = trigonometric_distance - 1.0
        
        if distance < 0:
            distance = 0
        
        print(f"人接近で、{distance}進む")
        self.bc.translateDist(distance, 0.3)
        self.bc.translateDist(0.001,0.001)


        rospy.loginfo(f"Fin")
        self.count += 1

        # return DistanceResponse(result=min_distance)
        # distance = float(distance)
        # return float(distance)
        # self.distance = distance
        self.distance = float(distance)
        rospy.loginfo(self.distance)
        # global dis
        # dis = distance

    def get_distance_info(self, req):
        rospy.loginfo(f"サービスに応答中：距離 {self.distance}")
        # return DistanceResponse(result=self.distance)
        return float(self.distance)

        
if __name__ == "__main__":
    node = person_distance()
    rospy.spin()


"""
2D-LiDARで取得したデータをインデックス値に変換し、中央のインデックス値を出す
そこからラジアンを用いて1度あたり、何個のデータがあるのかを求め、それをもとに1度ごとのデータを取得している
その中で最も小さい値を取り出し余弦定理を使って正面までの距離を求めている
現在正面までの距離から1m前まで進む
"""