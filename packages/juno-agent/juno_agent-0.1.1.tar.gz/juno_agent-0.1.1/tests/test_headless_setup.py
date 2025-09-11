import os
from pathlib import Path


def write_pyproject(tmpdir: Path):
    tmpdir.mkdir(parents=True, exist_ok=True)
    (tmpdir / "pyproject.toml").write_text(
        """
[project]
name = "demo-proj"
version = "0.1.0"
dependencies = [
  "requests>=2.0.0",
  "pydantic"
]
""".strip()
    )


def test_headless_generators_write_files(tmp_path):
    # Arrange
    from juno_agent.setup import (
        generate_and_write_agents_md,
        generate_and_write_juno_md,
    )
    from juno_agent.fancy_ui.setup.dependency_scanner import DependencyScanner

    write_pyproject(tmp_path)

    # Act
    scan = DependencyScanner(project_path=tmp_path).scan_project_dependencies()
    detected = {
        "project_type": scan.get("metadata", {}).get("project_type", "Unknown"),
        "language": scan.get("language", "Unknown"),
        "dependencies": scan.get("dependencies", []),
        "package_files": scan.get("package_files", []),
    }
    fetched_docs = {"saved_files": []}

    generate_and_write_juno_md(
        workdir=tmp_path,
        project_description="test project",
        selected_editor="Generic",
        ai_analysis="",
        detected_deps=detected,
        fetched_docs=fetched_docs,
    )

    generate_and_write_agents_md(
        workdir=tmp_path,
        ide_name="Generic",
        project_description="test project",
        ai_analysis="",
        detected_deps=detected,
        fetched_docs=fetched_docs,
    )

    # Assert
    assert (tmp_path / "JUNO.md").exists(), "JUNO.md should be written in headless mode"
    assert (tmp_path / "AGENTS.md").exists(), "AGENTS.md should be written in headless mode"


def test_verify_agent_smoke(tmp_path):
    # Minimal files to allow verification to run without crashing
    (tmp_path / "JUNO.md").write_text("# JUNO Development Guide\n\n## Project Overview\n...\n")
    (tmp_path / "AGENTS.md").write_text("# AGENTS.md\n")

    from juno_agent.setup import VerifyAgent
    import asyncio

    out = asyncio.get_event_loop().run_until_complete(
        VerifyAgent(tmp_path, tmp_path.name).run(skip_external_calls=True)
    )
    assert isinstance(out.results, list) and len(out.results) > 0
