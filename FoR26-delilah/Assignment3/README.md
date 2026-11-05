# Assignment 03: Inverse Kinematics

**Course page:** <https://sites.google.com/nyu.edu/rob-gy6003/assignments/assignment-03-inverse-kinematics>

The course page is the official description of the assignment: what to hand in, the report format, and the deadlines. This folder is the practical companion. It takes you step by step from a bare computer to a robot you can command through ROS, so that you can spend your time on the kinematics.

## What the assignment asks for

In this assignment you add ROS, forward kinematics (FK), inverse kinematics (IK) and a typing controller to the robot.

**Goals**

1. Add ROS 2 to the robot.
2. Add robot simulation capabilities.
3. Embed FK, IK and PD control in the robot's control stack.
4. Demonstrate a feedback control experiment that uses ROS, IK and FK.

**What you hand in** (see the course page for details)

1. A video of the robot pressing three keys on a keyboard.
2. A report.
3. Your code, including your launch file and the files of your new ROS nodes.

## The guides

Follow them in this order. Each page ends with a check, so you know it worked before you move on.

| Guide | What you get | Assignment section |
| --- | --- | --- |
| [Setup](Setup/README.md) | The lab computer prepared: terminal basics, ROS 2, conda, MuJoCo, LeRobot, VS Code, SSH | 1. Software setup |
| [Hardware bring-up](HW-Bringup/README.md) | The robot wired, every servo checked, the arms calibrated, the real robot available in ROS | 2. Robot commands |
| [Simulation](Simulate/README.md) | MuJoCo, the LeKiwi model, and the `LeKiwiSim` simulator class | 2. Robot commands |
| [ROS](ROS/README.md) | ROS 2 concepts, your first two nodes, teleoperating the simulated robot with the leader arm, launch files | 1 and 2 |
| [Kinematics and typing](Kinematics/README.md) | Your forward kinematics, inverse kinematics and keyboard typing nodes, and your launch file | 3, 4 and 5 |

## How the guides map to the assignment

| Assignment section | Status of the guides |
| --- | --- |
| 1. Software setup: install ROS 2, build the code, configure the environment, study the nodes and topics | Covered by **Setup** and **ROS**, pages 1 and 2 |
| 2. Robot commands: teleoperate a simulated robot | Covered by **ROS**, page 4 |
| 2. Robot commands: teleoperate the hardware robot | Covered by **Hardware bring-up**, page 4 (draft: the motors-on part has not yet been run on the course robot) |
| 2. Robot commands: RViz visualization | Not yet available |
| 3. Forward kinematics node | Covered by **Kinematics**, page 1 |
| 4. Inverse kinematics node | Covered by **Kinematics**, page 2 |
| 5. Keyboard typing control | Covered by **Kinematics**, page 3, in simulation. Typing on a real keyboard follows the same page's last section. |

## The idea that carries through

Everything in these guides uses **one set of units**, the same one the real robot uses:

| Quantity | Unit |
| --- | --- |
| Arm joints | degrees, with 0 at the middle of each joint's range |
| Gripper | percent, 0 = closed, 100 = open |
| Base velocity | forward m/s, left m/s, turn deg/s |

The simulator, the ROS topics and the leader arm all speak these units. A node you write and test against the simulated robot can therefore later command the real one.
