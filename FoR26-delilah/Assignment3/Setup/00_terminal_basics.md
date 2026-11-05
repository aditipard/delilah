# 0. Terminal Basics

Almost everything in this guide is done by typing commands into a **terminal**. If you have never used one, read this page first. It takes about 10 minutes.

## What is a terminal?

A terminal is a window where you type a command, press `Enter`, and the computer does it and prints the result as text. It does the same things you would do by clicking around (opening folders, installing programs), only by typing.

## Open a terminal

On the lab computer (Ubuntu), press `Ctrl` + `Alt` + `T`.

A window opens with a line that looks like this:

```
team0@team0-MINI-S:~$
```

This line is called the **prompt**. It tells you:

| Part | Meaning |
| --- | --- |
| `team0` | your username |
| `team0-MINI-S` | the name of the computer |
| `~` | the folder you are in right now (`~` is short for your home folder, `/home/team0`) |
| `$` | "I am ready, type a command" |

Your username and computer name may be different from `team0`. That is fine. Wherever this guide shows `team0`, yours will show your own name.

## How to read the commands in this guide

Commands are shown in grey boxes like this:

```bash
pwd
```

Type (or copy and paste) exactly what is in the box, then press `Enter`. **Do not type the `$` from the prompt.**

Three rules that save a lot of trouble:

1. **Run one box at a time**, and wait for the prompt to come back before running the next one.
2. **Read what the command printed.** If you see the word `error` or `E:`, stop and read it before moving on.
3. **Capital letters matter.** `Downloads` and `downloads` are two different names.

## Copy and paste in the terminal

The usual `Ctrl` + `C` and `Ctrl` + `V` do **not** work in the terminal. Use these instead:

| Action | Keys |
| --- | --- |
| Paste | `Ctrl` + `Shift` + `V` |
| Copy | `Ctrl` + `Shift` + `C` |
| Stop a running command | `Ctrl` + `C` |

## The commands you need

Try each of these now.

**Where am I?**

```bash
pwd
```

It prints your current folder, for example `/home/team0`.

**What is in this folder?**

```bash
ls
```

It prints the files and folders, for example `Desktop  Documents  Downloads ...`.

**Go into a folder** (`cd` = change directory)

```bash
cd Downloads
```

The prompt changes to `~/Downloads$` to show you moved.

**Go back up one folder**

```bash
cd ..
```

**Go home from anywhere**

```bash
cd ~
```

**Make a new folder**

```bash
mkdir my_first_folder
```

**Show the contents of a text file**

```bash
cat ~/.bashrc
```

## Useful tricks

- Press the `Up` arrow to bring back the previous command, so you do not need to retype it.
- Press `Tab` to auto-complete a name. Type `cd Dow` then press `Tab`, and it becomes `cd Downloads/`.
- Type `clear` to clean the screen.

## `sudo`: doing things as administrator

Installing software changes the whole computer, so Ubuntu asks for administrator rights. You get them by putting `sudo` in front of a command:

```bash
sudo apt update
```

The first time, it asks:

```
[sudo] password for team0:
```

Type the password of your account and press `Enter`.

> **Nothing appears on the screen while you type the password**, not even dots. This is normal. Just type it and press `Enter`.

Only use `sudo` when this guide tells you to. In particular, **never use `sudo` with `conda` or `pip`**.

## `apt`: Ubuntu's app store for the terminal

`apt` is the program that downloads and installs software on Ubuntu. You will see two forms of it:

| Command | What it does |
| --- | --- |
| `sudo apt update` | refreshes the list of software that is available (installs nothing) |
| `sudo apt install NAME` | downloads and installs the program called `NAME` |

When `apt` asks `Do you want to continue? [Y/n]`, type `y` and press `Enter`.

## "Open a new terminal"

Several steps in this guide end with **"close the terminal and open a new one"**. Some settings are only read when a terminal starts, so a terminal that is already open does not notice the change. Closing it and pressing `Ctrl` + `Alt` + `T` again is the simplest way to pick up the new settings.

---

Next: [1. Install ROS 2](01_install_ros2.md)
