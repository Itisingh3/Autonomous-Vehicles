#include <oqs/oqs.h>
#include <chrono>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <string>
#include <vector>
#include <cmath>
#include <algorithm>
#include <stdexcept>

using Clock = std::chrono::steady_clock;
static double mean(const std::vector<double>& x) { return std::accumulate(x.begin(),x.end(),0.0)/x.size(); }
static double stdev(const std::vector<double>& x) { double m=mean(x),s=0; for(double v:x)s+=(v-m)*(v-m); return std::sqrt(s/(x.size()-1)); }
static double ci(const std::vector<double>& x) { return 1.96*stdev(x)/std::sqrt(static_cast<double>(x.size())); }

template<class F> static std::vector<double> measure(std::size_t n, F fn) {
    std::vector<double> out; out.reserve(n+1);
    fn();
    for (std::size_t i=0;i<n;i++) { auto a=Clock::now(); fn(); auto b=Clock::now(); out.push_back(std::chrono::duration<double,std::micro>(b-a).count()); }
    return out;
}

int main(int argc, char** argv) {
    std::size_t reps=1000; std::string output="../../results/raw/crypto_benchmark.csv";
    for(int i=1;i<argc;i++){ std::string a=argv[i]; if(a=="--repetitions"&&i+1<argc) reps=std::stoul(argv[++i]); else if(a=="--output"&&i+1<argc) output=argv[++i]; }
    OQS_KEM* kem=OQS_KEM_new(OQS_KEM_alg_ml_kem_768); OQS_SIG* sig=OQS_SIG_new(OQS_SIG_alg_ml_dsa_65);
    if(!kem||!sig) { std::cerr<<"required ML-KEM-768/ML-DSA-65 unavailable\n"; return 2; }
    std::vector<uint8_t> kemPk(kem->length_public_key), kemSk(kem->length_secret_key), ct(kem->length_ciphertext), ss(kem->length_shared_secret), ss2(kem->length_shared_secret);
    std::vector<uint8_t> sigPk(sig->length_public_key), sigSk(sig->length_secret_key), signature(sig->length_signature); const std::string msg="cav-pqc-validation-message";
    auto kemKeygen=measure(reps,[&]{ if(OQS_KEM_keypair(kem,kemPk.data(),kemSk.data())!=OQS_SUCCESS) throw std::runtime_error("KEM keygen"); });
    OQS_KEM_keypair(kem,kemPk.data(),kemSk.data());
    auto encap=measure(reps,[&]{ if(OQS_KEM_encaps(kem,ct.data(),ss.data(),kemPk.data())!=OQS_SUCCESS) throw std::runtime_error("KEM encap"); });
    OQS_KEM_encaps(kem,ct.data(),ss.data(),kemPk.data());
    auto decap=measure(reps,[&]{ if(OQS_KEM_decaps(kem,ss2.data(),ct.data(),kemSk.data())!=OQS_SUCCESS) throw std::runtime_error("KEM decap"); });
    if(ss!=ss2) { std::cerr<<"KEM shared secret mismatch\n"; return 3; }
    auto sigKeygen=measure(reps,[&]{ if(OQS_SIG_keypair(sig,sigPk.data(),sigSk.data())!=OQS_SUCCESS) throw std::runtime_error("DSA keygen"); });
    OQS_SIG_keypair(sig,sigPk.data(),sigSk.data()); size_t sigLen=0;
    auto signing=measure(reps,[&]{ if(OQS_SIG_sign(sig,signature.data(),&sigLen,reinterpret_cast<const uint8_t*>(msg.data()),msg.size(),sigSk.data())!=OQS_SUCCESS) throw std::runtime_error("DSA sign"); });
    OQS_SIG_sign(sig,signature.data(),&sigLen,reinterpret_cast<const uint8_t*>(msg.data()),msg.size(),sigSk.data());
    auto verifying=measure(reps,[&]{ if(OQS_SIG_verify(sig,reinterpret_cast<const uint8_t*>(msg.data()),msg.size(),signature.data(),sigLen,sigPk.data())!=OQS_SUCCESS) throw std::runtime_error("DSA verify"); });
    OQS_KEM_free(kem); OQS_SIG_free(sig);
    std::ofstream f(output); if(!f){std::cerr<<"cannot open output\n";return 4;} f<<"algorithm,operation,repetitions,mean_us,median_us,stddev_us,ci95_halfwidth_us,success_count\n";
    auto write=[&](const char* alg,const char* op,const std::vector<double>& x){std::vector<double> y=x;std::sort(y.begin(),y.end()); f<<alg<<","<<op<<","<<x.size()<<","<<mean(x)<<","<<y[y.size()/2]<<","<<stdev(x)<<","<<ci(x)<<","<<x.size()<<"\n";};
    write("ML-KEM-768","key_generation",kemKeygen); write("ML-KEM-768","encapsulation",encap); write("ML-KEM-768","decapsulation",decap); write("ML-DSA-65","key_generation",sigKeygen); write("ML-DSA-65","signing",signing); write("ML-DSA-65","verification",verifying); std::cout<<"Wrote "<<output<<"\n";
}
