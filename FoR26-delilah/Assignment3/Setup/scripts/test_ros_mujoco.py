import mujoco
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64

# A tiny world: a floor and a ball that starts 1 metre above it.
XML = """
<mujoco>
  <worldbody>
    <light pos="0 0 3"/>
    <geom type="plane" size="2 2 0.1"/>
    <body name="ball" pos="0 0 1">
      <freejoint/>
      <geom type="sphere" size="0.1" rgba="0.8 0.2 0.2 1"/>
    </body>
  </worldbody>
</mujoco>
"""


class BallSimulator(Node):
    def __init__(self):
        super().__init__("ball_simulator")
        self.model = mujoco.MjModel.from_xml_string(XML)
        self.data = mujoco.MjData(self.model)
        self.publisher = self.create_publisher(Float64, "ball_height", 10)
        # Call self.step 10 times per second.
        self.timer = self.create_timer(0.1, self.step)

    def step(self):
        # Drop the ball again every 2 seconds, so the numbers keep changing.
        if self.data.time >= 2.0:
            mujoco.mj_resetData(self.model, self.data)

        # Advance the MuJoCo simulation by 0.1 seconds.
        target_time = self.data.time + 0.1
        while self.data.time < target_time:
            mujoco.mj_step(self.model, self.data)

        # Publish the height of the ball on a ROS topic.
        msg = Float64()
        msg.data = float(self.data.qpos[2])
        self.publisher.publish(msg)
        self.get_logger().info(f"t = {self.data.time:.1f} s, ball height = {msg.data:.3f} m")


def main():
    rclpy.init()
    node = BallSimulator()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
