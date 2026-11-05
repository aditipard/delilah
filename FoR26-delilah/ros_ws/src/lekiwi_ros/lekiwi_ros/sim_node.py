"""ROS 2 node that runs the LeKiwi simulator.

Subscribes:
    arm_commands   std_msgs/Float64MultiArray, 6 values: 5 joint angles (deg) and the gripper (%)
    base_commands  std_msgs/Float64MultiArray, 3 values: forward (m/s), left (m/s), turn (deg/s)
    fk_pose        geometry_msgs/PoseStamped: a position in the robot's base frame. The simulator
                   draws a pink ball there, so you can see where your forward kinematics points.
Publishes:
    arm_state      std_msgs/Float64MultiArray, 6 values, same layout as arm_commands
    base_pose      std_msgs/Float64MultiArray, 3 values: x (m), y (m), heading (deg)
    true_fingertip geometry_msgs/PointStamped: where the fingertip really is, in the base frame
    key_pressed    std_msgs/String: the name of a key, each time one is pushed down (keyboard scene)
    camera/image   sensor_msgs/Image (only if the parameter publish_images is true)
Parameters:
    scene           "cubes" (default), "keyboard" or "empty"
    viewer          open the 3-D window (default true; needs a monitor)
    publish_images  publish camera pictures (default false)
    camera          which camera to publish (default "front")
"""
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PointStamped, PoseStamped
from sensor_msgs.msg import Image
from std_msgs.msg import Float64MultiArray, String

from lekiwi_sim import LeKiwiSim

BASE_COMMAND_TIMEOUT = 0.5  # seconds. Like the real robot: no fresh base command, no driving.
IMAGE_EVERY_N_STEPS = 5     # 50 steps per second / 5 = 10 pictures per second


class SimNode(Node):
    def __init__(self):
        super().__init__("sim_node")
        self.declare_parameter("viewer", True)
        self.declare_parameter("publish_images", False)
        self.declare_parameter("camera", "front")
        self.publish_images = self.get_parameter("publish_images").value
        self.camera = self.get_parameter("camera").value

        self.declare_parameter("scene", "cubes")
        self.sim = LeKiwiSim(scene=self.get_parameter("scene").value)
        if self.get_parameter("viewer").value:
            self.sim.open_viewer()
        self.has_viewer = self.sim.viewer_is_open()

        self.create_subscription(Float64MultiArray, "arm_commands", self.on_arm_command, 10)
        self.create_subscription(Float64MultiArray, "base_commands", self.on_base_command, 10)
        self.arm_state_pub = self.create_publisher(Float64MultiArray, "arm_state", 10)
        self.base_pose_pub = self.create_publisher(Float64MultiArray, "base_pose", 10)
        self.image_pub = self.create_publisher(Image, "camera/image", 10)
        self.create_subscription(PoseStamped, "fk_pose", self.on_fk_pose, 10)
        self.fingertip_pub = self.create_publisher(PointStamped, "true_fingertip", 10)
        self.key_pub = self.create_publisher(String, "key_pressed", 10)
        self.keys_down = set()

        self.last_base_command_time = None
        self.steps = 0
        self.create_timer(self.sim.control_dt, self.on_timer)
        self.get_logger().info("Simulator running. Waiting for arm_commands and base_commands.")

    def on_arm_command(self, msg):
        if len(msg.data) != 6:
            self.get_logger().warn(f"arm_commands needs 6 values, got {len(msg.data)}. Ignored.")
            return
        self.sim.set_command(arm=list(msg.data))

    def on_base_command(self, msg):
        if len(msg.data) != 3:
            self.get_logger().warn(f"base_commands needs 3 values, got {len(msg.data)}. Ignored.")
            return
        self.sim.set_command(base=list(msg.data))
        self.last_base_command_time = self.get_clock().now()

    def on_fk_pose(self, msg):
        p = msg.pose.position
        self.sim.set_marker("fk", self.sim.base_to_world([p.x, p.y, p.z]))

    def on_timer(self):
        if self.has_viewer and not self.sim.viewer_is_open():
            self.get_logger().info("Viewer closed, stopping.")
            raise SystemExit

        # Stop the base if its last command is too old.
        if self.last_base_command_time is not None:
            age = (self.get_clock().now() - self.last_base_command_time).nanoseconds / 1e9
            if age > BASE_COMMAND_TIMEOUT:
                self.sim.set_command(base=[0.0, 0.0, 0.0])
                self.last_base_command_time = None

        self.sim.step()
        self.steps += 1
        state = self.sim.get_state()
        self.arm_state_pub.publish(Float64MultiArray(data=state["arm_position"].tolist()))
        self.base_pose_pub.publish(Float64MultiArray(data=state["base_pose"].tolist()))
        tip = PointStamped()
        tip.header.stamp = self.get_clock().now().to_msg()
        tip.header.frame_id = "base"
        tip.point.x, tip.point.y, tip.point.z = (float(v) for v in state["fingertip_in_base"])
        self.fingertip_pub.publish(tip)
        for name, key in state["keys"].items():
            if key["pressed"] and name not in self.keys_down:
                self.keys_down.add(name)
                self.key_pub.publish(String(data=name))
                self.get_logger().info(f"{name} pressed")
            elif not key["pressed"]:
                self.keys_down.discard(name)

        if self.publish_images and self.steps % IMAGE_EVERY_N_STEPS == 0:
            picture = self.sim.get_image(self.camera)
            msg = Image()
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.header.frame_id = self.camera
            msg.height, msg.width = picture.shape[0], picture.shape[1]
            msg.encoding = "rgb8"
            msg.step = picture.shape[1] * 3
            msg.data = picture.tobytes()
            self.image_pub.publish(msg)


def main():
    rclpy.init()
    node = SimNode()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        node.sim.close()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
