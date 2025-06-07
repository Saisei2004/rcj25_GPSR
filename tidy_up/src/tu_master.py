#!/usr/bin/env python3
# coding: utf-8

import rospy
import smach
import smach_ros
import subprocess
import math
import random
from geometry_msgs.msg import Twist, PoseWithCovarianceStamped
from std_srvs.srv import Trigger
from happymimi_msgs.srv import StrTrg, StrTrgRequest
from std_msgs.msg import Bool, Float64, String
from happymimi_voice_msgs.srv import piperTTS, piperTTSRequest
from sensor_msgs.msg import LaserScan  # Add this import for Lidar data
from grasping_items.msg import PointArray

from happymimi_navigation.srv import NaviLocation
from grasping_items.srv import GraspItemWithTarget, GraspItemWithTargetRequest
from grasping_items.srv import GetDetectedObjects, SetJointAngles, SetJointAnglesRequest
from grasping_items.srv import CalculateArmAngles
import threading
MAX_ROUNDS = 12
# Add a global dictionary to track visits to each destination
destination_visits = {
    "trash": 0,
    "counter_a": 0,
    "counter_b": 0,
    "li_shelf_a": 0,
    "li_shelf_b": 0,
}

class LidarDistanceFinder:
    def __init__(self):
        self.scan_data = None
        self.scan_lock = threading.Lock()
        self.sub = rospy.Subscriber('/scan', LaserScan, self.scan_callback)
        
    def scan_callback(self, data):
        with self.scan_lock:
            self.scan_data = data
    
    def get_front_distance(self):
        """ロボット前方の障害物までの距離を取得"""
        with self.scan_lock:
            if self.scan_data is None:
                rospy.logwarn("⚠️ Lidarデータがまだ受信されていません")
                return None
                
            # 前方のLidarデータ (0度付近) を使用
            # インデックスの計算: angle = index * angle_increment + angle_min
            center_idx = len(self.scan_data.ranges) // 2
            
            # 前方10度範囲の平均を取る
            angle_range = 10  # ±5度
            samples = int(angle_range / math.degrees(self.scan_data.angle_increment))
            
            start_idx = center_idx - samples // 2
            end_idx = center_idx + samples // 2
            
            # 範囲内の有効な測定値を平均
            valid_ranges = [r for r in self.scan_data.ranges[start_idx:end_idx] 
                          if r > self.scan_data.range_min and r < self.scan_data.range_max]
            
            if not valid_ranges:
                rospy.logwarn("⚠️ 前方に有効な距離データがありません")
                return None
                
            avg_distance = sum(valid_ranges) / len(valid_ranges)
            rospy.loginfo(f"📏 前方障害物までの平均距離: {avg_distance:.2f}m")
            return avg_distance

class SimpleBaseControl:
    def __init__(self):
        self.cmd_vel_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
        self.current_pose = None
        rospy.Subscriber('/amcl_pose', PoseWithCovarianceStamped, self.pose_callback)

    def pose_callback(self, msg):
        self.current_pose = msg.pose.pose

    def rotateAngle(self, angle_deg, angular_speed=0.6):
        """指定した角度だけ回転する（deg単位）"""
        twist = Twist()
        rad = math.radians(angle_deg)
        twist.angular.z = angular_speed if rad > 0 else -angular_speed
        duration = abs(rad / angular_speed)

        rospy.loginfo(f"↻ rotateAngle: {angle_deg}° ({duration:.2f}s, speed: {angular_speed})")
        self.cmd_vel_pub.publish(twist)
        rospy.sleep(duration)
        self.cmd_vel_pub.publish(Twist())
        rospy.sleep(0.5)

    def translateDist(self, distance, linear_speed=0.3):
        """指定した距離だけ直進・後退する（m単位）"""
        twist = Twist()
        twist.linear.x = linear_speed if distance > 0 else -linear_speed
        duration = abs(distance / linear_speed)

        rospy.loginfo(f"⇆ translateDist: {distance}m ({duration:.2f}s, speed: {linear_speed})")
        self.cmd_vel_pub.publish(twist)
        rospy.sleep(duration)
        self.cmd_vel_pub.publish(Twist())
        rospy.sleep(0.5)

    def adjust_position(self, x_adjust=0.0, y_adjust=0.0, angle_adjust=0.0):
        """位置を微調整する関数"""
        if x_adjust != 0.0:
            self.translateDist(x_adjust, linear_speed=0.1)
        
        if angle_adjust != 0.0:
            self.rotateAngle(angle_adjust, angular_speed=0.2)
            
        if y_adjust != 0.0:
            self.rotateAngle(90, angular_speed=0.1)
            self.translateDist(y_adjust, linear_speed=0.1)
            self.rotateAngle(-90, angular_speed=0.1)


