# Skilled agent registry

Agents are responsibility roles, not autonomous authority. Assignments are bounded by approved
contracts and the repository `AGENTS.md` rules.

| Agent | Primary responsibility |
|---|---|
| Implementation Director | Scope, sequencing, approvals, assignment, evidence, final gate |
| Architecture | Boundaries, ADRs, tenancy, data flow, non-functional design |
| Backend | API, domain logic, persistence, migrations, jobs |
| Identity/Security | Authentication, authorization, isolation, privacy, threat review |
| Admin Web | Admin UX, permissions, accessibility, browser tests |
| Mobile | Mobile UX, lifecycle, secure storage, background behavior |
| Realtime | Connections, presence transport, messaging delivery/ordering |
| Voice/WebRTC | Media sessions, signaling, ICE/TURN, quality, devices |
| Telecom/PBX | PSTN/SIP, numbering, routing, provider/regulatory boundary |
| Mobility/eSIM | Carrier/eSIM provisioning boundary and device lifecycle |
| Integration | Provider-neutral adapters, webhooks, CRM/external contracts |
| AI | Model evaluation, inference features, safety, data minimisation |
| DevOps/SRE | CI, environments, observability, reliability, release/rollback |
| QA/Validation | Independent acceptance, regression, adversarial/evidence review |

## Assignment rules

- Every contract has one accountable Implementation Director and one primary implementation agent.
- Architecture, Identity/Security, DevOps/SRE, and QA/Validation review material concerns; they must
  not self-approve work they solely authored.
- Telecom, mobility, AI, billing, or production work requires a dedicated later contract.
- Agents report uncertainty, dependencies, deferred scope, and evidence without widening scope.
