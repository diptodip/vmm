#include<iostream>
#include<fstream>
#include<string>

int main(int argc, char** argv) {
    using namespace std;
    int test[100 * 200 * 100 * 200];
    for (int i = 0; i < 100 * 200 * 100 * 200; i++) {
        test[i] = i;
    }
    cout << "DONE" << endl;
    return 0;
}
