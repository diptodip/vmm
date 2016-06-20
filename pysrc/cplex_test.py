import cplex

c = cplex.Cplex()
c.read("a_linear.lp")
c.solve()
