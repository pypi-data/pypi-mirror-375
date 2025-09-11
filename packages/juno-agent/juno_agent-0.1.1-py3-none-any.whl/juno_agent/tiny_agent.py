"""TinyCodeAgent integration for juno-agent."""

import asyncio
import json
import os
import platform
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
import uuid
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from .config import ConfigManager
from .debug_logger import debug_logger
from .system_prompt_manager import SystemPromptManager


def is_binary_file(file_path: str) -> bool:
    """
    Check if a file is binary by examining its extension and content.
    
    Args:
        file_path: Path to the file to check
        
    Returns:
        True if the file is likely binary, False otherwise
    """
    # Common binary file extensions
    binary_extensions = {
        '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp',  # Images
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',  # Documents
        '.zip', '.tar', '.gz', '.rar', '.7z',  # Archives
        '.exe', '.dll', '.so', '.dylib',  # Executables/Libraries
        '.mp3', '.mp4', '.wav', '.avi', '.mov',  # Media
        '.bin', '.dat', '.sqlite', '.db'  # Data files
    }
    
    file_path = Path(file_path)
    
    # Check extension first
    if file_path.suffix.lower() in binary_extensions:
        return True
    
    # For small files, check if content appears to be binary
    try:
        if file_path.exists() and file_path.stat().st_size > 0:
            with open(file_path, 'rb') as f:
                chunk = f.read(512)  # Read first 512 bytes
                if b'\x00' in chunk:  # Null bytes typically indicate binary
                    return True
                # Check for high ratio of non-printable characters
                printable_chars = sum(1 for byte in chunk if 32 <= byte <= 126 or byte in (9, 10, 13))
                if len(chunk) > 0 and printable_chars / len(chunk) < 0.7:
                    return True
    except (IOError, OSError):
        pass
    
    return False


