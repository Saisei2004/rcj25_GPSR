import roslib, sys, rospy
file_path = roslib.packages.get_pkg_dir('happymimi_teleop') + '/src/'
sys.path.insert(0, file_path)
from base_control import BaseControl
from person_distance import *
from config import *
from happymimi_navigation.srv import NaviLocation, NaviCoord
navi = rospy.ServiceProxy('navi_location_server', NaviLocation)
bc = BaseControl()
from happymimi_voice_msgs.srv import piperTTS, piperTTSRequest

'''書き方
bc.rotateAngle(angle,0,1)
bc.translateDist(distance)
'''

from happymimi_voice_msgs.srv import TextToSpeech
#逐次処理でしゃべる
tts_ser = rospy.ServiceProxy('/mimic1/tts/service', TextToSpeech)

from happymimi_msgs.srv import SetStr, SetStrRequest
#何言ってるか聞き取る
stt_ser = rospy.ServiceProxy('/whisper_stt', SetStr)
from config import names

# names = ["Jack", "Aaron", "Angel", "Adam", "Vanessa", "Chris", "William", "Max", "Hunter", "Olivia","them"]

# def find_name_mod(name):

#     angle_list = (30,100,180)

#     '''
#     ここで江もりが作ったやつ埋め込んでangle_listに角度のリスト格納
#     '''

#     for i in angle_list:
#         print(f"find_nameで{i}度回転")
#         bc.rotateAngle(i,0,1)
#         print("find_nameで進む")
#         distance = person_distance()
#         # tts_ser("What is your name?")
#         # ans = stt_ser(SetStrRequest()).result
#         name_list = names
#         confirmed_name = get_confirmed_name(name_list)
#         # return confirmed_name
#         if confirmed_name == name:
#             break
#         else:
#             bc.translateDist(distance * -1)
#             bc.rotateAngle(i * -1,0,1)

import re
from happymimi_voice_msgs.srv import YesNo
yesno = rospy.ServiceProxy('/yes_no', YesNo)

def get_confirmed_name(name_list):
    """
    音声認識で取得した文章から、name_listに近い名前を抽出し、
    ユーザーに確認を取って確定させる関数。最大3回まで試行する。
    self.tts_ser() で話しかけ、self.stt_ser() で入力を受け取り、
    self.yesno() でYes/Noの確認を取る。
    """
    confirmed_name = None
    tts_ser2 = rospy.ServiceProxy("/piper/tts", piperTTS)

    for attempt in range(3):
        tts_ser2("Hi! Whatcha name?")  # 音声で話しかける
        print("hi! whatcha name?")
        user_input = stt_ser(SetStrRequest()).result  # 音声認識の結果を取得
        # print(user_input)

        sentences = [s.strip() for s in user_input.split(',')]
        results = []

        for sentence in sentences:
            # 名前っぽい語句を抽出
            match = re.search(
                r"(?:my name is|call me|I'm|i am|known as|they call me|some say|some call me|nickname is)\s+(\w+)",
                sentence, re.IGNORECASE)

            if not match:
                match = re.search(r"(\w+)[.!?]?$", sentence)

            if match:
                target_word = match.group(1).strip()
                closest_word = None
                min_distance = float('inf')

                for word in name_list:
                    if word[0].lower() == target_word[0].lower():
                        # レーベンシュタイン距離を計算
                        m, n = len(target_word), len(word)
                        dp = [[0] * (n + 1) for _ in range(m + 1)]

                        for i in range(m + 1):
                            for j in range(n + 1):
                                if i == 0:
                                    dp[i][j] = j
                                elif j == 0:
                                    dp[i][j] = i
                                elif target_word[i - 1].lower() == word[j - 1].lower():
                                    dp[i][j] = dp[i - 1][j - 1]
                                else:
                                    dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])

                        distance = dp[m][n]
                        if distance < min_distance:
                            min_distance = distance
                            closest_word = word

                if closest_word:
                    results.append(f"Input: '{sentence}' -> Closest name: '{closest_word}'")
                    tts_ser2("Are you {}? Please answer Yes or No.".format(closest_word))
                    print("Are you {}? Please answer Yes or No.".format(closest_word))
                    yes_no = yesno().result

                    if yes_no:
                        confirmed_name = closest_word
                        results.append(f"Confirmed name: '{closest_word}'")
                        break
                    else:
                        print("Let's try again.")
                else:
                    results.append(f"Input: '{sentence}' -> No close match found.")
            else:
                results.append(f"Input: '{sentence}' -> Name extraction failed.")

        if confirmed_name:
            break
        elif attempt < 2:
            tts_ser2("What's your name again? Please say it clearly.")
        else:
            print("Maximum attempts reached.")

    if confirmed_name:
        print(f"Confirmed name: {confirmed_name}")
    else:
        print("No valid name confirmed.")

    return confirmed_name  # None or 確定した名前
