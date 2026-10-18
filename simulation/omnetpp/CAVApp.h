#pragma once
#include "veins/modules/application/ieee80211p/DemoBaseApplLayer.h"
#include "CavMsg_m.h"
#include "PqcCrypto.h"

namespace cavpqc {
class CAVApp : public veins::DemoBaseApplLayer {
public: void initialize(int stage) override; ~CAVApp() override;
protected: void onWSM(veins::BaseFrame1609_4* frame) override; void handleSelfMsg(omnetpp::cMessage* msg) override;
private:
    PqcCrypto crypto_; KemKeyPair kem_; SigKeyPair sig_; std::string pid_, targetRsu_, nextRsu_, sessionId_, helloTranscript_, handoverTokenSignature_; Bytes vehicleNonce_, sessionKey_, handoverContextKey_, handoverNonce_; omnetpp::cMessage* startEvent_ = nullptr;
    omnetpp::simsignal_t handshakeLatencySignal_, handoverLatencySignal_, cryptoMicrosSignal_, successSignal_, failureSignal_;
    omnetpp::simtime_t handshakeStarted_, handoverStarted_; double fullHandshakeLatency_ = -1; bool fallbackUsed_ = false, handoverComplete_ = false;
    void sendVehicleHello(); void handleServerHello(CavMsg* message); void sendFinished(CavMsg* serverHello, const Bytes& confirmKey); void handleFullHandshakeAck(CavMsg* message); void handleHandoverOffer(CavMsg* message); void sendHandoverRequest(CavMsg* offer); void handleHandoverConfirm(CavMsg* message); void handleFallback(CavMsg* message); void writeHandoverResult(double latency, bool success) const;
    std::string helloBytes() const; Bytes deriveSessionKey(const CavMsg& message, const Bytes& sharedSecret) const;
};
}
