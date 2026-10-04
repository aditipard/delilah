#%%
import numpy as np
import matplotlib.pyplot as plt

#%% define standard 2Drotation matrix
def rotation_matrix(theta):
    return np.array([
        [np.cos(theta), -np.sin(theta)],
        [np.sin(theta), np.cos(theta)]
    ])
#%% hmg transformation matrix
#top left is the rot matrix, then rigth column [tx, ty] is translation vector, bottom [0,0,1] to keep the math consistent (as said in class)
#rotation by theta counterclockwise by a shift of [tx,ty]
def homogeneous_transformation_matrix(theta, tx, ty):
    return np.array([
        [np.cos(theta), -np.sin(theta), tx],
        [np.sin(theta), np.cos(theta), ty],
        [0, 0, 1]
    ])
#%%HT with rotation on x-axis
#x column is where we are rotating, so the rotating is in the YZ plane. 
#Shift/translation happens by 'tx' units in X direction and 'ty' in Y direction

def HomogeneousTranRot_X(theta_x, tx, ty):
    return np.array([
        [1, 0, 0, tx],
        [0, np.cos(theta_x), -np.sin(theta_x), ty],
        [0, np.sin(theta_x), np.cos(theta_x), 0],
        [0, 0, 0, 1]
    ])
#%%HT with rotation on y-axis
#y column is where we are rotating, so the rotating is in the XZ plane. 
#Shift/translation happens by 'tx' units in X direction and 'ty' in Y direction
def HomogeneousTranRot_Y(theta_y, tx, ty):
    return np.array([
        [np.cos(theta_y),0, np.sin(theta_y), tx],
        [0, 1, 0, ty],
        [-np.sin(theta_y), 0, np.cos(theta_y), 0],
        [0, 0, 0, 1]
    ])