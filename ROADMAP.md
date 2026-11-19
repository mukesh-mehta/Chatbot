# Chatbot development roadmap

**Baseline:** v0.2 prototype · **Updated:** 19 November 2026

The goal is to grow the original flight-chatbot idea into a reliable conversational
travel workspace. This document is a prioritized backlog, not a list of features
already implemented or a promised delivery schedule. Milestones should ship in
small releases after their acceptance criteria are met.

The current release deliberately solves a narrow problem: it runs on Python 3.12,
lets a person build a trip through chat or a form, and displays fictional flight
options. Real supplier availability, general-purpose AI, accounts, and bookings
are still future work.

## Status and priority conventions

- **Delivered:** implemented in the active runtime and covered by the checks
  described in the verification document.
- **Planned:** designed backlog; not implemented or implied by the current UI.
- **P0:** required before the dependent release can be shared as a service.
- **P1:** valuable next-release functionality with clear dependencies.
- **P2:** later expansion after the underlying workflow is reliable.

Dependencies identify work that must land first. They do not imply exact dates.
An item is complete only when its behavior, tests, documentation, and failure
handling have all been reviewed. The project does not currently have assigned
owners or delivery estimates for planned items.

## M0 — Runnable foundation · delivered

The modernization establishes these capabilities:

- [x] Python 3.12 entry point with portable pinned dependencies.
- [x] Preserved legacy implementation with an explicit compatibility boundary.
- [x] Flask application factory and a Waitress launcher.
- [x] Immutable trip model and shared validation for chat and direct searches.
- [x] Deterministic multi-turn collection of route, dates, adults, and cabin.
- [x] Eight supported airports and common city aliases.
- [x] One-way and round-trip sample results, including valid same-day ordering.
- [x] Responsive chat workspace and synchronized trip editor.
- [x] Price/duration sorting, local itinerary selection, and JSON export.
- [x] Bounded tab-local history, reset confirmation, and refreshed offer validation.
- [x] Python and JavaScript checks plus Python 3.12 Linux/Windows CI configuration.
- [x] Non-root container build, HTTP smoke check, and contributor documentation.

**Boundary:** this baseline does not make the old Rasa/Facebook application
Python 3.12 compatible. It provides a new supported runtime for the same project.
No live ticket, reservation, or supplier price exists in this release.

## Release sequence and dependency map

| Milestone | Outcome | Depends on | Release gate |
| --- | --- | --- | --- |
| M1 | Robust frontend and API foundation | M0 | Browser journeys, accessibility review, stable contracts |
| M2 | Measured language understanding | M1 core contracts | Labeled evaluation, controlled fallback, bounded model behavior |
| M3 | Live flight discovery | M1 + supplier access | Supplier contract tests, truthful prices, timeout/expiry handling |
| M4 | Accounts and durable trips | M1 | Ownership checks, migrations, retention, restore tests |
| M5 | Operable hosted pilot | M3 + M4 | Protected deployment, measured limits, backups and incident runbooks |
| M6 | Assisted booking workflow | M3 + M4 + M5 | Repricing, explicit confirmation, idempotent supplier operations |
| M7 | More channels and markets | Stable M5 or M6 | Channel/locale-specific evaluation and support capability |
| Ongoing | Governance and maintenance | Every milestone | Dependency, provenance, release, and scope review |

M2 can proceed alongside M3 after their shared contract work is complete.
Booking must not be implemented as an unreviewed shortcut through the language
model. The application should remain usable through the form when AI is disabled.

## M1 — API reliability and maintainable application boundaries

**Priority:** P0/P1 · **Status:** planned

### CORE-01 · Versioned request and response schemas · P0

Define typed API schemas for trip state, assistant replies, provider offers, and
errors. Generate a versioned OpenAPI document and example clients.
**Accept when:** incompatible fields fail predictably, fixtures validate against
the published contract, and one documented migration path exists for clients.
**Depends on:** M0.

