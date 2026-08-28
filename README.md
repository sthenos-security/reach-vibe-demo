# REACHABLE Vibe Demo

**Three AI coding agents. One identical brief. 20, 8 and 5 security findings.**

Same specification, same day, same scanner. Codex, Claude Code and Cursor each
wrote the application, and each wrote a different number of vulnerabilities into
it. REACHABLE found them, handed them back to the agent that wrote them, and
verified the fixes.

| Agent | Findings put in scope | Evidence |
| --- | --- | --- |
| Codex | **20** | [status](https://sthenos-security.github.io/reach-vibe-demo/codex/) |
| Claude Code | **8** | [status](https://sthenos-security.github.io/reach-vibe-demo/claude/) |
| Cursor | **5** | [status](https://sthenos-security.github.io/reach-vibe-demo/cursor/) |

**[Open the demo hub →](https://sthenos-security.github.io/reach-vibe-demo/)**

Every page links the generated code before remediation, the exact prompt, the
fixed code, and a side-by-side diff. Nothing is summarised that you cannot open.

## Why This Matters

Agent-generated code ships vulnerabilities, and that is now measured rather than
argued. [SusVibes](https://leililab.github.io/susvibes-leaderboard/#blog), a
benchmark from Lei Li Lab at Carnegie Mellon, puts frontier models and agent
frameworks against 186 real-world, repository-level tasks and scores whether
what they produce is secure as well as working.

The spread above is the operational consequence. **Which agent writes your code
determines how much risk you ship**, and you cannot know that in advance from a
model's reputation or a benchmark average.

REACHABLE closes that gap before production: it proves which issues are actually
reachable by an attacker, drives the agent that wrote the code to fix them, and
rescans to confirm. Finding the same issues after deployment costs more and pulls
people back in.

## Read This Honestly

**These runs are not reproducible, and we publish them anyway.** Generation is
non-deterministic. Run the same lane twice and the agent writes a different
application, so the findings change with it. Treat 20 / 8 / 5 as one sample, not
a score — the next run will move it, and a vendor showing you stable numbers for
generated code is showing you a best-of.

That instability is the argument. A benchmark average cannot tell you what is in
*your* repository this week. Only scanning what the agent actually wrote, every
time it writes it, can.

## Run It Yourself

Open **Actions**, pick a pipeline, click **Run workflow**:

- **Run Codex Demo** · **Run Claude Demo** · **Run Cursor Demo**

Use `full-demo` for the complete story: generate, scan, remediate, rescan,
publish. Use `refresh-pages` to rebuild these pages from a previous run.

Some LLM vendors restrict automated code generation for security-themed prompts.
Sthenos is approved as a cybersecurity user; where a vendor still blocks an
agent, the demo reports that separately from a REACHABLE scan or remediation
failure, so a vendor refusal is never presented as a product result.

## Contact

Website: https://sthenosec.com

Questions: info@sthenosec.com
