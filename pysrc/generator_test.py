from vmm import *
from vmm_generator import *

a = VMM(3, 6)
a.generate()
generate_lp_integer_linear(a, "generator.lp")
