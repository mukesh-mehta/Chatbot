# Contributing

Use Python 3.12 and an isolated environment. Install `requirements-dev.txt`, then
run the checks listed in the README. Node 18+ is only required for frontend work;
the interface itself has no build step. Changes to pinned requirements should
include successful clean-environment installation on the supported CI platforms.

Keep new code in the active application. Do not broadly reformat, execute, or
silently repair files under `legacy/`; propose a separate migration with provenance
review if historical behavior is required.

For a contribution, reference a roadmap ID and explain the user-visible behavior,
implementation boundaries, and meaningful validation. Test date boundaries,
request types, state changes, and provider failure paths when relevant. UI changes
need keyboard and narrow-screen checks as well as state-helper tests.

Never commit credentials, passport/payment information, customer conversations,
runtime environments, or downloaded datasets. Do not remove sample-data labeling
until a real provider is integrated, verified, and accurately represented.

Use focused `feat:`, `fix:`, `test:`, `docs:`, or `chore:` commits. Do not claim a
roadmap item is delivered until its acceptance criteria and dependencies are met.
