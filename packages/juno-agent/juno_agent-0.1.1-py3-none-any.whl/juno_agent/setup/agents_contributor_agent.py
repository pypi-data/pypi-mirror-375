"""Generate AGENTS.md contributor guide via TinyAgent (with safe fallback)."""

from __future__ import annotations

import platform
from datetime import datetime
from pathlib import Path
from typing import Optional, Any


def _hydrate_prompt(template: str, workdir: Path) -> str:
    subs = {
        "${PLATFORM}": platform.system(),
        "${ARCHITECTURE}": platform.machine(),
        "${CURRENT_DATE}": datetime.now().strftime("%Y-%m-%d"),
        "${WORKING_DIRECTORY}": str(workdir),
        "${PROJECT_NAME}": workdir.name,
        "${SESSION_ID}": datetime.now().strftime("%Y%m%d_%H%M%S"),
    }
    hydrated = template
    for k, v in subs.items():
        hydrated = hydrated.replace(k, v)
    return hydrated


def _load_prompt(workdir: Path) -> Optional[str]:
    prompt_file = workdir / "py_wizard_cli" / "juno_agent" / "prompts" / "prompt_garden.yaml"
    if not prompt_file.exists():
        return None
    try:
        import yaml  # type: ignore
        data = yaml.safe_load(prompt_file.read_text(encoding="utf-8"))
        return data.get("prompts", {}).get("agents_contributor_guide", {}).get("prompt")
    except Exception:
        return None


def _fallback_contributor_guide(workdir: Path) -> str:
    # Minimal deterministic content if TinyAgent is unavailable
    project = workdir.name
    return f"""# Repository Guidelines

## Project Structure & Module Organization
- Root project: `{project}`; sources under `py_wizard_cli/`, tests under `py_wizard_cli/tests/`, assets under `frontend/`.

## Build, Test, and Development
- Install: `pip install -e .[dev]`
- Run TUI: `juno-agent`
- Tests: `pytest -q`

## Coding Style & Naming
- Python: Black (88 chars), Ruff, MyPy; snake_case for variables/functions, PascalCase for classes.

## Testing Guidelines
- Pytest; name tests `test_*.py`; keep tests near features under `py_wizard_cli/tests/`.

## Security & Configuration Tips
- Store API keys in `.env` (never commit). Load via `set -a && source .env && set +a`.
- MCP: Cursor uses `.cursor/mcp.json`; Claude Code via `claude mcp add` (local scope).
- External context is symlinked to `~/.ASKBUDI/<project>/external_context` (check permissions on macOS/Linux).

## Commit & PRs
- Write concise, imperative commits (e.g., "Add headless MCP install").
- PRs should include description, screenshots (if UI), and linked issues.
"""


def generate_contributor_guide(workdir: Path, logger: Optional[Any] = None) -> str:
    """Generate contributor guide text via TinyAgent; fallback on failure."""
    prompt_template = _load_prompt(Path.cwd()) or _load_prompt(workdir)
    if not prompt_template:
        return _fallback_contributor_guide(workdir)

    prompt = _hydrate_prompt(prompt_template, workdir)

    # Try TinyAgent
    try:
        from ..tiny_agent import TinyCodeAgent  # type: ignore
        agent = TinyCodeAgent()
        # Keep short; no tools required for pure text generation
        resp = agent.run_sync(prompt, max_turns=3)
        text = str(resp) if resp is not None else ""
        if logger:
            logger.info("agents_md_agent_done", used_agent=True, chars=len(text))
        if text.strip():
            return text
    except Exception as e:
        if logger:
            logger.warning(f"agents_md_agent_failed: {e}")

    # Fallback deterministic guide
    text = _fallback_contributor_guide(workdir)
    if logger:
        logger.info("agents_md_agent_done", used_agent=False, chars=len(text))
    return text
