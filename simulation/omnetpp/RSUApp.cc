#include "RSUApp.h"
#include <cstdlib>
#include <omnetpp.h>

using namespace omnetpp;
namespace cavpqc {
namespace {
constexpr int VEHICLE_HELLO=1, SERVER_HELLO=2, FINISHED=3, FULL_ACK=4, RSU_CONTEXT=9, HANDOVER_OFFER=10, HANDOVER_REQUEST=11, HANDOVER_CONFIRM=12, HANDOVER_FALLBACK=13;
std::int64_t nowMs(simtime_t t) { return static_cast<std::int64_t>(t.dbl()*1000.0); }
Bytes text(const std::string& s) { return Bytes(s.begin(),s.end()); }
}
Define_Module(RSUApp);

void RSUApp::initialize(int stage) {
    DemoBaseApplLayer::initialize(stage); if(stage!=0)return;
    rsuId_=par("rsuId").stdstringValue(); nextRsu_=par("nextRsu").stdstringValue(); sig_=crypto_.generateSigKeyPair();
    rsuChannelKey_=crypto_.hkdfSha384(text("CAV-PQC-v1/RSU-A-B"),crypto_.shake256(text("rsu-channel")),"rsu-context-channel");
    SimulationCredentialDirectory::registerSigningKey(rsuId_,sig_.publicKey);
    handshakeLatencySignal_=registerSignal("v2rHandshakeLatency"); handoverLatencySignal_=registerSignal("handoverLatency"); cryptoMicrosSignal_=registerSignal("cryptoProcessingMicros"); successSignal_=registerSignal("v2rHandshakeSuccess"); failureSignal_=registerSignal("v2rHandshakeFailure");
}
bool RSUApp::fresh(const CavMsg& m) const { return std::llabs(nowMs(simTime())-m.getTimestampMs())<=static_cast<std::int64_t>(par("maxClockSkew").doubleValue()*1000); }

void RSUApp::handleVehicleHello(CavMsg* m) {
 try {
    if(std::string(m->getReceiverPid())!=rsuId_||!fresh(*m))throw std::runtime_error("hello freshness");
    const Bytes vehicleKey=SimulationCredentialDirectory::signingKey(m->getSenderPid());
    if(vehicleKey!=PqcCrypto::unhex(m->getSigningPublicKeyHex()))throw std::runtime_error("credential");
    const std::string hello="CAV-PQC-v1|VEHICLE_HELLO|"+std::string(m->getSessionId())+"|"+std::string(m->getSenderPid())+"|"+std::string(m->getKemPublicKeyHex())+"|"+std::string(m->getNonceHex())+"|"+std::to_string(m->getTimestampMs());
    if(!crypto_.verify(vehicleKey,crypto_.shake256(text(hello)),PqcCrypto::unhex(m->getSignatureHex())))throw std::runtime_error("vehicle signature");
    const std::pair<Bytes,Bytes> kem=crypto_.encapsulate(PqcCrypto::unhex(m->getKemPublicKeyHex())); const Bytes nonce=crypto_.random(32);
    const std::string context="CAV-PQC-v1/v2r-context|"+std::string(m->getKemPublicKeyHex())+"|"+PqcCrypto::hex(kem.first)+"|"+std::string(m->getNonceHex())+"|"+PqcCrypto::hex(nonce)+"|"+std::string(m->getSenderPid())+"|"+rsuId_;
    const Bytes session=crypto_.hkdfSha384(kem.second,crypto_.shake256(text(context)),"CAV-PQC-v1/session|"+std::string(m->getSessionId()));
    const std::string helloHash=PqcCrypto::hex(crypto_.shake256(text(hello)));
    const std::string reply="CAV-PQC-v1|SERVER_HELLO|"+std::string(m->getSessionId())+"|"+rsuId_+"|"+PqcCrypto::hex(kem.first)+"|"+PqcCrypto::hex(nonce)+"|"+helloHash;
    const Bytes signature=crypto_.sign(sig_.secretKey,crypto_.shake256(text(reply)));
    pending_[m->getSessionId()]=Pending{session,crypto_.hkdfSha384(session,crypto_.shake256(text(hello+"|"+reply)),"CAV-PQC-v1/finished"),hello+"|"+reply,simTime(),m->getSenderPid()};
    auto* r=new CavMsg("ServerHello"); populateWSM(r); r->setMessageType(SERVER_HELLO);r->setSessionId(m->getSessionId());r->setSenderPid(rsuId_.c_str());r->setReceiverPid(m->getSenderPid());r->setSigningPublicKeyHex(PqcCrypto::hex(sig_.publicKey).c_str());r->setKemCiphertextHex(PqcCrypto::hex(kem.first).c_str());r->setNonceHex(PqcCrypto::hex(nonce).c_str());r->setTranscriptHashHex(helloHash.c_str());r->setTimestampMs(nowMs(simTime()));r->setSignatureHex(PqcCrypto::hex(signature).c_str());r->addBitLength((sig_.publicKey.size()+kem.first.size()+nonce.size()+signature.size())*8);sendDown(r);
 } catch(const std::exception&) { emit(failureSignal_,1L); }
}
void RSUApp::handleFinished(CavMsg* m) {
 try {
    const auto found=pending_.find(m->getSessionId()); if(found==pending_.end()||!fresh(*m)||std::string(m->getReceiverPid())!=rsuId_)throw std::runtime_error("finished");
    const Bytes hash=crypto_.shake256(text(found->second.transcript)); const Bytes expected=crypto_.hmacSha384(found->second.confirmKey,text("CAV-PQC-v1/vehicle-finished|"+PqcCrypto::hex(hash)+"|"+std::string(m->getSessionId())));
    if(PqcCrypto::hex(expected)!=m->getFinishedTagHex()||PqcCrypto::hex(hash)!=m->getTranscriptHashHex())throw std::runtime_error("confirmation");
    recordScalar("v2rHandshakeLatencySeconds",(simTime()-found->second.started).dbl()); recordScalar("keyConfirmationVerified",1.0);
    auto* ack=new CavMsg("FullHandshakeAck");populateWSM(ack);ack->setMessageType(FULL_ACK);ack->setSessionId(m->getSessionId());ack->setSenderPid(rsuId_.c_str());ack->setReceiverPid(found->second.pid.c_str());ack->setTimestampMs(nowMs(simTime()));sendDown(ack);
    if(!nextRsu_.empty())issueHandover(m->getSessionId(),found->second); pending_.erase(found);
 } catch(const std::exception&) { emit(failureSignal_,1L); }
}
void RSUApp::issueHandover(const std::string& sid,const Pending& p) {
 const double speedKmph = par("vehicleSpeedKmph").doubleValue();
 const double headingDeg = par("vehicleHeadingDeg").doubleValue();
 const double spacingM = par("rsuSpacingMeters").doubleValue();
 if (speedKmph <= 0 || spacingM <= 0 || headingDeg < -360 || headingDeg > 360) return;
 const std::int64_t ts=nowMs(simTime()), expiry=ts+static_cast<std::int64_t>(par("tokenValidity").doubleValue()*1000);
 const Bytes ctx=crypto_.hkdfSha384(p.sessionKey,crypto_.shake256(text("CAV-PQC-v1/handover-context")),"handover-context"); const Bytes tokenNonce=crypto_.random(16);
 const std::string nonceHex=PqcCrypto::hex(tokenNonce), ctxHash=PqcCrypto::hex(crypto_.shake256(ctx));
 const std::string token="CAV-PQC-v1/handover-token|"+p.pid+"|"+nextRsu_+"|"+ctxHash+"|"+std::to_string(ts)+"|"+std::to_string(expiry)+"|"+nonceHex;
 const Bytes signature=crypto_.sign(sig_.secretKey,crypto_.shake256(text(token))); const std::string ad="CAV-PQC-v1/rsu-context|"+sid+"|"+p.pid+"|"+nextRsu_; const AeadCiphertext enc=crypto_.aeadEncrypt(rsuChannelKey_,ctx,text(ad));
 auto* context=new CavMsg("RsuContext"); populateWSM(context); context->setMessageType(RSU_CONTEXT);context->setSessionId(sid.c_str());context->setSenderPid(p.pid.c_str());context->setReceiverPid(nextRsu_.c_str());context->setSourceRsuId(rsuId_.c_str());context->setNextRsuId(nextRsu_.c_str());context->setNonceHex(nonceHex.c_str());context->setHandoverTokenSignatureHex(PqcCrypto::hex(signature).c_str());context->setContextKeyHashHex(ctxHash.c_str());context->setContextNonceHex(PqcCrypto::hex(enc.nonce).c_str());context->setContextCiphertextHex(PqcCrypto::hex(enc.ciphertext).c_str());context->setContextTagHex(PqcCrypto::hex(enc.tag).c_str());context->setTimestampMs(ts);context->setExpiryMs(expiry);sendDown(context);
 auto* offer=context->dup(); offer->setName("HandoverOffer");offer->setMessageType(HANDOVER_OFFER);offer->setReceiverPid(p.pid.c_str());offer->setContextCiphertextHex("");offer->setContextNonceHex("");offer->setContextTagHex("");sendDown(offer);
}
void RSUApp::handleRsuContext(CavMsg* m) {
 try { if(std::string(m->getReceiverPid())!=rsuId_||std::string(m->getNextRsuId())!=rsuId_)throw std::runtime_error("context destination"); const std::string ad="CAV-PQC-v1/rsu-context|"+std::string(m->getSessionId())+"|"+std::string(m->getSenderPid())+"|"+rsuId_; const AeadCiphertext enc{PqcCrypto::unhex(m->getContextNonceHex()),PqcCrypto::unhex(m->getContextCiphertextHex()),PqcCrypto::unhex(m->getContextTagHex())}; handoverContexts_[m->getSessionId()]=HandoverContext{m->getSenderPid(),m->getSourceRsuId(),crypto_.aeadDecrypt(rsuChannelKey_,enc,text(ad)),m->getContextKeyHashHex(),m->getNonceHex(),m->getHandoverTokenSignatureHex(),m->getTimestampMs(),m->getExpiryMs()}; }catch(const std::exception&){emit(failureSignal_,1L);}
}
void RSUApp::sendFallback(CavMsg* m,const char*) { auto* r=new CavMsg("HandoverFallback");populateWSM(r);r->setMessageType(HANDOVER_FALLBACK);r->setSessionId(m->getSessionId());r->setSenderPid(rsuId_.c_str());r->setReceiverPid(m->getSenderPid());r->setTimestampMs(nowMs(simTime()));sendDown(r); }
void RSUApp::handleHandoverRequest(CavMsg* m) {
 try {
  const auto found=handoverContexts_.find(m->getSessionId()); if(found==handoverContexts_.end()||std::string(m->getReceiverPid())!=rsuId_||std::string(m->getNextRsuId())!=rsuId_||m->getExpiryMs()<=nowMs(simTime())||usedTokenNonces_.count(m->getNonceHex()))throw std::runtime_error("handover state");
  const HandoverContext& ctx=found->second; if(ctx.tokenSignature!=m->getHandoverTokenSignatureHex())throw std::runtime_error("token mismatch");
  const Bytes vehicleKey=SimulationCredentialDirectory::signingKey(m->getSenderPid());if(vehicleKey!=PqcCrypto::unhex(m->getSigningPublicKeyHex()))throw std::runtime_error("vehicle credential");
  const std::string request="CAV-PQC-v1/handover-request|"+std::string(m->getSenderPid())+"|"+rsuId_+"|"+std::string(m->getHandoverTokenSignatureHex())+"|"+std::string(m->getNonceHex())+"|"+std::to_string(m->getTimestampMs());if(!crypto_.verify(vehicleKey,crypto_.shake256(text(request)),PqcCrypto::unhex(m->getSignatureHex())))throw std::runtime_error("vehicle signature");
  usedTokenNonces_.insert(m->getNonceHex()); const Bytes rsuNonce=crypto_.random(32); const auto ts=nowMs(simTime()); const Bytes newKey=crypto_.hkdfSha384(ctx.contextKey,crypto_.shake256(text(std::string(m->getNonceHex())+"|"+PqcCrypto::hex(rsuNonce)+"|"+std::to_string(ts))),"CAV-PQC-v1/handover-session");
  const std::string confirm="CAV-PQC-v1/handover-confirm|"+std::string(m->getSessionId())+"|"+std::string(m->getSenderPid())+"|"+rsuId_+"|"+std::string(m->getNonceHex())+"|"+PqcCrypto::hex(rsuNonce);const Bytes signature=crypto_.sign(sig_.secretKey,crypto_.shake256(text(confirm)));
  auto* r=new CavMsg("HandoverConfirm");populateWSM(r);r->setMessageType(HANDOVER_CONFIRM);r->setSessionId(m->getSessionId());r->setSenderPid(rsuId_.c_str());r->setReceiverPid(m->getSenderPid());r->setNonceHex(PqcCrypto::hex(rsuNonce).c_str());r->setTimestampMs(ts);r->setSignatureHex(PqcCrypto::hex(signature).c_str());sendDown(r);recordScalar("handoverSessionKeyBytes",static_cast<double>(newKey.size()));handoverContexts_.erase(found);
 }catch(const std::exception&){sendFallback(m,"validation failed");}
}
void RSUApp::onWSM(veins::BaseFrame1609_4* f) {auto* m=dynamic_cast<CavMsg*>(f);if(!m||std::string(m->getReceiverPid())!=rsuId_)return;switch(m->getMessageType()){case VEHICLE_HELLO:handleVehicleHello(m);break;case FINISHED:handleFinished(m);break;case RSU_CONTEXT:handleRsuContext(m);break;case HANDOVER_REQUEST:handleHandoverRequest(m);break;}}
}