def get_file_info_for_binary(file_path: str) -> str:
    """
    Get informative description for binary files instead of their content.
    
    Args:
        file_path: Path to the binary file
        
    Returns:
        Description of the binary file
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        return f"File not found: {file_path}"
    
    try:
        stat = file_path.stat()
        size = stat.st_size
        
        # Format file size
        if size < 1024:
            size_str = f"{size} bytes"
        elif size < 1024 * 1024:
            size_str = f"{size / 1024:.1f} KB"
        else:
            size_str = f"{size / (1024 * 1024):.1f} MB"
        
        file_type = file_path.suffix.lower() or "unknown"
        
        return f"BINARY FILE: {file_path.name}\n" \
               f"Type: {file_type} file\n" \
               f"Size: {size_str}\n" \
               f"Path: {file_path}\n" \
               f"Note: Binary files cannot be displayed as text. Use appropriate tools for viewing this file type."
    
    except (IOError, OSError) as e:
        return f"ERROR reading file info for {file_path}: {e}"


class TinyCodeAgentChat:
    """Chat interface with TinyCodeAgent integration."""
    
    def __init__(self, config_manager: ConfigManager, debug: bool = False, console: Optional[Console] = None, ui_callback: Optional[Callable[[str, dict], None]] = None, storage_manager=None, enable_custom_instructions: bool = True):
        debug_logger.log_function_entry("TinyCodeAgentChat.__init__",
                                       debug=debug,
                                       ui_callback_available=ui_callback is not None,
                                       console_overridden=console is not None,
                                       storage_manager_available=storage_manager is not None)
        
        # Use debug logger instead of print for storage manager details
        if storage_manager:
            debug_logger.log_event("storage_manager_provided", 
                                 storage_type=type(storage_manager).__name__,
                                 session_id=getattr(storage_manager, 'current_session_id', 'None'))
        else:
            debug_logger.log_event("no_storage_manager")
        
        self.config_manager = config_manager
        # Store original console parameter for UI mode detection
        self._original_console = console
        # Allow overriding the console (e.g., to suppress Rich output inside Textual)
        self.console = console or Console()
        self.conversation_history: List[Dict[str, Any]] = []
        self.agent = None  # Will be initialized when needed
        self.subagent = None  # Coding subagent for specialized tasks
        self.debug_logger = config_manager.create_debug_logger(debug=debug)  # Debug logging
        self.debug = debug  # Store debug flag
        self.ui_callback = ui_callback  # Optional UI update callback for tool tracking
        self.storage_manager = storage_manager  # Optional storage manager for conversation persistence
        self.enable_custom_instructions = enable_custom_instructions  # Whether to enable custom instructions
        self.token_tracker = None  # Will be set when agent is initialized
        self.system_prompt_manager = SystemPromptManager(workdir=config_manager.workdir, config_manager=config_manager)
        
        # Debug: Log the ui_callback details
        if ui_callback:
            import asyncio
            debug_logger.log_event("tiny_code_agent_ui_callback_received",
                                 callback_id=hex(id(ui_callback)),
                                 callback_name=getattr(ui_callback, '__name__', 'unknown'),
                                 is_async=asyncio.iscoroutinefunction(ui_callback),
                                 is_method=hasattr(ui_callback, '__self__'))
        else:
            debug_logger.log_event("tiny_code_agent_no_ui_callback")
        self.log_manager = self.initialize_log_manager(config_manager.config_dir, debug)
        
        debug_logger.log_event("tiny_code_agent_chat_initialized",
                             agent_id=hex(id(self)),
                             ui_callback_id=hex(id(ui_callback)) if ui_callback else None)
    
    def _construct_model_name(self, agent_config) -> str:
        """Construct model name consistently across main agent and subagents.
        
        This method ensures that all agents (main and subagents) use the exact same
        model name construction logic to prevent model mismatches.
        
        Args:
            agent_config: Agent configuration object
            
        Returns:
            Properly formatted model name string
        """
        if agent_config.provider.lower() in agent_config.model_name.lower():
            return agent_config.model_name
        else:
            return agent_config.provider.lower() + "/" + agent_config.model_name.lower()

    def initialize_log_manager(self, config_dir: Path, debug: bool = False):
        """Initialize log manager with graceful fallback when tinyagent is not available."""
        import logging
        import sys
        import os
        
        self.config_dir = config_dir
        self.logs_dir = config_dir / "logs"
        self.logs_dir.mkdir(exist_ok=True)
        
        # Use centralized app_run.log file in current working directory
        self.log_file = Path(os.getcwd()) / "app_run.log"
        
        try:
            # Try to use TinyAgent's LoggingManager if available
            from tinyagent.hooks.logging_manager import LoggingManager
            
            log_manager = LoggingManager(default_level=logging.INFO)
            log_manager.set_levels({
                'tinyagent.hooks.gradio_callback': logging.DEBUG,
                'tinyagent.tiny_agent': logging.DEBUG,
                'tinyagent.mcp_client': logging.INFO,
                'tinyagent.code_agent': logging.DEBUG,
                'tinyagent': logging.DEBUG,  # Catch all tinyagent logs
            })

            # No console handler - all logs go to file only to prevent TUI leakage
            # This prevents debug logs from appearing in the TUI interface
            
            # File handler - append to centralized log file, always log DEBUG to file
            file_handler = logging.FileHandler(self.log_file, mode='a')
            file_handler.setLevel(logging.DEBUG)

            log_manager.configure_handler(
                file_handler,
                format_string='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                level=logging.DEBUG
            )
            
            
            # Only redirect TinyAgent-specific loggers, not the root logger
            for logger_name in ['tinyagent', 'tinyagent.tiny_agent', 'tinyagent.mcp_client', 
                               'tinyagent.code_agent', 'tinyagent.hooks']:
                specific_logger = logging.getLogger(logger_name)
                # Remove any existing console handlers
                for handler in specific_logger.handlers[:]:
                    if isinstance(handler, logging.StreamHandler) and handler.stream in (sys.stdout, sys.stderr):
                        specific_logger.removeHandler(handler)
                # Add file handler if not already present
                if file_handler not in specific_logger.handlers:
                    specific_logger.addHandler(file_handler)
                specific_logger.setLevel(logging.DEBUG)
                specific_logger.propagate = False  # Don't propagate to root
            
            
            # Log initialization message to mark TinyAgent logging start
            logger = logging.getLogger('tinyagent.tiny_agent')
            logger.info(f"TinyAgent LogManager initialized - writing to {self.log_file}")

            return log_manager
            
        except ImportError:
            # Fallback to standard Python logging when tinyagent is not available
            log_manager = logging.getLogger('juno_agent.fallback')
            log_manager.setLevel(logging.DEBUG if debug else logging.INFO)
            
            # Create file handler - no console handler to prevent TUI leakage
            file_handler = logging.FileHandler(self.log_file, mode='a')
            file_handler.setLevel(logging.DEBUG)
            
            # Create formatter
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            
            # Add file handler only to logger
            if not log_manager.handlers:  # Avoid duplicate handlers
                log_manager.addHandler(file_handler)
            
            # Log fallback initialization message
            log_manager.info(f"Fallback LogManager initialized (tinyagent not available) - writing to {self.log_file}")
            
            return log_manager

    async def create_coding_subagent(self, force_new: bool = False):
        """Create a specialized coding subagent with shell tools only.
        
        Args:
            force_new: If True, always create a new subagent regardless of config
        """
        config = self.config_manager.load_config()
        agent_config = config.agent_config
        
        # CRITICAL FIX: Always create new subagent instances for proper session isolation
        # Each subagent call should get its own unique session and storage context
        # Disable reuse to ensure this behavior
        force_new = True  # Override to ensure unique instances
        debug_logger.log_event("create_coding_subagent_forcing_new", reason="proper session isolation")
            
        try:
            # Import TinyCodeAgent and callbacks
            from tinyagent import TinyCodeAgent
            from tinyagent.hooks import MessageCleanupHook
            from tinyagent.hooks import AnthropicPromptCacheCallback
            from tinyagent.hooks.token_tracker import create_token_tracker
            
            # Get API key for the configured model
            api_key = self.config_manager.get_model_api_key()
            if not api_key:
                expected_env_var = self._get_expected_env_var(agent_config.provider)
                raise ValueError(f"API key not found for subagent. Set {expected_env_var} environment variable")
            
            # Determine execution provider - same as main agent
            use_seatbelt = self._should_use_seatbelt()
            
            # CRITICAL FIX: Use consistent model name and prioritize parent's exact model
            parent_model = getattr(self.agent, 'model', None) if self.agent else None
            
            if parent_model:
                # Always use parent's exact model to ensure consistency
                model_name = parent_model
                debug_logger.log_event("create_coding_subagent_parent_model", model=model_name)
            else:
                # Fallback to standardized construction if no parent agent
                model_name = self._construct_model_name(agent_config)
                debug_logger.log_event("create_coding_subagent_constructed_model", model=model_name)
            
            subagent_params = {
                "model": model_name,
                "api_key": api_key,
                "system_prompt": self._get_subagent_system_prompt(agent_config),
                "enable_python_tool": False,  # Disabled as requested
                "enable_shell_tool": True,    # Enabled as requested
                "enable_file_tools": True,    # Enable file tools
                "enable_todo_write": True,    # Enable TodoWrite tool
                "local_execution": True,      # Same as main agent
                "temperature": agent_config.temperature,
                "default_workdir": str(self.config_manager.workdir)
            }
            
            # CRITICAL FIX: Add storage parameters if storage manager is available (each subagent gets unique session)
            if self.storage_manager:
                self.storage_manager._initialize_storage()
                if self.storage_manager.storage:
                    # Validate storage parameters before adding
                    if self.storage_manager.user_id is None:
                        raise ValueError("CRITICAL ERROR: storage_manager.user_id is None when creating subagent!")
                    
                    if self.storage_manager.current_session_id is None:
                        raise ValueError("CRITICAL ERROR: storage_manager.current_session_id is None when creating subagent!")
                    
                    # Create unique session ID for each subagent call (no reuse)
                    subagent_session_id = str(uuid.uuid4()) + "_subagent"
                    # Use main agent's user_id with _subagent postfix for proper isolation
                    subagent_user_id = self.storage_manager.user_id + "_subagent"
                    
                    storage_params = {
                        "storage": self.storage_manager.storage,
                        "session_id": subagent_session_id,
                        "user_id": subagent_user_id
                    }
                    
                    # Additional validation
                    assert storage_params["user_id"] is not None, "user_id must not be None"
                    assert storage_params["session_id"] is not None, "session_id must not be None"
                    
                    subagent_params.update(storage_params)
                    debug_logger.log_event("create_coding_subagent_storage", session_id=subagent_session_id, user_id=subagent_user_id)
            
            # Configure execution provider - same as main agent
            if use_seatbelt:
                subagent_params["provider"] = "seatbelt"
            else:
                subagent_params["provider"] = "modal"
                subagent_params["local_execution"] = True
            
            # Add max_tokens if specified
            if agent_config.max_tokens:
                subagent_params["max_tokens"] = agent_config.max_tokens
            
            # Add custom base URL if specified
            if agent_config.custom_base_url:
                subagent_params["base_url"] = agent_config.custom_base_url
            
            # Add custom parameters
            if agent_config.custom_params:
                subagent_params.update(agent_config.custom_params)
            
            # Add model_kwargs from configuration (inherit from main agent, excluding juno_config)
            if agent_config.model_kwargs:
                if "model_kwargs" not in subagent_params:
                    subagent_params["model_kwargs"] = {}
                
                # Create a copy of model_kwargs and remove juno_config before passing to TinyAgent
                model_kwargs_copy = agent_config.model_kwargs.copy()
                juno_config_removed = model_kwargs_copy.pop("juno_config", None)
                
                subagent_params["model_kwargs"].update(model_kwargs_copy)
                debug_logger.log_event("create_coding_subagent_model_kwargs", 
                                     kwargs=model_kwargs_copy,
                                     juno_config_removed=bool(juno_config_removed))
            
            # Initialize coding subagent
            new_subagent = TinyCodeAgent(**subagent_params)
            
            # CRITICAL FIX: Validate model name propagation after creation
            parent_model = getattr(self.agent, 'model', None) if self.agent else None
            subagent_model = getattr(new_subagent, 'model', None)
            debug_logger.log_event("create_coding_subagent_models", parent=parent_model, subagent=subagent_model)
            if parent_model and subagent_model != parent_model:
                print(f"[ERROR] create_coding_subagent: CRITICAL MODEL MISMATCH! Expected: {parent_model}, Got: {subagent_model}")
                print(f"[ERROR] create_coding_subagent: This indicates a regression in model propagation logic!")
                raise ValueError(f"Subagent model mismatch: expected {parent_model}, got {subagent_model}")
            else:
                debug_logger.log_event("create_coding_subagent_model_propagation_success")
            
            # CRITICAL FIX: Add all parent callbacks to subagent (properly propagated from parent)
            # Extract and propagate callbacks from parent agent if available
            message_cleanup_callback = None
            anthropic_cache_callback = None
            
            if self.agent and hasattr(self.agent, 'callbacks'):
                for callback in self.agent.callbacks:
                    callback_type = type(callback).__name__
                    
                    # Find MessageCleanupHook in parent callbacks
                    if callback_type == 'MessageCleanupHook':
                        message_cleanup_callback = callback
                        debug_logger.log_event("create_coding_subagent_found_cleanup_hook")
                    
                    # Find AnthropicPromptCacheCallback in parent callbacks
                    elif callback_type == 'AnthropicPromptCacheCallback':
                        anthropic_cache_callback = callback
                        debug_logger.log_event("create_coding_subagent_found_cache_callback")
            
            # Add parent callbacks if found, otherwise create new ones
            if message_cleanup_callback:
                new_subagent.add_callback(message_cleanup_callback)
                debug_logger.log_event("create_coding_subagent_added_parent_cleanup_hook")
            else:
                new_subagent.add_callback(MessageCleanupHook())
                debug_logger.log_event("create_coding_subagent_added_new_cleanup_hook")
                
            if anthropic_cache_callback:
                new_subagent.add_callback(anthropic_cache_callback)
                debug_logger.log_event("create_coding_subagent_added_parent_cache")
            else:
                new_subagent.add_callback(AnthropicPromptCacheCallback())
                debug_logger.log_event("create_coding_subagent_added_new_cache")
            
            # CRITICAL FIX: Add UI callback for tool usage tracking if available (inherits from main agent)
            if self.ui_callback:
                try:
                    from .fancy_ui.callbacks.textual_tool_callback import create_textual_tool_callback
                    subagent_tool_callback = create_textual_tool_callback(
                        logger=self.debug_logger,
                        ui_update_callback=self.ui_callback,  # Same UI callback as main agent
                        max_events=100,
                        agent_level=1,  # Subagent is level 1 (main agent is level 0)
                        agent_id="direct_subagent",
                        parent_id="main_agent",
                        display_name="Direct Coding Subagent"
                    )
                    new_subagent.add_callback(subagent_tool_callback)
                    debug_logger.log_event("create_coding_subagent_added_ui_callback")
                except Exception as e:
                    self.console.print(f"[yellow]⚠️ Could not add UI callback to subagent: {e}[/yellow]")
                    debug_logger.log_error("create_coding_subagent_ui_callback_failed", e)
            
            # CRITICAL FIX: Add TokenTracker for cost monitoring (inherits from main agent)
            try:
                # Get parent tracker from main agent if available
                parent_tracker = None
                if self.agent and hasattr(self.agent, 'callbacks'):
                    for callback in self.agent.callbacks:
                        if hasattr(callback, 'get_total_usage'):  # TokenTracker has this method
                            parent_tracker = callback
                            break
                
                # Create child tracker for subagent
                if parent_tracker:
                    child_tracker = create_token_tracker(
                        name="direct_subagent",
                        parent_tracker=parent_tracker,
                        enable_detailed_logging=True
                    )
                    new_subagent.add_callback(child_tracker)
                    debug_logger.log_event("create_coding_subagent_added_child_tracker")
                else:
                    # Create standalone tracker if no parent available
                    standalone_tracker = create_token_tracker(
                        name="direct_subagent",
                        enable_detailed_logging=True
                    )
                    new_subagent.add_callback(standalone_tracker)
                    debug_logger.log_event("create_coding_subagent_added_standalone_tracker")
                    
            except Exception as e:
                self.console.print(f"[yellow]⚠️ Could not add token tracking to subagent: {e}[/yellow]")
                debug_logger.log_error("create_coding_subagent_tracker_failed", e)
            
            # CRITICAL FIX: Never store subagent for reuse - always create fresh instances
            # This ensures each subagent call gets unique session and storage context
            # Log completion of callback setup
            callback_count = len(new_subagent.callbacks) if hasattr(new_subagent, 'callbacks') else 0
            debug_logger.log_event("create_coding_subagent_complete", 
                                 callback_count=callback_count,
                                 cleanup_hook="from_parent" if message_cleanup_callback else "new_instance",
                                 cache_callback="from_parent" if anthropic_cache_callback else "new_instance",
                                 storage_enabled=self.storage_manager is not None,
                                 ui_tracking_enabled=self.ui_callback is not None,
                                 cost_tracking_enabled=callback_count > 2)
            
            return new_subagent
            
        except Exception as e:
            self.console.print(f"[yellow]⚠️ Could not create coding subagent: {e}[/yellow]")
            import traceback
            debug_logger.log_error("create_coding_subagent_failed", e, traceback=traceback.format_exc())
            return None
    
    def _get_subagent_system_prompt(self, agent_config=None) -> str:
        """Get specialized system prompt for the coding subagent."""
        # Use dedicated subagent system prompt
        system_prompt, source = self._get_system_prompt(agent_config, is_subagent=True)
        self.debug_logger.info(f"Subagent system prompt selected from {source}")
        return system_prompt
    

    async def initialize_agent(self):
        """Initialize TinyCodeAgent if not already done."""
        if self.agent is not None:
            return
        
        # Validate model configuration before initializing
        if not self.config_manager.is_model_configured():
            status = self.config_manager.validate_model_setup()
            self.console.print("[bold yellow]⚠️ Model Configuration Required[/bold yellow]")
            self.console.print(f"Current model: {status['model_name']} ({status['provider']})")
            self.console.print(f"API key: {'Available' if status['has_api_key'] else 'Missing'}")
            self.console.print("\nUse '/model' command to configure your AI model and API key")
            return
            
        try:
            # Import TinyCodeAgent (this requires the tinyagent package)
            from tinyagent import TinyCodeAgent
            from tinyagent.hooks import MessageCleanupHook
            from tinyagent.hooks.token_tracker import TokenTracker, create_token_tracker
            from tinyagent.tools import create_coding_subagent
            from tinyagent import SubagentConfig
            from tinyagent.hooks import AnthropicPromptCacheCallback


            
            import tinyagent
            
            # Check tinyagent version for compatibility
            tinyagent_version = getattr(tinyagent, '__version__', 'unknown')
            if tinyagent_version != 'unknown':
                debug_logger.log_event("tinyagent_version", version=tinyagent_version)
            
            # Get configuration
            config = self.config_manager.load_config()
            agent_config = config.agent_config
            
            # Get API key for the configured model
            api_key = self.config_manager.get_model_api_key()
            if not api_key:
                expected_env_var = self._get_expected_env_var(agent_config.provider)
                raise ValueError(f"API key not found. Set {expected_env_var} environment variable or use /model command")
            
            # Determine execution provider based on system and user preference
            use_seatbelt = self._should_use_seatbelt()
            
            # Get system prompt using SystemPromptManager
            system_prompt, prompt_source = self._get_system_prompt(agent_config)
            
            # Prepare TinyCodeAgent parameters
            model_name = self._construct_model_name(agent_config)
            tiny_agent_params = {
                "model": model_name,
                "api_key": api_key,
                # Pass the system prompt from SystemPromptManager
                "system_prompt": system_prompt,
                "enable_python_tool": False,
                "enable_shell_tool": True,
                "enable_file_tools": True,  # Enable file tools (read_file, write_file, update_file, glob_tool, grep_tool)
                "enable_todo_write": True,  # Enable TodoWrite tool for task management
                "local_execution": True,  # Execute locally for safety
                "temperature": agent_config.temperature,
                "default_workdir": str(self.config_manager.workdir),  # Set working directory
                "log_manager": self.log_manager,
                # TinyCodeAgent has its own custom instruction handling
                # Pass configuration for TinyCodeAgent's custom instruction system  
                "enable_custom_instructions": self.enable_custom_instructions,  # TinyCodeAgent uses plural form
                # Pass absolute path to AGENTS.md if custom instructions are enabled
                "custom_instructions": str(self.config_manager.workdir / "AGENTS.md") if self.enable_custom_instructions else None,
                "custom_instruction_config": {
                    "auto_detect_agents_md": True,  # Enable auto-detection
                    "execution_directory": str(self.config_manager.workdir),  # Where to look for AGENTS.md
                    "custom_filename": "AGENTS.md"  # Filename to look for
                } if self.enable_custom_instructions else {}
            }
            
            # Add storage parameters if storage manager is available
            if self.storage_manager:
                self.storage_manager._initialize_storage()
                if self.storage_manager.storage:
                    # CRITICAL: Validate user_id before passing to TinyAgent
                    if self.storage_manager.user_id is None:
                        raise ValueError("CRITICAL ERROR: storage_manager.user_id is None when initializing TinyAgent!")
                    
                    if self.storage_manager.current_session_id is None:
                        raise ValueError("CRITICAL ERROR: storage_manager.current_session_id is None when initializing TinyAgent!")
                    
                    storage_params = {
                        "storage": self.storage_manager.storage,
                        "session_id": self.storage_manager.current_session_id,
                        "user_id": self.storage_manager.user_id
                    }
                    
                    # Additional validation
                    assert storage_params["user_id"] is not None, "user_id must not be None"
                    assert storage_params["session_id"] is not None, "session_id must not be None"
                    
                    tiny_agent_params.update(storage_params)
                    debug_logger.log_event("initialize_agent_storage_params",
                                         session_id=self.storage_manager.current_session_id,
                                         user_id=self.storage_manager.user_id)
            
            # Configure execution provider
            if use_seatbelt:
                tiny_agent_params["provider"] = "seatbelt"
                debug_logger.log_event("using_seatbelt_sandbox")
            else:
                tiny_agent_params["provider"] = "modal"
                tiny_agent_params["local_execution"] = True
                debug_logger.log_event("using_local_execution")
            
            # Add max_tokens if specified
            if agent_config.max_tokens:
                tiny_agent_params["max_tokens"] = agent_config.max_tokens
            
            # Add custom base URL if specified
            if agent_config.custom_base_url:
                tiny_agent_params["base_url"] = agent_config.custom_base_url
            
            # Add custom parameters
            if agent_config.custom_params:
                tiny_agent_params.update(agent_config.custom_params)
            
            # Add model_kwargs from configuration (excluding juno_config)
            if agent_config.model_kwargs:
                if "model_kwargs" not in tiny_agent_params:
                    tiny_agent_params["model_kwargs"] = {}
                
                # Create a copy of model_kwargs and remove juno_config before passing to TinyAgent
                model_kwargs_copy = agent_config.model_kwargs.copy()
                juno_config_removed = model_kwargs_copy.pop("juno_config", None)
                
                tiny_agent_params["model_kwargs"].update(model_kwargs_copy)
                debug_logger.log_event("initialize_agent_model_kwargs", 
                                     kwargs=model_kwargs_copy, 
                                     juno_config_removed=bool(juno_config_removed))
            
            # Configure Phoenix tracing if enabled via environment variable
            if os.getenv("JUNO_TRACING_ENABLED") == "1":
                debug_logger.log_event("enabling_phoenix_tracing")
                # Set OpenTelemetry service name for better trace identification
                if "OTEL_SERVICE_NAME" not in os.environ:
                    os.environ["OTEL_SERVICE_NAME"] = "juno-agent-tinyagent"
                debug_logger.log_event("phoenix_tracing_configured", 
                                     service_name=os.getenv("OTEL_SERVICE_NAME"),
                                     traces_exporter=os.getenv("OTEL_TRACES_EXPORTER"),
                                     juno_tracing_enabled=True)
            
            # Initialize TinyCodeAgent with configured model
            self.agent = TinyCodeAgent(**tiny_agent_params)
            
            # CRITICAL: Store the intended user_id before init_async() which might change it
            intended_user_id = self.storage_manager.user_id if self.storage_manager else None
            intended_session_id = self.storage_manager.current_session_id if self.storage_manager else None
            
            # Attach storage to agent BEFORE init_async() so it's available during initialization
            if self.storage_manager:
                debug_logger.log_event("attaching_storage_to_agent")
                self.storage_manager.attach_to_agent(self.agent)
            
            # CRITICAL: Initialize the agent to load any existing session from storage
            # This is essential for loading previous conversations when session_id and user_id are provided
            await self.agent.init_async()
            
            # CRITICAL FIX: Ensure user_id and session_id are restored after init_async()
            # TinyAgent's init_async() sometimes overwrites the user_id/session_id we provided
            if intended_user_id and hasattr(self.agent, 'user_id'):
                if self.agent.user_id != intended_user_id:
                    debug_logger.log_event("restoring_user_id_after_init_async", 
                                         original=self.agent.user_id, 
                                         intended=intended_user_id)
                    self.agent.user_id = intended_user_id
            
            if intended_session_id and hasattr(self.agent, 'session_id'):
                if self.agent.session_id != intended_session_id:
                    debug_logger.log_event("restoring_session_id_after_init_async", 
                                         original=self.agent.session_id, 
                                         intended=intended_session_id)
                    self.agent.session_id = intended_session_id
            
            # Debug logging for session initialization
            agent_session_id = getattr(self.agent, 'session_id', 'None')
            agent_user_id = getattr(self.agent, 'user_id', 'None')
            agent_messages = []
            
            # Try to get message count from the agent
            try:
                if hasattr(self.agent, 'messages') and self.agent.messages:
                    agent_messages = self.agent.messages
                elif hasattr(self.agent, 'conversation') and hasattr(self.agent.conversation, 'messages'):
                    agent_messages = self.agent.conversation.messages
                elif hasattr(self.agent, '_conversation') and hasattr(self.agent._conversation, 'messages'):
                    agent_messages = self.agent._conversation.messages
                
                message_count = len(agent_messages) if agent_messages else 0
            except Exception as e:
                message_count = -1  # Indicates error getting count
                debug_logger.log_error("initialize_agent_message_count_failed", e)
            
            # Log comprehensive initialization details
            self.debug_logger.info("agent_initialized", 
                                 agent_session_id=agent_session_id,
                                 agent_user_id=agent_user_id, 
                                 message_count=message_count,
                                 storage_session_id=self.storage_manager.current_session_id if self.storage_manager else 'None',
                                 storage_user_id=self.storage_manager.user_id if self.storage_manager else 'None',
                                 agent_type=type(self.agent).__name__,
                                 agent_id=hex(id(self.agent)))
            
            debug_logger.log_event("initialize_agent_complete",
                                 session_id=agent_session_id,
                                 user_id=agent_user_id,
                                 message_count=message_count)
            
            # Additional validation logging
            if self.storage_manager:
                session_match = agent_session_id == self.storage_manager.current_session_id
                user_match = agent_user_id == self.storage_manager.user_id
                self.debug_logger.info("agent_session_validation",
                                     session_id_match=session_match,
                                     user_id_match=user_match,
                                     expected_session_id=self.storage_manager.current_session_id,
                                     expected_user_id=self.storage_manager.user_id,
                                     actual_session_id=agent_session_id,
                                     actual_user_id=agent_user_id)
            
            self.agent.add_callback(MessageCleanupHook())
            parent_tracker = None
            # Add cache callback for Anthropic models, to cache prompts
            self.agent.add_callback(AnthropicPromptCacheCallback())
            
            # CRITICAL: Validate that TinyAgent received the user_id correctly
            if self.storage_manager:
                agent_user_id = getattr(self.agent, 'user_id', None)
                agent_session_id = getattr(self.agent, 'session_id', None)
                
                debug_logger.log_event("initialize_agent_created", user_id=agent_user_id, session_id=agent_session_id)
                
                if agent_user_id != self.storage_manager.user_id:
                    debug_logger.log_event("agent_user_id_mismatch_fixed", 
                                         expected=self.storage_manager.user_id, 
                                         got=agent_user_id)
                    # This should now be resolved by the fix above, but log for debugging
                
                if agent_user_id is None:
                    print(f"[ERROR] initialize_agent: CRITICAL - Agent user_id is None!")
                else:
                    debug_logger.log_event("initialize_agent_user_validation", user_id=agent_user_id)
            
            # Check storage integration
            if self.storage_manager and hasattr(self.agent, 'storage') and self.agent.storage:
                debug_logger.log_event("initialize_agent_storage_integrated", storage_type=type(self.agent.storage).__name__)
                debug_logger.log_event("conversation_storage_enabled")
            elif self.storage_manager:
                debug_logger.log_event("initialize_agent_storage_not_attached")
                self.console.print("[yellow]⚠️ Storage not fully integrated[/yellow]")
            else:
                debug_logger.log_event("initialize_agent_no_storage")
            
            # Add tool callback for UI tool usage tracking
            # Use SimpleUIToolCallback for direct console output, TextualToolCallback for Textual UI
            debug_logger.log_event("creating_tool_callback",
                                 agent_id=hex(id(self.agent)),
                                 ui_callback_available=self.ui_callback is not None,
                                 console_available=self.console is not None)
            main_tool_callback = None  # Store for subagent hierarchy
            
            # Detect UI mode based on original console parameter and ui_callback
            # Simple UI: console provided (not None) AND ui_callback is None
            # Fancy UI (Textual): console is None (explicitly passed) OR ui_callback provided
            # 
            # Key insight: Fancy UI passes console=None, Simple UI passes a console object
            use_simple_ui = (
                self._original_console is not None and 
                self.ui_callback is None
            )
            
            try:
                if use_simple_ui:
                    # Use SimpleUIToolCallback for direct Rich console output
                    from .simple_ui_tool_callback import create_simple_ui_tool_callback
                    main_tool_callback = create_simple_ui_tool_callback(
                        console=self.console,
                        logger=self.debug_logger,
                        max_result_length=200,
                        show_arguments=True,
                        show_results=True,
                        agent_level=0,  # Main agent is level 0
                        agent_id="main_agent",
                        display_name="Main Agent"
                    )
                    debug_logger.log_event("simple_ui_tool_callback_created",
                                         callback_id=hex(id(main_tool_callback)),
                                         agent_level=0,
                                         agent_id="main_agent")
                else:
                    # Use TextualToolCallback for Textual UI integration
                    from .fancy_ui.callbacks.textual_tool_callback import create_textual_tool_callback
                    main_tool_callback = create_textual_tool_callback(
                        logger=self.debug_logger,
                        ui_update_callback=self.ui_callback,
                        max_events=100,
                        agent_level=0,  # Main agent is level 0
                        agent_id="main_agent",
                        display_name="Main Agent"
                    )
                    debug_logger.log_event("textual_tool_callback_created",
                                         callback_id=hex(id(main_tool_callback)),
                                         ui_callback_id=hex(id(self.ui_callback)) if self.ui_callback else None,
                                         agent_level=0,
                                         agent_id="main_agent")
                
                self.agent.add_callback(main_tool_callback)
                debug_logger.log_event("tool_callback_added_to_agent",
                                     agent_id=hex(id(self.agent)),
                                     callback_id=hex(id(main_tool_callback)),
                                     callback_type="SimpleUI" if use_simple_ui else "Textual",
                                     total_callbacks=len(self.agent.callbacks))
                
                debug_logger.log_event("tool_tracking_enabled_main_agent", 
                                     callback_type="SimpleUI" if use_simple_ui else "Textual")
            except Exception as e:
                self.console.print(f"[yellow]⚠️ Could not enable tool usage tracking: {e}[/yellow]")
                self.debug_logger.error("Failed to create tool usage callback", error=str(e))
                debug_logger.log_error("tool_callback_creation_failed", e,
                                     ui_callback_available=self.ui_callback is not None,
                                     use_simple_ui=use_simple_ui)
            # Add TokenTracker for cost monitoring
            self.debug_logger.info("Initializing parent token tracker for main agent")
            try:
                parent_tracker = create_token_tracker(
                    name="main_agent",
                    enable_detailed_logging=True
                )
                self.agent.add_callback(parent_tracker)
                self.token_tracker = parent_tracker  # Store reference for UI access
                debug_logger.log_event("cost_tracking_enabled")
                self.debug_logger.info("Parent token tracker successfully created and added to main agent", 
                                     tracker_type=type(parent_tracker).__name__, 
                                     tracker_id=id(parent_tracker))
            except Exception as e:
                self.console.print(f"[yellow]⚠️ Could not enable cost tracking: {e}[/yellow]")
                self.debug_logger.error("Failed to create parent token tracker", error=str(e))
                parent_tracker = None
            # Create and add coding subagent tool using TinyCodeAgent.as_tool()
            
            try:
                from textwrap import dedent
                
                
                # Create child tracker (for subagent) - only if parent tracker was created successfully
                child_tracker = None
                self.debug_logger.info("Attempting to create child token tracker for subagent", 
                                     parent_available=parent_tracker is not None)
                if parent_tracker is not None:
                    try:
                        child_tracker = create_token_tracker(
                            name="subagent",
                            parent_tracker=parent_tracker,  # Link to parent
                            enable_detailed_logging=True
                        )
                        self.debug_logger.info("Child token tracker successfully created", 
                                             tracker_type=type(child_tracker).__name__, 
                                             tracker_id=id(child_tracker),
                                             parent_id=id(parent_tracker))
                    except Exception as e:
                        self.console.print(f"[yellow]⚠️ Could not create child token tracker: {e}[/yellow]")
                        self.debug_logger.error("Failed to create child token tracker", error=str(e), parent_id=id(parent_tracker))
                        child_tracker = None
                else:
                    self.debug_logger.warning("Skipping child token tracker creation - no parent tracker available")
                
                coding_tool_description = dedent("""
                        Launch a new agent with empty history that has access to the following tools: Bash, Apply Patch.
                        
                        Agent doesn't know anything about the main agent, and anything it needs to know should be provided in the prompt.
                        Launch Agent to give it a sub-task with defined scope.
                        
                        Usage notes:
                            1. Launch multiple agents concurrently whenever possible, to maximize performance; to do that, use a single message with multiple tool uses
                            2. When the agent is done, it will return a single message back to you. The result returned by the agent is not visible to the user. To show the user the result, you should send a text message back to the user with a concise summary of the result.
                            3. Each agent invocation is stateless. You will not be able to send additional messages to the agent, nor will the agent be able to communicate with you outside of its final report. Therefore, your prompt should contain a highly detailed task description for the agent to perform autonomously and you should specify exactly what information the agent should return back to you in its final and only message to you.
                            4. The agents outputs should generally be trusted
                            5. Clearly tell the agent whether you expect it to perform. Research for implementation details, extract API Doc, write code using path tool, etc, since it is not aware of the user's intent
                        
                        Args:
                        - prompt: str: Detailed and concise prompt for the sub-agent task. It should include every details and requirement for the task.
                        - absolute_workdir: str: The absolute path to the workdir of the sub-agent.
                        - description: str: A clear, concise description of what this command does in 5-10 words. User will see the description on the UI, and help them understand what you want to achieve.
                        
                        Returns:
                        - str: The result of the task. The result is not visible to the user
                        """).strip()
                
                # Use from_parent_agent to inherit parent callbacks, then override specific settings
                parent_callbacks = list(self.agent.callbacks) if hasattr(self.agent.callbacks, '__iter__') and not isinstance(self.agent.callbacks, str) else []
                
                # IMPORTANT: Create hierarchy-aware tool callback for subagent
                subagent_tool_callback = None
                if main_tool_callback and self.ui_callback:
                    try:
                        debug_logger.log_event("creating_subagent_tool_callback",
                                             parent_callback_id=hex(id(main_tool_callback)))
                        subagent_tool_callback = create_textual_tool_callback(
                            logger=self.debug_logger,
                            ui_update_callback=self.ui_callback,  # Same UI callback
                            max_events=100,
                            agent_level=1,  # Subagent is level 1
                            agent_id="subagent_coding",
                            parent_id="main_agent",
                            display_name="Coding Subagent"
                        )
                        debug_logger.log_event("subagent_tool_callback_created",
                                             callback_id=hex(id(subagent_tool_callback)),
                                             parent_id="main_agent",
                                             agent_level=1)
                        debug_logger.log_event("tool_tracking_enabled_subagent")
                    except Exception as e:
                        self.console.print(f"[yellow]⚠️ Could not create subagent tool callback: {e}[/yellow]")
                        debug_logger.log_error("subagent_tool_callback_creation_failed", e)
                
                # Build subagent callbacks list - include essential parent callbacks
                subagent_callbacks = []
                
                # CRITICAL FIX: Add MessageCleanupHook and AnthropicPromptCacheCallback from parent
                message_cleanup_callback = None
                anthropic_cache_callback = None
                
                # Extract essential callbacks from parent
                for callback in parent_callbacks:
                    callback_type = type(callback).__name__
                    
                    # Include MessageCleanupHook from parent
                    if callback_type == 'MessageCleanupHook':
                        message_cleanup_callback = callback
                        subagent_callbacks.append(callback)
                        self.debug_logger.info("Added parent MessageCleanupHook to subagent tool callbacks")
                    
                    # Include AnthropicPromptCacheCallback from parent
                    elif callback_type == 'AnthropicPromptCacheCallback':
                        anthropic_cache_callback = callback
                        subagent_callbacks.append(callback)
                        self.debug_logger.info("Added parent AnthropicPromptCacheCallback to subagent tool callbacks")
                
                # Add new instances if parent callbacks not found
                if not message_cleanup_callback:
                    from tinyagent.hooks import MessageCleanupHook
                    subagent_callbacks.append(MessageCleanupHook())
                    self.debug_logger.info("Added new MessageCleanupHook to subagent tool callbacks (parent not found)")
                
                if not anthropic_cache_callback:
                    from tinyagent.hooks import AnthropicPromptCacheCallback
                    subagent_callbacks.append(AnthropicPromptCacheCallback())
                    self.debug_logger.info("Added new AnthropicPromptCacheCallback to subagent tool callbacks (parent not found)")
                
                # Add child-specific callbacks
                if child_tracker:
                    subagent_callbacks.append(child_tracker)
                if subagent_tool_callback:
                    subagent_callbacks.append(subagent_tool_callback)
                
                # CRITICAL FIX: Debug model propagation for SubagentConfig
                parent_model = getattr(self.agent, 'model', None) if self.agent else None
                # Use consistent model construction for fallback
                fallback_model = self._construct_model_name(agent_config)
                subagent_model = parent_model if parent_model else fallback_model
                debug_logger.log_event("subagent_config_models", parent=parent_model, subagent=subagent_model)
                if parent_model and parent_model != subagent_model:
                    print(f"[WARNING] SubagentConfig: Model mismatch detected! Parent: {parent_model}, Subagent: {subagent_model}")
                else:
                    debug_logger.log_event("subagent_config_model_consistency_verified")
                
                self.debug_logger.info("Creating SubagentConfig with callbacks", 
                                     parent_callbacks_count=len(parent_callbacks),
                                     child_tracker_available=child_tracker is not None,
                                     child_tracker_id=id(child_tracker) if child_tracker else None,
                                     subagent_tool_callback_available=subagent_tool_callback is not None,
                                     total_subagent_callbacks=len(subagent_callbacks),
                                     has_message_cleanup=message_cleanup_callback is not None,
                                     has_anthropic_cache=anthropic_cache_callback is not None,
                                     parent_model=parent_model,
                                     subagent_model=subagent_model)
                
                # CRITICAL FIX: Add storage parameters for SubagentConfig
                subagent_kwargs = {
                    "parent_agent": self.agent,
                    "model": subagent_model,
                    "api_key": api_key,
                    "system_prompt": self._get_subagent_system_prompt(agent_config),
                    "enable_python_tool": False,
                    "enable_shell_tool": True,
                    "enable_file_tools": True,  # Enable file tools for subagent
                    "enable_todo_write": True,  # Enable TodoWrite tool for subagent
                    "local_execution": tiny_agent_params["local_execution"],
                    "provider": tiny_agent_params["provider"],
                    "temperature": agent_config.temperature,
                    "default_workdir": str(self.config_manager.workdir),
                    "callbacks": subagent_callbacks,
                    "inherit_parent_hooks": False  # Don't inherit parent hooks to avoid duplication
                }
                
                # Add storage parameters to subagent_kwargs if available
                if self.storage_manager and self.storage_manager.storage:
                    # Create unique session ID for each SubagentConfig call
                    subagent_session_id = str(uuid.uuid4()) + "_subagent_tool"
                    subagent_user_id = self.storage_manager.user_id + "_subagent"
                    
                    subagent_kwargs.update({
                        "storage": self.storage_manager.storage,
                        "session_id": subagent_session_id,
                        "user_id": subagent_user_id
                    })
                    debug_logger.log_event("subagent_config_storage", session_id=subagent_session_id, user_id=subagent_user_id)
                
                # Add model_kwargs from configuration (inherit from main agent, excluding juno_config)
                if agent_config.model_kwargs:
                    if "model_kwargs" not in subagent_kwargs:
                        subagent_kwargs["model_kwargs"] = {}
                    
                    # Create a copy of model_kwargs and remove juno_config before passing to TinyAgent
                    model_kwargs_copy = agent_config.model_kwargs.copy()
                    juno_config_removed = model_kwargs_copy.pop("juno_config", None)
                    
                    subagent_kwargs["model_kwargs"].update(model_kwargs_copy)
                    debug_logger.log_event("subagent_config_model_kwargs", 
                                         kwargs=model_kwargs_copy,
                                         juno_config_removed=bool(juno_config_removed))
                
                subagent_config = SubagentConfig.from_parent_agent(**subagent_kwargs)
                
                self.debug_logger.debug("SubagentConfig created successfully", 
                                      config_callbacks=len(subagent_config.callbacks) if hasattr(subagent_config, 'callbacks') else 'unknown')


                # Create the coding subagent tool
                self.debug_logger.info("Creating coding subagent tool with callbacks")
                
                # Log the config being passed to subagent
                agent_kwargs = subagent_config.to_agent_kwargs()
                self.debug_logger.debug("Subagent config kwargs", 
                                      kwargs_keys=list(agent_kwargs.keys()),
                                      has_callbacks=('callbacks' in agent_kwargs),
                                      callback_count=len(agent_kwargs.get('callbacks', [])))
                
                # DEBUG: Log each callback in detail
                if 'callbacks' in agent_kwargs:
                    for i, cb in enumerate(agent_kwargs['callbacks']):
                        cb_type = type(cb).__name__
                        cb_id = hex(id(cb))
                        self.debug_logger.debug(f"Callback[{i}]: {cb_type} @ {cb_id}")
                        debug_logger.log_event("subagent_callback_detail",
                                             index=i,
                                             callback_type=cb_type,
                                             callback_id=cb_id,
                                             is_textual_tool=cb_type == "TextualToolCallback",
                                             is_token_tracker=cb_type == "TokenTracker")
                
                # CRITICAL: Manually ensure callbacks are included if missing
                if 'callbacks' not in agent_kwargs:
                    self.debug_logger.warning("CRITICAL: callbacks missing from agent_kwargs, manually adding")
                    agent_kwargs['callbacks'] = subagent_callbacks
                    self.debug_logger.debug("Updated agent_kwargs", 
                                          has_callbacks_now=True,
                                          callback_count_now=len(agent_kwargs['callbacks']))
                
                # DEBUG: Log what we're passing to create_coding_subagent
                debug_logger.log_event("calling_create_coding_subagent",
                                     name='subAgent',
                                     has_callbacks='callbacks' in agent_kwargs,
                                     callback_count=len(agent_kwargs.get('callbacks', [])),
                                     kwargs_keys=list(agent_kwargs.keys()))
                
                coding_subagent_tool = create_coding_subagent(
                    name='subAgent',
                    description=coding_tool_description,
                    **agent_kwargs  # Clean, validated parameters
                )

                if coding_subagent_tool:
                    # Add the subagent tool to the main agent
                    self.agent.add_tool(coding_subagent_tool)
                    
                    # CRITICAL FIX: Validate SubagentConfig model propagation (debugging)
                    debug_logger.log_event("subagent_config_tool_model_validation")
                    if hasattr(coding_subagent_tool, '_config') and hasattr(coding_subagent_tool._config, 'model'):
                        tool_model = coding_subagent_tool._config.model
                        debug_logger.log_event("subagent_config_tool_model", model=tool_model)
                        if parent_model and tool_model != parent_model:
                            print(f"[ERROR] SubagentConfig tool: CRITICAL MODEL MISMATCH! Expected: {parent_model}, Got: {tool_model}")
                        else:
                            debug_logger.log_event("subagent_config_tool_consistency_verified")
                    
                    self.debug_logger.info("Coding subagent tool successfully added to main agent")
                    
                    # CRITICAL FIX: Always create fresh subagent tools for session isolation
                    debug_logger.log_event("coding_subagent_tool_added")
                    
                    # Add debugging info about token tracking
                    if child_tracker:
                        debug_logger.log_event("subagent_token_tracking_configured")
                        self.debug_logger.info("Token tracking fully configured with dedicated child tracker", 
                                             parent_tracker_id=id(parent_tracker), 
                                             child_tracker_id=id(child_tracker),
                                             child_tracker_linked_to_parent=True)
                    elif parent_tracker:
                        debug_logger.log_event("subagent_partial_token_tracking")
                        self.debug_logger.warning("Partial token tracking - parent only", parent_tracker_id=id(parent_tracker))
                    else:
                        debug_logger.log_event("subagent_no_token_tracking")
                        self.debug_logger.warning("No token tracking available for subagent")
                else:
                    self.console.print("[yellow]⚠️ Failed to create coding subagent tool[/yellow]")
                    self.debug_logger.error("Failed to create coding subagent tool")
                    
            except Exception as e:
                self.console.print(f"[yellow]⚠️ Could not add coding subagent tool: {e}[/yellow]")
                import traceback
                debug_logger.log_error("subagent_creation_traceback", None, traceback=traceback.format_exc())
            

            
            self.console.print(f"[green]✅ Juno Agent initialized with {agent_config.model_name} ({agent_config.provider})![/green]")
            
        except ImportError as e:
            self.console.print(f"[red]❌ TinyAgent package not available. Install with: pip install tinyagent-py[all][/red]")
            self.console.print(f"[red]Error: {e}[/red]")
            self.agent = None
        except Exception as e:
            self.console.print(f"[red]❌ Failed to initialize TinyCodeAgent: {e}[/red]")
            self.console.print("[yellow]💡 Try using /model command to configure your AI model and API key[/yellow]")
            self.agent = None
    
    def _get_expected_env_var(self, provider: str) -> str:
        """Get expected environment variable name for a provider."""
        provider_lower = provider.lower()
        if provider_lower == "openai":
            return "OPENAI_API_KEY"
        elif provider_lower == "anthropic":
            return "ANTHROPIC_API_KEY"
        elif provider_lower == "google":
            return "GOOGLE_API_KEY"
        elif provider_lower == "azure":
            return "AZURE_OPENAI_API_KEY"
        elif provider_lower == "cohere":
            return "COHERE_API_KEY"
        elif provider_lower == "huggingface":
            return "HUGGINGFACE_API_KEY"
        elif provider_lower == "groq":
            return "GROQ_API_KEY"
        else:
            return f"{provider.upper()}_API_KEY"
    
    def _should_use_seatbelt(self) -> bool:
        """Determine if seatbelt provider should be used."""
        # Only available on macOS
        if platform.system() != "Darwin":
            return False
        
        try:
            # Check if TinyCodeAgent supports seatbelt
            from tinyagent import TinyCodeAgent
            if hasattr(TinyCodeAgent, 'is_seatbelt_supported'):
                return TinyCodeAgent.is_seatbelt_supported()
            else:
                # Fallback: check for sandbox-exec command
                import shutil
                return shutil.which("sandbox-exec") is not None
        except ImportError:
            return False
    
    def _get_system_prompt(self, agent_config=None, is_subagent=False) -> tuple[str, str]:
        """
        Get system prompt for TinyCodeAgent using SystemPromptManager.
        
        Args:
            agent_config: AgentConfig object with model information
            is_subagent: Whether this is for a subagent (affects prompt selection)
            
        Returns:
            Tuple of (system_prompt, source_description)
        """
        if agent_config is None:
            config = self.config_manager.load_config()
            agent_config = config.agent_config
            
        # Extract juno_config from model_kwargs if present
        juno_config = {}
        if agent_config.model_kwargs and "juno_config" in agent_config.model_kwargs:
            juno_config = agent_config.model_kwargs["juno_config"].copy()
            
            # Add reasoning effort context for GPT-5 models
            if "reasoning" in agent_config.model_kwargs:
                reasoning_effort = agent_config.model_kwargs["reasoning"].get("effort", "default")
                juno_config["reasoning_effort"] = reasoning_effort
            elif "reasoning_effort" in agent_config.model_kwargs:
                juno_config["reasoning_effort"] = agent_config.model_kwargs["reasoning_effort"]
        
        # Use model_slug if available, otherwise fallback to model_name
        model_identifier = agent_config.model_slug or agent_config.model_name
        
        # Get system prompt using SystemPromptManager
        system_prompt, source = self.system_prompt_manager.get_system_prompt(
            model_slug=model_identifier,
            juno_config=juno_config,
            is_subagent=is_subagent
        )
        
        # Log the selected system prompt source
        self.debug_logger.info(f"System prompt selected from {source}",
                               model_slug=model_identifier,
                               juno_config_present=bool(juno_config),
                               prompt_length=len(system_prompt))
        
        return system_prompt, source
    
    async def process_chat_message(self, message: str, context: Optional[Dict] = None) -> str:
        """Process a chat message using TinyCodeAgent."""
        # Initialize agent if needed
        await self.initialize_agent()
        
        # Preprocess message to detect potential binary file issues
        processed_message = self._preprocess_message_for_binary_files(message)
        
        debug_logger.log_event("process_chat_message_start",
                             message_preview=message[:50] + "...",
                             agent_available=self.agent is not None)
        if self.agent and hasattr(self.agent, 'storage'):
            debug_logger.log_event("process_chat_message_agent_info",
                                 has_storage=self.agent.storage is not None,
                                 storage_type=type(self.agent.storage).__name__ if self.agent.storage else None)
        
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "role": "user",
            "content": message,
            "context": context or {}
        })
        
        if self.agent is None:
            # Fallback to simple response if agent not available
            response = await self._fallback_response(processed_message, context)
        else:
            # Use TinyCodeAgent
            # Only show progress indicator if NOT in simple UI mode
            # Simple UI (ui.py) has its own progress handling
            show_progress = not (self._original_console is not None and self.ui_callback is None)
            
            try:
                # Get max_turns from config
                config = self.config_manager.load_config()
                max_turns = config.agent_config.max_turns
                
                # Log agent state before running
                self.debug_logger.info("Running agent with message", 
                                     callback_count=len(self.agent.callbacks) if hasattr(self.agent, 'callbacks') else 0,
                                     max_turns=max_turns)
                
                # Log callback details
                if hasattr(self.agent, 'callbacks'):
                    for i, callback in enumerate(self.agent.callbacks):
                        callback_type = type(callback).__name__
                        self.debug_logger.debug(f"Callback {i}: {callback_type}", 
                                              callback_id=id(callback),
                                              has_get_total_usage=hasattr(callback, 'get_total_usage'))
                
                # Show progress only for fancy UI and headless mode
                if show_progress:
                    # For fancy UI and headless mode, show progress
                    with Progress(
                        SpinnerColumn(),
                        TextColumn("[progress.description]{task.description}"),
                        console=self.console,
                        transient=True,
                    ) as progress:
                        progress.add_task("🤖 Processing with TinyCodeAgent...", total=None)
                        
                        # Run the agent with the user's message and max_turns
                        debug_logger.log_event("process_chat_message_before_run",
                                             has_storage=hasattr(self.agent, 'storage') and self.agent.storage is not None)
                        
                        response = await self.agent.run(processed_message, max_turns=max_turns)
                        
                        debug_logger.log_event("process_chat_message_after_run",
                                             has_storage=hasattr(self.agent, 'storage') and self.agent.storage is not None)
                else:
                    # For simple UI, no progress indicator (ui.py handles it)
                    debug_logger.log_event("process_chat_message_before_run",
                                         has_storage=hasattr(self.agent, 'storage') and self.agent.storage is not None)
                    
                    response = await self.agent.run(processed_message, max_turns=max_turns)
                    
                    debug_logger.log_event("process_chat_message_after_run",
                                         has_storage=hasattr(self.agent, 'storage') and self.agent.storage is not None)
                
                # Log agent state after running
                self.debug_logger.info("Agent run completed", 
                                     callback_count=len(self.agent.callbacks) if hasattr(self.agent, 'callbacks') else 0)
            except UnicodeDecodeError as e:
                # Special handling for binary file read attempts
                response = "❌ **Binary File Error**: It looks like you tried to read a binary file (like PNG, JPG, PDF, etc.) as text.\n\n"
                response += "**Binary files cannot be read as text** - they contain non-text data that causes encoding errors.\n\n"
                response += "**What you can do instead:**\n"
                response += "• Use `file filename.png` to get file type information\n"
                response += "• Use `ls -la filename.png` to see file size and permissions\n"
                response += "• Use appropriate viewers/editors for that file type\n"
                response += "• For images: use image viewers or editors\n"
                response += "• For PDFs: use PDF readers\n\n"
                response += f"**Technical details**: {str(e)}"
            except Exception as e:
                response = f"❌ TinyCodeAgent error: {str(e)}\nFalling back to basic response..."
                response += "\n\n" + await self._fallback_response(message, context)
        
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "role": "assistant", 
            "content": response,
            "context": context or {}
        })
        
        debug_logger.log_event("process_chat_message_complete",
                             history_length=len(self.conversation_history),
                             storage_available=self.storage_manager is not None)
        
        return response
    
    def _preprocess_message_for_binary_files(self, message: str) -> str:
        """
        Preprocess message to detect potential binary file references and provide warnings.
        
        Args:
            message: The user's message
            
        Returns:
            Modified message with binary file warnings if needed
        """
        import re
        from pathlib import Path
        
        # Look for file paths in the message
        # Match patterns like: filename.png, ./path/file.jpg, /absolute/path/file.pdf, etc.
        file_patterns = [
            r'\b[\w\-./\\]+\.(?:png|jpg|jpeg|gif|bmp|pdf|exe|dll|zip|tar|gz|mp3|mp4|avi|mov|doc|docx|xls|xlsx|ppt|pptx)\b',
            r'"[^"]*\.(?:png|jpg|jpeg|gif|bmp|pdf|exe|dll|zip|tar|gz|mp3|mp4|avi|mov|doc|docx|xls|xlsx|ppt|pptx)"',
            r"'[^']*\.(?:png|jpg|jpeg|gif|bmp|pdf|exe|dll|zip|tar|gz|mp3|mp4|avi|mov|doc|docx|xls|xlsx|ppt|pptx)'"
        ]
        
        found_binary_files = []
        for pattern in file_patterns:
            matches = re.findall(pattern, message, re.IGNORECASE)
            for match in matches:
                # Clean up quotes
                clean_match = match.strip('"\'')
                if is_binary_file(clean_match):
                    found_binary_files.append(clean_match)
        
        if found_binary_files:
            warning = "\n\n⚠️ **Binary File Warning**: I detected references to binary files in your message:\n"
            for binary_file in found_binary_files[:3]:  # Show max 3 files
                warning += f"• `{binary_file}` - {Path(binary_file).suffix.upper()} file\n"
            if len(found_binary_files) > 3:
                warning += f"• ... and {len(found_binary_files) - 3} more\n"
            
            warning += "\nRemember: Binary files cannot be read as text. Use shell commands like `file` or `ls -la` to inspect them.\n"
            message += warning
        
        return message
    
    async def resume(self, additional_turns: Optional[int] = None) -> str:
        """Resume TinyAgent session with additional turns."""
        # Initialize agent if needed
        await self.initialize_agent()
        
        if self.agent is None:
            return "❌ No TinyAgent session available to resume"
        
        config = self.config_manager.load_config()
        max_turns = additional_turns or config.agent_config.max_turns
        
        try:
            # Resume the agent with additional turns
            if hasattr(self.agent, 'resume'):
                response = await self.agent.resume(max_turns=max_turns)
            else:
                # If resume method doesn't exist, just continue with a generic message
                response = await self.agent.run("Please continue with the previous task.", max_turns=max_turns)
            
            self.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "role": "assistant",
                "content": response,
                "context": {"resumed": True, "additional_turns": max_turns}
            })
            
            return response
        except Exception as e:
            error_msg = f"❌ Failed to resume TinyAgent: {str(e)}"
            self.console.print(f"[red]{error_msg}[/red]")
            return error_msg
    
    async def _fallback_response(self, message: str, context: Optional[Dict] = None) -> str:
        """Fallback response when TinyCodeAgent is not available."""
        _ = context  # Not used in fallback response
        message_lower = message.lower()
        
        # Code-related queries
        if any(keyword in message_lower for keyword in ["code", "function", "class", "debug", "error", "bug"]):
            return """🔧 **Code Assistance**

