# Security Architecture

`reach-vibe-demo` is public by design. It is not the runner.

## Boundary

The private `reach-vibe-throwdown` repo is the secure runner and SDK boundary.
It owns agent auth, local CLI invocation patterns, REACHABLE install, global
cache handling, scan DBs, remediation DBs, evidence building, and publish
contracts.

This public repository is only a bounded front door. It must not contain vendor
API keys, local agent runner code, scanner logic, remediation logic, scan DBs, or
remediation DBs.

## Secrets

The only secret this repository may use is
`REACH_DEMO_RUNNER_DISPATCH_TOKEN`. It is not a vendor key. It should be scoped
only to dispatch workflows in `sthenos-security/reach-vibe-throwdown`.

Vendor secrets stay in private `reach-vibe-throwdown`:

- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `CURSOR_API_KEY`

## Workflow Rules

The public workflow may accept only:

- `agent`: `codex`, `claude`, or `cursor`;
- `run`: `refresh-pages` or `full-demo`.

It must not accept shell commands, prompts, arbitrary workflow names, refs,
URLs, file paths, artifact names, scanner flags, or model settings.

The private remediation path must be local and inplace:

`reachctl remediate --context local --mode inplace`
