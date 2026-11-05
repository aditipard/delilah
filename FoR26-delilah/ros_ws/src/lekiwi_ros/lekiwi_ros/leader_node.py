"""ROS 2 node that reads the SO-101 leader arm and publishes its joint angles.

Publishes:
    arm_commands   std_msgs/Float64MultiArray, 6 values: 5 joint angles (deg) and the gripper (%)
Parameters:
    port       serial port of the leader arm's controller board (required)
    leader_id  the name the leader arm was calibrated under (default "leader")
    rate_hz    how often to read and publish (default 30.0)
"""
import rclpy
from lerobot.teleoperators.so_leader import SO101Leader, SO101LeaderConfig
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray

JOINTS = ("shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll", "gripper")


class LeaderNode(Node):
    def __init__(self):
        super().__init__("leader_node")
        self.declare_parameter("port", "")
        self.declare_parameter("leader_id", "leader")
        self.declare_parameter("rate_hz", 30.0)
        port = self.get_parameter("port").value
        if not port:
            raise RuntimeError("Set the port, for example: --ros-args -p port:=/dev/serial/by-id/usb-...")

        self.leader = SO101Leader(SO101LeaderConfig(port=port, id=self.get_parameter("leader_id").value))
        self.leader.connect()
        self.pub = self.create_publisher(Float64MultiArray, "arm_commands", 10)
        self.create_timer(1.0 / self.get_parameter("rate_hz").value, self.on_timer)
        self.get_logger().info(f"Reading the leader arm on {port}. Move it by hand.")

    def on_timer(self):
        try:
            action = self.leader.get_action()   # {"shoulder_pan.pos": degrees, ..., "gripper.pos": percent}
        except ConnectionError as error:        # the servo bus sometimes drops one reply: skip this cycle
            self.get_logger().warn(f"Could not read the leader arm this cycle: {error}")
            return
        self.pub.publish(Float64MultiArray(data=[float(action[f"{joint}.pos"]) for joint in JOINTS]))


def main():
    rclpy.init()
    node = LeaderNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.leader.disconnect()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