I'd love to help with your coding needs! However, TinyCodeAgent requires:

• OPENAI_API_KEY environment variable set
• `tinyagent` package installed (`pip install tinyagent`)

With TinyCodeAgent, I can:
• Debug and analyze your code
• Run shell commands for project management
• Use file tools (read_file, write_file, update_file, glob_tool, grep_tool) for safe file operations
• Use TodoWrite tool for task management and complex workflow tracking
• Generate and test code snippets

**To enable full functionality:**
```bash
export OPENAI_API_KEY="your-api-key-here"
pip install tinyagent
```

*In the meantime, I can still help with project analysis and configuration!*"""
        
        # File operations
        elif any(keyword in message_lower for keyword in ["file", "directory", "folder", "create", "delete", "move"]):
            return """📁 **File Operations**

TinyCodeAgent can help with file operations when properly configured:

• Create, read, modify, and organize files using safe file tools
• Directory structure analysis and cleanup with glob_tool and grep_tool
• Batch file operations and project management
• Git operations and version control
• Task management with TodoWrite tool

**Setup required:**
- OPENAI_API_KEY environment variable
- `tinyagent` package installation

*Use `/scan` to analyze your current project structure!*"""
        
        # Testing and validation
        elif any(keyword in message_lower for keyword in ["test", "pytest", "unittest", "validate", "check"]):
            return """🧪 **Testing & Validation**

