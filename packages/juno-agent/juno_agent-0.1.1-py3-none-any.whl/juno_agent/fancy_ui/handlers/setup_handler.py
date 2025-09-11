"""
Unified SetupHandler: thin wrappers around the shared setup pipeline and verifier.
"""

import asyncio
from pathlib import Path


class SetupHandler:
    def __init__(self, app, config_manager, chat_area, storage_manager=None):
        self.app = app
        self.config_manager = config_manager
        self.chat_area = chat_area
        self.storage_manager = storage_manager
        self.debug_log = config_manager.create_debug_logger(debug=True)
        self.setup_active = False

    async def auto_start_setup_wizard(self) -> None:
        await self.handle_setup_command()

    async def auto_start_verification_only(self) -> None:
        await self.handle_verification_only_command()

    async def auto_start_agentic_resolver(self) -> None:
        await self.handle_setup_command()

    async def handle_agentic_resolver_command(self) -> None:
        self.chat_area.add_message(
            "ℹ️ Agentic resolver is part of the unified setup pipeline. Running /setup...",
            is_user=False,
        )
        await self.handle_setup_command()

    async def handle_setup_command(self) -> None:
        self.chat_area.add_message(
            "**🚀 Unified Setup Pipeline**\n\nRunning the same setup process as headless (with UI).\n\n"
            "Progress Checklist (will remain visible):\n"
            "- [ ] Scan project\n"
            "- [ ] External context init\n"
            "- [ ] Agentic docs fetch\n"
            "- [ ] Generate JUNO.md + IDE docs\n"
            "- [ ] MCP install\n"
            "- [ ] Persist config\n"
            "- [ ] Verify\n\n",
            is_user=False,
        )
        try:
            from ...setup.pipeline import run_setup_pipeline
            workdir = Path(self.config_manager.workdir)
            cfg = self.config_manager.load_config()
            # Determine editor for pipeline: prefer configured; else detect; else default
            editor_display = cfg.editor or ""
            if not editor_display:
                try:
                    from ..setup.setup_verification_service import SetupVerificationService
                    svc = SetupVerificationService(str(workdir), workdir.name)
                    detected_editor = svc._get_selected_editor()
                    if detected_editor:
                        editor_display = detected_editor
                except Exception:
                    editor_display = ""
            if not editor_display:
                editor_display = "Cursor" if (workdir / ".cursor").exists() else "Claude Code"
            textual_cb = (
                self.app.app_lifecycle_handler.ui_tool_update_callback
                if hasattr(self.app, 'app_lifecycle_handler') else None
            )
            result = await asyncio.to_thread(
                run_setup_pipeline,
                workdir,
                self.config_manager,
                editor_display,
                self.debug_log,
                None,
                textual_cb,
            )
            completed = (
                "**✅ Setup Completed**\n\n"
                "- [x] Scan project\n"
                "- [x] External context init\n"
                "- [x] Agentic docs fetch\n"
                "- [x] Generate JUNO.md + IDE docs\n"
                "- [x] MCP install\n"
                "- [x] Persist config\n"
                "- [x] Verify\n\n"
            )
            summary = (
                f"**Verification Summary**\n"
                f"PASS: {result['pass']}  FAIL: {result['fail']}  WARN: {result['warn']}  INFO: {result['info']}\n"
            )
            self.chat_area.add_message(completed + summary, is_user=False)
        except Exception as e:
            import traceback
            self.chat_area.add_message(f"❌ Pipeline error: {e}", is_user=False)
            self.debug_log.error(f"pipeline_error: {e}")
            self.debug_log.error(traceback.format_exc())

    async def handle_verification_only_command(self) -> None:
        msg = (
            "**🔍 Setup Verification Mode**\n\n"
            "Running comprehensive verification of your current setup...\n\n"
            "This will check:\n"
            "- MCP server configuration\n"
            "- External context setup\n"
            "- IDE configuration files\n"
            "- Dependency documentation\n"
            "- API key configuration\n"
            "- File permissions\n"
            "- Project analysis accuracy\n\n"
            "*Running verification now...*\n"
        )
        self.chat_area.add_message(msg, is_user=False)
        try:
            from ...setup import VerifyAgent
            workdir = Path(self.config_manager.workdir)
            result = await asyncio.to_thread(
                lambda: asyncio.run(
                    VerifyAgent(workdir, project_name=workdir.name, logger=self.debug_log).run(skip_external_calls=False)
                )
            )
            pass_count = sum(1 for r in result.results if r.status == "PASS")
            fail_count = sum(1 for r in result.results if r.status == "FAIL")
            warn_count = sum(1 for r in result.results if r.status == "WARN")
            info_count = sum(1 for r in result.results if r.status == "INFO")
            summary = (
                f"**Verification Summary**\n"
                f"PASS: {pass_count}  FAIL: {fail_count}  WARN: {warn_count}  INFO: {info_count}\n\n"
                f"{result.report}"
            )
            self.chat_area.add_message(summary, is_user=False)
        except Exception as e:
            import traceback
            self.chat_area.add_message(
                f"**❌ Verification Failed**\n\nError: {e}\n\nPlease check your setup and try again.",
                is_user=False,
            )
            self.debug_log.error(f"verify_only_error: {e}")
            self.debug_log.error(traceback.format_exc())

    # Deprecated legacy hooks (no-ops for compatibility)
    async def initialize_setup_components(self) -> None:
        self.debug_log.debug("initialize_setup_components skipped (pipeline handles setup)")

    async def start_enhanced_setup_step(self) -> None:
        self.chat_area.add_message("ℹ️ Unified pipeline is active; legacy steps skipped.", is_user=False)

    def dependency_progress_callback(self, message: str, data: dict) -> None:
        return
