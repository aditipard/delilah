# 2. Check the Servos

On the previous page you made sure the computer can see the two controller **boards**. On this page the computer talks to every **servo** behind them for the first time.

You will:

1. allow your user account to use the boards,
2. stop an Ubuntu background service from disturbing them,
3. run a small program that asks every servo for its voltage and temperature,
4. find out which board is LeKiwi and which is the leader arm.

Everything here is **read-only**. No motor is switched on and nothing moves.

Time needed: about 15 minutes.

Before you start: the robot is wired and powered as on the [previous page](01_wiring.md), both USB cables are plugged in, and the [Setup guide](../Setup/README.md) is complete, including [LeRobot](../Setup/04_install_lerobot.md).

## Step 1: Allow your user to use the boards

Ubuntu shows each controller board as a **serial port**, a device file such as `/dev/ttyACM0`. For safety, only members of a user group called `dialout` may use serial ports, and your account is not in that group yet.

Add yourself to the group:

```bash
sudo usermod -aG dialout $USER
```

This prints nothing. `$USER` is filled in automatically with your username.

Group changes only take effect at the next login, so restart the computer:

```bash
sudo reboot
```

The motors stay powered during the restart and nothing moves.

After you have logged in again, open a terminal and check:

```bash
groups
```

The list must now contain `dialout`, for example:

```
team0 adm dialout cdrom sudo dip plugdev users lpadmin lxd
```

## Step 2: Stop Ubuntu from disturbing the boards

Ubuntu runs a background service called ModemManager. Whenever a new serial device is plugged in, it sends test commands to it, to find out whether it is a phone modem. Our boards are not modems, and those test commands can confuse the servos.

The following command creates a small rule file that tells ModemManager to leave our boards alone. Copy the whole line:

```bash
echo 'SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="55d3", ENV{ID_MM_DEVICE_IGNORE}="1"' | sudo tee /etc/udev/rules.d/99-servo-boards.rules
```

It prints the rule back to you. The numbers `1a86` and `55d3` identify the USB chip on our controller boards.

Now tell Ubuntu to load the new rule and apply it to the boards that are already plugged in:

```bash
sudo udevadm control --reload
```

```bash
sudo udevadm trigger
```

Check that the rule is active:

```bash
udevadm info -q property -n /dev/ttyACM0 | grep ID_MM
```

The output must contain this line:

```
ID_MM_DEVICE_IGNORE=1
```

## Step 3: Create the servo check program

List the two boards again:

```bash
ls /dev/serial/by-id/
```

You should see the two names from the previous page, for example:

```
usb-1a86_USB_Single_Serial_5B8E116010-if00
usb-1a86_USB_Single_Serial_5B8E116601-if00
```

Now create a small Python program that checks all servos on one board:

```bash
nano ~/check_servos.py
```

Paste the code below with `Ctrl` + `Shift` + `V`. Then save with `Ctrl` + `O`, `Enter`, and exit with `Ctrl` + `X`.

```python
"""Read-only health check of every servo on one controller board.

Usage: python check_servos.py <port>

It pings servo IDs 1 to 9 and prints each one's supply voltage and temperature.
It never switches a motor on, so nothing moves.
"""
import sys

import scservo_sdk as scs

BAUDRATE = 1_000_000
ADDR_VOLTAGE = 62      # Present_Voltage, in units of 0.1 V
ADDR_TEMPERATURE = 63  # Present_Temperature, in degrees Celsius
PINGS = 20


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    port = scs.PortHandler(sys.argv[1])
    if not port.openPort():
        sys.exit(f"Could not open {sys.argv[1]}")
    port.setBaudRate(BAUDRATE)
    packet = scs.PacketHandler(0)

    print(" ID  replies  voltage  temperature")
    found = 0
    for servo_id in range(1, 10):
        replies = sum(packet.ping(port, servo_id)[1] == scs.COMM_SUCCESS for _ in range(PINGS))
        if replies == 0:
            print(f"{servo_id:3d}  no reply")
            continue
        found += 1
        volts = packet.read1ByteTxRx(port, servo_id, ADDR_VOLTAGE)[0] / 10
        temp = packet.read1ByteTxRx(port, servo_id, ADDR_TEMPERATURE)[0]
        print(f"{servo_id:3d}  {replies:2d}/{PINGS}    {volts:4.1f} V   {temp:3d} C")
    port.closePort()
    print(f"{found} servos found")


if __name__ == "__main__":
    main()
```

The same file is in this folder as [`scripts/check_servos.py`](scripts/check_servos.py).

What the program does: for each servo ID from 1 to 9 it sends 20 "are you there?" messages (called **pings**) and counts the replies. For every servo that answers, it reads two values the servo measures itself: the voltage it is supplied with and its temperature.

