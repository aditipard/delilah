# 5. Install VS Code

**Visual Studio Code** (VS Code) is the editor you will write your code in. It is much more comfortable than `nano`: it colours your code, completes names as you type, shows mistakes, and has a terminal built in.

This page installs VS Code **on the lab computer**. The [next page](06_ssh_and_remote_development.md) shows how to use VS Code on your own laptop instead.

Time needed: about 5 minutes.

## Step 1: Download VS Code

Open a terminal (`Ctrl` + `Alt` + `T`) and go to your Downloads folder:

```bash
cd ~/Downloads
```

Download the installer (about 250 MB):

```bash
wget -O vscode.deb "https://code.visualstudio.com/sha/download?build=stable&os=linux-deb-x64"
```

Type the quotes around the address exactly as shown.

## Step 2: Install it

```bash
sudo apt install -y ./vscode.deb
```

The `./` in front of the file name matters. It tells `apt` to install the file in this folder.

If a blue screen asks **"Add Microsoft apt repository for Visual Studio Code?"**, make sure `<Yes>` is selected and press `Enter`. This lets Ubuntu keep VS Code up to date together with the rest of the system.

## Step 3: Check the installation

```bash
code --version
```

You should see three lines: a version number, a long code, and `x64`. For example:

```
1.141.0
2a59476c9bfcb90b3ddc372c36762471b7dfad1c
x64
```

## Step 4: Install the Python extension

VS Code is a general editor. **Extensions** add support for specific languages. Install the official Python extension:

```bash
code --install-extension ms-python.python
```

It ends with:

```
Extension 'ms-python.python' v... was successfully installed.
```

## Step 5: Open VS Code

Create a folder for your course work and open it in VS Code:

```bash
mkdir -p ~/robotics_ws
```

```bash
code ~/robotics_ws
```

VS Code opens with that folder. If it asks **"Do you trust the authors of the files in this folder?"**, click **Yes, I trust the authors**.

You can also start VS Code from the applications menu: press the `Windows` key, type `code`, and press `Enter`.

## Step 6: Tell VS Code to use your conda environment

VS Code needs to know which Python to use, so that it finds MuJoCo and ROS.

1. Create a file: click **File > New File...**, name it `hello.py`, and press `Enter` twice.
2. Press `Ctrl` + `Shift` + `P`. A search box opens at the top. This is the **Command Palette**, the place where you can run any VS Code command by name.
3. Type `Python: Select Interpreter` and press `Enter`.
4. Choose the entry that contains `ros_mujoco`. Its path is `~/miniforge3/envs/ros_mujoco/bin/python`.

The bottom-right corner of the window now shows `ros_mujoco`.

## Step 7: Run code from VS Code

Type this into `hello.py` and save with `Ctrl` + `S`:

```python
import mujoco
import rclpy

print("MuJoCo", mujoco.__version__, "and ROS are ready.")
```

Open the built-in terminal with **Terminal > New Terminal** (or `` Ctrl + ` ``). It is the same kind of terminal you have used so far, just inside the editor.

In that terminal, run:

```bash
conda activate ros_mujoco
```

```bash
python hello.py
```

You should see:

```
MuJoCo 3.15.0 and ROS are ready.
```

## If something went wrong

| What you see | What to do |
| --- | --- |
| `code: command not found` | The install in Step 2 did not finish. Run Step 2 again and read the output for a line starting with `E:`. |
| `E: Unsupported file ./vscode.deb given on commandline` | You are not in the Downloads folder. Run `cd ~/Downloads` and try again. |
| `Python: Select Interpreter` does not list `ros_mujoco` | Click the refresh arrow at the top right of the list. If it is still missing, choose **Enter interpreter path...** and type `~/miniforge3/envs/ros_mujoco/bin/python`. |
| `ModuleNotFoundError` when running `hello.py` | The terminal inside VS Code does not have the environment active. Run `conda activate ros_mujoco` in it. |

---

Previous: [4. Install LeRobot](04_install_lerobot.md) | Next: [6. SSH and remote development](06_ssh_and_remote_development.md)