class GoToTable1(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=["arrived", "failed"], output_keys=["launch_started"])
        self.move_srv = rospy.ServiceProxy("/navi_location_server", NaviLocation)
        self.arm_srv = rospy.ServiceProxy("/servo/arm", StrTrg)
        self.head_pub = rospy.Publisher("/servo/head", Float64, queue_size=10)
        self.text_to_speech = rospy.ServiceProxy("/piper/tts", piperTTS)
        self.count = 0
        self.base_control = SimpleBaseControl()

    def execute(self, userdata):
        rospy.loginfo("➡ 移動: low_table")
        try:
            rospy.sleep(1.0)
            self.move_srv("low_table")
            rospy.loginfo("✅ low_table に到着")
            self.base_control.translateDist(-0.1, 0.1)
        except rospy.ServiceException as e:
            rospy.logerr(f"❌ ナビゲーション失敗: {e}")
            return "failed"
    

        # launch起動
        subprocess.Popen([
            "gnome-terminal", "--", "bash", "-c",
            "source ~/.bashrc && source ~/main_ws/devel/setup.bash && roslaunch grasping_items grasping_items_tu.launch"
        ])
        userdata.launch_started = True

        rospy.loginfo("⏳ /execute_grasp サービスを待機中...")
        try:
            rospy.wait_for_service("/execute_grasp", timeout=30.0)
            rospy.loginfo("✅ /execute_grasp 起動確認")
        except rospy.ROSException as e:
            rospy.logerr(f"❌ /execute_grasp サービス待機タイムアウト: {e}")

        try:
            self.arm_srv("carry")
            rospy.loginfo("🤖 アームを carry に設定")
        except rospy.ServiceException as e:
            rospy.logerr(f"❌ アーム設定失敗: {e}")

        self.head_pub.publish(-30.0)
        rospy.sleep(5.0)
        

        return "arrived"


class ClassifyItem(smach.State):
    def __init__(self):
        smach.State.__init__(self,
                             outcomes=["found", "retry"],
                             input_keys=["retry_count"],
                             output_keys=["target_name", "target_list", "retry_count"])

        from grasping_items.msg import PointArray
        self.depth_data = {}
        self.depth_received_time = None
        self.depth_data_list = []
        self.base_control = SimpleBaseControl()
        self.text_to_speech = rospy.ServiceProxy("/piper/tts", piperTTS)
        self.collect_srv = rospy.ServiceProxy("/collect_object_depths", Trigger)

        rospy.Subscriber('/detected_object_depths', PointArray, self.depth_callback)

    def depth_callback(self, msg):
        self.depth_data = dict(zip(msg.names, msg.distances))
        self.depth_received_time = rospy.Time.now()
        rospy.loginfo(f"📥 depth_callback: 受信 {self.depth_data}")

    def execute(self, userdata):
        self.text_to_speech("Detecting objects")

        if not hasattr(userdata, "retry_count"):
            userdata.retry_count = 0

        self.depth_received_time = None
        self.depth_data_list = []

        NUM_ATTEMPTS = 3
        for attempt in range(NUM_ATTEMPTS):
            self.depth_data = {}
            self.depth_received_time = None

            try:
                rospy.loginfo(f"📡 [{attempt+1}/{NUM_ATTEMPTS}] /collect_object_depths 呼び出し")
                self.collect_srv()
            except rospy.ServiceException as e:
                rospy.logwarn(f"⚠️ サービス失敗: {e}")
                continue

            timeout = rospy.Duration(3.0)
            wait_start = rospy.Time.now()

            while not rospy.is_shutdown():
                if self.depth_data and self.depth_received_time:
                    if rospy.Time.now() - self.depth_received_time < rospy.Duration(2.0):
                        for name, dist in self.depth_data.items():
                            self.depth_data_list.append((name, dist))
                        break
                if rospy.Time.now() - wait_start > timeout:
                    rospy.logwarn("⏰ データ待機タイムアウト")
                    break
                rospy.sleep(0.1)

            rospy.sleep(0.5)

        if not self.depth_data_list:
            rospy.logwarn("❌ 有効な物体データが取得できませんでした")
            if userdata.retry_count < 3:
                userdata.retry_count += 1
                self.base_control.translateDist(0.1)
                return "retry"
            else:
                userdata.target_name = ""
                userdata.target_list = []
                return "retry"

        from collections import defaultdict
        depth_group = defaultdict(list)
        for name, dist in self.depth_data_list:
            if name.lower() == "bottle":
                rospy.loginfo(f"🚫 bottle は無視します（距離: {dist:.2f}）")
                continue
            depth_group[name].append(dist)

        if not depth_group:
            rospy.logwarn("❌ 有効な物体がすべて無視されたため、再試行します")
            if userdata.retry_count < 3:
                userdata.retry_count += 1
                self.base_control.translateDist(0.1)
                return "retry"
            else:
                userdata.target_name = ""
                userdata.target_list = []
                return "retry"

        avg_depths = {name: sum(dlist)/len(dlist) for name, dlist in depth_group.items()}
        closest_obj = min(avg_depths.items(), key=lambda x: x[1])[0]

        userdata.target_name = closest_obj
        userdata.target_list = list(avg_depths.keys())
        userdata.retry_count = 0

        rospy.loginfo(f"✅ 最終選択物体: {closest_obj}（平均距離: {avg_depths[closest_obj]:.2f} m）")
        return "found"
    
