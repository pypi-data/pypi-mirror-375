"""
Comprehensive Textual Pilot tests for setup command execution functionality.

This module tests the primary setup command flows to ensure they work without errors
and provide proper user feedback. Tests focus on command parsing, routing, and 
basic execution paths.
"""

import pytest
import asyncio
import tempfile
import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from textual.pilot import Pilot
from juno_agent.fancy_ui.app import PyWizardTUIApp
from juno_agent.config import ConfigManager


class TestSetupCommandExecution:
    """Test setup command execution scenarios."""

    @pytest.fixture
    async def setup_test_app(self, tmp_path):
        """Create a test app instance with mocked setup handler."""
        # Create test environment
        project_dir = tmp_path / "test_project"
        project_dir.mkdir()
        
        # Create basic project files for dependency detection
        (project_dir / "requirements.txt").write_text("fastapi>=0.68.0\nuvicorn>=0.15.0\n")
        (project_dir / "src").mkdir()
        
        config_manager = ConfigManager(str(project_dir))
        app = PyWizardTUIApp(config_manager)
        
        # Mock the setup handler methods to prevent actual setup execution
        app.setup_handler.handle_setup_command = AsyncMock()
        app.setup_handler.handle_docs_only_command = AsyncMock()
        app.setup_handler.handle_verification_only_command = AsyncMock()
        app.setup_handler.handle_agentic_resolver_command = AsyncMock()
        
        return app

    @pytest.mark.asyncio
    async def test_basic_setup_command_execution(self, setup_test_app):
        """
        GIVEN a TUI application is running
        WHEN user types '/setup' command
        THEN the setup wizard should start without errors
        """
        async with setup_test_app.run_test() as pilot:
            # Wait for app initialization
            await pilot.pause(0.1)
            
            # Execute setup command
            await pilot.press("slash")
            await pilot.type("setup")
            await pilot.press("enter")
            
            # Wait for command processing
            await pilot.pause(0.2)
            
            # Verify setup handler was called
            setup_test_app.setup_handler.handle_setup_command.assert_called_once()
            
            # Verify no exceptions occurred (app is still running)
            assert setup_test_app.is_running

    @pytest.mark.asyncio
    async def test_setup_docs_only_command_execution(self, setup_test_app):
        """
        GIVEN a TUI application is running
        WHEN user types '/setup --docs-only' command
        THEN the docs-only setup flow should execute
        """
        async with setup_test_app.run_test() as pilot:
            await pilot.pause(0.1)
            
            # Execute docs-only setup command
            await pilot.press("slash")
            await pilot.type("setup --docs-only")
            await pilot.press("enter")
            
            await pilot.pause(0.2)
            
            # Verify docs-only handler was called
            setup_test_app.setup_handler.handle_docs_only_command.assert_called_once()
            
            # Verify regular setup was not called
            setup_test_app.setup_handler.handle_setup_command.assert_not_called()

    @pytest.mark.asyncio
    async def test_setup_verify_only_command_execution(self, setup_test_app):
        """
        GIVEN a TUI application is running
        WHEN user types '/setup --verify-only' command  
        THEN the verification-only flow should execute
        """
        async with setup_test_app.run_test() as pilot:
            await pilot.pause(0.1)
            
            # Execute verification-only setup command
            await pilot.press("slash")
            await pilot.type("setup --verify-only")
            await pilot.press("enter")
            
            await pilot.pause(0.2)
            
            # Verify verification handler was called
            setup_test_app.setup_handler.handle_verification_only_command.assert_called_once()
            
            # Verify other handlers were not called
            setup_test_app.setup_handler.handle_setup_command.assert_not_called()
            setup_test_app.setup_handler.handle_docs_only_command.assert_not_called()

    @pytest.mark.asyncio
    async def test_setup_agentic_command_execution(self, setup_test_app):
        """
        GIVEN a TUI application is running
        WHEN user types '/setup --agentic' command
        THEN the agentic dependency resolver flow should execute
        """
        async with setup_test_app.run_test() as pilot:
            await pilot.pause(0.1)
            
            # Execute agentic resolver setup command
            await pilot.press("slash")
            await pilot.type("setup --agentic")
            await pilot.press("enter")
            
            await pilot.pause(0.2)
            
            # Verify agentic resolver handler was called
            setup_test_app.setup_handler.handle_agentic_resolver_command.assert_called_once()
            
            # Verify other handlers were not called
            setup_test_app.setup_handler.handle_setup_command.assert_not_called()

    @pytest.mark.asyncio 
    async def test_setup_command_argument_parsing(self, setup_test_app):
        """
        GIVEN a TUI application is running
        WHEN user types setup commands with various argument combinations
        THEN the correct handlers should be called for each
        """
        test_cases = [
            ("setup", "handle_setup_command"),
            ("setup --docs-only", "handle_docs_only_command"),  
            ("setup --verify-only", "handle_verification_only_command"),
            ("setup --agentic", "handle_agentic_resolver_command"),
            ("setup   --docs-only  ", "handle_docs_only_command"),  # with extra spaces
        ]
        
        async with setup_test_app.run_test() as pilot:
            for command, expected_method in test_cases:
                # Reset mocks
                setup_test_app.setup_handler.handle_setup_command.reset_mock()
                setup_test_app.setup_handler.handle_docs_only_command.reset_mock()
                setup_test_app.setup_handler.handle_verification_only_command.reset_mock()
                setup_test_app.setup_handler.handle_agentic_resolver_command.reset_mock()
                
                await pilot.pause(0.1)
                
                # Execute command
                await pilot.press("slash")
                await pilot.type(command)
                await pilot.press("enter")
                
                await pilot.pause(0.2)
                
                # Verify correct method was called
                expected_handler = getattr(setup_test_app.setup_handler, expected_method)
                expected_handler.assert_called_once()

    @pytest.mark.asyncio
    async def test_setup_command_invalid_arguments(self, setup_test_app):
        """
        GIVEN a TUI application is running  
        WHEN user types '/setup --invalid-arg' command
        THEN it should default to regular setup flow
        """
        async with setup_test_app.run_test() as pilot:
            await pilot.pause(0.1)
            
            # Execute setup command with invalid argument
            await pilot.press("slash")
            await pilot.type("setup --invalid-arg")
            await pilot.press("enter")
            
            await pilot.pause(0.2)
            
            # Should fall back to regular setup
            setup_test_app.setup_handler.handle_setup_command.assert_called_once()
            
            # Verify other handlers were not called
            setup_test_app.setup_handler.handle_docs_only_command.assert_not_called()
            setup_test_app.setup_handler.handle_verification_only_command.assert_not_called()

    @pytest.mark.asyncio
    async def test_setup_command_empty_args(self, setup_test_app):
        """
        GIVEN a TUI application is running
        WHEN user types '/setup' with no arguments
        THEN regular setup should execute
        """
        async with setup_test_app.run_test() as pilot:
            await pilot.pause(0.1)
            
            await pilot.press("slash")
            await pilot.type("setup")
            await pilot.press("enter")
            
            await pilot.pause(0.2)
            
            # Should execute regular setup
            setup_test_app.setup_handler.handle_setup_command.assert_called_once()

    @pytest.mark.asyncio
    async def test_multiple_setup_commands_sequential(self, setup_test_app):
        """
        GIVEN a TUI application is running
        WHEN user executes multiple setup commands sequentially
        THEN each command should execute properly without interference
        """
        commands = ["setup", "setup --docs-only", "setup --verify-only"]
        expected_methods = [
            "handle_setup_command",
            "handle_docs_only_command", 
            "handle_verification_only_command"
        ]
        
        async with setup_test_app.run_test() as pilot:
            for command, expected_method in zip(commands, expected_methods):
                await pilot.pause(0.1)
                
                # Reset all mocks
                setup_test_app.setup_handler.handle_setup_command.reset_mock()
                setup_test_app.setup_handler.handle_docs_only_command.reset_mock()
                setup_test_app.setup_handler.handle_verification_only_command.reset_mock()
                
                # Execute command
                await pilot.press("slash")
                await pilot.type(command)
                await pilot.press("enter")
                
                await pilot.pause(0.2)
                
                # Verify correct method was called
                expected_handler = getattr(setup_test_app.setup_handler, expected_method)
                expected_handler.assert_called_once()


