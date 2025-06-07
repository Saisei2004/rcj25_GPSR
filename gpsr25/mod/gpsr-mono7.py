#!/usr/bin/env python3
# coding: utf-8

"""
もと８　新しいやつ
これは画面全体を取得し、OpenAI API に画像認識と指示処理を委ねる ROS1 サービスモジュールです。
rosservice call /shelf_object_feature "input: 'What is the most heaviest object?'"
"""
import rospy
import os
import sys
import base64
from datetime import datetime
from cv_bridge import CvBridge, CvBridgeError
from sensor_msgs.msg import Image
import cv2
from openai import OpenAI
from happymimi_msgs.srv import Str2Str, Str2StrResponse

# OpenAI APIキーは環境変数から取得
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

class ShelfObjectFeatureService:
    def __init__(self):
        # ノード初期化
        rospy.init_node('shelf_object_feature_service_node')
        # 画像変換用
        self.bridge = CvBridge()
        self.latest_frame = None

        # OpenAI クライアント
        if not OPENAI_API_KEY:
            rospy.logerr("OpenAI API key is not set in OPENAI_API_KEY")
            sys.exit(1)
        self.client = OpenAI(api_key=OPENAI_API_KEY)

        # カメラ画像購読
        rospy.Subscriber('/camera/color/image_raw', Image, self.image_callback)

        # サービス提供
        self.service = rospy.Service(
            '/shelf_object_feature',
            Str2Str,
            self.handle_service
        )
        rospy.loginfo("/shelf_object_feature サービス提供中 🚀")

    def image_callback(self, msg):
        try:
            self.latest_frame = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        except CvBridgeError as e:
            rospy.logerr(f"画像変換失敗: {e}")

    def prepare_save_directory(self):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        save_dir = os.path.expanduser(
            f"~/main_ws/src/arc24/modules/src/shelf_feature_images/{timestamp}"
        )
        os.makedirs(save_dir, exist_ok=True)
        return save_dir

    def handle_service(self, req):
        user_prompt = req.input.strip()
        if not user_prompt:
            return Str2StrResponse(output="Error: 入力が空です")

        if self.latest_frame is None:
            rospy.logwarn("まだ画像を受信していません")
            return Str2StrResponse(output="Error: No image received")

        # フレームコピー
        frame = self.latest_frame.copy()
        # 保存ディレクトリ作成 & 保存
        save_dir = self.prepare_save_directory()
        raw_path = os.path.join(save_dir, "full.png")
        cv2.imwrite(raw_path, frame)

        # ——— リサイズ＆圧縮(Base64) ———
        # 横幅512px、高さは512に固定（例）
        h, w = frame.shape[:2]
        new_w = 512
        new_h = 512
        small = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)
        success, buf = cv2.imencode('.jpg', small, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        if not success:
            rospy.logerr("画像のエンコードに失敗しました。")
            return Str2StrResponse(output="Error: Image encoding failed")
        img_b64 = base64.b64encode(buf).decode()

        # 既知の物体リスト
        known_objects = [
            "cookies", "tea box", "noodles", "potato chips", "detergent",
            "cup", "lunch box", "dice", "glue gun", "light bulb",
            "caramel corn", "sponge", "phone stand"
        ]

        # プロンプト構築
        prompt = (
            "You are GPT-4o-mini with vision capability.\n"
            "Below is an image encoded in base64 (JPEG, small & compressed):\n"
            f"{img_b64}\n\n"
            "You also have a fixed list of known object names:\n"
            f"{known_objects}\n\n"
            "Step 1: Identify which of the known objects actually appear IN THE IMAGE. "
            "Use only the exact names from the list; do not invent new names.\n"
            "Step 2: Then, based on the user instruction below, select exactly one object from that array, "
            "and respond with the simple sentence: \"The Answer is <object>\". "
            "Do not add any other words or punctuation—only that sentence.\n\n"
            f"Please Answer only One Object Name .\n"
            f"User Instruction: \"{user_prompt}\"\n"
            "Respond now."
        )

        # OpenAI API呼び出し
        try:
            resp = self.client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that can see and understand images."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                max_tokens=300
            )
        
        # 応答の確認
            if not resp.choices or not hasattr(resp.choices[0].message, "content"):
                rospy.logwarn("OpenAI API 応答が空でした")
                return Str2StrResponse(output="The Answer is Right Object")
            
            result = resp.choices[0].message.content.strip()
            rospy.loginfo(f"OpenAI返答: {result}")
            return Str2StrResponse(output=result)
            
        except Exception as e:
            rospy.logerr(f"OpenAI API 呼び出し失敗: {e}")
            return Str2StrResponse(output="Error: OpenAI API call failed")

        """
        result = resp.choices[0].message.content.strip()
        rospy.loginfo(f"OpenAI返答: {result}")
        return Str2StrResponse(output=result)
        """

    def run(self):
        rospy.spin()

if __name__ == "__main__":
    node = ShelfObjectFeatureService()
    node.run()
