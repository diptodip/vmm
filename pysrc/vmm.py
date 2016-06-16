import random as rng
import numpy as np

MAX_CAPACITY = 3000
MAX_DISTANCE = 100
MAX_LOAD = 1000
MAX_TRAFFIC = 500

class PM(object):
    def __init__(self, number, capacity):
        self.number = number
        self.capacity = capacity
        self.neighbors = set()

    def __str__(self):
        return "PM {}".format(self.number)
    
    def __repr__(self):
        return "PM {}".format(self.number)

class VM(object):
    def __init__(self, number, load):
        self.number = number
        self.load = load
        self.neighbors = set()
        
    def __str__(self):
        return "VM {}".format(self.number)
    
    def __repr__(self):
        return "VM {}".format(self.number)

class VMM(object):
    def __init__(self, physical_size = 3, virtual_size = 4):
        self.physical_size = physical_size
        self.virtual_size = virtual_size
        self.physical_machines = set()
        self.virtual_machines = set()
        self.pm_list = []
        self.vm_list = []
        self.distances = {}
        self.traffic = {}

    def generate(self):
        # initialize physical machines
        for i in xrange(self.physical_size):
            pm = PM(i+1, rng.randint(1, MAX_CAPACITY))
            self.pm_list.append(pm)
            self.physical_machines.add(pm)
        for pm in self.physical_machines:
            pm.neighbors = set(rng.sample(self.physical_machines, rng.randint(1, self.physical_size)))
            pm.neighbors.discard(pm)
            for neighbor in pm.neighbors:
                if not (self.distances.has_key((pm, neighbor)) or self.distances.has_key((neighbor, pm))):
                    self.distances[(pm, neighbor)] = rng.randint(1, MAX_DISTANCE)
                    self.distances[(neighbor, pm)] = self.distances[(pm, neighbor)]
            self.distances[(pm, pm)] = 0

        # initialize virtual machines
        for i in xrange(self.virtual_size):
            vm = VM(i+1, rng.randint(1, MAX_LOAD))
            self.vm_list.append(vm)
            self.virtual_machines.add(vm)
        for vm in self.virtual_machines:
            vm.neighbors = set(rng.sample(self.virtual_machines, rng.randint(1, self.virtual_size)))
            vm.neighbors.discard(vm)
            for neighbor in vm.neighbors:
                if not (self.traffic.has_key((vm, neighbor)) or self.traffic.has_key((neighbor, vm))):
                    self.traffic[(vm, neighbor)] = rng.randint(1, MAX_TRAFFIC)
                    self.traffic[(neighbor, vm)] = self.traffic[(vm, neighbor)]
            self.traffic[(vm, vm)] = 0

    def read(self, filename):
        with open(filename) as f:
            self.physical_size = int(f.readline())
            for i in range(self.physical_size):
                pm = PM(i+1, int(f.readline()))
                self.pm_list.append(pm)
                self.physical_machines.add(pm)
            self.virtual_size = int(f.readline())
            for i in range(self.virtual_size):
                vm = VM(i+1, int(f.readline()))
                self.vm_list.append(vm)
                self.virtual_machines.add(vm)
            for i in range(self.physical_size):
                pm = self.pm_list[i]
                line = f.readline()
                vals = line.split(" ")
                vals = [int(v) for v in vals]
                for j in range(self.physical_size):
                    if vals[j] > 0:
                        pm.neighbors.add(self.pm_list[j])
                        self.distances[(pm, self.pm_list[j])] = vals[j]
            for i in range(self.virtual_size):
                vm = self.vm_list[i]
                line = f.readline()
                vals = line.split(" ")
                vals = [int(v) for v in vals]
                for j in range(self.virtual_size):
                    if vals[j] > 0:
                        vm.neighbors.add(self.vm_list[j])
                        self.traffic[(vm, self.vm_list[j])] = vals[j]
    
    def write(self, filename):
        with open(filename, 'w') as f:
            f.write(str(self.physical_size) + "\n")
            for pm in self.pm_list:
                f.write(str(pm.capacity) + "\n")
            f.write(str(self.virtual_size) + "\n")
            for vm in self.vm_list:
                f.write(str(vm.load) + "\n")
            for pm1 in self.pm_list:
                line = ""
                for pm2 in self.pm_list:
                    if pm1 == pm2:
                        line += "0 "
                    elif self.distances.has_key((pm1, pm2)):
                        line += str(self.distances[(pm1, pm2)]) + " "
                    else:
                        line += "-1 "
                line = line[:-1]
                line += "\n"
                f.write(line)
            for vm1 in self.vm_list:
                line = ""
                for vm2 in self.vm_list:
                    if vm1 == vm2:
                        line += "0 "
                    elif self.traffic.has_key((vm1, vm2)):
                        line += str(self.traffic[(vm1, vm2)]) + " "
                    else:
                        line += "-1 "
                line = line[:-1]
                line += "\n"
                f.write(line)
