import rospy
import roslaunch

launch = None

def chaser_setup(signal):
    global launch
    if signal == "start":
        uuid = roslaunch.rlutil.get_or_generate_uuid(None, False)
        roslaunch.configure_logging(uuid)
        launch = roslaunch.parent.ROSLaunchParent(uuid, ["/home/mimi/main_ws/src/happymimi_apps/chacer24/launch/chacer24.launch"])
        launch.start()
        return 
    
    elif signal == "stop":
        if launch is not None:
            launch.shutdown()
            print("Launch stopped")
        else:
            print("Launch not running")
        return
    
    else:
        print("Error")
        return