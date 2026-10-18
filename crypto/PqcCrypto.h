#pragma once

#include <cstdint>
#include <string>
#include <utility>
#include <vector>

namespace cavpqc {
using Bytes = std::vector<std::uint8_t>;

struct KemKeyPair { Bytes publicKey; Bytes secretKey; };
struct SigKeyPair { Bytes publicKey; Bytes secretKey; };
struct AeadCiphertext { Bytes nonce; Bytes ciphertext; Bytes tag; };

class PqcCrypto final {
public:
    KemKeyPair generateKemKeyPair() const;
    SigKeyPair generateSigKeyPair() const;
    std::pair<Bytes, Bytes> encapsulate(const Bytes& publicKey) const;
    Bytes decapsulate(const Bytes& secretKey, const Bytes& ciphertext) const;
    Bytes sign(const Bytes& secretKey, const Bytes& message) const;
    bool verify(const Bytes& publicKey, const Bytes& message, const Bytes& signature) const;
    Bytes random(std::size_t length) const;
    Bytes shake256(const Bytes& input, std::size_t outputLength = 32) const;
    Bytes hkdfSha384(const Bytes& ikm, const Bytes& salt, const std::string& info, std::size_t outputLength = 32) const;
    Bytes hmacSha384(const Bytes& key, const Bytes& input) const;
    AeadCiphertext aeadEncrypt(const Bytes& key, const Bytes& plaintext, const Bytes& associatedData) const;
    Bytes aeadDecrypt(const Bytes& key, const AeadCiphertext& encrypted, const Bytes& associatedData) const;
    static std::string hex(const Bytes& input);
    static Bytes unhex(const std::string& input);
};

// Simulation-only credential directory for the first single-process Veins
// milestone. Replace with the Phase 4 TA credential directory before any
// multi-process or reported network experiment.
class SimulationCredentialDirectory final {
public:
    static void registerSigningKey(const std::string& subject, const Bytes& publicKey);
    static Bytes signingKey(const std::string& subject);
};
}
