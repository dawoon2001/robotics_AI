import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist

from cv_bridge import CvBridge
import cv2
import numpy as np

from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy


class RedCubeFollower(Node):
    def __init__(self):
        super().__init__('red_cube_follower')

        qos = QoSProfile(
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
            reliability=ReliabilityPolicy.BEST_EFFORT
        )

        self.image_topic = self.declare_parameter('image_topic', '/duckie/camera/image_raw').value
        self.cmd_topic = self.declare_parameter('cmd_topic', '/duckie/cmd_vel').value

        self.sub = self.create_subscription(Image, self.image_topic, self.on_image, qos)
        self.pub = self.create_publisher(Twist, self.cmd_topic, 10)

        self.bridge = CvBridge()

        # ===== 튜닝 파라미터 =====
        self.k_ang = 1.2
        self.max_ang = 1.5            # 최대 각속도
        self.fwd_speed = 0.15         # 기본 전진 속도

        self.center_deadband = 0.12   # 중앙 허용 오차
        self.stop_area = 250000       # (원하면) 너무 가까우면 정지 (중앙일 때만)
        self.min_area = 100000           # 너무 작은 잡음 무시

        # ✅ 큐브가 없어졌을 때도 "계속 직진" 속도
        self.cruise_speed = 0.18      # 원하면 0.15~0.25로 튜닝

        self.debug_every_n = 15
        self._frame_i = 0

        self.get_logger().info(
            f"Subscribed: {self.image_topic}, Publishing: {self.cmd_topic}\n"
            f"Params: center_deadband={self.center_deadband}, stop_area={self.stop_area}, cruise_speed={self.cruise_speed}"
        )

    def on_image(self, msg: Image):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        h, w = frame.shape[:2]

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        lower1 = np.array([0, 120, 80])
        upper1 = np.array([10, 255, 255])
        lower2 = np.array([170, 120, 80])
        upper2 = np.array([180, 255, 255])

        mask1 = cv2.inRange(hsv, lower1, upper1)
        mask2 = cv2.inRange(hsv, lower2, upper2)
        mask = cv2.bitwise_or(mask1, mask2)

        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        twist = Twist()

        # ✅ [핵심] 빨간 큐브가 안 보이면: 계속 직진
        if not contours:
            twist.linear.x = float(self.cruise_speed)
            twist.angular.z = 0.0
            self.pub.publish(twist)
            return

        c = max(contours, key=cv2.contourArea)
        area = float(cv2.contourArea(c))

        # ✅ [핵심] 너무 작으면(노이즈/멀리 있음): 계속 직진
        if area < self.min_area:
            twist.linear.x = float(self.cruise_speed)
            twist.angular.z = 0.0
            self.pub.publish(twist)
            return

        M = cv2.moments(c)
        if M['m00'] > 0:
            cx = float(M['m10'] / M['m00'])
        else:
            x, y, bw, bh = cv2.boundingRect(c)
            cx = float(x + bw / 2.0)

        err = (cx - (w / 2.0)) / (w / 2.0)  # -1 ~ +1

        # deadband 안이면 회전 안함(그냥 전진)
        if abs(err) < self.center_deadband:
            ang = 0.0
        else:
            # ✅ [핵심] 큐브 방향으로 회전
            ang = -self.k_ang * err
            ang = float(np.clip(ang, -self.max_ang, self.max_ang))

        # 기본 전진
        lin = self.fwd_speed

        # (선택) 너무 가까운데 "정면"이면 정지
        if (area >= self.stop_area) and (abs(err) < self.center_deadband):
            lin = 0.0
            ang = 0.0

        twist.linear.x = float(lin)
        twist.angular.z = float(ang)
        self.pub.publish(twist)

        self._frame_i += 1
        if self._frame_i % self.debug_every_n == 0:
            self.get_logger().info(
                f"err={err:+.3f} area={area:.0f} lin={lin:.2f} ang={ang:.2f} (cruise={self.cruise_speed})"
            )


def main():
    rclpy.init()
    node = RedCubeFollower()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
