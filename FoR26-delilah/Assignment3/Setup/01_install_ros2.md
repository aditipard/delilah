# 1. Install ROS 2

## What is ROS?

**ROS** (Robot Operating System) is a set of software libraries and tools for building robot programs. A robot program is usually split into many small programs (ROS calls them **nodes**), for example one that reads a camera, one that plans a motion and one that drives the motors. ROS is what lets those nodes send messages to each other.

We install **ROS 2 Jazzy**, the version made for Ubuntu 24.04.

Time needed: about 20 to 30 minutes, mostly waiting for downloads (about 750 MB, using about 3.5 GB of disk).

## Before you start

Check that your computer runs Ubuntu 24.04. Open a terminal (`Ctrl` + `Alt` + `T`) and run:

```bash
lsb_release -ds
```

You should see something like:

```
Ubuntu 24.04.5 LTS
```

If the number does not start with `24.04`, stop and ask your TA, because the steps below are for 24.04 only.

## Step 1: Refresh the software list and install two helper tools

```bash
sudo apt update
```

It will ask for your password. Remember that nothing shows while you type it.

```bash
sudo apt install -y software-properties-common curl
```

The `-y` means "answer yes automatically", so `apt` does not stop to ask.

## Step 2: Enable the "universe" software collection

Some packages that ROS needs live in a part of Ubuntu's software collection called `universe`. Make sure it is switched on:

```bash
sudo add-apt-repository -y universe
```

## Step 3: Tell Ubuntu where to find ROS

Ubuntu does not know about ROS by default. The next three commands download and install a small package that adds the official ROS download server to Ubuntu's list.

Copy and run each box separately.

First, look up the latest version of that small package and remember it:

```bash
export ROS_APT_SOURCE_VERSION=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest | grep -F "tag_name" | awk -F'"' '{print $4}')
```

This prints nothing. To check that it worked, run:

```bash
echo $ROS_APT_SOURCE_VERSION
```

You should see a version number such as `1.3.0`. If the line is empty, check your internet connection and run the first command again.

Next, download the package:

```bash
curl -L -o /tmp/ros2-apt-source.deb "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ROS_APT_SOURCE_VERSION}/ros2-apt-source_${ROS_APT_SOURCE_VERSION}.$(. /etc/os-release && echo ${UBUNTU_CODENAME:-${VERSION_CODENAME}})_all.deb"
```

Then install it:

```bash
sudo dpkg -i /tmp/ros2-apt-source.deb
```

You should see a line that says `Setting up ros2-apt-source ...`.

> These three commands must be run **in the same terminal**, one after another. If you close the terminal in between, start Step 3 again from the first box.

## Step 4: Update the computer

Refresh the software list again so Ubuntu sees the ROS packages:

```bash
sudo apt update
```

In the output you should now see lines that mention `packages.ros.org`.

Then bring the existing software up to date. ROS recommends this before installing:

```bash
sudo apt upgrade -y
```

This can take several minutes. Wait until the prompt comes back.

Some updates only take effect after a restart. Check whether one is needed:

```bash
ls /var/run/reboot-required
```

- If it prints `No such file or directory`, no restart is needed. Continue with Step 5.
- If it prints `/var/run/reboot-required`, you can still continue now, but restart the computer once you have finished this page (`sudo reboot`, or use the power menu at the top right of the screen).

## Step 5: Install ROS 2 Jazzy

```bash
sudo apt install -y ros-jazzy-desktop ros-dev-tools
```

| Package | What it contains |
| --- | --- |
| `ros-jazzy-desktop` | ROS itself, example programs, and visual tools such as RViz |
| `ros-dev-tools` | tools for building your own ROS packages, such as `colcon` |

This is the long step: more than 1000 small packages are downloaded and installed. Expect 10 to 20 minutes. It is finished when the prompt (`$`) comes back.

## Step 6: Switch ROS on in every terminal

ROS is now on the disk in `/opt/ros/jazzy`, but a terminal does not use it until you run its setup file. This is called **sourcing** ROS:

```bash
source /opt/ros/jazzy/setup.bash
```

You would have to type that in every new terminal. To make it automatic, add the line to the end of your `.bashrc` file, which the terminal reads each time it starts:

```bash
echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
```

> Run this `echo` command **only once**. Running it again adds the same line a second time.

Now **close the terminal and open a new one**.

## Step 7: Check that ROS works

In the new terminal, run:

```bash
echo $ROS_DISTRO
```

You should see:

```
jazzy
```

Now run a real example with two nodes talking to each other. You need **two terminals** open side by side.

In terminal 1, start a node that sends messages:

```bash
ros2 run demo_nodes_cpp talker
```

It prints a new line every second:

```
[INFO] [1791513065.895006335] [talker]: Publishing: 'Hello World: 1'
[INFO] [1791513066.895182863] [talker]: Publishing: 'Hello World: 2'
```

In terminal 2, start a node that receives them:

```bash
ros2 run demo_nodes_py listener
```

It prints:

```
[INFO] [1791513066.913343097] [listener]: I heard: [Hello World: 2]
[INFO] [1791513067.897728407] [listener]: I heard: [Hello World: 3]
```

The long number in each line is a timestamp, so yours will be different.

If the listener hears the talker, ROS is installed and working. Press `Ctrl` + `C` in each terminal to stop the nodes.

## If something went wrong

| What you see | What to do |
| --- | --- |
| `ros2: command not found` | ROS is not sourced in this terminal. Run `source /opt/ros/jazzy/setup.bash`, or open a new terminal after Step 6. |
| `E: Unable to locate package ros-jazzy-desktop` | Step 3 did not finish. Repeat Step 3 and Step 4. |
| `E: Could not get lock /var/lib/dpkg/lock-frontend` | Ubuntu is installing updates in the background. Wait a few minutes and run the command again. |
| `echo $ROS_DISTRO` prints an empty line | The line was not added to `.bashrc`. Repeat Step 6 and open a new terminal. |
| The download stops with a network error | Run the same `sudo apt install` command again. It continues where it stopped. |

---

Previous: [0. Terminal basics](00_terminal_basics.md) | Next: [2. Install conda](02_install_conda.md)
