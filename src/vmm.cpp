#include<iostream>

class VM {
    public:
        int id;
        int load;
};

class PM {
    public:
        int id;
        int capacity;
};

class VMM {
    public:
        int vm_size;
        int pm_size;
        VM V[vm_size];
        PM P[pm_size];
        
        void generate_random():
            for(int i = 0; i < pm_size; i++) {
                P[i] = P(i, rand())
            }
}
