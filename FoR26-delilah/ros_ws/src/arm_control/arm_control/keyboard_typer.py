"""KeyboardTyper node: presses a key when it is told a letter.

Subscribes:
    key           std_msgs/String: one letter out of KEY_POSITIONS, for example "a"
    arm_state     std_msgs/Float64MultiArray: where the arm is now
Publishes:
    arm_commands  std_msgs/Float64MultiArray, 6 values: 5 joint angles (deg) and the gripper (%)

For each letter the fingertip moves to a point above the key, down onto it, and back up.
"""
import numpy as np
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray, String

from arm_control.kinematics import inverse_kinematics

# Where the top of each key is, in the robot's base frame (metres). These values are for the
# SIMULATED keyboard. For a real keyboard, measure your own and replace them.
KEY_POSITIONS = {
    "a": [0.300, 0.070, -0.012],
    "s": [0.300, 0.000, -0.012],
    "d": [0.300, -0.070, -0.012],
}
HOVER_HEIGHT = 0.04   # metres above the key before and after pressing
PRESS_DEPTH = 0.008   # metres below the key's top to aim for when pressing
MOVE_TIME = 1.5       # seconds for each of the three moves
RATE_HZ = 20.0
FINGER_DOWN = [0.0, 0.0, -1.0]
GRIPPER_CLOSED = 0.0


class KeyboardTyper(Node):
    def __init__(self):
        super().__init__("keyboard_typer")
        self.arm_state = None
        self.waypoints = []      # joint-angle targets still to visit, each a list of 6 numbers
        self.start = None        # where the current move started
        self.steps_done = 0
        # TODO 1: create the publisher for "arm_commands" (self.publisher), subscribe to "key" (String,
        # self.on_key) and "arm_state" (Float64MultiArray, self.on_arm_state), and create a timer that
        # calls self.on_timer RATE_HZ times per second.
        self.get_logger().info(f"KeyboardTyper started. Keys: {sorted(KEY_POSITIONS)}")

    def on_arm_state(self, msg):
        self.arm_state = list(msg.data)

    def on_key(self, msg):
        letter = msg.data.strip().lower()
        if letter not in KEY_POSITIONS:
            self.get_logger().warn(f"Unknown key {letter!r}. Known keys: {sorted(KEY_POSITIONS)}")
            return
        if self.waypoints:
            self.get_logger().warn("Still busy with the previous key. Ignored.")
            return
        if self.arm_state is None:
            self.get_logger().warn("No arm_state received yet.")
            return
        # TODO 2: build the plan for this key. Compute three fingertip targets (above the key, pressed,
        # above again), solve inverse kinematics for each, starting each solve from the previous result,
        # and store the three results (5 angles + GRIPPER_CLOSED each) in self.waypoints. Also set
        # self.start to the current arm_state and self.steps_done to 0.

    def on_timer(self):
        if not self.waypoints:
            return
        # TODO 3: publish one command that lies between self.start and self.waypoints[0], so that the
        # move takes MOVE_TIME seconds. When the waypoint is reached, remove it from the list and make
        # it the new self.start.


def main():
    rclpy.init()
    node = KeyboardTyper()
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
