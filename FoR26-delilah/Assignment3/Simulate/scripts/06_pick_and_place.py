"""Pick the red cube from the table and put it on the left shelf, using fixed arm poses.

Usage:  python 06_pick_and_place.py           no window, prints the result (works over SSH)
        python 06_pick_and_place.py --view    also shows it in the 3-D viewer (at the lab computer)
"""
import sys

import numpy as np

from lekiwi_sim import LeKiwiSim

# (what happens, arm target [5 joints in degrees, gripper in %], seconds to get there)
WAYPOINTS = [
    ("above the cube", [-9.4, 39.7, -35.9, 100.0, 90.0, 100.0], 2.0),
    ("down to the cube", [-10.5, 47.0, -20.2, 77.4, 90.0, 100.0], 1.5),
    ("close the gripper", [-10.5, 47.0, -20.2, 77.4, 90.0, 0.0], 2.0),
    ("lift", [-9.9, 45.2, -54.7, 100.0, 90.0, 0.0], 2.0),
    ("over the shelf", [-75.5, 38.9, -63.6, 95.4, 90.0, 0.0], 3.0),
    ("lower onto the shelf", [-75.2, 54.5, -62.9, 96.0, 90.0, 0.0], 2.0),
    ("open the gripper", [-75.2, 54.5, -62.9, 96.0, 90.0, 100.0], 1.5),
    ("move away", [-75.2, 48.7, -74.6, 100.0, 90.0, 100.0], 1.5),
]

view = "--view" in sys.argv
sim = LeKiwiSim()
if view:
    sim.open_viewer()


def move_arm(target, seconds):
    """Move the arm from its current target to `target` along a straight line in joint space."""
    start = sim.get_command()["arm"]
    steps = int(seconds / sim.control_dt)
    for i in range(steps):
        sim.set_command(arm=start + (np.array(target) - start) * (i + 1) / steps)
        sim.step(realtime=view)
    sim.step(25, realtime=view)   # wait half a second for the arm to settle


print("red cube starts at", sim.get_state()["objects"]["red_cube"]["position"].round(3))
for description, target, seconds in WAYPOINTS:
    move_arm(target, seconds)
    cube = sim.get_state()["objects"]["red_cube"]["position"]
    print(f"{description:22s} cube at {cube.round(3)}")

height = sim.get_state()["objects"]["red_cube"]["position"][2]
print("The cube is on the shelf." if abs(height - 0.095) < 0.005 else "The cube did not end up on the shelf.")

while view and sim.viewer_is_open():   # keep the window open until you close it
    sim.step(realtime=True)
sim.close()
