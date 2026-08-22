# REACHABLE Vibe Demo

AI coding agents can move fast, but the code they generate is often insecure in
ways that matter in production.

This demo shows REACHABLE closing that loop: an agent generates an application,
REACHABLE finds the reachable security issues, and then REACHABLE asks the same
agent to remediate them. The result is rescanned and published with evidence.

## What To Show

Start here:

- Demo hub: https://sthenos-security.github.io/reach-vibe-throwdown/
- Codex status page: https://sthenos-security.github.io/reach-vibe-throwdown/codex/
- Claude status page: https://sthenos-security.github.io/reach-vibe-throwdown/claude/
- Cursor status page: https://sthenos-security.github.io/reach-vibe-throwdown/cursor/

Each status page shows the same story:

1. What the agent generated.
2. What REACHABLE found.
3. What REACHABLE asked the agent to fix.
4. What changed.
5. What the final scan proved.

The pages link to the before scan, fix result, before/after code, diff, and
evidence files.

## How The Demo Runs

This public repo is only the demo button. The private
`sthenos-security/reach-vibe-throwdown` repo runs the agents, scanners,
remediation, cache, and evidence publishing.

Use GitHub Actions:

1. Open **Actions**.
2. Choose **Request REACHABLE vibe demo**.
3. Pick `codex`, `claude`, or `cursor`.
4. Pick `full-demo`.
5. Run the workflow.

For a quick page rebuild, pick `refresh-pages` and provide the private runner
run ID in `resume_from_run`.

## Why It Matters

The important claim is not that every generated app is perfectly fixed. The
important claim is that REACHABLE identifies the issues that are actually
reachable, drives the developer's own AI agent to fix them, and publishes the
before/after evidence instead of asking a human to trust a black box.

## Boundary

The public repo does not store vendor API keys and does not run agents,
scanners, or remediation. It only uses `REACH_DEMO_RUNNER_DISPATCH_TOKEN` to
dispatch the private runner.

The private runner owns the AI credentials, REACHABLE cache, scan databases,
remediation databases, and published evidence.

## Contact

Questions: info@sthenosec.com
