#import cvxopt
import cplex
from vmm import *
import itertools
import numpy as np
import time

def check_capacities(x, vmm):
    capacities = dict()
    for vm in vmm.virtual_machines:
        if capacities.has_key(x[vm]):
            capacities[x[vm]] += vm.load
        else:
            capacities[x[vm]] = vm.load
        if capacities.has_key(x[vm]) and capacities[x[vm]] > x[vm].capacity:
            return False
    return True

def calc_cost(x, vmm):
    updated = 0
    if not check_capacities(x, vmm):
        return -1
    else:
        cost = 0
        for pair in itertools.combinations(vmm.virtual_machines, 2):
            pm1 = x[pair[0]]
            pm2 = x[pair[1]]
            distance = -1
            if vmm.distances.has_key((pm1, pm2)):
                distance = vmm.distances[(pm1, pm2)]
            traffic = -1
            if vmm.traffic.has_key(pair):
                traffic = vmm.traffic[(pair)]
            if not distance == -1 and not traffic == -1:
                cost += (traffic * distance)
                updated += 1
        if updated > 0:
            return cost
        else:
            return -2

def generate_mapping(part, pms, vms, space, reps):
    space += [dict(zip(vms, x)) for x in itertools.product(part, pms, repeat=reps)]

def brute_force(vmm):
    print("[info] enumerating space")
    space = [dict(zip(vmm.virtual_machines, x)) for x in itertools.product(vmm.physical_machines, repeat=vmm.virtual_size)]
    print("[out] space enumerated")
    costs = [calc_cost(x, vmm) for x in space]
    x, index = min((x, index) for (index, x) in enumerate(costs) if x >= 0)
    #print(space)
    #for cost in costs:
        #print("[out] {}".format(cost))
    print("[out] brute force solution: {}".format(space[index]))
    print("[out] brute force cost: {}".format(x))
    print("[out] brute force done")

def integer_program(vmm):
    vms = list(vmm.virtual_machines)
    loads = [x.load for x in vms]
    pms = list(vmm.physical_machines)
    capacities = [x.capacity for x in pms]
    distances = vmm.distances
    traffic = vmm.traffic
    c = cplex.Cplex()
    c.parameters.mip.limits.nodes.set(10000)
    c.objective.set_sense(c.objective.sense.minimize)
    allvars = []
    allcosts = []
    assignments = np.ndarray(shape=(vmm.physical_size, vmm.virtual_size, vmm.physical_size, vmm.virtual_size), dtype=object)
    #costs = np.ndarray(shape=(vmm.physical_size, vmm.virtual_size, vmm.physical_size, vmm.virtual_size), dtype=uint32)


    # assignment variables: assignvars["a_i_j-k_l"] = 1 if VM j assigned to PM i AND VM l assigned to PM k, else 0
    for i, k in itertools.product(range(vmm.physical_size), repeat=2):
        for j, l in itertools.product(range(vmm.virtual_size), repeat=2):
            varname = "a_" + str(i) + "_" + str(j) + "-" + str(k) + "_" + str(l)
            allvars.append(varname)
            assignments[i, j, k, l] = varname
            distance = 1
            demand = 1
            if vmm.distances.has_key((pms[i], pms[k])) and vmm.traffic.has_key((vms[j], vms[l])):
                distance = vmm.distances[(pms[i], pms[k])]
                demand = vmm.traffic[(vms[j], vms[l])]
            allcosts.append(distance * demand)
            #costs[i, j, k, l] = distance * demand

    c.variables.add(names=allvars, lb=[0] * len(allvars), ub=[1] * len(allvars), types=["B"] * len(allvars), obj=allcosts)

    # each VM is assigned to exactly one PM
    for j, l in itertools.product(range(vmm.virtual_size), repeat=2):
        variables = []
        for i, k in itertools.product(range(vmm.physical_size), repeat=2):
            variables.append(assignments[i, j, k, l])
        c.linear_constraints.add(lin_expr=[cplex.SparsePair(variables, [1] * len(variables))], senses=["E"], rhs=[2])

    # VM assignments cannot violate PM capacities
    coefficients = []
    righthand = []
    for i, k in itertools.product(range(vmm.physical_size), repeat=2):
        for j, l in itertools.product(range(vmm.virtual_size), repeat=2):
            load_j = loads[j]
            load_l = loads[l]
            capacity_i = capacities[i]
            capacity_k = capacities[k]
            coefficients.append(load_j + load_l)
            righthand.append(capacity_i + capacity_k)
    
    c.linear_constraints.add(lin_expr=[cplex.SparsePair([allvars[x]], [coefficients[x]]) for x in range(len(allvars))], senses=["L"] * len(allvars), rhs=righthand)

    # solve the ILP
    c.solve()
    sol = c.solution

    # print results
    print(sol.get_status())
    print(sol.status[sol.get_status()])
    
    if sol.is_primal_feasible():
        print("[out] ILP cost = {}".format(sol.get_objective_value()))
    else:
        print("[out] ILP infeasible")
    print("[out] ILP done")

def main():
    bf_time = time.time()
    a = VMM(3, 4)
    a.generate()
    brute_force(a)
    print("-----%s seconds-----" % (time.time() - bf_time))
    ilp_time = time.time()
    integer_program(a)
    print("-----%s seconds-----" % (time.time() - ilp_time))

if __name__ == '__main__': main()

