"""Tests for command autocomplete functionality."""

import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from rich.console import Console

from juno_agent.ui import AutoCompleteInput


class TestAutoCompleteInput:
    """Test AutoCompleteInput class."""
    
    def test_initialization(self):
        """Test AutoCompleteInput initialization."""
        commands = ["/test", "/help"]
        console = Console()
        
        autocomplete = AutoCompleteInput(commands, console)
        assert autocomplete.commands == commands
        assert autocomplete.console == console
    
    def test_get_suggestions(self):
        """Test getting command suggestions."""
        commands = ["/apikey", "/agent", "/editor", "/exit", "/help"]
        console = Console()
        autocomplete = AutoCompleteInput(commands, console)
        
        # Test partial command completion
        suggestions = autocomplete.get_suggestions("/a")
        assert "/apikey" in suggestions
        assert "/agent" in suggestions
        assert len(suggestions) == 2
        
        # Test single completion
        suggestions = autocomplete.get_suggestions("/api")
        assert suggestions == ["/apikey"]
        
        # Test all commands
        suggestions = autocomplete.get_suggestions("/")
        assert len(suggestions) == 5
        
        # Test no match
        suggestions = autocomplete.get_suggestions("/xyz")
        assert suggestions == []
        
        # Test non-command
        suggestions = autocomplete.get_suggestions("hello")
        assert suggestions == []
    
    def test_show_completions(self):
        """Test showing available completions."""
        commands = ["/apikey", "/agent", "/editor", "/exit"]
        console = Console()
        autocomplete = AutoCompleteInput(commands, console)
        
        # Test partial command completion
        completions = autocomplete.show_completions("/a")
        assert "/apikey" in completions
        assert "/agent" in completions
        assert len(completions) == 2
        
        # Test single completion
        completions = autocomplete.show_completions("/api")
        assert completions == ["/apikey"]
        
        # Test all completions
        completions = autocomplete.show_completions("/")
        assert len(completions) == 4
        
        # Test no match
        completions = autocomplete.show_completions("/nonexistent")
        assert completions == []
    
    def test_update_commands(self):
        """Test updating the command list."""
        commands = ["/test", "/help"]
        console = Console()
        autocomplete = AutoCompleteInput(commands, console)
        
        # Initial commands
        assert autocomplete.commands == commands
        
        # Update commands
        new_commands = ["/apikey", "/editor", "/exit"]
        autocomplete.update_commands(new_commands)
        assert autocomplete.commands == new_commands
        
        # Verify new suggestions work
        suggestions = autocomplete.get_suggestions("/api")
        assert suggestions == ["/apikey"]
    
    def test_cleanup(self):
        """Test cleanup method."""
        commands = ["/test", "/help"]
        console = Console()
        autocomplete = AutoCompleteInput(commands, console)
        
        # Should not raise any exceptions
        autocomplete.cleanup()
    
    @pytest.mark.asyncio
    async def test_ainput_with_prompt_toolkit(self):
        """Test async input with prompt_toolkit."""
        commands = ["/test", "/help"]
        console = Console()
        autocomplete = AutoCompleteInput(commands, console)
        
        # Mock prompt_toolkit session
        mock_session = MagicMock()
        mock_session.prompt_async = MagicMock(return_value="/test")
        
        with patch.object(autocomplete, 'pt_session', mock_session):
            # This would normally be called in an async context
            # We're just testing the structure exists
            assert hasattr(autocomplete, 'ainput')
    
    def test_history_file_location(self):
        """Test that history file is created in the right location."""
        commands = ["/test", "/help"]
        console = Console()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            autocomplete = AutoCompleteInput(commands, console, config_dir)
            
            # Check history file path
            if autocomplete.history_file:
                # History should be in .askbudi/simple_history/chat_history.txt
                assert ".askbudi" in str(autocomplete.history_file)
                assert "chat_history.txt" in str(autocomplete.history_file)