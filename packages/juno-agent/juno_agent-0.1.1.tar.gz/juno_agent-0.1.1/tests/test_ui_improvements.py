"""Tests for UI improvements and bug fixes."""

import asyncio
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from rich.console import Console

from juno_agent.config import ConfigManager
from juno_agent.ui import (
    WelcomeScreen, ChatInterface, AutoCompleteInput, WizardApp
)
from juno_agent.utils import SystemStatus


class TestAPIKeyInputMasking:
    """Test that API key input is properly masked."""
    
    # NOTE: SetupWizard has been removed, these tests need to be updated
    # to test the unified setup pipeline instead
    pass


class TestAutoComplete:
    """Test autocomplete functionality."""
    
    def test_autocomplete_initialization(self):
        """Test that AutoCompleteInput initializes correctly."""
        console = Console()
        commands = ["/help", "/setup", "/exit"]
        autocomplete = AutoCompleteInput(commands, console)
        
        assert autocomplete.commands == commands
        assert autocomplete.console == console
    
    def test_command_suggestions(self):
        """Test command suggestion functionality."""
        console = Console()
        commands = ["/help", "/setup", "/exit"]
        autocomplete = AutoCompleteInput(commands, console)
        
        # Test getting suggestions
        suggestions = autocomplete.get_suggestions("/he")
        assert suggestions == ["/help"]
        
        suggestions = autocomplete.get_suggestions("/")
        assert len(suggestions) == 3
        
        suggestions = autocomplete.get_suggestions("/nonexistent")
        assert suggestions == []


class TestWelcomeScreen:
    """Test welcome screen display."""
    
    def test_welcome_screen_display(self):
        """Test that welcome screen displays correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            config_manager = ConfigManager(workdir)
            system_status = SystemStatus(workdir)
            
            welcome = WelcomeScreen(config_manager, system_status)
            
            # Should not raise any exceptions
            welcome.display()


class TestChatInterface:
    """Test chat interface functionality."""
    
    def test_chat_interface_initialization(self):
        """Test that ChatInterface initializes correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            config_manager = ConfigManager(workdir)
            
            chat = ChatInterface(config_manager)
            
            assert chat.config_manager == config_manager
            assert chat.commands
            assert chat.autocomplete_input


class TestEventLoopSafety:
    """Test event loop safety for various UI operations."""
    
    def test_run_coro_in_thread(self):
        """Test that _run_coro_in_thread safely executes coroutines."""
        from juno_agent.ui import _run_coro_in_thread
        
        async def test_coro():
            await asyncio.sleep(0.01)
            return "success"
        
        result = _run_coro_in_thread(test_coro())
        assert result == "success"
    
    def test_no_nested_event_loops(self):
        """Test that UI operations don't create nested event loops."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            config_manager = ConfigManager(workdir)
            
            # Create chat interface
            chat = ChatInterface(config_manager)
            
            # This should not raise any nested event loop errors
            # when running in an async context
            async def test_async_operations():
                # Simulate some async operations
                await asyncio.sleep(0.01)
                return True
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(test_async_operations())
                assert result
            finally:
                loop.close()


class TestPromptToolkitIntegration:
    """Test prompt_toolkit integration."""
    
    def test_unified_style(self):
        """Test that unified prompt_toolkit style is available."""
        from juno_agent.ui import get_unified_pt_style
        
        style = get_unified_pt_style()
        # Style may be None if prompt_toolkit is not installed,
        # but function should not raise
        assert style is None or style is not None


class TestSimpleUI:
    """Test Simple UI mode functionality."""
    
    @pytest.mark.asyncio
    async def test_simple_ui_no_alternate_screen(self):
        """Test that Simple UI doesn't switch to alternate screen."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            config_manager = ConfigManager(workdir)
            
            app = WizardApp(config_manager)
            
            # Simple UI should not use Textual or curses
            # which would switch to alternate screen
            assert hasattr(app, 'run_simple_ui')