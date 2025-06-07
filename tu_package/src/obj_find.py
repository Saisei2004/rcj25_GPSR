import rospy
import json
import roslib
import sys

file_path = roslib.packages.get_pkg_dir('happymimi_teleop') + '/src/'
sys.path.insert(0, file_path)
from base_control import BaseControl
from happymimi_msgs.srv import StrTrg, StrTrgResponse
from happymimi_msgs.srv import SetStr


class RecognitionService:
    def __init__(self):
        rospy.init_node('recognition_service_node')    
        self.yolo_info = rospy.ServiceProxy('/recognition/yolo_info', SetStr)
        
        # サービスサーバーの作成
        self.service = rospy.Service('obj_find', StrTrg, self.look_obj)
        rospy.loginfo("サーバーを起動しました")
        self.bc = BaseControl()
        # カメラの設定
        self.image_width = 640  # 画像の幅（ピクセル）
        self.horizontal_fov = 70  # 水平視野角（度）
    
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
    
    def look_obj(self, req):
        rospy.loginfo(f"リクエストを受け付けました: {req.data}")
        target = req.request
        result = json.loads(self.yolo_info().result)
        max_area = 0
        target_center_x = 0
        
        try:
            for key, value in result.items():
                if key == target:
                    area = value['size_x'] * value['size_y']
                    if area > max_area:
                        max_area = area
                        target_center_x = value['center_x']
            
            rotation_angle = self.calculate_rotation_angle(target_center_x)
            # 回転角度が小さい場合は回転しない
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

