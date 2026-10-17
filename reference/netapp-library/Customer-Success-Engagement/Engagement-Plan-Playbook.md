# Engagement Plan Playbook — from "here's a customer scenario" to a phased, measurable plan

**Purpose**: this is the tool to actually run. When the engineer describes a customer scenario — their environment, situation, or a specific ask — use this playbook to produce a complete engagement plan: stakeholder map, environment/whitespace assessment, and a phased, prioritized, measurable plan that blends CSM (adoption/success), TAM (technical risk/roadmap), and SAM (pipeline/expansion) actions as appropriate to what's actually going on in the account. See [README.md](README.md) for the underlying frameworks this playbook draws on (TSIA, Gainsight, MEDDPICC, Challenger, stakeholder power-interest mapping) and the NetApp portfolio whitespace map.

Work through the six steps below in order. Not every step needs a lengthy answer for every scenario — a straightforward technical-refresh conversation may need a thin stakeholder map and a heavier Phase 2; a competitive-displacement pursuit needs a heavy stakeholder map and MEDDPICC qualification before any plan gets built at all. State explicitly which steps got a light touch and why, rather than silently skipping them.

## Step 1 — Intake: pin down the scenario before planning anything

Before building a plan, establish (ask the engineer directly for anything not already given, rather than assuming):

- **Who is the customer** (industry, size, single-site vs. multi-site) and **what's the trigger** for this engagement right now (renewal approaching, technical incident, refresh cycle, competitive threat, inbound request, proactive outreach)?
- **Current NetApp footprint**: platforms (AFF/ASA/AFX/FAS generation, approximate age), ONTAP version, data protection posture (SnapMirror/SnapVault/SnapCenter in use?), any cloud (CVO/BlueXP), any 3rd-party backup/DSPM integration, current support tier (standard/SupportEdge Advisor/TAM/SAM-covered).
- **Environment and workload context**: primary workloads (VMware/Hyper-V/Kubernetes/databases/AI-ML/general file), current pain points or open risk (performance, capacity, an approaching EOA/EOL platform, a recent incident, an audit/compliance driver), and anything competitive in play (evaluating or already running a competing platform).
- **Relationship state today**: who currently owns the relationship (the engineer alone, or a broader account team), what's the last known health signal (recent QBR outcome, open P1/P2 cases, adoption trend, renewal date), and what's the role in play — is this primarily a CSM motion (adoption/renewal), a TAM motion (technical risk/escalation), a SAM motion (new pipeline), or a blend?
- **What does success look like for this specific engagement** — a closed opportunity, a resolved technical risk, a renewed contract, a healthier relationship, a reference-able case study? Get this stated up front; it defines the plan's measurable outcomes in Step 5.

If any of the above is unknown, say so explicitly in the output and mark it as an open discovery item in Phase 0 of the plan (Step 4) rather than assuming a default.

## Step 2 — Stakeholder map

