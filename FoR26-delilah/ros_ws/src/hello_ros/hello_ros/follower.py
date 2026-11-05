"""Exercise 2: a "follower" node that subscribes to two topics.

When it is finished, this node listens to what the leader commands (arm_commands) and to where
the simulated arm really is (arm_state), and once per second prints how far apart they are.

Fill in the three TODOs.
"""
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray


class Follower(Node):
    def __init__(self):
        super().__init__("follower")
        self.command = None   # the latest message from arm_commands (a list of 6 numbers)
        self.state = None     # the latest message from arm_state (a list of 6 numbers)

        # TODO 1: subscribe to the topic "arm_commands" (type Float64MultiArray) so that
        #         self.on_command is called for every message.
        #         Hint: self.create_subscription(message type, topic name, function to call, 10)

        # TODO 2: subscribe to the topic "arm_state" in the same way, calling self.on_state.

        self.create_timer(1.0, self.report)
        self.get_logger().info("Follower started.")

    def on_command(self, msg):
        self.command = list(msg.data)

    def on_state(self, msg):
        self.state = list(msg.data)

    def report(self):
        if self.command is None or self.state is None:
            self.get_logger().info("Waiting for arm_commands and arm_state ...")
            return

        # TODO 3: compute how far shoulder_pan (index 0) is from its command, in degrees, and
        #         print the command, the state and the difference with self.get_logger().info(...).
        #         Hint: an f-string such as f"{value:6.1f}" prints a number with one decimal.


def main():
    rclpy.init()
    node = Follower()
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
