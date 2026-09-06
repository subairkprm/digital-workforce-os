# ADR-005-07: shared-scale deferral

STATUS=PROPOSED

The bounded DWCO 0.5 implementation and evidence environment is one application instance with
isolated local PostgreSQL, Redis, coturn, and two synthetic/device peers. Process-local WebSocket
notifications are explicitly non-authoritative. Local acceptance proves at most 10 concurrent calls
for 30 minutes and a 20-call admission burst; it makes no production capacity or availability claim.

A shared or staged environment requires a separate DEP-012 contract covering broker/fan-out,
session affinity, scalable revocation, DNS, certificates, secrets, firewall/relay capacity, DDoS and
abuse operations, observability/SLOs, ownership/cost, backup/recovery, teardown, and synthetic-data
policy. DEP-001 remote CI and DEP-007 production TURN remain open.
