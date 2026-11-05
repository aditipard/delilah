# Lab Setup Guide

This guide takes a freshly installed Ubuntu 24.04 lab computer and turns it into a working robotics development machine. No previous experience with Linux, the terminal or ROS is needed.

Follow the pages **in order**. Each one ends with a check that tells you whether it worked, so do not move on until the check passes.

| # | Page | What you get | Time |
| --- | --- | --- | --- |
| 0 | [Terminal basics](00_terminal_basics.md) | Enough terminal knowledge to follow the rest | 10 min |
| 1 | [Install ROS 2](01_install_ros2.md) | ROS 2 Jazzy, tested with a talker and a listener | 20 to 30 min |
| 2 | [Install conda](02_install_conda.md) | Conda (Miniforge) for managing Python environments | 5 min |
| 3 | [Create the ROS + MuJoCo environment](03_conda_env_ros_mujoco.md) | A conda environment where Python can use ROS and MuJoCo together | 5 min |
| 4 | [Install LeRobot](04_install_lerobot.md) | LeRobot, the library that talks to the robot's motors, in the same environment | 10 min |
| 5 | [Install VS Code](05_install_vscode.md) | A code editor on the lab computer | 5 min |
| 6 | [SSH and remote development](06_ssh_and_remote_development.md) | Working on the lab computer from your own laptop | 15 min |

## What you need

- A lab computer with **Ubuntu 24.04** and an internet connection.
- The **username and password** of your account on it.
- For page 6: your own laptop (Windows, macOS or Linux), connected to the same network as the lab computer.

## What ends up installed

| Software | Version this guide was tested with | Where it lives |
| --- | --- | --- |
| Ubuntu | 24.04.5 LTS | |
| ROS 2 | Jazzy | `/opt/ros/jazzy` |
| Conda (Miniforge) | 26.7.2 | `~/miniforge3` |
| Conda environment `ros_mujoco` | Python 3.12 | `~/miniforge3/envs/ros_mujoco` |
| MuJoCo | 3.15.0 | inside `ros_mujoco` |
| NumPy | 2.2.6 | inside `ros_mujoco` |
| LeRobot | 0.6.2 (commit `1bc0bdf`) | inside `ros_mujoco` |
| PyTorch | 2.11.0 (CPU build) | inside `ros_mujoco` |
| FFmpeg | 7.1.1 | inside `ros_mujoco` |
| VS Code | 1.141.0 | `/usr/bin/code` |

Newer versions of conda, MuJoCo and VS Code are fine. The things that must not change are **ROS 2 Jazzy**, **Python 3.12** in the environment, **NumPy 2.2.6**, and the **LeRobot** version given on page 4.

## The short version

Once everything is installed, this is all you do at the start of each work session:

```bash
conda activate ros_mujoco
```

After that, `python` can `import rclpy`, `import mujoco` and `import lerobot`, and the `ros2` and `lerobot-*` commands work.

## Test scripts

The three test programs used on page 3 are also in the [`scripts`](scripts) folder, in case you prefer to copy the files instead of pasting the code:

| File | What it tests |
| --- | --- |
| [`test_mujoco.py`](scripts/test_mujoco.py) | MuJoCo physics, text output only |
| [`test_viewer.py`](scripts/test_viewer.py) | The MuJoCo 3D window (run at the lab computer, not over SSH) |
| [`test_ros_mujoco.py`](scripts/test_ros_mujoco.py) | ROS and MuJoCo in the same Python program |

## If you get stuck

1. Read the last few lines the terminal printed. The reason is usually written there.
2. Look at the **"If something went wrong"** table at the bottom of the page you are on.
3. Close the terminal, open a new one, and try the step again.
4. Ask your TA, and bring the exact command you ran and the exact text of the error.
