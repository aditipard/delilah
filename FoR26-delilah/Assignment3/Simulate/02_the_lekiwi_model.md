# 2. The LeKiwi Model

The pendulum on the previous page had one body and one joint. The LeKiwi model is the same kind of thing, only much bigger. On this page you look inside it.

The model is the file `~/FOR26/models/LeKiwi-sim/mjcf_lcmm_robot.xml`. It was made by converting the robot's CAD drawings to MJCF.

## Look inside

```bash
conda activate ros_mujoco
cd ~/FOR26/Assignment3/Simulate/scripts
python 02_explore_model.py
```

You should see:

```
bodies: 68, joints: 35, actuators: 9, cameras: 1
numbers in qpos (positions): 47, in qvel (velocities): 45
timestep: 0.002 s

Actuators (the things you can command):
  0: drive_motor_1  drives joint 'ST3215_Servo_Motor-v1-2_Hub---Servo', no command limit
  1: drive_motor_2  drives joint 'ST3215_Servo_Motor-v1-1_Hub-2---Servo', no command limit
  2: drive_motor_3  drives joint 'ST3215_Servo_Motor-v1_Revolute-40', no command limit
  3: Rotation       drives joint 'Rotation', command range -2.01 to  2.01
  4: Pitch          drives joint 'Pitch', command range -3.14 to  0.17
  5: Elbow          drives joint 'Elbow', command range -0.09 to  3.14
  6: Wrist_Pitch    drives joint 'Wrist_Pitch', command range -0.35 to  3.14
  7: Wrist_Roll     drives joint 'Wrist_Roll', command range  1.92 to  6.46
  8: Jaw            drives joint 'Jaw', command range -0.17 to  1.75

Joints that are not passive wheel rollers:
  target_block_free                        type free  starts at qpos[0]
  base_free                                type free  starts at qpos[7]
  ST3215_Servo_Motor-v1-2_Hub---Servo      type hinge starts at qpos[14]
  ST3215_Servo_Motor-v1-1_Hub-2---Servo    type hinge starts at qpos[23]
  ST3215_Servo_Motor-v1_Revolute-40        type hinge starts at qpos[32]
  Rotation                                 type hinge starts at qpos[41]
  Pitch                                    type hinge starts at qpos[42]
  Elbow                                    type hinge starts at qpos[43]
  Wrist_Pitch                              type hinge starts at qpos[44]
  Wrist_Roll                               type hinge starts at qpos[45]
  Jaw                                      type hinge starts at qpos[46]
  ... plus 24 passive roller joints on the three omni wheels
```

## What this tells you

**Nine actuators, like the nine servos of the real robot.** Three drive the wheels and six drive the arm. These nine numbers in `data.ctrl` are all you can command.

**The base is a free body.** `base_free` is a `free` joint: the base is not attached to the world. It moves only because its wheels push against the floor, exactly like the real robot. A free joint takes 7 numbers in `qpos` (3 for position, 4 for orientation), which is why the next joint starts at `qpos[14]`.

**The wheels are real omni wheels.** An omni wheel has small rollers around its rim that spin freely, so the wheel can slide sideways while it rolls forward. The model contains all 24 rollers (8 per wheel) as passive joints. This is what lets the robot drive sideways.

**47 position numbers for a robot with 9 motors.** Most of `qpos` describes things you do not command: the base pose, the rollers, the loose block. This is normal, and it is the reason you want a wrapper class instead of indexing into `qpos` by hand.

## The arm: model names and real names

The model uses the names from the CAD drawing. The real robot, through LeRobot, uses different names. They are the same six joints.

| Real robot (LeRobot) | Model | What it does |
| --- | --- | --- |
| `shoulder_pan` | `Rotation` | turns the whole arm left and right |
| `shoulder_lift` | `Pitch` | raises and lowers the upper arm |
| `elbow_flex` | `Elbow` | bends the elbow |
| `wrist_flex` | `Wrist_Pitch` | tilts the hand up and down |
| `wrist_roll` | `Wrist_Roll` | rotates the hand about its own axis |
| `gripper` | `Jaw` | opens and closes the gripper |

## The model does not speak the real robot's units

This is the most important thing on this page. The model and the real robot describe the same pose with **different numbers**.

| | Real robot | Model |
| --- | --- | --- |
| Arm angles | degrees | radians |
| Where zero is | the middle of each joint's range | wherever the CAD drawing put it |
| Positive direction | LeRobot's convention | opposite, for all five arm joints |
| Gripper | 0 % (closed) to 100 % (open) | -0.17 rad to 1.75 rad |
| Base | forward m/s, left m/s, turn deg/s | three separate wheel speeds in rad/s |

For the five rotary arm joints the conversion is

```
model_angle_in_degrees = sign * real_angle_in_degrees + offset
```

with these values:

| Joint | sign | offset (degrees) |
| --- | --- | --- |
| `shoulder_pan` | -1 | 0 |
| `shoulder_lift` | -1 | -90 |
| `elbow_flex` | -1 | 90 |
| `wrist_flex` | -1 | 80 |
| `wrist_roll` | -1 | 270 |

These values were found by comparing the model with a real arm, joint by joint. You do not need to remember them. The `LeKiwiSim` class on the next page applies them for you in both directions, so that **you only ever see the real robot's units**. That is what will later allow the same code to drive the simulated robot and the real one.

## How far each joint can move

In the real robot's units, the simulated arm accepts:

| Joint | Lowest | Highest |
| --- | --- | --- |
| `shoulder_pan` | -115° | 115° |
| `shoulder_lift` | -100° | 90° |
| `elbow_flex` | -90° | 95° |
| `wrist_flex` | -100° | 100° |
| `wrist_roll` | -100° | 160° |
| `gripper` | 0 % | 100 % |

A command outside these limits is cut off at the limit.

## What is simplified

A simulation is a model of reality, not reality. Know the differences:

- **The arm's shape is from an older arm version** (SO-100). The real arm is an SO-101. Near the gripper the two differ by a few centimetres.
- **Most parts of the robot cannot collide.** The original model switches collisions off for nearly every part, because the detailed CAD shapes overlap each other. Only the wheels, a few spheres along the arm, and the gripper fingers can touch things. The arm can therefore pass through the robot's own base.
- **The gripper fingers are our addition.** The original model had no collision shapes on the gripper at all, so it could not hold anything. `LeKiwiSim` adds an invisible contact pad on each finger and a weaker gripper motor. See `_build_model` in `~/FOR26/lekiwi_sim/simulator.py`.
- **Turning on the spot is slightly slow.** A command of 30 deg/s gives about 26 deg/s, because the wheels slip a little.
- **The wheel motors are our change too.** In the original model a stopped robot slowly creeps when the arm leans out. `LeKiwiSim` makes the wheel motors hold their position when stopped, as real servos do.

## Try it yourself

1. Open `~/FOR26/models/LeKiwi-sim/mjcf_lcmm_robot.xml` in VS Code and find the `<actuator>` section. Which actuator type do the wheels use, and which do the arm joints use?
2. The real `shoulder_lift` is at 0°. Using the table above, what angle does the model's `Pitch` joint have, in degrees?
3. Why does `qvel` have 45 numbers when `qpos` has 47? (Hint: count the free joints, and look up how MuJoCo stores orientation.)

---

Previous: [1. What is MuJoCo?](01_what_is_mujoco.md) | Next: [3. The simulator class](03_the_simulator_class.md)
