"""Load the LeKiwi robot model directly with mujoco and list what is inside it."""
from pathlib import Path

import mujoco

MODEL = Path(__file__).resolve().parents[3] / "models" / "LeKiwi-sim" / "mjcf_lcmm_robot.xml"

model = mujoco.MjModel.from_xml_path(str(MODEL))
data = mujoco.MjData(model)


def name(kind, index):
    return mujoco.mj_id2name(model, kind, index)


print(f"bodies: {model.nbody}, joints: {model.njnt}, actuators: {model.nu}, cameras: {model.ncam}")
print(f"numbers in qpos (positions): {model.nq}, in qvel (velocities): {model.nv}")
print(f"timestep: {model.opt.timestep} s")

print("\nActuators (the things you can command):")
for i in range(model.nu):
    joint = model.actuator_trnid[i, 0]
    low, high = model.actuator_ctrlrange[i]
    limits = f"command range {low:5.2f} to {high:5.2f}" if model.actuator_ctrllimited[i] else "no command limit"
    print(f"  {i}: {name(mujoco.mjtObj.mjOBJ_ACTUATOR, i):14s} drives joint {name(mujoco.mjtObj.mjOBJ_JOINT, joint)!r}, {limits}")

print("\nJoints that are not passive wheel rollers:")
kinds = {0: "free", 1: "ball", 2: "slide", 3: "hinge"}
for j in range(model.njnt):
    joint_name = name(mujoco.mjtObj.mjOBJ_JOINT, j)
    if "roller" in joint_name.lower():
        continue
    print(f"  {joint_name:40s} type {kinds[model.jnt_type[j]]:5s} starts at qpos[{model.jnt_qposadr[j]}]")
rollers = sum("roller" in name(mujoco.mjtObj.mjOBJ_JOINT, j).lower() for j in range(model.njnt))
print(f"  ... plus {rollers} passive roller joints on the three omni wheels")
