"""EEControl: inverse kinematics controller for the LeKiwi robot."""
import numpy as np
from lekiwi_sim.arm_model import JOINT_LIMITS_DEG
import rclpy
from rclpy.node import Node

from geometry_msgs.msg import PoseStamped
from std_msgs.msg import Float64MultiArray

from arm_control.kinematics import inverse_kinematics, forward_kinematics


MAX_ERROR = 0.005
MAX_DIRECTION_ERROR = 5.0


def quaternion_to_direction(q):
    """Convert target orientation to fingertip direction (+X axis)."""

    quaternion = np.array([q.x, q.y, q.z, q.w], dtype=float)

    norm = np.linalg.norm(quaternion)

    if not np.isfinite(norm) or norm < 1e-8:
        raise ValueError("Invalid target quaternion.")

    x, y, z, w = quaternion / norm

    direction = np.array([
        1 - 2 * (y*y + z*z),
        2 * (x*y + z*w),
        2 * (x*z - y*w)
    ])

    return direction


class EEControl(Node):

    def __init__(self):
        super().__init__("ee_control")

        self.declare_parameter("gripper", 0.0)

        self.arm_state = None

        # Publisher: desired robot joint angles
        self.publisher = self.create_publisher(
            Float64MultiArray,
            "arm_commands",
            10
        )

        # Subscriber: desired end-effector position
        self.create_subscription(
            PoseStamped,
            "ik_target",
            self.on_target,
            10
        )

        # Subscriber: current robot joint angles
        self.create_subscription(
            Float64MultiArray,
            "arm_state",
            self.on_arm_state,
            10
        )

        self.get_logger().info("EEControl started.")

    def on_arm_state(self, msg):
        """Store current joint angles."""
        if len(msg.data) >= 6:
            self.arm_state = list(msg.data)

    def on_target(self, msg):
        """Calculate IK and publish desired joint angles."""

        if self.arm_state is None:
            self.get_logger().warn(
                "No arm_state received yet."
            )
            return

        target = [
            msg.pose.position.x,
            msg.pose.position.y,
            msg.pose.position.z
        ]

        # Get desired finger direction from target orientation
        try:
            target_direction = quaternion_to_direction(
                msg.pose.orientation
            )
        except ValueError as exc:
            self.get_logger().warn(str(exc))
            return

        # Calculate inverse kinematics
        angles, error = inverse_kinematics(
            target,
            target_direction,
            self.arm_state[:5]
        )

        # Check position error
        if not np.isfinite(error) or error >= MAX_ERROR:
            self.get_logger().warn(
                f"IK solution rejected. Error: {error:.4f} m"
            )
            return
        # Check finger direction
        _, actual_direction = forward_kinematics(angles)

        direction_error = np.degrees(
            np.arccos(
                np.clip(
                    np.dot(target_direction, actual_direction),
                    -1.0,
                    1.0
                )
            )
        )

        if not np.isfinite(direction_error) or direction_error >= MAX_DIRECTION_ERROR:
            self.get_logger().warn(
                f"IK rejected. Direction error: {direction_error:.2f} degrees"
            )
            return

        # Check joint limits
        limits_ok = np.all(
            np.isfinite(angles)
            & (angles >= JOINT_LIMITS_DEG[:, 0])
            & (angles <= JOINT_LIMITS_DEG[:, 1])
        )

        if not limits_ok:
            self.get_logger().warn(
                "IK rejected. Joint angles outside limits."
            )
            return
        # Get gripper value
        gripper = self.get_parameter(
            "gripper"
        ).value

        # Create joint-angle command
        command = Float64MultiArray()

        command.data = [
            float(angle) for angle in angles
        ] + [float(gripper)]

        # Publish to robot controller
        self.publisher.publish(command)

        self.get_logger().info(
            f"IK solution published. Error: {error:.4f} m"
        )


def main():
    rclpy.init()

    node = EEControl()

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
