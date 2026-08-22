# Local Agent Runner Implementation Plan

Status: implementation contract. Do not code outside this plan without updating
this file first.

## Goal

Build a simple, tested demo flow where the public repo is only a front door and
the private throwdown repo runs the real local-agent demo.

The product claim being preserved is:

> An AI coding agent writes vulnerable code. REACHABLE scans it, hands the same
> local agent a remediation task, rescans the result, and publishes DB-backed
> evidence.

## Non-Negotiable Boundary

Public repo:

- accepts only bounded choices;
- dispatches private workflow runs;
- stores no vendor API keys;
- runs no scanner;
- runs no coding agent;
- contains no remediation logic.

Private `reach-vibe-throwdown` repo:

- owns local runner/toolkit code;
- owns agent install/auth;
- owns `reachctl scan`;
- owns `reachctl remediate --context local --mode inplace`;
- owns scan DB and remediation DB state;
- owns evidence/page build;
- owns publish.

## Forbidden Runtime Paths

The implementation must not use:

- `uses: sthenos-security/reach-ci-github/...`;
- `--context ci`;
- `--mode branch`;
- Copilot dispatch;
- GitHub hosted remediation;
- remediation PR creation;
- `CODEX_ACCESS_TOKEN`;
- per-agent workflow forks;
- per-agent duplicated shell logic.

`reach-ci-github` is reference code only. Its proven mechanics may be copied
into private throwdown code, but it must not be a runtime dependency.

## Existing Code To Reuse

Reuse before writing new code.

Private throwdown:

- `src/throwdown/agent_lane.py`
  - agent registry;
  - `codex`, `claude`, `cursor` mapping;
  - install/auth;
  - token/model preflight;
  - generation invocation;
  - local remediation invocation.

- `.github/scripts/install_reachable.sh`
  - the only REACHABLE installer in the private runner.

- `.github/scripts/demo-state.sh`
  - pack/unpack/require state across jobs;
  - carries workspace, `.git`, scan DB, remediation DB.

- `.github/scripts/stage-paths.py`
  - safe staging filter.

- `.github/scripts/check_workspace_quality.py`
  - generated-workspace quality evidence.

- `.github/scripts/create_file_viewer.py`
  - before/after source viewer.

- `.github/scripts/create_code_diff_viewer.py`
  - side-by-side diff viewer.

- `.github/scripts/collect_evidence.py`
  - publish prompt, logs, scans, audit, source snippets.

- `.github/scripts/build_fixed_page.py`
  - fixed/remediation page from DB evidence.

- `.github/scripts/publish_lane.py`
  - lane publish to `gh-pages`.

Reference repos:

- `reach-ci-github/scripts/remediation-core.sh`
  - copy the loop shape, timeout handling, max-batch guard, rescan discipline,
    and safe staging idea only.

- `reach-ci-github/scripts/run-agent.sh`
  - copy the thin local-agent runner idea only.

- `reach-testbed-github-go/.github/workflows/reachable-remediate.yml`
  - copy the tiny workflow wrapper shape only.

## Agent Contract

The only allowed per-agent differences live in `src/throwdown/agent_lane.py`.

| Agent | Credential | CLI | `reachctl` remediation id |
|---|---|---|---|
| `codex` | `OPENAI_API_KEY` | `codex` | `codex` |
| `claude` | `ANTHROPIC_API_KEY` | `claude` | `claude_code` |
| `cursor` | `CURSOR_API_KEY` | `cursor-agent` | `cursor` |

Everything else is shared:

- same workflow;
- same workspace pattern;
- same state pack/unpack;
- same scan command;
- same actionable export;
- same remediation sizing;
- same local remediation command shape;
- same rescan;
- same page build;
- same publish/failure status.

## Validated Implementation Shape

Do not add a new runtime controller for the current fix.

The private repo already has the correct architectural center:

- one runtime workflow: `.github/workflows/demo-remediation.yml`;
- one agent registry: `src/throwdown/agent_lane.py`;
- one local remediation invocation:
  `reachctl remediate ... --context local --mode inplace`;
- one DB-backed fixed page path using `--remediation-db`;
- one public dispatcher workflow in `reach-vibe-throwdown-public`.

The current problem is a half-finished migration, not absence of a runner. The
implementation must therefore be a targeted contract cleanup:

1. fix the private workflow permissions so lane publish can push `gh-pages`;
2. normalize every mutable workflow input in `plan` and consume only
   `needs.plan.outputs.*` in later jobs;
3. keep Cursor-specific setup in `agent_lane.py`, not in workflow branches;
4. add static contract tests that fail if the workflow drifts back into
   per-agent forks, PR remediation, CI remediation, or raw input consumption;
5. update README/runbook/layout docs that still describe the old three-workflow
   model.

A later simplification can move more shell into Python, but it must not happen
until the existing single-lane workflow is green. Shrinking YAML and proving the
demo are separate tasks.

## Stage Responsibilities

### `plan`

Inputs:

- `agent`;
- `run`;
- `source`;
- `scan_mode`;
- `agent_model`;
- `agent_timeout_sec`;
- `generate_timeout_sec`;
- `app_scale`;
- `deep_remediation`;
- `absolute_max_sec`;
- `max_batch_rules`;
- `resume_from_run`.

Behavior:

- validate every input;
- resolve agent through `agent_lane`;
- choose default model from the registry when empty;
- emit GitHub outputs for later jobs;
- estimate runtime/tokens;
- do not contact agent providers;
- do not run scanner.

### `generate`

Behavior:

