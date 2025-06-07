#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
gpsr-super7.py の派生

Yoloを自前で建てる前提のモジュールです。
++ Yoloモデルの起動最適化を実施 Lサイズでメモリ800MB使用

multi_person_scan_service.py

3つの機能を統合:
  - Find:   特定の特徴を持つ1人を見つける
  - Count:  複数人の中から特徴に合致する複数人を数える
  - List:   全てのバウンディングボックスの数と角度を返す
  - single: 目の前の人の特徴を教える
  - height: 目の前の人の身長を推測する

入力: 'mode=find,prompt=white shart'
  mode: find, count, list, single
  prompt: OpenAI APIに投げる特徴指定（listモードでは空文字）
  angle: 探索を行う角度（singleモードでは空文字）
  
  rosservice call /multi_person_scan "input: 'mode=find,prompt=white shart,angle=180'"
  rosservice call /multi_person_scan "input: 'mode=count,prompt=white shart,angle=180'"
  rosservice call /multi_person_scan "input: 'mode=list,prompt=white shart,angle=180'"
  
  服の色を聞くやつ　うまくいく
  rosservice call /multi_person_scan "input: 'mode=single,prompt=What color shirt is this person wearing?'"
  
  年齢をきくやつ　うまくいく
  rosservice call /multi_person_scan "input: 'mode=single,prompt=just guess this persons age based on their appearance accuracy doesnt matter just give a two digit number no matter what.'"
  
  身長を聞くやつ　うまく行く
  rosservice call /multi_person_scan "input: 'mode=single,prompt=just guess this persons height in centimeters based on their appearance accuracy doesnt matter just give a three digit number no matter what'"
  
  これはOpenAIを使わずに身長を求めるモード
  rosservice call /multi_person_scan "input: 'mode=height'"

出力: "count=X:list=a,b,c" の形式
  output: "count=4:list=100,130,140,230"
  
  singleモードのみ
  出力: "count=X:list=a,b,c:text=Hello World!" の形式
  output: "count=4:list=100,130,140,230:text=Hello World!"
  
  heightモード
  出力: "count=170:list="  の形式（countに推定身長をcmで入れます）
  

変更点
　・使用モデルをGPT-4o-miniからGPT-4 Turboに変更
　・探索角度の指定に対応
　・mode:single を追加
　・新規追加: mode=height を推定する HeightEstimator クラスを実装
 
 新型のBaseControalに対応　引数は角度、速度の2つです
