# Changelog

Notable changes to the split-stack toolkit. The book is a fixed reference; this repo is
live code and evolves to keep serving it. Corrections to the printed book live in
`ERRATA.md`; this file tracks changes to the code and layout here.

Format loosely follows [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Added
- `chapters/02-route-a-task/roster.py`: the worked-estimate stub Chapter 2 builds
  alongside `route.py`. Prints the output-cost-vs-Fable column and prices one fixed
  50K-token job on every seat, straight from the rate table (`python3 roster.py`).
- `ERRATA.md`: corrections to the printed edition and notes for reconciling the book
  with the current repo (compact demo app, reader-input CLIs, the Chapter 12 clone path).

### Fixed
- `chapters/08-review/needs-senior.sh` no longer prints `SHIP ON GATE` when its
  changed-files list is absent. A missing list now reports the error and exits non-zero,
  so it can't be read as a false all-clear on the review gate.

### Changed
- `GOTCHAS.md`: the "`.model` is null" entry now points to `ERRATA.md` for the appendix
  correction instead of stating it inline.

## [1.0.0] — 2026-07-14

Initial public release.

- One folder per chapter (`02-route-a-task` through `12-portable-team`), each with its
  exercise, the one command to run, and a success condition.
- `install.sh` puts the `/architect` skill and the pinned executor sub-agent into
  `~/.claude/`, so the router works in every project.
- `demo/invoicing-api`: a real application that compiles, boots, and passes 11 tests with
  every seeded bug still inside it, unlabelled. Answer key in `SPOILERS.md`.
- Reader-input tools: `estimate.py`, `route.py`, `fallback.py`, `ledger.py`,
  `contract-lint.js`, and the shell gates. Each takes your own input rather than replaying
  canned numbers.
- `Makefile` (`make test`, `make lint`), structural mermaid diagrams, and CI.
