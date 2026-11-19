# Contributing

Use Python 3.12 and an isolated environment. Install `requirements-dev.txt`, then
run the checks listed in the README. Node 18+ is only required for frontend work;
the interface itself has no build step. Changes to pinned requirements should
include successful clean-environment installation on the supported CI platforms.

Keep new code in the active application. Do not broadly reformat, execute, or
silently repair files under `legacy/`; propose a separate migration with provenance
review if historical behavior is required.

For a contribution, reference a roadmap feature ID (F01–F12) and explain the
user-visible behavior, implementation boundaries, and meaningful validation.
Follow the milestone dependencies. Test date boundaries, permissions, revisions,
retry identities, storage failures, and synthetic-provider errors when relevant.
UI changes need keyboard, narrow-screen, and real API/browser checks as well as
state-helper tests.

Keep the active roadmap runnable on one machine with Python, SQLite, and a browser
after dependency setup. Use local test identities and original synthetic fixtures.
No milestone may depend on a model, live supplier, cloud account, external message,
payment service, GPU, or Docker. Keep all frontend runtime assets local.

Never commit credentials, passport/payment information, customer conversations,
runtime environments, or downloaded datasets. Retain sample-data labeling in
screens, exchange files, and simulated change reports throughout this roadmap.

Use focused `feat:`, `fix:`, `test:`, `docs:`, or `chore:` commits. Do not claim a
roadmap item is delivered until its acceptance criteria and dependencies are met.
