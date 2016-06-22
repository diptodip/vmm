from vmm import *
from vmm_solver import *
import cplex
import time

a = VMM(20, 40)
#a.read("a.vmm")
a.generate()
#x = brute_force(a)
#bf = calc_cost(x, a)
#write_solution("brute_force_a.vmms", x, bf)
#time_a = time.time()
y = quadratic_integer_program(a)
#print(time.time() - time_a)
#iqp = calc_cost(y, a)
#write_solution("quadratic_program_a.vmms", y, iqp)
z = integer_program(a)
#ilp = calc_cost(z, a)
#write_solution("linear_program_a.vmms", z, ilp)
#time_b = time.time()
#random_iteration(a, 500 * len(a.vm_list) * len(a.pm_list))
#print(time.time() - time_b)
