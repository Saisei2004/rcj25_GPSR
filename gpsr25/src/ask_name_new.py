# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import rospy
import roslib
import sys
import re
import difflib
import math

from happymimi_voice_msgs.srv import TTS
from sensor_msgs.msg import LaserScan
from happymimi_voice_msgs.srv import TextToSpeech
from std_msgs.msg import String
from happymimi_msgs.srv import SetStr, SetStrRequest, StrTrg
from fmm24.srv import Distance, DistanceResponse
from happymimi_voice_msgs.srv import piperTTS, piperTTSRequest
from simple_base_control import SimpleBaseControl
from person_distance import *

file_path = roslib.packages.get_pkg_dir('happymimi_teleop') + '/src/'
sys.path.insert(0, file_path)
from base_control import BaseControl

class Ask_name:
    def __init__(self, angle_list=None, want_name=['Jack']):
        # rospy.init_node("ask_node")
    
    
    

        rospy.wait_for_service('get_distance')
        try:
            self.get_distance_service = rospy.ServiceProxy('get_distance', Distance)
            rospy.loginfo("Connected to Distance service.")
        except rospy.ServiceException as e:
            rospy.logerr("Service call failed: %s", e)
        

        self.bc = BaseControl()
        self.bc2 = SimpleBaseControl()
        self.tts_pub = rospy.Publisher('/mimic1/tts/topic', String, queue_size=10)
        self.tts_ser = rospy.ServiceProxy('/mimic1/tts/service', TextToSpeech)
        self.tts_ser = rospy.ServiceProxy("/piper/tts", piperTTS)
        self.stt_ser = rospy.ServiceProxy('/whisper_stt', SetStr)

        self.angle_list = angle_list if angle_list else [30, 50, 80, 90]
        self.want_name = want_name

        self.num = len(self.angle_list)
        self.now_num = 1
        self.list_num = 0
        self.now_angle = 90
        self.done = False

        # self.name_list = ["Jack", "Aaron", "Angel", "Adam", "Vanessa", "Chris", "William", "Max", "Hunter", "Olivia", "them"]
        self.answer_list = ["yes", "no"]

    def ask_name(self):
        print(self.angle_list)
        for i in range(self.num):
            angle = self.angle_list[self.list_num]
            print(self.now_angle)
            if angle < self.now_angle:
                if i == 0:
                    rot_angle = angle * -1#+ self.now_angle
                else:
                    rot_angle = angle
                print("→",rot_angle)
                self.bc2.rotateAngle(rot_angle,0.5)#ここなぜ３つになってた？？？？
                rospy.sleep(3)

                response = self.get_distance_service()
                distance_to_move = response.result
                rospy.loginfo(f"取得した値{distance_to_move}")

                if distance_to_move < 0:
                    distance_to_move = 0
                print(distance_to_move)
                response = person_distance()
                rospy.sleep(5)
                print("🍏🍏🍏🍏🍏",response.distance)
                # self.bc.translateDist(distance_to_move, 0.3)
                # self.bc.translateDist(0.1,0.1)
                # self.bc.translateDist(-0.01,0.01)

                print("ああああああああああああああああああああああああああああああああ")
                rospy.sleep(1.0)

                while True:
                    self.tts_ser(f"Are you {self.want_name}? Please answer yes or no.")
                    answer = self.stt_ser(SetStrRequest()).result
                    answer_words = [w for w in re.split("[. !?,]", answer.strip()) if w]
                    if answer_words:
                        answer = answer_words[-1]
                        rospy.loginfo(answer)

                        answer = difflib.get_close_matches(answer, self.answer_list, n=1, cutoff=0.3)
                        print("answer💢:",answer)
                        yes_variants = ["yes", "yeah", "yep", "yup", "sure", "certainly", "absolutely", "affirmative", "indeed", "yesh", "Jess", "guess"]
                        if type(answer) == list:
                            answer = answer[0]
                        if answer in yes_variants:
                            rospy.loginfo("ターゲットを発見！")
                            rospy.loginfo(f"ターゲットの名前：{self.want_name}、ターゲットのいる角度：{angle}")
                            self.done = True
                            return "FIN"

                        else:
                            rospy.loginfo("ターゲットではありませんでした。")
                            self.bc2.translateDist(-1 * float(response.distance), 0.3)
                            break

                    else:
                        rospy.loginfo("聞き取り失敗")
                        
                if self.done:
                    break

        return "NOT_FOUND"

if __name__ == "__main__":
    # rospy.init_node("ask_node")
    client = Ask_name()
    result = client.ask_name()
    print(f"結果: {result}")
    rospy.spin()

def run_ask_name_with_params(angle_list, want_name):
    """
    他ファイルから呼び出すための関数。
    :param angle_list: 角度のリスト（例: [30, 60, 90]）
    :param want_name: 探したい名前のリスト（例: ["Olivia"]）
    :return: 実行結果（FIN or NOT_FOUND）
    """
    print("🌟",angle_list,"の方向の中から", want_name,"を探す🌟")
    # rospy.init_node("ask_node", anonymous=True)
    client = Ask_name(angle_list=angle_list, want_name=want_name)
    result = client.ask_name()
    return result

