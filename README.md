# robotics_AI
final project

1) 파일 소개


- "duckie_isaac"에는 인터넷에서 구할 수 있는 duckiebot의 원형인 "duckiebot.urdf"가 포함되어 있다. 이를 불러와서 작업하였다.
- "src/duckie_vision_control"에는 카메라 제어를 위한 파이썬 코드(red_cube_follower.py)가 들어있다.
- "duckiebot.usd"에는 기말 프로젝트를 수행한 duckiebot 파일이 들어 있다.
- "script_node.py"는 LED 제어 부분에서 script node에 적은 script에 대한 코드이다.


2) Ubuntu에서 사용하는 코드 모음


ros 접근

source ~/ros2_ws/install/setup.bash

source /opt/ros/humble/setup.bash

-------------------------------------------------
LED 제어

ros2 topic pub /duckie_led_control std_msgs/msg/String "{data: 'red'}" -1
ros2 topic pub /duckie_led_control std_msgs/msg/String "{data: 'green'}" -1
ros2 topic pub /duckie_led_control std_msgs/msg/String "{data: 'blue'}" -1
ros2 topic pub /duckie_led_control std_msgs/msg/String "{data: 'white'}" -1

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

-------------------------------------------------
