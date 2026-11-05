"""Kinematic description of the simulated LeKiwi arm, for forward and inverse kinematics.

Everything is expressed in the robot's BASE FRAME:
    origin  the centre of the bottom base plate
    x       forward (towards the arm)
    y       to the robot's left
    z       up

The description is for the ZERO POSE: all five arm joints at 0 degrees (the real robot's
convention, 0 = the middle of each joint's range).

For joint i:
    JOINT_POINTS[i]  a point on the joint's rotation axis (metres)
    JOINT_AXES[i]    the direction of the rotation axis (unit vector). Turning the joint by a
                     POSITIVE angle rotates everything after it counter-clockwise about this
                     vector (right-hand rule).

The END EFFECTOR is the tip of the gripper's fixed finger:
    HOME_FINGERTIP          its position at the zero pose (metres)
    HOME_FINGER_DIRECTION   the direction the finger points in at the zero pose (unit vector)

These numbers were read out of the MuJoCo model in models/LeKiwi-sim. The gripper joint is not
part of the chain: opening or closing the gripper does not move the fixed finger.
"""
import numpy as np

JOINT_NAMES = ("shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll")

JOINT_POINTS = np.array([
    [0.06715, 0.00000, 0.08445],    # shoulder_pan
    [0.09775, -0.01830, 0.13665],   # shoulder_lift
    [0.11583, -0.01680, 0.25123],   # elbow_flex
    [0.24876, -0.01530, 0.27995],   # wrist_flex
    [0.30778, 0.00480, 0.29577],    # wrist_roll
])

JOINT_AXES = np.array([
    [0.0, 0.0, -1.0],               # shoulder_pan: positive turns the arm to the robot's right
    [0.0, 1.0, 0.0],                # shoulder_lift
    [0.0, 1.0, 0.0],                # elbow_flex
    [0.0, 1.0, 0.0],                # wrist_flex
    [-0.96593, 0.0, -0.25882],      # wrist_roll
])

HOME_FINGERTIP = np.array([0.41257, 0.00480, 0.31039])
HOME_FINGER_DIRECTION = np.array([0.96593, 0.0, 0.25882])

# Lowest and highest angle of each joint, in degrees.
JOINT_LIMITS_DEG = np.array([
    [-115.0, 115.0],
    [-100.0, 90.0],
    [-90.0, 95.0],
    [-100.0, 100.0],
    [-100.0, 160.0],
])
