#import cvxopt
#import cplex
from vmm import *
import itertools
import numpy as np
import time
import random as rng
import math

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
        for vm1, vm2 in itertools.combinations(vmm.virtual_machines, 2):
            pm1 = x[vm1]
            pm2 = x[vm2]
            distance = -1
            if vmm.distances.has_key((pm1, pm2)):
                distance = vmm.distances[(pm1, pm2)]
            traffic = -1
            if vmm.traffic.has_key((vm1, vm2)):
                traffic = vmm.traffic[(vm1, vm2)]
            if not distance == -1 and not traffic == -1:
                cost += traffic * distance
        return cost

def write_solution(filename, x, cost):
    sol = [[0] for i in range(len(x))]
    print(len(x))
    for vm in x:
        vm_index = vm.number
        pm_index = x[vm].number
        sol[vm_index] = pm_index
    with open(filename, 'w') as f:
        f.write(str(cost) + "\n")
        for s in sol:
            f.write(str(s) + "\n")

def write_cplex(c, filename):
    c.write(filename)

def brute_force(vmm):
    print("[info] enumerating space")
    space = [dict(zip(vmm.virtual_machines, x)) for x in itertools.product(vmm.physical_machines, repeat=vmm.virtual_size)]
    print("[out] space enumerated")
    costs = [calc_cost(x, vmm) for x in space]
    x, index = min((x, index) for (index, x) in enumerate(costs) if x >= 0)
    #print(space)
    #for cost in costs:
        #print("{}".format(cost))
    print("[out] brute force solution: \n{0}".format(space[index]))
    print("[out] brute force cost: {}".format(x))
    print("[out] brute force done")
    return space[index]

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
            d = 0
            w = 0
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
    return x

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
            distance = 0
            demand = 0
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
    return x

def quadratic_program(vmm):
    P = list(vmm.physical_machines)
    V = list(vmm.virtual_machines)

    c = cplex.Cplex()
    c.set_problem_type(cplex.Cplex.problem_type.QP)
    c.objective.set_sense(c.objective.sense.minimize)
    #c.parameters.mip.limits.nodes.set(100000)

    allvars = []
    assignments = np.ndarray(shape=(vmm.physical_size, vmm.virtual_size), dtype=object)

    # assign variables: a_u_i = 1 if VM i is assigned to PM u, else 0
    for u in range(vmm.physical_size):
        for i in range(vmm.virtual_size):
            varname = "a_" + str(u) + "_" + str(i)
            allvars.append(varname)
            assignments[u, i] = varname

    c.variables.add(names = allvars, lb=[0.0] * len(allvars), ub = [1.0] * len(allvars), types=["C"] * len(allvars))

    # set quadratic objective function: min{sum(w_j_l * d_i_k * a_u_i * a_k_l)}
    for u, v in itertools.product(range(vmm.physical_size), repeat=2):
        for i, j in itertools.product(range(vmm.virtual_size), repeat=2):
            # these are d_u_v and w_i_j from the VMM problem definition
            # (distance and traffic demand, respectively)
            d = 0.0
            w = 0.0
            if vmm.distances.has_key((P[u], P[v])):
                d = vmm.distances[(P[u], P[v])]
            if vmm.traffic.has_key((V[i], V[j])):
                w = vmm.traffic[(V[i], V[j])]
            t = float(d * w)
            c.objective.set_quadratic_coefficients(assignments[u, i], assignments[v, j], t)

    # linear constraint: given i, sum_i(a_u_i) for all u = 1
    # (each VM is assigned to exactly one PM)
    for i in range(vmm.virtual_size):
        variables = []
        for u in range(vmm.physical_size):
            variables.append(assignments[u, i])
        c.linear_constraints.add(lin_expr=[cplex.SparsePair(variables, [1.0] * len(variables))], senses=["E"], rhs=[1.0])

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

    # solve the QP
    c.solve()
    sol = c.solution
    """
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
    #print("[out] IQP cost: {}".format(cost))
    # using CPLEX cost
    """
    print("[out] QP CPLEX cost: {}".format(sol.get_objective_value()))
    print("[out] QP done")
    #return x

