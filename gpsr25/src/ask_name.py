#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# import rospy
# import roslib
# import sys
# import re
# import difflib
# import math

# from happymimi_voice_msgs.srv import TTS
# from sensor_msgs.msg import LaserScan
# from happymimi_voice_msgs.srv import TextToSpeech
# from std_msgs.msg import String
# from happymimi_msgs.srv import SetStr, SetStrRequest, StrTrg
# from fmm24.srv import Distance, DistanceResponse

# file_path = roslib.packages.get_pkg_dir('happymimi_teleop') + '/src/'
# sys.path.insert(0, file_path)
# from base_control import BaseControl

# class Ask_name:
#     def __init__(self, angle_list=None, want_name=['Jack']):
#         # if not rospy.get_node_uri():
#         #     rospy.init_node("ask_node")

#         rospy.wait_for_service('get_distance')
#         try:
#             self.get_distance_service = rospy.ServiceProxy('get_distance', Distance)
#             rospy.loginfo("Connected to Distance service.")
#         except rospy.ServiceException as e:
#             rospy.logerr("Service call failed: %s", e)

#         self.bc = BaseControl()
#         self.tts_pub = rospy.Publisher('/mimic1/tts/topic', String, queue_size=10)
#         self.tts_ser = rospy.ServiceProxy('/mimic1/tts/service', TextToSpeech)
#         self.stt_ser = rospy.ServiceProxy('/whisper_stt', SetStr)

#         self.angle_list = angle_list if angle_list else [30, 50, 80, 90]
#         self.want_name = want_name

#         self.num = len(self.angle_list)
#         self.now_num = 1
#         self.list_num = 0
#         self.now_angle = 90

#         self.name_list = ["Jack", "Aaron", "Angel", "Adam", "Vanessa", "Chris", "William", "Max", "Hunter", "Olivia", "them"]
#         self.answer_list = ["yes", "no"]

#     def ask_name(self):
#         print(self.angle_list)
#         for i in range(self.num):
#             angle = self.angle_list[self.list_num]
#             print(self.now_angle)
#             if angle < self.now_angle:
#                 rot_angle = angle - self.now_angle
#                 print(rot_angle)
#                 self.bc.rotateAngle(rot_angle, 0, 1)

#                 response = self.get_distance_service()
#                 distance_to_move = response.result
#                 rospy.loginfo(f"取得した値{distance_to_move}")

#                 if distance_to_move < 0:
#                     distance_to_move = 0

#                 self.bc.translateDist(distance_to_move, 0.5)
#                 rospy.sleep(1.0)

#                 while True:
#                     self.tts_ser("What your name?")
#                     sentence = self.stt_ser(SetStrRequest()).result

#                     name_tx_list = [w for w in re.split("[. !?,]", sentence.strip()) if w]
#                     rospy.loginfo(name_tx_list)

#                     if name_tx_list:
#                         name = name_tx_list[-1]
#                         rospy.loginfo(name)

#                         name = difflib.get_close_matches(name, self.name_list, n=1, cutoff=0.3)
#                         rospy.loginfo(name)

#                         if name:
#                             self.tts_ser(f"Are you {name[0]}?")
#                             self.tts_ser("please answer yes or no.")
#                             answer = self.stt_ser(SetStrRequest()).result

#                             answer_words = [w for w in re.split("[. !?,]", answer.strip()) if w]
#                             if answer_words:
#                                 answer = answer_words[-1]
#                                 rospy.loginfo(answer)

#                                 answer = difflib.get_close_matches(answer, self.answer_list, n=1, cutoff=0.3)
#                                 rospy.loginfo(answer)

#                                 if answer == ['yes']:
#                                     rospy.loginfo("名前の受取に成功")
#                                     break
#                                 else:
#                                     rospy.loginfo("名前の受取に失敗。再試行します。")
#                                     continue
#                         else:
#                             rospy.loginfo("候補が見つかりませんでした。再試行します。")
#                             continue
#                     else:
#                         rospy.loginfo("聞き取り失敗。再試行します。")
#                         continue

#                 rospy.loginfo(f"受け取った名前：{name}")
#                 rospy.loginfo(f"ターゲットの名前：{self.want_name}")
#                 if name[0] == self.want_name:
#                     rospy.loginfo("名前の一致を確認")
#                     rospy.loginfo(f"ターゲットの名前：{name}、ターゲットのいた角度：{angle}")
#                     self.bc.translateDist(-distance_to_move, 0.5)
#                     return "FIN"
#                 else:
#                     rospy.loginfo("名前が一致しませんでした。")
#                     self.bc.translateDist(-distance_to_move, 0.5)
#                     continue
#             else:
#                 rospy.loginfo("2回目以降")

