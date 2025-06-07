#!/usr/bin/env python3
# -*- coding: utf-8 -*-

########################################
'''
ここで各行動を管理します。
モジュールはすべてここで管理します。

以下起動方法

roslaunch grasping_items grasping_items.launch

rosservice info /execute_grasp
をして、


'''
########################################

import rospy
import smach
import smach_ros
from utils import *
import rospy
import difflib
from std_msgs.msg import Int32
import roslib
import sys
import yaml
import re
import math
import json
import os
import subprocess
from cmd_gen import *
from config import talk
from std_srvs.srv import Trigger, TriggerResponse
import threading

from std_msgs.msg import Bool
#######################################
# モジュールのインポート
rospy.init_node('minimal_node', anonymous=True)

file_path = roslib.packages.get_pkg_dir('happymimi_teleop') + '/src/'
sys.path.insert(0, file_path)
from base_control import BaseControl
from happymimi_msgs.srv import SimpleString
from std_msgs.msg import String
from happymimi_voice_msgs.srv import TextToSpeech
from happymimi_msgs.srv import SetStr, SetStrRequest
from happymimi_navigation.srv import NaviLocation, NaviCoord
from happymimi_voice_msgs.srv import YesNo
from std_msgs.msg import Float64
from happymimi_msgs.srv import SetStr
from happymimi_msgs.srv import SimpleTrg, StrTrg, SetStr
from happymimi_msgs.srv import StrTrg
from happymimi_recognition_msgs.srv import depth_meter
from happymimi_recognition_msgs.srv import MultipleLocalize
from happymimi_recognition_msgs.srv import depth_meter
from happymimi_recognition_msgs.srv import StrInt
from person_distance import *
from happymimi_voice_msgs.srv import piperTTS, piperTTSRequest
from happymimi_msgs.srv import SimpleString
from std_msgs.msg import String
# from grasping_view_only import initialize_publishers, look_at_target_object
clip_pub = rospy.Publisher('/clip_sign', String)
# from chaser import *


# #########################################
# #ここでモジュール初期化（ごめんなさい）
tts_ser = rospy.ServiceProxy("/piper/tts", piperTTS)
#並列処理でしゃべる
# tts_pub = rospy.Publisher('/mimic1/tts/topic', String, queue_size=10)


#逐次処理でしゃべる
# tts_ser = rospy.ServiceProxy('/mimic1/tts/service', TextToSpeech)
tts_ser2 = rospy.ServiceProxy("/piper/tts", piperTTS)


def grasp_launch():
    # launch起動
    subprocess.Popen([
        "gnome-terminal", "--", "bash", "-c",
        "source ~/.bashrc && source ~/main_ws/devel/setup.bash && roslaunch grasping_items grasping_items_tu.launch"
    ])

    rospy.loginfo("⏳ /execute_grasp サービスを待機中...")
    try:
        rospy.wait_for_service("/execute_grasp", timeout=30.0)
        rospy.loginfo("✅ /execute_grasp 起動確認")
        rospy.sleep(5.0)
    except rospy.ROSException as e:
        rospy.logerr(f"❌ /execute_grasp サービス待機タイムアウト: {e}")
        
def kill_grasp_launch():
    subprocess.Popen(["pkill", "-f", "roslaunch grasping_items grasping_items_tu.launch"])
    rospy.loginfo("🛑 grasping_items.launch を停止")


def tts_pub2(text):
    # --- スレッドの中で実行する関数を定義 ---
    def speak():
        try:
            rospy.wait_for_service("/piper/tts")  # サービスを待つ
            tts_ser2(text)  # テキストを渡してTTSサービスを呼び出す
        except rospy.ServiceException as e:
            rospy.logerr(f"TTSサービス呼び出し失敗: {e}")

    # --- スレッドをその場で作ってスタート ---
    t = threading.Thread(target=speak)
    t.start()


#何言ってるか聞き取る
stt_ser = rospy.ServiceProxy('/whisper_stt', SetStr)
#ナヴィゲーション
# navi = rospy.ServiceProxy('navi_location_server', NaviLocation)

def navi(navi_room):
    print(navi_room)
    
    
#人に近づく（旧バージョン）
apper = rospy.ServiceProxy('/approach_person_server', StrTrg)#depthmaskのに変えたい
#デプスマスク
depth_meter = rospy.ServiceProxy('depth_mask',depth_meter)
#3次元位置推定
multiple = rospy.ServiceProxy('/recognition/multiple_localize',MultipleLocalize)
#クリップで特徴検出
clip_pub = rospy.Publisher('/clip_sign', String)
#人の方見る？
choose_person = rospy.ServiceProxy('choose_person', SetStr)
#ベースコントロール
bc = BaseControl()
bc = SimpleBaseControl()
#いぇすのー
yesno = rospy.ServiceProxy('/yes_no', YesNo)
#頭の角度変える
head = rospy.Publisher('/servo/head',Float64, queue_size = 1)
#アームの形を変える
arm = rospy.ServiceProxy('/servo/arm', StrTrg)
#クリップの結果出力
yaml_path = roslib.packages.get_pkg_dir('person_feature_extraction') + "/config/extract.yaml"
#人接近
#person_distance()
#Yoloの情報の取得 recog_tool_v8
yolo_info = rospy.ServiceProxy('/recognition/yolo_info', SetStr)
#指定した物体の数を数える
obj_count = rospy.ServiceProxy('/target_check', StrInt)
 #chaser24を起動させるためのトピック
