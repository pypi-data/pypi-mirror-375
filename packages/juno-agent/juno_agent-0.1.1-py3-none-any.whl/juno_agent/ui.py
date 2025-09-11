"""User interface components for juno-agent."""

import asyncio
import json
import sys
import threading
from pathlib import Path
from typing import List, Optional, Dict, Any, Union, Tuple
import requests

# Cached prompt_toolkit Style for unified look across dialogs
_PT_STYLE_CACHE = None

def get_unified_pt_style():
    """Return a shared prompt_toolkit Style for all dialogs.

    Modern developer-focused design with electric blue accents and clean typography.
    """
    global _PT_STYLE_CACHE
    if _PT_STYLE_CACHE is not None:
        return _PT_STYLE_CACHE
    try:
        from prompt_toolkit.styles import Style  # type: ignore
        # Modern dark theme with electric blue accents
        _PT_STYLE_CACHE = Style.from_dict({
            # Dialog container and frame
            "dialog": "bg:#0f1419 #f8f9fa",
            "dialog.body": "bg:#0f1419 #f8f9fa",
            "dialog frame.label": "bg:#0f1419 #00d4ff bold",
            "frame.border": "#666666",

            # Buttons
            "button": "bg:#2a3441 #f8f9fa",
            "button.focused": "bg:#00d4ff #000000 bold",

            # Inputs / text areas 
            "text-area": "bg:#000000 #f8f9fa",
            "input-field": "bg:#000000 #f8f9fa",
            "textarea": "bg:#000000 #f8f9fa",

            # Radio/checkbox lists
            "radio": "#f8f9fa",
            "radio.selected": "#00d4ff bold",
            "checkbox": "#f8f9fa",
            "checkbox.focused": "#00d4ff bold",

            # Generic selected item emphasis
            "selected": "#00d4ff bold",
            "focused selected": "#00d4ff bold",
        })
    except Exception:
        _PT_STYLE_CACHE = None
    return _PT_STYLE_CACHE


from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text

from .config import ConfigManager, Config
from .utils import SystemStatus, open_browser
from .scanner import ProjectScanner
from .editors import MCPServerInstaller
from .agent import TinyAgentChat, ProjectAnalysisAgent
from .tiny_agent import TinyCodeAgentChat, TinyCodeAgentManager
from .storage_manager_async import AsyncConversationStorageManager
from .fancy_ui.setup import get_supported_editors, get_editor_display_names


def _run_coro_in_thread(coro):
    """Run a coroutine in a daemon thread to avoid nested event loops and Ctrl-C hangs."""
    result_holder = {}
    error_holder = {}
    done = threading.Event()

    def runner():
        try:
            result_holder['value'] = asyncio.run(coro)
        except Exception as e:
            error_holder['error'] = e
        finally:
            done.set()

    t = threading.Thread(target=runner, daemon=True)
    t.start()
    try:
        t.join()
    except KeyboardInterrupt:
        # Allow graceful exit; daemon thread will be terminated by interpreter
        pass
    if 'error' in error_holder:
        raise error_holder['error']
    return result_holder.get('value')

def _run_call_in_daemon_thread(fn, *args, **kwargs):
    """Run a blocking function in a daemon thread; return its result or raise its exception."""
    result_holder = {}
    error_holder = {}
    done = threading.Event()

    def runner():
        try:
            result_holder['value'] = fn(*args, **kwargs)
        except Exception as e:
            error_holder['error'] = e
        finally:
            done.set()

    t = threading.Thread(target=runner, daemon=True)
    t.start()
    try:
        t.join()
    except KeyboardInterrupt:
        pass
    if 'error' in error_holder:
        raise error_holder['error']
    return result_holder.get('value')


class AutoCompleteInput:
    """Enhanced input handler with inline tab completion like codex-cli."""
    
    def __init__(self, commands: List[str], token_tracker=None):
        self.commands = commands
        self.history_file = None
        self.pt_session = None
        self.pt_completer = None
        self.pt_kb = None
        self.token_tracker = token_tracker  # For tracking token usage
        self.has_readline = False  # Will be set to True if prompt_toolkit is available
        
        # History location: always local project .askbudi/simple_history/chat_history.txt
        try:
            base = Path.cwd()
            hist_dir = base / ".askbudi" / "simple_history"
            hist_dir.mkdir(parents=True, exist_ok=True)
            self.history_file = hist_dir / "chat_history.txt"
        except Exception:
            self.history_file = None
        
        # Optional prompt_toolkit session for inline popup completions
        try:
            from prompt_toolkit import PromptSession  # type: ignore
            from prompt_toolkit.completion import Completer, Completion, FuzzyCompleter  # type: ignore
            from prompt_toolkit.history import FileHistory  # type: ignore
            from prompt_toolkit.key_binding import KeyBindings  # type: ignore
            from prompt_toolkit.key_binding.key_processor import KeyPressEvent  # type: ignore
            from prompt_toolkit.application.current import get_app  # type: ignore
            from prompt_toolkit.filters import Condition  # type: ignore
            from prompt_toolkit.auto_suggest import AutoSuggestFromHistory  # type: ignore

            # Create completer
            self.pt_completer = self._create_completer(commands)

            # Key bindings: Ctrl+J inserts newline; Enter accepts input
            kb = KeyBindings()

            # Ctrl+J inserts newline
            @kb.add("c-j")
            def _(event: KeyPressEvent):  # type: ignore
                event.current_buffer.insert_text("\n")

            # Optional: Shift+Enter alternative (some terms map it to same Enter)
            # Can't reliably capture Shift+Enter; add Alt+Enter as alternative
            @kb.add("escape", "enter")
            def _(event: KeyPressEvent):  # type: ignore
                event.current_buffer.insert_text("\n")

            # If completion menu is showing, Enter accepts the highlighted completion
            @kb.add("enter", filter=Condition(lambda: get_app().current_buffer.complete_state is not None), eager=True)
            def _(event: KeyPressEvent):  # type: ignore
                buf = event.app.current_buffer
                cs = buf.complete_state
                if cs and cs.current_completion is not None:
                    buf.apply_completion(cs.current_completion)
                # Do not accept line yet; keep editing

            # Arrow keys navigate completion menu when visible
            @kb.add("down", filter=Condition(lambda: get_app().current_buffer.complete_state is not None), eager=True)
            def _(event: KeyPressEvent):  # type: ignore
                event.app.current_buffer.complete_next()

            @kb.add("up", filter=Condition(lambda: get_app().current_buffer.complete_state is not None), eager=True)
            def _(event: KeyPressEvent):  # type: ignore
                event.app.current_buffer.complete_previous()

            # Start completion with Tab when at command-start
            @kb.add("tab", filter=Condition(lambda: (
                get_app().current_buffer.document.text_before_cursor.startswith('/') and
                (' ' not in get_app().current_buffer.document.text_before_cursor and '\n' not in get_app().current_buffer.document.text_before_cursor)
            )))
            def _(event: KeyPressEvent):  # type: ignore
                buf = event.app.current_buffer
                if buf.complete_state:
                    buf.complete_next()
                else:
                    buf.start_completion(select_first=True)

            self.pt_kb = kb

            history = FileHistory(str(self.history_file)) if self.history_file else None
            # Only complete while typing at the start of a command (before first space)
            complete_when_command_start = Condition(lambda: (
                get_app().current_buffer.document.text_before_cursor.startswith('/') and
                (' ' not in get_app().current_buffer.document.text_before_cursor and '\n' not in get_app().current_buffer.document.text_before_cursor)
            ))
            self.pt_session = PromptSession(
                completer=self.pt_completer,
                complete_while_typing=True,  # Always enable for better UX
                complete_in_thread=True,
                history=history,
                auto_suggest=AutoSuggestFromHistory(),
                key_bindings=self.pt_kb,
                style=get_unified_pt_style(),
            )
            self.has_readline = True  # Successfully initialized prompt_toolkit
        except Exception:
            self.pt_session = None
            self.pt_completer = None

    def _create_completer(self, commands: List[str]):
        """Create a command-only completer for the given commands."""
        try:
            from prompt_toolkit.completion import Completer, Completion, FuzzyCompleter  # type: ignore
            
            class CommandOnlyCompleter(Completer):
                def __init__(self, cmds: List[str]):
                    self._cmds = cmds
                def get_completions(self, document, complete_event):
                    text = document.text_before_cursor
                    # Offer completions only when at start (no space typed yet) and starting with '/'
                    if not text.startswith('/'):
                        return
                    if ' ' in text or '\t' in text or '\n' in text:
                        return
                    prefix = text  # exact prefix (like '/mo') for replacement
                    # Yield all commands that could match
                    for c in self._cmds:
                        # Check if command starts with the prefix (case-insensitive)
                        if c.lower().startswith(prefix.lower()):
                            yield Completion(c, start_position=-len(prefix))

            base_completer = CommandOnlyCompleter(commands)
            # Wrap with fuzzy completer for better matching while typing
            return FuzzyCompleter(base_completer)
        except Exception:
            return None

    def input(self, prompt: str = "") -> str:
        """Get input with enhanced inline tab completion."""
        try:
            # Prefer prompt_toolkit if available for a true inline palette
            if self.pt_session is not None:
                # Clean input with gray frame
                from prompt_toolkit.cursor_shapes import CursorShape  # type: ignore
                user_input = self.pt_session.prompt(
                    prompt,
                    show_frame=True,
                    cursor=CursorShape.BLOCK,
                    mouse_support=False,
                    multiline=False,
                    rprompt=lambda: "",
                    bottom_toolbar=self._get_bottom_toolbar
                )
            else:
                # Basic fallback
                user_input = input(prompt)
            
            return user_input
        except (EOFError, KeyboardInterrupt):
            raise KeyboardInterrupt()

    async def ainput(self, prompt: str = "") -> str:
        """Async-friendly input method.

        - Uses prompt_toolkit's prompt_async when available (no nested loops).
        - Else reads input in a thread executor to avoid blocking the event loop.
        """
        try:
            if self.pt_session is not None:
                # Use prompt_toolkit's async prompt to integrate with running loop
                from prompt_toolkit.cursor_shapes import CursorShape  # type: ignore
                return await self.pt_session.prompt_async(
                    prompt,
                    show_frame=True,
                    cursor=CursorShape.BLOCK,
                    mouse_support=False,
                    multiline=False,
                    rprompt=lambda: "",
                    bottom_toolbar=self._get_bottom_toolbar
                )
            else:
                loop = asyncio.get_running_loop()
                return await loop.run_in_executor(None, lambda: self.input(prompt))
        except (EOFError, KeyboardInterrupt):
            raise KeyboardInterrupt()
    
    def update_commands(self, new_commands: List[str]):
        """Update the available commands for autocomplete."""
        self.commands = new_commands
        if self.pt_completer is not None and self.pt_session is not None:
            try:
                # Recreate the completer with new commands
                self.pt_completer = self._create_completer(new_commands)
                # Replace session completer (prompt_toolkit v3 allows runtime change)
                if self.pt_completer is not None:
                    self.pt_session.completer = self.pt_completer
            except Exception:
                pass
    
    
    def get_suggestions(self, text: str) -> List[str]:
        """Get completion suggestions for given text."""
        if text.startswith('/'):
            return [cmd for cmd in self.commands if cmd.startswith(text)]
        return []
    
    def cleanup(self):
        """Clean up settings."""
        pass
    
    def show_completions(self, text: str) -> List[str]:
        """Show available completions for the given text (for testing)."""
        return self.get_suggestions(text)
    
    def _get_bottom_toolbar(self) -> str:
        """Generate clean bottom toolbar with token/cost info."""
        base_toolbar = " Enter: Send • Ctrl+J: Newline • /: Commands"
        
        if self.token_tracker:
            try:
                if hasattr(self.token_tracker, 'get_total_usage'):
                    usage = self.token_tracker.get_total_usage()
                    if usage:
                        total_tokens = getattr(usage, 'total_tokens', 0)
                        total_cost = getattr(usage, 'cost', 0.0)
                        if total_tokens > 0:
                            return f"{base_toolbar} • 📊 {total_tokens:,} tokens • 💰 ${total_cost:.4f}"
                        else:
                            return f"{base_toolbar} • 📊 0 tokens • 💰 $0.00"
                    else:
                        return f"{base_toolbar} • 📊 0 tokens • 💰 $0.00"
            except Exception:
                pass
        
        return base_toolbar



