import veins.modules.messages.BaseFrame1609_4;

namespace cavpqc;

packet CavMsg extends veins::BaseFrame1609_4 {
    int messageType = 0;
    string sessionId;
    string senderPid;
    string receiverPid;
    string kemPublicKeyHex;
    string kemCiphertextHex;
    string signingPublicKeyHex;
    string nonceHex;
    string transcriptHashHex;
    string signatureHex;
    string finishedTagHex;
    string sourceRsuId;
    string nextRsuId;
    string handoverTokenSignatureHex;
    string contextCiphertextHex;
    string contextNonceHex;
    string contextTagHex;
    string contextKeyHashHex;
    int64_t expiryMs = 0;
    int64_t timestampMs = 0;
    int64_t cryptoProcessingMicros = 0;
}
