import rospy
from sensor_msgs.msg import Image
from ultralytics import YOLOWorld
import sys
import roslib
from cv_bridge import CvBridge, CvBridgeError

file_path = roslib.packages.get_pkg_dir('happymimi_teleop') + '/src/'
sys.path.insert(0, file_path)
from base_control import BaseControl
from happymimi_msgs.srv import StrTrg, StrTrgResponse


class RecognitionService:
    def __init__(self):
        rospy.init_node('recognition_service_node')
        try:
            # YOLOモデルのロード
            self.model = YOLOWorld("yolov8l-world.pt")  # YOLOモデルをロード
            # 初期クラスは空に設定　未検証
            self.model.set_classes([])
            # CvBridgeの初期化
            self.bridge = CvBridge()
        except Exception as e:
            rospy.logerr(f"Failed to load YOLO model: {e}")
            rospy.signal_shutdown("Failed to load YOLO model")
            
        
        rospy.Subscriber('/camera/color/image_raw', Image, self.img_listener)
        
        # サービスサーバーの作成
        self.service = rospy.Service('feature_obj_find', StrTrg, self.handle_service)
        rospy.loginfo("サーバーを起動しました")
        
        # 現在の画像を保持する変数
        self.current_image = None
        self.bc = BaseControl()
        self.image_width = 640  # 画像の幅（ピクセル）
        self.horizontal_fov = 70  # 水平視野角（度）
        
    def img_listener(self, img):
        try:
            # 画像データを受け取り、OpenCV形式に変換
            self.current_image = self.bridge.imgmsg_to_cv2(img, "bgr8")  # ROSイメージメッセージをOpenCV画像に変換
        except CvBridgeError as e:
            rospy.logerr(f"Failed to convert image: {e}")
            
    def calculate_rotation_angle(self, target_x):
        # 画像の中心座標
        image_center = self.image_width / 2
        # 中心からのずれ（ピクセル）
        offset = target_x - image_center
        # 1ピクセルあたりの角度（度）
        angle_per_pixel = self.horizontal_fov / self.image_width
        # 必要な回転角度（度）
        rotation_angle = offset * angle_per_pixel
        return rotation_angle
        
    def check_target_point(self, target):
        try:
            # リクエストから受け取ったターゲットを検出クラスとして設定
            self.model.set_classes([target])
            
            if self.current_image is None:
                rospy.logwarn("画像が受信されていません")
                return 0
            
            # YOLOで物体検出を実行
            results = self.model(self.current_image)
            
            # 検出結果がない場合
            if not results:
                rospy.logwarn(f"{target}が検出されませんでした")
                return 0
                
            # 最も信頼度の高い検出結果を選択
            max_confidence = 0.0
            best_x_point = 0
            
            for result in results:
                boxes = result.boxes
                confidences = result.boxes.conf
                
                for i, box in enumerate(boxes):
                    confidence = confidences[i].item()
                    
                    # 信頼度が閾値（0.5）以上の場合のみ処理
                    if confidence > 0.5 and confidence > max_confidence:
                        max_confidence = confidence
                        # バウンディングボックスの中心x座標を計算
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        best_x_point = (x1 + x2) // 2
                        
                        rospy.loginfo(f"検出: {target}, 信頼度: {confidence:.2f}, x座標: {best_x_point}")
            
            # 有効な検出結果がない場合
            if max_confidence == 0.0:
                rospy.logwarn(f"信頼度の高い{target}の検出結果がありません")
                return 0
                
            return best_x_point
                
        except Exception as e:
            rospy.logerr(f"物体検出中にエラーが発生しました: {e}")
            return 0
    
    def handle_service(self, req):
        try:
            # リクエストの処理
            rospy.loginfo(f"リクエストを受け付けました: {req.request}")
            target = req.request
            x_point = self.check_target_point(target)
            rotation_angle = self.calculate_rotation_angle(x_point)
            if abs(rotation_angle) < 1.0:  # 1度未満の場合は無視
                rospy.loginfo("目標は既に中心にあります")
                return StrTrgResponse(result=True)
            self.bc.rotateAngle(rotation_angle, 0, 0.3)
            return StrTrgResponse(result=True)
        except Exception as e:
            rospy.logerr(f"エラーが発生しました: {e}")
            return StrTrgResponse(result=False)

def main():
    try:
        #変数に入れなくても良かったかも
        recognition_service = RecognitionService()
        rospy.spin()
    except rospy.ROSInitException:
        print('Shutting down')  # 初期化エラーが発生した場合、メッセージを出力

if __name__ == '__main__':
    main()