Build a table with, at minimum: **name/role (if known, else "TBD — [role]")**, **stakeholder type** (economic buyer / executive sponsor / champion / technical buyer-evaluator / gatekeeper / signer / end-user-influencer — per [README.md](README.md#sales-pipeline-generation--opportunity-qualification--frameworks)), **power/interest quadrant** (manage closely / keep satisfied / keep informed / monitor), **current sentiment** (advocate / neutral / skeptic / unknown), and **engagement approach** (what cadence and content this specific stakeholder needs — an executive gets ROI/outcome summaries, a technical evaluator gets architecture depth, a gatekeeper gets a lighter, access-preserving touch).

If stakeholders aren't yet known by name, still populate the table with **role placeholders** ("Economic buyer — TBD, likely CIO or VP Infrastructure based on org size") and flag identifying them as a Phase 0 discovery action. Never skip the table because names aren't known yet — the structure itself is the useful part.

## Step 3 — Environment & whitespace assessment

Two parts:

1. **Technical risk/opportunity scan** against the current footprint described in Step 1: is any platform approaching EOA/EOL (check [Platforms-Hardware](../Platforms-Hardware/README.md)), any ONTAP version approaching end of support, any data-protection gap (no tested recovery point, no offsite/cloud copy), any security-hardening gap (ARP/MAV not enabled, no SnapLock/immutability story — see [Security-Hardening](../Security-Hardening/README.md)). These double as both **TAM risk items** and **SAM expansion triggers**.
2. **Portfolio whitespace scan** against the [NetApp portfolio whitespace map](README.md#netapp-portfolio-whitespace-map-for-sam-pipeline-building) — for each row in that table, state whether the customer already has it, and if not, whether this specific scenario creates a plausible trigger to introduce it. Don't force-fit every row; name the 2–4 that are genuinely relevant to this customer's situation.

## Step 4 — Phased engagement plan

Build a plan with these four phases. Adjust the timeframes to the actual urgency of the scenario (a P1-incident-driven engagement compresses Phase 0–1 into days; a routine annual account-planning cycle can spread all four phases across a quarter) — state the adjusted timeframe explicitly rather than defaulting to a generic quarter-long cadence for every scenario.

| Phase | Objective | Typical activities | Owner (CSM/TAM/SAM) | Exit criteria |
| --- | --- | --- | --- | --- |
| **Phase 0 — Discover & confirm** | Close every gap flagged "TBD" in Steps 1–3; confirm the plan is built on fact, not assumption | Stakeholder-identification calls, environment/architecture review, health-score/AutoSupport data pull, current-state technical review | Whoever owns the relationship today | Stakeholder map has no unresolved "TBD" on the high-power quadrants; technical footprint is confirmed, not assumed |
| **Phase 1 — Align & quick win** | Build/confirm champion buy-in; deliver one visible, low-effort win to establish credibility before asking for anything bigger | Present findings from Phase 0 back to the champion/technical buyer; propose and execute one fast, low-risk action (e.g., a config/health remediation, a quick QBR readout, a scoped technical assessment) | CSM/TAM-led | Champion has seen a concrete, delivered result; agreement in hand on what Phase 2 will cover |
| **Phase 2 — Core execution** | Deliver the substantive work — the technical remediation, the adoption program, the qualified opportunity pursuit | Execute the prioritized action list from Step 3 (technical items via TAM, adoption/success-plan items via CSM, MEDDPICC-qualified opportunity pursuit via SAM); regular cadence check-ins (weekly for active technical work, bi-weekly/monthly otherwise) | Split by workstream owner | Each prioritized item from Step 3 is closed, in progress with a committed date, or explicitly deprioritized with a stated reason |
| **Phase 3 — Review & expand** | Confirm the defined success criteria (Step 1) were met; formally identify what's next | QBR-style readout against the original success definition; refresh the health score; re-run the whitespace scan now that trust/credibility is higher; propose the next expansion or renewal motion | SAM-led for expansion, CSM-led for renewal | Success criteria explicitly confirmed met/not met; next-phase opportunity (if any) is documented as a new qualified pipeline item, not left implicit |

**Prioritization within each phase**: when a phase has more than 2–3 candidate action items, rank them using a simple impact-vs-effort call — state it as such (e.g., "high impact/low effort — do first," "high impact/high effort — schedule with a committed date," "low impact — defer or drop") rather than listing everything as equally urgent.

## Step 5 — Success criteria & measurement

For each phase, state what "done" looks like in terms the engineer (and the customer, where relevant) can verify without judgment calls:

- **Health score inputs to track**: pick 4–6 signals genuinely relevant to *this* account (per [README.md](README.md#customer-success-planning--frameworks)) — e.g., ONTAP/platform version currency, open case volume/severity trend, adoption of a specific feature/capability being pushed, renewal date proximity, AutoSupport delivery consistency (a stale/missing AutoSupport is itself a health signal, not just a data gap — see [Operations-Troubleshooting](../Operations-Troubleshooting/README.md)).
- **Milestone dates**: every Phase 1–3 action gets a committed date, not an open-ended "ongoing."
- **Opportunity qualification (if a SAM motion is in play)**: state the MEDDPICC status explicitly — which of Metrics/Economic buyer/Decision criteria/Decision process/Identify pain/Champion/Paper process/Competition are confirmed vs. still open. An engagement plan that proposes pursuing an opportunity without a stated champion or economic buyer should say so plainly, not imply the deal is further along than it is.
- **Review cadence**: state how and when this plan itself gets revisited (a formal QBR, an internal account-team sync, an ad hoc check tied to the next milestone date) — a plan with no stated review point will silently go stale.

## Step 6 — Output format

Present the finished plan as: (1) a one-paragraph scenario summary, (2) the stakeholder map table, (3) the environment/whitespace findings, (4) the four-phase plan table with owners and exit criteria, (5) the success-criteria/measurement section. Flag explicitly anywhere the plan is built on an assumption rather than a confirmed fact from the engineer, so it's clear what still needs validating before this goes in front of the customer.
