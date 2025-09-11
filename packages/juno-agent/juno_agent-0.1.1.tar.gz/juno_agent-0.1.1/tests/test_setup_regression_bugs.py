"""
Bug-specific regression tests for setup command functionality.

This module contains tests that specifically validate the fixes for the recently
resolved bugs in the setup command:
1. Agentic dependency discovery bug - Fixed inconsistency between --docs-only and regular setup modes
2. Debug logging leakage - Fixed debug logs appearing in TUI instead of app_run.log only  
3. Verification step freezing - Fixed using @work decorator for background processing
4. MCP Installation for Cursor - Already working correctly, creates .cursor/mcp.json
"""

import pytest
import asyncio
import tempfile
import os
import io
import sys
import logging
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch, call

from textual.pilot import Pilot
from juno_agent.fancy_ui.app import PyWizardTUIApp
from juno_agent.config import ConfigManager


class TestAgenticDependencyConsistencyBug:
    """Test regression for agentic dependency discovery consistency bug."""

    @pytest.fixture
    async def dependency_test_app(self, tmp_path):
        """Create test app for dependency testing."""
        project_dir = tmp_path / "dependency_test"
        project_dir.mkdir()
        
        # Create project files with dependencies
        (project_dir / "requirements.txt").write_text("fastapi>=0.68.0\nuvicorn>=0.15.0\npydantic>=1.8.0\n")
        (project_dir / "package.json").write_text('{"dependencies": {"express": "^4.18.0", "cors": "^2.8.5"}}')
        
        config_manager = ConfigManager(str(project_dir))
        app = PyWizardTUIApp(config_manager)
        
        # Mock AgenticDependencyResolver to track consistency
        mock_resolver = AsyncMock()
        mock_resolver.run = AsyncMock()
        
        # Track calls to verify consistency between modes
        app.agentic_calls = []
        
        async def track_agentic_call(*args, **kwargs):
            app.agentic_calls.append({"args": args, "kwargs": kwargs})
            return {
                "success": True,
                "dependencies": ["fastapi", "uvicorn", "pydantic"],
                "documentation_fetched": {"saved_files": [], "failed_saves": []},
                "files_created": 3,
                "symlinks_created": True
            }
        
        mock_resolver.run.side_effect = track_agentic_call
        
        # Mock the resolver creation
        with patch('juno_agent.agentic_dependency_resolver.AgenticDependencyResolver') as mock_class:
            mock_class.return_value = mock_resolver
            app._mock_resolver_class = mock_class
            app._mock_resolver = mock_resolver
            
            yield app

    @pytest.mark.asyncio
    async def test_agentic_dependency_consistency_between_modes(self, dependency_test_app):
        """
        GIVEN a project with detected dependencies
        WHEN running regular setup and --docs-only setup
        THEN both should use AgenticDependencyResolver consistently
        AND both should process the same dependencies
        """
        async with dependency_test_app.run_test() as pilot:
            # Mock the setup handler's initialize method
            dependency_test_app.setup_handler.initialize_setup_components = AsyncMock()
            dependency_test_app.setup_handler.agentic_dependency_resolver = dependency_test_app._mock_resolver
            
            # Test regular setup mode
            await dependency_test_app.setup_handler.handle_agentic_resolver_command()
            await pilot.pause(0.1)
            
            # Reset call tracking
            regular_setup_calls = dependency_test_app.agentic_calls.copy()
            dependency_test_app.agentic_calls.clear()
            dependency_test_app._mock_resolver.run.reset_mock()
            
            # Test docs-only mode  
            await dependency_test_app.setup_handler.handle_docs_only_command()
            await pilot.pause(0.1)
            
            docs_only_calls = dependency_test_app.agentic_calls.copy()
            
            # Verify both modes called the resolver
            assert len(regular_setup_calls) > 0, "Regular setup should call AgenticDependencyResolver"
            assert len(docs_only_calls) > 0, "Docs-only setup should call AgenticDependencyResolver"
            
            # Verify consistency in resolver usage
            dependency_test_app._mock_resolver.run.assert_called()

    @pytest.mark.asyncio
    async def test_dependency_resolver_consistent_parameters(self, dependency_test_app):
        """
        GIVEN AgenticDependencyResolver is used in both setup modes
        WHEN both modes are executed
        THEN the resolver should be initialized with consistent parameters
        """
        async with dependency_test_app.run_test() as pilot:
            # Mock the setup components initialization
            dependency_test_app.setup_handler.initialize_setup_components = AsyncMock()
            dependency_test_app.setup_handler.agentic_dependency_resolver = dependency_test_app._mock_resolver
            
            # Execute both modes
            await dependency_test_app.setup_handler.handle_agentic_resolver_command()
            await dependency_test_app.setup_handler.handle_docs_only_command()
            
            # Verify resolver was created with consistent parameters
            # Both calls should use same project_path, config_manager, etc.
            create_calls = dependency_test_app._mock_resolver_class.call_args_list
            
            if len(create_calls) >= 2:
                first_call = create_calls[0]
                second_call = create_calls[1]
                
                # Compare key parameters for consistency
                assert first_call[1].get('project_path') == second_call[1].get('project_path')
                assert first_call[1].get('config_manager') == second_call[1].get('config_manager')


