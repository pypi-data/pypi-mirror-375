import os
import pytest
from pathlib import Path


@pytest.mark.asyncio
async def test_tui_verify_only_starts_and_logs(tmp_path):
    # Use App.run_test() which returns a pilot context without importing textual.testing

    # Arrange workdir and chdir so app_run.log lands here
    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        from juno_agent.config import ConfigManager
        from juno_agent.fancy_ui.app import PyWizardTUIApp

        cfg = ConfigManager(tmp_path)

        app = PyWizardTUIApp(
            config_manager=cfg,
            auto_start_setup=False,
            verify_only_mode=True,  # trigger verification-only path via timer
            agentic_resolver_mode=False,
        )

        async with app.run_test() as pilot:  # type: ignore[attr-defined]
            # Allow timers/workers to run
            await pilot.pause(1.2)

        # Assert debug log contains verify-only marker
        log_path = Path(tmp_path) / "app_run.log"
        assert log_path.exists(), "app_run.log should be created by the app"
        content = log_path.read_text(encoding="utf-8")
        assert "Verify-only mode enabled" in content or "Setup Verification Mode" in content
    finally:
        os.chdir(cwd)


@pytest.mark.asyncio
async def test_tui_docs_only_timer_runs(tmp_path):
    # Use App.run_test() without importing textual.testing

    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        from juno_agent.config import ConfigManager
        from juno_agent.fancy_ui.app import PyWizardTUIApp

        cfg = ConfigManager(tmp_path)
        app = PyWizardTUIApp(
            config_manager=cfg,
            auto_start_setup=False,
            verify_only_mode=False,
            agentic_resolver_mode=True,  # trigger docs-only path via timer
        )
        async with app.run_test() as pilot:  # type: ignore[attr-defined]
            await pilot.pause(1.2)

        # Check that log notes the agentic resolver mode enabled
        log_path = Path(tmp_path) / "app_run.log"
        assert log_path.exists()
        content = log_path.read_text(encoding="utf-8")
        assert (
            "Agentic resolver mode enabled" in content
            or "resolver will use direct API mode" in content
            or "Auto-starting Agentic Dependency Resolver" in content
        )
    finally:
        os.chdir(cwd)
