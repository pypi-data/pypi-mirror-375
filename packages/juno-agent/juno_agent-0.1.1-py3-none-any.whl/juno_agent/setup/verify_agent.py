"""Setup verification agent wrapper.

Provides a UI-agnostic wrapper around the existing SetupVerificationService
to make verification callable from CLI or TUI without duplicating logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, List, Optional

from ..fancy_ui.setup.setup_verification_service import (
    SetupVerificationService,
    VerificationResult,
)


@dataclass
class VerificationOutput:
    results: List[VerificationResult]
    report: str
    ai_report: Optional[str]


class VerifyAgent:
    def __init__(self, project_root: Path, project_name: Optional[str] = None, logger: Optional[Any] = None) -> None:
        self.project_root = Path(project_root)
        self.project_name = project_name or self.project_root.name
        self.log = logger

    async def run(self, skip_external_calls: bool = False) -> VerificationOutput:
        if self.log:
            self.log.debug(
                "verify_agent_start",
                project_root=str(self.project_root),
                project_name=self.project_name,
                skip_external_calls=skip_external_calls,
            )

        svc = SetupVerificationService(str(self.project_root), self.project_name)
        results = svc.verify_all_components(skip_external_calls=skip_external_calls)
        report = svc.generate_summary_report(results)

        # AI verification analysis may be integrated by the caller if needed.
        ai_report = None

        if self.log:
            # Summarize counts for quick grep in logs
            counts = {"PASS": 0, "FAIL": 0, "WARN": 0, "INFO": 0}
            for r in results:
                counts[r.status] = counts.get(r.status, 0) + 1
            self.log.info("verify_agent_done", **counts)

        return VerificationOutput(results=results, report=report, ai_report=ai_report)

