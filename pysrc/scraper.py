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

for i in range(1000):
    a = VMM(3, 6)
    a.generate()
    x = {}
    try:
        x = brute_force(a)
        a.write("data/random_3p4v_" + str(i) + ".vmm")
        true_cost = calc_cost(x, a)
        iqp = quadratic_integer_program(a)
        ilp = integer_program(a)
        iqp_cost = calc_cost(iqp, a)
        ilp_cost = calc_cost(ilp, a)
        variable.append(true_cost)
        iqp_response.append(iqp_cost - true_cost)
        ilp_response.append(ilp_cost - true_cost)
        write_solution("data/random_3p4v_bf_" + str(i) + ".vmms", x, true_cost)
        write_solution("data/random_3p4v_iqp_" + str(i) + ".vmms", iqp, iqp_cost)
        write_solution("data/random_3p4v_ilp_" + str(i) + ".vmms", ilp, ilp_cost)
    except:
        pass

average_variable = [0, 1]
average_widths = [0.175, 1.175]
iqp_average = np.average(iqp_response)
ilp_average = np.average(ilp_response)
average_response = [iqp_average, ilp_average]

plt.figure()
plt.title("Difference in cost compared to brute force")
plt.xlabel("true brute force cost")
plt.ylabel("difference from brute force cost")
ilp_plot, = plt.plot(variable, ilp_response, 'bo', label='ILP')
iqp_plot, = plt.plot(variable, iqp_response, 'ro', label='IQP')
plt.legend(handles=[ilp_plot, iqp_plot])
plt.savefig("figure1.png", format="png", dpi=72)
plt.clf()

fig, ax = plt.subplots()
plt.title("Average cost difference compared to brute force")
plt.xlabel("average difference in cost")
rects = ax.bar(average_variable, average_response, 0.35, color = 'r')
ax.set_xticks(average_widths)
ax.set_xticklabels(("IQP", "ILP"))
figure2 = plt.plot()
plt.savefig("figure2.png", format="png", dpi=72)
