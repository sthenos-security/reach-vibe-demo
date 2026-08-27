from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_DIR = ROOT / ".github" / "workflows"
README = ROOT / "README.md"
SECURITY_DOC = ROOT / "docs" / "SECURITY-ARCHITECTURE.md"

EXPECTED_WORKFLOWS = {
    "run-codex-demo.yml": ("Run Codex Demo", "codex"),
    "run-claude-demo.yml": ("Run Claude Demo", "claude"),
    "run-cursor-demo.yml": ("Run Cursor Demo", "cursor"),
}

#: The publisher is deliberately NOT an agent dispatcher, and holding it to the
#: dispatcher contract would fail for the reasons it exists: it takes no secret,
#: dispatches nothing, and checks this repo out because its whole job is to run a
#: copier that lives here. Every test that walks "the workflows" means the three
#: dispatchers; the publisher has its own contract at the bottom of this file.
PUBLISH_WORKFLOW = "publish-public-demo.yml"
MIRROR_SCRIPT = ROOT / ".github" / "scripts" / "mirror_status_pages.py"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _without_comments(text: str) -> str:
    return "\n".join(
        line for line in text.splitlines() if not line.lstrip().startswith("#")
    )


def _workflow_paths() -> list[Path]:
    """The agent dispatchers, which are what the contract below is about."""
    return sorted(WORKFLOW_DIR / name for name in EXPECTED_WORKFLOWS)


def _canonical_workflow(filename: str, agent: str) -> str:
    display = {"codex": "Codex", "claude": "Claude", "cursor": "Cursor"}[agent]
    text = _text(WORKFLOW_DIR / filename)
    return text.replace(display, "Agent").replace(agent, "agent")


def test_public_repo_has_one_visible_pipeline_per_agent() -> None:
    workflows = {path.name for path in WORKFLOW_DIR.glob("*.yml")}

    assert workflows == set(EXPECTED_WORKFLOWS) | {PUBLISH_WORKFLOW}
    for filename, (display_name, agent) in EXPECTED_WORKFLOWS.items():
        text = _text(WORKFLOW_DIR / filename)
        assert f"name: {display_name}" in text
        assert f"agent: '{agent}'" in text
        assert f"group: dispatch-demo-{agent}" in text


def test_public_workflows_are_same_code_after_agent_constants() -> None:
    canonical = {
        filename: _canonical_workflow(filename, agent)
        for filename, (_display_name, agent) in EXPECTED_WORKFLOWS.items()
    }

    assert canonical["run-claude-demo.yml"] == canonical["run-codex-demo.yml"]
    assert canonical["run-cursor-demo.yml"] == canonical["run-codex-demo.yml"]


def test_public_workflows_mirror_private_live_stages() -> None:
    for path in _workflow_paths():
        text = _text(path)

        assert "timeout-minutes: 60" in text
        assert "id: dispatch" in text
        assert "private_run_id" in text
        assert "const publicRunId = String(context.runId);" in text
        assert "dispatch_source_run: publicRunId" in text
        assert "(run.display_title || '').includes(`public ${publicRunId}`)" in text
        assert "Estimate tokens and time" in text
        assert "model tokens | 53,000-600,000 total" in text
        assert "input tokens | 28,000-370,000" in text
        assert "output tokens | 25,000-230,000" in text
        assert "60 minute hard cap" in text
        assert "wait_private_job" in text
        assert "surface_private_failure" in text
        assert "Collecting redacted private failure diagnostics" in text
        assert "Credit balance is too low" in text
        assert "token[- ]?budget" in text
        assert "safety measures" in text
        assert "Cyber Verification Program" in text
        assert "Private failure diagnostics" in text
        assert "1. the app the selected agent wrote" in text
        assert 'startswith("2. ")' in text
        assert 'startswith("3. ")' in text
        assert 'startswith("4. ")' in text
        assert "Waiting for rescan and publish." in text
        assert "Public status page:" in text


