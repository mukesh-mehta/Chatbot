# Historical implementation — not the supported runtime

The original tracked files have been moved here without changing their contents.
This includes the original README, requirements and Conda environment, modified
Rasa libraries, Messenger/Goibibo integrations, date utilities, IDE files, datasets,
and serialized models.

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
