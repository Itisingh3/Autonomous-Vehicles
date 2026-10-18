# V2R OMNeT++/Veins milestone

This directory implements only the first integration milestone: ML-KEM-768 and
ML-DSA-65 based mutual authentication and session-key establishment between a
CAV and an RSU. Handover-token logic is deliberately absent.

## Build prerequisites

Run inside the compatible `opp_env` shell after Veins has been built. The
checked-in `Makefile` uses the project-local liboqs build in `.deps/oqs` and
the Veins 5.2 release library at `/home/opp_env/veins`; regenerate it if your
paths differ. `make` generates `CavMsg_m.h/.cc` from `CavMsg.msg`.

```text
simulation/omnetpp
crypto
```

Include/link flags required by the crypto service are:

```text
-I../../crypto -I../../.deps/oqs/include
-L../../.deps/oqs/lib -loqs -lcrypto -lveins
```

The Veins source/include/library paths must come from the selected Veins 5.2
project configuration; do not copy its generated build flags blindly across
framework versions.

## What the smoke scenario verifies

1. CAV signs a Vehicle Hello with ML-DSA-65.
2. RSU validates the simulation credential binding and signature, then
   encapsulates ML-KEM-768 to the CAV key.
3. RSU signs Server Hello, including the Vehicle Hello transcript hash.
4. CAV validates Server Hello, decapsulates, and sends Finished HMAC.
5. RSU verifies Finished; this demonstrates both sides derived the same session
   key without logging that key.

The scalar output records Vehicle Hello, Server Hello, and Finished message
sizes; vehicle, RSU, and CAV cryptographic wall-clock work; simulated
handshake latency; 32-byte key lengths at both endpoints; and
`keyConfirmationVerified = 1`. Crypto execution time is measured separately
and is not silently added to simulated network time.

## Run the deterministic integration check

The default `General` configuration uses one fixed-position CAV and one RSU.
It validates the complete three-message exchange without depending on TraCI:

```bash
cd /home/opp_env/cav-pqc-framework/simulation/omnetpp
opp_env run omnetpp-6.0.1 -c "make MODE=release -j2"
opp_env run omnetpp-6.0.1 -c "./cav_pqc_network -u Cmdenv -n .:../.neddeps -f omnetpp.ini"
```

The `SumoIntegration` configuration retains the vehicle-density, speed, RSU
spacing, and token-validity parameters for the future mobility experiment.
It requires a Veins/SUMO pair with compatible TraCI API versions. The installed
Veins 5.2 and SUMO 1.25.0 pair is not compatible, so it must not be used to
claim mobility results until one component is aligned.

The in-process `SimulationCredentialDirectory` is a test-only credential
binding mechanism. Replace it with the Phase 4 TA credential directory before
any reportable or distributed experiment.