### CORE-02 · Explicit conversation transitions · P1

Represent slot updates, ambiguity, clarification, search, and reset as named
transitions instead of growing one parser function indefinitely.
**Accept when:** a transcript can explain why a field changed, contradictory
updates prompt clarification, and unrecognized input cannot silently retain a
wrong route while displaying fresh results. **Depends on:** CORE-01.

### CORE-03 · Strong provider-result validation · P0

Validate supplier output separately from user input: currency, amount units,
timestamps, airport codes, offer validity, itinerary ordering, and missing fields.
**Accept when:** malformed provider fixtures fail closed with a useful response;
no partial or invented fare is displayed as bookable. **Depends on:** CORE-01.

### CORE-04 · Request tracing without message-content logs · P1

Add request IDs and structured events for validation/search outcomes. Define
which metadata is allowed in logs and ensure exception handling follows it.
**Accept when:** an operator can correlate an error across layers without seeing
raw conversation text, tokens, or passenger details. **Depends on:** CORE-01.

### CORE-05 · Enforced limits and consistent errors · P0

Add deployment-level rate limits, per-provider concurrency limits, bounded
timeouts, and a standard error taxonomy beyond local input validation.
**Accept when:** excessive load receives a documented retry response, worker
capacity stays bounded, and clients can distinguish retryable from terminal
failures. **Depends on:** CORE-01, CORE-04.

### CORE-06 · Dependency and compatibility maintenance · P1

Automate dependency update proposals, include a reproducible lock-refresh process,
and evaluate newer Python releases in a separate compatibility matrix.
**Accept when:** updates include clean installs and meaningful behavior checks;
Python 3.12 remains supported until a documented support-policy change.
**Depends on:** M0; does not require a framework rewrite.

## M1 — Frontend product and interaction backlog

**Priority:** P0/P1/P2 · **Status:** planned beyond the delivered workspace

### FE-01 · Split rendering into focused components · P1

Separate conversation, trip form, results, and saved itinerary into small modules
with clear state/event boundaries. Keep the current buildless approach unless
measured complexity justifies a framework.
**Accept when:** updating the results component does not reset drafts or focus,
and shared state has one documented owner. **Depends on:** M0.

### FE-02 · Automated browser journeys · P0

Add repeatable desktop and mobile tests for chat-to-form updates, round trips,
invalid input, airport swap, sorting, saving, download, reload, and reset.
**Accept when:** tests exercise the running API through visible controls and
include delayed responses and connection failures. **Depends on:** FE-01.

### FE-03 · Accessibility audit and remediation · P0

Audit keyboard order, screen-reader announcements, labels, contrast, touch targets,
zoom, reduced motion, and mobile virtual keyboards across representative browsers.
**Accept when:** all primary flows work without a pointer, validation moves focus
sensibly, and the audit records resolved issues and any remaining limits.
**Depends on:** FE-01; use FE-02 to retain fixes.

### FE-04 · Reliable drafts and asynchronous interactions · P1

Keep unsent drafts across navigation, announce only new assistant content, and
handle cancelled or out-of-order requests without replacing a newer trip.
**Accept when:** a slow response cannot overwrite current edits, retry never
duplicates messages, and storage failure leaves the page usable.
**Depends on:** FE-01, CORE-01.

### FE-05 · Searchable airport selection · P1

Replace the short airport dropdown with an accessible combobox when the catalog
grows. Show city, country, airport name, and code; distinguish metropolitan areas
from individual airports.
**Accept when:** keyboard selection, no-match states, duplicate city names, and
screen-reader announcements are tested. **Depends on:** FE-03, PROV-02.

### FE-06 · Better date and traveller controls · P1

Add linked departure/return calendars, clear timezone explanations, flexible-date
selection where supported, and explicit adult/child/infant rules.
**Accept when:** invalid combinations cannot be submitted, supported age rules
come from the supplier contract, and the native-input fallback still works.
**Depends on:** CORE-01, PROV-03, FE-03.