def linear_program(vmm):
    vms = list(vmm.virtual_machines)
    loads = [x.load for x in vms]
    pms = list(vmm.physical_machines)
    capacities = [x.capacity for x in pms]
    distances = vmm.distances
    traffic = vmm.traffic
    c = cplex.Cplex()
    c.set_problem_type(cplex.Cplex.problem_type.LP)
    #c.parameters.mip.limits.nodes.set(100000)
    c.objective.set_sense(c.objective.sense.minimize)
    allvars = []
    allcosts = []
    costs = np.ndarray(shape=(vmm.physical_size, vmm.virtual_size, vmm.physical_size, vmm.virtual_size))
    pairs = np.ndarray(shape=(vmm.physical_size, vmm.virtual_size, vmm.physical_size, vmm.virtual_size), dtype=object)
    assignments = np.ndarray(shape=(vmm.physical_size, vmm.virtual_size), dtype=object)

    print("[out] generating variables")
    # assignment variables: pairs["a_u_i-k_l"] = 1 if VM j assigned to PM i AND VM l assigned to PM k, else 0
    for i, k in itertools.product(range(vmm.physical_size), repeat=2):
        for j, l in itertools.product(range(vmm.virtual_size), repeat=2):
            varname = "a_" + str(i) + "_" + str(j) + "-" + str(k) + "_" + str(l)
            allvars.append(varname)
            pairs[i, j, k, l] = varname
            distance = 0
            demand = 0
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

    print("[out] variables generated")

    print("[out] initializing objective and variables")

    c.variables.add(names=allvars, lb=[0.0] * len(allvars), ub=[1.0] * len(allvars), types=["C"] * len(allvars))

    # set objective function
    for i, k in itertools.product(range(vmm.physical_size), repeat=2):
        for j, l in itertools.product(range(vmm.virtual_size), repeat=2):
            # these are d_i_k and w_j_l from the VMM problem definition
            # (distance and traffic demand, respectively)
            t = costs[i, j, k, l]
            c.objective.set_linear(pairs[i, j, k, l], t)

    print("[out] generating constraints")

    # each VM is assigned to exactly one PM
    for j in range(vmm.virtual_size):
        variables = []
        for i in range(vmm.physical_size):
            variables.append(assignments[i, j])
        c.linear_constraints.add(lin_expr=[cplex.SparsePair(variables, [1] * len(variables))], senses=["E"], rhs=[1])

    for j, l in itertools.product(range(vmm.virtual_size), repeat=2):
        for i, k in itertools.product(range(vmm.physical_size), repeat=2):
            if not (i, j) == (k, l):
                constraint = [cplex.SparsePair([assignments[i, j], assignments[k, l], pairs[i, j, k, l]], [1.0, 1.0, -1.0])]
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

    print("[out] constraints complete")
    write_cplex(c, "test.lp")
    print("DONE WRITING")

    # solve the LP
    c.solve()
    sol = c.solution

    """
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
    #print("[out] ILP cost: {}".format(cost))
    # using CPLEX cost
    """
    print("[out] LP CPLEX cost: {}".format(sol.get_objective_value()))
    print("[out] LP done")
    return sol.get_objective_value()

def random_mapping(vmm):
    x = {}
    for vm in vmm.vm_list:
        x[vm] = rng.choice(vmm.pm_list)
    return x

def random_iteration(vmm, k):
    cost = 1e40
    x = {}
    while not cost < 1e40:
        print("[info] starting batch")
        for i in range(k):
            current = random_mapping(vmm)
            current_cost = calc_cost(current, vmm)
            if current_cost == 0:
                cost = current_cost
                x = current
                break
            if current_cost >= 0 and current_cost < cost:
                cost = current_cost
                x = current
    print("[out] RI solution: \n{}".format(x))
    print("[out] RI cost: {}".format(cost))
    print("[out] RI done")
    return x

def likelihood(current_cost, new_cost, T):
    if new_cost >= 0 and new_cost < current_cost:
        return 1
    else:
        return math.exp((abs(current_cost) - abs(new_cost))/T)

def swap(vmm, current, k):
    new = {}
    keys = current.keys()
    for key in keys:
        new[key] = current[key]
    for i in range(k):
        no_step = keys[i]
        if i + 1 < vmm.virtual_size:
            one_step = keys[i + 1]
            new[no_step] = current[one_step]
        else:
            first = keys[0]
            new[no_step] = current[first]
    return new

def simulated_annealing(vmm, T, decay):
    cost = 1e40
    vms = vmm.vm_list
    x = random_mapping(vmm)
    current = x
    current_cost = calc_cost(current, vmm)
    while T > 1:
        new = swap(vmm, current, rng.randint(2, vmm.virtual_size))
        new_cost = calc_cost(new, vmm)
        if likelihood(current_cost, new_cost, T) >= rng.random():
            current = new
            current_cost = new_cost
        if current_cost >= 0 and current_cost < cost:
            cost = current_cost
            x = current
            if cost == 0:
                break
        T *= 1 - decay
    print("[out] SA solution: \n{}".format(x))
    print("[out] SA cost: {}".format(calc_cost(x, vmm)))
    print("[out] SA done")
    return x

