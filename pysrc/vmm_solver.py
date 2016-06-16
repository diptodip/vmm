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
        for vm1, vm2 in itertools.product(vmm.virtual_machines, repeat=2):
            pm1 = x[vm1]
            pm2 = x[vm2]
            distance = -1
            if vmm.distances.has_key((pm1, pm2)):
                distance = vmm.distances[(pm1, pm2)]
            traffic = -1
            if vmm.traffic.has_key((vm1, vm2)):
                traffic = vmm.traffic[(vm1, vm2)]
            if not distance == -1 and not traffic == -1:
                cost += (traffic * distance)
                updated += 1
        if updated > 0:
            return cost
        else:
            return -2

def write_solution(filename, x, cost):
    sol = [0] * len(x)
    for vm in x:
        vm_index = vm.name
        pm_index = x[vm].name
        sol[vm_index] = pm_index
    with open(filename, w) as f:
        f.write(str(cost) + "\n")
        for s in sol:
            f.write(str(s) + "\n")

def brute_force(vmm):
    print("[info] enumerating space")
    space = [dict(zip(vmm.virtual_machines, x)) for x in itertools.product(vmm.physical_machines, repeat=vmm.virtual_size)]
    print("[out] space enumerated")
    costs = [calc_cost(x, vmm) for x in space]
    x, index = min((x, index) for (index, x) in enumerate(costs) if x >= 0)
    #print(space)
    #for cost in positive_costs:
        #print("{}".format(cost))
    print("[out] brute force solution: \n{0}".format(space[index]))
    print("[out] brute force cost: {}".format(x))
    print("[out] brute force done")

def quadratic_integer_program(vmm):
    P = list(vmm.physical_machines)
    V = list(vmm.virtual_machines)

    c = cplex.Cplex()
    c.objective.set_sense(c.objective.sense.minimize)
    c.parameters.mip.limits.nodes.set(100000)
    
    allvars = []
    assignments = np.ndarray(shape=(vmm.physical_size, vmm.virtual_size), dtype=object)
    
    # assign variables: a_u_i = 1 if VM i is assigned to PM u, else 0
    for u in range(vmm.physical_size):
        for i in range(vmm.virtual_size):
            varname = "a_" + str(u) + "_" + str(i)
            allvars.append(varname)
            assignments[u, i] = varname

    c.variables.add(names = allvars, lb=[0] * len(allvars), ub = [1] * len(allvars), types=["B"] * len(allvars))
    
    # set quadratic objective function: min{sum(w_j_l * d_i_k * a_u_i * a_k_l)}
    for u, v in itertools.product(range(vmm.physical_size), repeat=2):
        for i, j in itertools.product(range(vmm.virtual_size), repeat=2):
            # these are d_u_v and w_i_j from the VMM problem definition
            # (distance and traffic demand, respectively)
            d = cplex.infinity
            w = cplex.infinity
            if vmm.distances.has_key((P[u], P[v])):
                d = vmm.distances[(P[u], P[v])]
            if vmm.traffic.has_key((V[i], V[j])):
                w = vmm.traffic[(V[i], V[j])]
            t = d * w
            c.objective.set_quadratic_coefficients(assignments[u, i], assignments[v, j], t)

    # linear constraint: given i, sum_i(a_u_i) for all u = 1
    # (each VM is assigned to exactly one PM)
    for i in range(vmm.virtual_size):
        variables = []
        for u in range(vmm.physical_size):
            variables.append(assignments[u, i])
        c.linear_constraints.add(lin_expr=[cplex.SparsePair(variables, [1] * len(variables))], senses=["E"], rhs=[1])

    # linear constraint: given u, sum_u(a_u_i * load(i)) for all i <= capacity(i)
    # (the loads of the assigned VMs do not exceed the capacity of any PM)
    for u in range(vmm.physical_size):
        variables = []
        coefficients = []
        righthand = P[u].capacity
        for i in range(vmm.virtual_size):
            variables.append(assignments[u, i])
            coefficients.append(V[i].load)
        c.linear_constraints.add(lin_expr=[cplex.SparsePair(variables, coefficients)], senses=["L"], rhs=[righthand])

    # solve the IQP
    c.solve()
    sol = c.solution

    # check solution feasibility
    found = 0
    for j in range(vmm.virtual_size):
        for i in range(vmm.physical_size):
            s = sol.get_values(assignments[i, j])
            if s == 1:
                found += 1
    if found > vmm.virtual_size:
        print("[out] IQP assigned VM to multiple PMs")
    else:
        print("[out] IQP did not assign VM to multiple PMs")

    # manually calculate solution cost (CPLEX PLSSSSSSS)
    x = {}
    for i in range(vmm.physical_size):
        for j in range(vmm.virtual_size):
            s = sol.get_values(assignments[i, j])
            if s == 1:
                x[V[j]] = P[i]
    print(x)
    
    cost = calc_cost(x, vmm)

    # print results
    #print(sol.get_status())
    #print(sol.status[sol.get_status()])

    # using manually calculated cost
    print("[out] IQP cost: {}".format(cost))
    # using CPLEX cost
    print("[out] IQP CPLEX cost: {}".format(sol.get_objective_value()))
    print("[out] IQP done")

