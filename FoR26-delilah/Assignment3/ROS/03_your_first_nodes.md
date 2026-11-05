# 3. Your First Nodes

Now you write two nodes yourself.

- A **leader** that publishes arm commands, so that the simulated arm waves.
- A **follower** that subscribes to the commands and to the arm's real position, and reports how well the arm keeps up.

```
 your leader  ──/arm_commands──►  sim_node  ──/arm_state──►  your follower
      │                                                          ▲
      └──────────────────/arm_commands──────────────────────────┘
```

Both files already exist in the package `hello_ros`, with the ROS parts left out and marked `TODO`. You fill them in.

Time needed: about 45 minutes.

## The anatomy of a node

Every Python node in this course has the same skeleton:

```python
import rclpy
from rclpy.node import Node


class MyNode(Node):                       # 1. a class based on Node
    def __init__(self):
        super().__init__("my_node")       # 2. the node's name
        # 3. create publishers, subscriptions and timers here

    # 4. functions that ROS calls when a message arrives or a timer fires


def main():
    rclpy.init()                          # start ROS
    node = MyNode()
    rclpy.spin(node)                      # wait and handle messages and timers, until Ctrl+C
```

`rclpy` is the ROS library for Python. The three building blocks you need:

| Building block | Code | Meaning |
| --- | --- | --- |
| Publisher | `self.pub = self.create_publisher(Type, "topic", 10)` | I will send messages of this type on this topic |
| | `self.pub.publish(msg)` | send one message |
| Subscription | `self.create_subscription(Type, "topic", self.function, 10)` | call `self.function(msg)` for every message on this topic |
| Timer | `self.create_timer(seconds, self.function)` | call `self.function()` every so many seconds |

The `10` is the queue size: how many messages may wait if they arrive faster than they are handled. 10 is the usual value.

Functions that ROS calls for you, such as the ones you pass to a subscription or a timer, are called **callbacks**.

## Exercise 1: the leader

Open `~/FOR26/ros_ws/src/hello_ros/hello_ros/leader.py` in VS Code and read it from top to bottom.

The node already computes an angle that swings between -40 and +40 degrees. Three things are missing:

| TODO | What to write |
| --- | --- |
| 1 | Create a publisher for `Float64MultiArray` on the topic `"arm_commands"`. Keep it in `self.publisher`. |
| 2 | Create a timer that calls `self.on_timer` 20 times per second. |
| 3 | In `on_timer`: create a `Float64MultiArray`, fill `.data` with `[shoulder_pan, 0.0, 0.0, 0.0, 0.0, 50.0]`, and publish it. |

A message is created and filled like this:

```python
msg = Float64MultiArray()
msg.data = [1.0, 2.0, 3.0]
```

### Build and run

After **every** change to a Python file, build again.

Terminal 1, the simulator:

```bash
conda activate ros_mujoco
cd ~/FOR26/ros_ws
colcon build
source install/setup.bash
ros2 run lekiwi_ros sim_node
```

Terminal 2, your leader:

```bash
conda activate ros_mujoco
cd ~/FOR26/ros_ws
source install/setup.bash
ros2 run hello_ros leader
```

### Check your work

Before you fill anything in, the node starts, prints `Leader started.` and does nothing else. That is the expected starting point.

When it is finished:

- In the simulator window the arm swings left and right, once every 4 seconds.
- In a third terminal, `ros2 topic hz /arm_commands` shows about 20:

  ```
  average rate: 20.003
  ```

- `ros2 topic info /arm_commands` shows `Publisher count: 1`.

## Exercise 2: the follower

Open `~/FOR26/ros_ws/src/hello_ros/hello_ros/follower.py`.

The node already stores the latest message of two topics and has a timer that calls `report` once per second. Missing:

| TODO | What to write |
| --- | --- |
| 1 | Subscribe to `"arm_commands"` so that `self.on_command` is called for each message. |
| 2 | Subscribe to `"arm_state"` so that `self.on_state` is called for each message. |
| 3 | In `report`: compute `state - command` for `shoulder_pan` (index 0) and print all three numbers with `self.get_logger().info(...)`. |

`self.get_logger().info("text")` is the ROS way to print. It adds the time and the node's name.

### Build and run

Keep `sim_node` and your leader running. Build again in any terminal (`cd ~/FOR26/ros_ws`, then `colcon build`), and start the follower in a third terminal:

```bash
conda activate ros_mujoco
cd ~/FOR26/ros_ws
source install/setup.bash
ros2 run hello_ros follower
```

### Check your work

Before you fill anything in, it prints `Waiting for arm_commands and arm_state ...` once per second.

When it is finished, the output looks like this:

```
[INFO] [1791554525.466681750] [follower]: Follower started.
[INFO] [1791554526.450713632] [follower]: shoulder_pan: command  -40.0 deg, state  -39.3 deg, difference   0.7 deg
[INFO] [1791554527.450668299] [follower]: shoulder_pan: command    0.1 deg, state   -6.3 deg, difference  -6.4 deg
[INFO] [1791554528.450765071] [follower]: shoulder_pan: command   40.0 deg, state   39.3 deg, difference  -0.7 deg
[INFO] [1791554529.450684524] [follower]: shoulder_pan: command   -0.1 deg, state    6.3 deg, difference   6.4 deg
```

Your numbers will differ, depending on when in the swing each report falls.

## What the numbers tell you

Look at the difference column in the example. At the ends of the swing (command ±40) the arm is almost exactly on target. In the middle (command near 0), where the commanded angle changes fastest, the arm is about 6 degrees **behind**.

This is called **tracking lag**. A motor needs time to follow a moving target, so the faster the target moves, the further the arm trails. A real arm does the same. You measured it with a 15-line node, without touching the simulator's code. That is the point of topics: any node can listen in.

## Try it yourself

1. In `leader.py`, set `PERIOD_S = 1.0`. Build, run, and watch the difference. What happens to the lag, and why?
2. Make the leader also open and close the gripper while it swings.
3. Stop the leader with `Ctrl` + `C` while the follower runs. What does the follower print now, and why does the arm stay where it is?
4. Start a **second** leader in another terminal. What does the arm do? What does `ros2 topic info /arm_commands` say? This is why a topic that commands a robot should have exactly one publisher.
5. Make the follower report all six joints.

## If something went wrong

| What you see | What to do |
| --- | --- |
| Your change has no effect | Run `colcon build` in `~/FOR26/ros_ws` and restart the node. |
| `AttributeError: 'Leader' object has no attribute 'publisher'` | TODO 3 uses `self.publisher`, but TODO 1 did not create it or used a different name. |
| `IndentationError` | Python is strict about the spaces at the start of a line. Your new lines must line up with the comment lines of the TODO. |
| The follower keeps printing `Waiting for ...` | One of the two topics has no messages. Check with `ros2 topic hz /arm_commands` and `ros2 topic hz /arm_state` which one. |

---

Previous: [2. Build and run](02_build_and_run.md) | Next: [4. Teleoperation in simulation](04_teleop_in_sim.md)
