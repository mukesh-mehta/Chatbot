# License and provenance boundaries

The new active implementation (`chatbot/`, `web/`, root launcher, tests, scripts,
documentation, and deployment/configuration files) is original project code under
the root MIT license.

Everything moved into `legacy/` retains its pre-existing provenance and notices.
The previous repository embedded modified Rasa NLU/dialogue-manager code,
Pymessenger, emoji, Goibibo utilities, a date parser, and related artifacts without
a complete repository-level license inventory. This update preserves that material
and does not assert ownership or apply a new license to it. In particular, embedded
notices such as the one in `legacy/emoji/__init__.py` remain intact.

The credential cleanup described in [the archive notice](legacy/ARCHIVE.md)
removes embedded authentication material and compiled copies without changing
the license or ownership of the remaining historical code.

Do not infer the license of a modified historical file solely from a current
upstream project's license. Resolve its exact source/version and required notices
before moving it into the active runtime. The licensing/provenance backlog is
tracked as **GOV-02** in the roadmap.

Installed Flask, Waitress, timezone data, test tools, and formatting tools retain
their own licenses. They are installed from pinned package requirements rather
than copied into this repository.