### FE-07 · Useful filtering and comparisons · P1

Offer filters for stops, departure windows, duration, baggage, and price only when
the provider supplies those facts. Add side-by-side comparison of a bounded set.
**Accept when:** applied filters are visible and resettable, sorting is stable,
and unknown baggage/fare details are shown as unknown. **Depends on:** PROV-03.

### FE-08 · Fare and itinerary details · P0 for live discovery

Add a detail view with all legs, local dates, layovers, currency, total-price scope,
fare rules, price timestamp, and expiry. Explain sample versus live mode everywhere.
**Accept when:** users can distinguish a search result, saved quote, and confirmed
booking without relying on color. **Depends on:** CORE-03, PROV-03, PROV-04.

### FE-09 · Saved-trips workspace · P1

Add named trips, recent searches, a saved-itinerary drawer, and explicit unsave
controls. Separate local-only state from account-backed records.
**Accept when:** empty/loading/error states work and each saved item shows whether
its price needs refreshing. **Depends on:** DATA-01, DATA-02, PROV-04.

### FE-10 · Share and export with ownership controls · P2

Support a readable itinerary export and optional revocable sharing. Let the owner
choose what details are included before generating a shareable artifact.
**Accept when:** private trips cannot be enumerated, revoked links stop working,
and exports exclude unnecessary personal data. **Depends on:** DATA-03, DATA-04.

### FE-11 · Localization and currency presentation · P2

Move interface strings into message catalogs and support locale-aware numbers,
dates, pluralization, and right-to-left layout. Keep display conversion separate
from the supplier's actual settlement currency.
**Accept when:** at least two locales have complete core-flow tests and no
currency conversion is presented as a supplier guarantee. **Depends on:** PROV-03.

### FE-12 · Better small-screen navigation · P1

Evaluate chat/trip tabs, a sticky search summary, safe-area spacing, and deliberate
scroll/focus restoration on phones without hiding essential fare information.
**Accept when:** primary controls remain reachable with the keyboard open and
there is no horizontal scrolling at supported narrow widths. **Depends on:** FE-03.

### FE-13 · Measured loading and rendering performance · P1

Measure initial load, input responsiveness, search latency, large-result rendering,
and layout movement before selecting optimizations.
**Accept when:** a recorded baseline, agreed budgets, and representative low-end
device checks exist; performance claims cite measurements. **Depends on:** FE-02.

### FE-14 · Recoverable connection and supplier failures · P0

Distinguish offline, timeout, rejected input, expired offers, rate limits, and
supplier downtime. Provide focused retry actions and preserve the user's draft.
**Accept when:** each state has a browser test and retries do not create duplicate
bookings or misleading availability. **Depends on:** CORE-05, PROV-05.

### FE-15 · Reusable design system documentation · P1

Document tokens, typography, spacing, buttons, inputs, cards, error messages, focus
states, and loading patterns. Use examples from the actual app rather than a second
unmaintained mockup.
**Accept when:** new screens can reuse patterns with accessibility notes and
visual regression coverage. **Depends on:** FE-01, FE-03.

### FE-16 · Privacy-conscious product feedback · P2

Collect explicit feedback on misunderstood requests and unsuccessful searches,
with clear controls over whether any text accompanies the report.
**Accept when:** event schemas exclude raw conversation by default, deletion is
documented, and feedback cannot become an unintended data-exfiltration channel.
**Depends on:** DATA-04, GOV-03.

## M2 — Evaluated language understanding and optional AI

**Status:** planned · **Goal:** improve understanding without inventing travel facts.

