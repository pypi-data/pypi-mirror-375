"""Simple UI tool callback for Rich-based inline tool visualization."""

import asyncio
import json
import logging
import time
from typing import Any, Dict, Optional
from dataclasses import dataclass

from rich.console import Console

from .debug_logger import debug_logger


@dataclass
class ToolEvent:
    """Represents a tool usage event for simple UI."""
    tool_name: str
    timestamp: float
    tool_call_id: Optional[str] = None
    arguments: Optional[Dict[str, Any]] = None
    result: Optional[str] = None
    error: Optional[str] = None
    duration: Optional[float] = None
    agent_level: int = 0
    is_subagent: bool = False
    agent_id: Optional[str] = None
    display_name: Optional[str] = None


class SimpleUIToolCallback:
    """
    A callback for TinyAgent that displays tool usage inline using Rich console.
    
    This callback shows tool calls as they happen in the simple UI, providing
    immediate feedback about what the agent is doing without overwhelming the user.
    """
    
    def __init__(
        self,
        console: Console,
        logger: Optional[logging.Logger] = None,
        max_result_length: int = 200,
        show_arguments: bool = True,
        show_results: bool = True,
        agent_level: int = 0,
        agent_id: Optional[str] = None,
        display_name: Optional[str] = None
    ):
        """
        Initialize the Simple UI tool callback.
        
        Args:
            console: Rich console instance for output
            logger: Optional logger instance
            max_result_length: Maximum length of result text to display
            show_arguments: Whether to show tool arguments
            show_results: Whether to show tool results
            agent_level: Hierarchy level (0 = main agent, 1+ = subagent)
            agent_id: Unique identifier for the agent
            display_name: Human-readable name for the agent
        """
        debug_logger.log_function_entry("SimpleUIToolCallback.__init__",
                                       console_available=console is not None,
                                       max_result_length=max_result_length,
                                       agent_level=agent_level)
        
        self.console = console
        self.logger = logger or logging.getLogger(__name__)
        self.max_result_length = max_result_length
        self.show_arguments = show_arguments
        self.show_results = show_results
        
        # Hierarchy information
        self.agent_level = agent_level
        self.agent_id = agent_id or "main_agent"
        self.display_name = display_name or ("Main Agent" if agent_level == 0 else f"Subagent-{agent_level}")
        self.is_subagent = agent_level > 0
        
        # Event tracking
        self.active_tools: Dict[str, ToolEvent] = {}
        
        debug_logger.log_event("simple_ui_callback_initialized",
                              callback_id=hex(id(self)),
                              agent_level=agent_level,
                              display_name=self.display_name)
    
    def _truncate_text(self, text: str, max_length: int) -> str:
        """Truncate text to specified length with ellipsis."""
        if not text:
            return ""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."
    
    def _format_arguments(self, args: Dict[str, Any]) -> str:
        """Format tool arguments for display."""
        if not args or not self.show_arguments:
            return ""
        
        # Show only the most important arguments to keep display clean
        key_args = {}
        for key, value in args.items():
            if key in ['prompt', 'command', 'file_path', 'query', 'message', 'description']:
                if isinstance(value, str):
                    key_args[key] = self._truncate_text(value, 100)
                else:
                    key_args[key] = str(value)
        
        if not key_args:
            return f"({len(args)} args)"
        
        arg_strs = [f"{k}={v!r}" for k, v in key_args.items()]
        return f"({', '.join(arg_strs)})"
    
    def _format_result(self, result: str) -> str:
        """Format tool result for display."""
        if not result or not self.show_results:
            return ""
        
        # Clean up the result text
        clean_result = result.strip()
        if not clean_result:
            return ""
            
        # Truncate long results
        truncated = self._truncate_text(clean_result, self.max_result_length)
        
        # Replace newlines with spaces for inline display
        return truncated.replace('\n', ' ').replace('\r', ' ')
    
    def _get_tool_emoji(self, tool_name: str) -> str:
        """Get consistent emoji for all tools - removed for simplicity and consistency."""
        # Following UI guidelines: keep it simple and consistent
        # All tools now use the same green ✷ indicator in _display_tool_start
        return ""  # No longer used, keeping method for compatibility
    
    def _display_tool_start(self, event: ToolEvent):
        """Display tool start event with simple formatting following UI guidelines."""
        args = event.arguments or {}
        command_display = ""
        
        # Show main command/operation with 4 lines before truncating
        if 'command' in args:
            command_lines = str(args['command']).split('\n')
            if len(command_lines) > 4:
                command_display = '\n'.join(command_lines[:4]) + '...'
            else:
                command_display = args['command']
        elif 'file_path' in args:
            command_display = str(args['file_path'])
        elif 'prompt' in args:
            prompt_lines = str(args['prompt']).split('\n')
            if len(prompt_lines) > 4:
                command_display = '\n'.join(prompt_lines[:4]) + '...'
            else:
                command_display = args['prompt']
        
        # Add spacing before tool call
        self.console.print()
        
        # Simple consistent format with green indicator
        if command_display:
            self.console.print(f"  [green]✷[/green] [bold]{event.tool_name}[/bold]")
            # Show command details with proper indentation
            for line in command_display.split('\n'):
                if line.strip():
                    self.console.print(f"    [dim]{line.strip()}[/dim]")
        else:
            self.console.print(f"  [green]✷[/green] [bold]{event.tool_name}[/bold]")
    
    def _display_tool_end(self, event: ToolEvent):
        """Display tool end event with simple formatting following UI guidelines."""
        duration_str = f"{event.duration:.1f}s" if event.duration else "?"
        
        # Determine status with proper linking symbol and spacing
        if event.error:
            status_icon = "❌"
            summary = self._truncate_text(event.error, 80)
            self.console.print(f"    [dim]⎿ {status_icon} {duration_str} - [red]{summary}[/red][/dim]")
        else:
            status_icon = "✔️"  # Using ✔️ as requested
            result = event.result or ""
            if result:
                lines = result.strip().split('\n')
                if len(lines) > 1:
                    summary = f"{len(lines)} lines"
                else:
                    summary = self._truncate_text(result, 80)
                self.console.print(f"    [dim]⎿ {status_icon} {duration_str} - {summary}[/dim]")
            else:
                self.console.print(f"    [dim]⎿ {status_icon} {duration_str}[/dim]")
        
        # Add spacing after tool result
        self.console.print()
    
    async def __call__(self, event_name: str, agent: Any, *args, **kwargs: Any) -> None:
        """
        Main callback entry point for TinyAgent events.
        
        This method handles both new interface (kwargs_dict as positional arg)
        and legacy interface (**kwargs) for backward compatibility.
        """
        debug_logger.log_callback_invocation("SimpleUIToolCallback", event_name,
                                            agent_id=hex(id(agent)),
                                            args_count=len(args),
                                            kwargs_keys=list(kwargs.keys()),
                                            callback_agent_level=self.agent_level,
                                            callback_agent_id=self.agent_id,
                                            callback_is_subagent=self.is_subagent,
                                            callback_display_name=self.display_name)
        
        # Extract kwargs from either interface
        if args and isinstance(args[0], dict):
            # New interface: kwargs_dict passed as positional argument
            event_kwargs = args[0]
        else:
            # Legacy interface: use **kwargs
            event_kwargs = kwargs
        
        debug_logger.log_event("simple_ui_callback_event_routing",
                             event_name_param=event_name,
                             event_kwargs_keys=list(event_kwargs.keys()),
                             agent_hierarchy=f"Level {self.agent_level}: {self.display_name}",
                             is_subagent_callback=self.is_subagent)
        
        # Route to appropriate handler
        handler = getattr(self, f"_handle_{event_name}", None)
        if handler:
            debug_logger.log_event("calling_simple_ui_event_handler",
                                 event_name_param=event_name,
                                 handler_name=handler.__name__)
            await handler(agent, **event_kwargs)
        else:
            self.logger.debug(f"No handler for event: {event_name}")
            debug_logger.log_event("no_simple_ui_handler_found", event_name_param=event_name)
    
    async def _handle_tool_start(self, agent: Any, **kwargs: Any) -> None:
        """Handle tool start event."""
        debug_logger.log_function_entry("_handle_tool_start",
                                       kwargs_keys=list(kwargs.keys()),
                                       agent_level=self.agent_level,
                                       agent_id=self.agent_id,
                                       display_name=self.display_name)
        
        # Extract tool call information
        tool_call = kwargs.get("tool_call")
        if not tool_call:
            self.logger.warning("No tool_call in tool_start event")
            return
        
        # Handle Pydantic model attributes
        if hasattr(tool_call, 'function'):
            # Pydantic ChatCompletionMessageToolCall object
            func_info = tool_call.function
            tool_name = func_info.name if hasattr(func_info, 'name') else "unknown_tool"
            tool_call_id = tool_call.id if hasattr(tool_call, 'id') else f"call_{int(time.time())}"
            arguments_str = func_info.arguments if hasattr(func_info, 'arguments') else "{}"
        else:
            # Fallback for dict-like objects
            func_info = tool_call.get("function", {}) if isinstance(tool_call, dict) else {}
            tool_name = func_info.get("name", "unknown_tool") if isinstance(func_info, dict) else "unknown_tool"
            tool_call_id = tool_call.get("id", f"call_{int(time.time())}") if isinstance(tool_call, dict) else f"call_{int(time.time())}"
            arguments_str = func_info.get("arguments", "{}") if isinstance(func_info, dict) else "{}"
        
        debug_logger.log_event("simple_ui_tool_start_extraction",
                             tool_call_id=tool_call_id,
                             tool_name=tool_name)
        
        # Parse arguments
        try:
            args = json.loads(arguments_str)
        except (json.JSONDecodeError, TypeError) as e:
            args = {"raw_args": arguments_str, "parse_error": str(e)}
            debug_logger.log_error("simple_ui_tool_start_args_parse_failed", e, tool_call_id=tool_call_id)
        
        # Create tool event
        event = ToolEvent(
            tool_name=tool_name,
            timestamp=time.time(),
            tool_call_id=tool_call_id,
            arguments=args,
            agent_level=self.agent_level,
            is_subagent=self.is_subagent,
            agent_id=self.agent_id,
            display_name=self.display_name
        )
        
        # Store active tool
        self.active_tools[tool_call_id] = event
        
        # Display tool start
        self._display_tool_start(event)
        
        debug_logger.log_tool_event("start", tool_name,
                                  tool_call_id=tool_call_id,
                                  agent_level=self.agent_level,
                                  is_subagent=self.is_subagent,
                                  agent_display_name=self.display_name)
        
        debug_logger.log_function_exit("_handle_tool_start")
    
    async def _handle_tool_end(self, agent: Any, **kwargs: Any) -> None:
        """Handle tool end event."""
        debug_logger.log_function_entry("_handle_tool_end",
                                       kwargs_keys=list(kwargs.keys()),
                                       agent_level=self.agent_level,
                                       agent_id=self.agent_id,
                                       display_name=self.display_name)
        
        # Extract tool call information
        tool_call = kwargs.get("tool_call")
        result = kwargs.get("result", "")
        
        # Extract tool_call_id
        if hasattr(tool_call, 'id'):
            tool_call_id = tool_call.id
        elif isinstance(tool_call, dict):
            tool_call_id = tool_call.get("id")
        else:
            tool_call_id = None
        
        debug_logger.log_event("simple_ui_tool_end_extraction",
                             tool_call_id=tool_call_id,
                             result_length=len(str(result)) if result else 0)
        
        # Find corresponding start event
        start_event = self.active_tools.pop(tool_call_id, None) if tool_call_id else None
        
        if start_event:
            tool_name = start_event.tool_name
            duration = time.time() - start_event.timestamp
            debug_logger.log_event("simple_ui_tool_end_matched_start",
                                 tool_name=tool_name,
                                 tool_call_id=tool_call_id,
                                 duration=duration)
        else:
            # Fallback: extract tool name
            if hasattr(tool_call, 'function'):
                func_info = tool_call.function
                tool_name = func_info.name if hasattr(func_info, 'name') else "unknown_tool"
            elif isinstance(tool_call, dict):
                func_info = tool_call.get("function", {})
                tool_name = func_info.get("name", "unknown_tool") if isinstance(func_info, dict) else "unknown_tool"
            else:
                tool_name = "unknown_tool"
            duration = None
            debug_logger.log_event("simple_ui_tool_end_orphaned",
                                 tool_call_id=tool_call_id,
                                 fallback_tool_name=tool_name)
        
        # Detect if this is an error result
        error_message = None
        is_error = False
        if result and isinstance(result, str):
            # Simple error detection - look for common error patterns
            result_lower = result.lower()
            if any(pattern in result_lower for pattern in [
                "error:", "exception:", "failed:", "traceback:",
                "command not found", "permission denied", "no such file"
            ]):
                is_error = True
                # Extract first line as error message
                error_message = result.split('\n')[0].strip()
        
        # Create tool end event
        event = ToolEvent(
            tool_name=tool_name,
            timestamp=time.time(),
            tool_call_id=tool_call_id,
            result=result,
            error=error_message,
            duration=duration,
            agent_level=self.agent_level,
            is_subagent=self.is_subagent,
            agent_id=self.agent_id,
            display_name=self.display_name
        )
        
        # Display tool end
        self._display_tool_end(event)
        
        debug_logger.log_tool_event("end" if not is_error else "error", tool_name,
                                  tool_call_id=tool_call_id,
                                  duration=duration,
                                  result_length=len(str(result)) if result else 0,
                                  has_error=is_error,
                                  agent_level=self.agent_level,
                                  is_subagent=self.is_subagent,
                                  agent_display_name=self.display_name)
        
        debug_logger.log_function_exit("_handle_tool_end")
    


def create_simple_ui_tool_callback(
    console: Console,
    logger: Optional[logging.Logger] = None,
    max_result_length: int = 200,
    show_arguments: bool = True,
    show_results: bool = True,
    agent_level: int = 0,
    agent_id: Optional[str] = None,
    display_name: Optional[str] = None
) -> SimpleUIToolCallback:
    """
    Factory function to create a SimpleUIToolCallback instance.
    
    Args:
        console: Rich console instance for output
        logger: Optional logger instance
        max_result_length: Maximum length of result text to display
        show_arguments: Whether to show tool arguments
        show_results: Whether to show tool results
        agent_level: Hierarchy level (0 = main agent, 1+ = subagent)
        agent_id: Unique identifier for the agent
        display_name: Human-readable name for the agent
        
    Returns:
        SimpleUIToolCallback instance
    """
    return SimpleUIToolCallback(
        console=console,
        logger=logger,
        max_result_length=max_result_length,
        show_arguments=show_arguments,
        show_results=show_results,
        agent_level=agent_level,
        agent_id=agent_id,
        display_name=display_name
    )