chaser_pub = rospy.Publisher('/chacer_sign', String, queue_size=10)
#新たに作った指定した塗ったいの方向に向くモジュール
obj_find = rospy.ServiceProxy('/obj_find', SetStr)

endeffector_pub = rospy.Publisher("/servo/endeffector", Bool, queue_size=1)

#定数
IMAGE_WIDTH = 640  # 画像の幅（ピクセル）
HORIZONTAL_FOV = 70  # 水平視野角（度）

yaml_path = roslib.packages.get_pkg_dir('person_feature_extraction') + "/config/extract.yaml"

def person_center():
    #yolo_infoの結果をjson形式に変換、つまり辞書型に変換
    print("lokhsjijgsoih;oshgtos")
    result = json.loads(yolo_info().result)
    print(result)
    max_area = 0
    target_center_x = 0
    
    for obj in result:
        if obj.get('name') == 'person':
            # value = obj['person']
            area = obj['size_x'] * obj['size_y']
            if area > max_area:
                max_area = area
                target_center_x = obj['center_x']

    
    print(f"目標の中心x座標: {target_center_x}")
    return target_center_x

def calculate_rotation_angle(target_x):
    # 画像の中心座標
    image_center = IMAGE_WIDTH / 2
    # 中心からのずれ（ピクセル）
    offset = target_x - image_center
    # 1ピクセルあたりの角度（度）
    angle_per_pixel = HORIZONTAL_FOV / IMAGE_WIDTH
    # 必要な回転角度（度）
    rotation_angle = offset * angle_per_pixel
    return rotation_angle

#########################################
from happymimi_msgs.srv import Str2Str

def parse_response(response_str):
    """
    "count=4:list=100,130,140,230" のような文字列を解析して
    count（int）とlist（intのリスト）を返す
    """
    """
    count = 0
    angle_list = []

    parts = response_str.split(":")
    for part in parts:
        if part.startswith("count="):
            count = int(part.replace("count=", ""))
        elif part.startswith("list="):
            angle_str = part.replace("list=", "")
            if angle_str.strip():
                angle_list = list(map(int, angle_str.split(",")))

    return count, angle_list
    """

    count = 0
    angle_list = []
    text = ""
    
    parts = response_str.split(":")
    for part in parts:
        if part.startswith("count="):
            count = int(part.replace("count=", ""))
        elif part.startswith("list="):
            angle_str = part.replace("list=", "")
            if angle_str.strip():
                angle_list = list(map(int, angle_str.split(",")))
        elif part.startswith("text="):
            text = part.replace("text=", "")
    
    print(count)
    print(angle_list) 
    print(text)
    
    return count, angle_list, text

    
    """
    江森が追加　4月20日　textへの対応のため
    "count=4:list=100,130,140,230:text=Hello World !" のような文字列を解析して
    count（int）、list（intのリスト）、text（文字列）を返す
    """
    # count = 0
    # angle_list = []
    # text = ""

    # parts = response_str.split(":")
    # for part in parts:
    #     if part.startswith("count="):
    #         count = int(part.replace("count=", ""))
    #     elif part.startswith("list="):
    #         angle_str = part.replace("list=", "")
    #         if angle_str.strip():
    #             angle_list = list(map(int, angle_str.split(",")))
    #     elif part.startswith("text="):
    #         text = part.replace("text=", "")

    # print(count)
    # print(list)
    # print(text)
    # return count, angle_list, text

from grasping_items.srv import GraspItemWithTarget, GraspItemWithTargetRequest
def grasp(obj):
    obj_to_reco = {
    "bottle":"plastic bottle",
    "noodle": "cup noodle",
    "noodles": "cup noodle",
    "cup noodle":"noodles",
    "cookies": "box",
    "cookie": "box",
    "potatp chips": "chip star",
    "potatp chip": "chip star",
    "gummy": "caramel corn",
    "detergent" : "detergent",
    "cup" : "cup",
    "lunch box" : "box",
    "bowl" : "bowl",
    "dice" : "dice",
    "light bulb" : "box",
    # "block" : "box" ,
    "phone stand":"phone stand",
    "caramel corn":"caramel corn"

    }

    reco_obj = obj_to_reco.get(obj)
    print(reco_obj)
    if reco_obj is None:
        print(f"⚠️ 指定されたオブジェクト『{obj}』は登録されていません。")
    else:
        print(f"🧾 対象のオブジェクトは「{reco_obj}」です。")


    # rospy.init_node('call_execute_grasp_service')

    # --- サービス待機 ---
    rospy.wait_for_service('/execute_grasp')
    try:
        # サービスプロキシ作成
        grasp_srv = rospy.ServiceProxy('/execute_grasp', GraspItemWithTarget)

        # リクエスト作成
        req = GraspItemWithTargetRequest()
        req.target_object = reco_obj  # ← 把持したい物体名をここに書く

        # サービスを呼び出す
        res = grasp_srv(req)

        # 結果表示
        if res.success:
            rospy.loginfo("✅ 把持成功しました！")
            head.publish(0.0)
            return True
        else:
            rospy.logwarn("❌ 把持失敗しました。")
            return False
    except rospy.ServiceException as e:
        rospy.logerr(f"サービス呼び出し失敗: {e}")
    

