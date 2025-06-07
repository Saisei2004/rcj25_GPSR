#!/usr/bin/env python3
# server.py

# import rospy
# import math
# from sensor_msgs.msg import LaserScan
# from fmm24.srv import Distance, DistanceResponse
# from simple_base_control import SimpleBaseControl

# class DistanceServer:
#     def __init__(self):
#         rospy.init_node('distance_client')
        
#         self.count = 0
#         self.has_scanned = False
#         self.distance = float('inf')

#         self.ranges = []
#         self.angle_increment = 0.0

#         self.scan_sub = rospy.Subscriber('/scan', LaserScan, self.scan_callback)
#         self.service = rospy.Service('/get_distance', Distance, self.handle_get_distance)

#         rospy.loginfo("Distance Server is ready.")
#         rospy.spin()

#     def scan_callback(self, msg: LaserScan) -> None:
        
#         if self.count == 1:
#             exit()
#         # print(f"スキャン開始角度：{msg.angle_min}")
#         # print(f"スキャン終了角度：{msg.angle_max}")
#         # print(f"1つのデータ間の角度差：{msg.angle_increment}")
#         # print(f"1測距点間の取得時間：{msg.time_increment}")
#         # print(f"1スキャンにかかる総時間：{msg.scan_time}")
#         # print(f"測定可能な最小距離：{msg.range_min}")
#         # print(f"測定可能な最大距離：{msg.range_max}")
#         # print(f"距離データサイズ：{len(msg.ranges)}")
#         #print(f"初期位置の距離データ：{msg.range[0]} m")

#         self.ranges = msg.ranges
#         self.angle_increment = msg.angle_increment

#         self.center_index = len(msg.ranges) // 2 #ここで丁度真ん中のインデックス値を出している

#         total_angle = 270.0 * math.pi / 180.0

#         indexes_per_degree = int(len(msg.ranges) / total_angle * (math.pi / 180))

#         #中心から＋ー30度のデータを取得
#         start_index = max(self.center_index - 30 * indexes_per_degree, 0)
#         end_index = min(self.center_index + 30 * indexes_per_degree, len(msg.ranges) - 1)

#         #1度ごとのデータを取得
#         self.ranges_60_deg = [msg.ranges[i] for i in range(start_index, end_index + 1, indexes_per_degree)]
#         self.ranges_60_data = [(i-20, r) for i, r in enumerate(self.ranges_60_deg) if r > 0.2]

#         self.has_scanned = True

#         self.indexes_def, self.distances_def = zip(*self.ranges_60_data) if self.ranges_60_data else ([], [])

#         if not self.distances_def:
#             rospy.logerr(f"404 : distances data")
#             return DistanceResponse(result=float("inf"))

#         min_distance = min(self.distances_def) #距離データの中で最も小さい値を取得

#         try:
#             min_index = self.indexes_def[self.distances_def.index(min_distance)]
#         except ValueError:
#             rospy.logwarn(f"Could not find exact match for min_distance {min_distance}. Using approximate match.")
#             min_index = self.indexes_def[min(range(len(self.distances_def)), key=lambda i: abs(self.distances_def[i] - min_distance))]

#         angle_to = min_index
#         trigonometric_distance = min_distance * math.cos(math.radians(angle_to)) #角度から直線距離を求めた

#         self.distance = trigonometric_distance - 1.0
        

#         self.has_scanned = True

#     def handle_get_distance(self, req):
#         if not self.has_scanned:
#             rospy.logwarn("No scan data yet.")
#             return DistanceResponse(result=float("inf"))

#         rospy.loginfo(f"Returning distance: {self.distance:.2f} m")
#         return DistanceResponse(result=self.distance)

# if __name__ == '__main__':
#     DistanceServer()

import rospy
import math
from sensor_msgs.msg import LaserScan
from fmm24.srv import Distance, DistanceResponse
#from simple_base_control import SimpleBaseControl  # ← 今回使わないのでコメントアウトしてOK

class DistanceServer:
    def __init__(self):
        rospy.init_node('distance_client')  # ← サーバなので名前も修正
        
        self.has_scanned = False
        self.distance = float('inf')

        self.scan_sub = rospy.Subscriber('/scan', LaserScan, self.scan_callback)
        self.service = rospy.Service('/get_distance', Distance, self.handle_get_distance)

        rospy.loginfo("Distance Server (v2) is ready.")
        rospy.spin()

    def scan_callback(self, msg: LaserScan) -> None:
        # データ受け取り時の処理

        self.ranges = msg.ranges
        self.angle_min = msg.angle_min  # スキャン開始角度
        self.angle_increment = msg.angle_increment  # 各データ間の角度差
        
        candidates = []  # 条件を満たす(x, y)リスト

        for i, r in enumerate(self.ranges):
            if r < 0.2 or math.isinf(r):  # ノイズ除去
                continue

            # θを計算（開始角度 + インデックス * 角度増分）
            theta = self.angle_min + i * self.angle_increment

            # (x, y)座標に変換
            x = r * math.cos(theta)
            y = r * math.sin(theta)

            # xが-10～+10の範囲にあるかチェック
            if -0.1 <= x <= 0.1 and y > 0:
                candidates.append((x, y))

        if not candidates:
            rospy.logwarn("No valid points in x=[-10,10] range.")
            self.distance = float('inf')
        else:
            # y座標が一番小さいものを選ぶ
            _, min_y = min(candidates, key=lambda p: p[1])
            self.distance = min_y

        self.has_scanned = True

    def handle_get_distance(self, req):
        if not self.has_scanned:
            rospy.logwarn("No scan data yet.")
            return DistanceResponse(result=float("inf"))

        rospy.loginfo(f"Returning distance: {self.distance:.2f} m")
        return DistanceResponse(result=self.distance)

if __name__ == '__main__':
    DistanceServer()

