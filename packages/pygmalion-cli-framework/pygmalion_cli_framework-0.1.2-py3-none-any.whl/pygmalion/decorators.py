"""
Decorators for integrating Pygmalion with Click commands.

Provides drop-in decorators that add adaptive behavior to existing
Click applications with minimal code changes.
"""

import functools
from typing import Any, Callable, Dict, Optional
import click

from .core import PygmalionApp


# Global app instance for decorator usage
_default_app: Optional[PygmalionApp] = None


def set_default_app(app: PygmalionApp) -> None:
    """Set the default Pygmalion app for decorators."""
    global _default_app
    _default_app = app


def get_default_app() -> PygmalionApp:
    """Get or create the default Pygmalion app."""
    global _default_app
    if _default_app is None:
        _default_app = PygmalionApp()
    return _default_app


def command(name: Optional[str] = None, cls: Optional[type] = None, **attrs: Any):
    """
    Pygmalion-enhanced version of Click's @command decorator.
    
    This decorator wraps Click commands to add automatic tracking,
    suggestions, and adaptive behavior.
    
    Args:
        name: Command name (optional)
        cls: Command class (optional)
        **attrs: Additional Click command attributes
        
    Returns:
        Decorated command function
    """
    def decorator(f: Callable) -> Callable:
        # Create the Click command first
        click_command = click.command(name, cls, **attrs)(f)
        
        # Get the Pygmalion app
        app = get_default_app()
        
        # Register the command with Pygmalion
        command_name = name or f.__name__
        app.register_command(command_name, click_command)
        
        # Wrap the command function to add tracking
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            # Record command execution
            app.tracker.record_command(command_name, kwargs)
            
            # Execute original function
            result = f(*args, **kwargs)
            
            # Check for suggestions after execution
            app._check_and_show_suggestions()
            
            return result
        
        # Replace the callback in the Click command
        click_command.callback = wrapper
        
        return click_command
    
    return decorator


def group(name: Optional[str] = None, **attrs: Any):
    """
    Pygmalion-enhanced version of Click's @group decorator.
    
    Args:
        name: Group name (optional)
        **attrs: Additional Click group attributes
        
    Returns:
        Decorated group function
    """
    def decorator(f: Callable) -> Callable:
        # Create the Click group first
        click_group = click.group(name, **attrs)(f)
        
        # Get the Pygmalion app
        app = get_default_app()
        
        # Enhance the group's get_command method to support aliases
        original_get_command = click_group.get_command
        
        def enhanced_get_command(ctx: click.Context, cmd_name: str):
            # First try to get regular command
            cmd = original_get_command(ctx, cmd_name)
            if cmd:
                return cmd
            
            # Try to resolve as alias
            alias = app.alias_manager.get_alias(cmd_name)
            if alias:
                # Get the original command
                original_cmd = original_get_command(ctx, alias.command)
                if original_cmd:
                    # Create a wrapped command that applies alias args
                    return _create_aliased_command(original_cmd, alias)
            
            # Try to resolve as workflow
            workflow = app.alias_manager.get_workflow(cmd_name)
            if workflow:
                return _create_workflow_command(workflow, app)
            
            return None
        
        click_group.get_command = enhanced_get_command
        
        # Enhance list_commands to include aliases and workflows
        original_list_commands = click_group.list_commands
        
        def enhanced_list_commands(ctx: click.Context):
            commands = original_list_commands(ctx)
            
            # Add aliases
            aliases = app.alias_manager.list_aliases()
            commands.extend([alias.name for alias in aliases])
            
            # Add workflows
            workflows = app.alias_manager.list_workflows()
            commands.extend([workflow.name for workflow in workflows])
            
            return sorted(set(commands))
        
        click_group.list_commands = enhanced_list_commands
        
        return click_group
    
    return decorator


def _create_aliased_command(original_cmd: click.Command, alias) -> click.Command:
    """Create a command that applies alias arguments."""
    
    class AliasedCommand(click.Command):
        def __init__(self):
            super().__init__(
                name=alias.name,
                callback=original_cmd.callback,
                params=original_cmd.params,
                help=f"Alias for: {alias.command} (with preset options)"
            )
        
        def invoke(self, ctx: click.Context):
            # Merge alias args with provided args
            for key, value in alias.args.items():
                if key not in ctx.params:
                    ctx.params[key] = value
            
            return super().invoke(ctx)
    
    return AliasedCommand()


