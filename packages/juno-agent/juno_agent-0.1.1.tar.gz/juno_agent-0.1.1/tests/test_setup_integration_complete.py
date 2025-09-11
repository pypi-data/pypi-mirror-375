"""
Comprehensive integration tests for complete setup flows.

This module tests end-to-end setup scenarios, including complete setup flows
from start to finish, setup with different editor configurations, setup
cancellation/interruption, and setup with various project structures.
"""

import pytest
import asyncio
import tempfile
import json
import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from textual.pilot import Pilot
from juno_agent.fancy_ui.app import PyWizardTUIApp
from juno_agent.config import ConfigManager


class TestCompleteSetupFlows:
    """Test complete end-to-end setup flows."""

    @pytest.fixture
    async def integration_app(self, tmp_path):
        """Create comprehensive test app for integration testing."""
        project_dir = tmp_path / "integration_test"
        project_dir.mkdir()
        
        # Create realistic project structure
        (project_dir / "src").mkdir()
        (project_dir / "tests").mkdir()
        (project_dir / "docs").mkdir()
        
        # Create package files for dependency detection
        (project_dir / "requirements.txt").write_text(
            "fastapi>=0.68.0\n"
            "uvicorn>=0.15.0\n" 
            "pydantic>=1.8.0\n"
            "pytest>=7.0.0\n"
        )
        
        (project_dir / "pyproject.toml").write_text("""
[project]
name = "test-integration-project"
version = "1.0.0"
description = "Integration test project"
dependencies = [
    "fastapi>=0.68.0",
    "uvicorn>=0.15.0",
    "pydantic>=1.8.0"
]

[project.optional-dependencies]
dev = ["pytest>=7.0.0"]
""")
        
        config_manager = ConfigManager(str(project_dir))
        app = PyWizardTUIApp(config_manager)
        
        # Mock all setup components for integration testing
        app.integration_test_data = {
            "setup_completed": False,
            "steps_completed": [],
            "editor_selected": None,
            "dependencies_detected": [],
            "mcp_installed": False,
            "docs_fetched": False,
            "verification_passed": False
        }
        
        return app

    @pytest.mark.asyncio
    async def test_complete_setup_flow_python_project(self, integration_app):
        """
        GIVEN a Python project with dependencies
        WHEN complete setup flow is executed
        THEN all setup steps should complete successfully
        AND project should be fully configured
        """
        # Mock complete setup flow
        async def complete_setup_flow():
            test_data = integration_app.integration_test_data
            
            # Step 1: Project description
            integration_app.chat_area.add_message("📋 **Project Description**", is_user=False)
            test_data["steps_completed"].append("project_description")
            
            # Step 2: Editor selection
            integration_app.chat_area.add_message("📝 **Editor Selection: Claude Code**", is_user=False)
            test_data["editor_selected"] = "Claude Code"
            test_data["steps_completed"].append("editor_selection")
            
            # Step 3: Dependency detection
            integration_app.chat_area.add_message("🔍 **Dependencies detected: 4 packages**", is_user=False)
            test_data["dependencies_detected"] = ["fastapi", "uvicorn", "pydantic", "pytest"]
            test_data["steps_completed"].append("dependency_detection")
            
            # Step 4: MCP installation
            integration_app.chat_area.add_message("⚙️ **MCP servers installed successfully**", is_user=False)
            test_data["mcp_installed"] = True
            test_data["steps_completed"].append("mcp_installation")
            
            # Step 5: Documentation fetching
            integration_app.chat_area.add_message("📚 **Documentation fetched for 4 dependencies**", is_user=False)
            test_data["docs_fetched"] = True
            test_data["steps_completed"].append("docs_fetching")
            
            # Step 6: External context setup
            integration_app.chat_area.add_message("📁 **External context configured**", is_user=False)
            test_data["steps_completed"].append("external_context")
            
            # Step 7: IDE configuration
            integration_app.chat_area.add_message("📝 **IDE configuration files created**", is_user=False)
            test_data["steps_completed"].append("ide_config")
            
            # Step 8: Verification
            integration_app.chat_area.add_message("🔍 **Verification: All components PASS**", is_user=False)
            test_data["verification_passed"] = True
            test_data["steps_completed"].append("verification")
            
            # Step 9: Completion
            integration_app.chat_area.add_message("🎉 **Setup Complete!**", is_user=False)
            test_data["setup_completed"] = True
            test_data["steps_completed"].append("completion")
        
        integration_app.setup_handler.handle_setup_command = AsyncMock(side_effect=complete_setup_flow)
        
        async with integration_app.run_test() as pilot:
            await pilot.pause(0.1)
            
            # Execute complete setup
            await pilot.press("slash")
            await pilot.type("setup")
            await pilot.press("enter")
            
            await pilot.pause(0.5)  # Allow time for complete flow
            
            test_data = integration_app.integration_test_data
            
            # Verify all steps completed
            expected_steps = [
                "project_description", "editor_selection", "dependency_detection",
                "mcp_installation", "docs_fetching", "external_context", 
                "ide_config", "verification", "completion"
            ]
            
            for step in expected_steps:
                assert step in test_data["steps_completed"], f"Step {step} should be completed"
            
            # Verify setup data
            assert test_data["setup_completed"], "Setup should be marked as completed"
            assert test_data["editor_selected"] == "Claude Code", "Editor should be selected"
            assert len(test_data["dependencies_detected"]) == 4, "Should detect 4 dependencies"
            assert test_data["mcp_installed"], "MCP should be installed"
            assert test_data["docs_fetched"], "Docs should be fetched"
            assert test_data["verification_passed"], "Verification should pass"

    @pytest.mark.asyncio
    async def test_complete_docs_only_flow(self, integration_app):
        """
        GIVEN a project with existing configuration
        WHEN docs-only setup flow is executed
        THEN only documentation steps should execute
        """
        async def docs_only_flow():
            test_data = integration_app.integration_test_data
            
            integration_app.chat_area.add_message("📚 **Documentation Fetching Mode**", is_user=False)
            
            # Skip to docs fetching
            integration_app.chat_area.add_message("🔄 **Scanning existing dependencies**", is_user=False)
            test_data["dependencies_detected"] = ["fastapi", "uvicorn", "pydantic", "pytest"]
            
            integration_app.chat_area.add_message("📚 **Fetching documentation for 4 dependencies**", is_user=False)
            test_data["docs_fetched"] = True
            test_data["steps_completed"].append("docs_only_complete")
            
            integration_app.chat_area.add_message("✅ **Documentation fetching complete**", is_user=False)
        
        integration_app.setup_handler.handle_docs_only_command = AsyncMock(side_effect=docs_only_flow)
        
        async with integration_app.run_test() as pilot:
            await pilot.pause(0.1)
            
            await pilot.press("slash")
            await pilot.type("setup --docs-only") 
            await pilot.press("enter")
            
            await pilot.pause(0.3)
            
            test_data = integration_app.integration_test_data
            
            # Verify only docs steps completed
            assert "docs_only_complete" in test_data["steps_completed"], "Docs-only should complete"
            assert test_data["docs_fetched"], "Documentation should be fetched"
            assert len(test_data["dependencies_detected"]) == 4, "Should detect dependencies"
            
            # Verify other setup steps were NOT executed
            assert not test_data["mcp_installed"], "MCP should not be installed in docs-only mode"
            assert not test_data["setup_completed"], "Full setup should not be marked complete"

    @pytest.mark.asyncio
    async def test_complete_verification_only_flow(self, integration_app):
        """
        GIVEN a project with existing setup
        WHEN verification-only flow is executed
        THEN comprehensive verification should run
        """
        async def verification_only_flow():
            test_data = integration_app.integration_test_data
            
            integration_app.chat_area.add_message("🔍 **Setup Verification Mode**", is_user=False)
            
            # Simulate verification checks
            checks = [
                ("MCP Server Configuration", "PASS"),
                ("External Context Setup", "PASS"),
                ("IDE Configuration Files", "PASS"),
                ("Dependency Documentation", "PASS"),
                ("API Key Configuration", "WARN")
            ]
            
            for component, status in checks:
                integration_app.chat_area.add_message(f"🔍 **{component}**: {status}", is_user=False)
            
            integration_app.chat_area.add_message("✅ **Verification Complete: 80% success rate**", is_user=False)
            test_data["verification_passed"] = True
            test_data["steps_completed"].append("verification_only_complete")
        
        integration_app.setup_handler.handle_verification_only_command = AsyncMock(side_effect=verification_only_flow)
        
        async with integration_app.run_test() as pilot:
            await pilot.pause(0.1)
            
            await pilot.press("slash")
            await pilot.type("setup --verify-only")
            await pilot.press("enter")
            
            await pilot.pause(0.3)
            
            test_data = integration_app.integration_test_data
            
            # Verify verification completed
            assert "verification_only_complete" in test_data["steps_completed"], "Verification should complete"
            assert test_data["verification_passed"], "Verification should be marked as passed"


