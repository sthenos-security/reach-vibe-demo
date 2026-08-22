from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "request-agent-demo.yml"
README = ROOT / "README.md"
SECURITY_DOC = ROOT / "docs" / "SECURITY-ARCHITECTURE.md"


def _text(path: Path = WORKFLOW) -> str:
    return path.read_text(encoding="utf-8")


def _without_comments(text: str) -> str:
    return "\n".join(
        line for line in text.splitlines() if not line.lstrip().startswith("#")
    )


def test_public_workflow_dispatches_only_private_throwdown() -> None:
    text = _text()

    workflows = list((ROOT / ".github" / "workflows").glob("*.yml"))
    assert workflows == [WORKFLOW]
    assert "const owner = 'sthenos-security';" in text
    assert "const repo = 'reach-vibe-throwdown';" in text
    assert "const workflow_id = 'demo-remediation.yml';" in text
    assert "createWorkflowDispatch" in text
    assert "reach-vibe-throwdown-public" not in text
    assert "demo-remediation-claude.yml" not in text
    assert "demo-remediation-cursor.yml" not in text


def test_public_workflow_uses_demo_dispatch_environment() -> None:
    text = _text()

    assert "environment: demo-dispatch" in text
    assert "group: dispatch-demo" in text
    assert "secrets.REACH_DEMO_RUNNER_DISPATCH_TOKEN" in text
    assert "github-token: ${{ secrets.REACH_DEMO_RUNNER_DISPATCH_TOKEN }}" in text


def test_workflow_has_only_bounded_user_inputs() -> None:
    text = _text()

    assert "options: [codex, claude, cursor]" in text
    assert "options: [refresh-pages, full-demo]" in text
    assert "resume_from_run:" in text
    assert "/^[0-9]+$/.test(resumeFromRun)" in text
    assert "resume_from_run: resumeFromRun" in text
    assert "'refresh-pages': 're-publish only (rebuild the pages from the last run)'" in text
    assert "'full-demo': 'everything (generate, scan, remediate, publish)'" in text
    assert "const allowedAgents = ['codex', 'claude', 'cursor'];" in text

    forbidden_inputs = (
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


def test_public_workflow_does_not_run_agents_scanners_or_remediation() -> None:
    executable = _without_comments(_text())
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
    text = _text()

    assert "REACH_DEMO_RUNNER_DISPATCH_TOKEN" in text
    assert "OPENAI_API_KEY" not in text
    assert "ANTHROPIC_API_KEY" not in text
    assert "CURSOR_API_KEY" not in text
    assert "GITHUB_ENV" not in text


def test_docs_state_the_public_security_boundary() -> None:
    combined = _text(README) + "\n" + _text(SECURITY_DOC)

    assert "reach-vibe-throwdown-public" not in combined
    assert "private `reach-vibe-throwdown`" in combined
    assert "REACH_DEMO_RUNNER_DISPATCH_TOKEN" in combined
    assert "vendor API keys" in combined
    assert "does not run agents" in combined
