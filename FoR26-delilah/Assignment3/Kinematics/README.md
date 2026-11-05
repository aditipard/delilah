# Kinematics and Typing

This is the main part of Assignment 03. You write three ROS nodes and one launch file:

| Node | What it does | Assignment section |
| --- | --- | --- |
| `forward_kinematics` | joint angles in, fingertip position out | 3 |
| `inverse_kinematics` | wanted fingertip position in, joint angles out | 4 |
| `keyboard_typer` | a letter in, the motion that presses that key out | 5 |

```
                 /arm_state                    /fk_pose
 sim_node ───────────────────► forward_kinematics ─────► sim_node draws a pink ball
    ▲    │
    │    └──/arm_state──► inverse_kinematics ◄──/ik_target── (you, or any node)
    │                            │
    ├────────/arm_commands───────┘
    │
    └────────/arm_commands─── keyboard_typer ◄──/key── (you: "a", "s" or "d")
```

You develop and test everything against the **simulated** robot and a simulated keyboard. The same nodes then run on the real robot.

Do the [ROS guide](../ROS/README.md) first. Then follow these pages in order.

| # | Page | What you do |
| --- | --- | --- |
| 1 | [Forward kinematics](01_forward_kinematics.md) | Write `forward_kinematics()` and the `ForwardKinematics` node, and check it against the simulator |
| 2 | [Inverse kinematics](02_inverse_kinematics.md) | Write `inverse_kinematics()` and the `InverseKinematics` node |
| 3 | [Keyboard typing](03_keyboard_typing.md) | Write the `KeyboardTyper` node, add your nodes to the launch file, and type |

## Your package

Your files are in the ROS package `arm_control`, in `~/FOR26/ros_ws/src/arm_control`.

| File | Contents |
| --- | --- |
| `arm_control/kinematics.py` | the two maths functions: `forward_kinematics` and `inverse_kinematics` |
| `arm_control/fk_node.py` | the `ForwardKinematics` node |
| `arm_control/ik_node.py` | the `InverseKinematics` node |
| `arm_control/keyboard_typer.py` | the `KeyboardTyper` node |
| `launch/typing_sim.launch.py` | the launch file |

Each file has gaps marked `TODO`. Everything around the gaps is given: the imports, the class skeleton, the checks, the logging.

Until you fill them in, every node starts and does nothing. After every change, build again:

```bash
cd ~/FOR26/ros_ws
colcon build
```

## The topics

| Topic | Message type | Content |
| --- | --- | --- |
| `/arm_state` | `std_msgs/Float64MultiArray` | 5 joint angles (deg) and the gripper (%): where the arm is |
| `/arm_commands` | `std_msgs/Float64MultiArray` | 5 joint angles (deg) and the gripper (%): where the arm should go |
| `/fk_pose` | `geometry_msgs/PoseStamped` | the fingertip position your forward kinematics computes, in the base frame |
| `/true_fingertip` | `geometry_msgs/PointStamped` | where the fingertip really is, in the base frame. Simulator only, for checking. |
| `/ik_target` | `geometry_msgs/PoseStamped` | a wanted fingertip position, in the base frame |
| `/key` | `std_msgs/String` | a letter to type |
| `/key_pressed` | `std_msgs/String` | the name of a key, each time it goes down. Simulator only. |

## The base frame

All positions on these pages are in the robot's **base frame**:

| | |
| --- | --- |
| Origin | the centre of the bottom base plate |
| x | forward, towards the arm |
| y | to the robot's left |
| z | up |

The origin is a few centimetres above the floor, so points near the floor have a slightly **negative** z.

## The end effector

The point that all the kinematics is about is the **tip of the gripper's fixed finger**. It is the point that touches a key. In the simulator it is marked with a small pink dot.

## A known limitation

The simulated arm has the shape of an older arm version (SO-100). The real arm is an SO-101, and the two differ by a few centimetres near the gripper. The kinematic numbers on these pages describe the **simulated** arm. On the real robot, expect your forward kinematics to be off by about that much, and measure your key positions with the real robot itself (page 3).
