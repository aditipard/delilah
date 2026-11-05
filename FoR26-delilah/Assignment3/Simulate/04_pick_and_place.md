# 4. Pick and Place

This page puts everything together in one complete task: the robot picks the red cube from the table and puts it on the left shelf.

## Run it

Without a window (this works over SSH):

```bash
conda activate ros_mujoco
cd ~/FOR26/Assignment3/Simulate/scripts
python 06_pick_and_place.py
```

You should see:

```
red cube starts at [0.3   0.06  0.055]
above the cube         cube at [0.3   0.06  0.055]
down to the cube       cube at [0.3   0.06  0.055]
close the gripper      cube at [0.299 0.052 0.055]
lift                   cube at [0.332 0.055 0.137]
over the shelf         cube at [0.134 0.293 0.191]
lower onto the shelf   cube at [0.133 0.284 0.115]
open the gripper       cube at [0.133 0.289 0.095]
move away              cube at [0.133 0.289 0.095]
The cube is on the shelf.
```

Follow the cube's height, the third number. It starts at 0.055 m on the table, is lifted to 0.137 m, carried over the shelf at 0.191 m, lowered, and comes to rest at 0.095 m. That is the shelf top (0.08 m) plus half a cube (0.015 m).

With the 3-D window, at the lab computer:

```bash
python 06_pick_and_place.py --view
```

The motion takes about 20 seconds. Close the window when you have seen enough.

## How it works

The program is a list of **waypoints**. Each waypoint is an arm pose, and the program moves the arm from one to the next.

```python
WAYPOINTS = [
    ("above the cube",       [-9.4, 39.7, -35.9, 100.0, 90.0, 100.0], 2.0),
    ("down to the cube",     [-10.5, 47.0, -20.2, 77.4, 90.0, 100.0], 1.5),
    ("close the gripper",    [-10.5, 47.0, -20.2, 77.4, 90.0, 0.0],   2.0),
    ("lift",                 [-9.9, 45.2, -54.7, 100.0, 90.0, 0.0],   2.0),
    ...
]
```

Each entry is a description, six arm values, and the number of seconds the move should take. Read the values with what you know:

- The **last value** is the gripper: 100 (open) on the way down, then 0 (closed) to grasp, then 100 again to let go.
- The **fifth value**, `wrist_roll`, is 90 the whole time. At 0 the two fingers are one above the other. Turning the wrist by 90 degrees puts them side by side, so they can come down on either side of the cube.
- Between "down to the cube" and "close the gripper" only the gripper value changes. The arm stays still while the fingers close.

The function that moves between waypoints is short:

```python
def move_arm(target, seconds):
    start = sim.get_command()["arm"]
    steps = int(seconds / sim.control_dt)
    for i in range(steps):
        sim.set_command(arm=start + (np.array(target) - start) * (i + 1) / steps)
        sim.step(realtime=view)
    sim.step(25, realtime=view)
```

Instead of sending the final pose at once, it sends many small intermediate targets, one per step. This is called **interpolation**. The arm then moves smoothly and at a speed you choose, instead of rushing to the target as fast as its motors allow.

## Why this only works here

The waypoints are fixed numbers. They were worked out for exactly this scene: this cube position, this shelf, the robot starting at the origin. The program never looks at where the cube actually is.

This is called **open-loop** control: act without checking the result. It works in a simulator because the simulator is perfectly repeatable. Run the program ten times and you get the same ten results.

It would fail on a real robot, where the cube is never in exactly the same place twice. A real program must **close the loop**: measure where things are (from `get_state()` or from a camera image), compute where to go, act, and measure again.

## Try it yourself

1. **Break it.** In the program, after `sim = LeKiwiSim()`, add `sim.set_command(base=[-0.1, 0, 0]); sim.step(10); sim.set_command(base=[0, 0, 0])` so the robot starts 2 cm further back. Does the pick still work? Why?
2. **Slow down, speed up.** Change every duration to 0.5 s. What happens to the cube?
3. **Another cube.** Change the first waypoints so the robot picks the green cube instead. The green cube is at the same distance, on the other side. Which joint value has to change the most?
4. **Other shelf.** Put the cube on `shelf_right`, which is 4 cm higher.
5. **Close the loop (harder).** Before each move, read `gripper_position` and the cube's position from `get_state()`, and adjust `shoulder_pan` so that the gripper is in line with the cube.

---

Previous: [3. The simulator class](03_the_simulator_class.md) | Next: [5. MJX and faster simulation](05_mjx.md)
