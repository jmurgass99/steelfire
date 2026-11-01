// thermalKernel.cpp — C++ WebAssembly kernel for EN 1993-1-2 steel thermal
// conductivity k_a(theta) and incremental heating step.

extern "C" {

double steelConductivityLinear(double theta_C) {
    return 54.0 - 0.0333 * theta_C;
}

double steelTempIncrement(double am_v, double h_net, double c_a, double dt_s) {
    return (am_v * h_net * dt_s) / (7850.0 * c_a);
}

}
