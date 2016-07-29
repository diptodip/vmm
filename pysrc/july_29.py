from vmm import *
from vmm_solver import *
import random as rng
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
plt.style.use("ggplot")

variable = []
aa_response = []
sh_response = []

for i in range(10):
    size = rng.randint(100, 500)
    a = VMM(size, 2*size)
    a.generate()
    try:
        aa = appaware(a)
        sh = shuffle(a, size*2*size)
        sh_cost = calc_cost(sh, a)
        aa_cost = calc_cost(aa, a)
        variable.append(size)
        sh_response.append(sh_cost)
        aa_response.append(aa_cost)
        a.write("july-29/random_{0}p{1}v_".format(size, 2*size) + str(i) + ".vmm")
        write_solution("july-29/random_{0}p{1}v_sh_".format(size, 2*size) + str(i) + ".vmms", sh, sh_cost)
        write_solution("july-29/random_{0}p{1}v_aa_".format(size, 2*size) + str(i) + ".vmms", aa, aa_cost)
    except:
        continue

average_variable = [0, 1]
average_widths = [0.1, 1.1]
aa_average = np.average(aa_response)
sh_average = np.average(sh_response)
average_response = [sh_average, aa_average]

plt.figure()
plt.title("Cost of solutions vs. size of problem")
plt.xlabel("size of problem")
plt.ylabel("cost")
aa_plot, = plt.plot(variable, aa_response, 'ro', label='AA')
sh_plot, = plt.plot(variable, sh_response, 'bo', label='SH')

plt.legend(handles=[aa_plot, sh_plot])
plt.savefig("july_29_fig1.png", format="png", dpi=300)
plt.clf()

fig, ax = plt.subplots()
plt.title("Average cost of solutions for various algorithms")
plt.ylabel("average cost")
rects = ax.bar(average_variable, average_response, 0.2, color = 'r')
ax.set_xticks(average_widths)
ax.set_xticklabels(("SH", "AA"))
figure2 = plt.plot()
plt.savefig("july_29_fig2.png", format="png", dpi=300)
