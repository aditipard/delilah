#%%
import numpy as np
import matplotlib.pyplot as plt
import scipy as sp
from scipy.optimize import least_squares
import math
import unittest

#%% define standard 2D rotation matrix
def rotation_matrix(theta):

        c = np.cos(theta)
        s = np.sin(theta)
        return np.array([
        [c,-s],
        [s, c]
])

#%% hmg transformation matrix
#top left is the rot matrix, then right column [tx, ty] is translation vector, bottom [0,0,1] to keep the math consistent (as said in class)
#rotation by theta counterclockwise by a shift of [tx,ty]
def homogeneous_transformation_matrix(theta, tx, ty):
    c = np.cos(theta)
    s = np.sin(theta)
    return np.array([
        [c, -s, tx],
        [s, c, ty],
        [0, 0, 1]
    ])


#%%HT with rotation on x-axis
#x column is where we are rotating, so the rotating is in the YZ plane.
#Shift/translation happens by 'tx' units in X direction and 'ty' in Y direction

def HomogeneousTranRot_X(theta, tx, ty):
    c = np.cos(theta)
    s = np.sin(theta)
    return np.array([
        [1, 0, 0, tx],
        [0, c, -s, ty],
        [0, s, c, 0],
        [0, 0, 0, 1]
    ])

#%%HT with rotation on y-axis
#y column is where we are rotating, so the rotating is in the XZ plane.
#Shift/translation happens by 'tx' units in X direction and 'ty' in Y direction
def HomogeneousTranRot_Y(theta, tx, ty):
    c = np.cos(theta)
    s = np.sin(theta)
    return np.array([
        [c, 0, s, tx],
        [0, 1, 0 , ty],
        [-s, 0, c, 0],
        [0, 0, 0, 1]
    ])

#%%HT with rotation on z-axis
#z column is where we are rotating, so the rotating is in the XY plane.
#Shift/translation happens by 'tx' units in X direction and 'ty' in Y direction
def HomogeneousTranRot_Z(theta, tx, ty):
    c = np.cos(theta)
    s = np.sin(theta)
    return np.array([
        [c, -s, 0, tx],
        [s, c, 0, ty],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])

#%%HT with translation on x,y,z
def HomogeneousTranTranslation(theta, tx, ty, tz):
  return np. array([
      [1, 0 , 0, tx],
      [0, 1, 0, ty],
      [0, 0, 1, tz],
      [0, 0, 0, 1]
  ])

#%% T01
# no rotation, ground to base
# x & z translation
# L is in cm
theta0 = np.pi
c = np.cos(theta0)
s = np.sin(theta0)

def Trans_Gr_Base(theta0):
    Lx = 3
    Ly = 0
    Lz = 5
    return np.array([
    [1, 0, 0, Lx],
    [0, 1, 0, Ly],
    [0, 0 , 1, Lz],
    [0, 0, 0, 1]
])

#%% T12
# no rotation, Base to Motor 1
# x translation

theta1 = np.pi
c = np.cos(theta1)
s = np.sin(theta1)

def Trans_Base_M1(theta1):
    Lx = 4
    Ly = 0
    Lz = 0
    return np.array([
    [1, 0, 0, Lx],
    [0, 1, 0, Ly],
    [0, 0, 1, Lz],
    [0, 0, 0, 1]
])

#%% T23
# no rotation, Motor 2 to Motor 3
# Rotation on Z-Axis and X & Z translation
theta2 = np.pi
c = np.cos(theta2)
s = np.sin(theta2)

def Trans_M2_M3(theta2):
  Lx = 4
  Ly = 0
  Lz = 6
  c = np.cos(theta2)
  s = np.sin(theta2)
  return np.array([
    [c, -s, 0, Lx],
    [s, c, 0, Ly],
    [0, 0, 1, Lz],
    [0, 0, 0, 1]
])

#%% T34
# Motor 3 to Motor 4
# Rotation on Y-Axis and X translation
theta3 = np.pi
c = np.cos(theta3)
s = np.sin(theta3)

def Trans_M3_M4(theta3):
  Lx = 8
  Ly = 0
  Lz = 0
  c = np.cos(theta3)
  s = np.sin(theta3)
  return np.array([
    [c, 0, s, Lx],
    [0, 1, 0, Ly],
    [-s, 0, c, Lz],
    [0, 0, 0, 1]
])

#%% T45
# Motor 4 to Motor 5
# Rotation on Y-Axis and Z translation
theta4 = np.pi
c = np.cos(theta4)
s = np.sin(theta4)

def Trans_M4_M5(theta4):
  Lx = 0
  Ly = 0
  Lz = 8
  c = np.cos(theta4)
  s = np.sin(theta4)
  return np.array([
    [c, 0, s, Lx],
    [0, 1, 0, Ly],
    [-s, 0, c, Lz],
    [0, 0, 0, 1]
])

#%% T56
# Motor 5 to Motor 6
# Rotation on Y-Axis and X translation
theta5 = np.pi
c = np.cos(theta5)
s = np.sin(theta5)

def Trans_M5_M6(theta5):
  Lx = 4
  Ly = 0
  Lz = 0
  c = np.cos(theta5)
  s = np.sin(theta5)
  return np.array([
    [c, 0, s, Lx],
    [0, 1, 0, Ly],
    [-s, 0, c, Lz],
    [0, 0, 0, 1]
])

#%% forward_kinematics(x, y, ...) that returns a transformation matrix representing the
#robot's end effector pose relative to the stationary base frame.
#arguments provide the rotation angles and translations for each transformation

