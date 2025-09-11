"""Main entry point for juno-agent."""

import os
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

from .config import ConfigManager
from .ui import WizardApp
from .utils import SystemStatus

app = typer.Typer(
    name="juno-agent",
    help="A Python CLI tool to help developers setup their libraries in AI coding tools",
    add_completion=True,
)

console = Console()


def initialize_tracing() -> None:
    """Initialize Phoenix tracing with environment configuration."""
    try:
        from phoenix.otel import register
        
        # Get configuration from environment variables
        project_name = os.getenv("PHOENIX_PROJECT_NAME", "juno-cli")
        endpoint = os.getenv("PHOENIX_ENDPOINT", "https://app.phoenix.arize.com/v1/traces")
        
        # Register Phoenix tracing
        tracer_provider = register(
            project_name=project_name,
            endpoint=endpoint,
            auto_instrument=True
        )
        
        console.print(f"[green]✅ Phoenix tracing initialized[/green]")
        console.print(f"[dim]Project: {project_name}[/dim]")
        console.print(f"[dim]Endpoint: {endpoint}[/dim]")
        
        return tracer_provider
        
    except ImportError:
        console.print(f"[red]❌ Phoenix tracing not available. Install with: pip install arize-phoenix-otel[/red]")
        console.print(f"[yellow]Continuing without tracing...[/yellow]")
        return None
    except Exception as e:
        console.print(f"[red]❌ Failed to initialize Phoenix tracing: {e}[/red]")
        console.print(f"[yellow]Continuing without tracing...[/yellow]")
        return None


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    workdir: Optional[Path] = typer.Option(
        None,
        "--workdir",
        "-w",
        help="Working directory (defaults to current directory)",
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        help="Enable debug mode",
    ),
    trace: bool = typer.Option(
        False,
        "--trace",
        help="Enable Phoenix tracing (requires arize-phoenix package)",
    ),
    debug_litellm: bool = typer.Option(
        False,
        "--debug-litellm",
        help="Enable LiteLLM debug mode for detailed API request/response logging",
    ),
    ui_mode: Optional[str] = typer.Option(
        None,
        "--ui-mode",
        help="UI mode: 'simple' or 'fancy' (defaults to config setting)",
    ),
) -> None:
    """Start the juno-agent interactive interface."""
    # Initialize tracing first if requested
    if trace:
        initialize_tracing()
    
    # Enable LiteLLM debug mode if requested
    if debug_litellm:
        try:
            import litellm
            litellm._turn_on_debug()
            console.print("[green]✅ LiteLLM debug mode enabled[/green]")
        except ImportError:
            console.print("[red]❌ LiteLLM not available for debug mode[/red]")
        except Exception as e:
            console.print(f"[red]❌ Failed to enable LiteLLM debug mode: {e}[/red]")
    
    if ctx.invoked_subcommand is not None:
        return
        
    if workdir is None:
        workdir = Path.cwd()
    
    workdir = workdir.resolve()
    
    if not workdir.exists() or not workdir.is_dir():
        console.print(f"[red]Error: Directory {workdir} does not exist[/red]")
        raise typer.Exit(1)
    
    try:
        # Initialize configuration manager
        config_manager = ConfigManager(workdir)
        
        # Override UI mode if specified via command line
        if ui_mode:
            from .config import UIMode
            if ui_mode.lower() == 'fancy':
                config = config_manager.load_config()
                config.ui_mode = UIMode.FANCY
                config_manager.save_config(config)
            elif ui_mode.lower() == 'simple':
                config = config_manager.load_config()
                config.ui_mode = UIMode.SIMPLE
                config_manager.save_config(config)
            else:
                console.print(f"[red]Invalid UI mode: {ui_mode}. Use 'simple' or 'fancy'.[/red]")
                raise typer.Exit(1)
        
        # Check system status
        system_status = SystemStatus(workdir)
        
        # Start the wizard application
        wizard_app = WizardApp(config_manager, system_status, debug=debug)
        wizard_app.run()
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Goodbye![/yellow]")
        raise typer.Exit(0)
    except Exception as e:
        if debug:
            console.print_exception()
        else:
            console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def version() -> None:
    """Show version information."""
    from . import __version__
    console.print(f"juno-agent version {__version__}")


