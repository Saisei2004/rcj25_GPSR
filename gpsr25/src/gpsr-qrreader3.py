# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-

# # gpsr-qrreader2.pyを参考に、戻り値を修正.
# # gpsr-qrmaster.pyを使ってデバックできます.

# import rospy
# import cv2
# import os
# import datetime
# import numpy as np
# from pyzbar.pyzbar import decode
# from sensor_msgs.msg import Image
# from cv_bridge import CvBridge, CvBridgeError
# from happymimi_msgs.srv import SetStr, SetStrResponse  # 文字列を返すサービス型を利用

# class QRCodeReaderNode:
#     def __init__(self):
#         # ROSノードの初期化
#         rospy.init_node('qr_code_reader_node', anonymous=True)
#         self.bridge = CvBridge()
#         self.image = None

#         # カメラ画像の購読
#         rospy.Subscriber('/camera/color/image_raw', Image, self.image_callback)

#         # スクリプトがあるディレクトリに「QR-read-png」フォルダを作成
#         script_dir = os.path.dirname(os.path.abspath(__file__))
#         self.save_dir = os.path.join(script_dir, "QR-read-png")
#         os.makedirs(self.save_dir, exist_ok=True)

#         # サービスサーバのセットアップ
#         rospy.Service("detect_qr_code", SetStr, self.handle_detect_qr_code)

#         rospy.loginfo("--------------------------------")
#         rospy.loginfo("QRコードリーダーノードが起動しました！")
#         rospy.loginfo("サービス名: detect_qr_code")
#         rospy.loginfo("--------------------------------")

#     def image_callback(self, img_msg):
#         """ROSの画像メッセージをOpenCV画像に変換し、self.imageに格納"""
#         try:
#             self.image = self.bridge.imgmsg_to_cv2(img_msg, "bgr8")
#         except CvBridgeError as e:
#             rospy.logerr("画像変換に失敗しました: {}".format(e))

#     def handle_detect_qr_code(self, req):
#         """サービス呼び出し時にQRコードを検出し、結果を返す"""
#         if self.image is None:
#             rospy.logwarn("カメラ画像がまだ取得されていません")
#             rospy.loginfo("--------------------------------")
#             return SetStrResponse(result="CAMERA_ERROR")

#         # QRコードのデコード
#         qr_codes = decode(self.image)
#         if not qr_codes:
#             rospy.loginfo("QRコードが検出されませんでした")
#             rospy.loginfo("--------------------------------")
#             return SetStrResponse(result="NOT_FOUND")

#         # 検出されたQRコードの最初の1件を処理
#         qr = qr_codes[0]
#         try:
#             decoded_text = qr.data.decode("utf-8")
#         except Exception as e:
#             rospy.logerr("QRコードのデコードに失敗しました: {}".format(e))
#             rospy.loginfo("--------------------------------")
#             return SetStrResponse(result="DECODE_ERROR")

#         rospy.loginfo("QRコード検出: {}".format(decoded_text))

#         # QRコードの座標情報を取得し描画
#         points = qr.polygon
#         if points and len(points) == 4:
#             pts = np.array([[p.x, p.y] for p in points], np.int32).reshape((-1, 1, 2))
#             cv2.polylines(self.image, [pts], isClosed=True, color=(0, 255, 0), thickness=3)
#         else:
#             rect = qr.rect
#             rospy.loginfo("QRコード位置: x={}, y={}, w={}, h={}".format(rect.left, rect.top, rect.width, rect.height))

#         # 画像を保存
#         timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
#         image_filename = "QR_{}.png".format(timestamp)
#         image_path = os.path.join(self.save_dir, image_filename)
#         cv2.imwrite(image_path, self.image)
#         rospy.loginfo("読み取りに成功しました。")
#         rospy.loginfo("画像を保存しました: {}".format(image_path))
#         rospy.loginfo("--------------------------------")

#         return SetStrResponse(result=decoded_text)

# if __name__ == '__main__':
#     try:
#         QRCodeReaderNode()
#         rospy.spin()
#     except rospy.ROSInterruptException:
#         pass