#         return "NOT_FOUND"

# if __name__ == "__main__":
#     # rospy.init_node("ask_node")
#     client = Ask_name()
#     result = client.ask_name()
#     print(f"結果: {result}")
#     rospy.spin()

# def run_ask_name_with_params(angle_list, want_name):
#     """
#     他ファイルから呼び出すための関数。
#     :param angle_list: 角度のリスト（例: [30, 60, 90]）
#     :param want_name: 探したい名前のリスト（例: ["Olivia"]）
#     :return: 実行結果（FIN or NOT_FOUND）
#     """
#     print("🌟",angle_list,"の方向の中から", want_name,"を探す🌟")
#     # rospy.init_node("ask_node", anonymous=True)
#     client = Ask_name(angle_list=angle_list, want_name=want_name)
#     result = client.ask_name()
#     return result

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rospy
import roslib
import sys
import re
import difflib

from happymimi_voice_msgs.srv import TextToSpeech
from std_msgs.msg import String
from happymimi_msgs.srv import SetStr, SetStrRequest
from fmm24.srv import Distance
from happymimi_voice_msgs.srv import piperTTS, piperTTSRequest

# base_control.py に含まれる制御クラスを読み込む
file_path = roslib.packages.get_pkg_dir('happymimi_teleop') + '/src/'
sys.path.insert(0, file_path)
from base_control import BaseControl

class AskName:
    def __init__(self, angle_list=None, want_name=['Jack']):
        rospy.wait_for_service('get_distance')
        self.get_distance_service = rospy.ServiceProxy('get_distance', Distance)
        self.bc = BaseControl()
        self.tts_ser = rospy.ServiceProxy('/mimic1/tts/service', TextToSpeech)
        self.tts_ser = rospy.ServiceProxy("/piper/tts", piperTTS)
        self.stt_ser = rospy.ServiceProxy('/whisper_stt', SetStr)

        self.angle_list = angle_list if angle_list else [30, 50, 80, 90]
        self.want_name = want_name

        self.now_angle = 90
        self.name_list = ["Jack", "Aaron", "Angel", "Adam", "Vanessa", "Chris", "William", "Max", "Hunter", "Olivia", "them"]
        self.answer_list = ["yes", "no"]

    def ask_name(self):
        for angle in self.angle_list:
            rot_angle = angle - self.now_angle
            self.bc.rotateAngle(rot_angle * -1)
            print(rot_angle* -1, "回転します")
            self.now_angle = angle

            # 距離取得と移動
            try:
                distance_to_move = self.get_distance_service().result
                if distance_to_move < 0:
                    distance_to_move = 0
            except rospy.ServiceException as e:
                rospy.logerr(f"距離取得に失敗: {e}")
                continue

            self.bc.translateDist(distance_to_move)
            print(f"移動距離: {distance_to_move}")
            rospy.sleep(1.0)

            # 名前の確認ループ
            while True:
                self.tts_ser("What your name?")
                print("what your name?")
                sentence = self.stt_ser(SetStrRequest()).result
                name_words = [w for w in re.split(r"[. !?,]", sentence.strip()) if w]

                if not name_words:
                    rospy.loginfo("名前が取得できませんでした。再試行します。")
                    continue

                name = difflib.get_close_matches(name_words[-1], self.name_list, n=1, cutoff=0.3)
                if not name:
                    rospy.loginfo("名前の候補が見つかりません。再試行します。")
                    continue

                self.tts_ser(f"Are you {name[0]}?")
                print(f"Are you {name[0]}?")
                self.tts_ser("please answer yes or no.")
                answer = self.stt_ser(SetStrRequest()).result
                answer_words = [w for w in re.split(r"[. !?,]", answer.strip()) if w]

                if answer_words:
                    final_answer = difflib.get_close_matches(answer_words[-1], self.answer_list, n=1, cutoff=0.3)
                    if final_answer == ['yes']:
                        rospy.loginfo(f"✅ 名前一致: {name[0]}")
                        self.bc.translateDist(-distance_to_move)
                        return "FIN"
                    else:
                        rospy.loginfo("名前の確認に失敗。次の人へ。")
                        break

            self.bc.translateDist(-distance_to_move)

        return "NOT_FOUND"

def run_ask_name_with_params(angle_list, want_name):
    # rospy.init_node("ask_name_node")
    client = AskName(angle_list=angle_list, want_name=want_name)
    return client.ask_name()

# if __name__ == "__main__":
#     result = run_ask_name_with_params([30, 60, 90], ["Olivia"])
#     print(f"🎉 結果: {result}")
