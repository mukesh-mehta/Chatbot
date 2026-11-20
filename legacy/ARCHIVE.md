# Historical implementation — not the supported runtime

The original tracked files were initially moved here without changing their
contents. This includes the original README, requirements and Conda environment,
modified Rasa libraries, Messenger/Goibibo integrations, date utilities, IDE files,
datasets, and serialized models.

## Credential cleanup — 20 November 2026

Embedded Goibibo credentials were removed from the source configuration and both
tracked compiled configuration copies. One compiled copy contained a different
older key. The source now reads `GOIBIBO_APP_ID` and `GOIBIBO_APP_KEY` from the
environment, defaulting to empty values.

The Facebook entry-point placeholders and unfinished actions token assignment
now use `FACEBOOK_VERIFY_TOKEN`, `FACEBOOK_APP_SECRET`, `FACEBOOK_PAGE_ID`, and
`FACEBOOK_PAGE_ACCESS_TOKEN` environment settings. No credentials are required by
the maintained application, and these changes do not make the archive runnable
or supported. Do not commit credentials or regenerate tracked bytecode files.

The initial cleanup changed the current files only. A subsequent history rewrite
on the same date removed the exposed values from the published branch's earlier
commits as well. That scan also found a Facebook access token in an already
deleted compiled actions file. See [the history cleanup record](../docs/HISTORY_CLEANUP.md)
for verification, clone recovery instructions, and copies outside this branch.
Previously exposed keys must still be revoked or rotated if valid.

## Compatibility and provenance

These files target an obsolete environment and are **not Python 3.12 compatible**.
Some were incomplete even in the previous checkout. Do not install this directory's
requirements, execute its entry points, expose its webhook code, or load its model
artifacts as part of the modern app.

The maintained entry point is `../run.py`. The archive is excluded from modern
tests, formatting, containers, and imports. For migration decisions and what has
not been carried forward, read [the migration guide](../docs/MIGRATION.md).

Third-party notices and original terms remain applicable. The new implementation's
MIT license does not relicense this historical material. Provenance review is a
prerequisite before reusing archived third-party code in future development.
