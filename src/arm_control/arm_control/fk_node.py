import rclpy
from geometry_msgs.msg import PoseStamped
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray

from arm_control.kinematics import forward_kinematics


class ForwardKinematics(Node):
    def __init__(self):
        super().__init__("forward_kinematics")

        self.publisher = self.create_publisher(
            PoseStamped, "fk_pose", 10
        )

        self.subscription = self.create_subscription(
            Float64MultiArray, "arm_state", self.on_arm_state, 10
        )
        self.update_count = 0

        self.get_logger().info("ForwardKinematics started.")

    def on_arm_state(self, msg):
        position, direction = forward_kinematics(msg.data)
        self.update_count += 1

        pose = PoseStamped()

        pose.header.stamp = self.get_clock().now().to_msg()
        pose.header.frame_id = "base"

        pose.pose.position.x = float(position[0])
        pose.pose.position.y = float(position[1])
        pose.pose.position.z = float(position[2])

        pose.pose.orientation.w = 1.0

        self.publisher.publish(pose)

        if self.update_count % 10 == 0:
            self.get_logger().info(
                f"FK fingertip in base: x={position[0]:.4f}, "
                f"y={position[1]:.4f}, z={position[2]:.4f} m"
            )


def main():
    rclpy.init()
    node = ForwardKinematics()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