def call_service(mode="list", prompt="", angle=180):
    rospy.wait_for_service('/multi_person_scan')
    try:
        service = rospy.ServiceProxy('/multi_person_scan', Str2Str)
        input_str = f"mode={mode},prompt={prompt},angle={angle}"
        response = service(input_str)

        # 結果の整形表示
        print("\n===== 📡 スキャン結果 =====")
        print(f"🔧 モード    : {mode}")
        print(f"🧠 特徴     : {prompt if prompt else 'なし（listモード）'}")
        print(f"🔄 角度     : {angle}°")
        print("--------------------------")

        count, angle_list, text = parse_response(response.output)
        print(f"👥 人数     : {count}")
        print(f"📐 角度一覧 : {angle_list if angle_list else '該当なし'}")
        print(f"📐 テキスト : {text if text else '該当なし'}")
        print("==========================\n")

        return count, angle_list, text

    except rospy.ServiceException as e:
        rospy.logerr(f"サービス呼び出し失敗: {e}")
        return -1, []

# rospy.loginfo("ノードが起動しました")
def input_com():
    # ###以下ランダム生成の場合のやつ###
    # cmd_gen = CommandGenerator(
    #     person_names,
    #     location_names,
    #     placement_location_names,
    #     room_names,
    #     object_names,
    #     object_categories_plural,
    #     object_categories_singular
    # )
    # # cmd_gen.generate_command_start()
    # input_text = cmd_gen.generate_command_start()#

    ###QRのやつここに統合して。###
    #ここかいたら上のマークコメントアウトしてよし。
    bc.rotateAngle(360,0,0.6)
    navi("operator")
    # tts_pub2("If you need help, scan the QR code.")
    tts_ser2("If you need help, scan the QR code.")


    """detect_qr_code サービスを呼び出し、結果を表示"""
    # rospy.init_node('qr_code_reader_client', anonymous=True)
    
    rospy.wait_for_service('detect_qr_code')
    rospy.loginfo("検出開始🎥")
    while 1:
        try:
            detect_qr_code = rospy.ServiceProxy('detect_qr_code', SetStr)
            response = detect_qr_code(SetStrRequest())
            

            # rospy.loginfo("QRコード検出結果: {}".format(response.result))
        except:
            rospy.logerr("サービス呼び出し失敗: {}".format(e))
            pass
        if response.result != "NOT_FOUND":
            break
        # from gpsr_ai import saved_live
        # if saved_live != False:
        #     break

    input_text = response.result
    ##########################
    
    tts_pub2(f"Thank you. I will execute {input_text} as instructed.")
    bc.rotateAngle(360,0,0.6)
    rospy.sleep(5)

    input_text = input_text.lower()
    return input_text


'''
やばくない
↑
🟣本番使わなそうだから放置だ。                     1
🔵触るな！！完成だ！！                           14
🟡MAPでたら急いで作れ。ただしほぼ完成だ。           2
⚪デバッグ次第                                  4
🔴できてない！！やばい！！                        1
↓
やばい
'''

def look_person():#🟣
    print(f"目の前の人を見る")
    # 人間の中心座標を取得
    # target_center_x = person_center()
    # # 必要な回転角度を計算
    # rotation_angle = calculate_rotation_angle(target_center_x)
    
    # # 回転角度が小さい場合は回転しない
    # if abs(rotation_angle) < 1.0:  # 1度未満の場合は無視
    #     rospy.loginfo("目標は既に中心にあります")
    #     return
    # bc.rotateAngle(rotation_angle, 0, 0.3)

#####江森派生シリーズ#########################################################################
"""
オリジナル
def find_person():#🔵
    print(f"人を探す")
    tts_pub2(f"Searching for a person.")
    head.publish(20.0)
    count, angle_list, text = call_service("find", "people", 180)
    print("angle_list",angle_list,"これにマイナスかける")
    bc.rotateAngle(angle_list[0] * -1,0,1)
"""
    
def find_person():#🔵
    print(f"人を探す1")
    tts_pub2(f"Searching for a person.")
    head.publish(20.0)
        
    # 試行は最大2回
    for attempt in range(2):
        count, angle_list, text = call_service("find", "people", 180)
        print("angle_list",angle_list,"これにマイナスかける")

        if count > 0:
            bc.rotateAngle(angle_list[0] * -1,0,0.6)
            break  # 成功したら抜ける
        else:
            print(f"Find 再試行します... ({attempt + 1}回目/2回目中)")
    else:
        print("2回失敗したので終了します。")

"""
オリジナル
def find_pose(person):#🔵
    print(f"{person}ポーズの人を見つける")
    tts_pub2(f"Finding a person in the {person} pose.")
    if person == "sitting"or"squatting":
        head.publish(-10.0)
    else:
        head.publish(10.0)
    
    count, angle_list, text = call_service("find", f"{person}pose", 180)
    print("angle_list",angle_list,"これにマイナスかける")
    bc.rotateAngle(-angle_list[0],0,1)
"""
    
def find_pose(person,room):#🔵
    print(f"{person}ポーズの人を見つける2")
    tts_pub2(f"Finding a person in the {person} pose.")
    if person == "sitting"or person == "squatting":
        head.publish(-10.0)
    else:
        head.publish(10.0)
        
        # 試行は最大2回
    for attempt in range(2):
        count, angle_list, text = call_service("find", f"{person}pose", 180)
        print("angle_list", angle_list, "これにマイナスかける")

        if count > 0:
            bc.rotateAngle(-angle_list[0], 0, 0.6)
            break  # 成功したら抜ける
        else:
            print(f"Find 再試行します... ({attempt + 1}回目/2回目中)")
            if room != None:
                navi(room)
    else:
        print("2回失敗したので終了します。")
    
    

