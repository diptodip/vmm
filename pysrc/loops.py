import itertools
import numpy as np

a = []
b = []

for i, j in itertools.product(range(2), repeat=2):
    for k, l in itertools.product(range(4), repeat=2):
        a.append("a_" + str(i) + "_" + str(j) + "_" + str(k) + "_" + str(l))

for i in range(2):
    for j in range(2):
        for k in range(4):
            for l in range(4):
                b.append("a_" + str(i) + "_" + str(j) + "_" + str(k) + "_" + str(l))

for i in range(len(a)):
    if i >= len(b):
        print("LENGTH")
    if not a[i] == b[i]:
        print("MISMATCH")

print("DONE")
