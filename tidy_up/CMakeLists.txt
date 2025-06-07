cmake_minimum_required(VERSION 3.0.2)
project(tidy_up)

find_package(catkin REQUIRED COMPONENTS
  rospy
  std_msgs
  message_generation
)

## サービスファイルの登録
add_service_files(
  FILES
  ClassifyItem.srv
)

## メッセージ/サービスの生成
generate_messages(
  DEPENDENCIES
  std_msgs
)

catkin_package(
  CATKIN_DEPENDS rospy std_msgs message_runtime
)

include_directories(
  ${catkin_INCLUDE_DIRS}
)

## Pythonスクリプトのインストール先を `src/` に変更
catkin_install_python(PROGRAMS
  src/tu_master.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)