def count_pose(person):#🔵
    print(f"{person}ポーズの人を数える3")
    tts_pub2(f"Counting the number of people in the {person} pose.")
    if person == "sitting"or"squatting":
        head.publish(-10.0)
    else:
        head.publish(20.0)
    count, angle_list, text = call_service("count", f"{person}pose", 180)
    print("count:",count,"人")
    return f"{person} is {count}"

"""
オリジナル
def find_color_cloth(color,clothe):#🔵
    print(f"{color}色の{clothe}の服を着ている人を探す")
    tts_pub2(f"Finding a person wearing a {color} {clothe}.")
    head.publish(20.0)
    count, angle_list, text = call_service("find", f"wearing a {color} {clothe}", 180)
    print("angle_list",angle_list,"これにマイナスかける")
    bc.rotateAngle(-1*angle_list[0],0,1)
"""
    
def find_color_cloth(color,clothe):#🔵
    print(f"{color}色の{clothe}の服を着ている人を探す4")
    tts_pub2(f"Finding a person wearing a {color} {clothe}.")
    head.publish(20.0)
    
    # 試行は最大2回
    for attempt in range(2):
        count, angle_list, text = call_service("find", f"wearing a {color} {clothe}", 180)
        print("angle_list",angle_list,"これにマイナスかける")

        if count > 0:
            bc.rotateAngle(-angle_list[0], 0, 0.6)
            break  # 成功したら抜ける
        else:
            print(f"Find 再試行します... ({attempt + 1}回目/2回目中)")
    else:
        print("2回失敗したので終了します。")
        

def count_color_cloth(color,clothe):#🔵
    print(f"{color}色の{clothe}の服を着ている人を数える5")
    tts_pub2(f"Counting the number of people wearing a {color} {clothe}.")
    head.publish(20.0)
    count, angle_list, text = call_service("count", f"wearing a {color} {clothe}", 180)
    print("count:",count,"人")
    return f"wearing a {color} {clothe} is {count}"

from ask_name_new import run_ask_name_with_params
# from ask_name import Ask_name
def find_name(name):#⚪
    print(f"角度を求めて、名前を聞いて{name}の場所を特定する6")
    # navi("living_room")
    head.publish(15.0)
    count, angle_list, text = call_service("list", "people", 180)
    print("angle_list",angle_list,"これにマイナスかける")
    # asker = Ask_name(angle_list=[30, 50, 80, 90], want_name=["Olivia"])
    # result = asker.ask_name()
    # print(result)
    # if result == "FIN":
    #     print("ターゲットを発見しました！")

    # angle_list = [30, 60, 90]
    # angle_list = angle
    want_name = name
    result = run_ask_name_with_params(angle_list, want_name)
    print("名前確認の結果:", result)

# def find_name_dbg(name):#⚪
#     print(f"角度を求めて、名前を聞いて{name}の場所を特定する")
#     # count, angle_list, text = call_service("find", "people", 180)
#     angle_list = [30,60,90]
#     print("angle_list",angle_list,"これにマイナスかける")

#     want_name = "jack"
#     result = run_ask_name_with_params(angle_list, want_name)
#     print("名前確認の結果:", result)
    

#############################################################################################################################
#"name", "shirt color", "age", "height"
from find_name import *
def find_info(person_info):#🔵
    result = {}
    print(f"目の前の人の{person_info}の特徴を取得する7")
    head.publish(20)
    # tts_pub.publish(f"Getting the {person_info} characteristics of the person in front.")
    if person_info == "name":
        print(1)
        response = get_confirmed_name(names)#⚪
        result = response
        print(2)
        print("result",result)
        return (f"his name is {result}")
    
    elif person_info == "shirt color":
        # Original
        # result, a =call_service(mode="single", prompt="What color shirt is this person wearing?")
        
        # emori edit
        count, angle_list, text = call_service(mode="single", prompt="You must guess what color shirt this person is wearing — just say a color even if you re not sure.🔹 Example; I think it s blue.")
        print("result",result)
        return f"{text}"
        
    elif person_info == "age":

        # clip_pub.publish("age")
        # rospy.sleep(5)
        # with open(self.yaml_path, 'r') as file:
        #     data = yaml.safe_load(file)
        # print(data)
        # Original
        # result =call_service(mode="single", prompt="Estimate this person height in centimeters.")
        # saved_info = "20"
        
        # emori edit
        count, angle_list, text = call_service(mode="single", prompt="just guess this persons age based on their appearance accuracy doesnt matter just give a two digit number no matter what")
        print("result",result)
        return f"{text}"
        # return　data
    
    elif person_info == "height":
        # Original
        # result =call_service(mode="single", prompt="How old does this person appear to be?")
        # saved_info = "170"
        
        #emori edit
        count, angle_list, text = call_service(mode="single", prompt="just guess this persons height in centimeters based on their appearance accuracy doesnt matter just give a three digit number no matter what")
        print("result",result)
        return f"{text}"
        
    #print("R1",result)
    

    #print(3)
    
    #return result
    # rospy.sleep(3)

###物体認識シリーズ###########################################################################################################
# from obj_count_mod import obj_count_mod

from happymimi_msgs.srv import Str2Str

