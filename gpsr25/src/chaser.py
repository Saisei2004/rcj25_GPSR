#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rospy
import time
from geometry_msgs.msg import Point
from std_msgs.msg import String
from happymimi_voice_msgs.srv import YesNo
from happymimi_msgs.srv import StrTrg

from base_control import BaseControl
from chaser_setup_node import chaser_setup
import threading
from happymimi_voice_msgs.srv import piperTTS, piperTTSRequest

class SimpleChaser:
    def __init__(self):
        # rospy.init_node("simple_chaser_node")
        self.cmd_sub = Point()
        self.chaser_pub = rospy.Publisher('/chacer_sign', String, queue_size=10)
        rospy.Subscriber('/follow_me/distance_angle_data', Point, self.chase_callback)
        self.base_control = BaseControl()
        self.yesno_srv = rospy.ServiceProxy('/yes_no', YesNo)
        self.arm_srv = rospy.ServiceProxy('/servo/arm', StrTrg)
        self.tts_pub = rospy.Publisher('/mimic1/tts/topic', String, queue_size=10)
        
        self.start_time = time.time()
        self.spoke = False
        self.tts_ser = rospy.ServiceProxy("/piper/tts", piperTTS)
        self.tts_ser2 = rospy.ServiceProxy("/piper/tts", piperTTS)

    def tts_pub2(self,text):
    # --- スレッドの中で実行する関数を定義 ---
        def speak():
            try:
                rospy.wait_for_service("/piper/tts")  # サービスを待つ
                self.tts_ser2(text)  # テキストを渡してTTSサービスを呼び出す
            except rospy.ServiceException as e:
                rospy.logerr(f"TTSサービス呼び出し失敗: {e}")

        # --- スレッドをその場で作ってスタート ---
        t = threading.Thread(target=speak)
        t.start()


    def chase_callback(self, rec):
        self.cmd_sub = rec

    def speak(self, text):
        self.tts_pub.publish(text)
        rospy.sleep(1.0)

    def start_chase(self):
        self.tts_pub2("I am starting to follow you. Please wait.")
        self.tts_pub2("Please stand in front of me")
        chaser_setup("start")
        rospy.sleep(3.0)

        while not rospy.is_shutdown():
            self.chaser_pub.publish('start')
            rospy.sleep(1.0)

            distance = self.cmd_sub.x
            time_elapsed = time.time() - self.start_time

            if distance > 0 and not self.spoke:
                self.tts_pub2("I am now following you.")
                self.spoke = True

            # 50秒後かつ停止距離に入ったら終了処理へ
            if (-0.2 < distance < 0 or 0 < distance <= 0.15) and time_elapsed >= 30:
                self.base_control.translateDist(-0.2, 0.2)
                self.tts_ser2("Is this the location?")
                try:
                    if self.yesno_srv().result:
                        self.stop_chase()
                        return
                except rospy.ServiceException as e:
                    rospy.logerr(f"Yes/No service failed: {e}")
            rospy.sleep(0.5)

    def stop_chase(self):
        self.chaser_pub.publish('stop')
        rospy.sleep(1.0)
        self.base_control.translateDist(-0.1, 0.15)
        # self.speak("Here you are.")
        # self.speak("Here you are.")
        # rospy.sleep(1.0)
        # self.arm_srv("give")
        # rospy.sleep(3.0)
        # self.speak("Returning to start position.")
        # self.base_control.rotateAngle(180, 0, 0.5)
        # rospy.sleep(1.5)
        # self.arm_srv("arm_tu_grasp")
        # rospy.sleep(1.0)
        chaser_setup("stop")

if __name__ == "__main__":
    chaser = SimpleChaser()
    chaser.start_chase()
