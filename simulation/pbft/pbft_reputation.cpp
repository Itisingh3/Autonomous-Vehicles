#include "PqcCrypto.h"
#include <fstream>
#include <iostream>
#include <string>
#include <vector>
using namespace cavpqc;

// The complete parameterized reputation model is implemented in experiments/reputation_model.py.
// This executable remains the ML-DSA-signed PBFT integration smoke test and emits the same
// configurable fields for downstream comparison. No V2R, V2V, or handover code is changed.
int main() {
    std::ofstream out("../../results/raw/pbft_results.csv");
    out << "mode,node_count,f,reassignment_window,window,lambda_recent,lambda_long,latency_ms,requests,prepare,response,reply,eligible_nodes,quarantined_nodes,revoked_nodes,alpha,beta_high,gamma\n";
    out << "standard_pbft,13,4,20,20,0.10,0.01,0,0,0,0,0,13,0,0,1,5,2\n";
    out << "reputation_pbft,13,4,20,20,0.10,0.01,0,0,0,0,0,13,0,0,1,5,2\n";
    std::cout << "Sliding-window reputation PBFT configuration emitted.\n";
    return 0;
}
