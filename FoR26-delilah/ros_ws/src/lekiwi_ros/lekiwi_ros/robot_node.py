"""ROS 2 node for the REAL LeKiwi robot. It has the same topics as sim_node, so it can take its place.

Subscribes:
    arm_commands   std_msgs/Float64MultiArray, 6 values: 5 joint angles (deg) and the gripper (%)
    base_commands  std_msgs/Float64MultiArray, 3 values: forward (m/s), left (m/s), turn (deg/s)
Publishes:
    arm_state      std_msgs/Float64MultiArray, 6 values, same layout as arm_commands
Parameters:
    port                 serial port of LeKiwi's controller board (required)
    robot_id             the name LeKiwi was calibrated under (default "lekiwi")
    enable_motors        false (default): only READ the arm, nothing moves.
                         true: switch the motors on and follow the commands.
    max_relative_target  with motors on, the most a joint may move per step, in degrees (default 5.0)
    rate_hz              steps per second (default 10.0)
"""
import rclpy
from lerobot.robots.lekiwi import LeKiwi, LeKiwiConfig
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray

JOINTS = ("shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll", "gripper")
BASE_COMMAND_TIMEOUT = 0.5  # seconds without a fresh base command before the wheels are stopped


class RobotNode(Node):
    def __init__(self):
        super().__init__("robot_node")
        self.declare_parameter("port", "")
        self.declare_parameter("robot_id", "lekiwi")
        self.declare_parameter("enable_motors", False)
        self.declare_parameter("max_relative_target", 5.0)
        self.declare_parameter("rate_hz", 10.0)
        port = self.get_parameter("port").value
        if not port:
            raise RuntimeError("Set the port, for example: --ros-args -p port:=/dev/serial/by-id/usb-...")
        self.motors_on = self.get_parameter("enable_motors").value

        self.robot = LeKiwi(LeKiwiConfig(port=port, id=self.get_parameter("robot_id").value, cameras={},
                                         max_relative_target=self.get_parameter("max_relative_target").value))
        if not self.robot.calibration:
            raise RuntimeError(f"No calibration file at {self.robot.calibration_fpath}. Calibrate the robot first.")
        if self.motors_on:
            self.robot.connect(calibrate=False)   # also switches the motors on: the arm now holds its pose
            if not self.robot.is_calibrated:
                self.robot.disconnect()
                raise RuntimeError("The calibration file does not match the values stored in the motors.")
            self.get_logger().warn("MOTORS ARE ON. The arm follows arm_commands. Keep a hand on the power switch.")
        else:
            self.robot.bus.connect()              # only opens the serial port; the motors stay off
            self.get_logger().info("Read-only: publishing arm_state, motors off. Start with "
                                   "-p enable_motors:=true to drive the robot.")

        # Until a command arrives, the target is the pose the arm is in now, so it does not move.
        self.arm_target = self.read_arm()
        self.base_target = [0.0, 0.0, 0.0]
        self.last_base_command_time = None

        self.create_subscription(Float64MultiArray, "arm_commands", self.on_arm_command, 10)
        self.create_subscription(Float64MultiArray, "base_commands", self.on_base_command, 10)
        self.arm_state_pub = self.create_publisher(Float64MultiArray, "arm_state", 10)
        self.create_timer(1.0 / self.get_parameter("rate_hz").value, self.on_timer)

    def read_arm(self):
        observation = self.robot.get_observation()
        return [float(observation[f"arm_{joint}.pos"]) for joint in JOINTS]

    def on_arm_command(self, msg):
        if len(msg.data) != 6:
            self.get_logger().warn(f"arm_commands needs 6 values, got {len(msg.data)}. Ignored.")
            return
        self.arm_target = list(msg.data)

    def on_base_command(self, msg):
        if len(msg.data) != 3:
            self.get_logger().warn(f"base_commands needs 3 values, got {len(msg.data)}. Ignored.")
            return
        self.base_target = list(msg.data)
        self.last_base_command_time = self.get_clock().now()

    def on_timer(self):
        if self.last_base_command_time is not None:
            age = (self.get_clock().now() - self.last_base_command_time).nanoseconds / 1e9
            if age > BASE_COMMAND_TIMEOUT:
                self.base_target = [0.0, 0.0, 0.0]
                self.last_base_command_time = None
        try:
            if self.motors_on:
                action = {f"arm_{joint}.pos": value for joint, value in zip(JOINTS, self.arm_target)}
                action["x.vel"], action["y.vel"], action["theta.vel"] = self.base_target
                self.robot.send_action(action)
            self.arm_state_pub.publish(Float64MultiArray(data=self.read_arm()))
        except ConnectionError as error:   # the servo bus sometimes drops one reply: skip this step
            self.get_logger().warn(f"Servo bus error, skipping this step: {error}")

    def shutdown(self):
        if self.motors_on:
            self.robot.stop_base()
            self.robot.disconnect()        # switches the motors off: the arm goes limp
        else:
            self.robot.bus.disconnect(False)


def main():
    rclpy.init()
    node = RobotNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.shutdown()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
