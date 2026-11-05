# 4. Teleoperation in Simulation

On the previous page your own leader node made the simulated arm move. Now you replace it with the **real leader arm**: you move the leader by hand and the simulated robot's arm copies it.

```
 leader arm  ──USB──►  leader_node  ──/arm_commands──►  sim_node
 (your hand)                                            (MuJoCo window)
```

Nothing on the simulator side changes. `sim_node` does not know or care who publishes `/arm_commands`. That is the idea from page 1 at work.

Time needed: about 20 minutes.

## Before you start

- The leader arm is wired, powered (5 V) and connected by USB: [Hardware bring-up, page 1](../HW-Bringup/01_wiring.md).
- You know the leader arm's name under `/dev/serial/by-id/`: [Hardware bring-up, page 2](../HW-Bringup/02_check_servos.md).
- The leader arm has a calibration file on this computer: [Hardware bring-up, page 3](../HW-Bringup/03_calibration.md).
- You are sitting **at the lab computer**, because you need to see the simulator window.

Only the leader arm is used on this page. The robot itself can stay switched off.

## Step 1: Start the simulator

Terminal 1:

```bash
conda activate ros_mujoco
cd ~/FOR26/ros_ws
source install/setup.bash
ros2 run lekiwi_ros sim_node
```

## Step 2: Make sure nothing else is commanding the arm

If your `leader` from the previous page is still running, stop it with `Ctrl` + `C`. Then check, in terminal 2:

```bash
conda activate ros_mujoco
cd ~/FOR26/ros_ws
source install/setup.bash
ros2 topic info /arm_commands
```

It must say `Publisher count: 0`.

## Step 3: Start the leader arm node

In terminal 2, with **your own** leader arm's port name:

```bash
ros2 run lekiwi_ros leader_node --ros-args -p port:=/dev/serial/by-id/usb-1a86_USB_Single_Serial_5B8E116010-if00
```

You should see:

```
[INFO] [1791554438.190356219] [leader_node]: Reading the leader arm on /dev/serial/by-id/usb-1a86_USB_Single_Serial_5B8E116010-if00. Move it by hand.
```

In the simulator window, the simulated arm moves to the pose your leader arm is in. If the leader is folded up in its rest position, the simulated arm folds up too.

`leader_node` has three parameters:

| Parameter | Meaning | Default |
| --- | --- | --- |
| `port` | the leader arm's serial port | none, you must give it |
| `leader_id` | the name the leader arm was calibrated under | `leader` |
| `rate_hz` | readings per second | `30.0` |

## Step 4: Move the leader arm

Take the leader arm and move it slowly. The simulated arm follows.

Try each joint on its own and watch which part of the simulated arm moves:

| Move this on the leader | The simulated arm should |
| --- | --- |
| turn the base of the arm left and right | turn left and right |
| raise and lower the upper arm | raise and lower its upper arm |
| bend the elbow | bend its elbow |
| tilt the wrist | tilt its wrist |
| rotate the wrist | rotate its gripper |
| squeeze the handle | close its gripper |

Then try to pick up a cube from the table and put it on a shelf.

## Step 5: Watch the data

Open a third terminal (with the three start lines) and compare what the leader sends with what the simulated arm does:

```bash
ros2 topic echo --once /arm_commands
```

```bash
ros2 topic echo --once /arm_state
```

With the leader arm folded in its rest position, we measured:

```
leader  /arm_commands:  22.7  -101.9   97.8  -98.7  -17.3   0.3
sim     /arm_state:     22.7  -100.5   95.6  -98.9  -17.3   0.3
```

Most values agree. Two do not: `shoulder_lift` (-101.9 commanded, -100.5 reached) and `elbow_flex` (97.8 commanded, 95.6 reached). The simulated joints stop at their limits of -100° and 95° ([the LeKiwi model](../Simulate/02_the_lekiwi_model.md)), and the real leader arm can go slightly further.

Check the rate too:

```bash
ros2 topic hz /arm_commands
```

```
average rate: 29.991
```

Now run **your follower** from the previous page in this terminal:

```bash
ros2 run hello_ros follower
```

It reports the tracking lag of your own hand movements. You wrote it for a different leader, and it works unchanged.

## Step 6: Stop

Press `Ctrl` + `C` in the `leader_node` terminal, then close the simulator window.

When `leader_node` stops, the simulated arm stays in its last pose, because an arm command is a position and is held.

## What you have built

```
 leader arm ─► leader_node ─/arm_commands─► sim_node ─/arm_state─► follower
```

Three nodes, two topics, and three different programs written by three different people (LeRobot's arm driver, the course's simulator, and your follower) working together without knowing each other.

Driving the **real** robot changes only one box: `robot_node` takes the place of `sim_node` and listens to the same `/arm_commands` topic. See [Hardware bring-up, page 4](../HW-Bringup/04_robot_node.md).

## Read the node

Open `~/FOR26/ros_ws/src/lekiwi_ros/lekiwi_ros/leader_node.py`. It is about 60 lines, and it has the same shape as the leader you wrote: a publisher, a timer, and a callback that fills a `Float64MultiArray`. The only difference is where the six numbers come from:

```python
action = self.leader.get_action()
```

`self.leader` is LeRobot's `SO101Leader` object. `get_action()` reads the six servos and returns their angles in degrees (and the gripper in percent), using the calibration file.

## Try it yourself

1. Run `leader_node` with `-p rate_hz:=5.0`. How does the simulated arm's motion change?
2. Write a node that subscribes to `/arm_commands` and publishes on `/base_commands`, so that turning the leader's `shoulder_pan` makes the robot's **base** rotate. (Remember: a base command must be repeated at least every 0.5 s.)
3. Start `sim_node` with `-p publish_images:=true` and run `ros2 topic hz /camera/image`. Then write a node that subscribes to `/camera/image` and prints the picture's width and height.

## If something went wrong

| What you see | What to do |
| --- | --- |
| `RuntimeError: Set the port, for example: ...` | You started `leader_node` without `-p port:=...`. |
| `Could not connect on port '...'` | The port name is wrong, the USB cable is unplugged, or another program is using the board. Check with `ls /dev/serial/by-id/`. |
| The node stops and asks you to press ENTER or to move the arm to the middle of its range | LeRobot found no calibration file that matches the servos. Stop it with `Ctrl` + `C` and do [Hardware bring-up, page 3](../HW-Bringup/03_calibration.md). |
| The simulated arm does not move | Check `ros2 topic hz /arm_commands`. If there are no messages, `leader_node` is not running. If there are, check that both terminals have the same `ROS_DOMAIN_ID`. |
| The simulated arm jitters between two poses | Two nodes publish on `/arm_commands`. Check `ros2 topic info /arm_commands` and stop one. |
| A joint moves the opposite way to the leader | Tell your TA which joint. The simulator's sign for that joint may need correcting for your arm. |
| `Could not read the leader arm this cycle` appears now and then | Harmless. The servo bus occasionally drops one reply and the node skips that reading. If it appears constantly, check the cables. |

---

Previous: [3. Your first nodes](03_your_first_nodes.md) | Next: [5. Launch files](05_launch_files.md)
