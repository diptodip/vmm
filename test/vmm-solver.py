#import cvxopt
from vmm import *
import itertools

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

def brute_force(vmm):
    print("[info] enumerating space")
    space = [dict(zip(vmm.virtual_machines, x)) for x in itertools.product(vmm.physical_machines, repeat=vmm.virtual_size)]
    print("[out] space enumerated")
    print("[info] calculating costs")
    costs = [calc_cost(x, vmm) for x in space]
    x, index = min((x, index) for (index, x) in enumerate(costs) if x >= 0)
    print(space)
    for cost in costs:
        print("[out] {}".format(cost))
    print("[out] solution: {}".format(space[index]))
    print("[out] cost: {}".format(x))
    print("[out] done")


a = VMM(5, 6)
a.generate()
brute_force(a)
