# ADR-005-02: WebRTC media boundary

STATUS=PROPOSED

DWCO 0.5 carries one microphone track between two authenticated app participants using WebRTC
DTLS-SRTP. Client ICE policy is relay-only to prevent peer-address disclosure. Coturn forwards
encrypted packets and does not terminate, inspect, or store media. Opus at a configured maximum
64 kbit/s is the only stage-acceptance codec.

Video, screen share, data channels, conferencing, recording, transcription, custom cryptography,
PSTN/SIP/PBX, and an end-to-end verified-identity encryption claim are excluded.

Consequence: acceptance requires real two-peer UDP-relay and TCP-relay evidence. A direct host or
server-reflexive media path is a privacy failure for this stage, not a fallback.
