# Governance control-plane project plan

## Purpose

Create a centralized, evidence-driven project record and control plane for the Implementation
Director and independent reviewers. It tracks the approved plan, requirements, stages, pull
requests, checks, risks, deviations, decisions, and next authorized action without becoming a path
to customer data or production control.

DWCO-GOV is an internal governance stream. It does not add product-stage completion weight and
cannot change the status recorded in `PROJECT_STATUS.md` without an accepted evidence record.

## Safety model

The first release is a read-only local template. Future capabilities progress from trusted import,
to authenticated review workflow, to carefully controlled GitHub status integration. Merge,
deployment, secrets, and production operations remain outside the control plane unless separately
approved.

```mermaid
flowchart LR
    subgraph Sources[Version-controlled evidence]
        MP[Master project plan]
        CT[Implementation contracts]
        PR[Pull requests and commits]
        CI[Quality results]
        CR[Completion reports]
    end

    subgraph Plane[Governance control plane]
        IN[Read-only ingestion]
        TR[Traceability and deviation engine]
        UI[Governance dashboard]
        AL[Immutable decision log - future]
    end

    subgraph People[Independent decision roles]
        ID[Implementation Director]
        AR[Architecture reviewer]
        SR[Identity / Security reviewer]
        QR[QA / Validation reviewer]
        OR[DevOps / SRE reviewer]
    end

    Sources --> IN --> TR --> UI
    UI --> People
    People -. future signed decisions .-> AL
    AL -. accepted evidence only .-> TR

    PROD[(Production systems)]
    DATA[(Customer data)]
    UI -. no access .-x PROD
    UI -. no access .-x DATA
```

## Current Docker topology

The governance container is isolated and does not join the application data path. Its distinct port
avoids the admin development server and existing infrastructure ports.

```mermaid
flowchart TB
    Browser[Local browser]
    Gov[governance-web\nunprivileged static service\nlocalhost:3100]
    Evidence[governance-data\nread-only whitelisted parser\ninternal only]
    Docs[Canonical repository docs\nread-only mounts]
    Admin[admin-web development\nlocalhost:3000]
    API[FastAPI\nlocalhost:8000]
    DB[(PostgreSQL\nlocalhost:5432)]
    Redis[(Redis\nlocalhost:6379)]

    Browser -->|read static project evidence| Gov
    Browser -->|poll normalized evidence| Gov --> Evidence --> Docs
    Browser --> Admin --> API
    API --> DB
    API --> Redis
    Gov -. no runtime connection .-x API
    Gov -. no runtime connection .-x DB
    Gov -. no runtime connection .-x Redis
    Evidence -. no credentials or network path .-x API
    Evidence -. no runtime connection .-x DB
    Evidence -. no runtime connection .-x Redis
```

## Governance record model

```mermaid
erDiagram
    PROJECT ||--o{ STAGE : contains
    STAGE ||--o{ REQUIREMENT : defines
    STAGE ||--o{ CONTRACT : authorizes
    CONTRACT ||--o{ ASSIGNMENT : delegates
    CONTRACT ||--o{ PULL_REQUEST : delivers
    PULL_REQUEST ||--o{ QUALITY_CHECK : produces
    PULL_REQUEST ||--o{ REVIEW : requires
    REQUIREMENT ||--o{ EVIDENCE : verified_by
    QUALITY_CHECK ||--o{ EVIDENCE : attaches
    STAGE ||--o{ DEPENDENCY : blocked_by
    STAGE ||--o{ DEVIATION : diverges_from
    DEVIATION ||--o{ DECISION : resolved_by
    REVIEW ||--o{ DECISION : records
    STAGE ||--o{ RISK : carries
    STAGE ||--o| COMPLETION_REPORT : closes_with
```

## Evidence and acceptance flow

