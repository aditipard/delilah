# 1. Forward Kinematics

**Forward kinematics (FK)** answers the question: the joints are at these angles, so where is the fingertip?

On this page you write the function that computes it, wrap it in a ROS node, and check it against the simulator.

## The arm's description

To compute FK you need to know the arm's geometry. It is given in `~/FOR26/lekiwi_sim/arm_model.py`, for the **zero pose** (all five joints at 0 degrees), in the [base frame](README.md#the-base-frame).

For each joint: a **point** on its rotation axis and the **direction** of that axis.

| Joint | Point on the axis (m) | Axis direction |
| --- | --- | --- |
| `shoulder_pan` | (0.06715, 0.00000, 0.08445) | (0, 0, -1) |
| `shoulder_lift` | (0.09775, -0.01830, 0.13665) | (0, 1, 0) |
| `elbow_flex` | (0.11583, -0.01680, 0.25123) | (0, 1, 0) |
| `wrist_flex` | (0.24876, -0.01530, 0.27995) | (0, 1, 0) |
| `wrist_roll` | (0.30778, 0.00480, 0.29577) | (-0.96593, 0, -0.25882) |

And for the end effector, at the zero pose:

| | |
| --- | --- |
| Fingertip position | (0.41257, 0.00480, 0.31039) m |
| Direction the finger points in | (0.96593, 0, 0.25882) |

Turning a joint by a **positive** angle rotates everything after it counter-clockwise about its axis direction (right-hand rule: thumb along the axis, fingers curl in the positive direction).

In Python these are `JOINT_POINTS`, `JOINT_AXES`, `HOME_FINGERTIP` and `HOME_FINGER_DIRECTION`.

## The idea

Rotating a point `p` about an axis that passes through the point `q` is done in three moves: shift so the axis passes through the origin, rotate, shift back.

```
p_new = q + rotate(p - q, axis, angle)
```

The function `rotate(vector, axis, angle_rad)` is given in `kinematics.py`.

The arm is a chain of five such rotations. Start with the fingertip at its zero-pose position and apply the joint rotations **from the last joint to the first**:

1. rotate about `wrist_roll`,
2. then about `wrist_flex`,
3. then `elbow_flex`,
4. then `shoulder_lift`,
5. then `shoulder_pan`.

Why this order? When you rotate about `wrist_roll` first, all the joints before it are still at zero, so its axis is exactly where the table says it is. Each later rotation then carries the fingertip, and everything already applied to it, along correctly. Going the other way round, you would have to move every later axis after each step.

The finger's **direction** is a direction, not a point, so it is only rotated, never shifted:

```
d_new = rotate(d, axis, angle)
```

This is the same mathematics as the product of exponentials formula from the lectures, written out for a point.

## Exercise 1: the function

Open `~/FOR26/ros_ws/src/arm_control/arm_control/kinematics.py` and find `forward_kinematics`. It already converts the angles to radians and sets `position` and `direction` to their zero-pose values. Fill in the TODO: apply the five rotations.

Test the function on its own, without ROS. From the folder that contains it:

```bash
conda activate ros_mujoco
cd ~/FOR26/ros_ws/src/arm_control
python -c "from arm_control.kinematics import forward_kinematics; print(forward_kinematics([0, 0, 0, 0, 0]))"
```

At the zero pose you must get the zero-pose values back:

```
(array([0.41257, 0.0048 , 0.31039]), array([0.96593, 0.     , 0.25882]))
```

That works even before you write anything, so try a pose that moves:

```bash
python -c "from arm_control.kinematics import forward_kinematics; print(forward_kinematics([90, 0, 0, 0, 0]))"
```

`shoulder_pan` at +90° turns the arm to the robot's **right**. The fingertip should now be far out in the **negative y** direction, with x close to the shoulder's own x (0.067).

## Exercise 2: the node

Open `fk_node.py`. Fill in the two TODOs:

| TODO | What to write |
| --- | --- |
| 1 | A publisher for `PoseStamped` on `"fk_pose"`, and a subscription to `"arm_state"` that calls `self.on_arm_state`. |
| 2 | In `on_arm_state`: build a `PoseStamped`, set `header.frame_id` to `"base"`, copy the position into `pose.position.x`, `.y`, `.z`, and publish it. |

A `PoseStamped` is filled like this:

```python
pose = PoseStamped()
pose.header.frame_id = "base"
pose.pose.position.x = 1.0
```

## Check it against the simulator

Build, then start the simulator with the keyboard scene.

Terminal 1:

```bash
conda activate ros_mujoco
cd ~/FOR26/ros_ws
colcon build
source install/setup.bash
ros2 run lekiwi_ros sim_node --ros-args -p scene:=keyboard
```

Terminal 2 (with the three start lines):

```bash
ros2 run arm_control forward_kinematics
```

**Check 1, by eye.** In the simulator window a **pink ball** appears. The simulator draws it wherever your node says the fingertip is. If your FK is right, the ball sits on the tip of the gripper's lower finger.

Now move the arm and watch whether the ball stays on the fingertip. In terminal 3:

```bash
ros2 topic pub --once /arm_commands std_msgs/msg/Float64MultiArray "{data: [40.0, 20.0, -30.0, 50.0, 0.0, 0.0]}"
```

Try several poses. Or run your `leader` from the ROS guide (`ros2 run hello_ros leader`) and watch the ball ride along as the arm swings.

**Check 2, by numbers.** The simulator also publishes where the fingertip really is. Compare:

```bash
ros2 topic echo --once /fk_pose
```

```bash
ros2 topic echo --once /true_fingertip
```

With a correct FK and the arm at rest, the three position values agree to within about a millimetre. For example, at the start pose we measured `x: 0.4171, y: 0.0048, z: 0.2977` on `/fk_pose`.

The z value is 1.3 cm lower than the zero-pose value from the table (0.3104), although all commands are zero. That is correct: the arm sags by about a degree under its own weight, the node computes FK from the **measured** angles in `/arm_state`, and so it follows the sag.

## What a wrong FK looks like

| What you see | Likely cause |
| --- | --- |
| The ball never moves from the zero-pose fingertip | The rotations are not applied, or the node passes the wrong numbers |
| The ball is right at the zero pose but drifts away as joints move | The rotations are applied in the wrong order (first joint to last) |
| The ball mirrors the arm's motion | A sign error: an angle or an axis is negated |
| The ball is far off even for small angles | Degrees were used where radians are needed |

## Try it yourself

1. Compute by hand where the fingertip is for `[90, 0, 0, 0, 0]`, using only the table. Compare with your function.
2. How long is the arm? Use your function to find the fingertip's distance from the `shoulder_lift` axis at the zero pose.
3. Which joint does **not** change the direction the finger points in? Check it with your function, then explain it from the table.

---

Back to the [overview](README.md) | Next: [2. Inverse kinematics](02_inverse_kinematics.md)
