packet CavMsg {
    string messageType;
    string sessionId;
    string senderId;
    string receiverId;
    string kemPublicKeyHex;
    string kemCiphertextHex;
    string signingPublicKeyHex;
    string signatureHex;
    string nonceHex;
    string transcriptHashHex;
    string finishedTagHex;
    int64_t timestampMs;
}
