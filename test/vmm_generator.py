import random as rng

MAX_CAPACITY = 5000
MAX_DISTANCE = 100
MAX_LOAD = 1000
MAX_TRAFFIC = 500

class PM:
    def __init__(self, capacity):
        self.capacity = capacity
        self.neighbors = set()

class VM:
    def __init__(self, load):
        self.load = load
        self.neighbors = set()

class VMM:
    def __init__(self, physical_size = 10, virtual_size = 20):
        self.physical_size = physical_size
        self.virtual_size = virtual_size
        self.physical_machines = set()
        self.virtual_machines = set()
        self.distances = {}
        self.traffic_demands = {}

    def generate(self):
        # initialize physical machines
        for i in xrange(self.physical_size):
            self.physical_machines.add(PM(rng.rand_int(1, MAX_CAPACITY)))
        for pm in self.physical_machines:
            pm.neighbors = set(rng.sample(self.physical_machines, rng.randint(1, physical_size)))
            pm.neighbors.remove(pm)
            for neighbor in pm.neighbors:
                self.distances[(pm, neighbor))] = rng.randint(1, MAX_DISTANCE)

        # initialize virtual machines
        for i in xrange(self.virtual_size):
            self.virtual_machines.add(PM(rng.randint(1, MAX_LOAD)))
        for vm in self.virtual_machines:
            vm.neighbors = set(rng.sample(self.virtual_machines, rng.randint(1, virtual_size)))
            vm.neighbors.remove(vm)
            for neighbor in vm.neighbors:
                self.distances[(vm, neighbor))] = rng.randint(1, MAX_TRAFFIC)
