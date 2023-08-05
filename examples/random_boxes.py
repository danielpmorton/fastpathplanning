"""Script version of random_boxes.ipynb for easier debugging"""

from itertools import product
import numpy as np
import matplotlib.pyplot as plt
import fastpathplanning as fpp

# parameters
P = 20 # side of the grid (square root of number of boxes)
sides = [2, .5] # sides of the boxes

# generate boxes
np.random.seed(0)
L = np.zeros((P ** 2, 2))
U = np.zeros((P ** 2, 2))
for k, c in enumerate(product(range(P), range(P))):
    np.random.shuffle(sides)
    diag = np.multiply(np.random.rand(2), sides)
    L[k] = c - diag
    U[k] = c + diag
    
# safe set
S = fpp.SafeSet(L, U, verbose=True)

# online path planning
p_init = np.zeros(2) # initial point
p_term = np.ones(2) * (P - 1) # terminal point
T = P # traversal time
alpha = [0, 1, 1] # cost weights
p = fpp.plan(S, p_init , p_term , T, alpha)

# plot result
plt.figure()
S.plot2d(alpha=.5) # plot safe set
p.plot2d() # plot smooth path
plt.show()
