from vmm import *
from vmm_solver import *

a = VMM(3, 4)
a.read("a.vmm")
brute_force(a)
