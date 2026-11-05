# 3. Create a Conda Environment with ROS and MuJoCo

In this step you create the conda environment you will use for the whole course. Inside it, Python can use both:

- **ROS 2** (the libraries you installed in step 1), and
- **MuJoCo**, a physics simulator for robots.

Time needed: about 5 minutes.

## The idea in one paragraph

ROS 2 Jazzy was built for **Python 3.12**, the Python that ships with Ubuntu 24.04. A conda environment can use the ROS libraries as long as it uses the **same Python version, 3.12**, and ROS is sourced in the terminal. So we create an environment with Python 3.12 and then add MuJoCo and a few small libraries that ROS expects to find.

## Step 1: Create the environment

Open a new terminal (`Ctrl` + `Alt` + `T`) and run:

```bash
conda create -n ros_mujoco python=3.12 -y
```

| Part | Meaning |
| --- | --- |
| `-n ros_mujoco` | the name of the new environment |
| `python=3.12` | the Python version to put in it. **This must be 3.12** to match ROS. |
| `-y` | answer yes automatically |

It ends with a message that explains how to activate the environment.

## Step 2: Activate the environment

```bash
conda activate ros_mujoco
```

Your prompt now starts with the environment name:

```
(ros_mujoco) team0@team0-MINI-S:~$
```

That `(ros_mujoco)` tells you the environment is switched on. Anything you install with `pip` now goes into this environment only.

Check that you are using the environment's Python:

```bash
python --version
```

You should see `Python 3.12` followed by another number, for example `Python 3.12.15`.

## Step 3: Install MuJoCo and the libraries ROS needs

Make sure the prompt starts with `(ros_mujoco)`, then run:

```bash
pip install mujoco "numpy==2.2.6" pyyaml lark
```

Type the quotes around `"numpy==2.2.6"` exactly as shown.

It ends with a line that begins with `Successfully installed`.

What each one is for:

| Library | Why it is needed |
| --- | --- |
| `mujoco` | the physics simulator |
| `numpy==2.2.6` | a maths library. We ask for this exact version because it is the one tested with ROS, MuJoCo and LeRobot (installed on the [next page](04_install_lerobot.md)) all together. |
| `pyyaml` | ROS uses it to read settings files. Without it, `import rclpy` fails with `No module named 'yaml'`. |
| `lark` | ROS uses it to read message definitions |

> No `sudo` here. Never use `sudo` with `pip` or `conda`.

## Step 4: Test MuJoCo

You will now write a short Python program. We use a simple text editor called `nano` that runs inside the terminal.

Open a new file:

```bash
nano ~/test_mujoco.py
```

Copy the code below and paste it into nano with `Ctrl` + `Shift` + `V`:

```python
import mujoco

# A tiny world: a floor and a box that starts 1 metre above it.
XML = """
<mujoco>
  <worldbody>
    <light pos="0 0 3"/>
    <geom type="plane" size="2 2 0.1"/>
    <body name="box" pos="0 0 1">
      <freejoint/>
      <geom type="box" size="0.1 0.1 0.1" rgba="0.8 0.2 0.2 1"/>
    </body>
  </worldbody>
</mujoco>
"""

model = mujoco.MjModel.from_xml_string(XML)
data = mujoco.MjData(model)

print("MuJoCo version:", mujoco.__version__)
print("Box height at start:", round(data.qpos[2], 3), "m")

# Simulate 1 second of physics.
while data.time < 1.0:
    mujoco.mj_step(model, data)

print("Box height after 1 s:", round(data.qpos[2], 3), "m")
```

Save and leave nano:

1. Press `Ctrl` + `O` (the letter O), then `Enter`, to save.
2. Press `Ctrl` + `X` to exit.

Run the program:

```bash
python ~/test_mujoco.py
```

You should see:

```
MuJoCo version: 3.15.0
Box height at start: 1.0 m
Box height after 1 s: 0.1 m
```

The box started 1 m above the floor, fell, and came to rest on the floor (its centre is 0.1 m up because the box is 0.2 m tall). MuJoCo works. Your version number may be newer.

## Step 5: See the simulation in 3D

> Do this step **sitting at the lab computer**, not over SSH. It opens a window, and windows cannot be shown through an SSH connection (see [page 6](06_ssh_and_remote_development.md)).

Create a second file:

```bash
nano ~/test_viewer.py
```

Paste this code, then save with `Ctrl` + `O`, `Enter`, and exit with `Ctrl` + `X`:

```python
import time
import mujoco
import mujoco.viewer

XML = """
<mujoco>
  <worldbody>
    <light pos="0 0 3"/>
    <geom type="plane" size="2 2 0.1"/>
    <body name="box" pos="0 0 1">
      <freejoint/>
      <geom type="box" size="0.1 0.1 0.1" rgba="0.8 0.2 0.2 1"/>
    </body>
  </worldbody>
</mujoco>
"""

model = mujoco.MjModel.from_xml_string(XML)
data = mujoco.MjData(model)

# Open a 3D window and run the simulation in real time until you close it.
with mujoco.viewer.launch_passive(model, data) as viewer:
    while viewer.is_running():
        mujoco.mj_step(model, data)
        viewer.sync()
        time.sleep(model.opt.timestep)
```