def test_public_workflows_dispatch_only_private_throwdown() -> None:
    for path in _workflow_paths():
        text = _text(path)

        assert "sthenos-security" in text
        assert "reach-vibe-throwdown" in text
        assert "workflow_id: 'demo-remediation.yml'" in text
        assert "createWorkflowDispatch" in text
        assert "reach-vibe-throwdown-public" not in text
        assert "demo-remediation-claude.yml" not in text
        assert "demo-remediation-cursor.yml" not in text


def test_public_workflows_use_demo_dispatch_environment() -> None:
    for path in _workflow_paths():
        text = _text(path)

        assert "environment: demo-dispatch" in text
        assert "secrets.REACH_DEMO_RUNNER_DISPATCH_TOKEN" in text
        assert "github-token: ${{ secrets.REACH_DEMO_RUNNER_DISPATCH_TOKEN }}" in text


def test_workflows_have_only_bounded_user_inputs() -> None:
    for path in _workflow_paths():
        text = _text(path)

        assert "options: [refresh-pages, full-demo]" in text
        assert "default: full-demo" in text
        assert "resume_from_run:" in text
        assert "/^[0-9]+$/.test(resumeFromRun)" in text
        assert "resume_from_run: resumeFromRun" in text
        assert "source: 'generated'" in text
        assert "scan_mode: 'real'" in text
        assert "agent_timeout_sec: '480'" in text
        assert "generate_timeout_sec: '1800'" in text
        assert "absolute_max_sec: '3000'" in text
        assert "pipeline_timeout_sec: '3600'" in text
        assert "'refresh-pages': 're-publish only (rebuild the pages from the last run)'" in text
        assert "'full-demo': 'everything (generate, scan, remediate, publish)'" in text

        forbidden_inputs = (
            "agent:",
            "prompt",
            "command",
            "workflow_name",
            "workflow_id:",
            "private_ref",
            "artifact",
            "scanner_flags",
        )
        workflow_inputs = text.split("permissions:", maxsplit=1)[0]
        for token in forbidden_inputs:
            assert token not in workflow_inputs


def test_public_workflows_do_not_run_agents_scanners_or_remediation() -> None:
    for path in _workflow_paths():
        executable = _without_comments(_text(path))
        forbidden = (
            "actions/checkout",
            "actions/cache",
            "reachctl",
            "codex ",
            "claude ",
            "cursor-agent",
            "OPENAI_API_KEY",
            "ANTHROPIC_API_KEY",
            "CURSOR_API_KEY",
            "CODEX_ACCESS_TOKEN",
            "reach-ci-github",
            "--context ci",
            "--context local",
            "--mode branch",
            "--mode inplace",
            "copilot",
            "createPullRequest",
            ".reachable",
            "repo.db",
            "reach_vibe_demo.runner",
        )
        for token in forbidden:
            assert token not in executable


def test_public_repo_uses_only_dispatch_token_secret() -> None:
    combined = "\n".join(_text(path) for path in _workflow_paths())

    assert "REACH_DEMO_RUNNER_DISPATCH_TOKEN" in combined
    assert "OPENAI_API_KEY" not in combined
    assert "ANTHROPIC_API_KEY" not in combined
    assert "CURSOR_API_KEY" not in combined
    assert "GITHUB_ENV" not in combined


def test_readme_is_vc_facing_and_avoids_security_plumbing() -> None:
    text = _text(README)

    assert "Run Codex Demo" in text
    assert "Run Claude Demo" in text
    assert "Run Cursor Demo" in text
    assert "REACH_DEMO_RUNNER_DISPATCH_TOKEN" not in text
    assert "demo-dispatch" not in text
    assert "vendor API keys" not in text
    assert "security boundary" not in text.lower()
    assert "info@sthenosec.com" in text