#%%
def forward_kinematics(
    theta2_angle=theta2,
    theta3_angle=theta3,
    theta4_angle=3 * np.pi / 4,
    theta5_angle=theta5,
):
  FK = (
      Trans_Gr_Base(0)
      @ Trans_Base_M1(0)
      @ Trans_M2_M3(theta2_angle)
      @ Trans_M3_M4(theta3_angle)
      @ Trans_M4_M5(theta4_angle)
      @ Trans_M5_M6(theta5_angle)
  )
  return FK

#%% Five simple unit tests for forward kinematics
class TestForwardKinematics(unittest.TestCase):
    def test_ground_to_base_translation(self):
        result = Trans_Gr_Base(0)
        expected_translation = np.array([3, 0, 5])
        print("\nGround-to-base translation")
        print("Expected:", expected_translation)
        print("Actual:  ", result[:3, 3])
        self.assertTrue(np.allclose(result[:3, 3], expected_translation))

    def test_motor_2_to_motor_3_translation(self):
        result = Trans_M2_M3(0)
        expected_translation = np.array([4, 0, 6])
        print("\nMotor 2-to-motor 3 translation")
        print("Expected:", expected_translation)
        print("Actual:  ", result[:3, 3])
        self.assertTrue(np.allclose(result[:3, 3], expected_translation))

    def test_motor_2_to_motor_3_rotation(self):
        result = Trans_M2_M3(np.pi / 2)
        expected_rotation = np.array([
            [0, -1, 0],
            [1, 0, 0],
            [0, 0, 1],
        ])
        print("\nMotor 2-to-motor 3 rotation")
        print("Expected:\n", expected_rotation)
        print("Actual:\n", result[:3, :3])
        self.assertTrue(np.allclose(result[:3, :3], expected_rotation))

    def test_motor_4_to_motor_5_rotation(self):
        result = Trans_M4_M5(np.pi / 2)
        expected_rotation = np.array([
            [0, 0, 1],
            [0, 1, 0],
            [-1, 0, 0],
        ])
        print("\nMotor 4-to-motor 5 rotation")
        print("Expected:\n", expected_rotation)
        print("Actual:\n", result[:3, :3])
        self.assertTrue(np.allclose(result[:3, :3], expected_rotation))

    def test_forward_kinematics(self):
        result = forward_kinematics(0, 0, 0, 0)
        expected = np.array([
            [1, 0, 0, 23],
            [0, 1, 0, 0],
            [0, 0, 1, 19],
            [0, 0, 0, 1],
        ])
        print("\nComplete forward kinematics")
        print("Expected:\n", expected)
        print("Actual:\n", result)
        self.assertTrue(np.allclose(result, expected))


print("Product of transformation matrices:")
print(forward_kinematics())

print("\nRunning forward-kinematics unit tests...")
forward_tests = unittest.defaultTestLoader.loadTestsFromTestCase(
    TestForwardKinematics
)
forward_result = unittest.TextTestRunner(verbosity=2).run(forward_tests)
print(
    "\nFORWARD-KINEMATICS TEST RESULT:",
    "SUCCESS" if forward_result.wasSuccessful() else "FAILURE",
)


#%% inverse_kinematics_position(x_des, y_des, z_des)
def inverse_kinematics_position(x_des, y_des, z_des):
  desired_position = np.array([x_des, y_des, z_des], dtype=float)

  def position_error(joint_angles):
    actual_position = forward_kinematics(*joint_angles)[:3, 3]
    return actual_position - desired_position

  solution = least_squares(
      position_error,
      x0=np.array([theta2, theta3, 3 * np.pi / 4, theta5]),
      bounds=(-np.pi, np.pi),
  )
  found = bool(np.linalg.norm(position_error(solution.x)) < 1e-6)
  return solution.x, found


#%% Unit tests for inverse kinematics
class TestInverseKinematics(unittest.TestCase):
    def test_returns_four_joint_angles(self):
        angles, found = inverse_kinematics_position(23, 0, 19)
        self.assertEqual(len(angles), 4)
        self.assertIsInstance(found, bool)

    def test_finds_default_position(self):
        expected_position = forward_kinematics()[:3, 3]
        angles, found = inverse_kinematics_position(*expected_position)
        self.assertTrue(found)
        self.assertTrue(
            np.allclose(forward_kinematics(*angles)[:3, 3], expected_position)
        )

    def test_reports_zero_angle_position_as_unreachable(self):
        expected_position = forward_kinematics(0, 0, 0, 0)[:3, 3]
        angles, found = inverse_kinematics_position(*expected_position)
        self.assertFalse(found)
        self.assertEqual(len(angles), 4)

    def test_reports_unreachable_position(self):
        angles, found = inverse_kinematics_position(100, 100, 100)
        self.assertFalse(found)
        self.assertEqual(len(angles), 4)

    def test_solution_is_within_joint_limits(self):
        expected_position = forward_kinematics()[:3, 3]
        angles, found = inverse_kinematics_position(*expected_position)
        self.assertTrue(found)
        self.assertTrue(np.all(angles >= -np.pi))
        self.assertTrue(np.all(angles <= np.pi))


print("\nRunning inverse-kinematics unit tests...")
inverse_tests = unittest.defaultTestLoader.loadTestsFromTestCase(
    TestInverseKinematics
)
inverse_result = unittest.TextTestRunner(verbosity=2).run(inverse_tests)
print(
    "\nINVERSE-KINEMATICS TEST RESULT:",
    "SUCCESS" if inverse_result.wasSuccessful() else "FAILURE",
)

desired_position = forward_kinematics()[:3, 3]
joint_angles, solution_found = inverse_kinematics_position(*desired_position)
print("\nInverse kinematics example:")
print("Desired position:", desired_position)
print("Joint angles:", joint_angles)
print("Solution found:", solution_found)