"""

import rospy
import os
import sys
import cv2
import glob
import base64
import re
from datetime import datetime
from cv_bridge import CvBridge, CvBridgeError
from sensor_msgs.msg import Image
from std_msgs.msg import Float64
from happymimi_msgs.srv import Str2Str, Str2StrResponse
from ultralytics import YOLOWorld
from openai import OpenAI
from simple import SimpleBaseControl

import roslib
file_path = roslib.packages.get_pkg_dir('happymimi_teleop') + '/src/'
sys.path.insert(0, file_path)
from base_control import BaseControl

# OpenAI APIキー（必要に応じて書き換えてください）
OPENAI_API_KEY = ""

def encode_image(path):
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:image/png;base64,{b64}"

def encode_cv_image(cv_image):
    ret, buffer = cv2.imencode('.png', cv_image)
    b64 = base64.b64encode(buffer).decode("utf-8")
    return f"data:image/png;base64,{b64}"

# グローバルYOLOモデル（Person検出用）
YOLO_PERSON_MODEL = None

# グローバルインスタンス（サービス呼び出しごとに再生成しないように）
scanner = None
single_scanner = None
height_estimator = None


# ---------- 共通スキャン処理クラス ----------

class MultiPersonScanner:
    """
    180度（可変angle_deg）見渡して人物のバウンディングボックスを検出し、
    画像を保存する共通処理をまとめたクラス
    """
    def __init__(self):
        self.bridge = CvBridge()
        # self.bc = BaseControl()
        self.bc = SimpleBaseControl()

        # YOLO モデルはグローバルで一度だけロード済み
        if YOLO_PERSON_MODEL is None:
            rospy.logerr("グローバルYOLOモデルが初期化されていません")
            raise RuntimeError("YOLOモデルが未ロード")
        self.model = YOLO_PERSON_MODEL

        rospy.Subscriber('/camera/color/image_raw', Image, self.image_callback)
        
        # 頭部サーボ制御用パブリッシャ
        self.head_pub = rospy.Publisher('/servo/head', Float64, queue_size=1)

        self.image = None
        self.min_width = 100  # 無視する最小幅
        self.half_angle = 0   # スキャン範囲半分のオフセットを保持
        self.save_dir = ""

    def prepare_save_directory(self):
        # 保存ディレクトリ（今回は参照用として作成）
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.save_dir = os.path.expanduser(
            f"~/main_ws/src/arc24/modules/src/person-image/{timestamp}"
        )
        os.makedirs(self.save_dir, exist_ok=True)
        rospy.loginfo(f"画像保存用ディレクトリ {self.save_dir} を作成しました。")

    def image_callback(self, img_msg):
        try:
            self.image = self.bridge.imgmsg_to_cv2(img_msg, "bgr8")
        except CvBridgeError as e:
            rospy.logerr("画像変換に失敗しました: {}".format(e))

    def detect_center_person(self):
        if self.image is None:
            rospy.logwarn("まだ画像を受信していません")
            return None

        try:
            results = self.model(source=self.image, conf=0.4)
        except Exception as e:
            rospy.logerr("YOLOモデルの実行に失敗しました: {}".format(e))
            return None

        boxes = results[0].boxes
        w_img = self.image.shape[1]
        left_bound  = w_img / 3
        right_bound = 2 * w_img / 3

        largest_w = 0
        sel_box = None

        for box in boxes:
            if int(box.cls) == 0:
                cx = int(box.xywh[0][0])
                w  = int(box.xywh[0][2])
                if w > largest_w and w > self.min_width and left_bound <= cx <= right_bound:
                    largest_w = w
                    sel_box   = box

        return sel_box

    def save_person_image(self, box, relative_angle):
        cx, cy, w, h = box.xywh[0]
        x1 = max(int(cx - w/2), 0)
        y1 = max(int(cy - h/2), 0)
        x2 = min(int(cx + w/2), self.image.shape[1])
        y2 = min(int(cy + h/2), self.image.shape[0])

        cropped = self.image[y1:y2, x1:x2]
        now_str  = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        # 実際の相対角度を計算（累積角度から半分のオフセットを引く）
        angle_str = str(int(relative_angle - self.half_angle))
        fname    = f"{now_str}_{angle_str}.png"
        fpath    = os.path.join(self.save_dir, fname)
        cv2.imwrite(fpath, cropped)
        rospy.loginfo(f"人物画像を保存しました: {fpath}")

    def run_scan(self, angle_deg):
        """
        angle_deg: スキャンする全角度（例：180 → −90～+90度）
        左端(start_angle)を向いてから、stepごとに回転しつつ検出・保存
        """

        self.prepare_save_directory()

        scanned = 0
        
        """
        # 1) 頭を上げる（＋20度）
        rospy.loginfo("🎯 heightモード: 頭を上げます")
        while self.head_pub.get_num_connections() == 0 and not rospy.is_shutdown():
            rospy.loginfo("⏳ /servo/head 接続待機中...")
            rospy.sleep(0.1)
        self.head_pub.publish(Float64(20.0))
        rospy.sleep(2.0)
        """

        # スキャン範囲の半分をインスタンス変数に保持
        half_angle  =  angle_deg // 2
        self.half_angle = half_angle
        
        rospy.loginfo(f"Debug : half_angle {half_angle}")

        # スキャンの開始地点（指定角度のマイナス半分）まで左を向く
        self.bc.rotateAngle(half_angle, 0.5)
        rospy.sleep(0.2)

        # スキャンの実行
        while scanned < angle_deg and not rospy.is_shutdown():
            box = self.detect_center_person()
            if box is not None:
                self.save_person_image(box, scanned)
                rospy.loginfo(f"Debug : ＝＝＝＝＝＝＝＝＝＝＝＝＝")
                rospy.loginfo(f"Debug : 人がいたので30度回転します")
                rospy.loginfo(f"Debug : 旋回前の累積角度 {scanned}")
                self.bc.rotateAngle(-32, 0.5)
                rospy.sleep(0.5)
                scanned += 30
                rospy.loginfo(f"Debug : 旋回後の累積角度 {scanned}")
                
                """
                rospy.loginfo(f"Debug : 無応答を予防する")
                self.bc.rotateAngle(1, 0.5)
                rospy.sleep(0.5)
                rospy.loginfo(f"Debug : ＝＝＝＝＝＝＝＝＝＝＝＝＝")
                
                #for i in range(4):
                #   rospy.sleep(0.1)
                """
            
            else:
                rospy.loginfo(f"Debug : ＝＝＝＝＝＝＝＝＝＝＝＝＝")
                rospy.loginfo(f"Debug : 人がいないので20度回転します")
                rospy.loginfo(f"Debug : 旋回前の累積角度 {scanned}")
                self.bc.rotateAngle(-22, 0.5)
                rospy.sleep(0.5)
                scanned += 20
                rospy.loginfo(f"Debug : 旋回後の累積角度 {scanned}")
                
                """
                rospy.loginfo(f"Debug : 無応答を予防する")
                self.bc.rotateAngle(1, 0.5)
                rospy.sleep(0.5)
                rospy.loginfo(f"Debug : ＝＝＝＝＝＝＝＝＝＝＝＝＝")
                
                #for i in range(4):
                #    rospy.sleep(0.1)
                """
                
            rospy.sleep(0.2)
            
        # スキャンの終了地点から元の前方位置に戻る
        rospy.loginfo(f"Debug : 今の角度　　　　　　 {scanned}")
        rospy.loginfo(f"Debug : 半分の角度　　　　　 {half_angle}")
        modoru_angle = scanned - half_angle 
        rospy.loginfo(f"Debug : もとの位置に戻ります {modoru_angle}")
        self.bc.rotateAngle(modoru_angle, 0.5)
        rospy.sleep(0.2)
        
        # 6) 頭を元に戻す（0度）
        rospy.loginfo("🎯 heightモード: 頭を元に戻します")
        self.head_pub.publish(Float64(0.0))
        rospy.sleep(1.0)

# ---------- SinglePersonScannerクラス ----------

# 保存先ディレクトリ: ~/main_ws/src/arc24/modules/src/

class SinglePersonScanner:
    """
    SinglePersonScanner は、旋回操作を行わずに、
    目の前の人物のバウンディングボックスを取得し、
    その画像をOpenAI APIに直接送信して応答を得るクラスです。
    """
    def __init__(self):
        self.bridge = CvBridge()
        # YOLO モデル読み込み

        # グローバルモデルを使い回す
        if YOLO_PERSON_MODEL is None:
            rospy.logerr("グローバルYOLOモデルが初期化されていません")
            raise RuntimeError("YOLOモデルが未ロード")
        self.model = YOLO_PERSON_MODEL
        
        self.bc = SimpleBaseControl()

        # 従来
        """
        try:
            self.model = YOLOWorld("yolov8l-world.pt")
            self.model.set_classes(["Person"])
        except Exception as e:
            rospy.logerr("YOLOモデルのロードに失敗しました: {}".format(e))
            raise
        """


        rospy.Subscriber('/camera/color/image_raw', Image, self.image_callback)

        self.image = None
        self.min_width = 100  # 無視する最小幅

        # 頭部サーボ制御用パブリッシャ
        self.head_pub = rospy.Publisher('/servo/head', Float64, queue_size=1)

        # OpenAI APIクライアントの初期化
        self.client = OpenAI(api_key=OPENAI_API_KEY)

        # 画像を保存するディレクトリのパス名
        self.save_dir = ""
    
    def prepare_save_directory(self):
        # 保存ディレクトリ（今回は参照用として作成）
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.save_dir = os.path.expanduser(
            f"~/main_ws/src/arc24/modules/src/person-image/{timestamp}"
        )
        os.makedirs(self.save_dir, exist_ok=True)
        rospy.loginfo(f"画像保存用ディレクトリ {self.save_dir} を作成しました。")


    def image_callback(self, img_msg):
        try:
            self.image = self.bridge.imgmsg_to_cv2(img_msg, "bgr8")
        except CvBridgeError as e:
            rospy.logerr("画像変換に失敗しました: {}".format(e))

    def detect_center_person(self):
        """
        幅が最も大きいバウンディングボックスを選択し、
        画面内どこにいても反応します。
        """
        if self.image is None:
            rospy.logwarn("まだ画像を受信していません")
            return None

        try:
            results = self.model(source=self.image, conf=0.4)
        except Exception as e:
            rospy.logerr("YOLOモデルの実行に失敗しました: {}".format(e))
            return None

        boxes = results[0].boxes

        largest_w = 0
        sel_box = None

        for box in boxes:
            if int(box.cls) == 0:
                w = int(box.xywh[0][2])
                if w > largest_w and w > self.min_width:
                    largest_w = w
                    sel_box = box

        return sel_box

    def crop_person_image(self, box):
        cx, cy, w, h = box.xywh[0]
        x1 = max(int(cx - w/2), 0)
        y1 = max(int(cy - h/2), 0)
        x2 = min(int(cx + w/2), self.image.shape[1])
        y2 = min(int(cy + h/2), self.image.shape[0])
        cropped = self.image[y1:y2, x1:x2]
        return cropped

    def scan_and_analyze(self, prompt):

        self.prepare_save_directory()

        # 頭を上げる（+30度）
        """
        rospy.loginfo("🎯 singleモード: 頭を上げます")
        while self.head_pub.get_num_connections() == 0 and not rospy.is_shutdown():
            rospy.loginfo("⏳ /servo/head 接続待機中...")
            rospy.sleep(0.1)
        self.head_pub.publish(Float64(20.0))
        rospy.sleep(1.0)
        """
        
        # 台車の回転デバック用DBG
        # self.bc.rotateAngle(720, 0.5)

        # 一定時間待って画像が受信されるのを待機
        timeout = rospy.Time.now() + rospy.Duration(5)
        while self.image is None and rospy.Time.now() < timeout:
            rospy.sleep(0.1)
        if self.image is None:
            rospy.logerr("画像を受信できませんでした。")
            # 頭を元に戻す（0度）
            rospy.loginfo("🎯 singleモード: 頭を元に戻します")
            self.head_pub.publish(Float64(0.0))
            rospy.sleep(1.0)
            return "Error: No image received"

        box = self.detect_center_person()
        if box is None:
            rospy.logwarn("人物が検出できませんでした。")
            # 頭を元に戻す（0度）
            rospy.loginfo("🎯 singleモード: 頭を元に戻します")
            self.head_pub.publish(Float64(0.0))
            rospy.sleep(1.0)
            return "count=0:list="

        # クロップ
        cropped = self.crop_person_image(box)
        # ファイルとして保存
        now_str2 = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        fname = f"{now_str2}.png"
        fpath = os.path.join(self.save_dir, fname)
        cv2.imwrite(fpath, cropped)
        rospy.loginfo(f"人物画像（送信用）を保存しました: {fpath}")
        rospy.loginfo(f"送信するファイル名: {fname}")

        # 画像をエンコードして送信
        encoded_image = encode_image(fpath)
        data = [{"type": "image_url", "image_url": {"url": encoded_image}}]

        try:
            resp = self.client.chat.completions.create(
                model="gpt-4.1",
                messages=[
                    #{"role": "system", "content": ""},
                    {"role": "user", "content": [
                        {"type": "text",
                         "text": f"{prompt}"}
                    ] + data}
                ],
                max_tokens=100
            )
        except Exception as e:
            rospy.logerr(f"OpenAI API call failed: {e}")
            # 頭を元に戻す（0度）
            rospy.loginfo("🎯 singleモード: 頭を元に戻します")
            self.head_pub.publish(Float64(0.0))
            rospy.sleep(1.0)
            return "count=0:list="

        result_text = resp.choices[0].message.content.strip().replace("\n", " ")
        rospy.loginfo(f"[OpenAI Response] {result_text}")

        # 頭を元に戻す（0度）
        rospy.loginfo("🎯 singleモード: 頭を元に戻します")
        self.head_pub.publish(Float64(0.0))
        rospy.sleep(1.0)

        # ファイル名を結果に含めて返却
        return f"count=1:list=:text={result_text}"

        

# ---------- HeightEstimatorクラス ----------
class HeightEstimator:
    """
    HeightEstimator は、旋回やOpenAI APIを使わずに、
    首を上げて頭部を映し、目の前の人物のバウンディングボックス上端の位置から
    おおよその身長を推定するクラスです。
    """
    def __init__(self):
        self.bridge = CvBridge()
        # YOLO モデル読み込み

        # グローバルモデルを使い回す
        if YOLO_PERSON_MODEL is None:
            rospy.logerr("グローバルYOLOモデルが初期化されていません")
            raise RuntimeError("YOLOモデルが未ロード")
        self.model = YOLO_PERSON_MODEL

        # 従来
        """
        try:
            self.model = YOLOWorld("yolov8l-world.pt")
            self.model.set_classes(["Person"])
        except Exception as e:
            rospy.logerr("YOLOモデルのロードに失敗しました: {}".format(e))
            raise
        """

        # 頭部サーボ制御用パブリッシャ
        self.head_pub = rospy.Publisher('/servo/head', Float64, queue_size=1)

        rospy.Subscriber('/camera/color/image_raw', Image, self.image_callback)
        self.image = None

        # 画像を保存するディレクトリのパス名
        self.save_dir = ""

    def image_callback(self, img_msg):
        try:
            self.image = self.bridge.imgmsg_to_cv2(img_msg, "bgr8")
        except CvBridgeError as e:
            rospy.logerr("画像変換に失敗しました: {}".format(e))

    def prepare_save_directory(self):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.save_dir = os.path.expanduser(
            f"~/main_ws/src/arc24/modules/src/person-image/{timestamp}"
        )
        os.makedirs(self.save_dir, exist_ok=True)
        rospy.loginfo(f"画像保存用ディレクトリ {self.save_dir} を作成しました。")

    def estimate_height(self):
        self.prepare_save_directory()

        # 1) 頭を上げる（＋20度）
        rospy.loginfo("🎯 heightモード: 頭を上げます")
        while self.head_pub.get_num_connections() == 0 and not rospy.is_shutdown():
            rospy.loginfo("⏳ /servo/head 接続待機中...")
            rospy.sleep(0.1)
        self.head_pub.publish(Float64(20.0))
        rospy.sleep(2.0)
        
        # デバック用
        #rospy.sleep(10)

        # 2) 画像受信待ち
        timeout = rospy.Time.now() + rospy.Duration(5)
        while self.image is None and rospy.Time.now() < timeout:
            rospy.sleep(0.1)
        if self.image is None:
            rospy.logerr("画像を受信できませんでした。")
            # 元に戻す
            self.head_pub.publish(Float64(0.0))
            return "count=0:list="

        # 3) YOLO 検出
        try:
            results = self.model(source=self.image, conf=0.4)
        except Exception as e:
            rospy.logerr("YOLOモデルの実行に失敗しました: {}".format(e))
            # 元に戻す
            self.head_pub.publish(Float64(0.0))
            return "count=0:list="

        # 4) 中央人物のバウンディングボックス選択
        boxes = results[0].boxes
        w_img = self.image.shape[1]
        left = w_img / 4
        right = 3 * w_img / 4
        largest_w = 0
        sel_box = None
        for box in boxes:
            if int(box.cls) == 0:
                cx = int(box.xywh[0][0])
                w  = int(box.xywh[0][2])
                if w > largest_w and w > 100 and left <= cx <= right:
                    largest_w = w
                    sel_box = box

        if sel_box is None:
            rospy.logwarn("人物が検出できませんでした。")
            # 元に戻す
            self.head_pub.publish(Float64(0.0))
            return "count=0:list="

        # 5) バウンディングボックス上端の y 座標から身長推定
        cx, cy, w, h = sel_box.xywh[0]
        top_y = cy - (h / 2)
        img_h = self.image.shape[0]

        if top_y   > (img_h * 12 / 16):
            print("BBOXの位置 12 / 16")
            height_cm = 130
        elif top_y > (img_h * 11 / 16):
            print("BBOXの位置 11 / 16")
            height_cm = 135
        elif top_y > (img_h * 10 / 16):
            print("BBOXの位置 10 / 16")
            height_cm = 140
        elif top_y > (img_h *  9 / 16):
            print("BBOXの位置  9 / 16")
            height_cm = 145
            
        elif top_y > (img_h *  8 / 16):
            print("BBOXの位置  8 / 16")
            height_cm = 150
            
        elif top_y > (img_h *  7 / 16):
            print("BBOXの位置  7 / 16")
            height_cm = 155
        elif top_y > (img_h *  6 / 16):
            print("BBOXの位置  6 / 16")
            height_cm = 160
        elif top_y > (img_h *  5 / 16):
            print("BBOXの位置  5 / 16")
            height_cm = 165
        elif top_y > (img_h *  4 / 16):
            print("BBOXの位置  4 / 16")
            height_cm = 170
        elif top_y > (img_h *  3 / 16):
            print("BBOXの位置  3 / 16")
            height_cm = 175
        elif top_y > (img_h *  2 / 16):
            print("BBOXの位置  2 / 16")
            height_cm = 180
        elif top_y > (img_h *  1 / 16):
            print("BBOXの位置  1 / 16")
            height_cm = 185
        
        else:
            height_cm = 10

        # 6) 頭を元に戻す（0度）
        rospy.loginfo("🎯 heightモード: 頭を元に戻します")
        self.head_pub.publish(Float64(0.0))
        rospy.sleep(1.0)

        #return f"count={height_cm}:list="
    
        return f"count=1:list=:text={height_cm}cm"


# ---------- Find解析クラス ----------

class FindAnalyzer:
    """
    特定の特徴を持つ1人を見つける処理
    """
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

    def extract_index(self, text):
        # 英語序数
        m = re.search(r'(-?\d+)(?:st|nd|rd|th)', text)
        if m:
            return int(m.group(1)) - 1
        # 日本語序数
        m = re.search(r'(-?\d+)\s*番目', text)
        if m:
            return int(m.group(1)) - 1
        # 単なる数字
        m = re.search(r'(-?\d+)', text)
        if m:
            return int(m.group(1)) - 1
        return None

    def analyze(self, prompt, image_dir):
        paths = sorted(glob.glob(os.path.join(image_dir, "*.png")) +
                       glob.glob(os.path.join(image_dir, "*.PNG")))
        if not paths:
            return "count=0:list="

        data = [{"type": "image_url", "image_url": {"url": encode_image(p)}} for p in paths[:5]]

        try:
            resp = self.client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You are an assistant who analyzes visual features."},
                    {"role": "user", "content": [
                        {"type": "text",
                         "text": f"Among these images, find the one with '{prompt}'. Reply with only one index, e.g., '3rd' or '3番目'."}
                    ] + data}
                ],
                max_tokens=100
            )
        except Exception as e:
            rospy.logerr(f"OpenAI API call failed: {e}")
            return "count=0:list="

        result_text = resp.choices[0].message.content.strip()
        rospy.loginfo(f"[OpenAI Response] {result_text}")

        idx = self.extract_index(result_text)
        if idx is not None and 0 <= idx < len(paths):
            match = re.search(r'_(-?\d+)\.png$', os.path.basename(paths[idx]))
            angle = match.group(1) if match else ""
            return f"count=1:list={angle}"
        else:
            return "count=0:list="

# ---------- Count解析クラス ----------

class CountAnalyzer:
    """
    複数人の中から特徴に合致する複数人を数える処理
    """
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

    def extract_indexes(self, text):
        indexes = set()
        matches = re.findall(r'(-?\d+)(?:st|nd|rd|th)?|(-?\d+)\s*番目', text)
        for m in matches:
            for grp in m:
                if grp:
                    indexes.add(int(grp) - 1)
        return sorted(indexes)

    def analyze(self, prompt, image_dir):
        paths = sorted(glob.glob(os.path.join(image_dir, "*.png")) +
                       glob.glob(os.path.join(image_dir, "*.PNG")))
        if not paths:
            return "count=0:list="

        data = [{"type": "image_url", "image_url": {"url": encode_image(p)}} for p in paths[:5]]

        try:
            resp = self.client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You are an assistant who analyzes visual features."},
                    {"role": "user", "content": [
                        {"type": "text",
                         "text": (
                             f"以下の画像には複数人写っています。\n"
                             f"その中で「{prompt}」という特徴に合致する人が写っている画像すべてを教えてください。\n"
                             f"該当する画像の番号（例：1番目, 3番目）をカンマ区切りで答えてください。\n"
                             f"それ以外の返答は不要です。"
                         )}
                    ] + data}
                ],
                max_tokens=150
            )
        except Exception as e:
            rospy.logerr(f"OpenAI API call failed: {e}")
            return "count=0:list="

        result_text = resp.choices[0].message.content.strip()
        rospy.loginfo(f"[OpenAI Response] {result_text}")

        idxs = self.extract_indexes(result_text)
        angles = []
        for i in idxs:
            if 0 <= i < len(paths):
                m = re.search(r'_(-?\d+)\.png$', os.path.basename(paths[i]))
                if m:
                    angles.append(m.group(1))
        if angles:
            return f"count={len(angles)}:list={','.join(angles)}"
        else:
            return "count=0:list="

# ---------- List解析クラス ----------

class ListAnalyzer:
    """
    すべてのバウンディングボックスの数と角度を返す処理
    """
    def analyze(self, prompt, image_dir):
        paths = sorted(glob.glob(os.path.join(image_dir, "*.png")) +
                       glob.glob(os.path.join(image_dir, "*.PNG")))
        if not paths:
            return "count=0:list="

        angles = set()
        for p in paths:
            m = re.search(r'_(-?\d+)\.png$', os.path.basename(p))
            if m:
                angles.add(int(m.group(1)))

        sorted_angles = sorted(angles)
        angle_str = ",".join(str(a) for a in sorted_angles)
        count = len(sorted_angles)
        return f"count={count}:list={angle_str}"

# ---------- サービス定義 ----------
# ---------- サービス定義 ----------

def handle_service(req):
    # 入力文字列から mode, prompt, angle を抽出
    input_str = req.input.strip()
    m_mode   = re.search(r'mode=(\w+)', input_str)
    m_prompt = re.search(r'prompt=([^,]*)', input_str)
    m_angle  = re.search(r'angle=(\d+)', input_str)

    mode   = m_mode.group(1) if m_mode else ""
    prompt = m_prompt.group(1).strip() if m_prompt else ""
    angle  = int(m_angle.group(1)) if m_angle else 180  # デフォルト180度

    rospy.loginfo(f"========== Service called ==========")
    rospy.loginfo(f"mode   = {mode}")
    rospy.loginfo(f"prompt = {prompt}")
    rospy.loginfo(f"angle  = {angle}")
    rospy.loginfo(f"====================================")

    # グローバル変数
    global scanner, single_scanner, height_estimator

    # カメラサブスクライブのウォームアップ
    start = rospy.Time.now()
    while scanner.image is None and rospy.Time.now() - start < rospy.Duration(1.0):
        rospy.sleep(0.1)
    rospy.loginfo("サービス開始：最初のカメラトピックを検出しました。")

    # サービスハンドラの先頭でグローバル変数を使う宣言をし、再インスタンス化をやめるように書き換え

    try:
            if mode == 'find':
                # もう再生成しない
                scanner.run_scan(angle)
                result = FindAnalyzer(OPENAI_API_KEY).analyze(prompt, scanner.save_dir)

            elif mode == 'count':
                scanner.run_scan(angle)
                result = CountAnalyzer(OPENAI_API_KEY).analyze(prompt, scanner.save_dir)

            elif mode == 'list':
                scanner.run_scan(angle)
                result = ListAnalyzer().analyze(prompt, scanner.save_dir)

            elif mode == 'single':
                result = single_scanner.scan_and_analyze(prompt)

            elif mode == 'height':
                result = height_estimator.estimate_height()

            else:
                result = "Error: Unknown mode"

            return Str2StrResponse(output=result)

    except Exception as e:
            rospy.logerr(f"Error: {e}")
            return Str2StrResponse(output="Error occurred: " + str(e))


# 従来のやつ
"""
    try:
        # モードによる分岐
        if mode == 'find':
            scanner = MultiPersonScanner()
            rospy.sleep(0.5)
            scanner.run_scan(angle)
            analyzer = FindAnalyzer(OPENAI_API_KEY)
            result = analyzer.analyze(prompt, scanner.save_dir)

        elif mode == 'count':
            scanner = MultiPersonScanner()
            rospy.sleep(0.5)
            scanner.run_scan(angle)
            analyzer = CountAnalyzer(OPENAI_API_KEY)
            result = analyzer.analyze(prompt, scanner.save_dir)

        elif mode == 'list':
            scanner = MultiPersonScanner()
            rospy.sleep(0.5)
            scanner.run_scan(angle)
            analyzer = ListAnalyzer()
            result = analyzer.analyze(prompt, scanner.save_dir)

        elif mode == 'single':
            scanner = SinglePersonScanner()
            rospy.sleep(0.5)
            result = scanner.scan_and_analyze(prompt)

        elif mode == 'height':
            estimator = HeightEstimator()
            rospy.sleep(0.5)
            result = estimator.estimate_height()

        else:
            result = "Error: Unknown mode"

        rospy.loginfo(f"======== Service Fin ========")
        return Str2StrResponse(output=result)

    except Exception as e:
        rospy.logerr(f"Error: {e}")
        return Str2StrResponse(output="Error occurred: " + str(e))
"""



def main():
    global scanner, single_scanner, height_estimator, YOLO_PERSON_MODEL

    # 1) ノード初期化
    rospy.init_node('multi_person_scan_service_node')

    # 2) YOLOモデルを一度だけロード
    try:
        YOLO_PERSON_MODEL = YOLOWorld("yolov8l-world.pt")
        YOLO_PERSON_MODEL.set_classes(["Person"])
    except Exception as e:
        rospy.logerr(f"YOLOモデルのロードに失敗しました: {e}")
        sys.exit(1)

    # 3) 各クラスのインスタンスを一度だけ生成
    scanner          = MultiPersonScanner()
    single_scanner   = SinglePersonScanner()
    height_estimator = HeightEstimator()

    # 4) サービス登録
    rospy.Service('/multi_person_scan', Str2Str, handle_service)
    rospy.loginfo("Service /multi_person_scan is ready.")

    # 5) イベントループ開始
    rospy.spin()

if __name__ == '__main__':
    main()

