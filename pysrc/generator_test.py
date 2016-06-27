from vmm import *
from vmm_generator import *

a = VMM(100, 200)
a.generate()
generate_lp_integer_linear(a, "generator.lp")
