#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
import time

def main():
    rospy.init_node('delay_node')
    duration = rospy.get_param('~duration', 1.0)  # デフォルト1秒
    rospy.loginfo(f"Delay node sleeping for {duration} seconds...")
    time.sleep(duration)
    rospy.loginfo("Delay node done. Shutting down.")
    rospy.signal_shutdown("Delay complete")

if __name__ == '__main__':
    main()
