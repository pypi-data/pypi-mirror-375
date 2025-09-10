"""
Adaptive help system for Pygmalion.

Generates personalized help messages based on user behavior,
command frequency, and usage patterns.
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import click

from .tracker import CommandTracker
from .alias import AliasManager


class AdaptiveHelp:
    """Generates personalized and adaptive help messages."""
    
    def __init__(self, tracker: CommandTracker, alias_manager: AliasManager):
        """
        Initialize adaptive help system.
        
        Args:
            tracker: Command tracker for usage analytics  
            alias_manager: Alias manager for shortcuts
        """
        self.tracker = tracker
        self.alias_manager = alias_manager
    
    def generate_main_help(self, ctx: click.Context, 
                          original_help: str) -> str:
        """
        Generate personalized main help message.
        
        Args:
            ctx: Click context
            original_help: Original help text from Click
            
        Returns:
            Enhanced help message with personalization
        """
        lines = [original_help]
        
        # Add usage analytics section
        usage_section = self._generate_usage_section()
        if usage_section:
            lines.extend(["\n", usage_section])
        
        # Add aliases section
        aliases_section = self._generate_aliases_section()
        if aliases_section:
            lines.extend(["\n", aliases_section])
        
        # Add suggestions section
        suggestions_section = self._generate_suggestions_section()
        if suggestions_section:
            lines.extend(["\n", suggestions_section])
        
        return "\n".join(lines)
    
    def _generate_usage_section(self) -> Optional[str]:
        """Generate the usage analytics section."""
        frequency = self.tracker.get_command_frequency()
        
        if not frequency:
            return None
        
        most_used = self.tracker.get_most_used_commands(5)
        
        lines = [
            click.style("📊 Your Most Used Commands:", fg="blue", bold=True),
        ]
        
        for command, count in most_used:
            percentage = (count / sum(frequency.values())) * 100
            bar_length = int(percentage / 5)  # Scale bar to reasonable size
            bar = "█" * bar_length + "░" * (20 - bar_length)
            
            lines.append(
                f"  {command:<15} {bar} {count:>3} times ({percentage:.1f}%)"
            )
        
        return "\n".join(lines)
    
    def _generate_aliases_section(self) -> Optional[str]:
        """Generate the aliases section."""
        aliases = self.alias_manager.list_aliases()
        
        if not aliases:
            return None
        
        lines = [
            click.style("⚡ Available Shortcuts:", fg="green", bold=True),
        ]
        
        for alias in aliases[:5]:  # Show top 5 aliases
            args_str = self._format_args_for_display(alias.args)
            lines.append(
                f"  {alias.name:<15} → {alias.command} {args_str}"
            )
        
        if len(aliases) > 5:
            lines.append(f"  ... and {len(aliases) - 5} more aliases")
        
        return "\n".join(lines)
    
    def _generate_suggestions_section(self) -> Optional[str]:
        """Generate the suggestions section."""
        suggestions = self.tracker.suggest_optimizations()
        
        if not suggestions:
            return None
        
        lines = [
            click.style("💡 Suggestions:", fg="yellow", bold=True),
        ]
        
        for suggestion in suggestions[:3]:  # Show top 3 suggestions
            icon = self._get_suggestion_icon(suggestion["type"])
            lines.append(f"  {icon} {suggestion['message']}")
        
        return "\n".join(lines)
    
    def _get_suggestion_icon(self, suggestion_type: str) -> str:
        """Get icon for suggestion type."""
        icons = {
            "alias": "🔗",
            "workflow": "🔄", 
            "discovery": "🌟"
        }
        return icons.get(suggestion_type, "💡")
    
    def _format_args_for_display(self, args: Dict[str, Any]) -> str:
        """Format command arguments for display."""
        if not args:
            return ""
        
        parts = []
        for key, value in args.items():
            if isinstance(value, bool):
                if value:
                    parts.append(f"--{key}")
            else:
                parts.append(f"--{key}={value}")
        
        return " ".join(parts)
    
    def generate_command_help(self, ctx: click.Context, command_name: str,
                            original_help: str) -> str:
        """
        Generate personalized help for a specific command.
        
        Args:
            ctx: Click context
            command_name: Name of the command
            original_help: Original help text
            
        Returns:
            Enhanced help message
        """
        lines = [original_help]
        
        # Add usage patterns for this command
        patterns_section = self._generate_command_patterns_section(command_name)
        if patterns_section:
            lines.extend(["\n", patterns_section])
        
        # Add related suggestions
        suggestions_section = self._generate_command_suggestions_section(command_name)
        if suggestions_section:
            lines.extend(["\n", suggestions_section])
        
        return "\n".join(lines)
    
    def _generate_command_patterns_section(self, command_name: str) -> Optional[str]:
        """Generate usage patterns section for a specific command."""
        patterns = self.tracker.get_command_patterns().get(command_name, [])
        
        if not patterns:
            return None
        
        # Count pattern usage
        from collections import Counter
        pattern_counts = Counter(item["pattern"] for item in patterns)
        most_common = pattern_counts.most_common(3)
        
        lines = [
            click.style(f"📈 How you usually use '{command_name}':", fg="cyan", bold=True),
        ]
        
        for pattern, count in most_common:
            percentage = (count / len(patterns)) * 100
            lines.append(f"  {pattern:<30} {count:>3} times ({percentage:.1f}%)")
        
        return "\n".join(lines)
    
    def _generate_command_suggestions_section(self, command_name: str) -> Optional[str]:
        """Generate suggestions section for a specific command."""
        suggestions = []
        
        # Check for potential aliases
        repetitive = self.tracker.get_repetitive_patterns()
        command_repetitive = [
            p for p in repetitive 
            if p["command"] == command_name
        ]
        
        if command_repetitive:
            best = command_repetitive[0]
            suggested_name = self.alias_manager.suggest_alias_name(
                command_name, best["example_args"]
            )
            suggestions.append(
                f"🔗 Create alias '{suggested_name}' for your common usage pattern"
            )
        
        # Check for unused options (simplified)
        unused = self.tracker.get_unused_options(command_name)
        if unused:
            suggestions.append(
                f"🌟 Try these options you haven't used: {', '.join(unused[:2])}"
            )
        
        if not suggestions:
            return None
        
        lines = [
            click.style("💡 Tips:", fg="yellow", bold=True),
        ]
        lines.extend(f"  {suggestion}" for suggestion in suggestions[:3])
        
        return "\n".join(lines)
    
    def get_smart_completions(self, ctx: click.Context, 
                            param: click.Parameter, 
                            incomplete: str) -> List[str]:
        """
        Generate smart completions based on usage history.
        
        Args:
            ctx: Click context
            param: Parameter being completed
            incomplete: Incomplete text
            
        Returns:
            List of completion suggestions
        """
        completions = []
        
        # If completing a command name, prioritize by frequency
        if isinstance(param, click.Command):
            frequency = self.tracker.get_command_frequency()
            commands = sorted(frequency.items(), key=lambda x: x[1], reverse=True)
            
            completions.extend([
                cmd for cmd, _ in commands 
                if cmd.startswith(incomplete)
            ])
        
        # Add alias completions
        aliases = self.alias_manager.list_aliases()
        alias_names = [alias.name for alias in aliases if alias.name.startswith(incomplete)]
        completions.extend(alias_names)
        
        return completions
    
    def show_interactive_suggestions(self) -> None:
        """Show interactive suggestions that user can act upon."""
        suggestions = self.tracker.suggest_optimizations()
        
        if not suggestions:
            click.echo(click.style("✨ No suggestions at this time!", fg="green"))
            return
        
        click.echo(click.style("\n💡 Pygmalion has some suggestions for you:", 
                              fg="blue", bold=True))
        
        for i, suggestion in enumerate(suggestions[:3], 1):
            click.echo(f"\n{i}. {suggestion['message']}")
            
            if suggestion["type"] == "alias":
                self._handle_alias_suggestion(suggestion)
            elif suggestion["type"] == "workflow":
                self._handle_workflow_suggestion(suggestion)
    
    def _handle_alias_suggestion(self, suggestion: Dict[str, Any]) -> None:
        """Handle interactive alias creation suggestion."""
        data = suggestion["data"]
        suggested_name = self.alias_manager.suggest_alias_name(
            data["command"], data["example_args"]
        )
        
        if click.confirm(f"   Create alias '{suggested_name}'?", default=False):
            alias_name = click.prompt("   Alias name", default=suggested_name)
            
            success = self.alias_manager.create_alias(
                alias_name, 
                data["command"], 
                data["example_args"],
                f"Auto-generated alias for common usage pattern"
            )
            
            if success:
                click.echo(click.style(f"   ✅ Alias '{alias_name}' created!", fg="green"))
            else:
                click.echo(click.style(f"   ❌ Failed to create alias.", fg="red"))
    
    def _handle_workflow_suggestion(self, suggestion: Dict[str, Any]) -> None:
        """Handle interactive workflow creation suggestion."""
        data = suggestion["data"]
        sequence = data["sequence"]
        suggested_name = self.alias_manager.suggest_workflow_name(sequence)
        
        if click.confirm(f"   Create workflow '{suggested_name}'?", default=False):
            workflow_name = click.prompt("   Workflow name", default=suggested_name)
            
            # Convert sequence to workflow commands format
            commands = [
                {"command": cmd, "args": {}} 
                for cmd in sequence
            ]
            
            success = self.alias_manager.create_workflow(
                workflow_name,
                commands,
                f"Auto-generated workflow for common command sequence"
            )
            
            if success:
                click.echo(click.style(f"   ✅ Workflow '{workflow_name}' created!", fg="green"))
            else:
                click.echo(click.style(f"   ❌ Failed to create workflow.", fg="red"))
    
    def get_recent_activity_summary(self, days: int = 7) -> Dict[str, Any]:
        """
        Get summary of recent activity.
        
        Args:
            days: Number of days to look back
            
        Returns:
            Activity summary dictionary
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        history = self.tracker.storage.get_command_history()
        
        # Filter recent commands
        recent_commands = [
            record for record in history
            if datetime.fromisoformat(record["timestamp"]) >= cutoff_date
        ]
        
        if not recent_commands:
            return {
                "total_commands": 0,
                "unique_commands": 0,
                "days": days,
                "most_used": [],
                "daily_average": 0.0,
                "peak_day": None
            }
        
        # Calculate statistics
        commands = [record["command"] for record in recent_commands]
        from collections import Counter
        command_counts = Counter(commands)
        
        return {
            "total_commands": len(recent_commands),
            "unique_commands": len(set(commands)),
            "days": days,
            "most_used": command_counts.most_common(5),
            "daily_average": len(recent_commands) / days,
            "peak_day": self._get_peak_day(recent_commands)
        }
    
    def _get_peak_day(self, commands: List[Dict[str, Any]]) -> Tuple[str, int]:
        """Find the day with most command usage."""
        from collections import defaultdict
        
        daily_counts = defaultdict(int)
        
        for record in commands:
            date = datetime.fromisoformat(record["timestamp"]).date()
            daily_counts[date] += 1
        
        if not daily_counts:
            return ("None", 0)
        
        peak_date, peak_count = max(daily_counts.items(), key=lambda x: x[1])
        return (peak_date.strftime("%Y-%m-%d"), peak_count)
