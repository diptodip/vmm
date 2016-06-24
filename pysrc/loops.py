import itertools

li = []
for i, j in itertools.product(range(20), repeat=2):
    for k, l in itertools.product(range(40), repeat=2):
        varname = "a_" + str(i) + "_" + str(j) + "_" + str(k) + "_" + str(l)
        li.append(varname)
print(li)
