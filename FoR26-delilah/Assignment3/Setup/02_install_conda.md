# 2. Install Conda (Miniforge)

## What is conda and why do we need it?

Python projects need extra libraries (for us: MuJoCo, NumPy and others). If you install all of them straight into the computer's own Python, different projects start to conflict, and you can even break Ubuntu tools that rely on that Python.

**Conda** solves this with **environments**. An environment is a separate, self-contained folder with its own Python and its own libraries. You can create one per project, switch between them, and delete one without affecting anything else.

We install conda using **Miniforge**, a small, free installer for conda.

Time needed: about 5 minutes.

## Step 1: Download the installer

Open a terminal (`Ctrl` + `Alt` + `T`) and go to your Downloads folder:

```bash
cd ~/Downloads
```

Download the installer (about 120 MB):

```bash
wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh
```

Check that the file is there:

```bash
ls
```

You should see `Miniforge3-Linux-x86_64.sh` in the list.

## Step 2: Run the installer

```bash
bash Miniforge3-Linux-x86_64.sh -b
```

The `-b` at the end means "install with the default answers and do not ask me questions". Conda is installed into the folder `~/miniforge3`.

A lot of text scrolls by. It is done when you see:

```
installation finished.
```

> Note: there is **no `sudo`** here. Conda lives inside your home folder and never needs administrator rights.

## Step 3: Tell the terminal about conda

```bash
~/miniforge3/bin/conda init bash
```

Near the end of the output you should see:

```
modified      /home/team0/.bashrc
```

This added a few lines to a file called `.bashrc`, which the terminal reads every time it starts.

## Step 4: Stop conda from switching itself on automatically

By default, conda activates an environment called `base` in every new terminal. We turn that off, because `base` uses a different Python version than ROS and the two would clash.

```bash
~/miniforge3/bin/conda config --set auto_activate false
```

This command prints nothing. That is expected.

## Step 5: Open a new terminal and check

**Close the terminal and open a new one** (`Ctrl` + `Alt` + `T`), then run:

```bash
conda --version
```

You should see a version number, for example:

```
conda 26.7.2
```

Your number may be newer. Any number means conda is installed.

Your prompt should still look like `team0@team0-MINI-S:~$`, with **no** `(base)` in front of it.

## If something went wrong

| What you see | What to do |
| --- | --- |
| `conda: command not found` | You are still in the old terminal. Close it and open a new one. If it still fails, run Step 3 again. |
| The prompt starts with `(base)` | Run Step 4 again, then open a new terminal. |
| `wget` stops with a network error | Check the internet connection and run the `wget` command again. |

---

Previous: [1. Install ROS 2](01_install_ros2.md) | Next: [3. Create the ROS + MuJoCo environment](03_conda_env_ros_mujoco.md)