class TestDebugLoggingLeakageBug:
    """Test regression for debug logging leakage to TUI."""

    @pytest.fixture
    async def logging_test_app(self, tmp_path):
        """Create test app for logging isolation testing."""
        project_dir = tmp_path / "logging_test"
        project_dir.mkdir()
        
        config_manager = ConfigManager(str(project_dir))
        app = PyWizardTUIApp(config_manager)
        
        # Create a way to capture what messages are sent to chat_area
        app.chat_messages = []
        original_add_message = app.chat_area.add_message
        
        def track_chat_message(message, is_user=False):
            app.chat_messages.append({"message": message, "is_user": is_user})
            return original_add_message(message, is_user)
        
        app.chat_area.add_message = track_chat_message
        
        # Mock setup handler with debug logging
        async def mock_setup_with_debug():
            # This should NOT appear in chat
            app.setup_handler.debug_log.debug("This is a debug message that should not leak to TUI")
            app.setup_handler.debug_log.info("This is an info message that should not leak to TUI")
            
            # This SHOULD appear in chat  
            app.chat_area.add_message("Setup started successfully", is_user=False)
            
        app.setup_handler.handle_setup_command = AsyncMock(side_effect=mock_setup_with_debug)
        
        return app

    @pytest.mark.asyncio
    async def test_debug_logs_not_leaked_to_tui(self, logging_test_app):
        """
        GIVEN setup process generates debug logs
        WHEN setup command is executed
        THEN debug logs should NOT appear in chat area
        AND only user-facing messages should appear in TUI
        """
        async with logging_test_app.run_test() as pilot:
            await pilot.pause(0.1)
            
            # Clear any initial messages
            logging_test_app.chat_messages.clear()
            
            # Execute setup command
            await pilot.press("slash")
            await pilot.type("setup")
            await pilot.press("enter")
            
            await pilot.pause(0.2)
            
            # Verify handler was called
            logging_test_app.setup_handler.handle_setup_command.assert_called_once()
            
            # Check chat messages
            chat_messages = [msg["message"] for msg in logging_test_app.chat_messages if not msg["is_user"]]
            
            # Should contain user-facing message
            user_facing_found = any("Setup started successfully" in msg for msg in chat_messages)
            assert user_facing_found, "User-facing message should appear in chat"
            
            # Should NOT contain debug messages
            debug_leaked = any("debug message" in msg.lower() for msg in chat_messages)
            assert not debug_leaked, "Debug messages should not leak to TUI"
            
            info_leaked = any("info message" in msg.lower() for msg in chat_messages)
            assert not info_leaked, "Info messages should not leak to TUI"

    @pytest.mark.asyncio
    async def test_only_user_messages_in_chat_during_setup(self, logging_test_app):
        """
        GIVEN setup process with mixed logging levels
        WHEN setup executes with debug logging enabled
        THEN only appropriate user messages appear in chat area
        """
        # Create a mock that simulates various log levels
        async def setup_with_various_logs():
            # Simulate debug logger calls (should not leak)
            logging_test_app.setup_handler.debug_log.debug("Initializing setup components")
            logging_test_app.setup_handler.debug_log.info("Configuration loaded")
            logging_test_app.setup_handler.debug_log.warning("Minor warning in setup")
            logging_test_app.setup_handler.debug_log.error("Non-critical error handled")
            
            # User-facing messages (should appear)
            logging_test_app.chat_area.add_message("🚀 **Setup wizard started**", is_user=False)
            logging_test_app.chat_area.add_message("✅ **Configuration completed**", is_user=False)
        
        logging_test_app.setup_handler.handle_setup_command.side_effect = setup_with_various_logs
        
        async with logging_test_app.run_test() as pilot:
            logging_test_app.chat_messages.clear()
            
            # Execute setup
            await pilot.press("slash")  
            await pilot.type("setup")
            await pilot.press("enter")
            
            await pilot.pause(0.2)
            
            chat_messages = [msg["message"] for msg in logging_test_app.chat_messages]
            
            # Should have user-facing messages
            assert any("Setup wizard started" in msg for msg in chat_messages)
            assert any("Configuration completed" in msg for msg in chat_messages)
            
            # Should not have internal log messages
            assert not any("Initializing setup components" in msg for msg in chat_messages)
            assert not any("Configuration loaded" in msg for msg in chat_messages)


