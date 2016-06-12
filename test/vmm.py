import random as rng
import numpy as np

MAX_CAPACITY = 5000
MAX_DISTANCE = 100
MAX_LOAD = 1000
MAX_TRAFFIC = 500

class PM(object):
    def __init__(self, capacity):
        self.capacity = capacity
        self.neighbors = set()

class VM(object):
    def __init__(self, load):
        self.load = load
        self.neighbors = set()

class VMM(object):
    def __init__(self, physical_size = 3, virtual_size = 4):
        self.physical_size = physical_size
        self.virtual_size = virtual_size
        self.physical_machines = set()
        self.virtual_machines = set()
        self.distances = {}
        self.traffic = {}

    def generate(self):
        # initialize physical machines
        for i in xrange(self.physical_size):
            self.physical_machines.add(PM(rng.randint(1, MAX_CAPACITY)))
        for pm in self.physical_machines:
            pm.neighbors = set(rng.sample(self.physical_machines, rng.randint(1, self.physical_size)))
            pm.neighbors.discard(pm)
            for neighbor in pm.neighbors:
                if not (self.distances.has_key((pm, neighbor)) or self.distances.has_key((neighbor, pm))):
                    self.distances[(pm, neighbor)] = rng.randint(1, MAX_DISTANCE)
                    self.distances[(neighbor, pm)] = self.distances[(pm, neighbor)]

        # initialize virtual machines
        for i in xrange(self.virtual_size):
            self.virtual_machines.add(VM(rng.randint(1, MAX_LOAD)))
        for vm in self.virtual_machines:
            vm.neighbors = set(rng.sample(self.virtual_machines, rng.randint(1, self.virtual_size)))
            vm.neighbors.discard(vm)
            for neighbor in vm.neighbors:
                if not (self.traffic.has_key((vm, neighbor)) or self.traffic.has_key((neighbor, vm))):
                    self.traffic[(vm, neighbor)] = rng.randint(1, MAX_TRAFFIC)
                    self.traffic[(neighbor, vm)] = self.traffic[(vm, neighbor)]
