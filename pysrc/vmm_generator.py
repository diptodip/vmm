from vmm import *
import itertools

def generate_lp_linear(vmm, filename):
    P = vmm.pm_list
    V = vmm.vm_list
    obj = ""
    bounds = ""
    assignment_guarantee = ""
    variable_matching = ""
    capacity_constraint = ""
    objvars = np.ndarray(shape=(vmm.physical_size, vmm.virtual_size, vmm.physical_size, vmm.virtual_size), dtype=object)
    assignments = np.ndarray(shape=(vmm.physical_size, vmm.virtual_size), dtype=object)

    print("[out] generating objective function")
    counter = 0
    for u, v in itertools.product(range(vmm.physical_size), repeat=2):
        for i, j in itertools.product(range(vmm.virtual_size), repeat=2):
            varname = "a_" + str(u) + "_" + str(i) + "_" + str(v) + "_" + str(j)
            objvars[u, i, v, j] = varname
            distance = 0
            demand = 0
            if vmm.distances.has_key((P[u], P[v])) and vmm.traffic.has_key((V[i], V[j])):
                distance = vmm.distances[(P[u], P[v])]
                demand = vmm.traffic[(V[i], V[j])]
            t = distance * demand
            objterm = str(t) + " " + varname
            if counter > 0:
                objterm = " + " + objterm
            obj += objterm
            counter += 1

    for u in range(vmm.physical_size):
        for i in range(vmm.virtual_size):
            varname = "a_" + str(u) + "_" + str(i)
            assignments[u, i] = varname

    print("[out] generating constraints")

    counter = 0
    for u in range(vmm.physical_size):
        capacity = vmm.pm_list[u].capacity
        constraint = ""
        for i in range(vmm.virtual_size):
            load = vmm.vm_list[i].load
            newterm = str(load) + " " + assignments[u, i]
            if i > 0:
                newterm = " + " + newterm
            constraint += newterm
        constraint = "c" + str(counter) + ": " + constraint
        capacity_constraint += constraint + " <= " + str(capacity) + "\n"
        counter += 1

    for u, v in itertools.product(range(vmm.physical_size), repeat=2):
        for i, j in itertools.product(range(vmm.virtual_size), repeat=2):
            matchvar = "c" + str(counter) + ": "
            matchvar += "-" + objvars[u, i, v, j] + " + " + assignments[u, i] + " + " + assignments[v, j] + " <= 1" + "\n"
            variable_matching += matchvar
            counter += 1

    for i in range(vmm.virtual_size):
        constraint = ""
        for u in range(vmm.physical_size):
            newterm = assignments[u, i]
            if u > 0:
                newterm = " + " + newterm
            constraint += newterm
        constraint = "c" + str(counter) + ": " + constraint
        assignment_guarantee += constraint + " = 1\n"
        counter += 1

    print("[out] generating bounds")
    
    for u, v in itertools.product(range(vmm.physical_size), repeat=2):
        for i, j in itertools.product(range(vmm.virtual_size), repeat=2):
            bounds += "0 <= " + str(objvars[u, i, v, j]) + " <= 1\n"

    for u in range(vmm.physical_size):
        for i in range(vmm.virtual_size):
            bounds += "0 <= " + str(assignments[u, i]) + " <= 1\n"

    print("[out] printing .lp file")

    with open(filename, 'w') as f:
        f.write("Minimize\n")
        f.write("obj: " + obj + "\n")
        f.write("Subject To\n")
        f.write(capacity_constraint)
        f.write(assignment_guarantee)
        f.write(variable_matching)
        f.write("Bounds\n")
        f.write(bounds)
        f.write("End")