Run it:

```bash
python ~/test_viewer.py
```

A window opens showing a red box falling onto the floor. Drag with the left mouse button to rotate the view, and scroll to zoom. Close the window to stop the program.

## Step 6: Test ROS and MuJoCo together

This is the real test: one Python program that uses **both** libraries. It simulates a falling ball in MuJoCo and publishes the ball's height on a ROS topic.

Create the file:

```bash
nano ~/test_ros_mujoco.py
```

Paste this code, then save with `Ctrl` + `O`, `Enter`, and exit with `Ctrl` + `X`:

```python
import mujoco
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64

# A tiny world: a floor and a ball that starts 1 metre above it.
XML = """
<mujoco>
  <worldbody>
    <light pos="0 0 3"/>
    <geom type="plane" size="2 2 0.1"/>
    <body name="ball" pos="0 0 1">
      <freejoint/>
      <geom type="sphere" size="0.1" rgba="0.8 0.2 0.2 1"/>
    </body>
  </worldbody>
</mujoco>
"""


class BallSimulator(Node):
    def __init__(self):
        super().__init__("ball_simulator")
        self.model = mujoco.MjModel.from_xml_string(XML)
        self.data = mujoco.MjData(self.model)
        self.publisher = self.create_publisher(Float64, "ball_height", 10)
        # Call self.step 10 times per second.
        self.timer = self.create_timer(0.1, self.step)

    def step(self):
        # Drop the ball again every 2 seconds, so the numbers keep changing.
        if self.data.time >= 2.0:
            mujoco.mj_resetData(self.model, self.data)

        # Advance the MuJoCo simulation by 0.1 seconds.
        target_time = self.data.time + 0.1
        while self.data.time < target_time:
            mujoco.mj_step(self.model, self.data)

        # Publish the height of the ball on a ROS topic.
        msg = Float64()
        msg.data = float(self.data.qpos[2])
        self.publisher.publish(msg)
        self.get_logger().info(f"t = {self.data.time:.1f} s, ball height = {msg.data:.3f} m")


def main():
    rclpy.init()
    node = BallSimulator()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
```

Run it (the prompt must start with `(ros_mujoco)`):

```bash
python ~/test_ros_mujoco.py
```

You should see a new line ten times per second:

```
[INFO] [1791513200.304316386] [ball_simulator]: t = 0.1 s, ball height = 0.950 m
[INFO] [1791513200.387327207] [ball_simulator]: t = 0.2 s, ball height = 0.802 m
[INFO] [1791513200.487238851] [ball_simulator]: t = 0.3 s, ball height = 0.556 m
```

Leave it running. Open a **second terminal** and listen to the topic with a ROS tool:

```bash
ros2 topic echo /ball_height
```

You should see the ball heights arriving, one message at a time:

```
data: 0.0996328165334239
---
data: 0.09963281816362318
---
```

The numbers go from about `0.95` down to about `0.1` and then start again, because the ball is dropped again every 2 seconds.

This proves the whole chain works: Python from your conda environment runs MuJoCo, talks to ROS, and other ROS programs receive the data.

Press `Ctrl` + `C` in both terminals to stop.

## What to do every time you start working

In every new terminal, before running your Python code:

```bash
conda activate ros_mujoco
```

ROS is already sourced automatically (you set that up in step 1). The environment is not activated automatically, so this one command is needed each time.

To leave the environment:

```bash
conda deactivate
```

## If something went wrong

| What you see | What to do |
| --- | --- |
| `ModuleNotFoundError: No module named 'rclpy'` | ROS is not sourced in this terminal. Run `echo $ROS_DISTRO`. If it is empty, go back to [step 1](01_install_ros2.md), Step 6. |
| `ModuleNotFoundError: No module named 'yaml'` | Repeat Step 3 with `(ros_mujoco)` showing in the prompt. |
| `ModuleNotFoundError: No module named 'mujoco'` | The environment is not active. Run `conda activate ros_mujoco`, and repeat Step 3 if needed. |
| A long warning that starts with `A module that was compiled using NumPy 1.x cannot be run in NumPy 2.2.6` when you `import cv_bridge` | Known limitation: the ROS camera-image helper `cv_bridge` was built for NumPy 1. Nothing else in this guide is affected. Tell your TA if you need `cv_bridge`. |
| An error that mentions `_rclpy_pybind11` | The environment does not use Python 3.12. Run `python --version`. If it is not 3.12, delete the environment with `conda deactivate` then `conda env remove -n ros_mujoco -y`, and start this page again. |
| `ERROR: could not initialize GLFW` | You ran the viewer over SSH. Run it in a terminal on the lab computer's own screen. |
| The prompt does not show `(ros_mujoco)` | Run `conda activate ros_mujoco`. |

---

Previous: [2. Install conda](02_install_conda.md) | Next: [4. Install LeRobot](04_install_lerobot.md)
