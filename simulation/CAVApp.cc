#include "CAVApp.h"
#include "CavMsg_m.h"

#include <chrono>
#include <cmath>
#include <cstdlib>

using namespace omnetpp;
using cavpqc::Bytes;
using cavpqc::PqcCrypto;

Define_Module(CAVApp);

namespace {
template <typename F> auto timed(cSimpleModule* module, simsignal_t signal, F&& action) {
    const auto start = std::chrono::steady_clock::now(); auto result = action();
    module->emit(signal, std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - start).count()); return result;
}
int bytes(const CavMsg& m) { return 48 + std::string(m.getSessionId()).size() + std::string(m.getSenderId()).size() + std::string(m.getReceiverId()).size() + (std::string(m.getKemPublicKeyHex()).size() + std::string(m.getKemCiphertextHex()).size() + std::string(m.getSigningPublicKeyHex()).size() + std::string(m.getSignatureHex()).size() + std::string(m.getNonceHex()).size() + std::string(m.getTranscriptHashHex()).size() + std::string(m.getFinishedTagHex()).size()) / 2; }
}

void CAVApp::initialize() {
    cryptoTimeSignal_ = registerSignal("cryptoProcessingMs"); handshakeLatencySignal_ = registerSignal("handshakeLatency");
    successSignal_ = registerSignal("v2rSuccess"); failureSignal_ = registerSignal("v2rFailure"); overheadSignal_ = registerSignal("messageOverheadBytes");
    try { kem_ = timed(this, cryptoTimeSignal_, [&] { return crypto_.kemKeygen(); }); signing_ = timed(this, cryptoTimeSignal_, [&] { return crypto_.signatureKeygen(); }); sendHello(); }
    catch (const std::exception& error) { fail(error.what()); }
}
std::int64_t CAVApp::nowMs() const { return static_cast<std::int64_t>(std::llround(simTime().dbl() * 1000.0)); }
Bytes CAVApp::helloTranscript(const CavMsg& m) const { return PqcCrypto::canonical({PqcCrypto::text("CAV-PQC-v1"),PqcCrypto::text(m.getMessageType()),PqcCrypto::text(m.getSessionId()),PqcCrypto::text(m.getSenderId()),PqcCrypto::text(m.getKemPublicKeyHex()),PqcCrypto::text(m.getNonceHex()),PqcCrypto::text(std::to_string(m.getTimestampMs()))}); }
Bytes CAVApp::replyTranscript(const CavMsg& m) const { return PqcCrypto::canonical({PqcCrypto::text("CAV-PQC-v1"),PqcCrypto::text(m.getMessageType()),PqcCrypto::text(m.getSessionId()),PqcCrypto::text(m.getSenderId()),PqcCrypto::text(m.getKemCiphertextHex()),PqcCrypto::text(m.getNonceHex()),PqcCrypto::text(std::to_string(m.getTimestampMs())),PqcCrypto::text(m.getTranscriptHashHex())}); }
void CAVApp::sendHello() {
    nonce_ = crypto_.randomBytes(32); const auto timestamp = nowMs();
    sessionId_ = PqcCrypto::hex(crypto_.digest("CAV-PQC-v1/session", PqcCrypto::canonical({PqcCrypto::text(par("pseudonym").stringValue()), kem_.publicKey, nonce_, PqcCrypto::text(std::to_string(timestamp))})));
    auto* hello = new CavMsg("vehicleHello"); hello->setMessageType("VEHICLE_HELLO"); hello->setSessionId(sessionId_.c_str()); hello->setSenderId(par("pseudonym").stringValue()); hello->setReceiverId(par("rsuId").stringValue()); hello->setKemPublicKeyHex(PqcCrypto::hex(kem_.publicKey).c_str()); hello->setSigningPublicKeyHex(PqcCrypto::hex(signing_.publicKey).c_str()); hello->setNonceHex(PqcCrypto::hex(nonce_).c_str()); hello->setTimestampMs(timestamp);
    helloTranscript_ = helloTranscript(*hello); Bytes signature; const auto input = crypto_.digest("CAV-PQC-v1/vehicle-hello", helloTranscript_); if (!timed(this, cryptoTimeSignal_, [&] { return crypto_.sign(signing_.secretKey, input, signature); })) throw std::runtime_error("vehicle signature failed"); hello->setSignatureHex(PqcCrypto::hex(signature).c_str()); hello->setByteLength(bytes(*hello)); emit(overheadSignal_, hello->getByteLength()); helloSent_ = simTime(); send(hello, "out");
}
void CAVApp::handleServerHello(CavMsg* reply) {
    if (std::string(reply->getSessionId()) != sessionId_ || std::string(reply->getReceiverId()) != par("pseudonym").stringValue() || std::string(reply->getSenderId()) != par("rsuId").stringValue()) { fail("server hello binding mismatch"); return; }
    if (std::llabs(nowMs() - reply->getTimestampMs()) > par("maxClockSkewMs").intValue()) { fail("server hello freshness failed"); return; }
    const auto expectedT1 = crypto_.digest("CAV-PQC-v1/vehicle-hello", helloTranscript_); if (PqcCrypto::hex(expectedT1) != std::string(reply->getTranscriptHashHex())) { fail("server hello transcript mismatch"); return; }
    const auto rsuPk = PqcCrypto::unhex(reply->getSigningPublicKeyHex()); const auto signature = PqcCrypto::unhex(reply->getSignatureHex()); const auto signedInput = crypto_.digest("CAV-PQC-v1/rsu-server-hello", replyTranscript(*reply));
    if (!timed(this, cryptoTimeSignal_, [&] { return crypto_.verify(rsuPk, signedInput, signature); })) { fail("RSU signature invalid"); return; }
    Bytes shared; if (!timed(this, cryptoTimeSignal_, [&] { return crypto_.kemDecaps(kem_.secretKey, PqcCrypto::unhex(reply->getKemCiphertextHex()), shared); })) { fail("ML-KEM decapsulation failed"); return; }
    const auto context = crypto_.digest("CAV-PQC-v1/v2r-context", PqcCrypto::canonical({kem_.publicKey,PqcCrypto::unhex(reply->getKemCiphertextHex()),nonce_,PqcCrypto::unhex(reply->getNonceHex()),PqcCrypto::text(par("pseudonym").stringValue()),PqcCrypto::text(par("rsuId").stringValue())}));
    sessionKey_ = timed(this, cryptoTimeSignal_, [&] { return crypto_.deriveKey(shared, context, "CAV-PQC-v1/session" + sessionId_); }); const auto transcript = crypto_.digest("CAV-PQC-v1/handshake", PqcCrypto::canonical({helloTranscript_,replyTranscript(*reply)})); const auto confirm = timed(this, cryptoTimeSignal_, [&] { return crypto_.deriveKey(sessionKey_, transcript, "CAV-PQC-v1/finished"); }); const auto tag = timed(this, cryptoTimeSignal_, [&] { return crypto_.hmacSha384(confirm, PqcCrypto::canonical({PqcCrypto::text("CAV-PQC-v1/vehicle-finished"),transcript,PqcCrypto::text(sessionId_)})); });
    auto* finished = new CavMsg("finished"); finished->setMessageType("FINISHED"); finished->setSessionId(sessionId_.c_str()); finished->setSenderId(par("pseudonym").stringValue()); finished->setReceiverId(par("rsuId").stringValue()); finished->setTranscriptHashHex(PqcCrypto::hex(transcript).c_str()); finished->setFinishedTagHex(PqcCrypto::hex(tag).c_str()); finished->setTimestampMs(nowMs()); finished->setByteLength(bytes(*finished)); emit(overheadSignal_, finished->getByteLength()); send(finished, "out");
}
void CAVApp::handleMessage(cMessage* message) { auto* packet = check_and_cast<CavMsg*>(message); try { if (std::string(packet->getMessageType()) == "RSU_SERVER_HELLO") handleServerHello(packet); else fail("unexpected CAV message"); } catch (const std::exception& error) { fail(error.what()); } delete packet; }
void CAVApp::fail(const char* reason) { EV_WARN << "CAV V2R failure: " << reason << "\n"; emit(failureSignal_, 1L); }