def test_security_doc_keeps_public_private_boundary() -> None:
    combined = "\n".join(_text(path) for path in _workflow_paths())
    security = _text(SECURITY_DOC)
    normalized_security = " ".join(security.split())

    assert "reach-vibe-throwdown-public" not in security
    assert "REACH_DEMO_RUNNER_DISPATCH_TOKEN" in security
    assert "vendor API keys" in normalized_security
    assert "does not run agents" in normalized_security
    assert "REACH_DEMO_RUNNER_DISPATCH_TOKEN" in combined


# --- the publisher -----------------------------------------------------------
#
# It copies four already-public pages onto this repository's Pages site. The
# properties worth pinning are the ones that keep it from becoming anything
# else: it must stay unauthenticated, it must be runnable by hand, and it must
# publish all four pages or fail.


def test_publisher_is_manual_and_runs_after_each_agent_pipeline() -> None:
    text = _text(WORKFLOW_DIR / PUBLISH_WORKFLOW)

    assert "name: Publish Public Demo" in text
    assert "workflow_dispatch:" in text
    assert "workflow_run:" in text
    for display_name, _agent in EXPECTED_WORKFLOWS.values():
        assert f'"{display_name}"' in text
    assert "types: [completed]" in text
    assert "group: publish-public-demo" in text
    assert "cancel-in-progress: false" in text


def test_publisher_holds_no_secret_and_dispatches_nothing() -> None:
    text = _text(WORKFLOW_DIR / PUBLISH_WORKFLOW)
    executable = _without_comments(text)

    assert "secrets." not in executable
    assert "REACH_DEMO_RUNNER_DISPATCH_TOKEN" not in text
    assert "createWorkflowDispatch" not in executable
    assert "demo-remediation.yml" not in executable
    # Reads the public site over HTTPS; never the private repository's API.
    assert "https://sthenos-security.github.io/reach-vibe-throwdown" in text
    assert "gh run view" not in executable
    assert "api.github.com" not in executable


def test_publisher_publishes_four_pages_or_fails() -> None:
    text = _text(WORKFLOW_DIR / PUBLISH_WORKFLOW)

    assert "mirror_status_pages.py" in text
    assert 'wc -l | tr -d \' \'" = "4"' in text or '= "4"' in text
    assert "actions/upload-pages-artifact" in text
    assert "actions/deploy-pages" in text
    assert "pages: write" in text
    assert "id-token: write" in text


def test_copier_keeps_the_four_pages_local_and_the_rest_on_the_source() -> None:
    import sys

    sys.path.insert(0, str(MIRROR_SCRIPT.parent))
    import mirror_status_pages as copier

    source = "https://example.test/throwdown"
    pages = copier.page_map(source)
    assert set(pages.values()) == {
        "index.html", "codex/index.html", "claude/index.html", "cursor/index.html",
    }

    # `./` on a lane page is that lane's own root -- the before-scan page -- and
    # `../` is the hub. Both are pages we copy, so both stay inside this site.
    html = (
        '<body><a href="./">initial scan</a> <a href="../">hub</a> '
        '<a href="./fixed.html">fixed</a> '
        '<a href="./evidence/code-diff-viewer.html">diff</a> '
        '<a href="https://github.com/sthenos-security/reach-vibe-throwdown/actions/runs/42">'
        'this pipeline run</a></body>'
    )
    out = copier.rewrite(
        html,
        page_url="https://example.test/throwdown/codex/",
        local_path="codex/index.html",
        source=source,
        pages=pages,
        fetched_at="2026-08-27 00:00 UTC",
    )

    # Both copied pages stay inside this site: the lane's own root and the hub.
    assert 'href="index.html"' in out
    assert 'href="../index.html"' in out
    # The evidence pages are not copied, so they resolve on the source site.
    assert 'href="https://example.test/throwdown/codex/fixed.html"' in out
    assert 'href="https://example.test/throwdown/codex/evidence/code-diff-viewer.html"' in out
    # The private run link is gone; the run id it carried is not.
    assert "actions/runs/42" not in out
    assert "this pipeline run" in out
    assert "private run 42" in out
    assert "Copied from" in out