| ID / priority | Work | Acceptance criteria | Dependencies |
| --- | --- | --- | --- |
| NLU-01 / P0 | Build a consented, labeled evaluation set from new examples; audit any legacy data before reuse | Include multi-turn corrections, typos, ambiguity, negative cases, and unsupported requests; keep test examples out of training | GOV-02, CORE-02 |
| NLU-02 / P1 | Define an extractor interface for intents, slot proposals, uncertainty, and explanations | Rule baseline and one alternative produce the same typed proposal; neither can bypass trip validation | CORE-01, CORE-02 |
| NLU-03 / P1 | Compare a maintained local classifier with an optional LLM adapter | Publish measured slot/intent results, latency, cost, and failure categories on the held-out set | NLU-01, NLU-02 |
| NLU-04 / P0 | Constrain model output and defend tool boundaries | Untrusted messages cannot alter tool permissions, invent supplier confirmations, or inject arbitrary URLs/commands | NLU-02, CORE-03 |
| NLU-05 / P1 | Handle ambiguous airports, relative dates, and corrections | Ask a specific clarification when meaning is uncertain; verify that clarification does not silently change unrelated fields | NLU-01, NLU-02 |
| NLU-06 / P1 | Add prompt/model versioning and regression evaluation | Every model/prompt change is reproducible and compared with a recorded baseline; failed thresholds block release | NLU-03, NLU-04 |
| NLU-07 / P1 | Implement predictable fallback and usage limits | Model timeout/quota failure falls back to the form or approved baseline; provider limits are enforced before calls | CORE-05, NLU-03 |
| NLU-08 / P2 | Evaluate additional languages and code-switching | Native-language review and per-language results precede a support claim; unsupported cases remain clear | NLU-01, FE-11 |

**M2 exit gate:** document the selected approach and its tradeoffs. The assistant
must remain useful with model calls disabled. An improved language score alone
does not justify live booking authority or removal of validation.

## M3 — Live flight discovery

**Status:** planned · **Prerequisite:** approved supplier access and a documented contract.

| ID / priority | Work | Acceptance criteria | Dependencies |
| --- | --- | --- | --- |
| PROV-01 / P0 | Select and connect a supported supplier sandbox | Credentials stay server-side; supported markets, quotas, costs, and commercial limits are documented | CORE-01, GOV-01 |
| PROV-02 / P1 | Maintain an airport/city/timezone catalog | Source, license, update cadence, airport aliases, and city-airport distinctions are recorded | GOV-02 |
| PROV-03 / P0 | Normalize supplier offers into the common schema | Multi-leg trips, local timezones, currency precision, passenger pricing, and unavailable fields are covered by fixtures | CORE-03, PROV-01, PROV-02 |
| PROV-04 / P0 | Track offer expiry and refresh/repricing | An expired or changed quote cannot be presented as a current confirmed fare; the UI explains changes | PROV-03, FE-08 |
| PROV-05 / P0 | Add timeouts, bounded retry, and outage isolation | Simulated timeouts/429/5xx responses do not saturate the API or create retry storms | CORE-05, PROV-01 |
| PROV-06 / P1 | Cache safe search results with provider-aware rules | Cache key includes every price-relevant parameter; freshness/terms are respected and stale values are labeled | PROV-03, PROV-04 |
| PROV-07 / P1 | Maintain contract fixtures and periodic sandbox checks | Supplier schema changes fail a readable check; sanitized fixtures reproduce common failures without live credentials | PROV-03, PROV-05 |

**M3 exit gate:** search-only live discovery works end to end in the supplier
sandbox, with honest frontend labeling and failure states. Results are still not
bookings. No production supplier account or live fare is configured in M0.

## M4 — Identity and durable trip management

**Status:** planned · **Goal:** move beyond best-effort browser-tab storage.

