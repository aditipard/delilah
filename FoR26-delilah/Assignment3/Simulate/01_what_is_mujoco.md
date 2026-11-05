# 1. What is MuJoCo?

**MuJoCo** (Multi-Joint dynamics with Contact) is a physics engine. You describe a world of rigid bodies, joints and motors, and MuJoCo computes how it moves over time under gravity, motor forces and contacts. It is free, open source, fast, and widely used in robotics research.

On this page you use MuJoCo directly, with a very small model, to learn the four ideas everything else is built on.

## Idea 1: the model is written in MJCF

A MuJoCo world is described in a text format called **MJCF**, which is XML. Here is a complete model: a floor and a pendulum with a motor.

```xml
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
```

The words you will meet again and again:

| MJCF element | Meaning |
| --- | --- |
| `<body>` | A rigid part. Bodies are nested: a body inside another body moves with it. |
| `<geom>` | A shape attached to a body (box, sphere, capsule, mesh, ...). Geoms give a body its look, its mass and its collisions. |
| `<joint>` | How a body may move relative to its parent. A `hinge` rotates about one axis. A body **without** a joint is welded to its parent. A `free` joint lets a body move freely, like a cube lying on a table. |
| `<actuator>` | A motor. It turns a command number into a force on a joint. |
| `timestep` | How much simulated time one physics step covers, here 0.002 s. |

Units are always metres, kilograms, seconds and radians.

## Idea 2: model and data

In Python, MuJoCo splits a simulation into two objects.

```python
model = mujoco.MjModel.from_xml_string(XML)
data = mujoco.MjData(model)
```

| Object | Holds | Changes while simulating? |
| --- | --- | --- |
| `model` (`MjModel`) | everything fixed: shapes, masses, joint limits, the timestep | no |
| `data` (`MjData`) | everything that evolves: time, positions, velocities, forces | yes |

The most important fields of `data`:

| Field | Meaning |
| --- | --- |
| `data.time` | simulated time in seconds |
| `data.qpos` | the position of every joint, as one long list of numbers |
| `data.qvel` | the velocity of every joint |
| `data.ctrl` | the command for every actuator. **This is the only thing you write.** |

## Idea 3: stepping

One call advances the simulation by one timestep:

```python
mujoco.mj_step(model, data)
```

MuJoCo reads `data.ctrl`, computes all forces, and updates `data.qpos`, `data.qvel` and `data.time`. Simulating one second with a timestep of 0.002 s therefore takes 500 calls.

Nothing happens between calls. The simulation does not run by itself in the background, and it does not care about real time: the loop runs as fast as your computer can compute.

## Idea 4: actuators turn commands into forces

You never set positions or velocities directly. You write a command into `data.ctrl`, and the actuator turns it into a force. What the command **means** depends on the type of actuator.

| Actuator type | The command is | Typical use |
| --- | --- | --- |
| `<motor>` | a force or torque | simple motors |
| `<position>` | a target angle; the actuator pushes toward it like a spring | robot arm joints (servos) |
| `<velocity>` | a target speed | wheels |

The pendulum above has a `<motor>`. The LeKiwi model on the next page uses `<position>` actuators for the arm and `<velocity>` actuators for the wheels, because that is how the real servos behave.

## Run it

The program [`scripts/01_pendulum.py`](scripts/01_pendulum.py) puts these ideas together.

```bash
conda activate ros_mujoco
cd ~/FOR26/Assignment3/Simulate/scripts
python 01_pendulum.py
```

You should see:

```
timestep: 0.002 s
number of joints: 1 | number of actuators: 1
t = 1.0 s, no torque:   angle =   1.58 rad, velocity =  -0.27 rad/s
t = 5.0 s, torque -0.6: angle = -42.25 rad, velocity = -14.88 rad/s
```

Read the two result lines:

- **No torque.** The pendulum starts horizontal and falls. After one second its angle is 1.58 rad, which is 90 degrees: it is hanging straight down and has almost stopped swinging, because the joint has some damping.
- **Torque -0.6.** The motor is now stronger than gravity, so the pendulum goes round and round. The angle keeps growing (42 rad is more than six full turns).

Open the file and find the two lines that matter most:

```python
data.ctrl[0] = -0.6
mujoco.mj_step(model, data)
```

## Try it yourself

Change the program and predict the result before you run it.

1. Set the torque to `-0.2` instead of `-0.6`. Does the pendulum still go round?
2. Remove `damping="0.05"` from the joint. What happens to the velocity after one second?
3. Change `timestep` to `0.02`. How many steps are now needed for one second?

## Read more

- MuJoCo overview: <https://mujoco.readthedocs.io/en/stable/overview.html>
- MJCF reference (every element and attribute): <https://mujoco.readthedocs.io/en/stable/XMLreference.html>
- Python bindings: <https://mujoco.readthedocs.io/en/stable/python.html>

---

Back to the [overview](README.md) | Next: [2. The LeKiwi model](02_the_lekiwi_model.md)