```mermaid
sequenceDiagram
    participant D as Implementation Director
    participant B as Builder agent
    participant G as GitHub / CI
    participant Q as Independent reviewers
    participant C as Control plane

    D->>C: Record approved bounded contract
    C-->>B: Authorize exact scope and criteria
    B->>G: Submit implementation PR
    G-->>C: Import commit and check evidence
    C->>Q: Request exact-commit reviews
    Q-->>C: PASS / FAIL / BLOCKED with evidence
    C-->>D: Show traceability, deviations and residual risk
    alt all required gates pass
        D->>C: Record stage acceptance
        C-->>C: Recalculate accepted progress
    else any gate fails or evidence is missing
        C-->>D: Preserve current status and name blocker
    end
```

## Product-readiness gates

```mermaid
flowchart LR
    G0[G0\nContract ready] --> G1[G1\nDesign, security and privacy]
    G1 --> G2[G2\nImplementation complete]
    G2 --> G3[G3\nIndependent verification]
    G3 --> G4[G4\nStage accepted]
    G4 --> G5[G5\nStaging readiness]
    G5 --> G6[G6\nProduction authorization]
    G6 --> G7[G7\nControlled pilot]
    G7 --> G8[G8\nProduct ready / GA]

    STOP{Failed invariant,\nmissing evidence,\nor critical risk}
    G1 -. fail .-> STOP
    G2 -. fail .-> STOP
    G3 -. fail .-> STOP
    G5 -. fail .-> STOP
    G6 -. fail .-> STOP
```

## Delivery phases

| Phase | Capability | Security boundary | Exit gate |
|---|---|---|---|
| GOV 0.1 | Local read-only dashboard template | No credentials, APIs, persistence, or mutations | Docker/local validation |
| GOV 0.2 | Trusted document and GitHub read ingestion | Read-only token, minimal scopes, signed inputs | Data accuracy and threat review |
| GOV 0.2A | Live local document ingestion | Whitelisted read-only mounts, no credential or external network | Parser, freshness and isolation evidence |
| GOV 0.2B | GitHub PR/check read ingestion | Read-only token, minimal scopes, server-side adapter | Permission, data accuracy and threat review |
| GOV 0.3 | Authenticated role-based review workspace | MFA, least privilege, audit, no self-approval | Independent security/QA acceptance |
| GOV 0.4 | Requirements, defects, risks, deviations, waivers | Immutable history and expiring waivers | Traceability and conflict-of-interest tests |
| GOV 0.5 | CI status/check integration | Signed webhooks; no false remote-pass representation | Remote CI and branch protection active |
| GOV 0.6 | Staging release-readiness records | Evidence only; no deployment execution | SRE and release review |
| GOV 1.0 | Production-ready governance plane | Separate deployment authorization and operations | Pen test, DR, SLO and privacy gates |

## Required quality checks

- Requirement-to-contract-to-code-to-test-to-evidence traceability.
- Exact commit SHA, environment, commands, results, artifacts, reviewer, and timestamp.
- Architecture, Identity/Security, DevOps/SRE, and QA/Validation independence.
- Severity, defect owner, exit evidence, waiver owner, and waiver expiry.
- Accessibility, responsive layout, failure/empty/loading states, and device/browser review.
- Threat model, data classification, token scopes, webhook signing/replay, and audit integrity before
  any live integration.
- Backup/restore, rollback, observability, SLO, incident, and release rehearsal before production.

## Global stop conditions

No merge, accepted stage credit, or deployment proceeds when scope is unapproved; tenant/security
invariants fail; required evidence is missing, failed, flaky, or not tied to the exact commit; the
reviewer is not independent; a destructive migration lacks rollback proof; secrets or sensitive data
are exposed; a provider/legal dependency is unapproved; or critical/high risk remains unresolved.

## Next approval checkpoint

Accept GOV 0.1 as a local UI template only. Before GOV 0.2, approve the ingestion architecture,
GitHub permission scopes, source reconciliation rules, data classification, authentication/RBAC,
audit model, and an explicit rule that the control plane cannot merge or deploy.
Review GOV 0.2A as a credential-free local live-evidence reader. Before GOV 0.2B, approve GitHub
permission scopes, source reconciliation rules, data classification, credential storage and
rotation, rate/failure handling, audit model, and an explicit rule that the control plane cannot
merge or deploy.