def call_shelf_feature_service(prompt):
    rospy.wait_for_service('/shelf_object_feature')  # サービスが起動するのを待つ
    try:
        service_client = rospy.ServiceProxy('/shelf_object_feature', Str2Str)
        response = service_client(prompt)  # サービス呼び出し
        return response.output
    except rospy.ServiceException as e:
        rospy.logerr(f"サービス呼び出しに失敗しました: {e}")
        return "エラー: サービス呼び出し失敗"
    
def count_object(obj):#⚪
    print(f"{obj}の数を数える")
    head.publish(-20.0)
    # count = obj_count(obj).result
    print("これからAPI通信")
    prompt = f"Among the visible object in front of you, how many are similar to a {obj}? For example: There are 3 cups."
    result = call_shelf_feature_service(prompt)
    print("OpenAIの返答:", result)
    
    

    return result

# def fo_mod(obj):
#     initialize_publishers()
#     result = look_at_target_object(obj)
#     print(result.success, result.message)
#     return result

# room_items = {
#     "bedroom": ["table", "shelf", "counter", "desk"],
#     "office": ["table", "shelf", "counter", "desk"],
#     "living room": ["shelf"],
#     "kitchen": ["table", "counter"]
# }
from find_obj import *

def find_object(obj, now_room):#🟡
    print(f"{now_room} の家具を調べて「{obj}」を探します...8")

    

    room_items = {
        "bedroom": [],
        "dining room": ["desk"],
        "study room": ["shelf"],
        "living room": ["table", "counter","tall table"]
    }


    furniture_list = room_items.get(now_room, [])

    if not furniture_list:
        rospy.logwarn(f"⚠️ 部屋名が不明: {now_room}")
        return

    # initialize_publishers()#これいる？

    for furniture in furniture_list:
        rospy.loginfo(f"👀 {furniture} で {obj} を探します...9")
        bc.rotateAngle(180,0,0.6)

        if furniture == "desk":
            head.publish(-10)
            navi("dining_table")
        elif furniture == "counter":
            head.publish(-20)
            navi("counter_c")
        elif furniture == "shelf":
            head.publish(-20)
            navi("st_shelf")
        elif furniture == "table":
            head.publish(-30)
            navi("low_table")
    
        grasp_launch()
        print(f"{obj}を把持します")
        grasp_return = grasp(obj)
        kill_grasp_launch()

        if grasp_return == True:
            rospy.loginfo(f"✅ {furniture} で {obj} を発見！")
            break
        else:
            rospy.logwarn(f"❌ {furniture} に {obj} は見つかりませんでした。")
    return True

        # obj を探す処理。家具の上を注視して obj が見つかるか確認する想定
        # result = look_at_target_object(obj)

        # if result.success:
        #     rospy.loginfo(f"✅ {furniture} で {obj} を発見！")
        #     break
        # else:
        #     rospy.logwarn(f"❌ {furniture} に {obj} は見つかりませんでした。")
            
        

    # obj_find(obj)これなんだっけ

def find_feature(obj_comp,obj):#🔴
    head.publish(-20)
    print(f"{obj_comp}の{obj}を探して特定する10")
    # head.publish(0)
    print("これからAPI通信")
    prompt = f"In front of you, where is the most {obj_comp} {obj}? Example answer: The largest plastic bottle is the second from the right."
    result = call_shelf_feature_service(prompt)
    print("OpenAIの返答:", result)

    return result
    #そのものの方向向いてほしいぜい

###############################################################################################################
# def identify_person(): #未使用
#     print(f"あるひとの身体的特徴を特定する")
#     tts_pub.publish(f"Identifying a person's physical characteristics.")
#     rospy.sleep(3)

# 対話・コミュニケーション
# def ask_name():#未使用
#     print(f"名前を聞く")
#     tts_pub.publish(f"Asking for a name.")
#     rospy.sleep(3)


def greet_selfintro():#🔵
    print(f"挨拶と自己紹介をする11")
    tts_ser2("Hello, nice to meet you. My name is Mimi.")

