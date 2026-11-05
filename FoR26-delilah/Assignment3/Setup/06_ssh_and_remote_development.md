# 6. SSH and Remote Development from Your Laptop

So far you have been sitting at the lab computer. This page shows how to work on it **from your own laptop**, without touching its keyboard or screen.

## What is SSH?

**SSH** (Secure Shell) is a way to open a terminal on another computer over the network. You type on your laptop, but the commands run on the lab computer and the results are sent back to your screen. Everything that travels between the two is encrypted.

Two words used on this page:

| Word | Meaning here |
| --- | --- |
| **local** | your own laptop |
| **remote** | the lab computer you connect to |

To connect you need three things:

1. Your laptop and the lab computer are on the **same network** (the lab Wi-Fi or router).
2. The **username** on the lab computer (for example `team0`) and its password.
3. The **IP address** of the lab computer, which is its address on the network (for example `192.168.123.222`).

## Part A: Prepare the lab computer (do this once, at the lab computer)

### A1. Make sure the SSH server is installed and running

Open a terminal on the lab computer and run:

```bash
sudo apt install -y openssh-server
```

```bash
sudo systemctl enable --now ssh
```

If it was already installed, these commands change nothing and are safe to run.

Check that it is running:

```bash
systemctl is-active ssh
```

You should see:

```
active
```

### A2. Find the IP address and username

```bash
hostname -I
```

It prints the IP address, for example:

```
192.168.123.222
```

If it prints more than one address, use the first one.

```bash
whoami
```

It prints your username, for example `team0`.

Write both down. In the rest of this page, replace `team0` and `192.168.123.222` with **your own** values.

> The IP address can change if the computer reconnects to the network. If SSH suddenly stops working one day, run `hostname -I` on the lab computer again and check whether the address is still the same.

## Part B: Connect from your laptop

### B1. Open a terminal on your laptop

| Laptop | How to open a terminal |
| --- | --- |
| Windows 10 or 11 | Press the `Windows` key, type `PowerShell`, press `Enter` |
| macOS | Press `Cmd` + `Space`, type `Terminal`, press `Enter` |
| Linux | Press `Ctrl` + `Alt` + `T` |

All three already have the `ssh` program installed.

### B2. Connect

```bash
ssh team0@192.168.123.222
```

The pattern is always `ssh USERNAME@IP_ADDRESS`.

The **first time** you connect to a computer, SSH asks whether you trust it:

```
The authenticity of host '192.168.123.222' can't be established.
ED25519 key fingerprint is SHA256:...
Are you sure you want to continue connecting (yes/no/[fingerprint])?
```

Type `yes` and press `Enter`. You are asked this only once per computer.

Then it asks for the password of the `team0` account on the lab computer. Type it and press `Enter` (nothing shows while you type).

When it works, your prompt changes to the lab computer's prompt:

```
team0@team0-MINI-S:~$
```

You are now typing on the lab computer. Try it:

```bash
hostname
```

It prints the name of the lab computer, not of your laptop.

Everything from the previous pages works here, for example:

```bash
conda activate ros_mujoco
python ~/test_ros_mujoco.py
```

### B3. Disconnect

```bash
exit
```

The prompt goes back to your laptop's prompt.

## Part C: Log in without typing the password (SSH keys)

Typing the password on every connection gets tiring, and VS Code (Part D) asks for it several times. An **SSH key** fixes this. It is a pair of files on your laptop:

- a **private key**, which stays on your laptop and must never be shared, and
- a **public key**, which you copy to the lab computer.

After that, the lab computer recognises your laptop and lets you in without a password.

Run these commands **on your laptop** (not inside an SSH session).

### C1. Create a key

```bash
ssh-keygen -t ed25519
```

It asks three questions (where to save, and a passphrase twice). Press `Enter` three times to accept the defaults.

If it says a key `already exists` and asks to overwrite, answer `n`. You already have a key and can use it.

### C2. Copy the public key to the lab computer

On **macOS or Linux**:

```bash
ssh-copy-id team0@192.168.123.222
```

On **Windows (PowerShell)**:

```powershell
type $env:USERPROFILE\.ssh\id_ed25519.pub | ssh team0@192.168.123.222 "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
```

Either way, you type the lab computer password one last time.

### C3. Test it

```bash
ssh team0@192.168.123.222
```

You should now get in **without** being asked for a password.

## Part D: Use VS Code on your laptop to edit code on the lab computer

