#!/usr/bin/env python3
# coding: utf-8

import rospy
from std_msgs.msg import String, Float64
from std_srvs.srv import Trigger
from grasping_items.srv import GraspItemWithTargetResponse

# グローバルなパブリッシャー（setup_pubsで初期化される）
head_angle_publisher = None
target_object_publisher = None

def initialize_publishers():
    """
    パブリッシャーを初期化する関数。
    他のファイルから呼び出して使う。
    """
    global head_angle_publisher, target_object_publisher
    head_angle_publisher = rospy.Publisher('/servo/head', Float64, queue_size=1)
    target_object_publisher = rospy.Publisher('/target_object', String, queue_size=1)

def look_at_target_object(object_name: str) -> GraspItemWithTargetResponse:
    """
    対象物体の方向を向く処理を実行する関数（把持は行わない）

    引数:
        object_name (str): 注視する物体名

    戻り値:
        GraspItemWithTargetResponse: 処理結果（成功 or 失敗メッセージ付き）
    """
    if head_angle_publisher is None or target_object_publisher is None:
        raise RuntimeError("🛑 initialize_publishers() を先に呼んでください")

    object_name = object_name.lower().strip()
    rospy.loginfo(f"🎯 対象物体として '{object_name}' を受信")

    # Step 1: 対象物体をパブリッシュ
    target_object_publisher.publish(object_name)
    rospy.sleep(1.0)

    # Step 2: 頭を -30 度に向ける
    rospy.loginfo("🧠 頭を -20 度に設定中...")
    while head_angle_publisher.get_num_connections() == 0 and not rospy.is_shutdown():
        rospy.loginfo("⏳ /servo/head 接続待機中...")
        rospy.sleep(0.1)
    head_angle_publisher.publish(Float64(-20.0))
    rospy.sleep(2.0)

    # Step 3: /face_object サービスを呼び出して注視する
    try:
        rospy.wait_for_service('/face_object', timeout=5.0)
        face_object_service = rospy.ServiceProxy('/face_object', Trigger)
        response = face_object_service()
        if not response.success:
            return GraspItemWithTargetResponse(success=False, message="face_object 失敗: " + response.message)
    except Exception as e:
        return GraspItemWithTargetResponse(success=False, message=f"face_object エラー: {e}")

    return GraspItemWithTargetResponse(success=True, message="🎉 把持なしで注視動作に成功しました")
