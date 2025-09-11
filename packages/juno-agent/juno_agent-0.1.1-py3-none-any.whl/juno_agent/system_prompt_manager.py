"""
System Prompt Manager for Juno Agent

Handles loading system prompts with priority order (highest to lowest):
1. User's local override prompt (./.askbudi/prompts/model_slug.md)
2. User's global override prompt (~/.ASKBUDI/prompts/model_slug.md)
3. Project-specific prompt (./prompts/overrides/model_slug.md)
4. Model's system_prompt in juno_config
5. Model's system_prompt_file reference in juno_config
6. Model's system_prompt_ref to prompt_garden
7. Default system prompt from prompt_garden (default_agent or coding_subagent)
"""

import os
import yaml
from pathlib import Path
from typing import Optional, Dict, Any, Union
import logging
from datetime import datetime
import platform

# Get logger
logger = logging.getLogger(__name__)


class SystemPromptManager:
    """Manages system prompt loading with override chain."""
    
    def __init__(self, workdir: Optional[str] = None, config_manager=None):
        """
        Initialize SystemPromptManager.
        
        Args:
            workdir: Working directory path
            config_manager: ConfigManager instance for project context
        """
        self.workdir = Path(workdir) if workdir else Path.cwd()
        self.config_manager = config_manager
        self.prompt_garden_path = Path(__file__).parent / "prompts" / "prompt_garden.yaml"
        self._prompt_garden_cache = None
        
    def get_system_prompt(self, model_slug: str, juno_config: Dict[str, Any], is_subagent: bool = False) -> tuple[str, str]:
        """
        Get system prompt for a model using override chain.
        
        Args:
            model_slug: Model slug (e.g., "gpt-5-minimal")
            juno_config: juno_config dictionary from model_kwargs
            is_subagent: Whether this is for a subagent (affects default prompt selection)
            
        Returns:
            Tuple of (system_prompt, source_description)
        """
        # Override chain (highest to lowest priority)
        sources = [
            ("user_local_override", self._get_user_local_override_prompt, model_slug),
            ("user_global_override", self._get_user_global_override_prompt, model_slug),
            ("project_override", self._get_project_override_prompt, model_slug),
            ("model_direct", self._get_model_direct_prompt, juno_config),
            ("model_file", self._get_model_file_prompt, juno_config),
            ("prompt_garden_ref", self._get_prompt_garden_ref, juno_config),
            ("default_prompt", self._get_default_prompt, is_subagent)
        ]
        
        for source_name, source_func, arg in sources:
            try:
                if arg is not None:
                    prompt = source_func(arg)
                else:
                    prompt = source_func()
                
                if prompt:
                    # Apply variable substitution
                    final_prompt = self._apply_variable_substitution(prompt, juno_config)
                    logger.info(f"Selected system prompt from: {source_name}")
                    return final_prompt, source_name
                    
            except Exception as e:
                logger.warning(f"Failed to load system prompt from {source_name}: {e}")
                continue
        
        # Fallback to hardcoded prompt if all else fails
        fallback_prompt = self._get_fallback_prompt()
        final_prompt = self._apply_variable_substitution(fallback_prompt, juno_config)
        logger.warning("Using fallback system prompt")
        return final_prompt, "fallback"
    
    def _get_user_global_override_prompt(self, model_slug: str) -> Optional[str]:
        """Get user's global override prompt from ~/.ASKBUDI/prompts/model_slug.md"""
        user_home = Path.home()
        global_prompt_file = user_home / ".ASKBUDI" / "prompts" / f"{model_slug}.md"
        
        if global_prompt_file.exists():
            return global_prompt_file.read_text(encoding='utf-8').strip()
        return None
    
    def _get_user_local_override_prompt(self, model_slug: str) -> Optional[str]:
        """Get user's local override prompt from ./.askbudi/prompts/model_slug.md"""
        local_prompt_file = self.workdir / ".askbudi" / "prompts" / f"{model_slug}.md"
        
        if local_prompt_file.exists():
            return local_prompt_file.read_text(encoding='utf-8').strip()
        return None
    
    def _get_project_override_prompt(self, model_slug: str) -> Optional[str]:
        """Get project-specific prompt from ./prompts/overrides/model_slug.md"""
        override_file = self.workdir / "prompts" / "overrides" / f"{model_slug}.md"
        
        if override_file.exists():
            return override_file.read_text(encoding='utf-8').strip()
        return None
    
    def _get_model_direct_prompt(self, juno_config: Dict[str, Any]) -> Optional[str]:
        """Get direct system_prompt from juno_config"""
        return juno_config.get("system_prompt")
    
    def _get_model_file_prompt(self, juno_config: Dict[str, Any]) -> Optional[str]:
        """Get system prompt from file reference in juno_config"""
        prompt_file = juno_config.get("system_prompt_file")
        if not prompt_file:
            return None
            
        # Try relative to workdir first, then absolute
        file_path = self.workdir / prompt_file
        if not file_path.exists():
            file_path = Path(prompt_file)
            
        if file_path.exists():
            return file_path.read_text(encoding='utf-8').strip()
        return None
    
    def _get_prompt_garden_ref(self, juno_config: Dict[str, Any]) -> Optional[str]:
        """Get system prompt from prompt_garden reference in juno_config"""
        prompt_ref = juno_config.get("system_prompt_ref")
        if not prompt_ref:
            return None
            
        return self._load_prompt_from_garden(prompt_ref)
    
    def _get_default_prompt(self, is_subagent: bool = False) -> Optional[str]:
        """Get default system prompt from prompt_garden"""
        if is_subagent:
            # Try to load dedicated subagent prompt first, fallback to default_agent
            subagent_prompt = self._load_prompt_from_garden("coding_subagent")
            if subagent_prompt:
                return subagent_prompt
        
        return self._load_prompt_from_garden("default_agent")
    
    def _load_prompt_from_garden(self, prompt_key: str) -> Optional[str]:
        """Load a specific prompt from prompt_garden.yaml"""
        if not self._prompt_garden_cache:
            try:
                if self.prompt_garden_path.exists():
                    with open(self.prompt_garden_path, 'r', encoding='utf-8') as f:
                        self._prompt_garden_cache = yaml.safe_load(f)
                else:
                    logger.warning(f"prompt_garden.yaml not found at {self.prompt_garden_path}")
                    return None
            except Exception as e:
                logger.error(f"Failed to load prompt_garden.yaml: {e}")
                return None
        
        prompts = self._prompt_garden_cache.get("prompts", {})
        prompt_config = prompts.get(prompt_key)
        
        if prompt_config and isinstance(prompt_config, dict):
            return prompt_config.get("prompt")
        return None
    
    def _apply_variable_substitution(self, prompt: str, juno_config: Dict[str, Any]) -> str:
        """Apply variable substitution to prompt template"""
        if not prompt:
            return prompt
            
        variables = self._get_template_variables(juno_config)
        
        try:
            return prompt.format(**variables)
        except KeyError as e:
            # If template variable is missing, log warning and return as-is
            logger.warning(f"Template variable {e} not found, using prompt as-is")
            return prompt
    
    def _get_template_variables(self, juno_config: Dict[str, Any]) -> Dict[str, str]:
        """Get template variables for prompt substitution"""
        variables = {
            "WORKING_DIRECTORY": str(self.workdir),
            "PLATFORM": platform.system(),
            "ARCHITECTURE": platform.machine(),
            "CURRENT_DATE": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        
        # Add project context
        project_context = self._get_project_context()
        variables["PROJECT_CONTEXT"] = project_context
        
        # Add reasoning effort for GPT-5 models
        reasoning_effort = juno_config.get("reasoning_effort", "default")
        variables["REASONING_EFFORT"] = reasoning_effort
        
        return variables
    
    def _get_project_context(self) -> str:
        """Get project context information"""
        if not self.config_manager:
            return "No project context available"
            
        try:
            config = self.config_manager.load_config()
            context_parts = []
            
            if config.project_description:
                context_parts.append(f"Project: {config.project_description}")
            
            if config.libraries:
                libs = ', '.join(config.libraries[:10])
                context_parts.append(f"Dependencies: {libs}")
                if len(config.libraries) > 10:
                    context_parts.append(f"... and {len(config.libraries) - 10} more")
            
            if config.editor:
                context_parts.append(f"Editor: {config.editor}")
                
            return "\n".join(context_parts) if context_parts else "No project context available"
            
        except Exception as e:
            logger.warning(f"Failed to get project context: {e}")
            return "No project context available"
    
    def _get_fallback_prompt(self) -> str:
        """Fallback system prompt if all other sources fail"""
        return """You are a helpful AI coding assistant integrated into juno-agent.

Working directory: ${WORKING_DIRECTORY}

You have access to the following tools:
- Shell commands for project management and system operations
- File tools: read_file, write_file, update_file, glob_tool, grep_tool for safe file operations
- TodoWrite tool for task management and tracking complex workflows

IMPORTANT: When working with files, be aware of binary files (images, executables, etc.):
- Binary files like PNG, JPG, PDF, etc. cannot be read as text and will cause UnicodeDecodeError
- Before reading files, consider if they might be binary based on their extension
- For binary files, use shell commands like 'file' to get information or 'ls -la' to check size
- Never try to read binary files with read_file tool - inform user about the file type instead

You can help the user with:
- Code analysis and debugging
- File operations and project management (with proper binary file handling)
- Dependency analysis
- Documentation generation
- Testing and validation
- Task planning and organization

Always be helpful, accurate, and safe with code execution. Use the TodoWrite tool to break down complex tasks into manageable steps. Ask for clarification if needed.
You are an autonomous agent, and you take care of the task yourself, instead of advising the user to do a task, you use your tools to perform the task and deliver the result."""