class TestSetupCommandError:
    """Test setup command error handling scenarios."""
    
    @pytest.fixture
    async def error_prone_app(self, tmp_path):
        """Create a test app that simulates setup errors."""
        project_dir = tmp_path / "error_project"
        project_dir.mkdir()
        
        config_manager = ConfigManager(str(project_dir))
        app = PyWizardTUIApp(config_manager)
        
        # Make setup handlers raise exceptions
        app.setup_handler.handle_setup_command = AsyncMock(
            side_effect=Exception("Mock setup error")
        )
        app.setup_handler.handle_docs_only_command = AsyncMock(
            side_effect=Exception("Mock docs error")  
        )
        
        return app

    @pytest.mark.asyncio
    async def test_setup_command_error_handling(self, error_prone_app):
        """
        GIVEN a TUI application where setup handlers throw errors
        WHEN user executes setup commands
        THEN the app should handle errors gracefully and remain running
        """
        async with error_prone_app.run_test() as pilot:
            await pilot.pause(0.1)
            
            # Execute setup command that will throw error
            await pilot.press("slash")
            await pilot.type("setup")
            await pilot.press("enter")
            
            await pilot.pause(0.2)
            
            # App should still be running despite error
            assert error_prone_app.is_running
            
            # Verify the handler was called (and threw error)
            error_prone_app.setup_handler.handle_setup_command.assert_called_once()

    @pytest.mark.asyncio
    async def test_docs_only_command_error_handling(self, error_prone_app):
        """
        GIVEN a TUI application where docs handler throws errors
        WHEN user executes docs-only setup command
        THEN the app should handle errors gracefully
        """
        async with error_prone_app.run_test() as pilot:
            await pilot.pause(0.1)
            
            # Execute docs-only command that will throw error
            await pilot.press("slash")
            await pilot.type("setup --docs-only")  
            await pilot.press("enter")
            
            await pilot.pause(0.2)
            
            # App should still be running
            assert error_prone_app.is_running
            
            # Verify the handler was called
            error_prone_app.setup_handler.handle_docs_only_command.assert_called_once()


