# Credential history cleanup — 20 November 2026

The published `master` history was rewritten after embedded credentials were
found in the original integration code and compiled Python files. The current
application remains independent of Goibibo and Facebook and requires no API keys.

## What changed

- Removed two historical Goibibo app IDs and their two app keys from file content
  across the full history. Historical source literals now contain
  `REMOVED_CREDENTIAL`; the current archived configuration reads environment
  variables instead.
- Removed a Facebook access token found in a compiled actions file that had
  already been deleted from the branch tip.
- Removed the three credential-bearing compiled files at all five historical
  paths, including their locations before and after the `legacy/` move.
- Preserved all 14 original commits and their noncredential file changes. Thirteen
  commits received new IDs. A follow-up documentation commit records this cleanup.
- Pruned the old objects and reflogs from the maintained local checkout.

The rewrite used `git-filter-repo` 2.47.0 in sensitive-data-removal mode. The full
mirror included the sole published branch, no tags, and the historical pull-request
reference. The cleaned branch was published with an explicit force-with-lease
check against its previous tip to avoid overwriting concurrent work.

## Verification

All 14 original commit trees were compared with their expected sanitized trees.
Before this documentation update, the branch tip's file tree was identical to
the previously tested version. All 455 stored Git objects in the cleaned mirror,
including binary blobs and commit metadata, were scanned for the five removed
values and common provider-token, private-key, and credential-URL patterns. No
matches remained. The removed compiled paths were absent from every commit.

This is a check for the identified values and the patterns used, not a guarantee
that every possible credential format can be detected.

## Copies outside the rewritten branch

GitHub retains the read-only reference for historical pull request #1. That
reference was cleaned in the local mirror, but repository owners cannot overwrite
it on GitHub. Thirteen public forks were also checked; their default branches
still contained the exposed Goibibo values at the time of this cleanup. Those
forks belong to other accounts and were not modified.

Rewriting this branch cannot erase third-party clones, forks, or GitHub's cached
views of old commits. Revoke or rotate every exposed credential that is still
valid. Fork owners need to clean their copies; GitHub Support controls retained
pull-request references and server-side cached objects. Support eligibility is
subject to GitHub's policy, which generally prioritizes credential rotation.
See [GitHub's sensitive-data removal guidance](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository).

## Existing clones

Use a fresh clone for future work. Do not merge, pull together, or push the old
and rewritten histories: that can restore the exposed commits.

If an old checkout contains uncommitted work or unpublished commits, preserve
those changes separately, inspect them for credentials and compiled files, then
apply only the needed changes to a fresh clone. Check the resulting changes
before committing. Do not copy the old `.git` directory or its backup refs into
the fresh clone. Remove the old checkout when its needed work has been recovered.