def integer_program(vmm):
    vms = list(vmm.virtual_machines)
    loads = [x.load for x in vms]
    pms = list(vmm.physical_machines)
    capacities = [x.capacity for x in pms]
    distances = vmm.distances
    traffic = vmm.traffic
    c = cplex.Cplex()
    c.parameters.mip.limits.nodes.set(100000)
    c.objective.set_sense(c.objective.sense.minimize)
    allvars = []
    allcosts = []
    costs = np.ndarray(shape=(vmm.physical_size, vmm.virtual_size, vmm.physical_size, vmm.virtual_size))
    pairs = np.ndarray(shape=(vmm.physical_size, vmm.virtual_size, vmm.physical_size, vmm.virtual_size), dtype=object)
    assignments = np.ndarray(shape=(vmm.physical_size, vmm.virtual_size), dtype=object)

    # assignment variables: pairs["a_u_i-k_l"] = 1 if VM j assigned to PM i AND VM l assigned to PM k, else 0
    for i, k in itertools.product(range(vmm.physical_size), repeat=2):
        for j, l in itertools.product(range(vmm.virtual_size), repeat=2):
            varname = "a_" + str(i) + "_" + str(j) + "-" + str(k) + "_" + str(l)
            allvars.append(varname)
            pairs[i, j, k, l] = varname
            distance = cplex.infinity
            demand = cplex.infinity
            if vmm.distances.has_key((pms[i], pms[k])) and vmm.traffic.has_key((vms[j], vms[l])):
                distance = vmm.distances[(pms[i], pms[k])]
                demand = vmm.traffic[(vms[j], vms[l])]
            allcosts.append(distance * demand)
            costs[i, j, k, l] = distance * demand

    # assignment variables: assignments["a_i_j"] = 1 if VM j is assigned to PM i, else 0
    for i in range(vmm.physical_size):
        for j in range(vmm.virtual_size):
            varname = "a_" + str(i) + "_" + str(j)
            allvars.append(varname)
            assignments[i, j] = varname

    c.variables.add(names=allvars, lb=[0] * len(allvars), ub=[1] * len(allvars), types=["B"] * len(allvars))

    # set objective function
    for i, k in itertools.product(range(vmm.physical_size), repeat=2):
        for j, l in itertools.product(range(vmm.virtual_size), repeat=2):
            # these are d_i_k and w_j_l from the VMM problem definition
            # (distance and traffic demand, respectively)
            t = costs[i, j, k, l]
            c.objective.set_linear(pairs[i, j, k, l], t)

    
    # each VM is assigned to exactly one PM
    for j in range(vmm.virtual_size):
        variables = []
        for i in range(vmm.physical_size):
            variables.append(assignments[i, j])
        c.linear_constraints.add(lin_expr=[cplex.SparsePair(variables, [1] * len(variables))], senses=["E"], rhs=[1])

    for j, l in itertools.product(range(vmm.virtual_size), repeat=2):
        for i, k in itertools.product(range(vmm.physical_size), repeat=2):
            if not (i, j) == (k, l):
                constraint = [cplex.SparsePair([assignments[i, j], assignments[k, l], pairs[i, j, k, l]], [1, 1, -1])]
                righthand = 1
                c.linear_constraints.add(lin_expr=constraint, senses=["L"], rhs=[righthand])

    # linear constraint: given u, sum_u(a_u_i * load(i)) for all i <= capacity(i)
    # (the loads of the assigned VMs do not exceed the capacity of any PM)
    for u in range(vmm.physical_size):
        variables = []
        coefficients = []
        righthand = pms[u].capacity
        for i in range(vmm.virtual_size):
            variables.append(assignments[u, i])
            coefficients.append(vms[i].load)
        c.linear_constraints.add(lin_expr=[cplex.SparsePair(variables, coefficients)], senses=["L"], rhs=[righthand])
    
    # solve the ILP
    c.solve()
    sol = c.solution

    # check solution feasibility
    found = 0
    for j in range(vmm.virtual_size):
        for i in range(vmm.physical_size):
            s = sol.get_values(assignments[i, j])
            if s == 1:
                found += 1
    if found > vmm.virtual_size:
        print("[out] ILP assigned VM to multiple PMs")
    else:
        print("[out] ILP did not assign VM to multiple PMs")

    # manually calculate solution cost (CPLEX PLSSSSSSS)
    x = {}
    for i in range(vmm.physical_size):
        for j in range(vmm.virtual_size):
            s = sol.get_values(assignments[i, j])
            if s == 1:
                x[vms[j]] = pms[i]
    print(x)
    
    cost = calc_cost(x, vmm)

    # print results
    #print(sol.get_status())
    #print(sol.status[sol.get_status()])

    # using manually calculated cost
    print("[out] ILP cost: {}".format(cost))
    # using CPLEX cost
    print("[out] ILP CPLEX cost: {}".format(sol.get_objective_value()))
    print("[out] ILP done")

def main():
    a = VMM(4, 6)
    a.generate()

    bf_time = time.time()
    brute_force(a)
    print("-----%s seconds-----" % (time.time() - bf_time))
    
    ilp_time = time.time()
    quadratic_integer_program(a)
    print("-----%s seconds-----" % (time.time() - ilp_time))

if __name__ == "__main__": main()
