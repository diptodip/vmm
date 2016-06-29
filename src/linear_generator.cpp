#include<iostream>
#include<fstream>
#include<string>
#include<vector>

int main(int argc, char** argv) {
    // reading .vmm file
    using namespace std;
    cout << "[out] reading .vmm file" << endl;
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
    string bounds;
    string variable_matching;
    string assignment_guarantee;
    string capacity_constraint(pm_size);
    string obj(bothsquared);

    cout << "[out] writing objective and generating variable matching constraints and variable bounds" << endl;

    int acounter = 0;
    int bounds_counter = 0;
    for(int u = 0; u < pm_size; u++) {
        for (int i = 0; i < vm_size; i++) {
            string varname += "a_" + to_string(acounter);
            assignments[u][i] = varname;
            acounter++;
            varname += " <= 1\n";
            bounds += "0 <=" + varname;
        }
    }
    
    int objcounter = 0;
    int counter = 0;
    int vmatch_counter = 0;

    cout << "[out] entering quadruple nested loop" << endl;

    for (int u = 0; u < pm_size; u++) {
        for (int v = 0; v < pm_size; v++) {
            for (int i = 0; i < pm_size; i++) {
                for (int j = 0; j < vm_size; j++) {
                    string varname = "obj_" + to_string(objcounter);
                    bounds[bounds_counter] = varname;
                    bounds_counter++;
                    string matchvar;
                    matchvar += "-" + varname + " + " + assignments[u][i] + " + " + assignments[v][j];
                    variable_matching += matchvar;
                    vmatch_counter++;
                    counter++;
                    int distance = distances[u][v];
                    int demand = traffic[u][v];
                    int total = 0;
                    if (demand > -1 && distance > -1) {
                        total = distance * demand;
                    }
                    string objterm += to_string(total) + " " + varname;
                    obj[objcounter] = objterm;
                    objcounter++;
                }
            }
        }
    }

    cout << "[out] generating remaining constraints" << endl;

    int cap_counter = 0;

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
        capacity_constraint[cap_counter] = constraint + " <= " + to_string(capacity);
        cap_counter++;
        counter++;
    }

    int guarantee_counter = 0;

    for (int i = 0; i < vm_size; i++) {
        string constraint;
        for (int u = 0; u < pm_size; u++) {
            string newterm = assignments[u][i];
            if (u > 0) {
                newterm = " + " + newterm;
            }
            constraint += newterm;
        }
        assignment_guarantee[guarantee_counter] = constraint;
        guarantee_counter++;
        counter++;
    }

    cout << "[out] printing .lp file";

    ofstream out(fileout);

    out << "Minimize" << endl;
    out << "obj: " << obj[0];
    for (int i = 1; i < sizeof(obj)/sizeof(obj[0]); i++) {
        out << " + " << obj[i];
    }
    out << endl;
    counter = 0;
    out << "Subject To" << endl;
    for (int i = 0; i < capacity_constraint.size(); i++) {
        out << "c" << counter << ": " << capacity_constraint[0] << endl;
        counter++;
    }
    for (int i = 0; i < assignment_guarantee.size(); i++) {
        out << "c" << counter << ": " << assignment_guarantee[0] << " = 1" << endl;
        counter++;
    }
    for (int i = 0; i < variable_matching.size(); i++) {
        out << "c" << counter << ": " << variable_matching[0] << " <= 1" << endl;
        counter++;
    }
    out << "Bounds" << endl;
    for (int i = 0; i < bounds.size(); i++) {
        out << "0 <= " << bounds[0] << " <= 1" << endl;
    }
    out << "End" << endl;
    out.close();
}
