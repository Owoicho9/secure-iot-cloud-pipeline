# Threat Model: Secure IoT-to-Cloud Sensor Network

## 1. System Overview

The system consists of simulated IoT sensor nodes (`node-01`, `node-02`, `node-03`) publishing readings over MQTT to a Mosquitto broker, and a subscriber acting as a backend data consumer. Each entity (broker, each node, subscriber) holds its own X.509 certificate, signed by a self-managed Certificate Authority (CA) created for this project.

## 2. Assets Being Protected

- **Sensor data integrity and confidentiality** — readings should not be readable or alterable by an eavesdropper in transit.
- **Broker access** — only legitimate, known devices should be able to connect at all.
- **Topic-level write scope** — a given device should only be able to publish data under its own identity, not impersonate or interfere with another device's data stream.

## 3. Threats Considered

| Threat | Description | Relevant to this system? |
|---|---|---|
| Eavesdropping / traffic sniffing | An attacker on the network reads sensor data in transit | Yes — addressed |
| Spoofed / rogue device | An unauthorized device connects to the broker and injects fake data | Yes — addressed |
| Man-in-the-middle (MITM) | An attacker impersonates the broker to intercept or manipulate traffic | Yes — addressed |
| Cross-device impersonation | A legitimate but compromised/misconfigured device publishes to another device's topic | Yes — addressed |
| Replay attacks | An attacker captures and re-sends a previously valid message | Not yet addressed — see Limitations |
| Denial of service | An attacker floods the broker with connections/messages | Not addressed — out of scope for this project |
| Compromise of the CA private key | If `ca.key` is stolen, an attacker could mint trusted certificates for arbitrary identities | Acknowledged — see Limitations |

## 4. Mitigations Implemented

### 4.1 Encryption in transit (TLS 1.3)
All MQTT traffic is encrypted using TLS 1.3. The plaintext listener (port 1883) was removed entirely — only the TLS listener (port 8883) is active. This was verified directly: an unmodified client attempting to connect on port 1883 receives a `ConnectionRefusedError`, since no service listens there at all. **This defends against eavesdropping.**

### 4.2 Mutual TLS (mTLS) — device authentication
Each device (broker, node-01, node-02, node-03, subscriber) holds a certificate signed by a self-created CA (`ca.crt`/`ca.key`). The broker is configured with `require_certificate true`, meaning any client that cannot present a certificate signed by the trusted CA is rejected during the TLS handshake itself. This was verified: a client attempting a plain (non-TLS) connection to port 8883 is rejected at the protocol level (`OpenSSL... wrong version number`). **This defends against spoofed/rogue devices and, combined with the broker's own certificate, against MITM impersonation of the broker.**

### 4.3 Identity binding (`use_identity_as_username`)
The broker is configured to use each certificate's Common Name (CN) as that connection's MQTT-level username. This means the cryptographic identity established during the TLS handshake carries through to the MQTT session, rather than being checked once and discarded. This was verified via broker logs showing each connection tagged with its correct identity (e.g. `u'node-01'`, `u'subscriber'`).

### 4.4 Topic-level authorization (ACLs)
An ACL file restricts each device to publishing only within its own topic namespace (e.g. `node-01` may only write to `sensors/node-01/#`). This was directly tested: `sensor_node.py` was deliberately reconfigured to present `node-02`'s certificate while still attempting to publish to `sensors/node-01/temperature`. The TLS handshake succeeded (the certificate was validly signed by the trusted CA), but the broker logged `Denied PUBLISH` for every attempt, since node-02's ACL scope does not include node-01's topic. **This demonstrates that authentication (proving identity) and authorization (permission to act) are enforced as two separate, independent controls** — a device having a valid identity does not imply it can act outside its granted scope.

## 5. Limitations and Future Work

- **CA key management:** `ca.key` is stored locally and is not hardware-protected (e.g. no HSM/TPM). In a production deployment, this would be a critical single point of failure — compromise of this key would allow an attacker to mint trusted certificates for any identity. Acceptable for a portfolio/demo project; would require a proper PKI solution (e.g. HashiCorp Vault, AWS Private CA) in production.
- **No replay protection:** the current system does not implement nonces, sequence numbers, or timestamp-freshness checks, so a captured valid message could theoretically be re-sent. MQTT QoS mechanisms and application-level sequence numbers would be the next step here.
- **No revocation tested:** Mosquitto supports certificate revocation lists (`crlfile`), which would allow disabling a specific compromised device's certificate without regenerating the entire CA. Not implemented in this phase.
- **Simulated, not physical, devices:** the "sensor nodes" are Python scripts generating synthetic data, not real hardware. The security model (mTLS + ACLs) is transport/identity-layer and would apply identically to real devices, but real deployments would add physical/firmware-level considerations (secure boot, key provisioning at manufacture) not covered here.

## 6. Summary

This phase established a layered defense: encryption (TLS 1.3) protects confidentiality, mutual authentication (mTLS) ensures only known devices can connect at all, and topic-level ACLs enforce least-privilege so that a valid identity cannot act outside its intended scope. Each control was independently and deliberately tested against a corresponding failure/attack scenario, rather than assumed to work from configuration alone.
