# 3. Calibration

The servos report their position as a raw number from 0 to 4095 per turn. **Calibration** is the information needed to turn that raw number into a joint angle in degrees: where each joint's middle is, and how far it can move to each side.

LeRobot keeps a calibration in **two places**:

| Where | What for |
| --- | --- |
| inside each servo | so the servo knows its own limits |
| in a file on the computer | so LeRobot can convert raw numbers to degrees |

Both must exist and agree. If they do not, any LeRobot program stops at start-up and asks you to calibrate.

Time needed: about 5 minutes to recover a file, about 15 minutes per arm for a full calibration.

## Which case are you in?

| Situation | What to do |
| --- | --- |
| The arm was calibrated before, on this or another computer, and you only lack the file | **Recover the file** (below) |
| The arm was never calibrated, or its calibration is wrong | Do a [full calibration](#full-calibration) (further down) |

If you are not sure, try the recovery first. It only reads from the servos, so it cannot make anything worse, and its output tells you which case you are in.

## Recover the leader arm's calibration file

You need the leader arm's name under `/dev/serial/by-id/` from the [previous page](02_check_servos.md).

```bash
conda activate ros_mujoco
```

```bash
python ~/FOR26/Assignment3/HW-Bringup/scripts/recover_calibration.py leader /dev/serial/by-id/usb-1a86_USB_Single_Serial_5B8E116010-if00
```

Replace the port name with **your own** leader arm's name.

On our leader arm it printed:

```
Calibration stored in the servos:
  shoulder_pan       id 1  homing_offset  -1910  range   784 to  3417
  shoulder_lift      id 2  homing_offset  -1557  range   961 to  3303
  elbow_flex         id 3  homing_offset   1831  range   775 to  2979
  wrist_flex         id 4  homing_offset   2008  range   866 to  3118
  wrist_roll         id 5  homing_offset   1838  range     0 to  4095
  gripper            id 6  homing_offset    941  range  1901 to  3119
Saved to /home/team0/.cache/huggingface/lerobot/calibration/teleoperators/so_leader/leader.json
File matches the servos: True
Pose now: {'shoulder_pan': 22.7, 'shoulder_lift': -101.9, 'elbow_flex': 97.8, 'wrist_flex': -98.7, 'wrist_roll': -17.3, 'gripper': 0.3}
```

Your numbers will be different. Every arm has its own.

## Check the result

**1. Do the ranges look calibrated?**

| Joint | A calibrated arm shows | A never-calibrated arm shows |
| --- | --- | --- |
| `shoulder_pan`, `shoulder_lift`, `elbow_flex`, `wrist_flex` | a range well inside 0 to 4095, about 2200 to 2700 wide | `0 to 4095` and `homing_offset 0` |
| `wrist_roll` | `0 to 4095`. This joint can turn all the way round, so that is correct. | the same |
| `gripper` | a range roughly 500 to 1500 wide | `0 to 4095`, or a range only 1 or 2 wide |

If your arm looks like the right-hand column, it needs a [full calibration](#full-calibration).

**2. Does the pose make sense?**

The last line shows the arm's current pose in degrees. With the leader arm folded up in its rest position you should see roughly:

| Joint | Folded rest position |
| --- | --- |
| `shoulder_lift` | about -100° |
| `elbow_flex` | about +95° |
| `gripper` | near 0 % when the handle is released |

Now move one joint by hand, run the program again, and check that only that joint's number changed.

**3. `File matches the servos: True`**

This line must say `True`.

## Where the file is

```
~/.cache/huggingface/lerobot/calibration/teleoperators/so_leader/leader.json
```

The file name, `leader`, is the **calibration name** (LeRobot calls it the `id`). Programs that use the leader arm must be given the same name. To use a different name, add it at the end:

```bash
python ~/FOR26/Assignment3/HW-Bringup/scripts/recover_calibration.py leader /dev/serial/by-id/usb-... team3_leader
```

**Back up this file.** It lives outside the course folder, and nothing else saves it.

## Full calibration

> **Draft.** This section follows LeRobot's calibration procedure and the reference setup this course is based on. Unlike the rest of this guide, it has **not yet been run on the course robot**. If a step does not match what you see, tell your TA.

A full calibration measures the arm again and writes the result to both the servos and the file. You need both hands, so do it sitting at the robot.

During calibration the motors are switched **off**. The arm is limp and will drop if you let go, so support it.

### Calibrate the leader arm

```bash
conda activate ros_mujoco
```

```bash
lerobot-calibrate --teleop.type=so101_leader --teleop.port=/dev/serial/by-id/usb-1a86_USB_Single_Serial_5B8E116010-if00 --teleop.id=leader
```

Replace the port with your own leader arm's name.

If a calibration file already exists, the program first asks:

```
Press ENTER to use provided calibration file associated with the id leader, or type 'c' and press ENTER to run calibration:
```

Type `c` and press `Enter` to calibrate again. Pressing only `Enter` keeps the old calibration.

Then it asks for two things:

1. **"Move ... to the middle of its range of motion and press ENTER"**

   Put **every joint roughly halfway** between its two mechanical end stops: the upper arm pointing up, the forearm pointing forward, the wrist straight, the gripper half open. Hold the arm there and press `Enter`.

2. **Move every joint through its full range, then press ENTER**

   One joint at a time, move it slowly from one end stop to the other and back. Open and close the gripper fully. The terminal shows the smallest and largest value seen for each joint. When every joint has been moved, press `Enter`.

   `wrist_roll` can turn all the way round, so it shows no minimum and maximum. That is expected.

The program ends with `Calibration saved to ...`.

**Why the middle pose matters.** The servo counts from 0 to 4095 and then starts again at 0. The pose in step 1 decides where that jump lies. If a joint is near one of its end stops in step 1, the jump ends up inside the joint's working range, and the arm can suddenly "jump" by a full turn while you use it. Starting from the middle keeps the jump far away from anything the joint can reach.

### Calibrate LeKiwi's arm

The same procedure, with the robot's own arm. LeKiwi's three wheels are on the same servo chain, but they turn freely and need no measuring.

Before you start: the robot is on blocks, the power switch is on, and nothing else is using the LeKiwi board.

```bash
lerobot-calibrate --config_path=$HOME/FOR26/Assignment3/HW-Bringup/config/lekiwi_nocam.yaml --robot.port=/dev/serial/by-id/usb-1a86_USB_Single_Serial_5B8E116601-if00 --robot.id=lekiwi
```

Replace the port with your own LeKiwi board's name. The `--config_path` file tells LeRobot that no cameras are connected. Without it, the program looks for two cameras and stops if it does not find them.

Follow the same two steps as for the leader arm. **Use the same middle pose for both arms.**

The file is saved as `~/.cache/huggingface/lerobot/calibration/robots/lekiwi/lekiwi.json`.

### Check a fresh calibration

Run the recovery program from the top of this page again (with `leader` or `lekiwi` as its first argument). It now simply reads back what you just calibrated. Go through the three checks under [Check the result](#check-the-result).

A range close to `0 to 4095` on any joint other than `wrist_roll` means the middle pose in step 1 was too close to an end stop. Calibrate that arm again.

## If something went wrong

| What you see | What to do |
| --- | --- |
| `Could not connect on port '...'` | The port name is wrong, the USB cable is unplugged, or another program is using the board. Check with `ls /dev/serial/by-id/`. |
| `Permission denied` | Your account is not in the `dialout` group. See the [previous page](02_check_servos.md), Step 1. |
| `File matches the servos: False` | Run the program again. If it stays `False`, ask your TA. |
| All ranges are `0 to 4095` | The arm was never calibrated. Do a [full calibration](#full-calibration). |

---

Previous: [2. Check the servos](02_check_servos.md) | Next: [4. The real robot in ROS](04_robot_node.md)
