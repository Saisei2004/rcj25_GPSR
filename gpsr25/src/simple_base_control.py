#!/usr/bin/env python3
# coding: utf-8

import rospy
import math
from geometry_msgs.msg import Twist, PoseWithCovarianceStamped

class SimpleBaseControl:
    def __init__(self):
        self.cmd_vel_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
        rospy.Subscriber('/amcl_pose', PoseWithCovarianceStamped, self.pose_callback)
        self.current_pose = None

    def pose_callback(self, msg):
        self.current_pose = msg.pose.pose

    def rotateAngle(self, angle_deg, angular_speed=0.6):
        """指定した角度だけ回転する（度単位）"""
        twist = Twist()
        rad = math.radians(angle_deg*1.0093)
        twist.angular.z = angular_speed if rad > 0 else -angular_speed
        duration = abs(rad / angular_speed)

        rospy.loginfo(f"↻ 回転: {angle_deg}°（時間: {duration:.2f}s, 速度: {angular_speed}）")
        self.cmd_vel_pub.publish(twist)
        rospy.sleep(duration)
        self.cmd_vel_pub.publish(Twist())  # 停止
        rospy.sleep(0.2)

    def translateDist(self, distance, linear_speed=0.3):
        """指定した距離だけ直進または後退（メートル単位）"""
        twist = Twist()
        twist.linear.x = linear_speed if distance > 0 else -linear_speed
        duration = abs(distance / linear_speed)

        rospy.loginfo(f"⇆ 直進/後退: {distance}m（時間: {duration:.2f}s, 速度: {linear_speed}）")
        self.cmd_vel_pub.publish(twist)
        rospy.sleep(duration)
        for i in range(3):
            rospy.loginfo("！！停止信号発信中！！")
            self.cmd_vel_pub.publish(Twist())  # 停止
        
        rospy.sleep(0.2)