class WelcomeScreen:
    """Welcome screen display."""
    
    def __init__(self, config_manager: ConfigManager, system_status: SystemStatus):
        self.config_manager = config_manager
        self.system_status = system_status
        self.console = Console()
    
    def display(self) -> None:
        """Display welcome screen."""
        config = self.config_manager.load_config()
        status_info = self.system_status.get_status_info()
        
        # JUNO AI ASCII Art
        juno_ascii = """[bold cyan]
   ██ ██   ██ ███   ██  ██████      █████  ██ 
   ██ ██   ██ ████  ██ ██    ██    ██   ██ ██ 
   ██ ██   ██ ██ ██ ██ ██    ██    ███████ ██ 
██ ██ ██   ██ ██  ████ ██    ██    ██   ██ ██ 
 ███   █████  ██   ███  ██████     ██   ██ ██ 
[/bold cyan]"""
        
        self.console.print(juno_ascii)
        
        welcome_text = f"""[bold blue]Welcome to JUNO AI CLI![/bold blue]

[bold]Current Status:[/bold]
• [blue]Working Directory:[/blue] {status_info['workdir']}
• [blue]Git Status:[/blue] {status_info['git_status']}
• [blue]API Key:[/blue] {status_info['api_key_status']}
• [blue]Selected Editor:[/blue] {status_info['editor']}

"""
        
        if config.setup_completed:
            welcome_text += "[green]✓ Setup completed! You can use the chat interface or commands.[/green]"
        elif self.config_manager.has_api_key():
            welcome_text += "[green]🚀 Ready to chat! Setup optional - run setup wizard if you want to configure more features.[/green]"
        else:
            welcome_text += "[yellow]🔧 Set your API key with '/apikey' command to start chatting with AI assistant.[/yellow]"
        
        panel = Panel.fit(
            welcome_text,
            title="JUNO AI CLI",
            border_style="blue",
        )
        
        self.console.print(panel)


class PromptToolkitMixin:
    """Mixin class providing prompt_toolkit dialog helper methods."""
    
    # ------------------- prompt_toolkit selection helpers -------------------
    def _pt_select_sync(self, title: str, options: List[str]) -> Optional[str]:
        """Synchronous radiolist selection using prompt_toolkit if available.

        Returns selected option or None. Falls back to None if unavailable.
        """
        try:
            from prompt_toolkit.shortcuts import radiolist_dialog  # type: ignore
            items = [(opt, opt) for opt in options]
            dlg = radiolist_dialog(title=title, text="Use ↑/↓ and Enter", values=items, style=get_unified_pt_style())
            return dlg.run()
        except Exception:
            return None

    async def _pt_select_async(self, title: str, options: List[str]) -> Optional[str]:
        """Async radiolist selection using prompt_toolkit if available.

        Returns selected option or None. Falls back to None if unavailable.
        """
        try:
            from prompt_toolkit.shortcuts import radiolist_dialog  # type: ignore
            dlg = radiolist_dialog(title=title, text="Use ↑/↓ and Enter", values=[(o, o) for o in options], style=get_unified_pt_style())
            # Use async if available on this object
            if hasattr(dlg, "run_async"):
                return await dlg.run_async()
            # Else run in thread so we don't block the loop
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(None, dlg.run)
        except Exception:
            return None

    # Compatibility shim for a hypothetical `shortcuts.choice` API.
    # We try `choice` first (if present in your environment), then fall back to
    # `radiolist_dialog`, maintaining the same return contract (selected str or None).
    def _pt_choice_sync(self, title: str, options: List[Union[str, Tuple[str,str]]]) -> Optional[str]:
        """Synchronous choice returning the option value when provided.

        Accepts either list[str] or list[(value,label)]. If tuples are provided,
        returns the selected value; otherwise returns the selected string.
        """
        try:
            from prompt_toolkit.shortcuts import radiolist_dialog  # type: ignore
            values: List[Tuple[str, str]] = []
            for o in options:
                if isinstance(o, str):
                    values.append((o, o))
                else:
                    values.append((o[0], o[1]))
            dlg = radiolist_dialog(title=title, text="Use ↑/↓ and Enter", values=values, style=get_unified_pt_style())
            return dlg.run()
        except Exception:
            return None

    async def _pt_choice_async(self, title: str, options: List[Union[str, Tuple[str,str]]]) -> Optional[str]:
        """Async choice returning the option value when provided.

        Accepts either list[str] or list[(value,label)]. If tuples are provided,
        returns the selected value; otherwise returns the selected string.
        """
        try:
            from prompt_toolkit.shortcuts import radiolist_dialog  # type: ignore
            values: List[Tuple[str, str]] = []
            for o in options:
                if isinstance(o, str):
                    values.append((o, o))
                else:
                    values.append((o[0], o[1]))
            dlg = radiolist_dialog(title=title, text="Use ↑/↓ and Enter", values=values, style=get_unified_pt_style())
            if hasattr(dlg, "run_async"):
                return await dlg.run_async()
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(None, dlg.run)
        except Exception:
            # Fallback to simple select with labels
            try:
                labels = [o if isinstance(o, str) else o[1] for o in options]
                return await self._pt_select_async(title, labels)
            except Exception:
                return None

    def _pt_input_sync(self, title: str, text: str, password: bool = False) -> Optional[str]:
        """Synchronous input dialog using prompt_toolkit if available."""
        try:
            if password:
                # input_dialog doesn't mask by default; use PromptSession as a fallback
                from prompt_toolkit import PromptSession  # type: ignore
                sess = PromptSession()
                return sess.prompt(f"{text}: ", is_password=True)
            from prompt_toolkit.shortcuts import input_dialog  # type: ignore
            dlg = input_dialog(title=title, text=text, style=get_unified_pt_style())
            return dlg.run()
        except Exception:
            return None

    async def _pt_input_async(self, title: str, text: str, password: bool = False) -> Optional[str]:
        """Async input dialog using prompt_toolkit if available."""
        try:
            # Prefer dialog if available
            from prompt_toolkit.shortcuts import input_dialog  # type: ignore
            dlg = input_dialog(title=title, text=text, style=get_unified_pt_style())
            if hasattr(dlg, "run_async"):
                return await dlg.run_async()
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(None, dlg.run)
        except Exception:
            # Fallback to session prompt
            try:
                from prompt_toolkit import PromptSession  # type: ignore
                sess = PromptSession()
                if password:
                    return await sess.prompt_async(f"{text}: ", is_password=True)
                return await sess.prompt_async(f"{text}: ")
            except Exception:
                return None

    def _pt_confirm_sync(self, title: str, text: str) -> Optional[bool]:
        """Synchronous yes/no dialog using prompt_toolkit if available."""
        try:
            from prompt_toolkit.shortcuts import yes_no_dialog  # type: ignore
            dlg = yes_no_dialog(title=title, text=text, style=get_unified_pt_style())
            return bool(dlg.run())
        except Exception:
            return None

    async def _pt_confirm_async(self, title: str, text: str) -> Optional[bool]:
        """Async yes/no dialog using prompt_toolkit if available."""
        try:
            from prompt_toolkit.shortcuts import yes_no_dialog  # type: ignore
            dlg = yes_no_dialog(title=title, text=text, style=get_unified_pt_style())
            if hasattr(dlg, "run_async"):
                res = await dlg.run_async()
                return bool(res)
            loop = asyncio.get_running_loop()
            res = await loop.run_in_executor(None, dlg.run)
            return bool(res)
        except Exception:
            return None

    def _simple_ui_tool_update_callback(self, message_type: str, data: Dict[str, Any]) -> None:
        """Render Juno Agent tool-call updates during setup for Simple UI.

        Receives events from TextualToolCallback via the shared pipeline resolver.
        """
        try:
            tool_name = data.get("tool_name") or data.get("name") or "tool"
            if message_type == "tool_start":
                self.console.print(f"[dim]🛠️ Tool Call:[/dim] {tool_name}")
            elif message_type == "tool_end":
                # Show short result status if error detection ran upstream
                error = data.get("error")
                if error:
                    self.console.print(f"[red]❌ Tool Error:[/red] {tool_name} — {error}")
                else:
                    self.console.print(f"[green]✅ Tool Completed:[/green] {tool_name}")
            else:
                # Generic fallback
                self.console.print(f"[cyan]🔧 {message_type}[/cyan]: {tool_name}")
        except Exception:
            # Best-effort; never break setup flow due to UI printing
            pass

    def _run_setup_pipeline_with_ui(self, project_description: str = None) -> Dict[str, Any]:
        """Run the shared setup pipeline with UI components.
        
        Handles:
        - Editor selection
        - Progress checklist display  
        - Pipeline execution
        - Completion summary
        
        Returns the pipeline result dict.
        """
        from .setup.pipeline import run_setup_pipeline
        from rich.table import Table
        from rich.prompt import Prompt
        from pathlib import Path

        workdir = Path.cwd()
        cfg = self.config_manager.load_config()
        
        # Prompt for IDE/editor selection using fancy UI's editor functions
        try:
            editor_display_names = get_editor_display_names()
            supported_editor_ids = list(editor_display_names.keys())
            supported_editor_display_names = list(editor_display_names.values())
        except Exception:
            # Fallback to hardcoded list if fancy UI functions fail
            editor_display_names = {
                'claude_code': 'Claude Code',
                'cursor': 'Cursor', 
                'windsurf': 'Windsurf',
                'vscode': 'VS Code'
            }
            supported_editor_ids = list(editor_display_names.keys())
            supported_editor_display_names = list(editor_display_names.values())

        self.console.print("\n[bold]Step 2: Editor Selection[/bold]")
        editor_id = ""
        editor_display = cfg.editor or ""
        
        # Prefer prompt_toolkit choice (styled, async to avoid run_async warnings); fallback to numeric
        try:
            choice_val = _run_coro_in_thread(self._pt_choice_async("Select IDE/Editor", [(name, name) for name in supported_editor_display_names] + [("__other__", "Other")]))
        except Exception:
            choice_val = None
            
        if choice_val:
            if choice_val == "__other__":
                editor_display = (self._pt_input_sync("Editor", "Enter editor name") or "").strip() or ("Cursor" if (workdir / ".cursor").exists() else "Claude Code")
                # Try to map back to an ID if possible
                editor_id = next((eid for eid, name in editor_display_names.items() if name == editor_display), editor_display.lower().replace(' ', '_'))
            else:
                # Map display name back to editor ID
                editor_id = next((eid for eid, name in editor_display_names.items() if name == choice_val), choice_val.lower().replace(' ', '_'))
                editor_display = choice_val
        else:
            # Fallback numeric selection
            table = Table(show_header=True, header_style="bold cyan")
            table.add_column("#", style="cyan", width=3)
            table.add_column("Editor", style="green")
            for i, ed in enumerate(supported_editor_display_names, 1):
                table.add_row(str(i), ed)
            table.add_row(str(len(supported_editor_display_names) + 1), "Other")
            self.console.print(table)
            
            try:
                idx = int(Prompt.ask("Select editor by number", default="1"))
                if 1 <= idx <= len(supported_editor_display_names):
                    editor_display = supported_editor_display_names[idx - 1]
                    editor_id = supported_editor_ids[idx - 1]
                elif idx == len(supported_editor_display_names) + 1:
                    try:
                        editor_display = (_run_coro_in_thread(self._pt_input_async("Editor", "Enter editor name")) or "").strip() or ("Cursor" if (workdir / ".cursor").exists() else "Claude Code")
                        editor_id = next((eid for eid, name in editor_display_names.items() if name == editor_display), editor_display.lower().replace(' ', '_'))
                    except Exception:
                        editor_display = "Cursor" if (workdir / ".cursor").exists() else "Claude Code"
                        editor_id = "cursor" if (workdir / ".cursor").exists() else "claude_code"
            except Exception:
                if not editor_display:
                    editor_display = "Cursor" if (workdir / ".cursor").exists() else "Claude Code"
                    editor_id = "cursor" if (workdir / ".cursor").exists() else "claude_code"

        # Optional project description prompt (if not provided)
        if project_description is None:
            try:
                proj_desc = _run_coro_in_thread(self._pt_input_async("Project Description", "Optional: project description for docs (leave empty to skip)")) or ""
                proj_desc = proj_desc.strip()
            except Exception:
                proj_desc = ""
        else:
            proj_desc = project_description or ""

        # Display intro with progress checklist
        intro = (
            "[bold]🚀 Unified Setup Pipeline[/bold]\n\n"
            "Running the same setup process as headless/TUI.\n\n"
            "Progress Checklist (will remain visible):\n"
            "- [ ] Scan project\n"
            "- [ ] External context init\n"
            "- [ ] Agentic docs fetch\n"
            "- [ ] Generate JUNO.md + IDE docs\n"
            "- [ ] MCP install\n"
            "- [ ] Persist config\n"
            "- [ ] Verify\n"
        )
        self.console.print(intro)

        # Run pipeline in a worker thread to avoid nested asyncio loop issues
        result = _run_call_in_daemon_thread(
            run_setup_pipeline,
            workdir,
            self.config_manager,
            editor_display,
            self.config_manager.create_debug_logger(debug=True),
            None,
            self._simple_ui_tool_update_callback,
            project_description=proj_desc or None,
        )
        
        # Display completion summary
        completed = (
            "\n[bold green]✅ Setup Completed[/bold green]\n\n"
            "- [x] Scan project\n"
            "- [x] External context init\n"
            "- [x] Agentic docs fetch\n"
            "- [x] Generate JUNO.md + IDE docs\n"
            "- [x] MCP install\n"
            "- [x] Persist config\n"
            "- [x] Verify\n"
        )
        summary = (
            f"\n[bold]Verification Summary[/bold]\n"
            f"PASS: {result['pass']}  FAIL: {result['fail']}  WARN: {result['warn']}  INFO: {result['info']}\n"
        )
        self.console.print(completed + summary)
        
        return result