| ID / priority | Work | Acceptance criteria | Dependencies |
| --- | --- | --- | --- |
| DATA-01 / P0 | Add database-backed trips and schema migrations | Clean install, upgrade with existing records, rollback strategy, and backup/restore checks are documented | CORE-01 |
| DATA-02 / P0 | Add login, session lifecycle, and record ownership | Every trip operation checks ownership; logout/expiry and cross-user negative tests pass | DATA-01 |
| DATA-03 / P0 | Add versioned edits and idempotent mutations | Two devices editing the same trip receive a conflict instead of silently losing data; retries are safe | DATA-01, DATA-02 |
| DATA-04 / P0 | Define retention, export, and deletion workflows | Users understand stored fields; deletion propagates to applicable stores and is tested with realistic backups/log policies | DATA-01, DATA-02, GOV-03 |
| DATA-05 / P1 | Migrate local trips into an account explicitly | Import is user-initiated, validated, deduplicated, and confirmed; browser data is never silently uploaded at login | DATA-02, DATA-03, FE-09 |
| DATA-06 / P2 | Add team trip collaboration and permissions | Sharing roles, revocation, audit events, and cross-team isolation are verified | DATA-02, DATA-03, DATA-04 |

**M4 exit gate:** no user can read or modify another user's records by changing an
identifier. Test migrations and restoration against populated databases before
the application relies on durable state.

## M5 — Deployment, observability, and a controlled pilot

**Status:** planned · **Goal:** a service that can be operated and recovered.

| ID / priority | Work | Acceptance criteria | Dependencies |
| --- | --- | --- | --- |
| OPS-01 / P0 | Create a repeatable deployment and environment configuration | TLS, host/proxy settings, non-root images, secret injection, migrations, and rollback are documented and rehearsed | CORE-05, DATA-01 |
| OPS-02 / P0 | Separate liveness, readiness, and dependency health | Readiness reflects essential services without cascading provider outages; probes do not leak credentials | PROV-05, DATA-01 |
| OPS-03 / P1 | Add bounded telemetry and actionable alerts | Queue-free request latency, provider latency, error rates, quota usage, and cost are visible without raw message logs | CORE-04, PROV-05 |
| OPS-04 / P0 | Run representative load and failure tests | Record workload, concurrency, hardware, p50/p95 latency, saturation, and recovery; agree limits from evidence | OPS-01, OPS-03 |
| OPS-05 / P0 | Rehearse recovery and incident response | Backup restoration and deployment rollback meet explicitly agreed objectives; ownership and escalation are clear | DATA-04, OPS-01 |
| OPS-06 / P1 | Ship through a small protected pilot | Feature flags, support workflow, feedback collection, and rollback thresholds are in place before broad exposure | FE-14, OPS-02–OPS-05 |

**Capacity policy:** there are no throughput or availability claims yet. Set pilot
targets after observing the real supplier and storage workload; do not infer
production capacity from a passing local smoke test.

## M6 — Booking only after discovery is trustworthy

**Status:** planned · **All booking features remain disabled in the prototype.**

| ID / priority | Work | Acceptance criteria | Dependencies |
| --- | --- | --- | --- |
| BOOK-01 / P0 | Model quote, selected offer, reservation, payment, and ticket as separate states | A saved search can never appear as a confirmed ticket; transitions and recovery are explicit | PROV-04, DATA-03 |
| BOOK-02 / P0 | Add a review-and-confirm flow with repricing | Travellers see the supplier's current price and required terms before explicitly confirming; changed quotes require a fresh decision | BOOK-01, FE-08 |
| BOOK-03 / P0 | Make reservation/payment operations idempotent | Duplicate submissions, network loss, webhook replay, and partial completion cannot create unnoticed duplicate charges or reservations | BOOK-01, DATA-03, OPS-05 |
| BOOK-04 / P0 | Integrate an approved hosted payment flow and verified callbacks | Sensitive payment entry stays with the selected payment service; signatures, replay windows, and reconciliation are tested | BOOK-02, BOOK-03 |
| BOOK-05 / P1 | Support cancellation, refund status, and human assistance | Supplier-specific eligibility and status are shown accurately; uncertain outcomes have an operator path and audit trail | BOOK-03, BOOK-04 |

**M6 exit gate:** complete sandbox journeys, including failed payment, successful
payment with delayed ticketing, duplicate callbacks, and cancellation. Obtain the
necessary supplier, payment, operational, and security approvals before any real
transaction. The language model may propose a workflow step; it must not become
an unrestricted transaction executor.

