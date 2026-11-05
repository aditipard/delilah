# Simulation

In this lab you work with a **simulated** LeKiwi robot. A simulator lets you try code without risk: nothing can break, you can reset with one line, and you do not need the robot on your desk.

You first learn how the physics engine **MuJoCo** works, then you use a ready-made Python class, `LeKiwiSim`, that wraps MuJoCo into a few simple calls: read the state, send a command, step, take a picture.

![The simulated scene](images/scene.png)

Do the [Setup guide](../Setup/README.md) first. Then follow these pages in order.

| # | Page | What you learn |
| --- | --- | --- |
| 0 | [Get the simulator](#get-the-simulator) (below) | Download the course code and install the simulator |
| 1 | [What is MuJoCo?](01_what_is_mujoco.md) | Model and data, the MJCF file format, stepping, actuators |
| 2 | [The LeKiwi model](02_the_lekiwi_model.md) | What is inside the robot model: joints, motors, units |
| 3 | [The simulator class](03_the_simulator_class.md) | `LeKiwiSim`: `get_state`, `set_command`, `step`, `get_image`, the viewer |
| 4 | [Pick and place](04_pick_and_place.md) | A complete example: move a cube from the table to a shelf |
| 5 | [MJX and faster simulation](05_mjx.md) | What MJX is, when you would need it, and where to read more |

## Get the simulator

The simulator lives in the course repository, in the folder `lekiwi_sim`. The robot's 3-D model is a separate repository that is pulled in as a **git submodule**, which is why the clone command has an extra option.

Open a terminal and download the repository into your home folder:

```bash
cd ~
git clone --recurse-submodules https://github.com/Rooholla-KhorramBakht/FOR26.git
```

This creates the folder `~/FOR26`.

If you already cloned it without `--recurse-submodules`, fetch the robot model like this:

```bash
cd ~/FOR26
git submodule update --init
```

Now install the simulator into your environment:

```bash
conda activate ros_mujoco
cd ~/FOR26
pip install -e .
```

The last line of the output should be:

```
Successfully installed lekiwi_sim-0.1.0
```

The `-e` means "editable": Python uses the files in `~/FOR26/lekiwi_sim` directly, so if you change them, the change takes effect the next time you run a program.

Check that it works:

```bash
python -c "from lekiwi_sim import LeKiwiSim; sim = LeKiwiSim(); print(sim.get_state()['arm_position'])"
```

You should see six numbers, the arm's start position:

```
[-0. -0. -0. -0. -0. 50.]
```

## The example programs

All example programs are in [`scripts`](scripts). Run them from that folder:

```bash
conda activate ros_mujoco
cd ~/FOR26/Assignment3/Simulate/scripts
python 01_pendulum.py
```

| Program | Page | Needs a monitor? |
| --- | --- | --- |
| [`01_pendulum.py`](scripts/01_pendulum.py) | 1 | no |
| [`02_explore_model.py`](scripts/02_explore_model.py) | 2 | no |
| [`03_hello_sim.py`](scripts/03_hello_sim.py) | 3 | no |
| [`04_viewer.py`](scripts/04_viewer.py) | 3 | **yes** |
| [`05_camera.py`](scripts/05_camera.py) | 3 | no |
| [`06_pick_and_place.py`](scripts/06_pick_and_place.py) | 4 | only with `--view` |

"Needs a monitor" means: run it in a terminal on the lab computer's own screen. Programs that open a window do not work through SSH.

## If something went wrong

| What you see | What to do |
| --- | --- |
| `FileNotFoundError: Robot model not found at ...` | The submodule was not downloaded. Run `git submodule update --init` in `~/FOR26`. |
| `ModuleNotFoundError: No module named 'lekiwi_sim'` | The environment is not active, or the install step was skipped. Run `conda activate ros_mujoco`, then `pip install -e .` in `~/FOR26`. |
| `ERROR: could not initialize GLFW` | You started a program that opens a window over SSH. Run it at the lab computer. |