class ChatInterface(PromptToolkitMixin):
    """Interactive chat interface."""
    
    def __init__(self, config_manager: ConfigManager, debug: bool = False):
        self.config_manager = config_manager
        self.debug = debug
        self.console = Console()
        self.commands = ["/apikey", "/editor", "/reset", "/setup", "/scan", "/agent", "/model", "/continue", "/config", "/cleanup", "/help", "/exit"]
        self.mcp_installer = MCPServerInstaller(config_manager.workdir)
        self.scanner = ProjectScanner(config_manager.workdir)
        self.tiny_agent = TinyAgentChat(config_manager)
        self.analysis_agent = ProjectAnalysisAgent(config_manager)
        
        # Initialize storage manager for session persistence (same as Fancy UI)
        try:
            self.storage_manager = AsyncConversationStorageManager()
        except Exception as e:
            # If storage manager fails to initialize, continue without it
            print(f"[DEBUG] ChatInterface.__init__: Failed to create storage manager: {e}")
            self.storage_manager = None
        
        # Configure logging for TinyAgent to redirect to app_run.log
        import logging
        
        # Configure tinyagent logger to go to file only
        tiny_logger = logging.getLogger('tinyagent')
        tiny_logger.setLevel(logging.WARNING)  # Only log warnings and errors
        tiny_logger.propagate = False  # Don't propagate to root logger
        
        # Remove any existing console handlers
        tiny_logger.handlers = [h for h in tiny_logger.handlers if not isinstance(h, logging.StreamHandler)]
        
        # Add file handler for app_run.log
        log_file = config_manager.workdir / 'app_run.log'
        if not tiny_logger.handlers or not any(isinstance(h, logging.FileHandler) for h in tiny_logger.handlers):
            file_handler = logging.FileHandler(log_file, mode='a')
            file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            tiny_logger.addHandler(file_handler)
        
        
        # Create TinyCodeAgentChat with console for SimpleUI tool callback detection and storage manager
        self.tiny_code_agent = TinyCodeAgentChat(
            config_manager, 
            debug=self.debug,
            console=self.console,  # This enables SimpleUIToolCallback auto-detection
            storage_manager=self.storage_manager  # Add storage manager for session persistence
        )
        self.tiny_manager = TinyCodeAgentManager(config_manager)
        self.token_tracker = None  # Will be set when TinyAgent is initialized
        self.autocomplete_input = AutoCompleteInput(self.commands, token_tracker=None)

    def _configure_editor(self) -> None:
        """Synchronous wrapper to configure editor using the async /editor flow."""
        _run_coro_in_thread(self._handle_editor_command())

    def _print_command_palette_hint(self) -> None:
        try:
            cmds = self.autocomplete_input.commands
            sample = cmds[:8]
            if not sample:
                self.console.print("[dim]No commands available[/dim]")
                return
            width = max(24, min(80, max(len(c) for c in sample) + 4))
            horiz = "─" * (width - 2)
            self.console.print("┌" + horiz + "┐")
            for c in sample:
                line = (c + " " * (width - 4))[: width - 4]
                self.console.print("│ " + line.ljust(width - 4) + " │")
            more = len(cmds) - len(sample)
            if more > 0:
                self.console.print("│ " + (f"… +{more} more").ljust(width - 4) + " │")
            self.console.print("└" + horiz + "┘")
            self.console.print("[dim]Tip: Type '/' then keep typing; press Tab to cycle, Enter to apply[/dim]")
        except Exception:
            self.console.print("[dim]Type '/' then Tab to see command suggestions[/dim]")

    # Removed curses-based inline palette to avoid alternate-screen UX; relying on readline palette
    
    async def run_with_tiny_default(self) -> None:
        """Run chat interface with TinyAgent as default for messages."""
        config = self.config_manager.load_config()
        
        # Check if we can initialize TinyAgent  
        status = self.tiny_manager.check_requirements()
        
        # Always try to use TinyAgent mode if possible, regardless of setup completion
        if status["can_initialize"]:
            await self._run_tiny_agent_mode()
        else:
            # Fall back to regular chat interface with helpful message
            await self._run_with_tiny_fallback()
    
    async def _run_with_tiny_fallback(self) -> None:
        """Run regular chat but with TinyAgent setup guidance."""
        # Show why TinyAgent isn't available and how to set it up
        status = self.tiny_manager.check_requirements()
        status_info = self.tiny_manager.get_status_info()
        
        fallback_message = f"""[bold yellow]⚠️ Juno Agent Not Available[/bold yellow]

[bold]Current Status:[/bold]
• OpenAI API Key: {status_info['openai_key']}
• TinyAgent Package: {status_info['tinyagent']}

[bold blue]To enable full AI coding assistant:[/bold blue]
1. Run [cyan]/setup[/cyan] to configure your API key
2. Restart the CLI to activate Juno Agent mode

[dim]For now, you can use basic commands like /help, /setup, /model[/dim]"""
        
        fallback_panel = Panel(
            fallback_message,
            title="[bold]🤖 AI Assistant Setup Needed[/bold]",
            border_style="yellow",
            padding=(1, 2)
        )
        self.console.print(fallback_panel)
        
        # Run regular interface
        await self.run()
    
    def _show_tiny_status(self) -> None:
        """Show Juno Agent status information."""
        status = self.tiny_manager.check_requirements()
        status_info = self.tiny_manager.get_status_info()
        
        if status["can_initialize"]:
            status_message = """[bold green]✅ Juno Agent is Active![/bold green]

[bold]Current Status:[/bold]
• OpenAI API Key: {openai_key}
• TinyAgent Package: {tinyagent}
• Model: {model}
• Provider: {provider}

[bold blue]How it works:[/bold blue]
• Just type your questions naturally
• Juno Agent processes all non-command messages
• Use [cyan]/help[/cyan] to see available commands

[dim]Juno Agent is your default AI coding assistant![/dim]""".format(**status_info)
        else:
            status_message = """[bold yellow]⚠️ Juno Agent Not Available[/bold yellow]

[bold]Current Status:[/bold]
• OpenAI API Key: {openai_key}
• TinyAgent Package: {tinyagent}

[bold blue]To activate Juno Agent:[/bold blue]
1. Run [cyan]/setup[/cyan] to configure missing requirements
2. Restart juno-agent

[dim]Once set up, Juno Agent will be your default AI assistant![/dim]""".format(**status_info)
        
        status_panel = Panel(
            status_message,
            title="[bold]🤖 Juno Agent Status[/bold]",
            border_style="cyan",
            padding=(1, 2)
        )
        self.console.print(status_panel)
    
    async def _run_tiny_agent_mode(self) -> None:
        """Run chat interface with Juno Agent as default processor."""
        config = self.config_manager.load_config()
        status_indicators = []
        
        if self.config_manager.has_api_key():
            status_indicators.append("🔑 API ✓")
        else:
            status_indicators.append("[dim]🔑 API ✗[/dim]")
            
        if config.editor:
            status_indicators.append(f"📝 {config.editor}")
        else:
            status_indicators.append("[dim]📝 None[/dim]")
            
        if config.mcp_server_installed:
            status_indicators.append("🔗 MCP ✓")
        else:
            status_indicators.append("[dim]🔗 MCP ✗[/dim]")
        
        status_bar = " │ ".join(status_indicators)
        
        # Clean minimal header
        header_content = f"""[dim]╭─ juno-agent ─ AI Coding Assistant ────────────────────╮[/dim]
[dim]│[/dim] {status_bar: <55} [dim]│[/dim]
[dim]╰───────────────────────────────────────────────────────╯[/dim]"""
        
        self.console.print(header_content)
        
        # Minimal capabilities display
        capabilities_content = """💬 Just type your questions - Juno Agent will help!
⚡ Commands starting with [bold]'/'[/bold] trigger system functions"""
        
        capabilities_panel = Panel(
            capabilities_content,
            border_style="dim",
            padding=(0, 1)
        )
        self.console.print(capabilities_panel)
        
        # Initialize TinyAgent
        try:
            await self.tiny_code_agent.initialize_agent()
            # Pass token tracker to autocomplete input for bottom toolbar
            if hasattr(self.tiny_code_agent, 'token_tracker') and self.tiny_code_agent.token_tracker:
                self.autocomplete_input.token_tracker = self.tiny_code_agent.token_tracker
        except Exception as e:
            self._print_ai_response(f"❌ Failed to initialize Juno Agent: {str(e)}", "error")
            return
        
        # Update autocomplete to include Juno Agent commands
        combined_commands = self.commands + ["/cost", "/compact"]
        # Remove duplicates while preserving order
        seen = set()
        unique_commands = []
        for cmd in combined_commands:
            if cmd not in seen:
                seen.add(cmd)
                unique_commands.append(cmd)
        self.autocomplete_input.update_commands(unique_commands)
        
        self.console.print("\n")
        
        conversation_history = []
        
        while True:
            try:
                # Clean user input prompt
                user_input = (await self.autocomplete_input.ainput()).strip()
                
                if not user_input:
                    continue
                
                conversation_history.append(("user", user_input))
                
                # Handle exit
                if user_input == "/exit":
                    break
                
                # Handle system commands (starting with /)
                elif user_input.startswith("/"):
                    if user_input == "/help":
                        self._handle_help_command()
                    elif user_input == "/":
                        self._print_command_palette_hint()
                        continue
                    elif user_input == "/apikey":
                        await self._handle_apikey_command()
                    elif user_input == "/editor":
                        await self._handle_editor_command()
                    elif user_input == "/reset":
                        self._handle_reset_command()
                    elif user_input == "/setup":
                        self._handle_setup_command()
                    elif user_input == "/scan":
                        self._handle_scan_command()
                    elif user_input == "/agent":
                        self._handle_agent_command()
                    elif user_input == "/model":
                        await self._handle_model_command()
                    elif user_input == "/continue":
                        await self._handle_continue_command()
                    elif user_input == "/config":
                        self._handle_config_command()
                    elif user_input == "/cleanup":
                        self._handle_cleanup_command()
                    elif user_input == "/cost":
                        await self._handle_tiny_cost_command()
                    elif user_input == "/compact":
                        await self._handle_tiny_compact_command()
                    else:
                        # Unknown command
                        completions = self.autocomplete_input.show_completions(user_input)
                        if completions:
                            if len(completions) == 1 and completions[0] != user_input:
                                response = f"💡 Did you mean [bold cyan]'{completions[0]}'[/bold cyan]?"
                                self._print_ai_response(response, "suggestion")
                                conversation_history.append(("ai", response))
                            elif len(completions) > 1:
                                options_str = " [dim]│[/dim] ".join(f"[cyan]{cmd}[/cyan]" for cmd in completions)
                                response = f"🎯 Available options: {options_str}"
                                self._print_ai_response(response, "options")
                                conversation_history.append(("ai", response))
                            else:
                                response = f"❓ Unknown command: [red]{user_input}[/red] [dim]- Type '/help' for available commands[/dim]"
                                self._print_ai_response(response, "error")
                                conversation_history.append(("ai", response))
                        else:
                            response = f"❓ Unknown command: [red]{user_input}[/red] [dim]- Type '/help' for available commands[/dim]"
                            self._print_ai_response(response, "error")
                            conversation_history.append(("ai", response))
                
                else:
                    # Regular message - send to TinyAgent
                    try:
                        import time
                        import asyncio
                        
                        # Get model display name for thinking indicator
                        config = self.config_manager.load_config()
                        agent_config = config.agent_config
                        
                        # Use model_slug if available, otherwise extract model name
                        if agent_config.model_slug:
                            model_display = agent_config.model_slug.upper()
                        else:
                            # Extract the last part after "/" for model name (e.g., "gpt-4o" from "openai/gpt-4o")
                            model_display = agent_config.model_name.split("/")[-1].upper()
                        
                        # Show loading indicator with elapsed time
                        response = None
                        error = None
                        
                        async def process_with_loading():
                            nonlocal response, error
                            try:
                                response = await self.tiny_code_agent.process_chat_message(user_input)
                            except Exception as e:
                                error = e
                        
                        # Create progress indicator with custom elapsed seconds
                        start_time = time.time()
                        with Progress(
                            SpinnerColumn(),
                            TextColumn(f"[bold cyan]🤖 {model_display} thinking...[/bold cyan]"),
                            TextColumn("[dim]"),
                            console=self.console,
                            transient=True,  # Will disappear when done
                            refresh_per_second=10
                        ) as progress:
                            task = progress.add_task("Processing", total=None)
                            
                            try:
                                # Run the processing in background
                                process_task = asyncio.create_task(process_with_loading())
                                
                                # Wait for completion with progress updates showing elapsed seconds
                                while not process_task.done():
                                    elapsed = int(time.time() - start_time)
                                    progress.update(task, description=f"[bold cyan]🤖 {model_display} thinking...[/bold cyan] [dim]{elapsed}s[/dim]")
                                    await asyncio.sleep(0.1)
                                
                                await process_task
                            except Exception:
                                # Cancel the task if it's still running
                                if not process_task.done():
                                    process_task.cancel()
                                    try:
                                        await process_task
                                    except asyncio.CancelledError:
                                        pass
                                # Re-raise the exception after cleanup
                                raise
                        
                        # Handle the result
                        if error:
                            raise error
                        
                        # Update the token tracker reference after each message
                        if self.tiny_code_agent.agent:
                            if hasattr(self.tiny_code_agent, 'token_tracker') and self.tiny_code_agent.token_tracker:
                                self.token_tracker = self.tiny_code_agent.token_tracker
                                # Update the autocomplete input with the tracker
                                self.autocomplete_input.token_tracker = self.token_tracker
                        
                        # Display agent response
                        self.console.print(f"{response}")
                        conversation_history.append(("ai", response))
                    except Exception as e:
                        error_response = f"❌ Juno Agent error: {str(e)}"
                        self.console.print(f"[red]{error_response}[/red]")
                        conversation_history.append(("ai", error_response))
                
                # Visual separator
                self.console.print(f"\n[dim]{'─' * 50}[/dim]\n")
                
            except KeyboardInterrupt:
                break
            except EOFError:
                break
        
        # Save conversation and cleanup
        try:
            self.tiny_code_agent.save_conversation()
        except Exception:
            pass
        
        # Restore original commands for autocomplete
        self.autocomplete_input.update_commands(self.commands)
        self.autocomplete_input.cleanup()
        
        goodbye_panel = Panel.fit(
            "[bold yellow]Thanks for using JUNO AI![/bold yellow]\n\n"
            "Your Juno Agent session has been saved.",
            title="Goodbye",
            border_style="yellow",
            padding=(0, 1)
        )
        self.console.print(goodbye_panel)

    async def run(self) -> None:
        """Run the sophisticated chat interface."""
        # Create an elegant header with status
        config = self.config_manager.load_config()
        status_indicators = []
        
        if self.config_manager.has_api_key():
            status_indicators.append("[green]🔑 API[/green]")
        else:
            status_indicators.append("[red]🔑 API[/red]")
            
        if config.editor:
            status_indicators.append(f"[blue]📝 {config.editor}[/blue]")
        else:
            status_indicators.append("[dim]📝 No Editor[/dim]")
            
        if config.mcp_server_installed:
            status_indicators.append("[green]🔗 MCP[/green]")
        else:
            status_indicators.append("[dim]🔗 MCP[/dim]")
        
        status_bar = " │ ".join(status_indicators)
        
        # Sophisticated header with gradient-like effect
        header_content = f"""[bold cyan]╭─────────────────────────────────────────────────────────╮[/bold cyan]
[bold cyan]│[/bold cyan] [bold white]🧙‍♂️ juno-agent[/bold white] [dim cyan]- AI-Powered Development Assistant[/dim cyan] [bold cyan]│[/bold cyan]
[bold cyan]├─────────────────────────────────────────────────────────┤[/bold cyan]
[bold cyan]│[/bold cyan] {status_bar: <55} [bold cyan]│[/bold cyan]
[bold cyan]╰─────────────────────────────────────────────────────────╯[/bold cyan]"""
        
        self.console.print(header_content)
        
        # Enhanced status display
        if self.autocomplete_input.has_readline:
            self.console.print("  [green]✨ Enhanced tab completion active[/green] [dim]- Press Tab for intelligent suggestions[/dim]")
        else:
            self.console.print("  [yellow]⚡ Basic completion mode[/yellow] [dim]- Type / for command hints[/dim]")
        
        # Sophisticated commands display with grouping
        command_groups = {
            "Setup": ["/apikey", "/editor", "/setup"],
            "AI Tools": ["/agent", "/model"], 
            "Project": ["/scan"],
            "System": ["/cleanup", "/reset", "/help", "/exit"]
        }
        
        commands_display = []
        colors = ['blue', 'green', 'magenta', 'yellow']
        for i, (group, cmds) in enumerate(command_groups.items()):
            color = colors[i % len(colors)]
            group_str = f"[bold {color}]{group}:[/bold {color}] {' '.join(cmds)}"
            commands_display.append(group_str)
        
        commands_panel = Panel(
            "\n".join(commands_display),
            title="[bold]🎛️  Command Palette[/bold]",
            border_style="bright_blue",
            padding=(0, 1),
            expand=False
        )
        self.console.print(commands_panel)
        
        # Interactive tips with animation
        tips = [
            "💡 Type [blue]'/help'[/blue] for detailed command information",
            "🚀 Use [green]Tab[/green] to autocomplete commands and get suggestions",
            "🔍 Commands starting with [cyan]'/'[/cyan] trigger smart actions",
            "🤖 Try [magenta]'/agent'[/magenta] for advanced AI coding assistance",
            "💬 Regular text activates the AI chat assistant"
        ]
        
        tip_text = "\n".join(f"  {tip}" for tip in tips)
        tips_panel = Panel.fit(
            tip_text,
            title="[bold]📚 Quick Tips[/bold]",
            border_style="bright_cyan",
            padding=(0, 1)
        )
        self.console.print(tips_panel)
        
        self.console.print("\n[dim bright_blue]━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Chat Session ━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/dim bright_blue]\n")
        
        conversation_history = []
        
        while True:
            try:
                current_time = self._get_current_time()
                self.console.print(f"[dim]{current_time}[/dim] [dim]🧙‍♂️ You[/dim] │ ", end="")
                user_input = (await self.autocomplete_input.ainput()).strip()
                # Echo user input in gray after they submit it
                self.console.print(f"\r[dim]{current_time}[/dim] [dim]🧙‍♂️ You[/dim] │ [dim]{user_input}[/dim]")
                
                if not user_input:
                    continue
                
                # Add to conversation history
                conversation_history.append(("user", user_input))
                
                if user_input == "/exit":
                    break
                elif user_input == "/help":
                    self._handle_help_command()
                elif user_input == "/":
                    self._print_command_palette_hint()
                    continue
                elif user_input == "/apikey":
                    await self._handle_apikey_command()
                elif user_input == "/editor":
                    await self._handle_editor_command()
                elif user_input == "/reset":
                    self._handle_reset_command()
                elif user_input == "/setup":
                    self._handle_setup_command()
                elif user_input == "/scan":
                    self._handle_scan_command()
                elif user_input == "/agent":
                    self._handle_agent_command()
                elif user_input == "/model":
                    await self._handle_model_command()
                elif user_input == "/continue":
                    await self._handle_continue_command()
                elif user_input == "/config":
                    self._handle_config_command()
                elif user_input == "/cleanup":
                    self._handle_cleanup_command()
                elif user_input.startswith("/"):
                    if user_input == "/help":
                        self._handle_help_command()
                        continue
                    elif user_input == "/":
                        self._print_command_palette_hint()
                        continue
                    # Enhanced command suggestion with better UX
                    completions = self.autocomplete_input.show_completions(user_input)
                    if completions:
                        if len(completions) == 1 and completions[0] != user_input:
                            # Single completion suggestion with action prompt
                            response = f"💡 Did you mean [bold cyan]'{completions[0]}'[/bold cyan]? [dim](Type it or press Tab)[/dim]"
                            self._print_ai_response(response, "suggestion")
                            conversation_history.append(("ai", response))
                        elif len(completions) > 1:
                            # Multiple options with better formatting
                            options_str = " [dim]│[/dim] ".join(f"[cyan]{cmd}[/cyan]" for cmd in completions)
                            response = f"🎯 Available options: {options_str}"
                            self._print_ai_response(response, "options")
                            conversation_history.append(("ai", response))
                        else:
                            response = f"❓ Unknown command: [red]{user_input}[/red] [dim]- Type '/help' for available commands[/dim]"
                            self._print_ai_response(response, "error")
                            conversation_history.append(("ai", response))
                    else:
                        response = f"❓ Unknown command: [red]{user_input}[/red] [dim]- Type '/help' for available commands[/dim]"
                        self._print_ai_response(response, "error")
                        conversation_history.append(("ai", response))
                else:
                    # Process with AI agent
                    try:
                        # Get project context for better responses
                        project_context = {
                            "workdir": str(self.config_manager.workdir),
                            "has_api_key": self.config_manager.has_api_key(),
                            "editor": self.config_manager.load_config().editor,
                            "libraries": self.config_manager.load_config().libraries or []
                        }
                        
                        # Process with TinyAgent
                        ai_response = await self.tiny_agent.process_chat_message(user_input, project_context)
                        
                        self._print_ai_response(ai_response, "normal")
                        conversation_history.append(("ai", ai_response))
                        
                    except Exception as e:
                        error_response = f"🔧 AI processing temporarily unavailable: {str(e)}\n   [dim]Use commands starting with '/' for full functionality.[/dim]"
                        self._print_ai_response(error_response, "error")
                        conversation_history.append(("ai", error_response))
                
                # Enhanced visual separator with conversation count
                conv_count = len([h for h in conversation_history if h[0] == "user"])
                self.console.print(f"[dim bright_blue]{'─' * 45} [{conv_count} exchanges] {'─' * 10}[/dim bright_blue]")
                
            except KeyboardInterrupt:
                break
            except EOFError:
                break
        
        # Save conversation history
        try:
            self.tiny_agent.save_conversation()
        except Exception as e:
            # Don't let saving errors affect exit
            pass
        
        # Clean up autocomplete
        self.autocomplete_input.cleanup()
        
        # Clean up storage manager
        if hasattr(self, 'storage_manager') and self.storage_manager:
            try:
                self.storage_manager.close()
            except Exception:
                pass
        
        # Show a nice goodbye message
        goodbye_panel = Panel.fit(
            "[bold yellow]Thanks for using juno-agent![/bold yellow]\n\n"
            "Your configuration has been saved and will be available next time you run the CLI.",
            title="Goodbye",
            border_style="yellow",
            padding=(0, 1)
        )
        self.console.print(goodbye_panel)
    
    def _get_current_time(self) -> str:
        """Get current time formatted for display."""
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")
    
    def _print_ai_response(self, response: str, response_type: str = "normal") -> None:
        """Print AI response with appropriate styling based on type."""
        current_time = self._get_current_time()
        
        # Choose emoji and color based on response type
        type_styles = {
            "suggestion": ("[bold green]💡 AI[/bold green]", "yellow"),
            "options": ("[bold blue]🎯 AI[/bold blue]", "cyan"),
            "error": ("[bold red]❌ AI[/bold red]", "red"),
            "info": ("[bold magenta]🤖 AI[/bold magenta]", "dim"),
            "success": ("[bold green]✅ AI[/bold green]", "green"),
            "normal": ("[bold green]🤖 AI[/bold green]", "white")
        }
        
        ai_prefix, color = type_styles.get(response_type, type_styles["normal"])
        self.console.print(f"[dim]{current_time}[/dim] {ai_prefix} │ [{color}]{response}[/{color}]")
    
    def _handle_help_command(self) -> None:
        """Handle /help command with enhanced formatting."""
        # Create a comprehensive help display
        help_sections = [
            {
                "title": "🎛️  Setup Commands",
                "commands": [
                    ("/apikey", "Set or update your ASKBUDI API key"),
                    ("/editor", "Select or change your preferred code editor"),
                    ("/setup", "Run the complete setup wizard")
                ],
                "color": "blue"
            },
            {
                "title": "🤖 AI Tools", 
                "commands": [
                    ("/agent", "Configure AI agent settings and project analysis"),
                    ("/model", "Configure AI model, provider, and API keys"),
                    ("/continue", "Resume Juno Agent session when max turns reached")
                ],
                "color": "green"
            },
            {
                "title": "🔍 Project Management", 
                "commands": [
                    ("/scan", "Scan project for dependencies and technologies")
                ],
                "color": "magenta"
            },
            {
                "title": "⚙️  System Commands",
                "commands": [
                    ("/config", "View and modify configuration settings"),
                    ("/cleanup", "Clear the screen and show current status"),
                    ("/reset", "Reset all configuration to defaults"),
                    ("/help", "Show this detailed help message"),
                    ("/exit", "Exit the application")
                ],
                "color": "yellow"
            }
        ]
        
        help_content = []
        for section in help_sections:
            section_lines = [f"[bold {section['color']}]{section['title']}[/bold {section['color']}]"]
            for cmd, desc in section["commands"]:
                section_lines.append(f"  [bold cyan]{cmd:8}[/bold cyan] │ {desc}")
            help_content.append("\n".join(section_lines))
        
        # Usage tips with better formatting
        tips_content = """[bold bright_magenta]💡 Usage Tips[/bold bright_magenta]
  [green]•[/green] [bold]Just type your questions![/bold] Juno Agent AI is active by default
  [green]•[/green] Commands starting with [bold cyan]/[/bold cyan] trigger system functions  
  [green]•[/green] Type [bold blue]/[/bold blue] and press [bold]Tab[/bold] for intelligent autocompletion
  [green]•[/green] Use [bold]↑/↓ arrows[/bold] to navigate command history
  [green]•[/green] Press [bold]Ctrl+C[/bold] anytime to exit"""
        
        # Getting started workflow
        workflow_content = """[bold bright_cyan]🚀 Quick Start Workflow[/bold bright_cyan]
  [bold]1.[/bold] Run [bold blue]/setup[/bold blue] to configure your API key and workspace
  [bold]2.[/bold] Start chatting! Juno Agent AI assistant is ready by default
  [bold]3.[/bold] Use [bold green]/scan[/bold green] to analyze your project structure  
  [bold]4.[/bold] Install MCP server integration with [bold blue]/editor[/bold blue] command"""
        
        # Combine all help content
        full_help = "\n\n".join([
            "\n".join(help_content),
            tips_content,
            workflow_content,
            "[dim]📚 Documentation: https://askbudi.ai/docs[/dim]"
        ])
        
        # Display in an elegant panel
        help_panel = Panel(
            full_help,
            title="[bold white]🧙‍♂️ juno-agent Help Guide[/bold white]",
            border_style="bright_blue",
            padding=(1, 2),
            expand=True
        )
        
        self._print_ai_response("Here's the complete help guide:", "info")
        self.console.print(help_panel)
    
    async def _handle_apikey_command(self) -> None:
        """Handle /apikey command with enhanced feedback."""
        self._print_ai_response("🔑 Managing your ASKBUDI API key...", "info")
        
        if self.config_manager.has_api_key():
            self._print_ai_response("API key is already configured.", "success")
            if (await self._pt_confirm_async("API Key", "Update your API key?") or False):
                api_key = getpass.getpass("🔐 Enter new API key (input hidden): ")
                if api_key.strip():
                    # Validate with backend if possible
                    self.console.print("🔍 [blue]Validating API key...[/blue]")
                    try:
                        validation_result = await self.config_manager.validate_api_key_with_backend(api_key.strip())
                        if validation_result.get("valid"):
                            # Ask for scope
                            scope = self.config_manager.prompt_config_scope("API Key", is_model_config=True)
                            self.config_manager.set_api_key_with_scope(api_key.strip(), scope=scope)
                            user_level = validation_result.get("user_level", "unknown")
                            scope_text = "globally" if scope == "global" else "locally"
                            self._print_ai_response(f"✅ API key updated {scope_text}! (Level: {user_level})", "success")
                        else:
                            error = validation_result.get("error", "Unknown error")
                            self._print_ai_response(f"❌ API key validation failed: {error}", "error")
                    except Exception as e:
                        self._print_ai_response(f"⚠️ Could not validate API key: {e}", "error")
                        if (await self._pt_confirm_async("API Key", "Save API key anyway?") or False):
                            # Ask for scope
                            scope = self.config_manager.prompt_config_scope("API Key", is_model_config=True)
                            self.config_manager.set_api_key_with_scope(api_key.strip(), scope=scope)
                            scope_text = "globally" if scope == "global" else "locally"
                            self._print_ai_response(f"💾 API key saved {scope_text} (validation pending)", "info")
                else:
                    self._print_ai_response("❌ Invalid API key - operation cancelled", "error")
        else:
            self._print_ai_response("No API key found. Let's set one up!", "info")
            self.console.print("\n🌐 [dim]Get your API key from: https://askbudi.ai[/dim]")
            
            api_key = getpass.getpass("🔐 Enter your API key (input hidden): ")
            if api_key.strip():
                # Ask for scope
                scope = self.config_manager.prompt_config_scope("API Key", is_model_config=True)
                self.config_manager.set_api_key_with_scope(api_key.strip(), scope=scope)
                scope_text = "globally" if scope == "global" else "locally"
                self._print_ai_response(f"✅ API key saved {scope_text}!", "success")
            else:
                self._print_ai_response("❌ Invalid API key - operation cancelled", "error")
    
    async def _handle_editor_command(self) -> None:
        """Handle /editor command."""
        config = self.config_manager.load_config()
        current_editor = config.editor or "None"
        self.console.print(f"Current editor: {current_editor}")
        
        if not (await self._pt_confirm_async("Editor", "Change editor?") or False):
            return

        # Fetch supported editors using fancy UI functions
        try:
            editor_display_names = get_editor_display_names()
            supported_editor_ids = list(editor_display_names.keys())
            supported_editor_display_names = list(editor_display_names.values())
        except Exception:
            # Fallback to hardcoded list if fancy UI functions fail
            editor_display_names = {
                'claude_code': 'Claude Code',
                'cursor': 'Cursor', 
                'windsurf': 'Windsurf',
                'vscode': 'VS Code'
            }
            supported_editor_ids = list(editor_display_names.keys())
            supported_editor_display_names = list(editor_display_names.values())

        choice = await self._pt_choice_async(
            "Select IDE/Editor",
            [(name, name) for name in supported_editor_display_names] + [("__other__", "Other")]
        )

        if not choice:
            self._print_ai_response("Editor selection cancelled.", "info")
            return

        if choice == "__other__":
            entered = await self._pt_input_async("Editor", "Enter editor name")
            selected_editor = (entered or "").strip()
            if not selected_editor:
                self._print_ai_response("❌ Editor name cannot be empty", "error")
                return
            # Try to map to an ID for consistency
            selected_editor_id = next((eid for eid, name in editor_display_names.items() if name == selected_editor), selected_editor.lower().replace(' ', '_'))
        else:
            selected_editor = choice
            # Map display name back to editor ID
            selected_editor_id = next((eid for eid, name in editor_display_names.items() if name == choice), choice.lower().replace(' ', '_'))

        # Save editor selection (display name for user-facing config)
        self.config_manager.update_config(editor=selected_editor)
        self._print_ai_response(f"✅ Editor set to {selected_editor}", "success")

        # Offer MCP install if supported and key present (use editor ID for MCP operations)
        if selected_editor_id in supported_editor_ids and self.config_manager.has_api_key():
            if (await self._pt_confirm_async("MCP Install", f"Install MCP server for {selected_editor}?") or False):
                api_key = self.config_manager.get_api_key()
                success, message = self.mcp_installer.install_mcp_server(selected_editor_id, api_key)
                if success:
                    self._print_ai_response(message, "success")
                    self.config_manager.update_config(mcp_server_installed=True)
                else:
                    self._print_ai_response(message, "error")
    
    async def _handle_model_command(self) -> None:
        """Handle /model command for configuring AI models."""
        import getpass
        
        self._print_ai_response("🤖 AI Model Configuration", "info")
        
        config = self.config_manager.load_config()
        agent_config = config.agent_config
        
        # Display current configuration
        current_config_content = f"""[bold]🔧 Current Configuration[/bold]
        
• **Model**: {agent_config.model_name}
• **Provider**: {agent_config.provider}
• **Temperature**: {agent_config.temperature}
• **Max Tokens**: {agent_config.max_tokens or 'Auto'}
• **API Key**: {'✅ Set' if self.config_manager.get_model_api_key() else '❌ Missing'}
• **Base URL**: {agent_config.custom_base_url or 'Default'}

[bold]🌟 Supported Providers[/bold]
• **OpenAI**: gpt-5, gpt-5-mini, o3, o4-mini
• **Anthropic**: claude-4-sonnet-20250514, claude-4-haiku
• **Google**: gemini-2.5-pro, gemini-2.5-flash
• **Groq**: moonshotai/kimi-k2-instruct, qwen-coder
• **Cohere**: command-r-plus, command-r, command-light
• **Hugging Face**: Any model ID (e.g., microsoft/DialoGPT-medium)
• **Local/Custom**: Any LiteLLM compatible endpoint"""
        
        config_panel = Panel(
            current_config_content,
            title="[bold]🤖 AI Model Dashboard[/bold]",
            border_style="bright_green",
            padding=(1, 2)
        )
        self.console.print(config_panel)
        
        # Interactive configuration options
        self._print_ai_response("Available actions:", "info")
        
        options = [
            ("1", "Change model/provider"),
            ("2", "Set API key for current model"),
            ("3", "Adjust parameters (temperature, max_tokens)"),
            ("4", "Set custom base URL"),
            ("5", "Reset to defaults"),
            ("q", "Back to main chat")
        ]
        
        for option, description in options:
            self.console.print(f"  [cyan]{option}[/cyan]. {description}")
        
        choice = await self._pt_choice_async(
            "Model Actions",
            [(o, d) for (o, d) in options]
        ) or "1"
        
        if choice == "1":
            await self._configure_model_and_provider()
        elif choice == "2":
            self._configure_model_api_key()
        elif choice == "3":
            self._configure_model_parameters()
        elif choice == "4":
            self._configure_custom_base_url()
        elif choice == "5":
            self._reset_model_config()
        elif choice.lower() == "q":
            self._print_ai_response("Model configuration cancelled.", "info")
        else:
            self._print_ai_response("Invalid option selected.", "error")
    
    async def _configure_model_and_provider(self) -> None:
        """Configure model and provider using interactive selector."""
        self._print_ai_response("🎯 Model & Provider Configuration", "info")
        
        # Load models from the same source as TUI (models.json)
        models = self._load_models_from_tui_config()
        if not models:
            # Fallback to previous backend fetch and presets
            models = self._fetch_models_from_backend() or []
            if not models:
                self._print_ai_response("⚠️ No models available", "warning")
                return
        
        # Add custom option
        custom_model = {
            "id": "custom",
            "name": "Custom Model",
            "model_name": "custom",
            "provider": "custom",
            "temperature": 0.7,
            "description": "Enter custom model and provider",
            "cost_tier": "standard"
        }
        display_models = models + [custom_model]
        
        # Simple UI: prompt_toolkit radiolist if available; else fallback numeric
        try:
            # Build choice list: (value, label)
            label_map = [
                f"{m.get('provider','')}: {m.get('display_name') or m.get('name') or m.get('model_name')} ({m.get('model_name') or m.get('id')})"
                for m in models
            ]
            option_pairs = [(label_map[i], label_map[i]) for i in range(len(models))]
            option_pairs.append(("__custom__", "Custom Model"))
            # Prefer `choice` API; fallback to radiolist
            selected_value = await self._pt_choice_async("Select Model", option_pairs)
            if not selected_value:
                # Fallback numeric selection
                table = Table(show_header=True, header_style="bold cyan")
                table.add_column("#", style="cyan", width=3)
                table.add_column("Model", style="green")
                for i, lbl in enumerate(label_map + ["Custom Model"], 1):
                    table.add_row(str(i), lbl)
                self.console.print(table)
                num = Prompt.ask("Select model by number", default="1")
                try:
                    idxnum = int(num)
                    selected_value = "__custom__" if idxnum == len(label_map) + 1 else label_map[idxnum - 1]
                except Exception:
                    self._print_ai_response("❌ Invalid selection", "error")
                    return
            if selected_value == "__custom__":
                # Custom model entry
                self.console.print("\n[bold]📝 Custom Model Configuration[/bold]")
                model_name = await self._pt_input_async("Model Name", "Enter model name (LiteLLM format)") or ""
                provider = await self._pt_input_async("Provider", "Enter provider (e.g., openai)") or "openai"
                temp_str = await self._pt_input_async("Temperature", "0.0-2.0", False) or "0.7"
                try:
                    temperature = float(temp_str)
                except ValueError:
                    temperature = 1.0
                # For custom models, use model_name as slug and empty model_kwargs
                model_slug = model_name
                model_kwargs = {}
            else:
                # Find model by label
                try:
                    idx = label_map.index(selected_value)
                except ValueError:
                    self._print_ai_response("❌ Selection not found", "error")
                    return
                selected_model = models[idx]
                model_name = selected_model.get("model_name") or selected_model.get("id") or "gpt-5-mini"
                provider = (selected_model.get("provider") or "openai").lower()
                temperature = float(selected_model.get("temperature", 0.7))
                # Extract model_slug and model_kwargs like fancy UI does
                model_slug = selected_model.get("slug", model_name)
                model_kwargs = selected_model.get("model_kwargs", {})
            
            # Ask for configuration scope (choice)
            scope = await self._pt_choice_async(
                "Apply configuration scope",
                [("project", "This project only"), ("global", "Global (all projects)")]
            ) or "project"
            
            # Get the correct API key environment variable for this provider
            api_key_env_var = self._get_expected_env_var(provider)
            
            # Update configuration with scope - include all parameters like fancy UI
            update_params = {
                "scope": scope,
                "model_name": model_name,
                "model_slug": model_slug,
                "provider": provider,
                "temperature": temperature,
                "api_key_env_var": api_key_env_var
            }
            
            # Add model_kwargs if provided (non-empty)
            if model_kwargs:
                update_params["model_kwargs"] = model_kwargs
            
            self.config_manager.update_agent_config_with_scope(**update_params)
            
            scope_text = "globally" if scope == "global" else "for this project"
            # Use model_slug for display if available, otherwise fallback to model_name (like fancy UI does)
            display_name = model_slug if model_slug and model_slug != model_name else model_name
            self._print_ai_response(f"✅ Model updated to {display_name} ({provider}) {scope_text}", "success")
            
            # Ask if they want to set API key (choice)
            want_key = await self._pt_confirm_async("API Key", f"Set API key for {provider} now?")
            if want_key:
                # Show expected variable and get key
                expected_env = self._get_expected_env_var(provider)
                key = await self._pt_input_async("API Key", f"Enter {expected_env}", password=True)
                if key and key.strip():
                    self.config_manager.set_model_api_key_with_scope(key.strip(), scope=scope, key_name=expected_env)
                    self._print_ai_response(f"✅ API key saved as {expected_env}", "success")
            
        except (ValueError, KeyboardInterrupt):
            self._print_ai_response("Configuration cancelled.", "info")

    def _load_models_from_tui_config(self) -> List[Dict[str, Any]]:
        """Load models from TUI's models.json and flatten with provider labels."""
        try:
            path = Path(__file__).parent / "fancy_ui" / "models.json"
            if not path.exists():
                return []
            data = json.loads(path.read_text())
            providers = data.get("providers", {})
            results: List[Dict[str, Any]] = []
            for provider_name, pdata in providers.items():
                for m in pdata.get("models", []):
                    item = dict(m)
                    item["provider"] = provider_name
                    # Normalize fields that Simple UI expects
                    if "model_name" not in item:
                        item["model_name"] = item.get("id")
                    if "name" not in item:
                        item["name"] = item.get("display_name") or item.get("id")
                    # Extract slug and model_kwargs like fancy UI does
                    if "slug" in m:
                        item["slug"] = m["slug"]
                    if "model_kwargs" in m:
                        item["model_kwargs"] = m["model_kwargs"]
                    results.append(item)
            return results
        except Exception:
            return []
    
    def _fetch_models_from_backend(self) -> List[Dict[str, Any]]:
        """Fetch available models from the backend endpoint."""
        try:
            # Default backend URL - could be made configurable
            # Try localhost first (for development), then fallback to production
            backend_urls = [
                "http://localhost:3000/api/v1/wizard/models",
                "https://vibecontext-ts-endpoint.askbudi.workers.dev/api/v1/wizard/models"
            ]
            
            response = None
            for backend_url in backend_urls:
                try:
                    response = requests.get(backend_url, timeout=3)
                    if response.status_code == 200:
                        break
                except requests.exceptions.RequestException:
                    continue
            
            if not response:
                self._print_ai_response("⚠️ All backend URLs failed", "warning")
                return []
            
            data = response.json()
            models = data.get("models", [])
            self._print_ai_response(f"✅ Loaded {len(models)} models from backend", "success")
            return models
        except requests.exceptions.RequestException as e:
            self._print_ai_response(f"⚠️ Failed to connect to backend: {str(e)}", "warning")
            return []
        except Exception as e:
            self._print_ai_response(f"⚠️ Error fetching models: {str(e)}", "warning")
            return []
    
    def _configure_model_api_key(self) -> None:
        """Configure API key for the current model."""
        config = self.config_manager.load_config()
        agent_config = config.agent_config
        
        self._print_ai_response(f"🔑 API Key for {agent_config.model_name} ({agent_config.provider})", "info")
        
        # Show expected environment variable name
        expected_env_var = self._get_expected_env_var(agent_config.provider)
        
        self.console.print(f"\n[dim]Expected environment variable: [bold]{expected_env_var}[/bold][/dim]")
        self.console.print("[dim]You can either:[/dim]")
        self.console.print("  [cyan]1.[/cyan] Enter API key now (saved to .env)")
        self.console.print("  [cyan]2.[/cyan] Set it yourself in environment/shell")
        
        try:
            want_key = _run_coro_in_thread(self._pt_confirm_async("API Key", "Enter API key now?"))
        except Exception:
            want_key = False
        if (want_key or False):
            try:
                api_key = _run_coro_in_thread(self._pt_input_async("API Key", f"Enter {agent_config.provider} API key", password=True)) or ""
            except Exception:
                api_key = ""
            if api_key.strip():
                # Ask for scope
                scope = self.config_manager.prompt_config_scope("API Key", is_model_config=True)
                
                # Save API key with scope
                self.config_manager.set_model_api_key_with_scope(api_key.strip(), scope=scope, key_name=expected_env_var)
                
                scope_text = "globally" if scope == "global" else "locally"
                self._print_ai_response(f"✅ API key saved {scope_text} as {expected_env_var}", "success")
                self._print_ai_response("🔒 Key is securely stored and will not be logged", "info")
            else:
                self._print_ai_response("❌ Invalid API key", "error")
        else:
            self.console.print(f"\n[yellow]💡 Set the environment variable manually:[/yellow]")
            self.console.print(f"   export {expected_env_var}=your_api_key_here")
    
    def _configure_model_parameters(self) -> None:
        """Configure model parameters like temperature and max_tokens."""
        config = self.config_manager.load_config()
        agent_config = config.agent_config
        
        self._print_ai_response("⚙️ Model Parameters Configuration", "info")
        
        # Temperature
        try:
            temp_str = _run_coro_in_thread(self._pt_input_async(
                "Temperature",
                f"0.0-2.0 (current: {agent_config.temperature})"
            )) or str(agent_config.temperature)
            temperature = float(temp_str)
            if 0.0 <= temperature <= 2.0:
                # Ask for scope
                scope = self.config_manager.prompt_config_scope("Temperature Setting", is_model_config=True)
                
                self.config_manager.update_agent_config_with_scope(scope=scope, temperature=temperature)
                scope_text = "globally" if scope == "global" else "for this project"
                self._print_ai_response(f"✅ Temperature set to {temperature} {scope_text}", "success")
            else:
                self._print_ai_response("❌ Temperature must be between 0.0 and 2.0", "error")
                return
        except ValueError:
            self._print_ai_response("❌ Invalid temperature value", "error")
            return
        
        # Max tokens
        max_tokens_str = _run_coro_in_thread(self._pt_input_async(
            "Max Tokens",
            f"Leave empty for auto (current: {agent_config.max_tokens or 'Auto'})"
        )) or ""
        
        if max_tokens_str.strip():
            try:
                max_tokens = int(max_tokens_str)
                if max_tokens > 0:
                    # Ask for scope
                    scope = self.config_manager.prompt_config_scope("Max Tokens Setting", is_model_config=True)
                    
                    self.config_manager.update_agent_config_with_scope(scope=scope, max_tokens=max_tokens)
                    scope_text = "globally" if scope == "global" else "for this project"
                    self._print_ai_response(f"✅ Max tokens set to {max_tokens} {scope_text}", "success")
                else:
                    self._print_ai_response("❌ Max tokens must be positive", "error")
            except ValueError:
                self._print_ai_response("❌ Invalid max tokens value", "error")
        else:
            # Ask for scope
            scope = self.config_manager.prompt_config_scope("Max Tokens Setting", is_model_config=True)
            
            self.config_manager.update_agent_config_with_scope(scope=scope, max_tokens=None)
            scope_text = "globally" if scope == "global" else "for this project"
            self._print_ai_response(f"✅ Max tokens set to auto {scope_text}", "success")
    
    def _configure_custom_base_url(self) -> None:
        """Configure custom base URL for API."""
        config = self.config_manager.load_config()
        agent_config = config.agent_config
        
        self._print_ai_response("🌐 Custom Base URL Configuration", "info")
        
        current_url = agent_config.custom_base_url or "Default"
        self.console.print(f"[dim]Current base URL: {current_url}[/dim]")
        
        try:
            base_url = _run_coro_in_thread(self._pt_input_async(
                "Custom Base URL",
                "Enter custom base URL (leave empty for default)"
            )) or ""
        except Exception:
            base_url = ""
        
        if base_url.strip():
            # Ask for scope
            scope = self.config_manager.prompt_config_scope("Base URL Setting", is_model_config=True)
            
            self.config_manager.update_agent_config_with_scope(scope=scope, custom_base_url=base_url.strip())
            scope_text = "globally" if scope == "global" else "for this project"
            self._print_ai_response(f"✅ Base URL set to {base_url.strip()} {scope_text}", "success")
        else:
            # Ask for scope
            scope = self.config_manager.prompt_config_scope("Base URL Setting", is_model_config=True)
            
            self.config_manager.update_agent_config_with_scope(scope=scope, custom_base_url=None)
            scope_text = "globally" if scope == "global" else "for this project"
            self._print_ai_response(f"✅ Base URL reset to default {scope_text}", "success")
    
    def _reset_model_config(self) -> None:
        """Reset model configuration to defaults."""
        if (self._pt_confirm_sync("Model", "Reset model configuration to defaults?") is True):
            from .config import AgentConfig
            default_config = AgentConfig()
            
            # Ask for scope
            scope = self.config_manager.prompt_config_scope("Reset Model Configuration", is_model_config=True)
            
            self.config_manager.update_agent_config_with_scope(
                scope=scope,
                model_name=default_config.model_name,
                provider=default_config.provider,
                temperature=default_config.temperature,
                max_tokens=default_config.max_tokens,
                custom_base_url=default_config.custom_base_url,
                api_key_env_var=default_config.api_key_env_var
            )
            
            scope_text = "globally" if scope == "global" else "for this project"
            self._print_ai_response(f"✅ Model configuration reset to defaults {scope_text}", "success")
            self._print_ai_response(f"Model: {default_config.model_name} ({default_config.provider})", "info")
    
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
    
    def _handle_cleanup_command(self) -> None:
        """Handle /cleanup command to clear the screen."""
        import os
        
        # Clear screen using system-appropriate method
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Show a nice header after clearing
        header_panel = Panel.fit(
            "[bold cyan]🧹 Screen Cleared![/bold cyan]\n\n"
            "[dim]Use /help to see available commands[/dim]",
            title="[bold]juno-agent[/bold]",
            border_style="bright_blue",
            padding=(0, 1)
        )
        self.console.print(header_panel)
        
        # Show current status quickly
        config = self.config_manager.load_config()
        status_items = []
        
        if self.config_manager.has_api_key():
            status_items.append("[green]🔑 API Key: ✓[/green]")
        else:
            status_items.append("[red]🔑 API Key: ✗[/red]")
            
        if config.editor:
            status_items.append(f"[blue]📝 Editor: {config.editor}[/blue]")
        else:
            status_items.append("[dim]📝 Editor: Not set[/dim]")
        
        # Add model info
        agent_config = config.agent_config
        # Use model_slug for display if available, otherwise fallback to model_name (like fancy UI does)
        display_model = agent_config.model_slug if agent_config.model_slug else agent_config.model_name
        model_status = f"[magenta]🤖 Model: {display_model}[/magenta]"
        status_items.append(model_status)
        
        if status_items:
            status_line = " │ ".join(status_items)
            self.console.print(f"[dim]{status_line}[/dim]\n")
    
    def _handle_reset_command(self) -> None:
        """Handle /reset command."""
        if (self._pt_confirm_sync("Reset", "This will reset all configuration. Are you sure?") is True):
            self.config_manager.reset_config()
            self.console.print("[green]✓ Configuration reset[/green]")
    
    def _handle_setup_command(self) -> None:
        """Handle /setup command (simple UI path) using unified setup pipeline."""
        try:
            self._run_setup_pipeline_with_ui()
        except Exception as e:
            import traceback
            self.console.print(f"[red]Error running setup pipeline: {e}[/red]")
            self.console.print(f"[red]{traceback.format_exc()}[/red]")

    def _handle_scan_command(self) -> None:
        """Handle /scan command."""
        self.console.print("[blue]Scanning project...[/blue]")
        
        with self.console.status("[bold blue]Analyzing project structure..."):
            project_info = self.scanner.scan()
        
        # Display scan results
        self.console.print("\n[bold]Project Scan Results[/bold]")
        
        if project_info.languages:
            self.console.print(f"[blue]Languages:[/blue] {', '.join(project_info.languages)}")
        
        if project_info.frameworks:
            self.console.print(f"[blue]Frameworks:[/blue] {', '.join(project_info.frameworks)}")
        
        if project_info.package_managers:
            self.console.print(f"[blue]Package Managers:[/blue] {', '.join(project_info.package_managers)}")
        
        if project_info.dependencies:
            dep_count = len(project_info.dependencies)
            if dep_count > 10:
                shown_deps = project_info.dependencies[:10]
                self.console.print(f"[blue]Dependencies ({dep_count} total):[/blue] {', '.join(shown_deps)}, ... ({dep_count - 10} more)")
            else:
                self.console.print(f"[blue]Dependencies:[/blue] {', '.join(project_info.dependencies)}")
        
        if project_info.config_files:
            self.console.print(f"[blue]Config Files:[/blue] {', '.join(project_info.config_files)}")
        
        if project_info.technologies:
            self.console.print(f"[blue]Technologies:[/blue] {', '.join(project_info.technologies)}")
        
        # Save scan results to config
        self.config_manager.update_config(libraries=project_info.dependencies)
        
        # Offer to create/update rules file
        config = self.config_manager.load_config()
        if config.editor and self.mcp_installer.is_editor_supported(config.editor):
            if (self._pt_confirm_sync("Rules", f"Update rules file for {config.editor}?") is True):
                success, message = self.mcp_installer.create_rules_file(
                    config.editor, project_info, project_info.dependencies
                )
                if success:
                    self.console.print(f"[green]✓ {message}[/green]")
                else:
                    self.console.print(f"[red]✗ {message}[/red]")
        
        self.console.print(f"\n[green]✓ Project scan completed. Found {len(project_info.dependencies)} dependencies.[/green]")
    
    def _handle_agent_command(self) -> None:
        """Handle /agent command - AI agent configuration and status."""
        self._print_ai_response("🤖 AI Agent Configuration", "info")
        
        config = self.config_manager.load_config()
        
        # Enhanced status display with AI capabilities
        status_panel_content = []
        
        # Core setup status
        setup_items = [
            ("🔑 API Key", "✅ Configured" if self.config_manager.has_api_key() else "❌ Missing"),
            ("📝 Editor", f"✅ {config.editor}" if config.editor else "❌ Not selected"),
            ("📊 Project Scan", f"✅ {len(config.libraries or [])} dependencies" if config.libraries else "❌ Not scanned"),
            ("🔗 MCP Server", "✅ Installed" if config.mcp_server_installed else "❌ Not installed"),
        ]
        
        status_panel_content.append("[bold blue]🔧 Core Setup Status[/bold blue]")
        for item, status in setup_items:
            status_panel_content.append(f"  {item}: {status}")
        
        # AI Agent features
        status_panel_content.append("\n[bold green]🤖 AI Agent Features[/bold green]")
        agent_features = [
            "✅ Intelligent chat interface",
            "✅ Context-aware responses", 
            "✅ Project analysis and insights",
            "✅ Command suggestions and help",
            "✅ Conversation history tracking",
            "🚧 TinyAgent-py integration (coming soon)",
            "🚧 Advanced dependency analysis (coming soon)",
            "🚧 Automated documentation generation (coming soon)"
        ]
        
        for feature in agent_features:
            status_panel_content.append(f"  {feature}")
        
        # Conversation stats
        conversation_summary = self.tiny_agent.get_conversation_summary()
        if conversation_summary["total_exchanges"] > 0:
            status_panel_content.append("\n[bold cyan]💬 Current Session[/bold cyan]")
            status_panel_content.append(f"  📝 Exchanges: {conversation_summary['total_exchanges']}")
            if conversation_summary["conversation_topics"]:
                topics = ", ".join(conversation_summary["conversation_topics"])
                status_panel_content.append(f"  🏷️  Topics: {topics}")
        
        # Display comprehensive status
        status_panel = Panel(
            "\n".join(status_panel_content),
            title="[bold]🧙‍♂️ AI Agent Status Dashboard[/bold]",
            border_style="bright_blue",
            padding=(1, 2)
        )
        self.console.print(status_panel)
        
        # Interactive options
        self._print_ai_response("Available agent actions:", "info")
        
        if (self._pt_confirm_sync("Analysis", "Run project analysis with AI insights?") is True):
            self._run_ai_project_analysis()
        
        if conversation_summary["total_exchanges"] > 0 and (self._pt_confirm_sync("Export", "Export conversation history?") is True):
            self._export_conversation_history()
        
    
    def _run_ai_project_analysis(self) -> None:
        """Run AI-powered project analysis."""
        self._print_ai_response("🔍 Running AI project analysis...", "info")
        
        try:
            analysis = _run_coro_in_thread(
                self.analysis_agent.analyze_project_context(self.config_manager.workdir)
            )
            
            insights_report = self.analysis_agent.generate_insights_report(analysis)
            
            analysis_panel = Panel(
                insights_report,
                title="[bold]🧠 AI Project Analysis[/bold]",
                border_style="bright_green",
                padding=(1, 2)
            )
            self.console.print(analysis_panel)
            
            self._print_ai_response("✅ Analysis complete! Use these insights to improve your project.", "success")
            
        except Exception as e:
            self._print_ai_response(f"❌ Analysis failed: {str(e)}", "error")
    
    def _export_conversation_history(self) -> None:
        """Export conversation history."""
        try:
            conversation_file = self.config_manager.config_dir / "conversation_history.json"
            if conversation_file.exists():
                self._print_ai_response(f"📄 Conversation history saved to: {conversation_file}", "success")
            else:
                self._print_ai_response("❌ No conversation history found", "error")
        except Exception as e:
            self._print_ai_response(f"❌ Export failed: {str(e)}", "error")
    
    async def _handle_continue_command(self) -> None:
        """Handle /continue command for resuming tinyagent when max turns reached."""
        self._print_ai_response("🔄 Continue Juno Agent", "info")
        
        # Check if we have an active tinyagent session
        if hasattr(self, 'tiny_code_agent') and self.tiny_code_agent:
            # Resume the agent with additional turns
            self._print_ai_response("Resuming Juno Agent session...", "info")
            # This would need to be implemented in the TinyCodeAgent class
            try:
                await self.tiny_code_agent.resume()
                self._print_ai_response("✅ Juno Agent resumed successfully", "success")
            except Exception as e:
                self._print_ai_response(f"❌ Failed to resume Juno Agent: {str(e)}", "error")
        else:
            # No active session available
            self._print_ai_response("No active Juno Agent session. In TinyAgent mode, Juno Agent is active by default.", "info")
    
    def _handle_config_command(self) -> None:
        """Handle /config command for configuration management."""
        self._print_ai_response("⚙️ Configuration Management", "info")
        
        config = self.config_manager.load_config()
        
        # Display current configuration
        config_content = f"""[bold]🔧 Current Configuration[/bold]
        
• **Working Directory**: {config.workdir}
• **Editor**: {config.editor or 'Not set'}
• **Backend URL**: {config.backend_url or 'Default'}
• **Git Controlled**: {'✅ Yes' if config.git_controlled else '❌ No'}
• **Setup Completed**: {'✅ Yes' if config.setup_completed else '❌ No'}

[bold]🤖 Agent Configuration[/bold]
• **Model**: {config.agent_config.model_name}
• **Provider**: {config.agent_config.provider}
• **Temperature**: {config.agent_config.temperature}
• **Max Tokens**: {config.agent_config.max_tokens or 'Auto'}
• **API Key**: {'✅ Set' if self.config_manager.get_model_api_key() else '❌ Missing'}

[bold]📚 Project Libraries[/bold]
• **Count**: {len(config.libraries)}
• **Libraries**: {', '.join(config.libraries[:5]) if config.libraries else 'None detected'}
{f'• **...and {len(config.libraries) - 5} more**' if len(config.libraries) > 5 else ''}
"""
        
        config_panel = Panel(
            config_content,
            title="Configuration",
            border_style="blue",
            padding=(1, 2)
        )
        
        self.console.print(config_panel)
        
        # Ask if they want to modify anything
        if (self._pt_confirm_sync("Config", "Modify configuration?") is True):
            options = [
                ("1", "Change Model/Provider"),
                ("2", "Set API Key"), 
                ("3", "Change Editor"),
                ("4", "Reset Configuration"),
                ("5", "Back to chat"),
            ]
            self.console.print("\n[bold]Configuration Options:[/bold]")
            for key, label in options:
                self.console.print(f"  {key}. {label}")
            selected = self._pt_choice_sync("Configuration", options) or "5"
            if selected == "1":
                self._configure_model_and_provider()
            elif selected == "2":
                self._configure_model_api_key()
            elif selected == "3":
                self._configure_editor()
            elif selected == "4":
                if (self._pt_confirm_sync("Reset", "Are you sure you want to reset all configuration?") is True):
                    self._handle_reset_command()
            else:
                pass
    
    async def _handle_tiny_cost_command(self) -> None:
        """Handle /cost command in Juno Agent mode - show conversation cost."""
        if not hasattr(self, 'tiny_code_agent') or not self.tiny_code_agent or not self.tiny_code_agent.agent:
            self._print_ai_response("❌ No active Juno Agent session", "error")
            return
        
        try:
            # Check if Juno Agent has token tracking
            agent = self.tiny_code_agent.agent
            
            # Look for TokenTracker in callbacks
            cost_info = None
            has_child_trackers = False
            child_tracker_count = 0
            
            if hasattr(agent, 'callbacks'):
                for callback in agent.callbacks:
                    callback_type = type(callback).__name__
                    
                    if callback_type == 'TokenTracker' or hasattr(callback, 'get_total_usage'):
                        try:
                            # TokenTracker has get_total_usage() method
                            if hasattr(callback, 'get_total_usage'):
                                stats = callback.get_total_usage()
                                
                                # Check for child trackers and aggregate their costs
                                if hasattr(callback, 'child_trackers') and callback.child_trackers:
                                    try:
                                        child_count = len(callback.child_trackers)
                                        has_child_trackers = True
                                        child_tracker_count = child_count
                                    except TypeError:
                                        # Handle Mock objects that don't support len()
                                        try:
                                            child_count = len(list(callback.child_trackers))
                                            has_child_trackers = True
                                            child_tracker_count = child_count
                                        except TypeError:
                                            pass
                                    
                                    if has_child_trackers:
                                        child_tokens = 0
                                        child_cost = 0.0
                                        child_calls = 0
                                        child_prompt_tokens = 0
                                        child_completion_tokens = 0
                                        
                                        for child_tracker in callback.child_trackers:
                                            if hasattr(child_tracker, 'get_total_usage'):
                                                child_stats = child_tracker.get_total_usage()
                                                child_tokens += child_stats.total_tokens
                                                child_cost += child_stats.cost
                                                child_calls += child_stats.call_count
                                                child_prompt_tokens += getattr(child_stats, 'prompt_tokens', 0)
                                                child_completion_tokens += getattr(child_stats, 'completion_tokens', 0)
                                        
                                        # Create aggregated stats including all child tracker data
                                        from types import SimpleNamespace
                                        aggregated_stats = SimpleNamespace(
                                            prompt_tokens=stats.prompt_tokens + child_prompt_tokens,
                                            completion_tokens=stats.completion_tokens + child_completion_tokens,
                                            total_tokens=stats.total_tokens + child_tokens,
                                            cost=stats.cost + child_cost,
                                            call_count=stats.call_count + child_calls,
                                            thinking_tokens=getattr(stats, 'thinking_tokens', 0),
                                            reasoning_tokens=getattr(stats, 'reasoning_tokens', 0),
                                            cache_creation_input_tokens=getattr(stats, 'cache_creation_input_tokens', 0),
                                            cache_read_input_tokens=getattr(stats, 'cache_read_input_tokens', 0)
                                        )
                                        stats = aggregated_stats
                                
                                cost_info = stats
                                break
                        except Exception:
                            continue
                    # Fallback: check for any callback with get_usage_stats method
                    elif hasattr(callback, 'get_usage_stats'):
                        try:
                            stats = callback.get_usage_stats()
                            cost_info = stats
                            break
                        except Exception:
                            continue
            
            if cost_info:
                # Check if this includes subagent costs
                if has_child_trackers:
                    subagent_info = f"• **Includes Subagent Costs**: ✅ Yes ({child_tracker_count} subagents tracked)\n"
                else:
                    subagent_info = "• **Includes Subagent Costs**: ❌ No subagent usage detected\n"
                
                # Display detailed cost information
                cost_content = f"""[bold]💰 Conversation Cost Analysis[/bold]

📊 **Token Usage**
• **Prompt Tokens**: {cost_info.prompt_tokens:,}
• **Completion Tokens**: {cost_info.completion_tokens:,}
• **Total Tokens**: {cost_info.total_tokens:,}

💸 **Cost Breakdown**
• **Total Cost**: ${cost_info.cost:.4f}
• **API Calls**: {cost_info.call_count}
• **Average per Call**: ${(cost_info.cost / max(cost_info.call_count, 1)):.4f}
{subagent_info}
🧠 **Advanced Tokens** (if supported)
• **Thinking Tokens**: {getattr(cost_info, 'thinking_tokens', 0):,}
• **Reasoning Tokens**: {getattr(cost_info, 'reasoning_tokens', 0):,}
• **Cache Creation**: {getattr(cost_info, 'cache_creation_input_tokens', 0):,}
• **Cache Read**: {getattr(cost_info, 'cache_read_input_tokens', 0):,}

[dim]💡 Cost tracking includes both main agent and subagent usage when available[/dim]"""
                
                cost_panel = Panel(
                    cost_content,
                    title="[bold bright_yellow]💰 Cost Tracker[/bold bright_yellow]",
                    border_style="bright_yellow",
                    padding=(1, 2)
                )
                self.console.print(cost_panel)
            else:
                self._print_ai_response("📊 Cost tracking not available. Enable TokenTracker hook for detailed cost analysis.", "info")
        
        except Exception as e:
            self._print_ai_response(f"❌ Error retrieving cost information: {str(e)}", "error")
    
    async def _handle_tiny_compact_command(self) -> None:
        """Handle /compact command in Juno Agent mode - compact conversation.
        
        Uses Juno Agent's compact() method which compacts the conversation AND updates the agent's context,
        unlike summarize() which only generates a summary without updating context.
        """
        if not hasattr(self, 'tiny_code_agent') or not self.tiny_code_agent.agent:
            self._print_ai_response("❌ No active Juno Agent session", "error")
            return
        
        try:
            self._print_ai_response("🗜️ Compacting conversation history...", "info")
            
            # Use Juno Agent's compact method (preferred) or fallback to summarize
            agent = self.tiny_code_agent.agent
            
            if hasattr(agent, 'compact'):
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=self.console,
                    transient=True,
                ) as progress:
                    task = progress.add_task("🗜️ Compacting conversation...", total=None)
                    
                    # Call the compact method
                    summary = await agent.compact()
            elif hasattr(agent, 'summarize'):
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=self.console,
                    transient=True,
                ) as progress:
                    task = progress.add_task("🗜️ Generating conversation summary...", total=None)
                    
                    # Fallback: Call the summarize method (doesn't update context)
                    summary = await agent.summarize()
            else:
                summary = None
            
            if summary:
                # Display the summary
                summary_content = f"""[bold]📝 Conversation Summary[/bold]

{summary}

[dim]✅ Conversation has been compacted to preserve context while reducing tokens[/dim]"""
                
                summary_panel = Panel(
                    summary_content,
                    title="[bold bright_blue]🗜️ Conversation Compact[/bold bright_blue]",
                    border_style="bright_blue",
                    padding=(1, 2)
                )
                self.console.print(summary_panel)
                
                self._print_ai_response("✅ Conversation successfully compacted!", "success")
            elif hasattr(agent, 'compact') or hasattr(agent, 'summarize'):
                self._print_ai_response("⚠️ No summary generated - conversation may be too short", "warning")
            else:
                self._print_ai_response("❌ Compacting not supported by current Juno Agent version", "error")
        
        except Exception as e:
            self._print_ai_response(f"❌ Error compacting conversation: {str(e)}", "error")
    
