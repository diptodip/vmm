#include<iostream>
#include<fstream>
#include<string>

int main(int argc, char** argv) {
    // reading .vmm file
    using namespace std;
    cout << "[out] reading .vmm file" << endl;
    ifstream in(argv[0]);
    string strin;
    getline(in, strin);
    int pm_size = stoi(strin);
    int pm_caps[pm_size];
    for (int i = 0; i < pm_size; i++) {
        getline(in, strin);
        pm_caps[i] = stoi(strin);
    }
    getline(in, strin);
    int vm_size = stoi(strin);
    int vm_loads[vm_size];
    for (int i = 0; i < vm_size; i++) {
        getline(in, strin);
        vm_loads[i] = stoi(strin);
    }
    int distances[pm_size][pm_size];
    for (int i = 0; i < pm_size; i++) {
        for (int j = 0; j < pm_size; j++) {
            in >> strin;
            distances[i][j] = stoi(strin);
        }
    }
    int traffic[vm_size][vm_size];
    for (int i = 0; i < vm_size; i++) {
        for (int j = 0; j < vm_size; j++) {
            in >> strin;
            traffic[i][j] = stoi(strin);
        }
    }
    in.close();

    string assignments[pm_size][vm_size];
    string bounds;
    string variable_matching;
    string assignment_guarantee;
    string capacity_constraint;
    string obj;

    cout << "[out] writing objective and generating variable matching constraints and variable bounds" << endl;

    for(int u = 0; u < pm_size; u++) {
        for (int i = 0; i < vm_size; i++) {
            string varname = "a_" + to_string(u) + "_" + to_string(i);
            assignments[u][i] = varname;
            bounds += "0 <= " + varname + " <= 1\n";
        }
    }
    
    int objcounter = 0;
    int counter = 0;

    for (int u = 0; u < pm_size; u++) {
        for (int v = 0; v < pm_size; v++) {
            for (int i = 0; i < pm_size; i++) {
                for (int j = 0; j < vm_size; j++) {
                    string varname = "a_" + to_string(u) + "_" + to_string(i) + "_" + to_string(v) + "_" + to_string(j);
                    bounds += "0 <= " + varname + " <= 1\n";
                    string matchvar = "c" + to_string(counter) + ": ";
                    matchvar += "-" + varname + " + " + assignments[u][i] + " + " + assignments[v][j] + " <= 1" + "\n";
                    variable_matching += matchvar;
                    counter++;
                    int distance = 0;
                    int demand = 0;
                    distance = distances[u][v];
                    demand = traffic[u][v];
                    int total = 0;
                    if (demand > -1 && distance > -1) {
                        total = distance * demand;
                    }
                    string objterm = to_string(total) + " " + varname;
                    if (objcounter > 0) {
                        objterm = " + " + objterm;
                    }
                    obj += objterm;
                    objcounter++;
                }
            }
        }
    }

    cout << "[out] generating remaining constraints" << endl;

    for (int u = 0; u < pm_size; u++) {
        int capacity = pm_caps[u];
        string constraint;
        for (int i = 0; i < vm_size; i++) {
            int load = vm_loads[i];
            string newterm = to_string(load) + " " + assignments[u][i];
            if (i > 0) {
                newterm = " + " + newterm;
            }
            constraint += newterm;
        }
        constraint = "c" + to_string(counter) + ": " + constraint;
        capacity_constraint += constraint + " <= " + to_string(capacity) + "\n";
        counter++;
    }

    for (int i = 0; i < vm_size; i++) {
        string constraint;
        for (int u = 0; u < pm_size; u++) {
            string newterm = assignments[u][i];
            if (u > 0) {
                newterm = " + " + newterm;
            }
            constraint += newterm;
        }
        constraint = "c" + to_string(counter) + ": " + constraint;
        assignment_guarantee += constraint + " = 1\n";
        counter++;
    }

    cout << "[out] printing .lp file";

    ofstream out(argv[1]);

    out << "Minimize" << endl;
    out << "obj: " << obj << endl;
    out << "Subject To" << endl;
    out << capacity_constraint;
    out << assignment_guarantee;
    out << variable_matching;
    out << "Bounds" << endl;
    out << bounds;
    out << "End" << endl;
    out.close();
}