Typing commands over SSH is fine, but editing code in a terminal is not comfortable. VS Code can connect over SSH so that:

- the VS Code window runs on **your laptop**, and
- the files, the terminal and the Python that runs your code are all on the **lab computer**.

This is called **remote development**.

### D1. Install VS Code on your laptop

Download it from <https://code.visualstudio.com> and install it like any other program.

### D2. Install the Remote - SSH extension

1. Open VS Code on your laptop.
2. Click the **Extensions** icon in the left bar (four small squares), or press `Ctrl` + `Shift` + `X` (`Cmd` + `Shift` + `X` on macOS).
3. Search for `Remote - SSH`.
4. Pick the one published by **Microsoft** and click **Install**.

### D3. Connect to the lab computer

1. Press `F1` (or `Ctrl` + `Shift` + `P`, `Cmd` + `Shift` + `P` on macOS). A search box opens at the top.
2. Type `Remote-SSH: Connect to Host` and press `Enter`.
3. Choose **Add New SSH Host...**, type `ssh team0@192.168.123.222` and press `Enter`.
4. When asked which configuration file to update, pick the first one in the list.
5. Press `F1` again, run `Remote-SSH: Connect to Host`, and this time choose `192.168.123.222` from the list.
6. A new VS Code window opens. If asked for the platform, choose **Linux**. If asked for a password, type the lab computer password.

The first connection takes a minute, because VS Code installs a small helper on the lab computer.

You are connected when the **bottom-left corner** of the window shows:

```
SSH: 192.168.123.222
```

### D4. Open a folder on the lab computer

1. Click **File > Open Folder...**
2. The list shows folders **on the lab computer**. Choose `/home/team0/` (or a project folder inside it) and click **OK**.
3. If asked "Do you trust the authors of the files in this folder?", click **Yes**.

The file list on the left now shows the lab computer's files. Any file you edit and save is saved on the lab computer.

### D5. Install the Python extension on the lab computer

Extensions are installed separately for each remote computer.

1. Open the **Extensions** panel.
2. Search for `Python` (by Microsoft).
3. Click **Install in SSH: 192.168.123.222**.

### D6. Choose the conda environment

1. Open any `.py` file, for example `test_ros_mujoco.py`.
2. Press `F1`, type `Python: Select Interpreter` and press `Enter`.
3. Choose the entry that contains `ros_mujoco`.

The bottom-right corner of the window now shows `ros_mujoco`.

### D7. Run code on the lab computer

Open a terminal inside VS Code with **Terminal > New Terminal**. This terminal runs **on the lab computer**. Use it exactly like before:

```bash
conda activate ros_mujoco
python ~/test_ros_mujoco.py
```

### D8. Disconnect

Click the `SSH: ...` label in the bottom-left corner and choose **Close Remote Connection**.

## Important: windows do not come through SSH

SSH carries **text only**. A program that opens a graphical window, such as the MuJoCo viewer or RViz, cannot show that window on your laptop. If you run the viewer script over SSH you get:

```
ERROR: could not initialize GLFW
```

This is expected. The rule is:

| What you are doing | Where to do it |
| --- | --- |
| Editing code, running ROS nodes, running simulations that only print numbers | From your laptop over SSH (terminal or VS Code) |
| Anything that opens a window (MuJoCo viewer, RViz) | In a terminal on the lab computer's own screen |

A good way to work is to write and save your code from your laptop in VS Code, then start the windowed program from the lab computer's own keyboard and screen.

## If something went wrong

| What you see | What to do |
| --- | --- |
| `ssh: connect to host ... port 22: Connection timed out` | Your laptop cannot reach the lab computer. Check that both are on the same network and that the IP address is still correct (`hostname -I` on the lab computer). |
| `ssh: connect to host ... port 22: Connection refused` | The SSH server is not running on the lab computer. Repeat step A1. |
| `Permission denied, please try again.` | Wrong username or password. Check the username with `whoami` on the lab computer. |
| `WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!` | The IP address now belongs to a different computer than before, or the lab computer was reinstalled. Ask your TA before continuing. |
| VS Code keeps asking for the password | Set up an SSH key (Part C). |
| `Python: Select Interpreter` does not list `ros_mujoco` | Make sure the Python extension is installed **on the remote** (D5), then run `Developer: Reload Window` from the `F1` menu. |

---

Previous: [5. Install VS Code](05_install_vscode.md) | Back to the [overview](README.md)