class GraspItem(smach.State):
    def __init__(self):
        smach.State.__init__(self,
                             outcomes=["grasped", "failed_goto_table"],
                             input_keys=["target_name", "launch_started"],
                             output_keys=["joint_angles", "launch_started"])

        self.grasp_srv = rospy.ServiceProxy("/execute_grasp", GraspItemWithTarget)
        self.calc_srv = rospy.ServiceProxy("/calculate_arm_angles", CalculateArmAngles)
        self.base_control = SimpleBaseControl()
        self.text_to_speech = rospy.ServiceProxy("/piper/tts", piperTTS)

    def execute(self, userdata):
        target = userdata.target_name
        rospy.loginfo(f"🦾 把持試行: {target}")
        grasp_success = False
        self.text_to_speech(f"Grasping {target}")

        try:
            res = self.grasp_srv(GraspItemWithTargetRequest(target_object=target))
            if res.success:
                rospy.loginfo(f"✅ 把持成功: {target}")
                grasp_success = True

                angle_res = self.calc_srv()
                userdata.joint_angles = angle_res.joint_angles if angle_res.success else []
        except rospy.ServiceException as e:
            rospy.logerr(f"❌ grasp サービス失敗: {e}")
            grasp_success = False

        if grasp_success:
            rospy.sleep(1.0)
            self.text_to_speech("Grasped")
            self.base_control.rotateAngle(180)
            return "grasped"

        rospy.logerr("❌ 物体把持に失敗しました。")

        if userdata.launch_started:
            try:
                subprocess.Popen(["pkill", "-f", "roslaunch grasping_items grasping_items_tu.launch"])
                userdata.launch_started = False
                rospy.loginfo("🛑 grasping_items.launch を停止")
            except Exception as e:
                rospy.logwarn(f"⚠️ launch 停止失敗: {e}")

        return "failed_goto_table"