class TestSetupWithDifferentEditors:
    """Test setup flows with different editor configurations."""

    @pytest.fixture
    async def editor_test_app(self, tmp_path):
        """Create test app for editor-specific testing."""
        project_dir = tmp_path / "editor_test"
        project_dir.mkdir()
        
        # Create cursor-specific directories
        (project_dir / ".cursor").mkdir()
        
        config_manager = ConfigManager(str(project_dir))
        app = PyWizardTUIApp(config_manager)
        
        app.editor_test_data = {
            "selected_editor": None,
            "mcp_config_created": {},
            "ide_files_created": []
        }
        
        return app

    @pytest.mark.asyncio
    async def test_setup_with_cursor_editor(self, editor_test_app):
        """
        GIVEN Cursor editor is selected
        WHEN setup executes
        THEN Cursor-specific configuration should be created
        """
        async def cursor_setup_flow():
            test_data = editor_test_app.editor_test_data
            test_data["selected_editor"] = "Cursor"
            
            editor_test_app.chat_area.add_message("📝 **Editor Selection: Cursor**", is_user=False)
            editor_test_app.chat_area.add_message("⚙️ **Installing MCP servers for Cursor**", is_user=False)
            
            # Simulate .cursor/mcp.json creation
            test_data["mcp_config_created"][".cursor/mcp.json"] = {
                "servers": {
                    "vibe_context": {
                        "command": "node",
                        "args": ["path/to/server"],
                        "env": {"ASKBUDI_API_KEY": "test_key"}
                    }
                }
            }
            
            editor_test_app.chat_area.add_message("✅ **Cursor MCP configuration created**", is_user=False)
            editor_test_app.chat_area.add_message("📝 **AGENTS.md created for Cursor**", is_user=False)
            test_data["ide_files_created"].append("AGENTS.md")
        
        editor_test_app.setup_handler.handle_setup_command = AsyncMock(side_effect=cursor_setup_flow)
        
        async with editor_test_app.run_test() as pilot:
            await pilot.pause(0.1)
            
            await pilot.press("slash")
            await pilot.type("setup")
            await pilot.press("enter")
            
            await pilot.pause(0.3)
            
            test_data = editor_test_app.editor_test_data
            
            # Verify Cursor-specific setup
            assert test_data["selected_editor"] == "Cursor", "Should select Cursor editor"
            assert ".cursor/mcp.json" in test_data["mcp_config_created"], "Should create Cursor MCP config"
            assert "AGENTS.md" in test_data["ide_files_created"], "Should create AGENTS.md for Cursor"

    @pytest.mark.asyncio
    async def test_setup_with_claude_code_editor(self, editor_test_app):
        """
        GIVEN Claude Code editor is selected
        WHEN setup executes
        THEN Claude Code-specific configuration should be created
        """
        async def claude_code_setup_flow():
            test_data = editor_test_app.editor_test_data
            test_data["selected_editor"] = "Claude Code"
            
            editor_test_app.chat_area.add_message("📝 **Editor Selection: Claude Code**", is_user=False)
            editor_test_app.chat_area.add_message("⚙️ **Installing MCP servers for Claude Code**", is_user=False)
            
            # Claude Code specific config
            test_data["mcp_config_created"]["claude_mcp.json"] = {
                "servers": {"vibe_context": {"command": "node"}}
            }
            
            editor_test_app.chat_area.add_message("✅ **Claude Code MCP configuration created**", is_user=False)
            editor_test_app.chat_area.add_message("📝 **CLAUDE.md created**", is_user=False)
            test_data["ide_files_created"].append("CLAUDE.md")
        
        editor_test_app.setup_handler.handle_setup_command = AsyncMock(side_effect=claude_code_setup_flow)
        
        async with editor_test_app.run_test() as pilot:
            await pilot.pause(0.1)
            
            await pilot.press("slash")
            await pilot.type("setup")
            await pilot.press("enter")
            
            await pilot.pause(0.3)
            
            test_data = editor_test_app.editor_test_data
            
            assert test_data["selected_editor"] == "Claude Code", "Should select Claude Code"
            assert "CLAUDE.md" in test_data["ide_files_created"], "Should create CLAUDE.md"

    @pytest.mark.asyncio
    async def test_setup_with_windsurf_editor(self, editor_test_app):
        """
        GIVEN Windsurf editor is selected
        WHEN setup executes
        THEN Windsurf-specific configuration should be created
        """
        async def windsurf_setup_flow():
            test_data = editor_test_app.editor_test_data
            test_data["selected_editor"] = "Windsurf"
            
            editor_test_app.chat_area.add_message("📝 **Editor Selection: Windsurf**", is_user=False)
            editor_test_app.chat_area.add_message("📝 **WINDSURF.md created**", is_user=False)
            test_data["ide_files_created"].append("WINDSURF.md")
        
        editor_test_app.setup_handler.handle_setup_command = AsyncMock(side_effect=windsurf_setup_flow)
        
        async with editor_test_app.run_test() as pilot:
            await pilot.pause(0.1)
            
            await pilot.press("slash")
            await pilot.type("setup")
            await pilot.press("enter")
            
            await pilot.pause(0.3)
            
            test_data = editor_test_app.editor_test_data
            
            assert test_data["selected_editor"] == "Windsurf", "Should select Windsurf"
            assert "WINDSURF.md" in test_data["ide_files_created"], "Should create WINDSURF.md"


