from vmm import *
from vmm_solver import *
import time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
plt.style.use("ggplot")

variable = []
bf_response = []
iqp_response = []
ilp_response = []
ri_response = []

# measuring times for various methods
for i in range(4):
    for j in range(50):
        a = 0
        if i == 3:
            a = VMM(i+1, 9)
        else:
            a = VMM(i+1, 2*(i+1))
        a.generate()
        x = {}
        try:
            bf_time = time.time()
            bf = brute_force(a)
            bf_time = time.time() - bf_time
            iqp_time = time.time()
            iqp = quadratic_integer_program(a)
            iqp_time = time.time() - iqp_time
            ilp_time = time.time()
            ilp = integer_program(a)
            ilp_time = time.time() - ilp_time
            ri_time = time.time()
            ri = random_iteration(a, 1000*(a.physical_size*2)*(a.virtual_size))
            ri_time = time.time() - ri_time
            bf_response.append(bf_time)
            iqp_response.append(iqp_time)
            ilp_response.append(ilp_time)
            ri_response.append(ri_time)
            variable.append(i+1)
            a.write("june-21/random_3p6v_" + str(i) + "_" + str(j) + ".vmm")
            #write_solution("june-21/random_3p6v_bf_" + str(i) + ".vmms", bf, true_cost)
            #write_solution("june-21/random_3p6v_iqp_" + str(i) + ".vmms", iqp, iqp_cost)
            #write_solution("june-21/random_3p6v_ilp_" + str(i) + ".vmms", ilp, ilp_cost)
            #write_solution("june-21/random_3p6v_ri_" + str(i) + ".vmms", ri, ri_cost)
        except:
            pass

average_variable = [0, 1, 2, 3]
average_widths = [0.1, 1.1, 2.1, 3.1]
bf_average = np.average(bf_response)
iqp_average = np.average(iqp_response)
ilp_average = np.average(ilp_response)
ri_average = np.average(ri_response)
average_response = [bf_average, iqp_average, ilp_average, ri_average]

plt.figure()
plt.title("Time to completion for VMM instances")
plt.xlabel("problem size in number of physical machines")
plt.ylabel("time (s)")
bf_plot, = plt.plot(variable, bf_response, 'co', label='BF')
ri_plot, = plt.plot(variable, ri_response, 'go', label='RI')
ilp_plot, = plt.plot(variable, ilp_response, 'bo', label='ILP')
iqp_plot, = plt.plot(variable, iqp_response, 'ro', label='IQP')
plt.legend(handles=[bf_plot, ilp_plot, iqp_plot, ri_plot])
plt.savefig("june-21-fig1.png", format="png", dpi=300)
plt.clf()
fig, ax = plt.subplots()
plt.title("Average time to completion for VMM instances")
plt.ylabel("average time (s)")
rects = ax.bar(average_variable, average_response, 0.4, color = 'r')
ax.set_xticks(average_widths)
ax.set_xticklabels(("BF", "IQP", "ILP", "RI"))
figure2 = plt.plot()
plt.savefig("june-21-fig2.png", format="png", dpi=300)
