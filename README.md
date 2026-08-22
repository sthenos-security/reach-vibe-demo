# REACHABLE Vibe Demo

AI coding agents are fast. They also generate security issues.

This demo shows the loop REACHABLE closes:

`generate -> scan -> discover -> triage -> remediate -> rescan -> repeat`

An agent writes an application. REACHABLE finds the reachable issues that matter,
asks the same agent to fix them, scans again, and publishes the evidence.

## Start Here

- Demo hub: https://sthenos-security.github.io/reach-vibe-throwdown/
- Codex status: https://sthenos-security.github.io/reach-vibe-throwdown/codex/
- Claude status: https://sthenos-security.github.io/reach-vibe-throwdown/claude/
- Cursor status: https://sthenos-security.github.io/reach-vibe-throwdown/cursor/

## Run A Demo

Open **Actions**, choose one pipeline, then click **Run workflow**:

- **Run Codex Demo**
- **Run Claude Demo**
- **Run Cursor Demo**

Use `full-demo` for the live story. Each run writes a generated app, scans it,
remediates it, verifies the result, and updates the status page.

Some LLM vendors restrict automated code generation for security-themed prompts.
Sthenos has been approved as a cybersecurity user. If a vendor still blocks an
agent, the demo surfaces that provider reason separately from REACHABLE scan or
remediation failures.

Use `refresh-pages` only when you want to rebuild the public pages from a prior
run.

## What To Show

Each status page should answer five questions:

1. What did the agent build?
2. What did REACHABLE find?
3. What did REACHABLE ask the agent to fix?
4. What changed in the code?
5. What did the final scan prove?

The point is not that AI always writes secure code. The point is that REACHABLE
secures generated code by proving which issues are exploitable and reachable by
an attacker, then driving the agent to remediate the risks that matter before
they reach build, runtime, or production. Fixing exploitable issues later in the
SDLC is slower, more painful, and usually pulls humans back into the loop.

Attackers chain sophisticated attacks. REACHABLE starts layered defense at code
generation, before exploitable paths become part of your deployed production app.

For small agentic development teams, SMBs, and focused vertical software
companies without a dedicated security team, this saves time and reduces the
need for late manual security work.

## Contact

Website: https://sthenosec.com

Questions: info@sthenosec.com
