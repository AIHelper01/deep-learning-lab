# Legacy Chinese notebooks (read-only archive)

These are the repository's early Chinese notebooks for the natural language processing module
(pytorch route). They are archived because:

- their cell structure does not line up with the rebuilt course notebooks, so they cannot be aligned
  cell by cell;
- their dependencies do not match the locked course environment, so they cannot be reproduced here;
- some cells contain syntax errors or stale failure outputs that no longer match the code.

The notebooks themselves sit on the Chinese side only; the English course never had these early
versions, which is why this directory holds just this README. The current Chinese course lives in
`../../../../../03-sentiment-analysis/pytorch/notebooks/` and pairs one file per file with the English lessons
here (enforced by `scripts/check_parity.py`); the Migration status section of `../../../../../AGENTS.md` records
which side currently keys the other.

Archived files stay in the repository for reference only. They are not executed or validated.
Use `git log --follow <path>` to inspect their history.
