# Security Architecture

`reach-vibe-demo` is public by design. It is not the runner.

## Architecture of record (do not change)

```
reach-vibe-demo (public)  ── REACH_DEMO_RUNNER_DISPATCH_TOKEN ──┐
                                                                ├──► reach-vibe-throwdown
reach-vibe-lab  (private) ── REACH_LAB_RUNNER_DISPATCH_TOKEN  ──┘         │
                                                                         ▼
                                                                   all vendor credentials
                                                                   OPENAI / ANTHROPIC / CURSOR
```

| Repo | Visibility | Role | REACHABLE build | Pages |
| --- | --- | --- | --- | --- |
| `reach-vibe-demo` | public | dispatcher only | posted **wheel** | `/<agent>/` (investor root) |
| `reach-vibe-lab` | private | dispatcher only | **latest source** (`main` by default) | `/lab/<agent>/` |
| `reach-vibe-throwdown` | private | engine + credentials | executes both clients | publishes both roots |

Credentials are held only in throwdown for security. Dispatchers hold at most a
cross-repo dispatch token — never vendor API keys.

## Two remediae CI paths (do not collapse)

| Path | Who runs the agent | Typical `reachctl remediate` shape | Used by |
| --- | --- | --- | --- |
| **A. Straight agent binaries** | Runner spawns `codex` / `claude` / `cursor-agent` | `--context local --mode inplace` + per-pass timeout + `--max-wall-clock-hours` | Demo/lab via throwdown |
| **B. Hosted coding-agent integration** | Hosted/async agent (e.g. GitHub Copilot); CI writes a bundle | `--context ci --mode branch --output-dir … --branch-name …` + handoff loop | `reach-ci-github` / Copilot testbeds — not this demo |

Do not pin `--profile` / `--all` / `--batch-size` / `--max-iterations` from CI.
Do not force path B's handoff loop onto path A, or path A's local spawn onto path B.

Lab pages use unique paths under `/lab/` so they never collide with demo status
pages at the site root. The public site mirrors throwdown **root** only, so
`/lab/` never reaches investors.

## Boundary

The private `reach-vibe-throwdown` repo is the secure runner and SDK boundary.
It owns agent auth, local CLI invocation patterns, REACHABLE install, global
cache handling, scan DBs, remediation DBs, evidence building, and publish
contracts.

This public repository is only a bounded front door. It must not contain vendor API
keys, local agent runner code, scanner logic, remediation logic, scan DBs, or
remediation DBs.
It does not run agents, scanners, or remediation.

The private lab (`reach-vibe-lab`) is the same kind of front door: dispatcher
only, no vendor keys. It may pass `reachable_source_ref` because it is private;
this public repo must not pass refs.

## Secrets

The only secret this repository may use is
`REACH_DEMO_RUNNER_DISPATCH_TOKEN`. It is not a vendor key. It should be scoped
only to dispatch workflows in `sthenos-security/reach-vibe-throwdown`.

Vendor secrets stay in private `reach-vibe-throwdown`:

- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `CURSOR_API_KEY`

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

This public dispatcher always starts **path A** (straight agent binaries) in
throwdown:

`reachctl remediate --context local --mode inplace`

It does not use path B (`--context ci` hosted coding-agent handoff).
