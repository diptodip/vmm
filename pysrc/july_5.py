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
iu_response = []

for i in range(500):
    size = rng.randint(100, 500)
    a = VMM(size, 2*size)
    a.generate()
    bf = {}
    try:
        aa = appaware(a)
        iu = iterative_unfolding(a)
        iu_cost = calc_cost(iu, a)
        aa_cost = calc_cost(aa, a)
        variable.append(size)
        iu_response.append(iu_cost)
        aa_response.append(aa_cost)
        a.write("july-5/random_{0}p8{1}_".format(size, 2*size) + str(i) + ".vmm")
        write_solution("july-5/random_{0}p{1}v_iu_".format(size, 2*size) + str(i) + ".vmms", iu, iu_cost)
        write_solution("july-5/random_{0}p{1}v_aa_".format(size, 2*size) + str(i) + ".vmms", aa, aa_cost)
    except:
        continue

average_variable = [0, 1]
average_widths = [0.1, 1.1]
aa_average = np.average(aa_response)
iu_average = np.average(iu_response)
average_response = [iu_average, aa_average]
percent_response = [iu_percent, aa_percent]

plt.figure()
plt.title("Cost of solutions vs. size of problem")
plt.xlabel("size of problem")
plt.ylabel("cost")
iu_plot, = plt.plot(variable, iu_response, 'bo', label='IU')
aa_plot, = plt.plot(variable, aa_response, 'ro', label='AA')

plt.legend(handles=[iu_plot, aa_plot])
plt.savefig("july_5_fig1.png", format="png", dpi=300)
plt.clf()

fig, ax = plt.subplots()
plt.title("Average cost of solutions for various algorithms")
plt.ylabel("average cost")
rects = ax.bar(average_variable, average_response, 0.2, color = 'r')
ax.set_xticks(average_widths)
ax.set_xticklabels(("RI", "AA"))
figure2 = plt.plot()
plt.savefig("july_5_fig2.png", format="png", dpi=300)