TinyCodeAgent can assist with testing when available:

• Run existing tests and analyze results
• Generate new test cases for your code
• Validate code quality and style with file tools
• Check for potential issues and bugs
• Organize testing workflows with TodoWrite tool

**Current project info:**
""" + self._get_project_summary()
        
        # General coding help
        else:
            return f"""🤖 **TinyCodeAgent Integration**

I received: *"{message}"*

**Current Status:**
❌ TinyCodeAgent not available (requires setup)

**What TinyCodeAgent can do:**
• Run shell commands for project management
• Use file tools (read_file, write_file, update_file, glob_tool, grep_tool) for safe file operations
• Use TodoWrite tool for task management and complex workflow tracking
• Analyze and debug your code interactively
• Generate and test code snippets
• Perform automated project tasks

**Setup Instructions:**
1. Set OPENAI_API_KEY environment variable
2. Install: `pip install tinyagent`
3. Use `/tiny` command for code assistance

**Available now:**
• Project configuration via `/setup`
• Dependency analysis via `/scan`
• Editor integration via `/editor`

*What specific coding task can I help you prepare for?*"""
    
    def _get_project_summary(self) -> str:
        """Get a summary of the current project."""
        config = self.config_manager.load_config()
        
        summary_parts = []
        if config.project_description:
            summary_parts.append(f"• Project: {config.project_description}")
        
        if config.libraries:
            dep_count = len(config.libraries)
            summary_parts.append(f"• Dependencies: {dep_count} libraries detected")
        
        if config.editor:
            summary_parts.append(f"• Editor: {config.editor}")
        else:
            summary_parts.append("• Editor: Not configured")
        
        return "\n".join(summary_parts) if summary_parts else "• No project data available (run `/scan`)"
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get summary of conversation for context."""
        return {
            "total_exchanges": len([h for h in self.conversation_history if h["role"] == "user"]),
            "last_user_message": next(
                (h["content"] for h in reversed(self.conversation_history) if h["role"] == "user"), 
                None
            ),
            "conversation_topics": self._extract_topics(),
            "session_start": self.conversation_history[0]["timestamp"] if self.conversation_history else None,
            "agent_available": self.agent is not None
        }
    
    def _extract_topics(self) -> List[str]:
        """Extract topics from conversation history."""
        topics = set()
        keywords_map = {
            "coding": ["code", "function", "class", "debug", "python", "javascript"],
            "files": ["file", "directory", "folder", "create", "delete"],
            "testing": ["test", "pytest", "unittest", "validate"],
            "project": ["project", "dependencies", "scan", "analyze"],
            "setup": ["setup", "configure", "install"],
            "git": ["git", "commit", "branch", "repository"]
        }
        
        for message in self.conversation_history:
            if message["role"] == "user":
                content_lower = message["content"].lower()
                for topic, keywords in keywords_map.items():
                    if any(keyword in content_lower for keyword in keywords):
                        topics.add(topic)
        
        return list(topics)
    
    def save_conversation(self) -> None:
        """Save conversation history to file."""
        if not self.conversation_history:
            return
            
        conversation_file = self.config_manager.config_dir / "tiny_agent_conversations.json"
        
        # Load existing conversations
        conversations = []
        if conversation_file.exists():
            try:
                with open(conversation_file, 'r') as f:
                    conversations = json.load(f)
            except:
                conversations = []
        
        # Add current conversation
        conversation_data = {
            "session_id": datetime.now().isoformat(),
            "messages": self.conversation_history,
            "summary": self.get_conversation_summary()
        }
        conversations.append(conversation_data)
        
        # Keep only last 10 conversations
        conversations = conversations[-10:]
        
        # Save updated conversations (create directory if needed)
        conversation_file.parent.mkdir(parents=True, exist_ok=True)
        with open(conversation_file, 'w') as f:
            json.dump(conversations, f, indent=2)
    
    def reset_conversation(self) -> None:
        """Reset/clear the conversation history."""
        self.conversation_history.clear()
        
        # Also clear agent's internal messages if agent exists
        if self.agent and hasattr(self.agent, 'messages'):
            self.agent.messages = []
        
        # Clear any cached conversation state
        if hasattr(self.agent, 'clear_conversation'):
            self.agent.clear_conversation()
    
    async def start_new_session(self) -> str:
        """Start a new conversation session with storage and properly reinitialize agent."""
        if self.storage_manager:
            # Create new session in storage
            new_session_id = self.storage_manager.new_session()
            
            # Clear current conversation
            self.reset_conversation()
            
            # CRITICAL FIX: Recreate agent with new session to ensure system prompt is preserved
            # Simply clearing messages loses the system prompt, so we need to reinitialize
            if self.agent:
                debug_logger.log_event("start_new_session_recreating", session_id=new_session_id)
                
                # Log debugging information about agent initialization
                self.debug_logger.info("start_new_session_initiated", 
                                     new_session_id=new_session_id,
                                     old_session_id=getattr(self.agent, 'session_id', 'None'),
                                     agent_messages_before=len(getattr(self.agent, 'messages', [])))
                
                # Use recreate_with_session_context to properly reinitialize with new session
                # This ensures the system prompt is preserved and the agent starts fresh
                success = await self.recreate_with_session_context(new_session_id, self.storage_manager.user_id)
                
                if success:
                    debug_logger.log_event("start_new_session_recreated_success")
                    
                    # Log final state
                    final_messages = len(getattr(self.agent, 'messages', []))
                    self.debug_logger.info("start_new_session_completed_success",
                                         new_session_id=new_session_id,
                                         agent_messages_after=final_messages,
                                         system_prompt_preserved=final_messages > 0)
                else:
                    print(f"[WARNING] start_new_session: Failed to recreate agent, falling back to session_id update")
                    
                    self.debug_logger.warning("start_new_session_fallback",
                                            new_session_id=new_session_id,
                                            reason="agent_recreation_failed")
                    
                    # Fallback: just update session_id if recreation fails
                    if hasattr(self.agent, 'session_id'):
                        self.agent.session_id = new_session_id
                    if hasattr(self.agent, 'messages'):
                        self.agent.messages = []
            
            # Save session metadata
            self.storage_manager.save_session_metadata({
                "started_at": datetime.now().isoformat(),
                "project_dir": str(self.config_manager.workdir)
            })
            
            return new_session_id
        else:
            # Just reset conversation if no storage
            self.reset_conversation()
            
            # For no storage case, we still need to preserve system prompt
            # The best approach is to reinitialize the agent if possible
            if self.agent:
                debug_logger.log_event("start_new_session_reinitializing_no_storage")
                try:
                    # Close and recreate agent to ensure system prompt is preserved
                    await self.agent.close()
                    self.agent = None
                    await self.initialize_agent()
                    debug_logger.log_event("start_new_session_reinitialized_success")
                except Exception as e:
                    print(f"[ERROR] start_new_session: Failed to reinitialize agent: {e}")
                    # Fallback: just clear messages (old behavior)
                    if hasattr(self.agent, 'messages'):
                        self.agent.messages = []
            
            return "no_storage"
    
    async def load_session(self, session_id: str) -> bool:
        """Load a session using TinyAgent's native loading.
        
        Simple approach: Update session_id and call init_async().
        """
        try:
            if not self.agent:
                return False
            
            # Update session_id
            self.agent.session_id = session_id
            
            # Let TinyAgent load the session
            await self.agent.init_async()
            return True
        except Exception as e:
            print(f"[ERROR] Failed to load session: {e}")
            return False
    
    async def recreate_with_session_context(self, session_id: str, user_id: str) -> bool:
        """Recreate TinyAgent with specific session and user context.
        
        This ensures the agent loads the existing conversation from the database
        with the proper session_id and user_id combination.
        """
        try:
            debug_logger.log_event("recreate_with_session_start", session_id=session_id, user_id=user_id)
            
            # Log session recreation start
            self.debug_logger.info("session_recreation_started",
                                 target_session_id=session_id,
                                 target_user_id=user_id,
                                 current_agent_exists=(self.agent is not None))
            
            # Close existing agent to ensure clean state
            if self.agent:
                old_agent_session = getattr(self.agent, 'session_id', 'None')
                old_agent_user = getattr(self.agent, 'user_id', 'None')
                debug_logger.log_event("recreate_with_session_closing_old", old_session=old_agent_session, old_user=old_agent_user)
                
                self.debug_logger.info("closing_existing_agent",
                                     old_agent_session_id=old_agent_session,
                                     old_agent_user_id=old_agent_user,
                                     agent_id=hex(id(self.agent)))
                
                await self.agent.close()
                self.agent = None
            
            # Update storage manager context BEFORE creating new agent
            if self.storage_manager:
                old_session = self.storage_manager.current_session_id
                old_user = self.storage_manager.user_id
                
                # Use switch_to_session to properly update both IDs
                self.storage_manager.switch_to_session(session_id, user_id)
                
                debug_logger.log_event("recreate_with_session_storage_switched", 
                                     old_session=old_session, old_user=old_user,
                                     new_session=session_id, new_user=user_id)
                
                self.debug_logger.info("storage_context_switched",
                                     old_session_id=old_session,
                                     old_user_id=old_user,
                                     new_session_id=session_id,
                                     new_user_id=user_id,
                                     storage_manager_id=hex(id(self.storage_manager)))
            else:
                print(f"[ERROR] recreate_with_session_context: No storage manager available")
                self.debug_logger.error("no_storage_manager_available")
                return False
            
            # Create new agent with the updated storage context
            # initialize_agent will:
            # 1. Use storage_manager's current session_id and user_id
            # 2. Create TinyCodeAgent with storage parameters
            # 3. Call init_async() to load the session from database
            await self.initialize_agent()
            
            if not self.agent:
                print(f"[ERROR] recreate_with_session_context: Failed to initialize agent")
                return False
            
            # The agent is now fully initialized with the session loaded from the database
            debug_logger.log_event("recreate_with_session_success")
            
            # Verify the agent has the correct session context and get message count
            final_agent_session_id = getattr(self.agent, 'session_id', 'None')
            final_agent_user_id = getattr(self.agent, 'user_id', 'None')
            
            # Try to get final message count
            try:
                final_messages = []
                if hasattr(self.agent, 'messages') and self.agent.messages:
                    final_messages = self.agent.messages
                elif hasattr(self.agent, 'conversation') and hasattr(self.agent.conversation, 'messages'):
                    final_messages = self.agent.conversation.messages
                elif hasattr(self.agent, '_conversation') and hasattr(self.agent._conversation, 'messages'):
                    final_messages = self.agent._conversation.messages
                    
                final_message_count = len(final_messages) if final_messages else 0
            except Exception as e:
                final_message_count = -1
                debug_logger.log_error("recreate_with_session_message_count_failed", e)
            
            debug_logger.log_event("recreate_with_session_verified",
                                 session_id=final_agent_session_id,
                                 user_id=final_agent_user_id,
                                 message_count=final_message_count)
            
            # Log successful recreation
            self.debug_logger.info("session_recreation_completed",
                                 success=True,
                                 final_agent_session_id=final_agent_session_id,
                                 final_agent_user_id=final_agent_user_id,
                                 final_message_count=final_message_count,
                                 target_session_id=session_id,
                                 target_user_id=user_id,
                                 session_id_match=(final_agent_session_id == session_id),
                                 user_id_match=(final_agent_user_id == user_id),
                                 agent_id=hex(id(self.agent)))
            
            return True
            
        except Exception as e:
            print(f"[ERROR] recreate_with_session_context: Failed to recreate agent: {e}")
            import traceback
            print(f"[ERROR] Traceback: {traceback.format_exc()}")
            
            # Log failed recreation
            self.debug_logger.error("session_recreation_failed",
                                  error=str(e),
                                  traceback=traceback.format_exc(),
                                  target_session_id=session_id,
                                  target_user_id=user_id)
            
            return False
    
    async def close(self):
        """Clean up resources."""
        try:
            # Close subagent instances created with as_tool()
            if hasattr(self, '_subagent_instances'):
                for subagent in self._subagent_instances:
                    try:
                        await subagent.close()
                    except Exception as e:
                        self.console.print(f"[yellow]Warning: Error closing subagent instance: {e}[/yellow]")
                self._subagent_instances = []
            
            # Close subagent first (legacy)
            if self.subagent:
                try:
                    await self.subagent.close()
                except Exception as e:
                    self.console.print(f"[yellow]Warning: Error closing subagent: {e}[/yellow]")
                self.subagent = None
            
            # Close main agent
            if self.agent:
                try:
                    await self.agent.close()
                except Exception as e:
                    self.console.print(f"[yellow]Warning: Error closing main agent: {e}[/yellow]")
                self.agent = None
            
            # Close storage manager
            if self.storage_manager:
                try:
                    self.storage_manager.close()
                except Exception as e:
                    self.console.print(f"[yellow]Warning: Error closing storage manager: {e}[/yellow]")
                self.storage_manager = None
            
            # Clear conversation history
            self.conversation_history.clear()
            
        except Exception as e:
            self.console.print(f"[red]Error during cleanup: {e}[/red]")