class GoToDestination(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=["arrived", "failed"], 
                            input_keys=["launch_started"],
                            output_keys=["launch_started", "destination"])

        self.navi_srv = rospy.ServiceProxy("/navi_location_server", NaviLocation)
        self.base_control = SimpleBaseControl()
        self.text_to_speech = rospy.ServiceProxy("/piper/tts", piperTTS)
        self.lidar = LidarDistanceFinder()
        self.category = "UNKNOWN"
        rospy.Subscriber("/object_category_detailed", String, self.category_callback)
        self.visit_lock = threading.Lock()
        self.counter_index = 0

    def category_callback(self, msg):
        self.category = msg.data.strip().upper()

    def execute(self, userdata):
        global category
        category = self.category
        if category == "FOOD":
            counters = ["counter_a", "counter_b"]
            destination = counters[self.counter_index % len(counters)]  # ★順番に選ぶ
            self.counter_index += 1
        elif category == "KITCHEN":
            destination = "li_shelf_a"
        elif category == "TASK":
            destination = "li_shelf_b"
        else:
            destination = "trash"

        userdata.destination = destination

        rospy.loginfo(f"➡ ナビゲーション開始: {destination}")
        self.text_to_speech("Going to the destination")
        rospy.sleep(1.0)

        try:
            self.navi_srv(destination)
            rospy.sleep(1.0)
            if category == "KITCHEN" or "TASK":
                self.base_control.translateDist(-0.2, 0.2)

            # with self.visit_lock:
            #     visit_count = destination_visits[destination]
            #     destination_visits[destination] += 1

            # safety_margin = 0.1 if visit_count == 0 else 0.2 if visit_count == 1 else 0.3
            # forward_distance = max(0.06, front_distance - safety_margin) if front_distance else 0.15

            # if forward_distance > 0:
            #     self.base_control.translateDist(forward_distance)
            #     rospy.sleep(1.0)

            return "arrived"
        except rospy.ServiceException as e:
            rospy.logerr(f"❌ ナビゲーション失敗: {e}")
            return "failed"

    
class PlaceItem(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=["placed"], 
                            input_keys=["launch_started", "destination"],
                            output_keys=["launch_started"])
        
        self.set_joint_srv = rospy.ServiceProxy("/servo/set_joint_angles", SetJointAngles)
        self.arm_srv = rospy.ServiceProxy("/servo/arm", StrTrg)
        self.endeffector_pub = rospy.Publisher("/servo/endeffector", Bool, queue_size=1)
        self.base_control = SimpleBaseControl()
        self.lidar = LidarDistanceFinder()

        # 角度受け取り
        self.shoulder_angle = None
        self.elbow_angle = None
        self.wrist_angle = None

        rospy.Subscriber("/shoulder_angle", Float64, self.shoulder_callback)
        rospy.Subscriber("/elbow_angle", Float64, self.elbow_callback)
        rospy.Subscriber("/wrist_angle", Float64, self.wrist_callback)

        # 🔁 カテゴリをトピックで購読
        self.category = "UNKNOWN"
        rospy.Subscriber("/object_category_detailed", String, self.category_callback)

    def category_callback(self, msg):
        self.category = msg.data.strip().upper()

    def shoulder_callback(self, msg):
        self.shoulder_angle = msg.data

    def elbow_callback(self, msg):
        self.elbow_angle = msg.data

    def wrist_callback(self, msg):
        self.wrist_angle = msg.data

    def execute(self, userdata):
        rospy.sleep(1.0)
        rospy.loginfo(f"🧾 PlaceItem開始（launch_started: {userdata.launch_started}）")

        # カテゴリによる角度指定
        rospy.loginfo(f"📦 カテゴリ: {category}")
        rospy.sleep(1.0)

        # 角度セット（デフォルト）
        shoulder_angle = 0.0
        elbow_angle = 0.0
        wrist_angle = 0.0

        if category == "FOOD":
            shoulder_angle = -75
            elbow_angle = 55
            wrist_angle = 30
        elif category == "KITCHEN":
            shoulder_angle = -35
            elbow_angle = 90
            wrist_angle = -45
        elif category == "TASK":
            shoulder_angle = -35
            elbow_angle = 90
            wrist_angle = -45
        else:  # UNKNOWNその他
            shoulder_angle = -60
            elbow_angle = 90
            wrist_angle = -45

        rospy.loginfo(f"📐 指定角度: shoulder={shoulder_angle:.2f}, elbow={elbow_angle:.2f}, wrist={wrist_angle:.2f}")

        try:
            req = SetJointAnglesRequest()
            req.shoulder = shoulder_angle
            req.elbow = elbow_angle
            req.wrist = wrist_angle

            self.set_joint_srv(req)
            rospy.sleep(4.0)
            
            if category == "KITCHEN" or "TASK":
                self.base_control.translateDist(0.2, 0.2)
                rospy.sleep(0.5)

            self.endeffector_pub.publish(False)
            rospy.loginfo("👐 ハンドを開きました")
            rospy.sleep(2.0)
        except rospy.ServiceException as e:
            rospy.logerr(f"❌ アーム再現失敗: {e}")

        try:
            self.arm_srv("carry")
            rospy.loginfo("🤖 アームを carry に戻しました")
        except rospy.ServiceException as e:
            rospy.logerr(f"❌ carryポジション戻し失敗: {e}")

        # ★後退処理・回転処理はここで一切しない
        
        if category == "KITCHEN" or "TASK":
            self.base_control.translateDist(-0.2, 0.2)
            rospy.sleep(0.5)
            
        if userdata.launch_started:
            subprocess.Popen(["pkill", "-f", "roslaunch grasping_items grasping_items_tu.launch"])
            rospy.loginfo("🛑 grasping_items.launch を停止しました")
            userdata.launch_started = False
        else:
            rospy.loginfo("ℹ️ launch はすでに停止済み")
            
        self.base_control.rotateAngle(180)

        return "placed"

