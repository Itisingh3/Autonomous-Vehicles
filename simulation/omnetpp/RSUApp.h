#pragma once
#include "veins/modules/application/ieee80211p/DemoBaseApplLayer.h"
#include "CavMsg_m.h"
#include "PqcCrypto.h"

#include <unordered_map>
#include <unordered_set>

namespace cavpqc {
class RSUApp : public veins::DemoBaseApplLayer {
public: void initialize(int stage) override;
protected: void onWSM(veins::BaseFrame1609_4* frame) override;
private:
    struct Pending { Bytes sessionKey; Bytes confirmKey; std::string transcript; omnetpp::simtime_t started; std::string pid; };
    struct HandoverContext { std::string pid; std::string sourceRsu; Bytes contextKey; std::string contextHash; std::string tokenNonce; std::string tokenSignature; std::int64_t issuedMs; std::int64_t expiryMs; };
    PqcCrypto crypto_; SigKeyPair sig_; std::string rsuId_, nextRsu_; Bytes rsuChannelKey_;
    std::unordered_map<std::string, Pending> pending_; std::unordered_map<std::string, HandoverContext> handoverContexts_; std::unordered_set<std::string> usedTokenNonces_;
    omnetpp::simsignal_t handshakeLatencySignal_, handoverLatencySignal_, cryptoMicrosSignal_, successSignal_, failureSignal_;
    void handleVehicleHello(CavMsg* message); void handleFinished(CavMsg* message); void issueHandover(const std::string& sessionId, const Pending& pending); void handleRsuContext(CavMsg* message); void handleHandoverRequest(CavMsg* message); void sendFallback(CavMsg* message, const char* reason); bool fresh(const CavMsg& message) const;
};
}
