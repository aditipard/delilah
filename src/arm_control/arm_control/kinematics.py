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
    for i in reversed(range(5)):
        axis = JOINT_AXES[i]
        point = JOINT_POINTS[i]
        angle = angles[i]

        position = point + rotate(position - point, axis, angle)
        direction = rotate(direction, axis, angle)
    # Use rotate(), JOINT_POINTS and JOINT_AXES. See Assignment3/Kinematics/01_forward_kinematics.md.
    return position, direction


def inverse_kinematics(target_position, target_direction, start_angles_deg,
                       iterations=500, direction_weight=0.1, damping=0.001,
                       require_direction=True):

    target_position = np.asarray(target_position, dtype=float)
    target_direction = np.asarray(target_direction, dtype=float)
    target_direction /= np.linalg.norm(target_direction)

    angles = np.asarray(start_angles_deg, dtype=float)[:5].copy()

    epsilon = 0.01  # Numerical derivative step in degrees

    for _ in range(iterations):

        position, direction = forward_kinematics(angles)

        # Calculate end-effector errors
        position_error = target_position - position
        direction_error = target_direction - direction

        error = np.concatenate([
            position_error,
            direction_weight * direction_error
        ])

        # Stop when the position is sufficiently accurate
        # Calculate angular error between target and actual finger direction

        # Calculate angular error
        direction_angle = np.arccos(
            np.clip(
                np.dot(target_direction, direction),
                -1.0,
                1.0
            )
        )

        # Check both position and direction
        if np.linalg.norm(position_error) < 0.001 and (
            not require_direction or direction_angle < np.radians(3.0)
        ):
            break

        # Numerical Jacobian
        J = np.zeros((6, 5))

        for j in range(5):
            test_angles = angles.copy()
            test_angles[j] += epsilon

            new_position, new_direction = forward_kinematics(test_angles)

            J[:3, j] = (new_position - position) / epsilon
            J[3:, j] = (
                direction_weight * (new_direction - direction) / epsilon
            )

        # Damped least squares
        damping_matrix = J @ J.T + damping**2 * np.eye(6)

        delta = J.T @ np.linalg.solve(damping_matrix, error)

        # Limit each iteration's angular change
        delta = np.clip(delta, -5.0, 5.0)

        angles[:5] += delta

        # Respect joint limits
        angles = np.clip(
            angles,
            JOINT_LIMITS_DEG[:, 0],
            JOINT_LIMITS_DEG[:, 1]
        )

    final_position, _ = forward_kinematics(angles)

    position_error = float(
        np.linalg.norm(target_position - final_position)
    )

    return angles, position_error