def impact(vm, pm, remaining, vmm):
    impact = 0
    for neighbor in vm.neighbors:
        if vmm.traffic.has_key((vm, neighbor)) and vmm.distances.has_key((pm, vmm.initial[neighbor])):
            impact += vmm.traffic[(vm, neighbor)] * vmm.distances[(pm, vmm.initial[neighbor])]
    impact /= (max(vmm.distances.values()) * max(vmm.traffic.values()))
    topology = 0
    for pm_l in vmm.pm_list:
        if vmm.distances.has_key((pm, pm_l)):
            topology += vmm.distances[(pm, pm_l)] * (pm_l.capacity - remaining[pm_l])
    topology /= (vmm.physical_size * max(vmm.distances.values()))
    impact += topology
    return impact

def appaware(vmm):
    vm_list = vmm.vm_list
    pm_list = vmm.pm_list
    total_weight = {}
    remaining = {}
    x = {}
    sorted_vm_list = []

    for pm in pm_list:
        remaining[pm] = pm.capacity

    for vm in vm_list:
        total = 0
        for neighbor in vm.neighbors:
            total += vmm.traffic[(vm, neighbor)]
        total_weight[vm] = total

    sorted_vm_list = sorted(total_weight, key=total_weight.get)
    for vm in sorted_vm_list:
        min_impact = 100000000
        min_pm = PM(-1, -1)
        for pm in pm_list:
            if vm.load < remaining[pm]:
                curr_impact = 0
                curr_impact = impact(vm, pm, remaining, vmm)
                if curr_impact < min_impact:
                    min_impact = curr_impact
                    min_pm = pm
        if min_pm.number > -1:
            x[vm] = min_pm
            remaining[min_pm] -= vm.load
            
    # guarantee a solution is found
    for vm in sorted_vm_list:
        if not x.has_key(vm):
            pm = rng.choice(pm_list)
            while remaining[pm] >= vm.load:
                x[vm] = pm
                remaining[pm] -= vm.load

    cost = calc_cost(x, vmm)
    print("[out] AA solution:")
    print(x)
    print("[out] AA cost: {}".format(cost))
    print("[out] AA done")
    return x

def greedy_unfold(vmm, initial_machine):
    # initialize variables
    vm_list = vmm.vm_list
    pm_list = vmm.pm_list
    total_weight = {}
    total_distance = {}
    remaining = {}
    sorted_vm_list = []
    x = {}
    
    for vm in vm_list:
        x[vm] = initial_machine
        total = 0
        for neighbor in vm.neighbors:
            total += vmm.traffic[(vm, neighbor)]
        total_weight[vm] = total

    for pm in pm_list:
        remaining[pm] = pm.capacity

    sorted_vm_list = sorted(total_weight, key=total_weight.get)

    for vm in sorted_vm_list:
        min_distance = 1e40
        min_neighbor = x[vm]
        for neighbor in x[vm].neighbors:
            if remaining[neighbor] >= vm.load and vmm.distances[(x[vm], neighbor)] < min_distance:
                min_neighbor = neighbor
                min_distance = vmm.distances[(x[vm], neighbor)]
        remaining[x[vm]] += vm.load
        x[vm] = min_neighbor
        remaining[min_neighbor] -= vm.load

    """
    cost = calc_cost(x, vmm)
    print("[out] UF solution:")
    print(x)
    print("[out] UF cost: {}".format(cost))
    print("[out] UF done")
    """
    return x

def iterative_unfolding(vmm):
    cost = 1e40
    x = {}
    for pm in vmm.pm_list:
        current = greedy_unfold(vmm, pm)
        current_cost = calc_cost(current, vmm)
        if current_cost >= 0 and current_cost < cost:
            cost = current_cost
            x = current
    print("[out] IUF solution:")
    print(x)
    print("[out] IUF cost: {}".format(cost))
    print("[out] IUF done")
    return x