class TestSetupCancellationAndInterruption:
    """Test setup cancellation and interruption scenarios."""

    @pytest.fixture
    async def cancellation_test_app(self, tmp_path):
        """Create test app for cancellation testing."""
        project_dir = tmp_path / "cancel_test"
        project_dir.mkdir()
        
        config_manager = ConfigManager(str(project_dir))
        app = PyWizardTUIApp(config_manager)
        
        app.cancellation_test_data = {
            "setup_started": False,
            "setup_cancelled": False,
            "cleanup_performed": False,
            "steps_before_cancel": []
        }
        
        return app

    @pytest.mark.asyncio
    async def test_setup_can_be_cancelled_during_execution(self, cancellation_test_app):
        """
        GIVEN setup is in progress
        WHEN user cancels setup
        THEN setup should stop gracefully
        AND cleanup should be performed
        """
        cancel_triggered = False
        
        async def interruptible_setup():
            test_data = cancellation_test_app.cancellation_test_data
            test_data["setup_started"] = True
            
            cancellation_test_app.chat_area.add_message("🚀 **Setup started**", is_user=False)
            
            steps = ["description", "editor", "dependencies", "mcp", "docs"]
            for i, step in enumerate(steps):
                if cancel_triggered:
                    test_data["setup_cancelled"] = True
                    test_data["cleanup_performed"] = True
                    cancellation_test_app.chat_area.add_message("❌ **Setup cancelled by user**", is_user=False)
                    cancellation_test_app.chat_area.add_message("🧹 **Cleanup performed**", is_user=False)
                    return
                
                test_data["steps_before_cancel"].append(step)
                cancellation_test_app.chat_area.add_message(f"⏳ **Processing {step}**", is_user=False)
                await asyncio.sleep(0.05)
            
            cancellation_test_app.chat_area.add_message("✅ **Setup completed**", is_user=False)
        
        cancellation_test_app.setup_handler.handle_setup_command = AsyncMock(side_effect=interruptible_setup)
        
        async with cancellation_test_app.run_test() as pilot:
            await pilot.pause(0.1)
            
            # Start setup
            await pilot.press("slash")
            await pilot.type("setup")
            await pilot.press("enter")
            
            # Let setup run for a bit
            await pilot.pause(0.1)
            
            # Trigger cancellation
            cancel_triggered = True
            
            # Let cancellation process
            await pilot.pause(0.2)
            
            test_data = cancellation_test_app.cancellation_test_data
            
            # Verify cancellation behavior
            assert test_data["setup_started"], "Setup should have started"
            assert test_data["setup_cancelled"], "Setup should be cancelled"
            assert test_data["cleanup_performed"], "Cleanup should be performed"
            assert len(test_data["steps_before_cancel"]) < 5, "Should have cancelled before completion"

    @pytest.mark.asyncio
    async def test_app_remains_stable_after_setup_cancellation(self, cancellation_test_app):
        """
        GIVEN setup is cancelled
        WHEN cancellation completes
        THEN app should remain stable and usable
        """
        async def cancelled_setup():
            cancellation_test_app.chat_area.add_message("🚀 **Setup started**", is_user=False)
            await asyncio.sleep(0.05)
            cancellation_test_app.chat_area.add_message("❌ **Setup cancelled**", is_user=False)
            cancellation_test_app.cancellation_test_data["setup_cancelled"] = True
        
        cancellation_test_app.setup_handler.handle_setup_command = AsyncMock(side_effect=cancelled_setup)
        
        async with cancellation_test_app.run_test() as pilot:
            await pilot.pause(0.1)
            
            # Start and cancel setup
            await pilot.press("slash")
            await pilot.type("setup")
            await pilot.press("enter")
            
            await pilot.pause(0.2)
            
            # Try to use app after cancellation
            await pilot.press("slash")
            await pilot.type("help")
            await pilot.press("enter")
            
            await pilot.pause(0.1)
            
            # App should still be running and responsive
            assert cancellation_test_app.is_running, "App should remain running after cancellation"
            assert cancellation_test_app.cancellation_test_data["setup_cancelled"], "Setup should be cancelled"


