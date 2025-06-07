#!/usr/bin/env python
import rospy
from std_msgs.msg import Int32
# ノードを初期化
rospy.init_node('minimal_node', anonymous=True)
rospy.loginfo("ノードが起動しましたaaaaaaa")

# ノードが終了するまで待機
from gpsr_ai import *
# rospy.Subscriber('/random_topic', Int32, callback)


print("↑これ")
# rospy.spin()
# rospy.signal_shutdown()
