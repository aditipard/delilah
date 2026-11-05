"""Open the 3-D viewer and move the robot. Run this at the lab computer, not over SSH."""
import math

from lekiwi_sim import LeKiwiSim

sim = LeKiwiSim()
sim.open_viewer()

while sim.viewer_is_open():
    t = sim.get_state()["time"]
    # Swing the shoulder left and right, open and close the gripper, and turn slowly on the spot.
    pan = 40.0 * math.sin(0.8 * t)
    gripper = 50.0 + 50.0 * math.sin(2.0 * t)
    sim.set_command(arm=[pan, 0, 0, 0, 0, gripper], base=[0.0, 0.0, 10.0])
    sim.step(realtime=True)

sim.close()
