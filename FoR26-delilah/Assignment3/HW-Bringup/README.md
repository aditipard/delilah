# Hardware Bring-Up

This guide takes you from a box of parts to a robot you can control from the computer, without ROS. You connect the hardware, check every motor, calibrate the arms, and then drive the robot by hand.

Do the [Setup guide](../Setup/README.md) first. Then follow these pages **in order**.

| # | Page | What you get |
| --- | --- | --- |
| 1 | [Wiring the robot](01_wiring.md) | Power, USB and servo cables connected; the computer sees both controller boards |
| 2 | [Check the servos](02_check_servos.md) | Permission to use the boards; every servo answers; you know which board is LeKiwi and which is the leader arm |
| 3 | [Calibration](03_calibration.md) | A calibration file for the leader arm, recovered from its servos or measured again; calibration of LeKiwi's arm |
| 4 | [The real robot in ROS](04_robot_node.md) | `robot_node`: reading the real arm from ROS, and (with care) driving it |

## Safety rules for all pages

1. **Never connect the 12 V power supply to the leader arm.** Its motors are 7.4 V motors.
2. **Power off before plugging or unplugging any servo cable.**
3. **Keep the robot on blocks**, wheels off the ground, until a page tells you otherwise.
4. **Keep a hand near the power switch** whenever something is about to move for the first time. It is the only emergency stop that works even if the software has frozen.
5. **One program per controller board.** Stop one program before starting another on the same board.

## The robot at a glance

| Part | Servos | Power | IDs |
| --- | --- | --- | --- |
| LeKiwi follower arm | 6 | 12 V | 1 to 6 |
| LeKiwi base (wheels) | 3 | 12 V | 7 to 9 |
| Leader arm | 6 | 5 V | 1 to 6 |

## Files in this folder

| File | What it is |
| --- | --- |
| [`images/lekiwi_wiring_diagram.png`](images/lekiwi_wiring_diagram.png) | The wiring diagram used on page 1 |
| [`scripts/check_servos.py`](scripts/check_servos.py) | The read-only servo check used on page 2 |
| [`config/lekiwi_nocam.yaml`](config/lekiwi_nocam.yaml) | LeKiwi settings without cameras, used on page 3 |
| [`scripts/recover_calibration.py`](scripts/recover_calibration.py) | Rebuilds a calibration file (leader arm or LeKiwi) from the servos, used on pages 3 and 4 |