@app.command() 
def status(
    workdir: Optional[Path] = typer.Option(
        None,
        "--workdir", 
        "-w",
        help="Working directory (defaults to current directory)",
    )
) -> None:
    """Show current status of the workspace."""
    if workdir is None:
        workdir = Path.cwd()
        
    workdir = workdir.resolve()
    system_status = SystemStatus(workdir)
    
    # Display status in a panel
    status_info = system_status.get_status_info()
    
    console.print(Panel.fit(
        f"""[bold]Workspace Status[/bold]
        
[blue]Working Directory:[/blue] {status_info['workdir']}
[blue]Git Repository:[/blue] {status_info['git_status']}
[blue]API Key:[/blue] {status_info['api_key_status']}
[blue]Editor:[/blue] {status_info['editor']}""",
        title="juno-agent",
        border_style="blue",
    ))


@app.command()
def setup(
    workdir: Optional[Path] = typer.Option(
        None,
        "--workdir",
        "-w", 
        help="Working directory (defaults to current directory)",
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        help="Enable debug mode",
    ),
    trace: bool = typer.Option(
        False,
        "--trace",
        help="Enable Phoenix tracing (requires arize-phoenix package)",
    ),
    debug_litellm: bool = typer.Option(
        False,
        "--debug-litellm",
        help="Enable LiteLLM debug mode for detailed API request/response logging",
    ),
    verify_only: bool = typer.Option(
        False,
        "--verify-only",
        help="Run only setup verification, skip full setup process",
    ),
    docs_only: bool = typer.Option(
        False,
        "--docs-only", 
        help="Run intelligent dependency resolver to scan and fetch documentation",
    ),
    headless: bool = typer.Option(
        False,
        "--headless",
        help="Run setup steps without launching the TUI (generate JUNO.md & AGENTS.md, then verify)",
    ),
    headless_fetch_docs: bool = typer.Option(
        False,
        "--headless-fetch-docs",
        help="In headless mode, run the Agentic Dependency Resolver to fetch docs into external_context",
    ),
    # Headless installs MCP by default (no extra flag to keep UX simple)
    report_file: Optional[Path] = typer.Option(
        None,
        "--report-file",
        help="When in headless mode, write the verification report markdown to this path",
    ),
    editor: Optional[str] = typer.Option(
        None,
        "--editor",
        help="Optional IDE/editor name for headless mode (e.g., 'claude_code', 'cursor', 'windsurf')",
    ),
    ui_mode: Optional[str] = typer.Option(
        None,
        "--ui-mode", 
        help="UI mode: 'simple' or 'fancy' (defaults to config setting)"
    ),
) -> None:
    """Launch the setup wizard or run verification only. Uses configured UI mode unless overridden."""
    # Initialize tracing first if requested
    if trace:
        initialize_tracing()
        # Set environment variables for TinyAgent tracing integration
        os.environ["JUNO_TRACING_ENABLED"] = "1"
        os.environ["OTEL_TRACES_EXPORTER"] = "phoenix"
    
    # Enable LiteLLM debug mode if requested
    if debug_litellm:
        try:
            import litellm
            litellm._turn_on_debug()
            console.print("[green]✅ LiteLLM debug mode enabled[/green]")
        except ImportError:
            console.print("[red]❌ LiteLLM not available for debug mode[/red]")
        except Exception as e:
            console.print(f"[red]❌ Failed to enable LiteLLM debug mode: {e}[/red]")
    
    # Validate flags - verify_only is exclusive with others
    if verify_only and docs_only:
        console.print("[red]Error: --verify-only cannot be used with --docs-only[/red]")
        raise typer.Exit(1)
    
    if workdir is None:
        workdir = Path.cwd()
    
    workdir = workdir.resolve()
    
    if not workdir.exists() or not workdir.is_dir():
        console.print(f"[red]Error: Directory {workdir} does not exist[/red]")
        raise typer.Exit(1)
    
    try:
        # Initialize configuration manager
        config_manager = ConfigManager(workdir)
        
        # Override UI mode if specified via command line
        if ui_mode:
            from .config import UIMode
            if ui_mode.lower() == 'fancy':
                config = config_manager.load_config()
                config.ui_mode = UIMode.FANCY
                config_manager.save_config(config)
            elif ui_mode.lower() == 'simple':
                config = config_manager.load_config()
                config.ui_mode = UIMode.SIMPLE
                config_manager.save_config(config)
            else:
                console.print(f"[red]Invalid UI mode: {ui_mode}. Use 'simple' or 'fancy'.[/red]")
                raise typer.Exit(1)
        
        if headless:
            # Unified headless path via shared pipeline
            from .setup.pipeline import run_setup_pipeline
            dbg = config_manager.create_debug_logger(debug=True)
            selected_editor = editor or (config_manager.load_config().editor or "Claude Code")
            result = run_setup_pipeline(
                workdir=Path(workdir),
                config_manager=config_manager,
                editor_display=("Claude Code" if selected_editor.lower() in ("claude_code", "claude code") else selected_editor),
                logger=dbg,
                report_file=Path(report_file) if report_file else None,
                textual_ui_callback=None,
            )
            console.print(f"[bold]Headless Setup Verification[/bold]")
            console.print(f"PASS: {result['pass']}  FAIL: {result['fail']}  WARN: {result['warn']}  INFO: {result['info']}")
            if report_file:
                console.print(f"\n[green]Report written to {report_file}[/green]")
            return
            # Headless path: generate JUNO.md and AGENTS.md using basic scanning, then verify
            from .fancy_ui.setup.dependency_scanner import DependencyScanner
            from .setup import (
                generate_and_write_agents_md,
                generate_and_write_juno_md,
                VerifyAgent,
            )
            # Agentic Dependency Resolver for fetching docs (run by default in headless full setup)
            from .fancy_ui.setup.agentic_dependency_resolver import AgenticDependencyResolver
            dbg = config_manager.create_debug_logger(debug=True)
            
            scanner = DependencyScanner(project_path=workdir)
            scan = scanner.scan_project_dependencies()
            # Normalize structure for generators
            detected = {
                "project_type": scan.get("metadata", {}).get("project_type", "Unknown"),
                "language": scan.get("language", "Unknown"),
                "dependencies": scan.get("dependencies", []),
                "package_files": scan.get("package_files", []),
            }
            fetched_docs = {"saved_files": []}
            project_desc = "Generated by headless setup"
            # Prefer a supported editor for verification friendliness
            selected_editor = editor or (config_manager.load_config().editor or "Claude Code")

            # If requested, run Agentic Dependency Resolver to fetch docs
            try:
                import asyncio as _asyncio
                resolver = AgenticDependencyResolver(
                    project_path=str(workdir),
                    config_manager=config_manager,
                    ui_callback=None,
                    storage_manager=None,
                )
                dbg.info("headless_resolver_start", deps=len(detected["dependencies"]))
                docs_result = _asyncio.get_event_loop().run_until_complete(
                    resolver.run()
                )
                dbg.info("headless_resolver_done", success=docs_result.get("success"))

                # Convert results to saved_files structure expected by generators
                if docs_result.get("success"):
                    files_created = docs_result.get("files_created")
                    file_names = docs_result.get("file_names") or []
                    documentation_fetched = docs_result.get("documentation_fetched", {})
                    saved_files = []
                    if files_created and file_names:
                        for name in file_names:
                            dep = name.replace(".md", "")
                            saved_files.append({
                                "dependency": dep,
                                "filename": name,
                            })
                    elif documentation_fetched:
                        for fi in documentation_fetched.get("saved_files", []):
                            saved_files.append({
                                "dependency": fi.get("name", "unknown"),
                                "filename": Path(fi.get("path", "")).name or f"{fi.get('name','unknown')}.md",
                            })
                    fetched_docs = {"saved_files": saved_files}
            except Exception as e:
                dbg.warning(f"headless_resolver_failed: {e}")

            # Ensure external_context exists and is symlinked into the project
            try:
                from .fancy_ui.setup.external_context_manager import ExternalContextManager
                ecm = ExternalContextManager(Path(workdir))
                ecm.initialize_context_structure()
            except Exception as e:
                dbg.warning(f"headless_external_context_init_failed: {e}")

            # Write JUNO.md and AGENTS.md
            generate_and_write_juno_md(
                workdir=workdir,
                project_description=project_desc,
                selected_editor=selected_editor,
                ai_analysis="",
                detected_deps=detected,
                fetched_docs=fetched_docs,
                logger=dbg,
            )
            # Generate agentic contributor guide content
            try:
                from .setup.agents_contributor_agent import generate_contributor_guide
                contributor_text = generate_contributor_guide(workdir, logger=dbg)
            except Exception as e:
                contributor_text = ""
                dbg.warning(f"agents_md_contributor_generation_failed: {e}")

            # Write IDE-specific file: CLAUDE.md for Claude Code; otherwise AGENTS.md
            if selected_editor.lower() in ("claude_code", "claude code"):
                from .setup import AgentsMdGenerator, AgentsMdInputs
                gen = AgentsMdGenerator(logger=dbg)
                content = gen.generate_content(
                    AgentsMdInputs(
                        workdir=workdir,
                        ide_name="Claude Code",
                        project_description=project_desc,
                        ai_analysis="",
                        detected_deps=detected,
                        fetched_docs=fetched_docs,
                    )
                )
                try:
                    merged_claude = (contributor_text.strip() + "\n\n" + content) if contributor_text else content
                    (workdir / "CLAUDE.md").write_text(merged_claude, encoding="utf-8")
                    dbg.info("headless_wrote_claude_md_with_contributor", path=str(workdir / "CLAUDE.md"))
                except Exception as e:
                    (workdir / "CLAUDE.md").write_text(content, encoding="utf-8")
                    dbg.warning(f"claude_md_merge_failed: {e}")
                # Also create AGENTS.md with contributor guide + general content for agents
                try:
                    merged_agents = contributor_text.strip() + "\n\n" + content
                    (workdir / "AGENTS.md").write_text(merged_agents, encoding="utf-8")
                    dbg.info("headless_wrote_agents_md_with_contributor", path=str(workdir / "AGENTS.md"))
                except Exception as e:
                    dbg.warning(f"agents_md_write_failed: {e}")
            else:
                # Merge contributor guide with generator output
                gen_path = generate_and_write_agents_md(
                    workdir=workdir,
                    ide_name=selected_editor,
                    project_description=project_desc,
                    ai_analysis="",
                    detected_deps=detected,
                    fetched_docs=fetched_docs,
                    logger=dbg,
                )
                try:
                    base = Path(gen_path).read_text(encoding="utf-8") if gen_path else ""
                    merged = contributor_text.strip() + "\n\n" + base
                    (workdir / "AGENTS.md").write_text(merged, encoding="utf-8")
                    dbg.info("headless_wrote_agents_md_with_contributor", path=str(workdir / "AGENTS.md"))
                except Exception as e:
                    dbg.warning(f"agents_md_merge_failed: {e}")

            # Install MCP servers for the selected editor in headless mode
            try:
                from .fancy_ui.setup import MCPInstaller, MCPInstallationError
                # Normalize editor key to the expected identifier
                raw = (selected_editor or "").strip().lower()
                if raw in ("claude code", "claude_code"):
                    editor_key = "claude_code"
                elif raw in ("cursor",):
                    editor_key = "cursor"
                elif raw in ("windsurf",):
                    editor_key = "windsurf"
                elif raw in ("vscode", "vs code", "visual studio code"):
                    editor_key = "vscode"
                else:
                    # Default to cursor-style project config for unknowns
                    editor_key = raw.replace(" ", "_") or "cursor"

                installer = MCPInstaller(project_dir=workdir)
                dbg.info("headless_mcp_install_start", editor=editor_key)
                ok = installer.install_mcp_servers(editor_key, Path(workdir))
                dbg.info("headless_mcp_install_done", editor=editor_key, success=ok)
                # Update local config flag based on installation result
                try:
                    cfg = config_manager.load_config()
                    cfg.mcp_server_installed = bool(ok)
                    config_manager.save_config(cfg)
                    dbg.info("headless_saved_mcp_flag", installed=bool(ok))
                except Exception as e:
                    dbg.warning(f"headless_save_mcp_flag_failed: {e}")
            except MCPInstallationError as e:
                dbg.warning(f"headless_mcp_install_error: {e}")
            except Exception as e:
                dbg.warning(f"headless_mcp_install_unexpected: {e}")

            # Persist editor selection in local config and .juno_config.json (for verifier heuristics)
            try:
                editor_display = selected_editor
                if selected_editor.lower() in ("claude_code", "claude code"):
                    editor_display = "Claude Code"
                # Save to local .askbudi/config.json via ConfigManager
                cfg = config_manager.load_config()
                cfg.editor = editor_display
                config_manager.save_config(cfg)
                dbg.info("headless_saved_local_editor", editor=editor_display, path=str(config_manager.config_file))
                cfg_path = workdir / ".juno_config.json"
                import json as _json
                cfg_path.write_text(_json.dumps({"editor": editor_display}), encoding="utf-8")
                dbg.info("headless_wrote_editor_config", editor=editor_display)
            except Exception as e:
                dbg.warning(f"headless_editor_config_failed: {e}")

            # Run verification; allow external checks to validate MCP on CLI-capable editors
            verifier = VerifyAgent(workdir, project_name=workdir.name, logger=dbg)
            import asyncio as _asyncio
            skip_external = False
            out = _asyncio.get_event_loop().run_until_complete(
                verifier.run(skip_external_calls=skip_external)
            )

            # Print concise report
            pass_count = sum(1 for r in out.results if r.status == "PASS")
            fail_count = sum(1 for r in out.results if r.status == "FAIL")
            warn_count = sum(1 for r in out.results if r.status == "WARN")
            info_count = sum(1 for r in out.results if r.status == "INFO")
            console.print(f"[bold]Headless Setup Verification[/bold]")
            console.print(f"PASS: {pass_count}  FAIL: {fail_count}  WARN: {warn_count}  INFO: {info_count}")
            console.print("\n[dim]Full report:[/dim]\n")
            console.print(out.report)
            if report_file:
                try:
                    report_path = Path(report_file)
                    report_path.write_text(out.report, encoding="utf-8")
                    console.print(f"\n[green]Report written to {report_path}[/green]")
                except Exception as e:
                    console.print(f"[red]Failed to write report file: {e}[/red]")
            return
        
        # Load config without forcing UI mode
        
        # Check system status
        system_status = SystemStatus(workdir)
        
        # Start the wizard application with appropriate mode
        if verify_only:
            wizard_app = WizardApp(config_manager, system_status, debug=debug, verify_only_mode=True)
        elif docs_only:
            # --docs-only runs intelligent dependency resolver ONLY
            wizard_app = WizardApp(config_manager, system_status, debug=debug, agentic_resolver_mode=True)
        else:
            wizard_app = WizardApp(config_manager, system_status, debug=debug, auto_start_setup=True)
        wizard_app.run()
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Goodbye![/yellow]")
        raise typer.Exit(0)
    except Exception as e:
        if debug:
            console.print_exception()
        else:
            console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
