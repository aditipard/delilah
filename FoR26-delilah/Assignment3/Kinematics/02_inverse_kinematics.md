# 2. Inverse Kinematics

**Inverse kinematics (IK)** asks the opposite question to FK: I want the fingertip **there**, so what should the joint angles be?

FK is a formula. IK usually is not: there may be many answers, or none. You solve it **numerically**: start from a guess, see how far off the fingertip is, improve the guess, and repeat. You may use the solver you wrote in Assignment 02, or the method described here.

## What exactly is asked for

To press a key, the fingertip must be at a certain position **and** the finger must point straight down. So the target has two parts:

| Part | Size | Example |
| --- | --- | --- |
| fingertip position | 3 numbers | (0.28, 0.05, 0.05) |
| finger direction | a unit vector | (0, 0, -1), straight down |

A direction has only 2 free numbers, so the target fixes 5 quantities.

The arm has 5 joints, but `wrist_roll` cannot help. Its axis runs along the finger, so rolling the wrist changes neither where the fingertip is (to within a millimetre or two) nor which way the finger points. That leaves **4 joints for 5 quantities**. In general there is no exact answer, only a best one, so the solver must be told what matters more. Position matters more: the direction part is given a small weight.

## The method: damped least squares

Put the things you care about into one vector, the **task**:

```
task(angles) = [ position (3 numbers),  weight * direction (3 numbers) ]
```

with `position` and `direction` from your own `forward_kinematics`. The goal is the same vector built from the target. Then repeat:

1. `error = goal - task(angles)`
2. Compute the **Jacobian** `J`: a table with 6 rows and 4 columns that says how the task changes when each of the 4 joints moves a little.
3. `change = Jᵀ (J Jᵀ + λ² I)⁻¹ error`
4. `angles[:4] = angles[:4] + change`, then clip to the joint limits.
5. Stop when the error is tiny, or after a fixed number of rounds.

Two practical points:

**The Jacobian without calculus.** Move one joint by a small step, see how much the task changes, and divide by the step:

```python
nudged = angles.copy()
nudged[j] += step
J[:, j] = (task(nudged) - task(angles)) / step
```

Do that for each of the 4 joints. This is called a **finite difference**.

**Why "damped".** Near a stretched-out pose the plain formula asks for enormous joint changes. The term `λ² I` (the damping) keeps the changes reasonable. A small λ follows the target closely, a larger one is calmer but slower. Also limit how much the angles may change in one round, for example to 10 degrees.

In NumPy, step 3 is one line:

```python
change = J.T @ np.linalg.solve(J @ J.T + damping**2 * np.eye(6), error)
```

## Exercise 1: the function

In `kinematics.py`, fill in the TODO in `inverse_kinematics`. The function already prepares `target_position`, `target_direction` and `angles`, and computes the remaining position error at the end.

Test it without ROS:

```bash
conda activate ros_mujoco
cd ~/FOR26/ros_ws/src/arm_control
python -c "from arm_control.kinematics import inverse_kinematics; print(inverse_kinematics([0.28, 0.05, 0.05], [0, 0, -1], [0, 0, 0, 0, 0]))"
```

Before you write anything it returns the starting angles and a large error:

```
(array([0., 0., 0., 0., 0.]), 0.2956700813406727)
```

A working solver returns something close to

```
(array([-15.4,  18.7,   3.3,  83. ,   0. ]), 0.0000...)
```

Your numbers need not be identical. What must hold is that the **error** (the second value, in metres) is well below a millimetre.

Then check your IK with your FK:

```bash
python -c "
from arm_control.kinematics import forward_kinematics, inverse_kinematics
angles, error = inverse_kinematics([0.28, 0.05, 0.05], [0, 0, -1], [0, 0, 0, 0, 0])
print(forward_kinematics(angles))"
```

The position must come out as (0.28, 0.05, 0.05) and the direction close to (0, 0, -1).

## What the arm can and cannot reach

With the finger pointing **straight down**, the arm's reach is smaller than you might expect. We measured, in the base frame:

| Target | Result |
| --- | --- |
| (0.28, 0.05, 0.05) | reached |
| (0.25, -0.10, 0.05) | reached |
| (0.35, 0.00, 0.00) | reached |
| (0.25, 0.10, 0.10) | 6 mm short |
| (0.30, 0.00, 0.10) | 27 mm short |
| (0.20, 0.00, 0.15) | 84 mm short |

Low targets in front of the robot work. Higher ones fail, because the wrist would have to bend further than its 100° limit to keep the finger vertical. A keyboard on the floor in front of the robot is within reach.

This is why the function returns the error: **always check it before you move the robot.**

## Exercise 2: the node

Open `ik_node.py` and fill in the two TODOs.

| TODO | What to write |
| --- | --- |
| 1 | A publisher for `Float64MultiArray` on `"arm_commands"`, a subscription to `"ik_target"` (`PoseStamped`, calls `self.on_target`) and one to `"arm_state"` (calls `self.on_arm_state`). |
| 2 | In `on_target`: solve IK starting from `self.arm_state`. If the error is above `MAX_ERROR`, warn and return. Otherwise publish the five angles plus the gripper value. |

Starting each solve from the arm's **current** angles is a good habit. Of all possible answers, the solver then finds one close to where the arm already is.

## Check it

Build, start `sim_node` with the keyboard scene and your `forward_kinematics` as on the previous page, and add in a new terminal:

```bash
ros2 run arm_control inverse_kinematics
```

Send a target:

```bash
ros2 topic pub --once /ik_target geometry_msgs/msg/PoseStamped "{pose: {position: {x: 0.28, y: 0.05, z: 0.05}}}"
```

The arm moves, and the finger ends up pointing down. Now check where the fingertip really went:

```bash
ros2 topic echo --once /true_fingertip
```

It should be within a few millimetres of (0.28, 0.05, 0.05). The remaining difference is real: the arm sags under its weight and the robot leans forward a little, and neither is part of your kinematic model.

Then send a target the arm cannot reach:

```bash
ros2 topic pub --once /ik_target geometry_msgs/msg/PoseStamped "{pose: {position: {x: 0.9, y: 0.0, z: 0.3}}}"
```

The node must refuse, with a warning like:

```
[WARN] [inverse_kinematics]: Target [0.9, 0.0, 0.3] is out of reach (error 664 mm). Not moving.
```

## Try it yourself

1. Change the direction weight. What happens to the position error and to the finger's tilt for the target (0.25, 0.10, 0.10) when the weight is 0.01, and when it is 1.0?
2. Solve the same target from two different starting poses. Do you get the same angles?
3. Set the damping to 0. Find a target for which the solver now misbehaves.
4. Replace the finite-difference Jacobian with the exact one: column `j` is `axis_j × (position − point_j)` for the position rows, with the axis and point moved to where they are in the current pose.

---

Previous: [1. Forward kinematics](01_forward_kinematics.md) | Next: [3. Keyboard typing](03_keyboard_typing.md)
