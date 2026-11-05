"""A first MuJoCo program: a motor-driven pendulum, written directly with the mujoco library."""
import mujoco

# The model is described in MJCF, MuJoCo's XML format.
XML = """
<mujoco>
  <option timestep="0.002"/>
  <worldbody>
    <light pos="0 0 3"/>
    <geom type="plane" size="1 1 0.1"/>
    <body name="arm" pos="0 0 0.5">
      <joint name="hinge" type="hinge" axis="0 1 0" damping="0.05"/>
      <geom type="capsule" fromto="0 0 0 0.3 0 0" size="0.02" mass="0.2"/>
    </body>
  </worldbody>
  <actuator>
    <motor name="motor" joint="hinge" ctrlrange="-1 1"/>
  </actuator>
</mujoco>
"""

model = mujoco.MjModel.from_xml_string(XML)  # everything that does not change: shapes, masses, limits
data = mujoco.MjData(model)                  # everything that does change: time, positions, velocities

print("timestep:", model.opt.timestep, "s")
print("number of joints:", model.njnt, "| number of actuators:", model.nu)

# No motor torque: the pendulum starts horizontal and swings down under gravity.
for _ in range(500):          # 500 steps of 0.002 s = 1 second
    mujoco.mj_step(model, data)
print(f"t = {data.time:.1f} s, no torque:   angle = {data.qpos[0]:6.2f} rad, velocity = {data.qvel[0]:6.2f} rad/s")

# Now push with the motor. data.ctrl holds one command per actuator.
data.ctrl[0] = -0.6
for _ in range(2000):         # 4 more seconds
    mujoco.mj_step(model, data)
print(f"t = {data.time:.1f} s, torque -0.6: angle = {data.qpos[0]:6.2f} rad, velocity = {data.qvel[0]:6.2f} rad/s")