- create workspace/evidence directories;
- if `scan_mode=nop`, write placeholder app and skip agent;
- if `source=prebuilt`, copy captured specimen and remove `fixture.json`;
- if `source=generated`:
  - install/auth selected local agent through `agent_lane`;
  - run `agent_lane check-token`;
  - materialize prompt from `examples/tasks.json`;
  - call `agent_lane run-generation`;
  - record model/prompt/log evidence;
- initialize git baseline;
- build before-code viewer;
- pack state with `demo-state.sh pack generate`.

### `scan-before`

Behavior:

- unpack generated state;
- install REACHABLE through `.github/scripts/install_reachable.sh`;
- run:

```bash
reachctl scan "$WORKSPACE" --ci --fail-on none \
  --branch main --commit "$BASE_SHA" \
  --sarif "$EVIDENCE/before.sarif"
```

- run:

```bash
reachctl validate "$WORKSPACE" --scope actionable --no-agent --json \
  --output-dir "$EVIDENCE/before"
```

- pack state with `demo-state.sh pack scan`.

### `remediate`

Behavior:

- unpack scan state;
- require scan DB with `demo-state.sh require scans`;
- install REACHABLE;
- install/auth selected local agent through `agent_lane`;
- run `agent_lane check-token`;
- read actionable count from:

```text
$EVIDENCE/before/signals-selected.json
```

- compute:
  - batch size;
  - passes needed;
  - passes affordable under absolute max;
  - wall-clock budget;
  - token estimate;
- write `remediation-budget.txt`;
- run local remediation through `agent_lane run-remediation`.

The underlying command must be equivalent to:

```bash
reachctl remediate "$WORKSPACE" \
  --context local \
  --mode inplace \
  --scan-mode deterministic \
  --agent "$remediation_id" \
  --profile balanced \
  --all \
  --batch-size "$batch_rules" \
  "$timeout_flag" "$agent_timeout_sec" \
  --max-iterations "$passes"
```

Allowed optional flag:

```bash
--deep-remediation
```

Only when requested and supported by the installed `reachctl`.

State rule:

- always pack remediation state before failing the job;
- a failed remediation must still publish a terminal status page.

### `scan-after`

Behavior:

- use the remediated workspace;
- stage agent changes through `stage-paths.py`;
- commit only staged safe paths;
- run final scan:

```bash
reachctl scan "$WORKSPACE" --ci --fail-on none \
  --branch main --commit "$HEAD_SHA" \
  --sarif "$EVIDENCE/after.sarif"
```

- run actionable validation to `$EVIDENCE/after`.

### `publish`

Behavior:

- unpack best available state;
- if state is missing or earlier stage failed before page build, write terminal
  lane status page;
- export per-finding audit with:

```bash
reachctl remediate "$WORKSPACE" --audit --json-output
```

- build proof/evidence pages using existing scripts;
- make `before.html` the lane root;
- publish only the selected lane directory using `publish_lane.py`;
- never leave a stale successful page visible after a failed run.

## Workflow Shape

Replace the private workflow with a thin wrapper:

```text
plan -> generate -> scan-before -> remediate -> scan-after/publish
```

The workflow may own only:

- checkout;
- Python setup;
- cosign setup;
- artifact upload/download;
- GitHub secrets mapping into step-scoped env;
- calling `python3 -m throwdown.demo_runner ...`;
- final job verdict.

The workflow must not contain long shell business logic.

## Tests To Add

Add:

```text
tests/test_demo_runner.py
```

Required assertions:

- `plan` resolves all three agents through the same code path;
- missing agent credential fails before install/generation/remediation;
- Codex uses `OPENAI_API_KEY` only;
- no runtime path uses `CODEX_ACCESS_TOKEN`;
- remediation command uses `--context local`;
- remediation command uses `--mode inplace`;
- remediation command never uses `--context ci`;
- remediation command never uses `--mode branch`;
- no Copilot string appears in workflow/runtime code;
- no `reach-ci-github` runtime dependency appears in workflow;
- batch sizing reads `signals-selected.json`;
- remediation failure still writes state/status before job failure;
- terminal publish page is produced when upstream state is missing.

Update:

```text
tests/test_demo_lane_workflow.py
```

Required assertions:

- exactly one private workflow exists;
- no `demo-remediation-claude.yml`;
- no `demo-remediation-cursor.yml`;
- workflow has one `agent` input;
- workflow calls `throwdown.demo_runner`;
- workflow does not call `throwdown.agent_lane` directly except through runner
  tests, if retained for bootstrap;
- workflow has no 100+ line inline remediation shell block;
- every job has a timeout;
- `publish` runs under `always()` and can publish failure status.

## Validation Gates

Before commit:

```bash
python3 -m pytest tests/test_demo_runner.py tests/test_agent_lane.py tests/test_demo_lane_workflow.py -q
python3 -m pytest -q
ruff check .
actionlint .github/workflows/demo-remediation.yml
git diff --check
```

Runtime rollout:

1. Run `scan_mode=nop`.
2. Run one real Codex pipeline.
3. Verify generated app, before scan, remediation state, after scan, and page.
4. Run Claude through the same workflow.
5. Run Cursor through the same workflow.

## Abort Conditions

Stop and report instead of guessing if:

- installed `reachctl` lacks required local remediation flags;
- `signals-selected.json` is missing or has a new schema;
- local remediation does not produce remediation DB state;
- page code cannot render from DB evidence;
- publish would overwrite a good lane with an empty page;
- tests show per-agent duplication returning to workflow YAML.