class ReturnToTable1(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=["back", "failed"])
        self.move_srv = rospy.ServiceProxy("/navi_location_server", NaviLocation)
        self.text_to_speech = rospy.ServiceProxy("/piper/tts", piperTTS)

    def execute(self, userdata):
        try:
            rospy.sleep(1.0)
            self.text_to_speech("Return To Table")
            self.move_srv("low_table")
            rospy.loginfo("✅ low_table に戻った")
            self.text_to_speech("arrived")
            rospy.sleep(1.0)
            return "back"
        except rospy.ServiceException as e:
            rospy.logerr(f"❌ low_table への復帰失敗: {e}")
            return "failed"


if __name__ == "__main__":
    rospy.init_node("item_delivery_master")
    sm = smach.StateMachine(outcomes=["all_done", "aborted"])
    sm.userdata.target_name = ""
    sm.userdata.target_list = []
    sm.userdata.launch_started = False
    sm.userdata.retry_count = 0
    sm.userdata.destination = ""
    sm.userdata.joint_angles = []

    with sm:
        for i in range(MAX_ROUNDS):
            prefix = f"ROUND{i+1}_"

            smach.StateMachine.add(
                f"{prefix}GOTO1", 
                GoToTable1(), 
                transitions={
                    "arrived": f"{prefix}CLASSIFY",
                    "failed": f"{prefix}GOTO1"
                }, 
                remapping={
                    "launch_started": "launch_started"
                }
            )

            smach.StateMachine.add(
                f"{prefix}CLASSIFY", 
                ClassifyItem(), 
                transitions={
                    "found": f"{prefix}GRASP",
                    "retry": f"{prefix}CLASSIFY"
                }, 
                remapping={
                    "target_name": "target_name", 
                    "target_list": "target_list",
                    "retry_count": "retry_count"
                }
            )

            smach.StateMachine.add(
                f"{prefix}GRASP", 
                GraspItem(), 
                transitions={
                    "grasped": f"{prefix}GOTODEST",
                    "failed_goto_table": f"{prefix}GOTO1"
                }, 
                remapping={
                    "target_name": "target_name", 
                    "launch_started": "launch_started",
                    "joint_angles": "joint_angles"
                }
            )

            smach.StateMachine.add(
                f"{prefix}GOTODEST", 
                GoToDestination(), 
                transitions={
                    "arrived": f"{prefix}PLACE",
                    "failed": f"{prefix}GOTODEST"
                }, 
                remapping={
                    "launch_started": "launch_started",
                    "destination": "destination"
                }
            )

            smach.StateMachine.add(
                f"{prefix}PLACE", 
                PlaceItem(), 
                transitions={
                    "placed": f"{prefix}RETURN"
                },
                remapping={
                    "joint_angles": "joint_angles",
                    "launch_started": "launch_started",
                    "destination": "destination"
                }
            )

            next_state = "all_done" if i == MAX_ROUNDS - 1 else f"ROUND{i+2}_GOTO1"
            smach.StateMachine.add(
                f"{prefix}RETURN", 
                ReturnToTable1(), 
                transitions={
                    "back": next_state,
                    "failed": f"{prefix}RETURN"
                }
            )

    # 状態マシンの可視化ツール起動
    sis = smach_ros.IntrospectionServer('item_delivery_smach_viewer', sm, '/ITEM_DELIVERY')
    sis.start()

    try:
        outcome = sm.execute()
    except rospy.ROSInterruptException:
        pass
    finally:
        sis.stop()