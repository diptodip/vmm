#include<iostream>
#include<fstream>
#include<string>
#include<vector>

int main(int argc, char** argv) {
    // reading .vmm file
    using namespace std;
    cout << "[in] reading .vmm file" << endl;
    string filein = argv[1];
    string fileout = argv[2];
    ifstream in(filein);
    string strin;
    getline(in, strin);
    const int pm_size = stoi(strin);
    int pm_caps[pm_size];
    for (int i = 0; i < pm_size; i++) {
        getline(in, strin);
        pm_caps[i] = stoi(strin);
    }
    getline(in, strin);
    const int vm_size = stoi(strin);
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

    const int bothsquared = pm_size * pm_size * vm_size * vm_size;
    const int sum = bothsquared + (pm_size * vm_size);

    vector<string> assign_layer(vm_size);
    vector<vector<string> > assignments(pm_size, assign_layer);
    string bounds = "";
    string assignment_guarantee = "";
    string capacity_constraint = "";
    string obj = "[ ";

    cout << "[info] writing objective and generating variable matching constraints and variable bounds" << endl;

    int acounter = 0;
    for(int u = 0; u < pm_size; u++) {
        for (int i = 0; i < vm_size; i++) {
            string varname = "a_" + to_string(acounter);
            assignments[u][i] = varname;
            acounter++;
            bounds += "0 <= " + varname + " <= 1\n";
        }
    }
    
    int objterm = 0;
    int counter = 0;

    cout << "[info] entering quadruple nested loop" << endl;

    for (int u = 0; u < pm_size; u++) {
        for (int v = 0; v < pm_size; v++) {
            for (int i = 0; i < vm_size; i++) {
                for (int j = 0; j < vm_size; j++) {
                    int distance = distances[u][v];
                    int demand = traffic[i][j];
                    int total = 0;
                    if (demand > 0 && distance > 0) {
                        total = distance * demand;
                        if (objterm == 0) {
                            obj += to_string(total) + " " + assignments[u][i] + " * " + assignments[v][j];
                        } else {
                            obj += " + " + to_string(total) + " " + assignments[u][i] + " * " + assignments[v][j];
                        }
                        objterm++;
                    }
                }
            }
        }
    }
    obj += " ] / 2";

    cout << "[info] generating remaining constraints" << endl;

    for (int u = 0; u < pm_size; u++) {
        int capacity = pm_caps[u];
        string constraint;
        for (int i = 0; i < vm_size; i++) {
            int load = vm_loads[i];
            string newterm = " + " + to_string(load) + " " + assignments[u][i];
            if (i == 0) {
                newterm = newterm.substr(3);
            }
            constraint += newterm;
        }
        capacity_constraint += "c" + to_string(counter) + ": " + constraint + " <= " + to_string(capacity) + "\n";
        counter++;
    }

    for (int i = 0; i < vm_size; i++) {
        string constraint;
        for (int u = 0; u < pm_size; u++) {
            string newterm = " + " + assignments[u][i];
            if (u == 0) {
                newterm = newterm.substr(3);
            }
            constraint += newterm;
        }
        assignment_guarantee += "c" + to_string(counter) + ": " + constraint + " = 1\n";
        counter++;
    }

    cout << "[out] printing .lp file" << endl;

    ofstream out(fileout);

    out << "Minimize" << endl;
    out << "obj: ";
    out << obj << endl;
    out << "Subject To" << endl;
    out << capacity_constraint;
    out << assignment_guarantee;
    out << "Bounds" << endl;
    out << bounds;
    out << "Binaries" << endl;
    for (int u = 0; u < pm_size; u++) {
        for (int i = 0; i < vm_size; i++) {
            out << assignments[u][i] << " ";
        }
        out << endl;
    }
    out << "End" << endl;
    out.close();
}
