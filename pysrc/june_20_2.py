from vmm import *
from vmm_solver import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
plt.style.use("ggplot")

variable = []
iqp_response = []
ilp_response = []
ri_response = []

for i in range(1000):
    a = VMM(3, 6)
    a.generate()
    x = {}
    try:
        x = brute_force(a)
        true_cost = calc_cost(x, a)
        iqp = quadratic_integer_program(a)
        ilp = integer_program(a)
        ri = random_iteration(a, 5000)
        iqp_cost = calc_cost(iqp, a)
        ilp_cost = calc_cost(ilp, a)
        ri_cost = calc_cost(ri, a)
        variable.append(true_cost)
        iqp_response.append(iqp_cost - true_cost)
        ilp_response.append(ilp_cost - true_cost)
        ri_response.append(ri_cost - true_cost)
        a.write("june-20-2/random_3p6v_" + str(i) + ".vmm")
        write_solution("june-20-2/random_3p6v_bf_" + str(i) + ".vmms", x, true_cost)
        write_solution("june-20-2/random_3p6v_iqp_" + str(i) + ".vmms", iqp, iqp_cost)
        write_solution("june-20-2/random_3p6v_ilp_" + str(i) + ".vmms", ilp, ilp_cost)
        write_solution("june-20-2/random_3p6v_ri_" + str(i) + ".vmms", ri, ri_cost)
    except:
        pass

average_variable = [0, 1, 2]
average_widths = [0.117, 1.117, 2.117]
iqp_average = np.average(iqp_response)
ilp_average = np.average(ilp_response)
ri_average = np.average(ri_response)
average_response = [iqp_average, ilp_average, ri_average]

plt.figure()
plt.title("Difference in cost compared to brute force")
plt.xlabel("true brute force cost")
plt.ylabel("difference from brute force cost")
ilp_plot, = plt.plot(variable, ilp_response, 'bo', label='ILP')
iqp_plot, = plt.plot(variable, iqp_response, 'ro', label='IQP')
ri_plot, = plt.plot(variable, ri_response, 'go', label='RI')
plt.legend(handles=[ilp_plot, iqp_plot, ri_plot])
plt.savefig("june-20-2-fig1.png", format="png", dpi=300)
plt.clf()

fig, ax = plt.subplots()
plt.title("Average cost difference compared to brute force")
plt.ylabel("average difference in cost")
rects = ax.bar(average_variable, average_response, 0.35, color = 'r')
ax.set_xticks(average_widths)
ax.set_xticklabels(("IQP", "ILP", "RI"))
figure2 = plt.plot()
plt.savefig("june-20-2-fig2.png", format="png", dpi=300)
