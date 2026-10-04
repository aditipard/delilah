#%%
import numpy as np
import matplotlib.pyplot as plt
import scipy as sp
import math

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

def Trans_Gr_Base(theta0, Lx, Ly, Lz):
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

def Trans_Base_M1(theta1, Lx, Ly, Lz):
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

def Trans_M2_M3(theta2, Lx, Ly, Lz):
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

def Trans_M3_M4(theta3, Lx, Ly, Lz):
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

def Trans_M4_M5(theta4, Lx, Ly, Lz):
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

def Trans_M5_M6(theta5, Lx, Ly, Lz):
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
def fwd_kin():
  total = (
      Trans_Gr_Base(0, 3, 0, 5)
      @ Trans_Base_M1(0, 4, 0, 0)
      @ Trans_M2_M3(theta2, 4, 0, 6)
      @ Trans_M3_M4(theta3, 8, 0, 0)
      @ Trans_M4_M5(3 * np.pi / 4, 0, 0, 8)
      @ Trans_M5_M6(theta5, 4, 0, 0)
  )
  print("Product of transformation matrices:")
  print(total)
  return total

# %%