class TinyCodeAgentManager:
    """Manager for TinyCodeAgent operations."""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.console = Console()
    
    def check_requirements(self) -> Dict[str, Any]:
        """Check if TinyCodeAgent requirements are met."""
        config = self.config_manager.load_config()
        agent_config = config.agent_config
        
        # Get expected API key for current model
        model_api_key = self.config_manager.get_model_api_key()
        expected_env_var = self._get_expected_env_var(agent_config.provider)
        
        status = {
            "model_api_key": bool(model_api_key),
            "tinyagent_available": False,
            "can_initialize": False,
            "missing_requirements": [],
            "current_model": agent_config.provider + "/" + agent_config.model_name,
            "current_provider": agent_config.provider,
            "expected_env_var": expected_env_var
        }
        
        # Check if TinyAgent is available (support both distribution names)
        try:
            import importlib.util as _ilutil
            has_tinyagent = _ilutil.find_spec("tinyagent") is not None
            has_tinyagent_py = _ilutil.find_spec("tinyagent_py") is not None
            status["tinyagent_available"] = bool(has_tinyagent or has_tinyagent_py)
        except Exception:
            status["tinyagent_available"] = False
        if not status["tinyagent_available"]:
            status["missing_requirements"].append("TinyAgent package (pip install tinyagent OR tinyagent-py)")
        
        # Check API key for current model
        if not status["model_api_key"]:
            status["missing_requirements"].append(f"{expected_env_var} environment variable or use /model command")
        
        status["can_initialize"] = status["model_api_key"] and status["tinyagent_available"]
        
        return status
    
    def _get_expected_env_var(self, provider: str) -> str:
        """Get expected environment variable name for a provider."""
        provider_lower = provider.lower()
        if provider_lower == "openai":
            return "OPENAI_API_KEY"
        elif provider_lower == "anthropic":
            return "ANTHROPIC_API_KEY"
        elif provider_lower == "google":
            return "GOOGLE_API_KEY"
        elif provider_lower == "azure":
            return "AZURE_OPENAI_API_KEY"
        elif provider_lower == "cohere":
            return "COHERE_API_KEY"
        elif provider_lower == "huggingface":
            return "HUGGINGFACE_API_KEY"
        elif provider_lower == "groq":
            return "GROQ_API_KEY"
        else:
            return f"{provider.upper()}_API_KEY"
    
    def display_setup_instructions(self) -> None:
        """Display setup instructions for TinyCodeAgent."""
        status = self.check_requirements()
        
        if status["can_initialize"]:
            setup_content = f"""[bold green]✅ Juno Agent Ready![/bold green]

All requirements are satisfied:
• ✅ {status["expected_env_var"]} environment variable set
• ✅ tinyagent package available

**Current Configuration:**
• Model: [bold]{status["current_model"]}[/bold]
• Provider: [bold]{status["current_provider"]}[/bold]
• Temperature: {self.config_manager.load_config().agent_config.temperature}

You can now use the `/tiny` command for advanced code assistance!

**What you can do:**
• Run shell commands for project management
• Use file tools (read_file, write_file, update_file, glob_tool, grep_tool) for safe file operations
• Use TodoWrite tool for task management and complex workflow tracking
• Debug and analyze code interactively
• Generate and test code snippets
• Perform automated project tasks

**Need to change models?** Use `/model` command to configure different AI providers."""
        else:
            missing_items = "\n".join(f"• ❌ {item}" for item in status["missing_requirements"])
            
            setup_content = f"""[bold yellow]🚧 TinyCodeAgent Setup Required[/bold yellow]

**Current Configuration:**
• Model: [bold]{status["current_model"]}[/bold]
• Provider: [bold]{status["current_provider"]}[/bold]

Missing requirements:
{missing_items}

**Setup Instructions:**

1. **Install TinyAgent:**
   ```bash
   pip install tinyagent
   ```

2. **Configure Model & API Key:**
   Use the `/model` command for easy setup, or set manually:
   ```bash
   export {status["expected_env_var"]}="your-api-key"
   ```

3. **Get API Keys:**
   • OpenAI: https://platform.openai.com/api-keys
   • Anthropic: https://console.anthropic.com/
   • Google: https://makersuite.google.com/app/apikey
   • Others: Check provider documentation

**Recommended for cost-effective usage:**
• OpenAI: gpt-5-mini
• Anthropic: claude-4-haiku
• Google: gemini-2.5-flash

**After setup:**
• Use `/model` command to configure your preferred AI model
• Use `/tiny` command for advanced AI coding assistance!"""
        
        setup_panel = Panel(
            setup_content,
            title="[bold]🤖 TinyCodeAgent Setup[/bold]",
            border_style="bright_blue" if status["can_initialize"] else "bright_yellow",
            padding=(1, 2)
        )
        
        self.console.print(setup_panel)
    
    def get_status_info(self) -> Dict[str, str]:
        """Get status information for display."""
        status = self.check_requirements()
        config = self.config_manager.load_config()
        agent_config = config.agent_config
        
        return {
            "status": "✅ Ready" if status["can_initialize"] else "❌ Setup Required",
            "openai_key": "✅ Set" if status["model_api_key"] else "❌ Missing", 
            "tinyagent": "✅ Available" if status["tinyagent_available"] else "❌ Not installed",
            "model": f"{agent_config.model_name} ({agent_config.provider})",
            "provider": f"Local Execution (temp: {agent_config.temperature})"
        }