def _create_workflow_command(workflow, app: PygmalionApp) -> click.Command:
    """Create a command that executes a workflow."""
    
    class WorkflowCommand(click.Command):
        def __init__(self):
            super().__init__(
                name=workflow.name,
                callback=self.execute_workflow,
                help=f"Workflow: {' → '.join([cmd['command'] for cmd in workflow.commands])}"
            )
        
        def execute_workflow(self, **kwargs):
            """Execute the workflow commands in sequence."""
            results = []
            
            for command_spec in workflow.commands:
                command_name = command_spec["command"]
                command_args = command_spec["args"].copy()
                
                # Merge any provided arguments
                command_args.update(kwargs)
                
                # Get the registered command
                if command_name in app._command_registry:
                    command_func = app._command_registry[command_name]
                    
                    # Record the execution
                    app.tracker.record_command(command_name, command_args)
                    
                    # Execute the command
                    result = command_func.callback(**command_args)
                    results.append(result)
                else:
                    click.echo(f"Warning: Command '{command_name}' not found in workflow")
            
            return results
    
    return WorkflowCommand()


def enable_suggestions(threshold: int = 3):
    """
    Decorator to enable automatic suggestions for a command group.
    
    Args:
        threshold: Number of uses before showing suggestions
        
    Returns:
        Decorator function
    """
    def decorator(f: Callable) -> Callable:
        app = get_default_app()
        app.suggestion_threshold = threshold
        app.suggestions_enabled = True
        return f
    
    return decorator


def track_only(f: Callable) -> Callable:
    """
    Decorator to only track commands without showing suggestions.
    
    Args:
        f: Function to decorate
        
    Returns:
        Decorated function
    """
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        app = get_default_app()
        
        # Record command but don't show suggestions
        command_name = f.__name__
        app.tracker.record_command(command_name, kwargs)
        
        return f(*args, **kwargs)
    
    return wrapper


def with_adaptive_help(f: Callable) -> Callable:
    """
    Decorator to enable adaptive help for a command.
    
    Args:
        f: Function to decorate
        
    Returns:
        Decorated function with adaptive help
    """
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)
    
    # Modify the Click command to use adaptive help
    if hasattr(wrapper, '__click_params__'):
        # This would be integrated with Click's help system
        # For now, this is a placeholder for the concept
        pass
    
    return wrapper


class PygmalionMultiCommand(click.MultiCommand):
    """
    Enhanced MultiCommand that supports aliases and workflows.
    """
    
    def __init__(self, app: PygmalionApp, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app
    
    def get_command(self, ctx: click.Context, cmd_name: str):
        # Try regular command resolution first
        cmd = super().get_command(ctx, cmd_name)
        if cmd:
            return cmd
        
        # Try alias resolution
        alias = self.app.alias_manager.get_alias(cmd_name)
        if alias:
            original_cmd = super().get_command(ctx, alias.command)
            if original_cmd:
                return _create_aliased_command(original_cmd, alias)
        
        # Try workflow resolution
        workflow = self.app.alias_manager.get_workflow(cmd_name)
        if workflow:
            return _create_workflow_command(workflow, self.app)
        
        return None
    
    def list_commands(self, ctx: click.Context):
        commands = super().list_commands(ctx)
        
        # Add aliases and workflows
        aliases = [alias.name for alias in self.app.alias_manager.list_aliases()]
        workflows = [wf.name for wf in self.app.alias_manager.list_workflows()]
        
        return sorted(set(commands + aliases + workflows))


def pygmalion_main(app: Optional[PygmalionApp] = None):
    """
    Main entry point decorator for Pygmalion-enhanced CLI apps.
    
    Args:
        app: Optional PygmalionApp instance
        
    Returns:
        Decorator function
    """
    def decorator(f: Callable) -> Callable:
        if app:
            set_default_app(app)
        
        @functools.wraps(f)
        def wrapper():
            current_app = app or get_default_app()
            
            # Show startup suggestions if enabled
            if current_app.suggestions_enabled:
                current_app._maybe_show_startup_suggestions()
            
            return f()
        
        return wrapper
    
    return decorator
