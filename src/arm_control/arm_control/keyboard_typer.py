"""KeyboardTyper node: presses a key when it is told a letter.

Subscribes:
    key           std_msgs/String: a letter or sequence from KEY_POSITIONS, for example "pool"
    arm_state     std_msgs/Float64MultiArray: where the arm is now
Publishes:
    arm_commands  std_msgs/Float64MultiArray, 6 values: 5 joint angles (deg) and the gripper (%)

For each letter the fingertip moves to a point above the key, down onto it, and back up.
"""
import importlib

np = importlib.import_module("numpy")
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray, String

from .kinematics import inverse_kinematics

# Measured key-top positions in the robot base frame.
KEY_POSITIONS = {
    "p": [0.1940, 0.0335, -0.0391],
    "o": [0.1905, 0.0190, -0.0406],
    "l": [0.2216, 0.0256, -0.0388],
}

# NOTE: These are the original positions provided for the sim
# KEY_POSITIONS = {
#     "a": [0.300, 0.070, -0.012],
#     "s": [0.300, 0.000, -0.012],
#     "d": [0.300, -0.070, -0.012],
# }
HOME_POSITION = np.array([0.1700, 0.0224, 0.0108])
HOVER_HEIGHT = 0.005   # metres above the key top
KEY_TRAVEL = 0.008   #  travel of the keyboard key                                                                                             
PRESS_DEPTH = 0.006   # enough travel to cross the simulator's press threshold
MOVE_TIME = 3.0      # seconds from home to the key hover pose
PRESS_TIME = 0.8     # seconds for each constant-rate press/release move
RATE_HZ = 10.0        # match the simulator's 0.02 s control period
FINGER_DOWN = [0.0, 0.0, -1.0] 
GRIPPER_CLOSED = 0.0


class KeyboardTyper(Node):
    def __init__(self):
        super().__init__("keyboard_typer")
        self.arm_state = None
        self.waypoints = []      # joint-angle targets still to visit, each pa list of 6 numbers
        self.waypoint_steps = []
        self.pending_keys = []
        self.start = None        # where the current move started
        self.home = None         # IK solution for HOME_POSITION; every letter returns here
        self.home_error_reported = False
        self.steps_done = 0
        self.publisher = self.create_publisher(
            Float64MultiArray, "arm_commands", 10
        )

        self.create_subscription(
            String, "key", self.on_key, 10
        )

        self.create_subscription(
            Float64MultiArray, "arm_state", self.on_arm_state, 10
        )

        self.create_timer(
            1.0 / RATE_HZ, self.on_timer
        )

        self.get_logger().info(
            f"KeyboardTyper started. Keys: {sorted(KEY_POSITIONS)}"
        )



    def on_arm_state(self, msg):
        self.arm_state = list(msg.data)
        if self.home is None and len(self.arm_state) == 6:
            home_angles, error = inverse_kinematics(
                HOME_POSITION,
                FINGER_DOWN,
                np.asarray(self.arm_state[:5], dtype=float),
                direction_weight=0.0,
                require_direction=False,
            )
            if np.isfinite(error) and error <= 0.005:
                self.home = list(home_angles) + [GRIPPER_CLOSED]
            elif not self.home_error_reported:
                self.get_logger().warn(
                    f"Home position is out of reach (IK error: {error:.4f} m)."
                )
                self.home_error_reported = True

    def on_key(self, msg):
        text = msg.data.strip().lower()
        if not text or any(letter not in KEY_POSITIONS for letter in text):
            self.get_logger().warn(
                f"Unknown key sequence {text!r}. Known keys: {sorted(KEY_POSITIONS)}"
            )
            return
        if self.arm_state is None:
            self.get_logger().warn("No arm_state received yet.")
            return
        if self.home is None:
            self.get_logger().warn("No home arm pose received yet.")
            return

        self.pending_keys.extend(text)
        if not self.waypoints:
            self.start = list(self.arm_state)
            self.plan_next_key()

    def plan_next_key(self):
        if not self.pending_keys:
            return

        letter = self.pending_keys.pop(0)
        key_top = np.asarray(KEY_POSITIONS[letter], dtype=float)
        vertical_offset = np.array([0.0, 0.0, 1.0])
        hover = key_top + HOVER_HEIGHT * vertical_offset
        press = key_top.copy()
        press[2] -= min(PRESS_DEPTH, KEY_TRAVEL)
        current_angles = np.asarray(self.start[:5], dtype=float)
        planned_waypoints = []
        planned_steps = []

        # Each key follows: hover, press, release, then return home.
        targets = (
            [(hover, self.move_steps())]
            + [(press, self.press_steps()), (hover, self.press_steps())]
        )

        for target, steps in targets:
            angles, error = inverse_kinematics(
                target, FINGER_DOWN, current_angles
            )
            if not np.isfinite(error) or error > 0.005:
                self.get_logger().warn(
                    f"Key {letter!r} is out of reach (IK error: {error:.4f} m)"
                )
                self.pending_keys.clear()
                return
            planned_waypoints.append(list(angles) + [GRIPPER_CLOSED])
            planned_steps.append(steps)
            current_angles = angles

        # Return home before planning the next queued letter.
        planned_waypoints.append(list(self.home))
        planned_steps.append(self.move_steps())
        self.waypoints = planned_waypoints
        self.waypoint_steps = planned_steps
        self.steps_done = 0
        self.get_logger().info(f"Movement plan created for key '{letter}'")

    def move_steps(self):
        return max(1, int(MOVE_TIME * RATE_HZ))

    def press_steps(self):
        return max(1, int(PRESS_TIME * RATE_HZ))


    def on_timer(self):
        if not self.waypoints:
            return
        # Number of interpolation steps per movement
        total_steps = self.waypoint_steps[0]

        # Advance one step
        self.steps_done += 1

        # Interpolation factor (0 to 1)
        alpha = min(self.steps_done / total_steps, 1.0)

        # Starting and target joint angles
        start = np.array(self.start, dtype=float)
        target = np.array(self.waypoints[0], dtype=float)

        # Calculate intermediate joint angles
        command = (1.0 - alpha) * start + alpha * target

        # Publish the joint command
        msg = Float64MultiArray()
        msg.data = command.tolist()
        self.publisher.publish(msg)

        # Check whether this movement is complete
        if self.steps_done >= total_steps:

            # Use the completed waypoint as the next starting point
            self.start = self.waypoints.pop(0)
            self.waypoint_steps.pop(0)

            # Reset the step counter
            self.steps_done = 0

            if not self.waypoints:
                if self.pending_keys:
                    self.get_logger().info(
                        "Home reached; starting the next queued key."
                    )
                else:
                    self.get_logger().info("Key press sequence completed at home.")
                self.plan_next_key()




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