## M7 — Channels and broader travel workflows

**Status:** later expansion; prioritize evidence from the pilot.

- **EXT-01 / P2 — Modern messaging adapter.** Reintroduce a supported messaging
  channel behind the same API only after webhook signatures, event deduplication,
  channel permissions, and account linking are tested. Depends on DATA-02 and
  CORE-05. Do not revive archived public-tunnel scripts as deployment tooling.
- **EXT-02 / P2 — Voice input.** Add explicit microphone permission, visible
  recording state, editable transcripts, cancellation, and retention controls.
  Depends on FE-03, NLU-08, and GOV-03. Text entry must remain fully usable.
- **EXT-03 / P2 — Price alerts.** Add opt-in saved searches and bounded background
  polling with freshness rules, unsubscribe, deduplication, and provider quotas.
  Depends on DATA-04, PROV-06, and OPS-03.
- **EXT-04 / P2 — More trip types.** Consider multi-city, mixed-cabin, and nearby
  airport searches only after the provider schema supports them. Accept when
  pricing and leg validation cover the new combinations. Depends on PROV-03.
- **EXT-05 / P2 — Disruption assistance.** Explain delay/cancellation updates and
  available assistance from authoritative supplier data. Do not invent rebooking
  eligibility. Depends on BOOK-05 and an approved operational data feed.

## Governance and recurring maintenance

- **GOV-01 / P0 — Product scope and supplier obligations.** Record which markets,
  user groups, and activities each release supports. Review provider terms and
  distinguish search, reservation, payment, and support responsibilities before
  adding them. Deliverable: a reviewed capability matrix.
- **GOV-02 / P0 — Provenance inventory.** Identify source/version/license for any
  historical code or dataset proposed for reuse. Retain required notices; do not
  assume the new MIT grant covers archived third-party files. Deliverable: a
  reviewed inventory with explicit reuse decisions.
- **GOV-03 / P0 — Data handling review.** Document collected fields, purpose,
  retention, third-party transfers, logging, access, and deletion. Review changes
  before sending conversation text to a model or supplier. Deliverable: a data-flow
  map and approved operating rules for the intended deployment.
- **GOV-04 / P1 — Releases and support policy.** Maintain changelog, migration
  notes, dependency review, vulnerability reporting, supported runtime/browser
  versions, and rollback instructions. Deliverable: repeatable release checklist
  applied to each release.

## Proposed measurement plan

These are measurement categories and future release decisions, **not current
benchmark results or guaranteed targets**.

| Area | Measure | How to use it |
| --- | --- | --- |
| Understanding | Correct slots, clarifications, unsupported-request handling | Compare new extractors with the deterministic baseline on held-out transcripts |
| Task success | Valid trip creation and successful search completion | Identify where users need the form, abandon a flow, or receive confusing errors |
| Frontend | Input responsiveness, layout movement, keyboard/reader completion | Set budgets on representative devices and retain them in browser checks |
| Supplier quality | Availability errors, repricing rate, latency, expiry | Tune freshness, retries, and UI expectations without inventing certainty |
| Operations | Request latency, error rate, saturation, recovery time | Establish capacity and incident thresholds from load/failure tests |
| Cost | Supplier calls and model usage per completed search | Enforce usage budgets and compare designs before a wider rollout |

## Suggested next three contributions

1. **CORE-01 + FE-02:** publish the API contract and automate the existing browser
   journeys before adding new product complexity.
2. **FE-03 + FE-04:** audit keyboard/screen-reader behavior and tighten asynchronous
   draft/state handling while the interface is still small.
3. **NLU-01 + PROV-01:** build an evaluation corpus and choose a supplier sandbox;
   these establish evidence and access for the next functional improvements.

Each contribution should leave the Python 3.12, no-credential sample experience
working. A future feature may be optional, but its absence must never prevent the
baseline application from starting.
