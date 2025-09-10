"""
Core Pygmalion application class.

The main entry point for creating adaptive CLI applications with
command tracking, suggestions, and intelligent behavior.
"""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from .storage import StorageBackend, JSONStorage, SQLiteStorage
from .tracker import CommandTracker
from .alias import AliasManager
from .help import AdaptiveHelp


class PygmalionApp:
    """
    Main Pygmalion application class.
    
    This class wraps Click applications to add adaptive behavior,
    command tracking, and intelligent suggestions.
    """
    
    def __init__(
        self,
        name: Optional[str] = None,
        storage_backend: str = "json",
        storage_path: Optional[str] = None,
        suggestion_threshold: int = 3,
        workflow_threshold: int = 3,
        analytics_enabled: bool = True,
        suggestions_enabled: bool = True,
        help_personalization: bool = True,
        **kwargs
    ):
        """
        Initialize Pygmalion application.
        
        Args:
            name: Application name (defaults to 'pygmalion-app')
            storage_backend: 'json' or 'sqlite'
            storage_path: Custom storage path
            suggestion_threshold: Commands uses before suggesting aliases
            workflow_threshold: Sequence occurrences before suggesting workflows
            analytics_enabled: Enable usage analytics
            suggestions_enabled: Enable automatic suggestions
            help_personalization: Enable personalized help messages
            **kwargs: Additional configuration options
        """
        self.name = name or "pygmalion-app"
        self.suggestion_threshold = suggestion_threshold
        self.workflow_threshold = workflow_threshold
        self.analytics_enabled = analytics_enabled
        self.suggestions_enabled = suggestions_enabled
        self.help_personalization = help_personalization
        
        # Initialize storage backend
        if storage_backend.lower() == "sqlite":
            self.storage = SQLiteStorage(self.name, storage_path)
        else:
            self.storage = JSONStorage(self.name, storage_path)
        
        # Initialize core components
        self.tracker = CommandTracker(self.storage, suggestion_threshold)
        self.alias_manager = AliasManager(self.storage)
        self.help = AdaptiveHelp(self.tracker, self.alias_manager)
        
        # Command registry for alias/workflow execution
        self._command_registry: Dict[str, click.Command] = {}
        
        # Console for rich output
        self.console = Console()
        
        # Track suggestion cooldowns to avoid spam
        self._last_suggestion_check = 0
    
    def register_command(self, name: str, command: click.Command) -> None:
        """
        Register a Click command with Pygmalion.
        
        Args:
            name: Command name
            command: Click command object
        """
        self._command_registry[name] = command
        self.alias_manager.register_command(name, command)
    
    def create_alias(self, alias_name: str, command: str, args: Dict[str, Any],
                    description: Optional[str] = None) -> bool:
        """
        Create a command alias.
        
        Args:
            alias_name: Name for the alias
            command: Original command name
            args: Command arguments
            description: Optional description
            
        Returns:
            True if alias was created successfully
        """
        return self.alias_manager.create_alias(alias_name, command, args, description)
    
    def create_workflow(self, workflow_name: str, commands: List[Dict[str, Any]],
                       description: Optional[str] = None) -> bool:
        """
        Create a command workflow.
        
        Args:
            workflow_name: Name for the workflow
            commands: List of commands with arguments
            description: Optional description
            
        Returns:
            True if workflow was created successfully
        """
        return self.alias_manager.create_workflow(workflow_name, commands, description)
    
    def show_suggestions(self) -> None:
        """Show interactive suggestions to the user."""
        if not self.suggestions_enabled:
            return
        
        self.help.show_interactive_suggestions()
    
    def show_analytics(self, days: int = 7) -> None:
        """
        Show usage analytics.
        
        Args:
            days: Number of days to include in analysis
        """
        if not self.analytics_enabled:
            self.console.print("📊 Analytics are disabled", style="yellow")
            return
        
        # Get usage statistics
        frequency = self.tracker.get_command_frequency()
        most_used = self.tracker.get_most_used_commands(10)
        session_stats = self.tracker.get_session_stats()
        recent_activity = self.help.get_recent_activity_summary(days)
        
        # Create analytics panel
        content = []
        
        if frequency:
            total_commands = sum(frequency.values())
            content.append(f"📈 Total Commands Executed: [bold]{total_commands}[/bold]")
            content.append(f"🔢 Unique Commands Used: [bold]{len(frequency)}[/bold]")
            content.append("")
            
            content.append("[bold]Most Used Commands:[/bold]")
            for command, count in most_used[:5]:
                percentage = (count / total_commands) * 100
                bar = "█" * int(percentage / 2) + "░" * (50 - int(percentage / 2))
                content.append(f"  {command:<15} {bar} {count:>3} ({percentage:.1f}%)")
            
            content.append("")
        
        # Session statistics
        if session_stats["total_commands"] > 0:
            content.append("[bold]Current Session:[/bold]")
            content.append(f"  Commands this session: {session_stats['total_commands']}")
            content.append(f"  Unique commands: {session_stats['unique_commands']}")
            content.append(f"  Commands per minute: {session_stats['commands_per_minute']:.1f}")
            content.append("")
        
        # Recent activity
        if recent_activity["total_commands"] > 0:
            content.append(f"[bold]Last {days} Days:[/bold]")
            content.append(f"  Total commands: {recent_activity['total_commands']}")
            content.append(f"  Daily average: {recent_activity['daily_average']:.1f}")
            content.append(f"  Peak day: {recent_activity['peak_day'][0]} ({recent_activity['peak_day'][1]} commands)")
        
        if not content:
            content = ["No usage data available yet. Start using commands to see analytics!"]
        
        panel = Panel(
            "\n".join(content),
            title=f"📊 Pygmalion Analytics - {self.name}",
            border_style="blue"
        )
        
        self.console.print(panel)
    
    def list_aliases(self) -> None:
        """List all available aliases."""
        aliases = self.alias_manager.list_aliases()
        
        if not aliases:
            self.console.print("No aliases created yet.", style="yellow")
            return
        
        content = []
        for alias in aliases:
            args_str = " ".join(f"--{k}={v}" if not isinstance(v, bool) else f"--{k}" 
                              for k, v in alias.args.items() if v)
            content.append(f"[bold]{alias.name}[/bold] → {alias.command} {args_str}")
            if alias.description:
                content.append(f"    {alias.description}")
            content.append("")
        
        panel = Panel(
            "\n".join(content),
            title="⚡ Available Aliases",
            border_style="green"
        )
        
        self.console.print(panel)
    
    def list_workflows(self) -> None:
        """List all available workflows."""
        workflows = self.alias_manager.list_workflows()
        
        if not workflows:
            self.console.print("No workflows created yet.", style="yellow")
            return
        
        content = []
        for workflow in workflows:
            command_names = [cmd["command"] for cmd in workflow.commands]
            content.append(f"[bold]{workflow.name}[/bold]")
            content.append(f"    Steps: {' → '.join(command_names)}")
            if workflow.description:
                content.append(f"    {workflow.description}")
            content.append("")
        
        panel = Panel(
            "\n".join(content),
            title="🔄 Available Workflows",
            border_style="cyan"
        )
        
        self.console.print(panel)
    
    def export_data(self, file_path: str, format: str = "json") -> bool:
        """
        Export Pygmalion data.
        
        Args:
            file_path: Path to export file
            format: Export format ('json' or 'csv')
            
        Returns:
            True if export was successful
        """
        try:
            if format.lower() == "json":
                return self._export_json(file_path)
            elif format.lower() == "csv":
                return self._export_csv(file_path)
            else:
                self.console.print(f"Unsupported format: {format}", style="red")
                return False
        except Exception as e:
            self.console.print(f"Export failed: {e}", style="red")
            return False
    
    def _export_json(self, file_path: str) -> bool:
        """Export data to JSON format."""
        import json
        
        data = {
            "app_name": self.name,
            "commands": self.tracker.storage.get_command_history(),
            "aliases": self.alias_manager.storage.get_aliases(),
            "workflows": self.alias_manager.storage.get_workflows(),
            "analytics": {
                "frequency": self.tracker.get_command_frequency(),
                "patterns": self.tracker.get_command_patterns(),
                "suggestions": self.tracker.suggest_optimizations()
            }
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        
        return True
    
    def _export_csv(self, file_path: str) -> bool:
        """Export command history to CSV format."""
        import csv
        
        history = self.tracker.storage.get_command_history()
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "command", "args"])
            
            for record in history:
                args_str = " ".join(f"--{k}={v}" if not isinstance(v, bool) else f"--{k}"
                                  for k, v in record["args"].items() if v)
                writer.writerow([record["timestamp"], record["command"], args_str])
        
        return True
    
    def reset_data(self, confirm: bool = False) -> bool:
        """
        Reset all Pygmalion data.
        
        Args:
            confirm: Must be True to actually reset
            
        Returns:
            True if data was reset
        """
        if not confirm:
            self.console.print("Use reset_data(confirm=True) to actually reset data", style="yellow")
            return False
        
        try:
            # This would require extending storage backends with reset methods
            # For now, we can delete the storage files
            if isinstance(self.storage, JSONStorage):
                if self.storage.file_path.exists():
                    self.storage.file_path.unlink()
            elif isinstance(self.storage, SQLiteStorage):
                if self.storage.db_path.exists():
                    self.storage.db_path.unlink()
                    
            # Reinitialize storage
            self.storage._init_db() if hasattr(self.storage, '_init_db') else None
            
            self.console.print("✅ Data reset successfully", style="green")
            return True
            
        except Exception as e:
            self.console.print(f"Reset failed: {e}", style="red")
            return False
    
    def _check_and_show_suggestions(self) -> None:
        """Check if we should show suggestions to the user."""
        import time
        
        if not self.suggestions_enabled:
            return
        
        # Implement cooldown to avoid suggestion spam
        current_time = time.time()
        if current_time - self._last_suggestion_check < 30:  # 30 second cooldown
            return
        
        self._last_suggestion_check = current_time
        
        # Get suggestions
        suggestions = self.tracker.suggest_optimizations()
        
        # Show high-priority suggestions immediately
        high_priority = [s for s in suggestions if s.get("priority") == "high"]
        
        if high_priority:
            self.console.print("\n💡 Quick suggestion:", style="yellow bold")
            suggestion = high_priority[0]
            self.console.print(f"   {suggestion['message']}")
            
            # Offer to show all suggestions
            self.console.print("   (Use --suggestions to see all suggestions)", style="dim")
    
    def _maybe_show_startup_suggestions(self) -> None:
        """Maybe show suggestions on app startup."""
        suggestions = self.tracker.suggest_optimizations()
        
        if len(suggestions) >= 2:  # Only show if we have multiple suggestions
            self.console.print(
                f"💡 Pygmalion has {len(suggestions)} suggestions for you! "
                "Use --suggestions to see them.",
                style="yellow"
            )
    
    def run(self) -> None:
        """Run the Pygmalion application (placeholder for integration)."""
        # This would typically be called by the CLI framework
        # For now, it's a placeholder for the concept
        pass
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration."""
        return {
            "name": self.name,
            "storage_backend": type(self.storage).__name__,
            "suggestion_threshold": self.suggestion_threshold,
            "workflow_threshold": self.workflow_threshold,
            "analytics_enabled": self.analytics_enabled,
            "suggestions_enabled": self.suggestions_enabled,
            "help_personalization": self.help_personalization,
        }
    
    def update_config(self, **kwargs) -> None:
        """Update configuration settings."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                self.console.print(f"Unknown config option: {key}", style="yellow")
