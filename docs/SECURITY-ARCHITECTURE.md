# Security Architecture

`reach-vibe-demo` is public by design. It is not the runner.

## Boundary

This public repository is only a bounded front door. It:

- accepts only bounded choices;
- dispatches a private workflow run in the runner that executes the real
  local-agent demo;
- stores no vendor API keys;
- runs no scanner;
- runs no coding agent;
- contains no local agent runner code, scanner logic, remediation logic, scan
  DBs, or remediation DBs.

The private runner owns agent auth, local CLI invocation patterns, REACHABLE
install, global cache handling, scan DBs, remediation DBs, evidence building,
and publish contracts. Its internal layout, CI invocation details, and the
full secret inventory are maintained privately and intentionally not
documented in this public repository. See the internal hardening record for
that detail if you have access.

## Secrets

The only secret this repository may use is
`REACH_DEMO_RUNNER_DISPATCH_TOKEN`. It is not a vendor key. It should be
scoped only to dispatch workflows in the private runner repository, with no
other permissions (no admin, no secrets access, no org access).

Vendor API keys (for any coding agent) are never present in this repository
and are held exclusively by the private runner.

## Workflow Rules

The public workflows are fixed per agent:

- `Run Codex Demo` dispatches `agent=codex`;
- `Run Claude Demo` dispatches `agent=claude`;
- `Run Cursor Demo` dispatches `agent=cursor`.

Each workflow may accept only:

- `run`: `refresh-pages` or `full-demo`;
- `resume_from_run`: empty, or a numeric private run ID for page refresh.

It must not accept shell commands, prompts, arbitrary workflow names, refs,
URLs, file paths, artifact names, scanner flags, or model settings.

This public dispatcher only ever triggers the private runner's standard
local-agent flow. It does not support, and must never be extended to support,
CI-hosted remediation handoff, Copilot dispatch, or remediation PR creation
from this repo.