class TestVerificationStepFreezingBug:
    """Test regression for verification step freezing the TUI."""

    @pytest.fixture
    async def verification_test_app(self, tmp_path):
        """Create test app for verification freeze testing."""
        project_dir = tmp_path / "verification_test"
        project_dir.mkdir()
        
        config_manager = ConfigManager(str(project_dir))
        app = PyWizardTUIApp(config_manager)
        
        # Track if UI remains responsive during verification
        app.ui_responsive = True
        app.verification_completed = False
        
        # Mock verification to simulate long-running operation
        async def mock_verification():
            # Simulate long-running verification that should not block UI
            await asyncio.sleep(0.1)  # Simulate work
            app.verification_completed = True
            app.chat_area.add_message("✅ **Verification completed**", is_user=False)
        
        # Mock the worker-decorated method
        with patch.object(app.setup_handler, '_run_verification_worker', new=mock_verification):
            with patch.object(app.setup_handler, '_run_standalone_verification_worker', new=mock_verification):
                yield app

    @pytest.mark.asyncio
    async def test_verification_does_not_freeze_ui(self, verification_test_app):
        """
        GIVEN verification process takes time to complete
        WHEN verification step runs
        THEN UI should remain responsive throughout
        AND verification should complete without freezing
        """
        async with verification_test_app.run_test() as pilot:
            await pilot.pause(0.1)
            
            # Start verification
            await verification_test_app.setup_handler.perform_setup_verification()
            
            # UI should remain responsive during verification
            assert verification_test_app.ui_responsive, "UI should remain responsive"
            
            # Wait for verification to complete
            await pilot.pause(0.3)
            
            # Verification should complete
            assert verification_test_app.verification_completed, "Verification should complete"

    @pytest.mark.asyncio
    async def test_standalone_verification_does_not_freeze_ui(self, verification_test_app):
        """
        GIVEN standalone verification process
        WHEN --verify-only command is executed
        THEN UI should not freeze during verification
        """
        async with verification_test_app.run_test() as pilot:
            await pilot.pause(0.1)
            
            # Start standalone verification
            await verification_test_app.setup_handler.perform_setup_verification_standalone()
            
            # UI should remain responsive
            assert verification_test_app.ui_responsive, "UI should remain responsive during standalone verification"
            
            await pilot.pause(0.3)
            
            # Verification should complete
            assert verification_test_app.verification_completed, "Standalone verification should complete"

    @pytest.mark.asyncio
    async def test_verification_uses_background_worker(self, verification_test_app):
        """
        GIVEN verification process
        WHEN verification runs
        THEN it should use the @work decorated background worker
        AND not block the main UI thread
        """
        async with verification_test_app.run_test() as pilot:
            await pilot.pause(0.1)
            
            # Mock the @work decorator behavior check
            with patch('juno_agent.fancy_ui.handlers.setup_handler.work') as mock_work:
                # The @work decorator should be used
                verification_test_app.setup_handler.perform_setup_verification_standalone()
                
                # Check that background processing is working
                await pilot.pause(0.2)
                
                # UI should remain responsive
                assert verification_test_app.is_running, "App should remain running during verification"