## Step 4: Check the first board

Activate the environment:

```bash
conda activate ros_mujoco
```

Run the program on the **first** name from your list. Type `python ~/check_servos.py /dev/serial/by-id/usb` and press `Tab` twice to see the names, then complete the one you want:

```bash
python ~/check_servos.py /dev/serial/by-id/usb-1a86_USB_Single_Serial_5B8E116010-if00
```

Replace the name with **your own** first board's name.

On our robot this board answered:

```
 ID  replies  voltage  temperature
  1  20/20     5.5 V    26 C
  2  20/20     5.5 V    25 C
  3  20/20     5.5 V    26 C
  4  20/20     5.4 V    24 C
  5  20/20     5.4 V    26 C
  6  20/20     5.5 V    28 C
  7  no reply
  8  no reply
  9  no reply
6 servos found
```

Six servos at about 5 V: this board is the **leader arm**.

## Step 5: Check the second board

Run the program again with the **second** name:

```bash
python ~/check_servos.py /dev/serial/by-id/usb-1a86_USB_Single_Serial_5B8E116601-if00
```

On our robot this board answered:

```
 ID  replies  voltage  temperature
  1  20/20    12.5 V    30 C
  2  20/20    12.5 V    29 C
  3  20/20    12.5 V    29 C
  4  20/20    12.5 V    30 C
  5  20/20    12.5 V    30 C
  6  20/20    12.5 V    30 C
  7  20/20    12.6 V    29 C
  8  20/20    12.5 V    31 C
  9  20/20    12.5 V    30 C
9 servos found
```

Nine servos at about 12 V: this board is **LeKiwi** (six arm servos plus three wheel servos).

## Step 6: Read the results

Compare your two outputs with this table.

| What to check | Leader arm | LeKiwi |
| --- | --- | --- |
| Servos found | 6 (IDs 1 to 6) | 9 (IDs 1 to 9) |
| Voltage | about 5 V | about 12 V |
| Replies | `20/20` on every line | `20/20` on every line |
| Temperature | near room temperature, 20 to 40 C | near room temperature, 20 to 40 C |

> **If the board with 6 servos shows about 12 V, turn the power switch off and unplug both power supplies immediately.** The leader arm is connected to the wrong supply. Go back to the [wiring page](01_wiring.md) and call your TA.

## Step 7: Write down which board is which

Fill in this table for your robot and keep it. Every later page needs these two names.

| Board | Name under `/dev/serial/by-id/` |
| --- | --- |
| Leader arm (6 servos, about 5 V) | |
| LeKiwi (9 servos, about 12 V) | |

Always use these long names, never the short `/dev/ttyACM0` and `/dev/ttyACM1`. The short names are handed out in the order the boards are plugged in, so they can swap. On our robot the leader arm happened to be `ttyACM0`, and it could just as well be the other way round next time.

## One program per board

A controller board can only talk to **one program at a time**. If two programs use the same board at once, their messages collide and both get garbage. Always stop one program (`Ctrl` + `C`) before starting another one on the same board.

## Checkpoint

You are done with this page when:

- [ ] `groups` shows `dialout`,
- [ ] the leader arm's board reports 6 servos at about 5 V,
- [ ] LeKiwi's board reports 9 servos at about 12 V,
- [ ] every line shows `20/20` replies,
- [ ] you have written down which name belongs to which board.

## If something went wrong

| What you see | What to do |
| --- | --- |
| `Permission denied: '/dev/serial/by-id/...'` | Your account is not in the `dialout` group yet, or you have not restarted since adding it. Run `groups`. If `dialout` is missing, repeat Step 1. |
| `No such file or directory: '/dev/...'` | The name is mistyped, or that board's USB cable is unplugged. Run `ls /dev/serial/by-id/` and copy the name from there. |
| `ModuleNotFoundError: No module named 'scservo_sdk'` | The environment is not active. Run `conda activate ros_mujoco`. |
| `0 servos found` | The board gets no motor power, or the servo cable from the board to the first servo is loose. Check the power supply, the power switch, and that cable. USB alone powers only the board's USB chip, not the servos. |
| Some IDs say `no reply` that should answer (for example 1 to 4 answer, 5 and 6 do not) | A servo cable is loose after the last servo that answers. Power off, push every plug in firmly, power on, run the check again. |
| Only ID 1 answers, or far fewer servos than expected | The servos may be brand new. New servos all have ID 1, so their replies collide. They need a one-time ID setup. Ask your TA. |
| Fewer than `20/20` replies on a line | A loose plug or a damaged cable near that servo. Power off and reseat its cables. |
| A temperature well above 40 C while nothing is moving | Power off and call your TA. |

---

Previous: [1. Wiring the robot](01_wiring.md) | Next: [3. Calibration](03_calibration.md)
