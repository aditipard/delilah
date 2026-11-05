# 5. Launch Files

So far you started every node in its own terminal with `ros2 run`. A **launch file** starts several nodes with one command, with their parameters already set.

## Run one

The package `lekiwi_ros` has a launch file that starts the simulator and the leader arm node together, which is the whole of the [previous page](04_teleop_in_sim.md) in one line:

```bash
conda activate ros_mujoco
cd ~/FOR26/ros_ws
source install/setup.bash
ros2 launch lekiwi_ros teleop_sim.launch.py port:=/dev/serial/by-id/usb-1a86_USB_Single_Serial_5B8E116010-if00
```

Use your own leader arm's port. Both nodes start in this terminal, and each line they print is labelled with the node it comes from. `Ctrl` + `C` stops them all.

The words after the file name are **launch arguments**, written `name:=value`. This launch file has three:

| Argument | Meaning | Default |
| --- | --- | --- |
| `port` | the leader arm's serial port | none, you must give it |
| `scene` | `cubes`, `keyboard` or `empty` | `cubes` |
| `viewer` | `true` or `false` | `true` |

To see a launch file's arguments without starting it:

```bash
ros2 launch lekiwi_ros teleop_sim.launch.py --show-args
```

## Read one

Open `~/FOR26/ros_ws/src/lekiwi_ros/launch/teleop_sim.launch.py`. A launch file is a Python file with one function, `generate_launch_description`, that returns a list.

```python
def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument("port", description="serial port of the leader arm"),
        DeclareLaunchArgument("scene", default_value="cubes"),

        Node(package="lekiwi_ros", executable="sim_node", output="screen",
             parameters=[{"scene": LaunchConfiguration("scene")}]),
        Node(package="lekiwi_ros", executable="leader_node", output="screen",
             parameters=[{"port": LaunchConfiguration("port")}]),
    ])
```

| Piece | Meaning |
| --- | --- |
| `DeclareLaunchArgument("name", default_value=...)` | an argument that can be set on the command line |
| `LaunchConfiguration("name")` | "the value of that argument", to be filled in when the launch file runs |
| `Node(package=..., executable=...)` | start a node, exactly like `ros2 run package executable` |
| `parameters=[{...}]` | the node's parameters, like `--ros-args -p name:=value` |
| `output="screen"` | show what the node prints in this terminal |

## Where launch files live

A launch file belongs to a package. It sits in the package's `launch` folder, and the package's `setup.py` has one line that installs everything in that folder:

```python
("share/" + package_name + "/launch", glob("launch/*.launch.py")),
```

Because launch files are **installed** by the build, you must run `colcon build` after changing one, just as for a node.

## Your turn

In the [Kinematics guide](../Kinematics/03_keyboard_typing.md) you complete a launch file of your own, which starts the simulator together with the three nodes you write there.

---

Previous: [4. Teleoperation in simulation](04_teleop_in_sim.md) | Back to the [overview](README.md)
