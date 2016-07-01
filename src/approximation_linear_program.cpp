#include <fstream>
#include <string>
#include <vector>
#include <time.h>
#include <ilcplex/ilocplex.h>
ILOSTLBEGIN

static void usage (const char *progname);

int main (int argc, char **argv) {
    IloEnv env;
    // reading .vmm file
    env.out() << "[in] reading .vmm file" << endl;
    std::string filein = argv[1];
    std::string fileout = argv[2];
    ifstream in(filein);
    std::string strin;
    std::getline(in, strin);
    const int pm_size = std::stoi(strin);
    int pm_caps[pm_size];
    for (int i = 0; i < pm_size; i++) {
        std::getline(in, strin);
        pm_caps[i] = std::stoi(strin);
    }
    std::getline(in, strin);
    const int vm_size = std::stoi(strin);
    int vm_loads[vm_size];
    for (int i = 0; i < vm_size; i++) {
        std::getline(in, strin);
        vm_loads[i] = std::stoi(strin);
    }
    /*
    int distances[pm_size][pm_size];
    for (int i = 0; i < pm_size; i++) {
        for (int j = 0; j < pm_size; j++) {
            in >> strin;
            distances[i][j] = std::stoi(strin);
        }
    }
    int traffic[vm_size][vm_size];
    for (int i = 0; i < vm_size; i++) {
        for (int j = 0; j < vm_size; j++) {
            in >> strin;
            traffic[i][j] = std::stoi(strin);
        }
    }
    */
    in.close();


    try {
        IloModel model(env);
        IloCplex cplex(env);
        IloObjective obj;
        IloNumVarArray var(env);
        IloRangeArray rng(env);
        cplex.importModel(model, argv[1], obj, var, rng);

        cplex.extract(model);
        clock_t t;
        t = clock();
        cplex.solve();
        t = clock() - t;
        env.out() << "[info] time: " << t << endl;
        /*
        
        int acounter = 0;

        for (int u = 0; u < pm_size; u++) {
            int cap = pm_caps[u];
            for (int i = 0; i < vm_size; i++) {
                std::string varname = "a_" + acounter;
                if (vm_loads[i] > cap) {
                    model.add(varname == 0);
                    cplex.extract(model);
                    cplex.solve();
                }
            }
        }
        */

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
