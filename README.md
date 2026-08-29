# REACHABLE Vibe Demo

**The same brief, given to three AI coding agents, produces three different
applications with three different sets of security flaws.**

Codex, Claude Code and Cursor each received an identical specification. Each
wrote a working application. Each wrote a different number of vulnerabilities
into it. REACHABLE found them, handed them back to the agent that wrote them,
and rescanned to prove what was actually fixed.

**[See what each agent produced →](https://sthenos-security.github.io/reach-vibe-demo/)**

Per-agent results:
**[Codex](https://sthenos-security.github.io/reach-vibe-demo/codex/)** ·
**[Claude Code](https://sthenos-security.github.io/reach-vibe-demo/claude/)** ·
**[Cursor](https://sthenos-security.github.io/reach-vibe-demo/cursor/)**

The hub carries the live finding count per agent. Every page links the generated
code before remediation, the exact prompt, the fixed code, and a side-by-side
diff. Nothing is summarised that you cannot open and check.

## Deterministic Code vs. Vibe Code

| Security dimension | Traditional secure coding | AI vibe coding |
| --- | --- | --- |
| **Code replication** | Identical every time. A security audit stays valid across deployments. | Changes every run. A new generation needs a new review. |
| **Vulnerability tracing** | Flaws are static and caught by standard SAST. | Flaws drift. The model may introduce or silently patch them between runs. |
| **Risk management** | Predictable. Patches apply to specific lines. | Unpredictable. Regenerating a feature to fix one bug can introduce three more. |

Traditional software pins its dependencies so builds are reproducible and their
security posture is knowable. Vibe coding replaces that with a natural-language
layer that pins nothing. **You cannot guarantee the security posture of one
generation from the last.**

Three ways that bites:

- **Different agents, different flaws.** The same prompt — *"write a Node.js
  login API"* — gets modern hashing from one model and a deprecated module or an
  injection flaw from another.
- **Hidden drift on retries.** Same agent, same day, click regenerate: a script
  that was clean the first time can come back with XSS or an IDOR.
- **No pinned dependency to fall back on.** There is no version number that makes
  the next generation behave like the last one.

This is measured, not asserted.
[SusVibes](https://leililab.github.io/susvibes-leaderboard/#blog), a benchmark
from Lei Li Lab at Carnegie Mellon, puts frontier models and agent frameworks
against 186 real-world, repository-level tasks and scores whether the code they
produce is secure as well as functional.

## Read The Numbers As One Sample

**These runs are not reproducible, and we publish them anyway.** Run a lane twice
and the agent writes a different application, so the findings change with it. A
vendor showing you stable figures for generated code is showing you a best-of.

Which is the point. A benchmark average cannot tell you what is in *your*
repository this week — only scanning what your agent just wrote can.

## Contact

Website: https://sthenosec.com

Questions: info@sthenosec.com
