# 4. The Real Robot in ROS

`robot_node` is the ROS node for the real LeKiwi. It has the same topics as the simulator node, so everything you built against the simulator can talk to the real robot instead.

```
 /arm_commands  ──►  robot_node  ──►  the real arm
 /base_commands ──►               ──►  the real wheels
                     robot_node  ──/arm_state──►  your nodes
```

> **Draft.** The read-only mode on this page was run on the course robot. The mode that switches the motors on (Part B) has **not** been run on the course robot yet. Treat it with extra care and tell your TA what you observe.

Before you start: the robot is wired and powered ([page 1](01_wiring.md)), you know the LeKiwi board's port ([page 2](02_check_servos.md)), and the workspace is built ([ROS guide, page 2](../ROS/02_build_and_run.md)).

## Step 1: A calibration file for LeKiwi

Like the leader arm, LeKiwi needs a calibration file on this computer. If the arm has been calibrated before, recover the file from the servos:

```bash
conda activate ros_mujoco
python ~/FOR26/Assignment3/HW-Bringup/scripts/recover_calibration.py lekiwi /dev/serial/by-id/usb-1a86_USB_Single_Serial_5B8E116601-if00
```

Use your own LeKiwi board's port. On our robot it printed:

```
Calibration stored in the servos:
  arm_shoulder_pan   id 1  homing_offset   1756  range   805 to  3364
  arm_shoulder_lift  id 2  homing_offset   -988  range   830 to  3165
  arm_elbow_flex     id 3  homing_offset  -1912  range   863 to  3090
  arm_wrist_flex     id 4  homing_offset  -1864  range   896 to  3207
  arm_wrist_roll     id 5  homing_offset    702  range     0 to  4095
  arm_gripper        id 6  homing_offset    957  range  2016 to  3456
  base_left_wheel    id 7  homing_offset      0  range     0 to  4095
  base_back_wheel    id 8  homing_offset      0  range     0 to  4095
  base_right_wheel   id 9  homing_offset      0  range     0 to  4095
Saved to /home/team0/.cache/huggingface/lerobot/calibration/robots/lekiwi/lekiwi.json
File matches the servos: True
Pose now: {'shoulder_pan': -23.0, 'shoulder_lift': -102.6, 'elbow_flex': 95.4, 'wrist_flex': 42.1, 'wrist_roll': 102.9, 'gripper': 24.0}
```

Judge the result as on the [calibration page](03_calibration.md#check-the-result). The three wheels always show `0 to 4095`, because they turn freely.

If the arm was never calibrated, do a [full calibration](03_calibration.md#full-calibration) first.

## Part A: Read-only mode

In read-only mode `robot_node` only **reads** the arm. The motors stay off, nothing moves, and the arm is limp. This is the default, and it is safe.

### Start it

```bash
conda activate ros_mujoco
cd ~/FOR26/ros_ws
source install/setup.bash
ros2 run lekiwi_ros robot_node --ros-args -p port:=/dev/serial/by-id/usb-1a86_USB_Single_Serial_5B8E116601-if00
```

```
[INFO] [1791565298.107864589] [robot_node]: Read-only: publishing arm_state, motors off. Start with -p enable_motors:=true to drive the robot.
```

### Look at the arm's state

In a second terminal (with the three start lines):

```bash
ros2 topic echo --once /arm_state
```

You get six numbers, the pose of the real arm in degrees and the gripper in percent. On our robot, folded in its rest position: `-23.0 -102.6 95.4 42.1 102.9 24.0`.

```bash
ros2 topic hz /arm_state
```

```
average rate: 9.983
```

Ten readings per second.

### Use it

Move the real arm **by hand** and watch `/arm_state` change. Every node you wrote that listens to `/arm_state` now works with the real arm:

- Your `follower` from the ROS guide.
- Your `forward_kinematics` node. Its `/fk_pose` now tells you where the **real** fingertip is, according to your model.

That second one is how you measure the positions of real keys for the [typing page](../Kinematics/03_keyboard_typing.md): rest the fingertip on a key and read `/fk_pose`.

## Part B: Motors on

> Read this whole part before you run anything.

With `enable_motors:=true` the node switches the motors on and the arm follows `/arm_commands`.

### What to expect

- **At start the arm goes stiff and holds the pose it is in.** The node's first target is the arm's own current position, so it should not move.
- **Each joint moves at most 5 degrees per step**, ten steps per second, so at most 50 degrees per second. This limit is the parameter `max_relative_target`.
- **The wheels stop if no base command arrives for half a second.**
- **When the node stops, the motors switch off and the arm goes limp.** Hold the arm, or put it in its folded rest position, before you press `Ctrl` + `C`.

### Before you start

- [ ] The robot is on blocks, wheels off the ground.
- [ ] Nothing and nobody is within the arm's reach.
- [ ] One person has a hand on the power switch.
- [ ] No other program is using the LeKiwi board.
- [ ] Nothing is publishing on `/arm_commands` yet. Check: `ros2 topic info /arm_commands` must say `Publisher count: 0`.

### Start it

```bash
ros2 run lekiwi_ros robot_node --ros-args -p port:=/dev/serial/by-id/usb-1a86_USB_Single_Serial_5B8E116601-if00 -p enable_motors:=true
```

The node warns that the motors are on. The arm should now resist when you push it gently, and stay where it is.

### First motion

Read the current pose and send it back with **one** joint changed by a few degrees:

```bash
ros2 topic echo --once /arm_state
```

```bash
ros2 topic pub --once /arm_commands std_msgs/msg/Float64MultiArray "{data: [-18.0, -102.6, 95.4, 42.1, 102.9, 24.0]}"
```

Use **your own** numbers from `/arm_state`, with only the first one changed by 5. The base of the arm should turn slightly.

If anything unexpected happens, **switch the power off**.

### Teleoperation

Once single commands work, the leader arm can drive the real arm:

1. Put the leader arm in the **same pose** as the robot's arm. Compare `/arm_state` with what the leader will send.
2. Start the leader node, as in the [ROS guide](../ROS/04_teleop_in_sim.md):

   ```bash
   ros2 run lekiwi_ros leader_node --ros-args -p port:=/dev/serial/by-id/usb-...your leader...
   ```

The real arm now follows the leader, at up to 50 degrees per second.

**Never run `sim_node` and `robot_node` at the same time.** Both publish `/arm_state`, and your nodes could not tell them apart.

## Parameters

| Parameter | Meaning | Default |
| --- | --- | --- |
| `port` | LeKiwi board's serial port | none, you must give it |
| `robot_id` | the calibration name | `lekiwi` |
| `enable_motors` | `false` = read-only, `true` = drive the robot | `false` |
| `max_relative_target` | most a joint may move per step, in degrees | `5.0` |
| `rate_hz` | steps per second | `10.0` |

## If something went wrong

| What you see | What to do |
| --- | --- |
| `RuntimeError: Set the port, for example: ...` | You started the node without `-p port:=...`. |
| `No calibration file at ...` | Do Step 1. |
| `The calibration file does not match the values stored in the motors.` | Run the recovery in Step 1 again, or calibrate. |
| `Could not connect on port ...` | Wrong port name, USB unplugged, or another program is using the board. |
| `Servo bus error, skipping this step` now and then | Harmless: the servo bus occasionally drops one reply. If it is constant, check the cables. |
| The node fails at start with `There is no status packet` | A dropped reply during start-up. Start it again. |
| The arm jumps or moves the wrong way | **Power off.** Do not retry. Tell your TA. |

---

Previous: [3. Calibration](03_calibration.md) | Back to the [overview](README.md)
