# robotics_AI
final project

ros 접근

source ~/ros2_ws/install/setup.bash

source /opt/ros/humble/setup.bash

-------------------------------------------------
LED 제어

ros2 topic pub /duckie_led_control std_msgs/msg/String "{data: 'red'}" -1

-------------------------------------------------
고수준 모터 제어

ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r /cmd_vel:=/duckie/cmd_vel

-------------------------------------------------
저수준 모터 제어

ros2 topic pub -r 10 /duckie/wheel_left_cmd std_msgs/msg/Float64 "{data: 5.0}"

ros2 topic pub -r 10 /duckie/wheel_right_cmd std_msgs/msg/Float64 "{data: 5.0}"

-------------------------------------------------
카메라 통신 확인

ros2 topic info /duckie/camera/image_raw

ros2 topic echo /duckie/camera/image_raw --once

-------------------------------------------------
큐브 감지 로봇 제어

ros2 run duckie_vision_control red_cube_follower
