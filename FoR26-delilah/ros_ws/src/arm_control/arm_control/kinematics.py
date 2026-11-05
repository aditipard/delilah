"""Forward and inverse kinematics of the LeKiwi arm.

All positions are in the robot's base frame (x forward, y left, z up), in metres.
All joint angles are in degrees, in the order of lekiwi_sim.arm_model.JOINT_NAMES.
The end effector is the tip of the gripper's fixed finger.
"""
import numpy as np

from lekiwi_sim.arm_model import (HOME_FINGER_DIRECTION, HOME_FINGERTIP, JOINT_AXES, JOINT_LIMITS_DEG,
                                  JOINT_POINTS)


def rotate(vector, axis, angle_rad):
    """Rotate `vector` about the unit vector `axis` by `angle_rad` (Rodrigues' rotation formula)."""
    vector, axis = np.asarray(vector, float), np.asarray(axis, float)
    return (vector * np.cos(angle_rad) + np.cross(axis, vector) * np.sin(angle_rad)
            + axis * (axis @ vector) * (1.0 - np.cos(angle_rad)))


def forward_kinematics(angles_deg):
    """Where is the fingertip, and which way does the finger point, for the given joint angles?

    Args:
        angles_deg: the five arm joint angles in degrees (a sixth value, the gripper, is ignored).
    Returns:
        (position, direction): the fingertip's position and the finger's unit direction vector.
    """
    angles = np.radians(np.asarray(angles_deg, float)[:5])
    position = HOME_FINGERTIP.copy()
    direction = HOME_FINGER_DIRECTION.copy()
    # TODO (forward kinematics): apply the five joint rotations to `position` and `direction`.
    # Use rotate(), JOINT_POINTS and JOINT_AXES. See Assignment3/Kinematics/01_forward_kinematics.md.
    return position, direction


def inverse_kinematics(target_position, target_direction, start_angles_deg, iterations=200,
                       direction_weight=0.05, damping=0.01):
    """Find joint angles that put the fingertip at `target_position`, pointing along `target_direction`.

    Solved numerically with damped least squares, starting from `start_angles_deg`. Only the first
    four joints are changed; wrist_roll keeps its starting value, because rolling the wrist does
    not change which way the finger points.

    Returns:
        (angles_deg, position_error): five joint angles, and how far the fingertip still is from
        the target in metres. Check the error: a target the arm cannot reach gives a large one.
    """
    target_position = np.asarray(target_position, float)
    target_direction = np.asarray(target_direction, float) / np.linalg.norm(target_direction)
    angles = np.asarray(start_angles_deg, float)[:5].copy()
    # TODO (inverse kinematics): change angles[:4] step by step until forward_kinematics(angles)
    # matches the target position and direction. See Assignment3/Kinematics/02_inverse_kinematics.md.
    position_error = float(np.linalg.norm(target_position - forward_kinematics(angles)[0]))
    return angles, position_error
