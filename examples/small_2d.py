"""Script version of small_2d.ipynb for easier debugging"""

import numpy as np
import matplotlib.pyplot as plt
import fastpathplanning as fpp


# offline preprocessing
L = np.array([
    [6.25,    4],
    [ 5.5,  2.5],
    [   1,    4],
    [ .25,  1.5],
    [2.25,  .75],
    [  .5, -.25],
    [   2,    0],
    [4.75, -.25],
    [   0,  5.2]
]) # lower bounds of the safe boxes
U = np.array([
    [7.25, 5.75],
    [ 7.5, 4.75],
    [   6,    5],
    [   7,    3],
    [   3,  2.5],
    [ 1.5,  4.5],
    [6.25,    1],
    [   6, 3.75],
    [   7,    6]
])# upper bounds of the safe boxes
S = fpp.SafeSet(L, U, verbose=True)


# online path planning
p_init = np.array([1, .25]) # initial point
p_term = np.array([.5, 5.6]) # terminal point
T = 10 # traversal time
alpha = [0, 0, 1] # cost weights
p = fpp.plan(S, p_init , p_term , T, alpha)


# plot result
plt.figure()
S.plot2d(alpha=.5) # plot safe set
p.plot2d() # plot smooth path
plt.show()
