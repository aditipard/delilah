import mujoco

# A tiny world: a floor and a box that starts 1 metre above it.
XML = """
<mujoco>
  <worldbody>
    <light pos="0 0 3"/>
    <geom type="plane" size="2 2 0.1"/>
    <body name="box" pos="0 0 1">
      <freejoint/>
      <geom type="box" size="0.1 0.1 0.1" rgba="0.8 0.2 0.2 1"/>
    </body>
  </worldbody>
</mujoco>
"""

model = mujoco.MjModel.from_xml_string(XML)
data = mujoco.MjData(model)

print("MuJoCo version:", mujoco.__version__)
print("Box height at start:", round(data.qpos[2], 3), "m")

# Simulate 1 second of physics.
while data.time < 1.0:
    mujoco.mj_step(model, data)

print("Box height after 1 s:", round(data.qpos[2], 3), "m")