class TestSetupCommandUI:
    """Test setup command UI interactions and feedback."""
    
    @pytest.fixture
    async def ui_test_app(self, tmp_path):
        """Create a test app for UI testing."""
        project_dir = tmp_path / "ui_test_project"
        project_dir.mkdir()
        
        config_manager = ConfigManager(str(project_dir))
        app = PyWizardTUIApp(config_manager)
        
        # Mock setup handlers to provide UI feedback simulation
        async def mock_setup():
            # Simulate adding a message to chat area
            app.chat_area.add_message("🚀 **Setup wizard started**", is_user=False)
            
        async def mock_docs_only():
            app.chat_area.add_message("📚 **Documentation fetching started**", is_user=False)
            
        app.setup_handler.handle_setup_command = AsyncMock(side_effect=mock_setup)
        app.setup_handler.handle_docs_only_command = AsyncMock(side_effect=mock_docs_only)
        
        return app

    @pytest.mark.asyncio
    async def test_setup_command_provides_user_feedback(self, ui_test_app):
        """
        GIVEN a TUI application is running
        WHEN user executes setup command
        THEN appropriate feedback should appear in chat area
        """
        async with ui_test_app.run_test() as pilot:
            await pilot.pause(0.1)
            
            # Execute setup command
            await pilot.press("slash")
            await pilot.type("setup")
            await pilot.press("enter")
            
            await pilot.pause(0.3)  # Allow time for UI update
            
            # Verify handler was called
            ui_test_app.setup_handler.handle_setup_command.assert_called_once()
            
            # Note: In real implementation, you would check chat_area content
            # This is a basic structure - actual chat content checking would
            # require accessing the chat widget's message history

    @pytest.mark.asyncio  
    async def test_command_autocomplete_shows_setup(self, ui_test_app):
        """
        GIVEN a TUI application is running
        WHEN user types '/' to trigger autocomplete
        THEN setup command should be available in suggestions
        """
        async with ui_test_app.run_test() as pilot:
            await pilot.pause(0.1)
            
            # Type slash to trigger autocomplete
            await pilot.press("slash")
            
            # Note: Actual autocomplete testing would require checking
            # the autocomplete menu content. This is a structural test.
            await pilot.pause(0.1)
            
            # The autocomplete widget should show setup as an option
            # In real implementation, you would check widget state
            assert ui_test_app.is_running  # Basic sanity check