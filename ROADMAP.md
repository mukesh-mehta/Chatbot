# Chatbot development roadmap

**Baseline:** v0.2 prototype · **Updated:** 19 November 2026

## Development goal

Grow the existing flight-planning prototype into a **local, collaborative travel
workspace**. A person should be able to build a multi-city plan, compare fictional
flights, save and share it with local test users, resolve conflicting edits,
inspect simulated schedule changes, and recover their work after a restart.

The difficult part is keeping one coherent trip across conversation, forms,
search results, database revisions, permissions, imports, and background updates.
An older browser response must not replace a newer edit; a retry must not create
a second trip; a restored database must not contain half of an accepted change.

**All 12 extensions below are planned.** Their designs and performance targets
are not implemented behavior or benchmark results. The current app remains the
smaller, working baseline described in [README](README.md#what-is-implemented).
This roadmap replaces the previous live-service expansion plan.

## Scope and operating environment

- Run on Linux with Python 3.12, SQLite, JavaScript, and a local browser. Node is
  development tooling; preserve a start path without a frontend build.
- After dependencies are installed from available package mirrors or prepared
  offline packages, every required workflow must work without external internet.
  Keep fonts, scripts, styles, catalog data, and schedule fixtures local.
- Use one machine for the server, optional local workers, and browser sessions.
  Exercise multiple users through isolated browser contexts on that machine.
  Cross-device access and public hosting are not completion requirements.
- Use original synthetic trips, fictional inventory, and local test users. Do not
  require real customer, personal, health, financial, or children's data,
  production accounts, external credentials, or employer/client material.
- Conversation handling remains an explicit rule-based parser. Model training,
  inference, evaluation, AI/ML infrastructure, and datasets for those purposes are
  outside this roadmap. Application behavior tests use synthetic inputs only.
- Live airline APIs, ticketing, payment, external messaging, cloud services, voice,
  and sound are outside this phase. Schedule and price changes are simulated.
- No GPU, Docker, system package installation, native GUI toolkit, or hosted
  service is required. Existing optional container packaging is separate from
  the local milestone gates.

Use a reference budget of **4 CPU cores and 16 GB RAM** for measurements.
Dependency and bundled-browser availability must be checked in the actual target
environment before calling its offline setup verified. Do not download a browser
or dataset during a required workflow.

## Twelve-feature product roadmap

Each feature expands a documented limitation of the current prototype. IDs are
stable references for issues and contributions. These are connected features,
not twelve independent applications.

| # | ID | Planned feature | Current limitation | Depends on |
| --- | --- | --- | --- | --- |
| 1 | F01 | Durable trip workspace and migrations | One selected itinerary exists only in tab storage | M0 |
| 2 | F02 | Local accounts and trip ownership | No accounts or server-side permissions | F01 |
| 3 | F03 | Accessible frontend and recoverable drafts | Basic controls exist; automated browser coverage and durable draft recovery do not | F01 |
| 4 | F04 | Multi-city and timezone-aware planning | One-way/round-trip inputs use eight airports and one timezone | F01, F03 |
| 5 | F05 | Versioned synthetic schedules and route search | The provider generates three simple sample offers | F04 |
| 6 | F06 | Advanced itinerary comparison | Results support price/duration sorting only | F03, F05 |
| 7 | F07 | Conflict-safe edits and idempotent commands | No shared durable revision or retry identity | F01, F02, F03 |
| 8 | F08 | Shared planning and revision history | No shared trips, roles, or persisted edit history | F02, F07 |
| 9 | F09 | Portable imports, exports, and tab migration | One JSON selection can be exported but not imported | F02, F04, F05, F07 |
| 10 | F10 | Schedule-change simulation and local alerts | No durable change-monitoring workflow | F05, F06, F07 |
| 11 | F11 | Backup, restore, retention, and deletion | No durable database to back up or restore | F08, F09, F10 |
| 12 | F12 | Local observability, performance, and recovery | No measured capacity or systematic failure campaign | F01–F11 |

F12 instrumentation begins with F01; its final gate covers the completed system.
F03 provides shared components early and gains screens as dependent features
land. Dependencies describe required behavior, not a requirement to finish every
screen before starting related backend work.

## M0 — Working foundation

Already delivered:

- [x] Python 3.12 runtime, pinned dependencies, Flask, and a Waitress launcher.
- [x] Limited deterministic conversation parsing and an editable trip form.
- [x] Shared validation, eight airports, one-way and round-trip searches.
- [x] Fictional offers, price/duration sorting, and sample-data labels.
- [x] Responsive chat workspace, one saved selection, and JSON download.
- [x] Bounded tab history, reset confirmation, timeout handling, and validation.
- [x] Python/JavaScript tests and the documented local HTTP smoke check.
- [x] An explicit archive boundary for the historical Rasa implementation.

The server is currently stateless. Database-backed trips, accounts, shared
editing, workers, and the new screens below are not delivered. The archive has
not been ported to Python 3.12 and is not a dependency of this plan.

## F01 — Durable trip workspace and migrations

**Status:** Planned · **Depends on:** M0

**Outcome:** Create, name, reopen, duplicate, and archive several trips without
depending on the lifetime of a browser tab.

Implementation work:

- Define versioned API contracts for trip IDs, revisions, errors, selections, and
  pagination. Preserve a compatibility path for existing stateless chat/search.
- Add SQLite persistence with transactions, foreign keys, migration versions, and
  a documented upgrade procedure. Separate trip state from selected-offer snapshots.
- Preserve inventory version and pricing context with each saved selection.
  Never silently replace a saved snapshot with a newly generated offer.
- Introduce a service/storage boundary so HTTP handlers, later workers, and
  imports share validation and transaction rules.
- Build a paginated trip list with create, rename, duplicate, archive, reopen,
  empty, loading, and failure states. Use an explicit local workspace before F02.

Acceptance checks:

- Create several named trips, restart the process, and reopen the same records.
- Upgrade a populated older schema without changing IDs or snapshots. Reject an
  unknown newer schema without modifying the database.
- Interrupt an update before commit: the old revision survives. Interrupt after
  commit: the whole new revision survives, including selection metadata.
- Duplication creates a new identity; archive/reopen never mutates another trip.
- Existing stateless chat and search behavior continues to pass its checks.

## F02 — Local accounts and trip ownership

**Status:** Planned · **Depends on:** F01

**Outcome:** Fictional users on the same machine have separate workspaces and
cannot read or change each other's private trips.

Implementation work:

- Add local test accounts, password hashing, session expiry, logout, and an
  offline reset procedure. Use locally generated application secrets, with no
  email, OAuth, production account, or external credential dependency.
- Bind every operation to an owner and centralize authorization across listing,
  updates, duplication, archives, imports, exports, and later background work.
- Add browser session protections and bounded login attempts as ordinary app
  behavior. Avoid disclosing whether another user's private record exists.
- Migrate the initial workspace to an explicitly selected owner. Do not retain
  an anonymous fallback that bypasses permissions once accounts are enabled.
- Build login, logout, expired-session, and ownership-aware navigation states.

Acceptance checks:

- Two isolated browser contexts see distinct trips; changing an ID or calling
  the API directly cannot bypass ownership.
- Logout and expiry invalidate access, including from an already open page.
- Switching accounts never displays the previous user's cached trip or draft.
- Ownership migration completes atomically or preserves the original workspace.
- All identities and passwords used by fixtures are synthetic and disposable.

## F03 — Accessible frontend and recoverable drafts

**Status:** Planned · **Depends on:** F01

**Outcome:** The growing workspace remains usable by keyboard and on narrow
screens, while errors and slow responses preserve unfinished work.

Implementation work:

- Split trip lists, chat, editing, results, and dialogs into focused modules with
  one documented state owner and shared loading, validation, focus, and errors.
- Give requests explicit identities. Apply responses only to the matching trip
  and revision; keep local drafts separate from confirmed server state.
- Store bounded drafts with schema versions and explicit discard/recovery.
  Handle unavailable/full storage. Scope drafts by user after F02 and route stale
  drafts through the F07 conflict flow.
- Add keyboard navigation, accessible dialogs, meaningful announcements, focus
  restoration, and mobile layouts as each screen is introduced.
- Automate browser journeys against the running local API using an available
  browser executable; exercise delayed responses, connection loss, and reload.

Acceptance checks:

- A slow response for trip A cannot replace trip B or overwrite newer edits.
- Reload recovers a draft; failed saves never mark uncommitted work as saved.
- Core journeys work by keyboard, at 200% zoom, and at a 390px viewport without
  page-level horizontal overflow. Review contrast and screen-reader behavior.
- New messages and reordered results do not unexpectedly steal keyboard focus.
- Browser checks exercise visible controls and the real API, not just helpers.

## F04 — Multi-city and timezone-aware planning

**Status:** Planned · **Depends on:** F01, F03

**Outcome:** Plan up to six ordered travel legs and understand the local date
and time at each stop.

Implementation work:

- Evolve the trip schema into ordered legs and migrate existing one-way and
  round-trip records without changing their meaning.
- Bundle a documented airport/city/timezone catalog with source/license records.
  Search locally and distinguish cities from individual airports.
- Validate chronology using UTC instants; display airport-local times. Define
  behavior for ambiguous/nonexistent local times, overnight travel, daylight-saving
  changes, and date-line crossings in synthetic fixtures.
- Build an accessible airport combobox and add/remove/reorder leg controls.
  Show precise errors while retaining valid parts of the draft.
- Keep chat edits deterministic: identify the affected leg, clarify ambiguity
  through explicit rules, and provide the form as a complete alternative.

Acceptance checks:

- Reorder/remove legs without orphaning dates or retaining stale selections.
- Reject impossible chronology, identical leg endpoints, and excess legs.
- Fixed cases cover leap days, overnight travel, timezone changes, and the date
  line, with expected results expressed as an independent UTC timeline.
- Original one-way/round-trip records migrate into equivalent plans.
- An ambiguous chat edit cannot silently change the wrong leg.

## F05 — Versioned synthetic schedules and route search

**Status:** Planned · **Depends on:** F04

**Outcome:** Search finite, reproducible fictional inventory with connections,
instead of generating three offers for every request.

Implementation work:

- Define a versioned local schedule format with stable flight IDs, operating dates,
  timezone-qualified times, fictional availability, fare attributes, and integer
  minor-unit prices. Use INR initially; no exchange-rate service is needed.
- Validate and activate complete schedule versions atomically. Retain the version
  used for a search or saved offer so subsequent changes remain explainable.
- Implement bounded route search with connection-time, maximum-stop, date, cabin,
  and traveller constraints. Specify incomplete-result behavior when limits are
  reached; never present a truncated search as an exhaustive cheapest result.
- Separate correctness from caching and sorting. Include every result-affecting
  input, inventory version, and relevant clock value in cache keys.
- Provide original synthetic fixtures and an injected clock. Show the inventory
  version and fictional-data status alongside results.

Acceptance checks:

- On small schedules, compare search with an independent exhaustive enumerator
  for valid routes, total price, elapsed time, and deterministic ordering.
- Reject impossible connections, unsupported cycles, sold-out fixtures,
  malformed prices, and travel outside operating dates.
- The same input, inventory version, and clock produce the same ordered result.
- Failed schedule imports leave the active inventory unchanged and usable.
- Invalid trips receive actionable errors rather than fabricated availability.

## F06 — Advanced itinerary comparison

**Status:** Planned · **Depends on:** F03, F05

**Outcome:** Compare meaningful tradeoffs between fictional itineraries while
keeping every option tied to the current trip and search version.

Implementation work:

- Compose filters for total price, stops, departure window, elapsed time, and
  fixture-provided baggage attributes; represent unknown information explicitly.
- Add stable ordering and comparison of up to three itineraries. Explain total
  versus per-traveller prices and elapsed versus local clock time.
- Show segments, layovers, date boundaries, fare attributes, and inventory version.
  Keep available fixture facts separate from unavailable information.
- Retain filters within a trip, announce empty results, and provide a reset.
  Changed searches invalidate incompatible comparison selections.
- Make comparison controls and details usable on mobile and by keyboard.

Acceptance checks:

- Combined filters return the expected intersection without mutating inputs.
- Ties are stable; zero, unknown, and missing values remain distinct.
- Totals agree across results, comparisons, saved snapshots, and exports.
- Switching trips or inventory versions cannot mix unrelated offers.
- Browser tests exercise filtering, comparison, selection, and empty results.

## F07 — Conflict-safe edits and idempotent commands

**Status:** Planned · **Depends on:** F01, F02, F03

**Outcome:** Two tabs can edit one trip without silent data loss, and retrying
an acknowledged or uncertain request does not repeat a successful mutation.

Implementation work:

- Use monotonic revisions and atomic compare-and-update operations. Return a
  structured, recoverable conflict for a stale starting revision.
- Scope command keys by actor and operation. Persist the request fingerprint and
  committed result in one transaction, with documented retention/expiry rules.
- Return the original result for the same key/payload; reject changed-payload
  reuse. Recheck permissions and resource lifecycle on retries so a stored result
  cannot bypass access revocation or expose deleted content.
- Show saved versus draft state in a conflict view, with explicit reload, reapply,
  or save-as-copy choices. Do not silently choose last-write-wins.
- Apply the contract to saves, copies, archives, imports, and collaboration.
  Disabling a button alone is not duplicate-command protection.

Acceptance checks:

- Race two edits from one revision: one commits, the other gets a conflict.
- Drop a response after commit, then retry: exactly one local mutation exists.
- Simultaneous duplicate commands produce one committed result and stable replies.
- Changed-payload reuse, expiry, and revoked access have explicit outcomes.
- Conflict recovery retains saved and draft states until the user chooses.
  Guarantees apply to local transactions, not arbitrary external side effects.

## F08 — Shared planning and revision history

**Status:** Planned · **Depends on:** F02, F07

**Outcome:** Share trips with named local test users, control editing rights,
and explain how the current revision was reached.

Implementation work:

- Add owner/editor/viewer roles and an action matrix. Select existing local
  users; invitations require neither email nor public sharing links.
- Record actor, revision, operation, time, and a bounded change summary in the
  same transaction as an accepted change. Preserve selected-offer snapshots.
- Provide readable revision differences and restore-as-a-new-revision behavior.
  Restoring a trip must not rewind permissions or erase later history.
- Enforce revocation for reads, writes, exports, history, and local alerts.
  Recheck access when background work executes and when results are displayed.
- Build member management, role badges, read-only states, and permission-loss
  feedback. History is an application record, not a tamper-proof compliance log.

Acceptance checks:

- Check each role/action combination at the API and through representative UI.
- Revoking an editor with an open draft prevents later saves and history reads.
- Restoring an old itinerary creates a new revision without restoring memberships.
- Concurrent edits obey F07 and have exactly matching accepted-change records.
- Archive/deletion policies explicitly define access to historical revisions.

## F09 — Portable imports, exports, and tab migration

**Status:** Planned · **Depends on:** F02, F04, F05, F07

**Outcome:** Transfer synthetic plans between local workspaces and produce
readable files without losing their meaning or fictional-data labels.

Implementation work:

- Define a versioned JSON exchange format for trips, selected snapshots, airport
  references, provenance, and units. Exclude passwords, sessions, conversation
  transcripts, and implicit membership grants.
- Validate imports before committing, enforce byte/record/depth limits, and show
  a preview of creations, duplicates, unsupported versions, and conflicts.
- Define duplicate identity and retry semantics. Import into the acting user's
  workspace; source IDs cannot overwrite another user's records.
- Add escaped, self-contained printable HTML with local styles and no remote
  assets. Preserve sample labels, timezone details, and price units.
- Preview and explicitly confirm migration from existing tab storage and v0.2
  JSON exports. Do not silently transfer browser data when a user logs in.

Acceptance checks:

- Round trips preserve documented trip/snapshot semantics; new IDs and ownership
  follow the destination workspace's rules.
- One invalid record rejects the whole batch; retrying a successful import with
  the same command key creates no additional records.
- Oversized, nested, malformed, and unknown-version inputs fail clearly.
- Script-like text remains text in previews and printable files.
- v0.2 exports have a tested migration path. Offline files never imply a ticket
  or reservation was purchased.

## F10 — Schedule-change simulation and local alerts

**Status:** Planned · **Depends on:** F05, F06, F07

**Outcome:** Replay fictional price, delay, availability, and cancellation events
and inspect their effect on saved plans without a live supplier.

Implementation work:

- Define ordered, versioned scenarios with an injected clock. Events identify
  their inventory version, flight, sequence, and change type.
- Add a local runner/worker with durable checkpoints and bounded batches.
  Make reprocessing safe after interruption and define ordering semantics.
- Evaluate saved-search watches and selected trips against new inventory.
  Preserve the original selection; require explicit action before replacing it.
- Persist deduplicated in-app alerts with seen/dismissed state and links to
  affected trip revisions. Do not send external messages.
- Build scenario controls and an alert drawer with clear simulation labels.
  A fictional flight cancellation is not a refund or booking workflow.

Acceptance checks:

- Known scenarios produce the expected persisted alerts with event/version lineage.
- Stop after alert commit but before checkpoint advancement, then restart:
  reprocessing produces no duplicate alert records.
- Duplicate, out-of-order, malformed, and unsupported events have defined handling.
- Changed/deleted trips and revoked users cannot receive or read alerts through
  a stale watch without the documented version and permission checks.
- Deterministic tests advance the injected clock rather than waiting in real time.

## F11 — Backup, restore, retention, and deletion

**Status:** Planned · **Depends on:** F08, F09, F10

**Outcome:** Recover a consistent local workspace and remove records according
to explicit policies without breaking history or exposing other users' data.

Implementation work:

- Use a consistent SQLite backup operation, a manifest, checksums, and explicit
  schema/fixture version handling. Copying a live database file alone does not
  establish consistency with its WAL state.
- Restore into a separate destination, check integrity and compatibility, and
  require an explicit decision before replacing a working workspace.
- Distinguish archive, deletion, retention cleanup, and historical placeholders.
  Define treatment of snapshots, watches, alerts, command results, and revisions.
- Add bounded cleanup with restartable checkpoints and consistent ownership/
  sharing rules. Keep these operations available through local tooling.
- Document that old backups may contain old data; define expiry/disposal and
  post-restore deletion handling rather than promising deletion from every copy.

Acceptance checks:

- Back up during writes; restore separately and verify relationships, complete
  revisions, ownership, snapshots, and database integrity.
- Corrupt/incompatible backups cannot damage the currently working database.
- Interrupted cleanup resumes without orphaned records or skipped policy work.
- Deleted content cannot be read through history, exports, cached command results,
  or alerts under the stated deletion policy.
- Reproduce recovery through the documented local interface or commands.

## F12 — Local observability, performance, and recovery

**Status:** Planned · **Depends on:** F01–F11 for the final gate

**Outcome:** Explain failures, establish measured limits, and show that overload
or interruption does not silently corrupt accepted work.

Implementation work:

- Add operation IDs and structured local events for searches, saves, migrations,
  imports, conflicts, and jobs. Exclude passwords, tokens, drafts, and chat bodies.
- Expose local readiness, latency, error, conflict, and job-backlog views. Keep
  metric labels bounded; user text and trip IDs are not metric label values.
- Bound pagination, search work, timeouts, and worker queues. Document contention
  and the supported SQLite/process model instead of claiming distributed scale.
- Build reproducible load/failure runners and record hardware, dependency versions,
  seed, workload, warmup, duration, and raw measurements.
- Exercise migration failure, process termination, full/unwritable storage,
  delayed responses, worker restart, and backup restoration.

Acceptance checks:

- Complete a local API/browser journey that creates, shares, conflicts, compares,
  exports, restores, and updates trips.
- Successful responses correspond to committed changes. Injected failures preserve
  internal consistency and produce actionable errors.
- Busy searches/jobs cannot cause unbounded queues or indefinitely block unrelated
  reads; capacity rejection remains visible.
- Diagnostics contain no authentication values or conversation bodies.
- Publish actual measurements against the proposed targets below, including
  failures and limits; targets alone are not evidence.

## Milestones and dependency order

| Milestone | Connected work | Reviewable outcome and exit gate |
| --- | --- | --- |
| M1 | F01 and F03 foundations | Versioned API, durable trip list, populated migrations, automated existing browser journeys |
| M2 | F02, F07, and F03 recovery | Two local users and two editing contexts; isolation, retry safety, conflict UI, and draft recovery |
| M3 | F04 and F05 | Multi-city editor and synthetic route search; timezone cases and reference-search checks |
| M4 | F06 and F09 | Offline filter/compare/select/import/export flow, including v0.2 migration and invalid imports |
| M5 | F08 and F10 | Shared revisions, revocation, scenario playback, and restart-safe local alerts |
| M6 | F11 and F12 | Restore/cleanup rehearsals, capacity measurements, interruption checks, and final browser journey |

Each milestone can span several sessions. Leave a runnable app and a committed
checkpoint at session boundaries. Tests and frontend behavior accompany each
milestone rather than being deferred to M6.

## Suggested session checkpoints

These split the existing backlog into connected reviews. Duration depends on
implementation and findings; they are not promises of one session per feature.

1. Establish current behavior, versioned API contracts, and ownership boundaries;
   automate an existing browser journey before introducing persistence.
2. Implement F01 storage/migrations and the F03 trip list; demonstrate restart,
   populated upgrade, and interrupted-write behavior.
3. Implement F02 identities and F07 revision/command contracts; demonstrate
   cross-user rejection, edit races, and response-loss recovery.
4. Complete F03 draft/conflict interactions and keyboard/mobile journeys, including
   account switches and denied saves.
5. Implement F04 legs/catalogs and migrations; inspect timezone and chronology
   cases through both the API and the editor.
6. Implement F05 bounded search and F06 comparison; compare with the reference
   enumerator and exercise a complete planning flow.
7. Implement F09 exchange files and v0.2 migration; test atomic rejection,
   safe retries, snapshot preservation, and printable output.
8. Implement F08 roles/history and F10 scenario jobs; revoke access during edits
   and restart between alert creation and checkpoint advancement.
9. Implement F11 backup/restore/deletion with populated data; verify that removed
   content cannot leak through secondary read paths.
10. Complete F12 workload/failure runs and the final browser journey; record actual
    measurements and resolve material failures before marking features delivered.

## Proposed success measures

These are **future acceptance targets**, not v0.2 results. Use fixed workloads
and record justified changes before the final run; do not silently shrink a
workload to hide a failed measurement.

| Area | Proposed completion evidence |
| --- | --- |
| Search correctness | At least 100 fixed small schedule cases agree with an independent exhaustive enumerator, including no-route and boundary cases |
| Concurrent edits | In 100 deterministic two-editor races, exactly one update per starting revision commits and the other receives a recoverable conflict |
| Safe retries | Concurrent duplicates and lost-response retries produce one local mutation per scoped command key, including imports and copies |
| Isolation | Every protected endpoint has role/ownership checks using at least three synthetic users; revocation covers workers and cached responses |
| Recovery | Before/after-commit interruption, populated migration, consistent restore, and resumed-cleanup cases preserve documented invariants |
| Frontend | Journeys cover every milestone, delayed responses, expired sessions, keyboard operation, 200% zoom, and a 390px viewport |
| Read performance | On 5,000 synthetic trips across 50 local users, target p95 below 500 ms for authenticated paginated reads with 10 concurrent clients for 120 seconds after 10 seconds of warmup |
| Search and memory | On 10,000 synthetic schedule rows, target p95 below 2 seconds for a fixed corpus of 100 searches with at most two connections per requested leg; each tested API/worker process stays below 1 GB peak RSS |
| Offline operation | With dependencies and a browser prepared, run the final workflow with external traffic blocked and loopback available; record how this was enforced |

Report absolute error counts, percentiles, peak memory, fixture versions, and
workload details. Include unsuccessful operations in error statistics. A search
limit must be visible to callers; do not omit hard cases or call truncated
results exhaustive.

## Frontend delivery map

Frontend work is part of the functional gates. [The frontend guide](docs/FRONTEND.md)
separates the current interface from these planned surfaces.

| Surface | Feature IDs | Required interaction |
| --- | --- | --- |
| Workspace and sign-in | F01, F02, F03 | Reopen a named trip, switch users safely, recover the correct user's draft |
| Multi-city editor | F03, F04 | Search airports, reorder legs, navigate by keyboard, and resolve precise errors |
| Results and comparison | F05, F06 | Inspect inventory version, filters, segments, prices, and comparison choices |
| Conflicts and history | F07, F08 | Compare draft/saved revisions, choose recovery, inspect changes and permissions |
| Import/export workspace | F09 | Preview validation/duplicates and open self-contained printable output |
| Scenarios and alerts | F10 | Replay fictional changes, inspect impact, acknowledge alerts without changing a saved selection |
| Recovery and diagnostics | F11, F12 | Inspect backup/restore outcomes and local health/performance reports |

## Provenance and release gates

- **GOV-02 — Provenance inventory:** retain source/version/license records for
  dependencies, catalogs, images, and fixtures. The active MIT license does not
  relicense the legacy archive. Exclude that archive from distributable source
  bundles unless the rights and contents of every included file are cleared.
- Keep fictional-data labels in screens, files, and reports. A saved/shared plan
  must never appear to be a purchased or confirmed ticket.
- Preserve historical commits and describe actual work. A roadmap states intent;
  it does not establish authorship or external approval.
- Provide a local setup path, pinned dependencies, recovery instructions, and
  supported runtime/browser versions. Prepare permitted dependencies before an
  offline run; do not assume a fresh machine already has every package.
- Mark a feature delivered only when its acceptance behavior works, meaningful
  checks pass, and README, API, frontend, and verification docs agree. Record
  remaining limits and measurement failures alongside successes.

## Next contribution

Start with **M1: F01 and the F03 foundations**. Ship versioned trip contracts,
populated migration fixtures, durable trip creation/reopening, and an automated
browser journey as the first coherent slice. Retain the existing deterministic
chat/form experience throughout. Later features then build on an observable,
recoverable trip lifecycle.