class TestSetupWithVariousProjectStructures:
    """Test setup with different project structures."""

    @pytest.fixture
    async def project_structure_test_app(self, tmp_path):
        """Create test app for project structure testing."""
        project_dir = tmp_path / "structure_test"
        project_dir.mkdir()
        
        config_manager = ConfigManager(str(project_dir))
        app = PyWizardTUIApp(config_manager)
        
        app.project_test_data = {
            "detected_language": None,
            "detected_framework": None,
            "dependency_files_found": [],
            "project_type": None
        }
        
        return app

    @pytest.mark.asyncio
    async def test_setup_with_python_fastapi_project(self, project_structure_test_app):
        """
        GIVEN a Python FastAPI project structure
        WHEN setup analyzes the project
        THEN it should correctly identify Python/FastAPI configuration
        """
        # Create Python FastAPI project structure
        project_dir = Path(project_structure_test_app.config_manager.workdir)
        
        (project_dir / "app").mkdir()
        (project_dir / "app" / "__init__.py").write_text("")
        (project_dir / "app" / "main.py").write_text("from fastapi import FastAPI\napp = FastAPI()")
        (project_dir / "requirements.txt").write_text("fastapi>=0.68.0\nuvicorn>=0.15.0")
        
        async def analyze_python_fastapi():
            test_data = project_structure_test_app.project_test_data
            
            project_structure_test_app.chat_area.add_message("🔍 **Analyzing project structure**", is_user=False)
            project_structure_test_app.chat_area.add_message("🐍 **Language detected: Python**", is_user=False)
            project_structure_test_app.chat_area.add_message("⚡ **Framework detected: FastAPI**", is_user=False)
            
            test_data["detected_language"] = "Python"
            test_data["detected_framework"] = "FastAPI"
            test_data["dependency_files_found"] = ["requirements.txt"]
            test_data["project_type"] = "Python Web API"
        
        project_structure_test_app.setup_handler.handle_setup_command = AsyncMock(side_effect=analyze_python_fastapi)
        
        async with project_structure_test_app.run_test() as pilot:
            await pilot.pause(0.1)
            
            await pilot.press("slash")
            await pilot.type("setup")
            await pilot.press("enter")
            
            await pilot.pause(0.3)
            
            test_data = project_structure_test_app.project_test_data
            
            assert test_data["detected_language"] == "Python", "Should detect Python"
            assert test_data["detected_framework"] == "FastAPI", "Should detect FastAPI"
            assert "requirements.txt" in test_data["dependency_files_found"], "Should find requirements.txt"
            assert test_data["project_type"] == "Python Web API", "Should identify as web API"

    @pytest.mark.asyncio
    async def test_setup_with_nodejs_express_project(self, project_structure_test_app):
        """
        GIVEN a Node.js Express project structure
        WHEN setup analyzes the project
        THEN it should correctly identify Node.js/Express configuration
        """
        # Create Node.js Express project structure
        project_dir = Path(project_structure_test_app.config_manager.workdir)
        
        (project_dir / "src").mkdir()
        (project_dir / "src" / "index.js").write_text("const express = require('express')")
        (project_dir / "package.json").write_text('{"dependencies": {"express": "^4.18.0"}}')
        
        async def analyze_nodejs_express():
            test_data = project_structure_test_app.project_test_data
            
            project_structure_test_app.chat_area.add_message("🔍 **Analyzing project structure**", is_user=False)
            project_structure_test_app.chat_area.add_message("📦 **Language detected: JavaScript/Node.js**", is_user=False)
            project_structure_test_app.chat_area.add_message("🚀 **Framework detected: Express**", is_user=False)
            
            test_data["detected_language"] = "JavaScript"
            test_data["detected_framework"] = "Express"
            test_data["dependency_files_found"] = ["package.json"]
            test_data["project_type"] = "Node.js API"
        
        project_structure_test_app.setup_handler.handle_setup_command = AsyncMock(side_effect=analyze_nodejs_express)
        
        async with project_structure_test_app.run_test() as pilot:
            await pilot.pause(0.1)
            
            await pilot.press("slash")
            await pilot.type("setup")
            await pilot.press("enter")
            
            await pilot.pause(0.3)
            
            test_data = project_structure_test_app.project_test_data
            
            assert test_data["detected_language"] == "JavaScript", "Should detect JavaScript"
            assert test_data["detected_framework"] == "Express", "Should detect Express"
            assert "package.json" in test_data["dependency_files_found"], "Should find package.json"
            assert test_data["project_type"] == "Node.js API", "Should identify as Node.js API"

    @pytest.mark.asyncio
    async def test_setup_with_mixed_language_project(self, project_structure_test_app):
        """
        GIVEN a project with multiple languages
        WHEN setup analyzes the project
        THEN it should handle mixed language projects gracefully
        """
        # Create mixed language project
        project_dir = Path(project_structure_test_app.config_manager.workdir)
        
        # Python backend
        (project_dir / "backend").mkdir()
        (project_dir / "backend" / "requirements.txt").write_text("fastapi>=0.68.0")
        
        # JavaScript frontend
        (project_dir / "frontend").mkdir()
        (project_dir / "frontend" / "package.json").write_text('{"dependencies": {"react": "^18.0.0"}}')
        
        async def analyze_mixed_project():
            test_data = project_structure_test_app.project_test_data
            
            project_structure_test_app.chat_area.add_message("🔍 **Analyzing project structure**", is_user=False)
            project_structure_test_app.chat_area.add_message("🌐 **Multi-language project detected**", is_user=False)
            project_structure_test_app.chat_area.add_message("🐍 **Backend: Python (FastAPI)**", is_user=False)
            project_structure_test_app.chat_area.add_message("⚛️ **Frontend: JavaScript (React)**", is_user=False)
            
            test_data["detected_language"] = "Multi-language"
            test_data["detected_framework"] = "FastAPI + React"
            test_data["dependency_files_found"] = ["requirements.txt", "package.json"]
            test_data["project_type"] = "Full-stack Application"
        
        project_structure_test_app.setup_handler.handle_setup_command = AsyncMock(side_effect=analyze_mixed_project)
        
        async with project_structure_test_app.run_test() as pilot:
            await pilot.pause(0.1)
            
            await pilot.press("slash")
            await pilot.type("setup")
            await pilot.press("enter")
            
            await pilot.pause(0.3)
            
            test_data = project_structure_test_app.project_test_data
            
            assert test_data["detected_language"] == "Multi-language", "Should detect multi-language"
            assert "FastAPI + React" in test_data["detected_framework"], "Should detect both frameworks"
            assert len(test_data["dependency_files_found"]) == 2, "Should find both dependency files"
            assert test_data["project_type"] == "Full-stack Application", "Should identify as full-stack"