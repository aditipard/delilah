# 3. Keyboard Typing

Now you combine everything: a node that receives a letter and makes the robot press that key. You also write the launch file that starts your whole system with one command.

## The simulated keyboard

The keyboard scene has a plate with three keys in front of the robot. Each key sits on a spring and goes down when pushed.

| Key | Letter | Top of the key in the base frame (m) |
| --- | --- | --- |
| `key_a` (red) | `a` | (0.300, 0.070, -0.012) |
| `key_s` (green) | `s` | (0.300, 0.000, -0.012) |
| `key_d` (blue) | `d` | (0.300, -0.070, -0.012) |

A key is 2.4 cm wide, travels 6 mm, and counts as pressed when it is 3 mm down. Each time a key goes down, `sim_node` prints a line and publishes the key's name on `/key_pressed`.

The z values are negative because the base frame's origin is above the floor (see [the base frame](README.md#the-base-frame)).

## The motion for one key

Pressing a key is three moves of the fingertip, with the finger pointing down throughout:

| Move | Fingertip target |
| --- | --- |
| 1. hover | 4 cm above the key |
| 2. press | 8 mm **below** the key's top |
| 3. hover | 4 cm above the key again |

Why aim below the top? The key only travels 6 mm, so the fingertip never gets there. Aiming a little too deep makes sure the key goes all the way down even if your kinematics is a few millimetres off. On a real keyboard, be careful with this value.

Each target is turned into joint angles with your `inverse_kinematics`. Start each solve from the result of the one before, so that the three arm poses are close to each other.

Do **not** jump from one pose to the next. Publish many small in-between commands, so that each move takes a set time. You saw this idea on the [pick and place page](../Simulate/04_pick_and_place.md): moving along a straight line in joint space from the start pose to the target.

```
command = start + (target - start) * fraction        with fraction going from 0 to 1
```

## Exercise 1: the node

Open `keyboard_typer.py`. The table `KEY_POSITIONS` and the constants are given. Fill in the three TODOs.

| TODO | What to write |
| --- | --- |
| 1 | The publisher for `"arm_commands"`, the subscriptions to `"key"` (`String`) and `"arm_state"`, and a timer that calls `self.on_timer` `RATE_HZ` times per second. |
| 2 | In `on_key`: compute the three fingertip targets, solve IK for each, and store the three joint-angle targets (5 angles plus `GRIPPER_CLOSED`) in `self.waypoints`. Set `self.start` to the current arm state and `self.steps_done` to 0. If a target is out of reach, warn and do not move. |
| 3 | In `on_timer`: publish one command between `self.start` and `self.waypoints[0]`. When the waypoint is reached, remove it from the list and make it the new `self.start`. |

The node keeps the gripper closed while typing, so that only the fixed finger's tip touches the key.

## Exercise 2: the launch file

Starting four nodes in four terminals gets tiring. A **launch file** starts them all with one command. It is a Python file that returns a list of things to start.

Open `~/FOR26/ros_ws/src/arm_control/launch/typing_sim.launch.py`. It already starts the simulator with the keyboard scene:

```python
Node(package="lekiwi_ros", executable="sim_node", output="screen",
     parameters=[{"scene": "keyboard", ...}]),
```

Each `Node(...)` entry does what `ros2 run package executable` does. `output="screen"` shows the node's messages in the terminal.

Fill in the TODO: add one entry for each of your three nodes.

## Run it

```bash
conda activate ros_mujoco
cd ~/FOR26/ros_ws
colcon build
source install/setup.bash
ros2 launch arm_control typing_sim.launch.py
```

Over SSH, add `viewer:=false` at the end.

All four nodes start in this one terminal, each line labelled with the node it comes from. Check from a second terminal:

```bash
ros2 node list
```

```
/forward_kinematics
/inverse_kinematics
/keyboard_typer
/sim_node
```

Now type. In the second terminal:

```bash
ros2 topic pub --once /key std_msgs/msg/String "{data: a}"
```

The arm moves above the red key, presses it, and lifts off. In the launch terminal you should see:

```
[keyboard_typer-4] [INFO] [keyboard_typer]: Typing 'a'
[sim_node-1] [INFO] [sim_node]: key_a pressed
```

Try `s` and `d`. Then try a letter that is not in the table:

```bash
ros2 topic pub --once /key std_msgs/msg/String "{data: q}"
```

```
[keyboard_typer-4] [WARN] [keyboard_typer]: Unknown key 'q'. Known keys: ['a', 'd', 's']
```

Stop everything with `Ctrl` + `C` in the launch terminal.

## Measure how well it works

Your report needs numbers. Some things you can measure in simulation:

- **Position error.** While the finger is on a key, compare `/true_fingertip` with the target you asked for. How many millimetres off, and in which direction?
- **Model error versus tracking error.** `/fk_pose` is where your model thinks the fingertip is. `/true_fingertip` is where it is. `/fk_pose` versus the target shows how well the arm followed its command. `/true_fingertip` versus `/fk_pose` shows how good the model is.
- **Speed versus success.** Lower `MOVE_TIME`. At what speed does a key stop registering?

## From simulation to the real robot

The same three nodes run on the real robot. What changes:

1. **`robot_node` takes the place of `sim_node`.** See [Hardware bring-up, page 4](../HW-Bringup/04_robot_node.md). It uses the same `/arm_commands` and `/arm_state` topics.
2. **You need your own key positions.** `KEY_POSITIONS` describes the simulated keyboard. For a real one, put the robot in read-only mode, move the arm **by hand** until the fingertip rests on a key, and read your `/fk_pose`. That is the key's position as your own kinematics sees it, which is exactly what your IK needs. Repeat for the three keys.
3. **There is no `/true_fingertip` and no `/key_pressed`.** On the real robot, the keyboard itself tells you whether a key was pressed.
4. **Start slowly.** Use a larger `MOVE_TIME` and a smaller `PRESS_DEPTH` at first, and keep a hand on the power switch.

Measuring the key positions with the robot's own FK has a useful side effect: an error in the kinematic model largely cancels out, because the same model is used to record the position and to return to it.

## If something went wrong

| What you see | What to do |
| --- | --- |
| `Still busy with the previous key. Ignored.` | You sent a letter while the arm was still moving. Wait for the three moves to finish. |
| `No arm_state received yet.` | `sim_node` is not running, or not on the same `ROS_DOMAIN_ID`. |
| `Key 'a' is out of reach` | Your IK did not converge. Test it on its own ([previous page](02_inverse_kinematics.md)). |
| The arm moves but the key is not pressed | Look at the pink ball. If it is on the fingertip, your FK is fine and the press is too shallow or off to the side. If it is not, fix FK first. |
| The finger hits the key with its side | The finger is not vertical. Check the direction part of your IK. |
| `ros2 launch` says `Package 'arm_control' not found` | Build and source the workspace again. |
| A launch file change has no effect | Launch files are installed by the build. Run `colcon build` after every change. |

---

Previous: [2. Inverse kinematics](02_inverse_kinematics.md) | Back to the [overview](README.md)