def give_info(talk):#🔵
    print(f"{talk}を伝える12")

    # if "something about yourself" in talk:
    #     ans = "My name is MIMI. I am a service robot designed to help people and make their lives more comfortable. Nice to meet you!"
    #     tts_ser("My name is MIMI. I am a service robot designed to help people and make their lives more comfortable. Nice to meet you!")
    # elif "what day today is" in talk:#（仮）
    #     ans = "Today is Saturday, March 22nd, 2025."
    #     tts_ser("Today is Saturday, March 22nd, 2025.")
    # elif "what day tomorrow is" in talk:#（仮）
    #     ans = "Tomorrow will be Sunday, March 23rd, 2025."
    #     tts_ser("Tomorrow will be Sunday, March 23rd, 2025.")
    # elif "where RoboCup is held this year" in talk:
    #     ans = "RoboCup is being held in Brazil this year."
    #     tts_ser("RoboCup is being held in Brazil this year.")
    # elif "what the result of 3 plus 5 is" in talk:
    #     ans = "Three plus five is eight."
    #     tts_ser("Three plus five is eight.")
    # elif "your team's name" in talk:
    #     ans = "Our team’s name is KIT Happy Robot from Kanazawa Institute of Technology."
    #     tts_ser("Our team’s name is KIT Happy Robot from Kanazawa Institute of Technology.")
    # elif "where you come from" in talk:
    #     ans = "I am from Nonoichi City, Ishikawa Prefecture."
    #     tts_ser("I am from Nonoichi City, Ishikawa Prefecture.")
    # elif "what the weather is like today" in talk:#（仮）
    #     ans = "Today's weather is sunny with a high of 18 degrees Celsius."
    #     tts_ser("Today's weather is sunny with a high of 18 degrees Celsius.")
    # elif "what the time is" in talk:#（仮）
    #     ans = "The current time is 3:45 PM."
    #     tts_ser("The current time is 3:45 PM.")
    # else:
    #     ans = "I'm sorry, I don't understand the question."
    #     tts_ser("I'm sorry, I don't understand the question.")
    # print(ans)
    # tts_ser(ans)
    # 質問文に応じて、答え(ans)をセットする処理

    if "go to the living room, count how many people are there, and report it to me" in talk:
        ans = "There are three people in the living room."

    elif "go to the dining table, check what objects are on it, and tell me what you found" in talk:
        ans = "I saw a cup on the dining table."

    elif "go to the person in the kitchen, ask them what their favorite food is, and come back to tell me" in talk:
        ans = "They said their favorite food is curry rice."

    elif "go to the person in the living room and tell them what color your body is" in talk:
        ans = "Hello, my body is yellow ."

    elif "move to the person in the living room and tell them your name" in talk:
        ans = "Hi, my name is Happy mimi."

    elif "what do thai people usually ride when catching insects" in talk:
        ans = "An elephant."

    elif "will you marry me" in talk:
        ans = "Oh! I don't want to void your warranty!"

    elif "can i trust you" in talk:
        ans = "Don't worry I just got Turing tested."

    elif "why do robots move in a jerky way" in talk:
        ans = "Because you're holding my joystick."

    elif "did you see my screwdriver" in talk:
        ans = "Please ask KIT Happy Robot, they may know."

    elif "what color is the japanese flag" in talk:
        ans = "The Japanese flag is white and red."

    elif "which room has no walls, no doors, and no windows" in talk:
        ans = "That would be a mushroom."

    elif "how many legs does a chair usually have" in talk:
        ans = "A chair usually has 4 legs."

    elif "what is the largest planet in our solar system" in talk:
        ans = "The largest planet is Jupiter."

    elif "what do bees make" in talk:
        ans = "Bees make honey."

    elif "what is the current world population" in talk:
        ans = "It is about 8 billion."

    elif "what is the most spoken language in the world" in talk:
        ans = "It is English."

    elif "what is the correct spelling of robot" in talk:
        ans = "It's spelled r-o-b-o-t."

    elif "what is the brightest star in the solar system" in talk:
        ans = "It is the Sun."

    elif "what is the probability of getting a total of 7 when rolling two dice" in talk:
        ans = "It is about 16.7%."

    elif "would you like something to drink" in talk:
        ans = "A glass of water would be nice, thank you."

    elif "do you have a favorite color, if i may ask" in talk:
        ans = "i like blue."

    elif "is there a time you need to be heading home today" in talk:
        ans = "i need to leave by 6 pm."

    elif "are there any foods you prefer to avoid" in talk:
        ans = "i'm not a fan of mushrooms."

    elif "is the room temperature comfortable for you" in talk:
        ans = "yes, it's perfect. thank you."

    elif "something about yourself" in talk:
        ans = "my name is mimi. I am a service robot designed to help people and make their lives more comfortable. nice to meet you!"
        # tts_ser("My name is MIMI. I am a service robot designed to help people and make their lives more comfortable. Nice to meet you!")
    elif "what day today is" in talk:#（仮）
        ans = "today is saturday, march 22nd, 2025."
        # tts_ser("Today is Saturday, March 22nd, 2025.")
    elif "what day tomorrow is" in talk:#（仮）
        ans = "Tomorrow will be Sunday, March 23rd, 2025."
        # tts_ser("Tomorrow will be Sunday, March 23rd, 2025.")
    elif "where robocup is held this year" in talk:
        ans = "RoboCup is being held in Brazil this year."
        # tts_ser("RoboCup is being held in Brazil this year.")
    elif "what the result of 3 plus 5 is" in talk:
        ans = "Three plus five is eight."
        # tts_ser("Three plus five is eight.")
    elif "your team's name" in talk:
        ans = "Our teams name is KIT Happy Robot."
        # tts_ser("Our team’s name is KIT Happy Robot .")
    elif "where you come from" in talk:
        ans = "I am from Nonoichi City, Ishikawa Prefecture."
        # tts_ser("I am from Nonoichi City, Ishikawa Prefecture.")
    elif "what the weather is like today" in talk:#（仮）
        ans = "Today's weather is sunny"
        # tts_ser("Today's weather is sunny with a high of 18 degrees Celsius.")
    elif "what the time is" in talk:#（仮）
        ans = "The current time is 3:45 PM."
        # tts_ser("The current time is 3:15 PM.")
    else:
        ans = "I'm sorry, I don't understand the question."
        # tts_ser("I'm sorry, I don't understand the question.")
    
    tts_ser2(ans)


def answer_question():#🔵
    print(f"質問に答える13")
    global talk
    # tts_pub.publish(f"Answering the question.")
    # tts_pub.publish(f"what is the question?")
    tts_pub2(f"what is the question?")
    rospy.sleep(1)
    q_cmd = stt_ser(SetStrRequest()).result
    best_score = 0
    best_match = ""
    for t in talk:
        score = difflib.SequenceMatcher(None, q_cmd, t).ratio()
        if score > best_score:
            best_score = score
            best_match = t

    talk = best_match
    give_info(talk) 

def give_saved_info(saved_info):#🔵
    talk_info = saved_info
    print(f"{talk_info}を伝える14")
    tts_ser2(f" {talk_info}.")

