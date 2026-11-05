# 2. Build and Run

On this page you build the course's ROS packages, start the simulator as a ROS node, and examine it with the `ros2` tools.

Time needed: about 30 minutes.

## Step 1: Keep your ROS traffic to yourself

By default, ROS nodes find each other across the whole network. In a lab where every team runs the same nodes, your leader arm would move another team's robot.

Two settings prevent that. Add them to your `.bashrc`, **replacing `7` with your team number**:

```bash
echo 'export ROS_DOMAIN_ID=7' >> ~/.bashrc
```

```bash
echo 'export ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST' >> ~/.bashrc
```

| Setting | Meaning |
| --- | --- |
| `ROS_DOMAIN_ID` | A number from 0 to 101. Only nodes with the same number can see each other. |
| `ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST` | Nodes only look for other nodes on this same computer. |

Run each `echo` command only once. Then **close the terminal and open a new one**.

## Step 2: Understand the workspace

ROS code lives in a **workspace**, a folder with a fixed layout. Ours is `~/FOR26/ros_ws`.

```
ros_ws/
└── src/                      the source code: one folder per package
    ├── lekiwi_ros/           package: the provided nodes
    │   ├── package.xml       the package's name and what it depends on
    │   ├── setup.py          which nodes the package contains
    │   ├── setup.cfg         build settings
    │   └── lekiwi_ros/       the Python files
    │       ├── sim_node.py
    │       └── leader_node.py
    ├── hello_ros/            package: your first nodes (page 3)
    └── arm_control/          package: your kinematics nodes (Kinematics guide)
```

A **package** is a folder of related code that ROS can find by name. Building the workspace creates three more folders next to `src`: `build`, `install` and `log`. You never edit those.

## Step 3: Build

The tool that builds a workspace is called `colcon`.

```bash
conda activate ros_mujoco
```

```bash
cd ~/FOR26/ros_ws
```

```bash
colcon build
```

You should see:

```
Starting >>> hello_ros
Starting >>> lekiwi_ros
Finished <<< hello_ros [1.60s]
Finished <<< lekiwi_ros [1.60s]
Starting >>> arm_control
Finished <<< arm_control [1.30s]

Summary: 3 packages finished [3.04s]
```

> Always run `colcon build` **inside `~/FOR26/ros_ws`**. If you run it in another folder, it creates `build`, `install` and `log` there.

## Step 4: Source the workspace

A terminal knows about ROS itself because your `.bashrc` sources `/opt/ros/jazzy/setup.bash`. It does not yet know about **your** workspace. Tell it:

```bash
source ~/FOR26/ros_ws/install/setup.bash
```

Check that ROS now finds the packages:

```bash
ros2 pkg executables lekiwi_ros
```

```
lekiwi_ros leader_node
lekiwi_ros robot_node
lekiwi_ros sim_node
```

You need the `source` line in **every new terminal** in which you want to use the workspace. From now on, every terminal in this lab starts with these three lines:

```bash
conda activate ros_mujoco
cd ~/FOR26/ros_ws
source install/setup.bash
```

## Step 5: Start the simulator node

> Do this in a terminal **on the lab computer's own screen**, because it opens the 3-D window.

```bash
ros2 run lekiwi_ros sim_node
```

The MuJoCo window opens, and the terminal prints:

```
[INFO] [1791554330.855950101] [sim_node]: Simulator running. Waiting for arm_commands and base_commands.
```

The robot stands still. The node is waiting for someone to publish commands. Leave it running.

Working over SSH? Start it without the window instead:

```bash
ros2 run lekiwi_ros sim_node --ros-args -p viewer:=false
```

`--ros-args -p name:=value` sets a **parameter** of the node. `viewer` is one of `sim_node`'s parameters.

## Step 6: Look at the running system

Open a **second terminal**, run the three start lines from Step 4, and then try each command.

**Which nodes are running?**

```bash
ros2 node list
```

```
/sim_node
```

**Which topics exist?**

```bash
ros2 topic list
```

```
/arm_commands
/arm_state
/base_commands
/base_pose
/camera/image
/fk_pose
/key_pressed
/parameter_events
/rosout
/true_fingertip
```

All but `/parameter_events` and `/rosout` belong to `sim_node`. Those two exist in every ROS system. `/fk_pose`, `/key_pressed` and `/true_fingertip` are used later, in the Kinematics guide.

**What does the node publish and subscribe to?**

```bash
ros2 node info /sim_node
```

```
/sim_node
  Subscribers:
    /arm_commands: std_msgs/msg/Float64MultiArray
    /base_commands: std_msgs/msg/Float64MultiArray
  Publishers:
    /arm_state: std_msgs/msg/Float64MultiArray
    /base_pose: std_msgs/msg/Float64MultiArray
    /camera/image: sensor_msgs/msg/Image
    ...
```

**Who is on a topic?**

```bash
ros2 topic info /arm_commands
```

