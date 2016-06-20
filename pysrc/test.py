from vmm import *
from vmm_solver import *
import cplex

a = VMM(3, 4)
a.read("a.vmm")
x = brute_force(a)
bf = calc_cost(x, a)
write_solution("brute_force_a.vmms", x, bf)
y = quadratic_integer_program(a)
iqp = calc_cost(y, a)
write_solution("quadratic_program_a.vmms", y, iqp)
z = integer_program(a)
ilp = calc_cost(z, a)
write_solution("linear_program_a.vmms", z, ilp)