from utils import *
def navigate(rooms):#🟡
    if type(rooms) == list:
        rooms = rooms[0]
    print(f"{rooms}に移動")
    tts_pub2(f"Moving to {rooms}.")
    # if rooms == "bedroom":
    #     room = "bed_room"

    # elif rooms == "living room":
    #     room = "living_room"

    # elif rooms == "dining room":
    #     room = "dining_room"

    # elif rooms == "study room":
    #     room = "study_room"

    # elif rooms == "shelf" or  rooms == "s":#家具
    #     room = "st_shelf"

    # elif rooms == "tall table":#家具
    #     room = "tall_table"
    # elif rooms == "":
    #     room = "cml_start"
    # elif rooms == "":
    #     room = "trash"
    # elif rooms == "counter":#家具
    #     room = "counter_c"
    # elif rooms == "right tray":
    #     room = "counter_b"
    # elif rooms == "":
    #     room = "li_shelf_a"
    # elif rooms == "":
    #     room = "li_shelf_b"
    # elif rooms == "low table":#家具
    #     room = "low_table"
    # elif rooms == "dining table":#家具
    #     room = "dining_table"
    # elif rooms == "table":#家具(仮)
    #     room = "dining_table"
    # elif rooms == "operator":
    #     room = "operator"
    # elif rooms == "exit":
    #     room = "exit"
    # elif rooms == "entrance":
    #     room = "entrance_a"
    # elif rooms == "entrance":
    #     room = "entrance_b"
        

    if rooms == "bedroom":
        room = "bed_room"
    elif rooms == "living room":
        room = "living_room"
    elif rooms == "dining room":
        room = "dining_room"
    elif rooms == "study room":
        room = "study_room"

    elif rooms == "shelf":
        room = "st_shelf"
    elif rooms == "counter":
        room = "counter_c"
    elif rooms == "left tray":
        room = "counter_a"
    elif rooms == "right tray":
        room = "counter_b"
    elif rooms == "pen holder":
        room = "counter_a"
    elif rooms == "container":
        room = "counter_b"
    elif rooms == "left kachaka shelf":
        room = "li_shelf_a"
    elif rooms == "right kachaka shelf":
        room = "li_shelf_b"
    elif rooms == "low table":
        room = "low_table"
    elif rooms == "tall table":
        room = "tall_table"
    elif rooms == "trash bin":
        room = "trash"
    elif rooms == "left chair":
        room = "chair"
    elif rooms == "right chair":
        room = "chair"
    elif rooms == "left kachaka station":
        room = "study room"
    elif rooms == "right kachaka station":
        room = "study room"
    elif rooms == "shelf":
        room = "st_shelf"
    elif rooms == "bed":
        room = "bed"
    elif rooms == "dining table":
        room = "dining room"
    elif rooms == "couch":
        room = "couch"

    elif rooms == "shelf":#p
        room = "study_room"
    elif rooms == "counter":#p
        room = "living room"
    elif rooms == "left tray":#p
        room = "living room"
    elif rooms == "right tray":#p
        room = "living room"
    elif rooms == "left kachaka shelf":#p
        room = "living room"
    elif rooms == "right kachaka shelf":#p
        room = "living room"
    elif rooms == "low table":#p
        room = "living room"
    elif rooms == "tall table":#p
        room = "living room"
    elif rooms == "trash bin":#p
        room = "living room"
    elif rooms == "dining table":#p
        room = "dining room"


        # bc.translateDist(-1, 0.5)

    rospy.sleep(3)
    
    bc.rotateAngle(180,0,0.7)
    navi(room)
    navi(room)
        
    # rooms = "operator"
    print(f"{rooms}に移動")


    # tts_pub.publish(f"Moving to {rooms}.")
    # print(f"{rooms}に移動")
    # navi("living")
    
    # navi(rooms)
    # navi("living")
    # tts_pub.publish(f"Moving to {rooms}.")
    # navi(rooms)
    # print(f"{rooms}に移動")
    # rospy.sleep(3)

def navi_find(rooms):
    if type(rooms) == list:
        rooms = rooms[0]
    print(f"{rooms}に移動15")
    tts_pub2(f"Moving to {rooms}.")

    if rooms == "bedroom":
        room = "bed_room"
    elif rooms == "living room":
        room = "living_room"
    elif rooms == "dining room":
        room = "dining_room"
    elif rooms == "study room":
        room = "study_room"

    elif rooms == "shelf":#p
        room = "study_room"
    elif rooms == "counter":#p
        room = "living room"
    elif rooms == "left tray":#p
        room = "living room"
    elif rooms == "right tray":#p
        room = "living room"
    elif rooms == "pen holder":
        room = "living room"
    elif rooms == "container":
        room = "living room"
    elif rooms == "left kachaka shelf":#p
        room = "living room"
    elif rooms == "right kachaka shelf":#p
        room = "living room"
    elif rooms == "low table":#p
        room = "living room"
    elif rooms == "tall table":#p
        room = "living room"
    elif rooms == "trash bin":#p
        room = "living room"
    elif rooms == "left chair":
        room = "study room"
    elif rooms == "right chair":
        room = "study room"
    elif rooms == "left kachaka station":
        room = "study room"
    elif rooms == "right kachaka station":
        room = "study room"
    elif rooms == "shelf":
        room = "study room"
    elif rooms == "bed":
        room = "bedroom"
    elif rooms == "dining table":#p
        room = "dining room"
    elif rooms == "couch":
        room = "dining room"


    navi(room)
    print(f"{rooms}に移動")


