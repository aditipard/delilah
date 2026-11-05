"""Rebuild an arm's calibration file from the values stored inside its servos.

Usage: python recover_calibration.py leader <port> [name]
       python recover_calibration.py lekiwi <port> [name]

A calibration is stored in two places: inside the servos, and in a file on the computer that
LeRobot reads. If the arm was calibrated on a different computer, the file is missing here.
This program reads the values from the servos and writes the file. It does not switch the
motors on and does not move anything.
"""
import sys

from lerobot.robots.lekiwi import LeKiwi, LeKiwiConfig
from lerobot.teleoperators.so_leader import SO101Leader, SO101LeaderConfig


def make_device(kind, port, name):
    if kind == "leader":
        return SO101Leader(SO101LeaderConfig(port=port, id=name))
    return LeKiwi(LeKiwiConfig(port=port, id=name, cameras={}))


def main():
    if len(sys.argv) < 3 or sys.argv[1] not in ("leader", "lekiwi"):
        sys.exit(__doc__)
    kind, port = sys.argv[1], sys.argv[2]
    name = sys.argv[3] if len(sys.argv) > 3 else kind

    device = make_device(kind, port, name)
    device.bus.connect()
    device.calibration = device.bus.read_calibration()
    print("Calibration stored in the servos:")
    for joint, c in device.calibration.items():
        print(f"  {joint:18s} id {c.id}  homing_offset {c.homing_offset:6d}  range {c.range_min:5d} to {c.range_max:5d}")
    device._save_calibration()
    print("Saved to", device.calibration_fpath)

    # Load the file again and read the arm once, without switching any motor on.
    device.bus.disconnect(False)
    device = make_device(kind, port, name)
    device.bus.connect()
    print("File matches the servos:", device.bus.is_calibrated)
    arm = [m for m in device.bus.motors if "wheel" not in m]
    pose = device.bus.sync_read("Present_Position", arm)
    print("Pose now:", {joint.removeprefix("arm_"): round(float(value), 1) for joint, value in pose.items()})
    device.bus.disconnect(False)


if __name__ == "__main__":
    main()
