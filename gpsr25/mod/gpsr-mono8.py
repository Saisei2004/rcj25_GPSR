
#!/usr/bin/env python3
# coding: utf-8

"""
もと７　古いやつ！！！

これはバウンディングボックスを取得せず、画面領域全体をOpen AI API に送るモジュールです。

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

# OpenAI APIキーは環境変数から取得することを推奨
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
        rospy.loginfo("\U0001F680 /shelf_object_feature サービス提供中")

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

    def encode_image(self, path):
        """ファイルパスから base64 エンコードされた data URL を生成"""
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
        return f"data:image/png;base64,{b64}"

    def handle_service(self, req):
        """
        入力フォーマット: 任意の文章（プロンプト）
        出力: OpenAIの返答（文字列全文）
        """
        user_prompt = req.input.strip()

        if not user_prompt:
            return Str2StrResponse(output="Error: 入力が空です")

        if self.latest_frame is None:
            rospy.logwarn("まだ画像を受信していません")
            return Str2StrResponse(output="Error: No image received")

        frame = self.latest_frame.copy()
        save_dir = self.prepare_save_directory()
        full_path = os.path.join(save_dir, "full.png")
        cv2.imwrite(full_path, frame)

        images_data = [{
            "type": "image_url",
            "image_url": {"url": self.encode_image(full_path)}
        }]

        system_prompt = "You respond concisely to the user's question."

        try:
            resp = self.client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": [
                        {"type": "text", "text": user_prompt}
                    ] + images_data}
                ],
                max_tokens=100
            )
        except Exception as e:
            rospy.logerr(f"OpenAI API 呼び出し失敗: {e}")
            return Str2StrResponse(output="Error: OpenAI API call failed")

        result = resp.choices[0].message.content.strip()
        rospy.loginfo(f"OpenAI返答: {result}")
        return Str2StrResponse(output=result)

    def run(self):
        rospy.spin()

if __name__ == "__main__":
    node = ShelfObjectFeatureService()
    node.run()
