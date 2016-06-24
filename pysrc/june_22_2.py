from vmm import *
from vmm_solver import *
import time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
plt.style.use("ggplot")

variable = []
iqp_response = []
ilp_response = []
lp_response = []

# measuring times for various methods
for i in range(10):
    for j in range(10):
        a = VMM(i+1, 2*(i+1))
        a.generate()
        try:
            iqp_time = time.time()
            iqp = quadratic_integer_program(a)
            iqp_time = time.time() - iqp_time
            ilp_time = time.time()
            ilp = integer_program(a)
            ilp_time = time.time() - ilp_time
            lp_time = time.time()
            lp = linear_program(a)
            print("NO LP ERROR")
            lp_time = time.time() - lp_time
            iqp_response.append(iqp_time)
            ilp_response.append(ilp_time)
            lp_response.append(lp_time)
            variable.append(i+1)
            a.write("june-22-2/random_" + str(j) + "pdoublev_" + str(i) + ".vmm")
            #write_solution("june-21/random_3p6v_bf_" + str(i) + ".vmms", bf, true_cost)
            #write_solution("june-21/random_3p6v_iqp_" + str(i) + ".vmms", iqp, iqp_cost)
            #write_solution("june-21/random_3p6v_ilp_" + str(i) + ".vmms", ilp, ilp_cost)
            #write_solution("june-21/random_3p6v_ri_" + str(i) + ".vmms", ri, ri_cost)
        except:
            continue

average_variable = [0, 1, 2]
average_widths = [0.1, 1.1, 2.1]
iqp_average = np.average(iqp_response)
ilp_average = np.average(ilp_response)
lp_average = np.average(lp_response)
average_response = [iqp_average, ilp_average, lp_average]

plt.figure()
plt.title("Time to completion for VMM instances")
plt.xlabel("problem size in number of physical machines")
plt.ylabel("time (s)")
iqp_plot, = plt.plot(variable, iqp_response, 'ro', label='IQP')
ilp_plot, = plt.plot(variable, ilp_response, 'bo', label='ILP')
lp_plot, = plt.plot(variable, lp_response, 'go', label='LP')
plt.legend(handles=[iqp_plot, ilp_plot, lp_plot])
plt.savefig("june-22-2-fig1.png", format="png", dpi=300)
plt.clf()
fig, ax = plt.subplots()
plt.title("Average time to completion for VMM instances")
plt.ylabel("average time (s)")
rects = ax.bar(average_variable, average_response, 0.3, color = 'r')
ax.set_xticks(average_widths)
ax.set_xticklabels(("IQP", "ILP", "LP"))
figure2 = plt.plot()
plt.savefig("june-22-2-fig2.png", format="png", dpi=300)
