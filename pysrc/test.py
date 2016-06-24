from vmm import *
from vmm_solver import *
import cplex
import time

#a = VMM(9, 18)
#a.read("a.vmm")
#a.generate()
#print("GENERATION DONE")
#x = brute_force(a)
#bf = calc_cost(x, a)
#write_solution("brute_force_a.vmms", x, bf)
#time_a = time.time()
#y = quadratic_integer_program(a)
#print(time.time() - time_a)
#iqp = calc_cost(y, a)
#write_solution("quadratic_program_a.vmms", y, iqp)
#z = linear_program(a)
#ilp = calc_cost(z, a)
#write_solution("linear_program_a.vmms", z, ilp)
#time_b = time.time()
#random_iteration(a, 500 * len(a.vm_list) * len(a.pm_list))
#print(time.time() - time_b)
c = cplex.Cplex()
c.read("test.lp")
c.solve()
sol = c.solution
for i in range(c.variables.get_num()):
    print(sol.get_values(i))
print("[out] LP CPLEX cost: {}".format(sol.get_objective_value()))
print("[out] LP done")
