# 4. Install LeRobot

## What is LeRobot?

**LeRobot** is a Python library from Hugging Face for low-cost robots. In this course it is the layer that talks to the robot's hardware: it sends commands to the servo motors of the arm and the wheels, reads their positions back, handles calibration, and reads the cameras.

You install it into the **same** `ros_mujoco` environment from the previous page. That way one Python can use ROS, MuJoCo and LeRobot together, which is what the later labs need.

This page only installs the software. You do **not** need the robot connected.

Time needed: about 10 minutes, mostly downloads (about 2.5 GB of disk).

## Step 1: Activate the environment

Open a terminal (`Ctrl` + `Alt` + `T`) and run:

```bash
conda activate ros_mujoco
```

The prompt must start with `(ros_mujoco)` for every command on this page.

## Step 2: Install FFmpeg

**FFmpeg** is a tool for reading and writing video. LeRobot uses it for camera recordings.

```bash
conda install -c conda-forge ffmpeg=7.1.1 -y
```

| Part | Meaning |
| --- | --- |
| `conda install` | install a package into the active environment |
| `-c conda-forge` | get it from the conda-forge collection |
| `ffmpeg=7.1.1` | this exact version, the one LeRobot's video decoder was tested with |
| `-y` | answer yes automatically |

Check it:

```bash
ffmpeg -version
```

The first line of the output should start with:

```
ffmpeg version 7.1.1
```

> This is the one place in this guide where `conda install` is used instead of `pip install`. FFmpeg is not a Python library, so `pip` cannot provide it.

## Step 3: Install LeRobot

This is one long command. Copy all of it, paste it with `Ctrl` + `Shift` + `V`, and press `Enter`:

```bash
pip install "lerobot[core_scripts,feetech,lekiwi] @ git+https://github.com/huggingface/lerobot.git@1bc0bdfb20ad4f4f76dc8a68a0e0746d54f50de9" --extra-index-url https://download.pytorch.org/whl/cpu
```

It takes one to two minutes and ends with a line that begins with `Successfully installed`.

What the parts of this command mean:

| Part | Meaning |
| --- | --- |
| `lerobot[...]` | install LeRobot plus the optional parts listed inside the brackets |
| `core_scripts` | the `lerobot-...` command-line tools (calibrate, teleoperate, and others) |
| `feetech` | support for the Feetech servo motors used in our robot |
| `lekiwi` | support for the LeKiwi mobile robot |
| `@ git+https://github.com/...` | download LeRobot straight from its GitHub repository |
| `@1bc0bdf...` | the exact revision of the code to use, so everyone in the course has the same one. It reports itself as version 0.6.2. |
| `--extra-index-url .../whl/cpu` | use the CPU version of PyTorch. The default version includes about 3 GB of files for NVIDIA graphics cards, which the lab computer does not have. |

## Step 4: Check the installation

Run these three checks one at a time.

**Check 1: no conflicting packages**

```bash
pip check
```

You should see:

```
No broken requirements found.
```

**Check 2: LeRobot reports its setup**

```bash
lerobot-info
```

The output should start like this:

```
- LeRobot version: 0.6.2
- Platform: Linux-7.0.0-31-generic-x86_64-with-glibc2.39
- Python version: 3.12.15
- Huggingface Hub version: 1.33.0
- Transformers version: N/A
- Datasets version: 4.8.5
- Numpy version: 2.2.6
- FFmpeg version: 7.1.1
- PyTorch version: 2.11.0+cpu
- Torchcodec version: 0.11.1+cpu
- Is PyTorch built with CUDA support?: False
```

The lines that matter are:

| Line | Must say |
| --- | --- |
| `LeRobot version` | `0.6.2` |
| `Python version` | starts with `3.12` |
| `Numpy version` | `2.2.6` |
| `FFmpeg version` | `7.1.1` |
| `PyTorch version` | ends with `+cpu` |

**Check 3: ROS, MuJoCo and LeRobot in the same Python**

```bash
python -c "import rclpy, mujoco, lerobot; print('ROS OK | MuJoCo', mujoco.__version__, '| LeRobot', lerobot.__version__)"
```

You should see:

```
ROS OK | MuJoCo 3.15.0 | LeRobot 0.6.2
```

If all three checks pass, the environment is complete.

## If something went wrong

| What you see | What to do |
| --- | --- |
| `ERROR: Could not find a version that satisfies the requirement lerobot==0.6.2` | You tried `pip install lerobot==0.6.2`. That version is not published on the Python package site. Use the full command from Step 3. |
| `lerobot-info` ends with `OSError: libavutil.so...: cannot open shared object file` | FFmpeg is missing from the environment. Do Step 2, then run `lerobot-info` again. |
| `git: command not found` during Step 3 | Run `sudo apt install -y git`, then repeat Step 3. |
| `lerobot-info: command not found` | The environment is not active, or Step 3 did not finish. Run `conda activate ros_mujoco` and repeat Step 3. |
| `PyTorch version` does not end with `+cpu` | The last part of the Step 3 command was cut off. Run `pip uninstall -y torch torchvision torchcodec`, then repeat Step 3 with the complete command. |
| The download stops with a network error | Run the same command again. Files already downloaded are reused. |
| A long warning that starts with `A module that was compiled using NumPy 1.x cannot be run in NumPy 2.2.6` when you `import cv_bridge` | Known limitation: the ROS camera-image helper `cv_bridge` was built for an older NumPy. Nothing else in this guide is affected. Tell your TA if you need `cv_bridge`. |

---

Previous: [3. Create the ROS + MuJoCo environment](03_conda_env_ros_mujoco.md) | Next: [5. Install VS Code](05_install_vscode.md)
