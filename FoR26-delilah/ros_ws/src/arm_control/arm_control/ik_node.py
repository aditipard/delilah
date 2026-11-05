"""InverseKinematics node: turns a wanted fingertip position into joint angles.

Subscribes:
    ik_target     geometry_msgs/PoseStamped: where the fingertip should go, in the robot's base
                  frame. The finger is always made to point straight down.
    arm_state     std_msgs/Float64MultiArray: where the arm is now (the starting point of the solve)
Publishes:
    arm_commands  std_msgs/Float64MultiArray, 6 values: 5 joint angles (deg) and the gripper (%)
Parameters:
    gripper       the gripper value to send along, in percent (default 0.0 = closed)
"""
import rclpy
from geometry_msgs.msg import PoseStamped
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray

from arm_control.kinematics import inverse_kinematics

FINGER_DOWN = [0.0, 0.0, -1.0]
MAX_ERROR = 0.005   # metres. A solution further than this from the target is not sent.


class InverseKinematics(Node):
    def __init__(self):
        super().__init__("inverse_kinematics")
        self.declare_parameter("gripper", 0.0)
        self.arm_state = None
        # TODO 1: create a publisher for Float64MultiArray on "arm_commands" (self.publisher), and
        # subscribe to "ik_target" (PoseStamped, self.on_target) and "arm_state" (Float64MultiArray,
        # self.on_arm_state).
        self.get_logger().info("InverseKinematics started.")

    def on_arm_state(self, msg):
        self.arm_state = list(msg.data)

    def on_target(self, msg):
        if self.arm_state is None:
            self.get_logger().warn("No arm_state received yet, cannot solve.")
            return
        target = [msg.pose.position.x, msg.pose.position.y, msg.pose.position.z]
        # TODO 2: call inverse_kinematics(target, FINGER_DOWN, self.arm_state). If the returned error
        # is larger than MAX_ERROR, warn and return. Otherwise publish the five angles followed by the
        # gripper parameter on arm_commands.


def main():
    rclpy.init()
    node = InverseKinematics()
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
