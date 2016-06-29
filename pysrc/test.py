from vmm import *
from vmm_solver import *
import cplex
import time

c = cplex.Cplex()
ctime = time.time()
c.read("test_big.lp")
c.solve()
sol = c.solution
print("[out] LP CPLEX cost: {}".format(sol.get_objective_value()))
with open("test_big_time.log", 'w') as f:
    f.write("{} \n".format(ctime - time.time()))
print("[out] LP done")
