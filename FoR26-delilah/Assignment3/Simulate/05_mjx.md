# 5. MJX and Faster Simulation

Everything so far ran one simulation on the computer's processor (CPU). That is the right tool for this course. This page explains what comes after it, so that you know the words when you meet them. There is nothing to install or run here.

## Why anyone needs something faster

On the lab computer, `LeKiwiSim` runs about 20 times faster than real time: one hour of robot time takes three minutes to simulate. For writing and testing a program, that is plenty.

Some methods need far more. **Reinforcement learning** trains a robot controller by trial and error, and may need the equivalent of months or years of robot time. Nobody can wait for that at 20 times real time. The answer is to run **thousands of copies of the simulation at once**.

## What MJX is

**MJX** (MuJoCo XLA) is a second implementation of MuJoCo's physics. It is written with **JAX**, a Python library from Google for fast numerical computing.

| | MuJoCo (what you have used) | MJX |
| --- | --- | --- |
| Runs on | the CPU | a graphics card (GPU), or other accelerators |
| Simulations at once | one | thousands, in parallel |
| Speed of a single simulation | fast | slower than MuJoCo |
| Can compute gradients | no | yes |
| Model file | MJCF | the same MJCF |

Two points in this table are often misunderstood:

- **MJX is not faster for one robot.** A single simulation is slower in MJX than in normal MuJoCo. MJX wins only when you run very many simulations side by side on a GPU.
- **MJX can differentiate.** Because it is written in JAX, it can compute how a small change in a command changes the outcome. Some learning and optimisation methods use this.

The basic pattern looks like this. You load the model with normal MuJoCo, then copy it to the accelerator:

```python
import mujoco
from mujoco import mjx

mj_model = mujoco.MjModel.from_xml_path("robot.xml")   # normal MuJoCo
mjx_model = mjx.put_model(mj_model)                    # the same model, on the GPU
mjx_data = mjx.make_data(mjx_model)
mjx_data = mjx.step(mjx_model, mjx_data)               # one physics step
```

Notice `mjx_data = mjx.step(...)`. Normal MuJoCo changes `data` in place. MJX returns a **new** data object each time, because JAX works with values that are never modified.

## Why we do not use it in this course

- **The lab computer has no suitable graphics card.** MJX on a CPU is slower than the MuJoCo you already have.
- **We run one robot, not thousands.**
- **MJX does not support everything MuJoCo does.** Some collision shapes and options are missing or limited, and detailed models like ours may need to be simplified first.

## Related tools

| Tool | What it is |
| --- | --- |
| **MuJoCo Warp** | A newer GPU implementation of MuJoCo, built on NVIDIA's Warp library instead of JAX. |
| **MuJoCo Playground** | A collection of ready-made robot learning environments built on MJX, with training examples. |

## Read more

- MJX documentation: <https://mujoco.readthedocs.io/en/stable/mjx.html>
- MuJoCo Playground: <https://github.com/google-deepmind/mujoco_playground>
- MuJoCo Warp: <https://github.com/google-deepmind/mujoco_warp>
- JAX: <https://docs.jax.dev>

---

Previous: [4. Pick and place](04_pick_and_place.md) | Back to the [overview](README.md)