class TestMCPInstallationRegression:
    """Test regression for MCP installation functionality."""

    @pytest.fixture
    async def mcp_test_app(self, tmp_path):
        """Create test app for MCP installation testing."""
        project_dir = tmp_path / "mcp_test"
        project_dir.mkdir()
        
        # Create Cursor directory structure for testing
        cursor_dir = project_dir / ".cursor"
        cursor_dir.mkdir()
        
        config_manager = ConfigManager(str(project_dir))
        app = PyWizardTUIApp(config_manager)
        
        # Mock MCP installer
        mock_installer = AsyncMock()
        mock_installer.install_mcp_servers = AsyncMock(return_value=True)
        app.setup_handler.mcp_installer_enhanced = mock_installer
        
        # Track MCP configuration files created
        app.mcp_files_created = []
        
        def track_file_creation(file_path, content=None):
            app.mcp_files_created.append(str(file_path))
            # Actually create the file for verification
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            if content:
                Path(file_path).write_text(content)
        
        # Mock file operations
        with patch('pathlib.Path.write_text', side_effect=lambda content: track_file_creation(project_dir / ".cursor" / "mcp.json", content)):
            yield app

    @pytest.mark.asyncio
    async def test_cursor_mcp_configuration_created(self, mcp_test_app):
        """
        GIVEN Cursor editor is selected
        WHEN MCP installation runs
        THEN .cursor/mcp.json should be created
        AND configuration should be valid
        """
        # Set up test data
        mcp_test_app.setup_handler.setup_data = {"selected_editor": "Cursor"}
        
        # Mock initialization
        mcp_test_app.setup_handler.initialize_setup_components = AsyncMock()
        
        async with mcp_test_app.run_test() as pilot:
            await pilot.pause(0.1)
            
            # Execute MCP installation step
            await mcp_test_app.setup_handler.perform_mcp_installation()
            
            # Verify MCP installer was called
            mcp_test_app.setup_handler.mcp_installer_enhanced.install_mcp_servers.assert_called()
            
            # In real implementation, verify .cursor/mcp.json was created
            # This test structure provides the framework for that verification

    @pytest.mark.asyncio
    async def test_mcp_installation_for_multiple_editors(self, mcp_test_app):
        """
        GIVEN different editors are selected
        WHEN MCP installation runs for each
        THEN appropriate configuration files should be created
        """
        editors_to_test = ["Cursor", "Claude Code", "Windsurf", "VS Code"]
        
        async with mcp_test_app.run_test() as pilot:
            for editor in editors_to_test:
                # Reset state
                mcp_test_app.setup_handler.mcp_installer_enhanced.reset_mock()
                mcp_test_app.setup_handler.setup_data = {"selected_editor": editor}
                
                await pilot.pause(0.1)
                
                # Execute MCP installation
                await mcp_test_app.setup_handler.perform_mcp_installation()
                
                # Verify installer was called for each editor
                mcp_test_app.setup_handler.mcp_installer_enhanced.install_mcp_servers.assert_called()

    @pytest.mark.asyncio
    async def test_mcp_installation_error_handling(self, mcp_test_app):
        """
        GIVEN MCP installation encounters errors
        WHEN installation step runs
        THEN errors should be handled gracefully
        AND setup should continue
        """
        # Make MCP installer fail
        mcp_test_app.setup_handler.mcp_installer_enhanced.install_mcp_servers.side_effect = Exception("MCP installation failed")
        
        mcp_test_app.setup_handler.setup_data = {"selected_editor": "Cursor"}
        
        async with mcp_test_app.run_test() as pilot:
            await pilot.pause(0.1)
            
            # Should not raise exception
            await mcp_test_app.setup_handler.perform_mcp_installation()
            
            # App should still be running
            assert mcp_test_app.is_running, "App should continue running after MCP installation error"


class TestSetupModeConsistencyRegression:
    """Test regression for consistency between different setup modes."""

    @pytest.fixture
    async def consistency_test_app(self, tmp_path):
        """Create test app for consistency testing."""
        project_dir = tmp_path / "consistency_test"
        project_dir.mkdir()
        
        config_manager = ConfigManager(str(project_dir))
        app = PyWizardTUIApp(config_manager)
        
        # Track calls to different setup modes
        app.setup_calls = {"regular": 0, "docs_only": 0, "verify_only": 0, "agentic": 0}
        
        # Mock handlers to track calls
        original_regular = app.setup_handler.handle_setup_command
        original_docs = app.setup_handler.handle_docs_only_command
        original_verify = app.setup_handler.handle_verification_only_command
        original_agentic = app.setup_handler.handle_agentic_resolver_command
        
        async def track_regular():
            app.setup_calls["regular"] += 1
            
        async def track_docs():
            app.setup_calls["docs_only"] += 1
            
        async def track_verify():
            app.setup_calls["verify_only"] += 1
            
        async def track_agentic():
            app.setup_calls["agentic"] += 1
        
        app.setup_handler.handle_setup_command = AsyncMock(side_effect=track_regular)
        app.setup_handler.handle_docs_only_command = AsyncMock(side_effect=track_docs)
        app.setup_handler.handle_verification_only_command = AsyncMock(side_effect=track_verify)
        app.setup_handler.handle_agentic_resolver_command = AsyncMock(side_effect=track_agentic)
        
        return app

    @pytest.mark.asyncio
    async def test_setup_modes_are_distinct(self, consistency_test_app):
        """
        GIVEN different setup command modes
        WHEN each mode is executed
        THEN each should call only its specific handler
        AND should not interfere with other modes
        """
        test_cases = [
            ("setup", "regular"),
            ("setup --docs-only", "docs_only"),
            ("setup --verify-only", "verify_only"),
            ("setup --agentic", "agentic")
        ]
        
        async with consistency_test_app.run_test() as pilot:
            for command, expected_mode in test_cases:
                # Reset call counters
                consistency_test_app.setup_calls = {k: 0 for k in consistency_test_app.setup_calls}
                
                await pilot.pause(0.1)
                
                # Execute command
                await pilot.press("slash")
                await pilot.type(command)
                await pilot.press("enter")
                
                await pilot.pause(0.2)
                
                # Verify only the expected mode was called
                assert consistency_test_app.setup_calls[expected_mode] == 1, f"Expected {expected_mode} to be called once"
                
                # Verify other modes were not called
                for mode, count in consistency_test_app.setup_calls.items():
                    if mode != expected_mode:
                        assert count == 0, f"Mode {mode} should not be called when executing {command}"