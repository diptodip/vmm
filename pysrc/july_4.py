from vmm import *
from vmm_solver import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
plt.style.use("ggplot")

variable = []
aa_response = []
ri_response = []

for i in range(1000):
    a = VMM(4, 8)
    a.generate()
    bf = {}
    try:
        bf = brute_force(a)
        ri = random_iteration(a, 200 * a.physical_size * a.virtual_size)
        aa = appaware(a)
        bf_cost = calc_cost(bf, a)
        ri_cost = calc_cost(ri, a)
        aa_cost = calc_cost(aa, a)
        variable.append(bf_cost)
        ri_response.append(ri_cost - bf_cost)
        aa_response.append(aa_cost - bf_cost)
        a.write("july-4/random_4p8v_" + str(i) + ".vmm")
        write_solution("july-4/random_4p8v_bf_" + str(i) + ".vmms", bf, bf_cost)
        write_solution("july-4/random_4p8v_ri_" + str(i) + ".vmms", ri, ri_cost)
        write_solution("july-4/random_4p8v_aa_" + str(i) + ".vmms", aa, aa_cost)
    except:
        continue

average_variable = [0, 1]
average_widths = [0.1, 1.1]
bf_average = np.average(variable)
aa_average = np.average(aa_response)
ri_average = np.average(ri_response)
average_response = [ri_average, aa_average]
aa_percent = 100.0 * aa_average / bf_average
ri_percent = 100.0 * ri_average / bf_average
percent_response = [ri_percent, aa_percent]

plt.figure()
plt.title("Cost difference compared to brute force")
plt.xlabel("true brute force cost")
plt.ylabel("cost difference")
ri_plot, = plt.plot(variable, ri_response, 'bo', label='RI')
aa_plot, = plt.plot(variable, aa_response, 'ro', label='AA')

plt.legend(handles=[ri_plot, aa_plot])
plt.savefig("july_4_fig1.png", format="png", dpi=300)
plt.clf()

fig, ax = plt.subplots()
plt.title("Average cost difference compared to brute force")
plt.ylabel("average cost difference")
rects = ax.bar(average_variable, average_response, 0.2, color = 'r')
ax.set_xticks(average_widths)
ax.set_xticklabels(("RI", "AA"))
figure2 = plt.plot()
plt.savefig("july_4_fig2.png", format="png", dpi=300)

fig, ax = plt.subplots()
plt.title("Average percent cost difference compared to brute force")
plt.ylabel("average percent difference in cost")
rects = ax.bar(average_variable, percent_response, 0.2, color = 'r')
ax.set_xticks(average_widths)
ax.set_xticklabels(("RI", "AA"))
figure2 = plt.plot()
plt.savefig("july_4_fig3.png", format="png", dpi=300)
