# REACHABLE Vibe Demo

This is the public front door for the REACHABLE local-agent remediation demo.

The private `reach-vibe-throwdown` repo is the secure runner. It stores vendor
API keys, invokes local agent CLIs, runs REACHABLE scans/remediation, manages
global `.reachable` cache state, builds evidence, and publishes sanitized pages.

This public repo does not run agents, scanners, or remediation. It accepts a
bounded request and dispatches the private runner.

## What The Demo Shows

An AI coding agent writes vulnerable code. REACHABLE scans it, hands the same
local agent a remediation task, rescans the result, and publishes DB-backed
evidence.

Published pages:

- hub: https://sthenos-security.github.io/reach-vibe-throwdown/
- Codex: https://sthenos-security.github.io/reach-vibe-throwdown/codex/
- Claude: https://sthenos-security.github.io/reach-vibe-throwdown/claude/
- Cursor: https://sthenos-security.github.io/reach-vibe-throwdown/cursor/

Each private lane publishes the same evidence shape: status, before scan,
fixed/remediation status, summary JSON, generation prompt, code before, code
after, side-by-side diff, evidence index, and raw patch.

## Run Shape

The public GitHub Actions workflow is:

`.github/workflows/request-agent-demo.yml`

Inputs:

| Input | Choices |
|---|---|
| `agent` | `codex`, `claude`, `cursor` |
| `run` | `refresh-pages`, `full-demo` |
| `resume_from_run` | optional numeric private run ID for `refresh-pages` |

Use `full-demo` for the live VC path. Use `refresh-pages` with
`resume_from_run` when you only want to rebuild the public evidence pages from a
known successful private run.

The private runner owns the actual stage architecture:

`plan -> generate -> scan-before -> remediate -> scan-after -> publish`

Those private stages use one shared code path. The only intentional difference
from the working GitHub remediation reference is that the private runner invokes
local agent CLIs instead of GitHub agent/Copilot integration. Copilot is not
supported.

## Cache

The private runner stores global REACHABLE state in GitHub cache:

- `~/.reachable/venv`
- `~/.reachable/tools`
- `~/.reachable/cache`
- `~/.reachable/semgrep`
- `~/.reachable/release-attestations`
- `~/.reachable/scans`
- `~/.reachable/transient/vibe`

The scan DB and remediation DB are therefore part of the cached REACHABLE state,
not ephemeral per-step scratch.

## Setup

Create one environment secret in this public repo:

`REACH_DEMO_RUNNER_DISPATCH_TOKEN`

Store it under:

`Settings -> Environments -> demo-dispatch -> Environment secrets`

The token should be fine-grained and scoped to dispatch workflows in
`sthenos-security/reach-vibe-throwdown`. The private runner keeps
`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, and `CURSOR_API_KEY`.

## Boundary

This public repo:

- uses only `REACH_DEMO_RUNNER_DISPATCH_TOKEN`;
- does not store vendor API keys;
- does not run agents;
- does not run scanners;
- does not run remediation;
- has no `reach-ci-github` runtime dependency;
- does not use Copilot;
- creates no remediation PRs;
- never uses `--context ci`;
- never uses `--mode branch`;
- never uses `CODEX_ACCESS_TOKEN`.

See [docs/design/LOCAL-AGENT-RUNNER-IMPLEMENTATION.md](docs/design/LOCAL-AGENT-RUNNER-IMPLEMENTATION.md).
