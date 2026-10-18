#pragma once
#include <omnetpp.h>
#include "PqcCrypto.h"
#include <unordered_map>
class CavMsg;
class RSUApp : public omnetpp::cSimpleModule {
  public: RSUApp() = default; ~RSUApp() override = default;
  protected: void initialize() override; void handleMessage(omnetpp::cMessage* message) override;
  private:
    struct Pending { cavpqc::Bytes sessionKey; cavpqc::Bytes confirmationKey; cavpqc::Bytes transcriptHash; omnetpp::simtime_t started; };
    cavpqc::PqcCrypto crypto_; cavpqc::SignatureKeyPair signing_; std::unordered_map<std::string, Pending> pending_;
    omnetpp::simsignal_t cryptoTimeSignal_, handshakeLatencySignal_, successSignal_, failureSignal_, overheadSignal_;
    std::int64_t nowMs() const; cavpqc::Bytes helloTranscript(const CavMsg& message) const; cavpqc::Bytes replyTranscript(const CavMsg& message) const;
    void handleHello(CavMsg* message); void handleFinished(CavMsg* message); void fail(const char* reason);
};