class WizardApp(PromptToolkitMixin):
    """Main wizard application."""
    
    def __init__(self, config_manager: ConfigManager, system_status: SystemStatus, debug: bool = False, auto_start_setup: bool = False, verify_only_mode: bool = False, agentic_resolver_mode: bool = False):
        self.config_manager = config_manager
        self.system_status = system_status
        self.debug = debug
        self.auto_start_setup = auto_start_setup
        self.verify_only_mode = verify_only_mode
        self.agentic_resolver_mode = agentic_resolver_mode
        self.console = Console()
    
    def run(self) -> None:
        """Run the wizard application."""
        config = self.config_manager.load_config()
        
        # Check UI mode and launch appropriate interface
        from .config import UIMode
        if hasattr(config, 'ui_mode') and config.ui_mode == UIMode.FANCY:
            # For fancy UI, let the TUI handle welcome screen and setup
            self._launch_fancy_ui()
        else:
            # For simple UI, show welcome screen here
            welcome = WelcomeScreen(self.config_manager, self.system_status)
            welcome.display()
            
            # Handle special modes
            if self.verify_only_mode:
                # Run verification only
                self._run_verification_only()
                return
            elif self.agentic_resolver_mode:
                # Run dependency resolver only
                self._run_agentic_resolver_only()
                return
            elif self.auto_start_setup:
                # Run setup directly without prompting
                self._run_unified_pipeline()
                return
            
            # Offer setup only if not configured
            workdir = Path(self.config_manager.workdir)
            docs_exist = any((workdir / name).exists() for name in ("AGENTS.md", "CLAUDE.md", "JUNO.md"))
            is_configured = bool(getattr(config, 'setup_completed', False) or (config.editor and docs_exist))
            if not is_configured:
                if not self.config_manager.has_api_key():
                    # Only prompt for setup if no API key is configured
                    if (self._pt_confirm_sync("Setup", "Setup recommended to configure API key. Run now?") is True):
                        # Minimal API key capture, then run the unified pipeline
                        self._prompt_api_key_if_missing()
                        self._run_unified_pipeline()
                    else:
                        self.console.print("[yellow]You can run setup later with '/setup' or set API key with '/apikey'.[/yellow]")
                else:
                    # API key exists, setup is optional
                    if (self._pt_confirm_sync("Setup", "Run unified setup to configure project context and editor integration?") is True):
                        self._run_unified_pipeline()
                    else:
                        self.console.print("[green]Ready to chat! Use '/setup' later for additional configuration.[/green]")
            
            # Validate model configuration before starting agent
            self._validate_model_configuration()
            
            # Start default chat interface with Juno Agent
            chat = ChatInterface(self.config_manager, debug=self.debug)
            _run_coro_in_thread(chat.run_with_tiny_default())

    def _prompt_api_key_if_missing(self) -> None:
        """Prompt user for ASKBUDI API key if not set."""
        if self.config_manager.has_api_key():
            return
        self.console.print("[bold]Step 1: API Key Configuration[/bold]")
        self.console.print("You need an ASKBUDI API key to use the agentic resolver.")
        if (self._pt_confirm_sync("API Key", "Do you have an ASKBUDI API key?") is True):
            api_key = self._pt_input_sync("API Key", "Enter your API key", password=True) or ""
            if api_key.strip():
                try:
                    validation_result = _run_coro_in_thread(
                        self.config_manager.validate_api_key_with_backend(api_key.strip())
                    )
                    if validation_result.get("valid"):
                        self.config_manager.set_api_key(api_key.strip())
                        level = validation_result.get("user_level", "unknown")
                        self.console.print(f"[green]✓ API key validated (Level: {level})[/green]")
                    else:
                        err = validation_result.get("error", "Unknown error")
                        self.console.print(f"[yellow]⚠️ Validation failed: {err}. Saving key anyway.[/yellow]")
                        self.config_manager.set_api_key(api_key.strip())
                except Exception as e:
                    self.console.print(f"[yellow]⚠️ Could not validate API key: {e}. Saving key anyway.[/yellow]")
                    self.config_manager.set_api_key(api_key.strip())
        else:
            self.console.print("You can get an API key from: https://askbudi.ai")

    def _run_unified_pipeline(self) -> None:
        """Run the shared setup pipeline with Simple UI parity (checklist + tool updates)."""
        # WizardApp uses sync project description prompt (different from ChatInterface async approach)
        proj_desc = self._pt_input_sync("Project Description", "Optional: short description for docs (leave empty to skip)")
        proj_desc = (proj_desc or "").strip()
        
        # Use the shared pipeline implementation
        self._run_setup_pipeline_with_ui(project_description=proj_desc)

    def _launch_fancy_ui(self) -> None:
        """Launch the fancy TUI with welcome screen."""
        try:
            from .fancy_ui import PyWizardTUIApp
            app = PyWizardTUIApp(self.config_manager, show_welcome=True, auto_start_setup=self.auto_start_setup, verify_only_mode=self.verify_only_mode, agentic_resolver_mode=self.agentic_resolver_mode)
            app.run()
        except ImportError as e:
            self.console.print(f"[red]Error: Could not import fancy UI components: {e}[/red]")
            self.console.print(f"[red]Import traceback: {e.__class__.__name__}: {str(e)}[/red]")
            import traceback
            self.console.print(f"[red]Full traceback:\n{traceback.format_exc()}[/red]")
            self.console.print("[yellow]Falling back to simple UI mode.[/yellow]")
            # Fall back to simple UI
            chat = ChatInterface(self.config_manager, debug=self.debug)
            _run_coro_in_thread(chat.run_with_tiny_default())
        except Exception as e:
            self.console.print(f"[red]Error launching fancy UI: {e}[/red]")
            self.console.print(f"[red]Exception type: {e.__class__.__name__}[/red]")
            self.console.print(f"[red]Exception args: {e.args}[/red]")
            import traceback
            self.console.print(f"[red]Full traceback:\n{traceback.format_exc()}[/red]")
            self.console.print("[yellow]Falling back to simple UI mode.[/yellow]")
            # Fall back to simple UI
            chat = ChatInterface(self.config_manager, debug=self.debug)
            _run_coro_in_thread(chat.run_with_tiny_default())
    
    def _validate_model_configuration(self) -> None:
        """Validate model configuration and guide user to setup if needed."""
        if not self.config_manager.is_model_configured():
            status = self.config_manager.validate_model_setup()
            
            # Show model configuration status
            status_content = f"""[bold yellow]⚠️ Model Configuration Required[/bold yellow]

**Current Settings:**
• Model: {status['model_name']}
• Provider: {status['provider']}
• API Key: {'✅ Available' if status['has_api_key'] else '❌ Missing'}

**Missing Requirements:**
{chr(10).join(f'• {req}' for req in status['missing_requirements'])}

**Next Steps:**
{chr(10).join(f'• {rec}' for rec in status['recommendations'])}

The agent requires a properly configured model and API key to function.
You can set this up now or continue with limited functionality."""
            
            status_panel = Panel(
                status_content,
                title="[bold]🤖 Model Setup Required[/bold]",
                border_style="bright_yellow",
                padding=(1, 2)
            )
            self.console.print(status_panel)
            
            # Ask if user wants to configure model now
            if (self._pt_confirm_sync("Model", "Configure model and API key now?") is True):
                from .ui import ChatInterface
                chat = ChatInterface(self.config_manager, debug=self.debug)
                # Run model configuration synchronously
                _run_coro_in_thread(chat._handle_model_command())
                
                # Re-validate after configuration
                if not self.config_manager.is_model_configured():
                    self.console.print("[yellow]⚠️ Model still not fully configured. Some features may not work.[/yellow]")
                else:
                    self.console.print("[green]✅ Model configuration complete![/green]")
            else:
                self.console.print("[yellow]⚠️ Continuing with limited functionality. Use '/model' command to configure later.[/yellow]")

    def _run_verification_only(self) -> None:
        """Run verification only mode for simple UI."""
        from pathlib import Path
        
        self.console.print("[bold blue]🔍 Setup Verification Mode[/bold blue]")
        self.console.print("Running comprehensive verification of your current setup...")
        self.console.print()
        self.console.print("This will check:")
        self.console.print("• MCP server configuration")
        self.console.print("• External context setup")
        self.console.print("• IDE configuration files")
        self.console.print("• Dependency documentation")
        self.console.print("• API key configuration")
        self.console.print("• File permissions")
        self.console.print("• Project analysis accuracy")
        self.console.print()
        self.console.print("[dim]Running verification now...[/dim]")
        
        try:
            # Import and run VerifyAgent synchronously using _run_coro_in_thread
            from .setup import VerifyAgent
            workdir = Path(self.config_manager.workdir)
            
            async def run_verification():
                return await VerifyAgent(workdir, project_name=workdir.name).run(skip_external_calls=False)
            
            result = _run_coro_in_thread(run_verification())
            
            # Process results
            pass_count = sum(1 for r in result.results if r.status == "PASS")
            fail_count = sum(1 for r in result.results if r.status == "FAIL")
            warn_count = sum(1 for r in result.results if r.status == "WARN")
            info_count = sum(1 for r in result.results if r.status == "INFO")
            
            self.console.print(f"\n[bold]Verification Summary[/bold]")
            self.console.print(f"PASS: {pass_count}  FAIL: {fail_count}  WARN: {warn_count}  INFO: {info_count}")
            self.console.print()
            self.console.print(result.report)
            
            if fail_count > 0:
                self.console.print("\n[red]⚠️ Some checks failed. Consider running setup to fix issues.[/red]")
            elif warn_count > 0:
                self.console.print("\n[yellow]⚠️ Some warnings found. Your setup should work but could be improved.[/yellow]")
            else:
                self.console.print("\n[green]✅ All checks passed! Your setup looks good.[/green]")
                
        except Exception as e:
            self.console.print(f"[red]❌ Error during verification: {e}[/red]")
            import traceback
            self.console.print(f"[red]Traceback: {traceback.format_exc()}[/red]")

    def _run_agentic_resolver_only(self) -> None:
        """Run agentic dependency resolver only mode for simple UI."""
        self.console.print("[bold blue]📚 Agentic Resolver Mode[/bold blue]")
        self.console.print("Note: Agentic resolver is part of the unified setup pipeline.")
        self.console.print("Running full setup to include agentic documentation fetch...")
        self.console.print()
        
        # The agentic resolver is integrated into the unified setup pipeline
        # so we just run the unified pipeline
        self._run_unified_pipeline()
