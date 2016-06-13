#import cvxopt
from vmm import *
import itertools
import multiprocessing as mp
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
    #space = []
    #results = []
    #pool = mp.Pool(processes=vmm.physical_size)
    #pms = list(vmm.physical_machines)
    #reps = vmm.physical_size - 1
    #print("[out] space enumerated")
    #print("[info] calculating costs")
    #for i in xrange(vmm.physical_size):
    #    part = 0
    #    if i == reps:
    #        part = pms[i:]
    #    else:
    #        part = pms[i:i+1]
    #    results.append(pool.apply_async(generate_mapping(part, pms, vmm.virtual_machines, space, reps)))
    print("[out] space enumerated")
    #costs = [calc_cost(x, vmm) for x in space]
    #x, index = min((x, index) for (index, x) in enumerate(costs) if x >= 0)
    #print(space)
    #for cost in costs:
        #print("[out] {}".format(cost))
    #print("[out] solution: {}".format(space[index]))
    #print("[out] cost: {}".format(x))
    #print("[out] done")

def main():
    start_time = time.time()
    a = VMM(8, 8)
    a.generate()
    brute_force(a)
    print("-----%s seconds-----" % (time.time() - start_time))

if __name__ == '__main__': main()

