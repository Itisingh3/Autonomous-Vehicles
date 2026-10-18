#pragma once
#include <omnetpp.h>
#include "PqcCrypto.h"
class CavMsg;

class CAVApp : public omnetpp::cSimpleModule {
  public: CAVApp() = default; ~CAVApp() override = default;
  protected: void initialize() override; void handleMessage(omnetpp::cMessage* message) override;
  private:
    cavpqc::PqcCrypto crypto_; cavpqc::KemKeyPair kem_; cavpqc::SignatureKeyPair signing_;
    cavpqc::Bytes nonce_; cavpqc::Bytes helloTranscript_; cavpqc::Bytes sessionKey_; std::string sessionId_; omnetpp::simtime_t helloSent_;
    omnetpp::simsignal_t cryptoTimeSignal_, handshakeLatencySignal_, successSignal_, failureSignal_, overheadSignal_;
    std::int64_t nowMs() const; cavpqc::Bytes helloTranscript(const CavMsg& message) const; cavpqc::Bytes replyTranscript(const CavMsg& message) const;
    void sendHello(); void handleServerHello(CavMsg* message); void fail(const char* reason);
};