def approach_person():#🔵
    print(f"前にいる人に近づく16")
    # tts_pub.publish(f"Approaching the person in front.")
    rospy.sleep(1)
    response = person_distance()
    rospy.sleep(5)
    print("🍏🍏🍏🍏🍏",response.distance)
    # global dis
    # print(dis)
    print(type(response))
    for i in range(5):
        rospy.sleep(1)
    # distance = response.result
    # return distance

from cml24.srv import PutDownSrv, PutDownSrvResponse
from chaser_setup_node import chaser_setup
import actionlib
import smach
import smach_ros
import time
import roslaunch


from chaser import *
def follow_person(rooms=None):#🔵
    print("ついてく１７")
    #ここについかしてもらいたい
    chaser = SimpleChaser()
    chaser.start_chase()
    rospy.sleep(3)

def guide(rooms):#🔵
    if type(rooms) == list:
        rooms = rooms[0]
    print(f"{rooms}へ案内する16")
    tts_pub2(f"I will guide you to {rooms}.")
    
    if rooms == "bedroom":
        room = "bed_room"

    elif rooms == "study room":
        room = "study_room"

    elif rooms == "dining room":
        room = "dining_room"

    elif rooms == "living room":
        room = "living_room"

    # elif rooms == "living room":@:1
    #     room = "living room"#??????
        # bc.translateDist(-1, 0.5)
    rospy.sleep(1.5)
    bc.rotateAngle(-180,0,0.6)
    tts_ser2("Please follow me.")
    navi(room)
    tts_ser2("You have arrived at your destination.")


from std_srvs.srv import Trigger



# 操作・物体の取り扱い#############################################################
def pick_object(obj):#⚪
    pick_mood = 1
    if pick_mood == 1:
        grasp_launch()
        print(f"{obj}を持つ18")
        tts_pub2(f"Picking up {obj}.")
        try:
            grasp_return = grasp(obj)
        except rospy.ROSInterruptException:
            "⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪⚪"
            pass
        print(grasp_return)
        kill_grasp_launch()
    else:
        tts_pub2(f"Please give me the {obj} in front of me.")
        rospy.sleep(3)
        endeffector_pub.publish(False)


def hand_object():#🔵
    print(f"持っているものを渡す19")
    tts_pub2(f"Handing over what I am holding.")
    rospy.sleep(3)
    arm("give")

from std_msgs.msg import Bool
from happymimi_msgs.srv import StrTrg
from grasping_items.srv import SetJointAngles, SetJointAnglesRequest

def place_object(joint_angles):
    # rospy.init_node('place_object_script')

    # --- 1. アームを指定角度にセット ---
    rospy.wait_for_service('/servo/set_joint_angles')
    print(10)
    try:
        set_angle_srv = rospy.ServiceProxy('/servo/set_joint_angles', SetJointAngles)
        req = SetJointAnglesRequest()
        req.shoulder = joint_angles[0]
        req.elbow = joint_angles[1]
        req.wrist = joint_angles[2]
        set_angle_srv(req)
        rospy.loginfo("🦾 アーム角度を再現")
        rospy.sleep(2.0)
    except rospy.ServiceException as e:
        rospy.logerr(f"❌ アーム設定失敗: {e}")
        return

    # --- 2. ハンドを開いて物を置く ---
    pub_hand = rospy.Publisher('/servo/endeffector', Bool, queue_size=1)
    rospy.sleep(1.0)
    pub_hand.publish(True)  # True = 開く
    rospy.loginfo("👐 ハンドを開いて物を置きました")
    rospy.sleep(2.0)

    # --- 3. carry姿勢に戻す ---
    rospy.wait_for_service('/servo/arm')
    try:
        carry_srv = rospy.ServiceProxy('/servo/arm', StrTrg)
        carry_srv("carry")
        rospy.loginfo("🔄 アームをcarryに戻しました")
    except rospy.ServiceException as e:
        rospy.logerr(f"❌ carryへの復帰失敗: {e}")

def put_object(put_pl):#⚪
    print(f"持っているものを置く20")
    put_mood = 1
    if put_mood == 1:

        try:
            # 例：把持時に記録していた角度（ラジアン）
            if put_pl in ["30",]:
                example_joint_angles = [-60,0,60]#
                place_object(example_joint_angles)
            elif put_pl in ["40"]:
                example_joint_angles = [-40, -40, 80]
                place_object(example_joint_angles)
            elif put_pl in ["50","low table"]:
                example_joint_angles = [-30, -30, 60]#
                place_object(example_joint_angles)
            elif put_pl in ["60","shelf","counter","tall table",]:
                example_joint_angles = [-30, 60, -30]#
                place_object(example_joint_angles)
                bc.translateDist(0.4, 0.3)
            elif put_pl == ["70","dining table",]:

                example_joint_angles = [0, -30, 30]#
                place_object(example_joint_angles)
            else:
                example_joint_angles = [-30, -30, 60]#
                
            print(2)
            
            # bc.translateDist(0.1, 0.3)
            endeffector_pub.publish(False)
            rospy.sleep(3.0)
            endeffector_pub.publish(False)
            print(3)
        except rospy.ROSInterruptException:
            pass

        print(4)
    elif put_mood == 2:
        tts_pub2(f"Please place this object in front of me.")
        rospy.sleep(3)
        endeffector_pub.publish(False)

################################################################################
