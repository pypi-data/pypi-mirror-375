"""AGENTS.md generator utilities.

This module centralizes generation and writing of AGENTS.md so both the
CLI/TUI can reuse a single, testable implementation.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class AgentsMdInputs:
    workdir: Path
    ide_name: str
    project_description: str = ""
    ai_analysis: str = ""
    detected_deps: Dict[str, Any] = None
    fetched_docs: Dict[str, Any] = None


class AgentsMdGenerator:
    """Generate and write AGENTS.md content.

    A thin, UI-agnostic helper with optional logging injection.
    """

    def __init__(self, logger: Optional[Any] = None) -> None:
        # Logger is expected to support .debug/.info/.warning/.error
        self.log = logger

    def generate_content(self, inputs: AgentsMdInputs) -> str:
        workdir = Path(inputs.workdir)
        project_name = workdir.name
        project_desc = inputs.project_description or "No description provided"
        detected = inputs.detected_deps or {}
        fetched = inputs.fetched_docs or {}

        if self.log:
            self.log.debug(
                "agents_md_generate_content",
                workdir=str(workdir),
                ide=inputs.ide_name,
                deps=len(detected.get("dependencies", [])),
            )

        content_parts = []
        content_parts.append(f"# {inputs.ide_name} Configuration for {project_name}")
        content_parts.append("")
        content_parts.append("## Project Analysis")
        content_parts.append("High-level summary of the project and environment.")
        content_parts.append("")
        content_parts.append("## Project Information")
        content_parts.append(f"- **Project Type**: {detected.get('project_type', 'Unknown')}")
        content_parts.append(f"- **Primary Language**: {detected.get('language', 'Unknown')}")
        content_parts.append(
            f"- **Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        content_parts.append("")
        content_parts.append("## Project Description")
        content_parts.append(project_desc)
        content_parts.append("")
        content_parts.append("## Architecture & Dependencies")

        # Include initial insights from AI analysis (first few non-heading lines)
        if inputs.ai_analysis and len(inputs.ai_analysis) > 100:
            content_parts.append("### AI Analysis Insights")
            content_parts.append("The following key insights were identified during setup:\n")
            analysis_lines = inputs.ai_analysis.split("\n")[:10]
            for line in analysis_lines:
                line = line.strip()
                if line and not line.startswith("#"):
                    content_parts.append(f"- {line}")
            content_parts.append("")

        # Dependencies
        content_parts.append("### Key Dependencies")
        deps = detected.get("dependencies", [])
        if deps:
            for dep in deps[:10]:
                content_parts.append(f"- `{dep}`")
            if len(deps) > 10:
                content_parts.append(f"- ... and {len(deps) - 10} more dependencies")
        else:
            content_parts.append("- No dependencies detected")
        content_parts.append("")

        # External documentation
        content_parts.append("## External Context")
        content_parts.append(
            "Access up-to-date docs for dependencies in the `external_context/` directory:"
        )
        saved_files = fetched.get("saved_files", [])
        if saved_files:
            for file_info in saved_files:
                dep_name = file_info.get("dependency", "unknown")
                filename = file_info.get("filename", f"{dep_name}.md")
                content_parts.append(f"- **{dep_name}**: `external_context/{filename}`")
        else:
            content_parts.append("- No external documentation available")

        # MCP server guidance (if installed list exists from setup data)
        content_parts.append("")
        content_parts.append("## MCP Server")
        content_parts.append(
            "This project is configured with VibeContext MCP server for enhanced documentation access."
        )
        content_parts.append("")
        content_parts.append("### Available Tools:")
        content_parts.append(
            "- `file_structure`: Analyze large files efficiently with structural overview"
        )
        content_parts.append(
            "- `resolve_library_id`: Search for libraries by name to get correct library ID"
        )
        content_parts.append(
            "- `get_library_docs`: Get specific documentation for libraries using library ID and prompt"
        )
        content_parts.append(
            "- `fetch_doc_url`: Fetch and convert documentation from URLs to markdown"
        )
        content_parts.append("")
        content_parts.append("### Usage Guidelines:")
        content_parts.append(
            "1. Always use `resolve_library_id` first to find the correct library identifier"
        )
        content_parts.append(
            "2. Use `get_library_docs` with specific questions about the library"
        )
        content_parts.append("3. Prefer MCP server documentation over general knowledge for accuracy")
        content_parts.append(
            "4. Use `fetch_doc_url` for external documentation when needed"
        )
        content_parts.append(
            "5. Use `file_structure` when processing large text files or encountering token limits"
        )

        # Development guidelines
        content_parts.append("")
        content_parts.append("## Development Guidelines")
        content_parts.append("")
        content_parts.append("### Code Style & Standards")
        content_parts.append(
            f"- Follow {detected.get('language', 'language')}-specific best practices"
        )
        content_parts.append("- Use consistent naming conventions throughout the project")
        content_parts.append(
            "- Write clear, self-documenting code with appropriate comments"
        )
        content_parts.append(
            f"- Leverage {inputs.ide_name} AI features for intelligent assistance"
        )
        content_parts.append("")
        content_parts.append("### Testing & Quality")
        content_parts.append("- Write comprehensive tests for new features")
        content_parts.append("- Maintain high code quality standards")
        content_parts.append("- Run tests before committing changes")
        content_parts.append("- Use AI assistance for test generation and code review")
        content_parts.append("")
        content_parts.append("### Documentation")
        content_parts.append("- Keep documentation up-to-date with code changes")
        content_parts.append("- Use external_context/ for dependency documentation references")
        content_parts.append("- Document complex algorithms and business logic")
        content_parts.append(
            "- Maintain this configuration file as project evolves"
        )
        content_parts.append("")
        content_parts.append("### AI Assistant Guidelines")
        content_parts.append(
            "- Use project context from JUNO.md for comprehensive understanding"
        )
        content_parts.append("- Reference external documentation when available")
        content_parts.append("- Be specific in your questions to get better responses")
        content_parts.append("- Validate AI-generated code against project requirements")
        content_parts.append(
            f"- Leverage {inputs.ide_name}'s intelligent features for code completion and analysis"
        )
        content_parts.append("")
        content_parts.append("---")
        content_parts.append(
            f"*This file was generated automatically by juno-agent setup on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
        )
        content_parts.append(
            "*Update by running `juno setup` or `juno-agent setup` in this directory*"
        )

        return "\n".join(content_parts) + "\n"

    def write(self, inputs: AgentsMdInputs) -> Path:
        """Generate and write AGENTS.md to the project root.

        Returns the written file path.
        """
        content = self.generate_content(inputs)
        agents_md_path = Path(inputs.workdir) / "AGENTS.md"
        agents_md_path.write_text(content, encoding="utf-8")
        if self.log:
            self.log.info("agents_md_written", path=str(agents_md_path))
        return agents_md_path


def generate_and_write_agents_md(
    workdir: Path,
    ide_name: str,
    project_description: str,
    ai_analysis: str,
    detected_deps: Dict[str, Any],
    fetched_docs: Dict[str, Any],
    logger: Optional[Any] = None,
) -> Path:
    """Convenience function to generate and write AGENTS.md in one call."""
    gen = AgentsMdGenerator(logger=logger)
    return gen.write(
        AgentsMdInputs(
            workdir=Path(workdir),
            ide_name=ide_name,
            project_description=project_description,
            ai_analysis=ai_analysis,
            detected_deps=detected_deps or {},
            fetched_docs=fetched_docs or {},
        )
    )