def pairwise_unfolding(vmm):
    # initialize variables
    vm_list = vmm.vm_list
    pm_list = vmm.pm_list
    initial_machine = rng.choice(pm_list)
    total_weight = {}
    total_distance = {}
    remaining = {}
    sorted_vm_list = []
    x = {}
    for vm in vm_list:
        x[vm] = initial_machine
        total = 0
        for neighbor in vm.neighbors:
            total += vmm.traffic[(vm, neighbor)]
        total_weight[vm] = total
    for pm in pm_list:
        remaining[pm] = pm.capacity
    sorted_vm_list = sorted(total_weight, key=total_weight.get)

    # iterate through pairs of VMs
    for i, j in itertools.product(range(vmm.virtual_size), repeat=2):
        vm_i = sorted_vm_list[i]
        vm_j = sorted_vm_list[j]
        min_i = x[vm_i]
        min_j = x[vm_j]
        min_cost = 1e40
        for u, v in itertools.product(range(vmm.physical_size), repeat=2):
            pm_u = pm_list[u]
            pm_v = pm_list[v]
            if remaining[pm_u] > vm_i.load and remaining[pm_v] > vm_j.load:
                cost = 0
                distance = 0
                traffic = 0
                if vmm.distances.has_key((pm_u, pm_v)):
                    distance = vmm.distances[(pm_u, pm_v)]
                if vmm.traffic.has_key((vm_i, vm_j)):
                    traffic = vmm.traffic[(vm_i, vm_j)]
                cost = distance * traffic
                if cost < min_cost:
                    min_cost = cost
                    min_i = pm_u
                    min_j = pm_v
        remaining[x[vm_i]] += vm_i.load
        remaining[x[vm_j]] += vm_j.load
        x[vm_i] = min_i
        x[vm_j] = min_j
        remaining[x[vm_i]] -= vm_i.load
        remaining[x[vm_j]] -= vm_j.load

    cost = calc_cost(x, vmm)
    print("[out] PUF solution:")
    print(x)
    print("[out] PUF cost: {}".format(cost))
    print("[out] PUF done")
    return x

def dependency_cost(vm, pm, x, vmm):
    cost = 0
    for neighbor in vm.neighbors:
        cost += vmm.traffic[(vm, neighbor)] * vmm.distances[(pm, x[neighbor])]
    return cost

def shuffle(vmm, k):
    # initialize variables
    vm_list = vmm.vm_list
    pm_list = vmm.pm_list
    total_weight = {}
    remaining = {}
    x = {}
    sorted_vm_list = []

    for pm in pm_list:
        remaining[pm] = pm.capacity

    for vm in vm_list:
        total = 0
        for neighbor in vm.neighbors:
            total += vmm.traffic[(vm, neighbor)]
        total_weight[vm] = total

    sorted_vm_list = sorted(total_weight, key=total_weight.get)

    # run appaware
    for vm in sorted_vm_list:
        min_impact = 100000000
        min_pm = PM(-1, -1)
        for pm in pm_list:
            if vm.load < remaining[pm]:
                curr_impact = 0
                curr_impact = impact(vm, pm, remaining, vmm)
                if curr_impact < min_impact:
                    min_impact = curr_impact
                    min_pm = pm
        if min_pm.number > -1:
            x[vm] = min_pm
            remaining[min_pm] -= vm.load

    # guarantee a solution is found
    for vm in sorted_vm_list:
        if not x.has_key(vm):
            pm = rng.choice(pm_list)
            while remaining[pm] >= vm.load:
                x[vm] = pm
                remaining[pm] -= vm.load
    
    # while compute time available, shuffle solution
    min_cost = calc_cost(x, vmm)
    for i in range(k):
        vm = rng.choice(sorted_vm_list)
        pm = rng.choice(pm_list)
        old_pm = x[vm]
        old_contribution = 0
        new_contribution = 0
        for neighbor in vm.neighbors:
            old_contribution += vmm.traffic[(vm, neighbor)] * vmm.distances[x[vm], x[neighbor]]
            new_contribution += vmm.traffic[(vm, neighbor)] * vmm.distances[pm, x[neighbor]]
        x[vm] = pm
        difference = new_contribution - old_contribution
        if remaining[pm] > vm.load and difference < 0:
            remaining[old_pm] += vm.load
            remaining[pm] -= vm.load
        else:
            x[vm] = old_pm
    
    cost = calc_cost(x, vmm)
    print("[out] SHAA solution:")
    print(x)
    print("[out] SHAA cost: {}".format(cost))
    print("[out] SHAA done")
    return x

def main():
    a = VMM(100, 200)
    a.generate()

    #bf_time = time.time()
    #brute_force(a)
    #print("-----%s seconds-----" % (time.time() - bf_time))

    #iqp_time = time.time()
    #quadratic_integer_program(a)
    #print("-----%s seconds-----" % (time.time() - iqp_time))

    #ilp_time = time.time()
    #integer_program(a)
    #print("-----%s seconds-----" % (time.time() - ilp_time))

    #qp_time = time.time()
    #quadratic_program(a)
    #print("-----%s seconds-----" % (time.time() - qp_time))

    #lp_time = time.time()
    #linear_program(a)
    #print("-----%s seconds-----" % (time.time() - lp_time))

    aa_time = time.time()
    appaware(a)
    print("-----%s seconds-----" % (time.time() - aa_time))

    ri_time = time.time()
    shuffle(a, a.virtual_size * a.physical_size)
    print("-----%s seconds-----" % (time.time() - ri_time))

if __name__ == "__main__": main()
