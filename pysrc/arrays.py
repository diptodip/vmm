import numpy as np
from itertools import product

A = np.ndarray(shape=(2, 3, 2, 3), dtype=object)
counter = 0

for i, k in product(range(2), repeat=2):
    for j, l in product(range(3), repeat=2):
        A[i, j, k, l] = "str_" + str(counter)
        counter += 1

for i, k in product(range(2), repeat=2):
    for j, l in product(range(3), repeat=2):
        print(A[i, j, k, l])
