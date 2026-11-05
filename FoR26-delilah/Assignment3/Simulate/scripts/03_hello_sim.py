"""First steps with the LeKiwiSim class: read the state, send a command, step, read again."""
import numpy as np

from lekiwi_sim import ARM_JOINTS, LeKiwiSim

np.set_printoptions(precision=3, suppress=True)

sim = LeKiwiSim()

state = sim.get_state()
print("The state contains:", list(state))
print("arm joints, in order:", ARM_JOINTS)
print("arm at start:", state["arm_position"])
print("gripper point at start:", state["gripper_position"])
print("objects:", {name: obj["position"] for name, obj in state["objects"].items()})

# Arm: 5 joint angles in degrees and the gripper in percent. Base: forward m/s, left m/s, turn deg/s.
sim.set_command(arm=[20, -30, 40, 30, 0, 100], base=[-0.1, 0.0, 0.0])
sim.step(100)   # 100 steps of 0.02 s = 2 seconds of simulated time

state = sim.get_state()
print(f"\nafter {state['time']:.1f} s of driving backwards at 0.1 m/s:")
print("arm:", state["arm_position"])
print("base pose [x, y, heading]:", state["base_pose"])
print("base velocity [forward, left, turn]:", state["base_velocity"])

sim.set_command(base=[0.0, 0.0, 0.0])   # the arm command is kept, only the base changes
sim.step(50)
print("\nafter the stop command, base velocity:", sim.get_state()["base_velocity"])