```
Type: std_msgs/msg/Float64MultiArray
Publisher count: 0
Subscription count: 1
```

One subscriber (`sim_node`) and no publisher. That is why the robot is not moving: nobody is sending commands.

**What is inside this message type?**

```bash
ros2 interface show std_msgs/msg/Float64MultiArray
```

The line that matters is the last one:

```
float64[]         data          # array of data
```

A `Float64MultiArray` carries a list of numbers called `data`. The `layout` part above it is optional and we leave it empty.

**What is being sent?**

```bash
ros2 topic echo --once /arm_state
```

```
layout:
  dim: []
  data_offset: 0
data:
- 4.478996530072039e-05
- 1.202294672380276
- 1.0454363015120265
- 0.2665051421516438
- 0.008322221336300117
- 49.981672332017766
---
```

Six numbers: the five arm joints are near 0 degrees and the gripper is at 50 %. `--once` prints one message and stops. Without it, messages scroll by until you press `Ctrl` + `C`.

**How often?**

```bash
ros2 topic hz /arm_state
```

```
average rate: 49.858
	min: 0.018s max: 0.023s std dev: 0.00093s window: 52
```

About 50 messages per second, one per simulator step. Stop it with `Ctrl` + `C`.

## Step 7: Move the robot by hand

You can publish a message from the command line. Send one arm command:

```bash
ros2 topic pub --once /arm_commands std_msgs/msg/Float64MultiArray "{data: [45.0, 0.0, 0.0, 0.0, 0.0, 100.0]}"
```

```
publisher: beginning loop
publishing #1: std_msgs.msg.Float64MultiArray(layout=std_msgs.msg.MultiArrayLayout(dim=[], data_offset=0), data=[45.0, 0.0, 0.0, 0.0, 0.0, 100.0])
```

In the simulator window the arm turns 45 degrees and the gripper opens. Check it with `ros2 topic echo --once /arm_state`.

Now drive the base. Publish a base command 10 times per second:

```bash
ros2 topic pub -r 10 /base_commands std_msgs/msg/Float64MultiArray "{data: [-0.1, 0.0, 0.0]}"
```

The robot drives backwards at 0.1 m/s. Press `Ctrl` + `C`: the robot stops within half a second.

That is a safety feature of `sim_node`, copied from the real robot: an **arm** command is a position and is held, but a **base** command is a velocity and expires after 0.5 s unless it is repeated. A program that crashes can therefore never leave the robot driving.

## Step 8: Send something wrong

```bash
ros2 topic pub --once /arm_commands std_msgs/msg/Float64MultiArray "{data: [1.0, 2.0]}"
```

Look at the terminal where `sim_node` runs:

```
[WARN] [1791554572.930501917] [sim_node]: arm_commands needs 6 values, got 2. Ignored.
```

ROS checked that the **type** was right, but it cannot know that this topic needs exactly six numbers. Checking the content is the receiving node's job.

## Step 9: Read the node

Open `~/FOR26/ros_ws/src/lekiwi_ros/lekiwi_ros/sim_node.py` in VS Code. It is about 140 lines. Find:

| Look for | What it does |
| --- | --- |
| `class SimNode(Node)` | every Python node is a class based on `Node` |
| `self.create_subscription(...)` | "call this function whenever a message arrives on this topic" |
| `self.create_publisher(...)` | "I will publish this type on this topic" |
| `self.create_timer(...)` | "call this function every so many seconds" |
| `on_timer` | one simulator step, then publish the state |
| `rclpy.spin(node)` | "now wait and handle messages and timers until stopped" |

On the next page you write a node of your own with exactly these building blocks.

Stop `sim_node` with `Ctrl` + `C`, or by closing the simulator window.

## If something went wrong

| What you see | What to do |
| --- | --- |
| `Package 'lekiwi_ros' not found` | The workspace is not sourced in this terminal. Run `source ~/FOR26/ros_ws/install/setup.bash`. |
| `ModuleNotFoundError: No module named 'lekiwi_sim'` | The conda environment is not active in this terminal. Run `conda activate ros_mujoco`. If it is active, install the simulator ([Simulation lab](../Simulate/README.md)). |
| `ros2 node list` prints nothing although a node is running | The two terminals have different `ROS_DOMAIN_ID` values, or one was opened before Step 1. Close both and open new ones. If it still happens, run `ros2 daemon stop` and try again. |
| `ERROR: could not initialize GLFW` | You started `sim_node` with the window over SSH. Add `--ros-args -p viewer:=false`. |
| You changed a `.py` file and nothing changed | You have to run `colcon build` again after every change. |
| `colcon build` created `build`, `install`, `log` in the wrong folder | Delete those three folders there and build again inside `~/FOR26/ros_ws`. |

---

Previous: [1. ROS concepts](01_ros_concepts.md) | Next: [3. Your first nodes](03_your_first_nodes.md)
