#include <ilcplex/ilocplex.h>
ILOSTLBEGIN

static void usage (const char *progname);

int main (int argc, char **argv) {
    IloEnv env;
    try {
        IloModel model(env);
        IloCplex cplex(env);
        IloObjective obj;
        IloNumVarArray var(env);
        IloRangeArray rng(env);
        cplex.importModel(model, argv[1], obj, var, rng);

        cplex.extract(model);
        cplex.solve();

        IloNumArray vals(env);
        cplex.getValues(vals, var);
        env.out() << "[out] CPLEX value: " << cplex.getObjValue() << endl;
        env.out() << "[out] CPLEX done" << endl;
    } catch (IloException& e) {
        cerr << "[err] CPLEX exception: " << e << endl; 
    } catch (...) {
        cerr << "[err] unknown exception" << endl;
    }

    env.end();
    return 0;
}
