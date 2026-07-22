import numpy as np
from scipy.linalg import expm

c_i = 0.8
beta = 0.5

H_B_i = np.array([
    [2*c_i - 1, -2*np.sqrt(c_i*(1-c_i))],
    [-2*np.sqrt(c_i*(1-c_i)), 1 - 2*c_i]
])

U_B_i = expm(-1j * beta * H_B_i)
print(np.round(U_B_i, 3))
