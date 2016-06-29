import java.io.BufferedReader;
import java.io.FileReader;
import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.PrintWriter;

public class Generator {
    public static void main(String[] args) throws Exception {
        // reading .vmm file
        System.out.println("[in] reading .vmm file");
        String filein = args[1];
        String fileout = args[2];
        BufferedReader in = new BufferedReader(new FileReader(filein));
        int pm_size = Integer.parseInt(in.readLine());
        int[] pm_caps = new int[pm_size];
        for (int i = 0; i < pm_size; i++) {
            pm_caps[i] = Integer.parseInt(in.readLine());
        }
        int vm_size = Integer.parseInt(in.readLine());
        int[] vm_loads = new int[vm_size];
        for (int i = 0; i < vm_size; i++) {
            vm_loads[i] = Integer.parseInt(in.readLine());
        }
        int[][] distances = new int[pm_size][pm_size];
        for (int i = 0; i < pm_size; i++) {
            String line = in.readLine();
            String[] terms = line.split(" ");
            for (int j = 0; j < pm_size; j++) {
                distances[i][j] = Integer.parseInt(terms[j]);
            }
        }
        int[][] traffic = new int[vm_size][vm_size];
        for (int i = 0; i < vm_size; i++) {
            String line = in.readLine();
            String[] terms = line.split(" ");
            for (int j = 0; j < vm_size; j++) {
                traffic[i][j] = Integer.parseInt(terms[j]);
            }
        }
        in.close();

        int bothsquared = pm_size * pm_size * vm_size * vm_size;
        int sum = bothsquared + (pm_size * vm_size);

        String[][] assignments = new String[pm_size][vm_size];
        String bounds;
        String variable_matching;
        String assignment_guarantee;
        String capacity_constraint;
        String obj;
        StringBuilder bounds_builder = new StringBuilder();
        StringBuilder match_builder = new StringBuilder();
        StringBuilder guarantee_builder = new StringBuilder();
        StringBuilder cap_builder = new StringBuilder();
        StringBuilder obj_builder = new StringBuilder();

        System.out.println("[info] writing objective and generating variable matching constraints and variable bounds");

        int acounter = 0;
        int bounds_counter = 0;
        for(int u = 0; u < pm_size; u++) {
            for (int i = 0; i < vm_size; i++) {
                String varname = "a_" + String.valueOf(acounter);
                assignments[u][i] = varname;
                acounter++;
                bounds_builder.append("0 <= ").append(varname).append(" <= 1\n");
            }
        }

        int objcounter = 0;
        int objterm = 0;
        int counter = 0;

        System.out.println("[info] entering quadruple nested loop");

        for (int u = 0; u < pm_size; u++) {
            for (int v = 0; v < pm_size; v++) {
                for (int i = 0; i < pm_size; i++) {
                    for (int j = 0; j < vm_size; j++) {
                        String varname = "obj_" + String.valueOf(objcounter);
                        bounds_builder.append("0 <= ").append(varname).append(" <= 1\n");
                        match_builder.append("c").append(counter).append(": ").append("-").append(varname).append(" + ").append(assignments[u][i]).append(" + ").append(assignments[v][j]).append(" <= 1\n");
                        counter++;
                        int distance = distances[u][v];
                        int demand = traffic[u][v];
                        int total = 0;
                        if (demand > -1 && distance > -1) {
                            total = distance * demand;
                            if (objterm == 0) {
                                obj_builder.append(total).append(" ").append(varname);
                            } else {
                                obj_builder.append(" + ").append(total).append(" ").append(varname);
                            }
                            objterm++;
                        }
                        objcounter++;
                    }
                }
            }
        }

        System.out.println("[info] generating remaining constraints");

        for (int u = 0; u < pm_size; u++) {
            int capacity = pm_caps[u];
            StringBuilder constraint = new StringBuilder();
            for (int i = 0; i < vm_size; i++) {
                int load = vm_loads[i];
                String newterm = " + " + String.valueOf(load) + " " + assignments[u][i];
                if (i == 0) {
                    newterm = newterm.substring(3);
                }
                constraint.append(newterm);
            }
            cap_builder.append("c").append(counter).append(": ").append(constraint).append(" <= ").append(capacity).append("\n");
            counter++;
        }

        for (int i = 0; i < vm_size; i++) {
            StringBuilder constraint = new StringBuilder();
            for (int u = 0; u < pm_size; u++) {
                String newterm = " + " + assignments[u][i];
                if (u == 0) {
                    newterm = newterm.substring(3);
                }
                constraint.append(newterm);
            }
            guarantee_builder.append("c").append(counter).append(": ").append(constraint).append(" = 1\n");
            counter++;
        }

        System.out.println("[out] printing .lp file");

        PrintWriter out = new PrintWriter(new BufferedWriter(new FileWriter(fileout)));

        out.println("Minimize");
        out.println(obj_builder.toString());
        out.println("Subject To");
        out.println(match_builder.toString());
        out.println(cap_builder.toString());
        out.println(guarantee_builder.toString());
        out.println("Bounds");
        out.println(bounds_builder.toString());
        out.println("End");
        out.close();
    }
}
