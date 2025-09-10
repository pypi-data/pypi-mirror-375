"""
Command tracking and analytics for Pygmalion.

Monitors command usage patterns, frequencies, and sequences
to enable intelligent suggestions and adaptive behavior.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter, defaultdict
import re

from .storage import StorageBackend


class CommandTracker:
    """Tracks command usage patterns and provides analytics."""
    
    def __init__(self, storage: StorageBackend, suggestion_threshold: int = 3):
        """
        Initialize command tracker.
        
        Args:
            storage: Storage backend for persistence
            suggestion_threshold: Minimum uses before suggesting optimizations
        """
        self.storage = storage
        self.suggestion_threshold = suggestion_threshold
        self._session_commands = []  # Track current session
    
    def record_command(self, command: str, args: Dict[str, Any], 
                      timestamp: Optional[datetime] = None) -> None:
        """
        Record a command execution.
        
        Args:
            command: Command name
            args: Command arguments and options
            timestamp: When command was executed (defaults to now)
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        # Store in persistent storage
        self.storage.record_command(command, args, timestamp)
        
        # Track in current session
        self._session_commands.append({
            "command": command,
            "args": args,
            "timestamp": timestamp
        })
    
    def get_command_frequency(self) -> Dict[str, int]:
        """Get frequency count for each command."""
        return self.storage.get_command_frequency()
    
    def get_most_used_commands(self, limit: int = 10) -> List[Tuple[str, int]]:
        """
        Get most frequently used commands.
        
        Args:
            limit: Maximum number of commands to return
            
        Returns:
            List of (command, count) tuples sorted by frequency
        """
        frequency = self.get_command_frequency()
        return sorted(frequency.items(), key=lambda x: x[1], reverse=True)[:limit]
    
    def get_command_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Analyze command usage patterns.
        
        Returns:
            Dictionary mapping commands to their usage patterns
        """
        history = self.storage.get_command_history()
        patterns = defaultdict(list)
        
        for record in history:
            command = record["command"]
            args = record["args"]
            
            # Create pattern signature from arguments
            pattern = self._create_pattern_signature(args)
            patterns[command].append({
                "pattern": pattern,
                "args": args,
                "timestamp": record["timestamp"]
            })
        
        return dict(patterns)
    
    def _create_pattern_signature(self, args: Dict[str, Any]) -> str:
        """Create a signature for argument patterns."""
        if not args:
            return "no_args"
        
        # Sort arguments for consistent signatures
        sorted_args = sorted(args.items())
        signature_parts = []
        
        for key, value in sorted_args:
            if isinstance(value, bool):
                if value:
                    signature_parts.append(f"--{key}")
            else:
                signature_parts.append(f"--{key}={type(value).__name__}")
        
        return " ".join(signature_parts) if signature_parts else "no_args"
    
    def get_repetitive_patterns(self) -> List[Dict[str, Any]]:
        """
        Find repetitive command patterns that could be aliased.
        
        Returns:
            List of patterns used frequently enough to suggest aliases
        """
        patterns = self.get_command_patterns()
        repetitive = []
        
        for command, usage_list in patterns.items():
            # Count pattern frequencies
            pattern_counts = Counter(item["pattern"] for item in usage_list)
            
            for pattern, count in pattern_counts.items():
                if count >= self.suggestion_threshold:
                    # Find a representative example
                    example = next(
                        item for item in usage_list 
                        if item["pattern"] == pattern
                    )
                    
                    repetitive.append({
                        "command": command,
                        "pattern": pattern,
                        "count": count,
                        "example_args": example["args"],
                        "suggestion_score": count / len(usage_list)
                    })
        
        # Sort by suggestion score (higher is better)
        return sorted(repetitive, key=lambda x: x["suggestion_score"], reverse=True)
    
    def get_command_sequences(self, min_length: int = 2, 
                            min_frequency: int = 2) -> List[Dict[str, Any]]:
        """
        Find common command sequences for workflow suggestions.
        
        Args:
            min_length: Minimum sequence length
            min_frequency: Minimum times sequence must occur
            
        Returns:
            List of command sequences with metadata
        """
        sequences = self.storage.get_command_sequences(min_length)
        
        # Count sequence frequencies
        sequence_counts = Counter(tuple(seq) for seq in sequences)
        
        # Filter by minimum frequency
        frequent_sequences = [
            {
                "sequence": list(seq),
                "count": count,
                "suggestion_score": count / len(sequences) if sequences else 0
            }
            for seq, count in sequence_counts.items()
            if count >= min_frequency
        ]
        
        return sorted(frequent_sequences, key=lambda x: x["suggestion_score"], reverse=True)
    
    def get_unused_options(self, command: str) -> List[str]:
        """
        Find options/flags that haven't been used for a command.
        
        Args:
            command: Command to analyze
            
        Returns:
            List of unused option patterns (this is a simplified implementation)
        """
        patterns = self.get_command_patterns().get(command, [])
        
        if not patterns:
            return []
        
        # This is a simplified implementation
        # In practice, you'd want to introspect the actual Click command
        # to get all available options
        used_patterns = set(item["pattern"] for item in patterns)
        
        # Mock some common options for demonstration
        common_options = [
            "--verbose", "--quiet", "--help", "--version",
            "--output", "--format", "--config", "--debug"
        ]
        
        # This is a placeholder - real implementation would need 
        # integration with Click's command introspection
        return common_options  # Simplified for now
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get statistics for the current session."""
        if not self._session_commands:
            return {"total_commands": 0, "unique_commands": 0, "duration": 0}
        
        start_time = self._session_commands[0]["timestamp"]
        end_time = self._session_commands[-1]["timestamp"]
        duration = (end_time - start_time).total_seconds()
        
        commands = [cmd["command"] for cmd in self._session_commands]
        
        return {
            "total_commands": len(commands),
            "unique_commands": len(set(commands)),
            "duration": duration,
            "most_used": Counter(commands).most_common(5),
            "commands_per_minute": len(commands) / max(duration / 60, 1)
        }
    
    def get_time_based_patterns(self) -> Dict[str, Any]:
        """Analyze command usage by time patterns."""
        history = self.storage.get_command_history()
        
        if not history:
            return {}
        
        # Group by hour of day
        hourly_usage = defaultdict(list)
        daily_usage = defaultdict(list)
        
        for record in history:
            timestamp = datetime.fromisoformat(record["timestamp"])
            hour = timestamp.hour
            day = timestamp.strftime("%A")
            
            hourly_usage[hour].append(record["command"])
            daily_usage[day].append(record["command"])
        
        return {
            "peak_hours": {
                hour: len(commands) 
                for hour, commands in hourly_usage.items()
            },
            "daily_patterns": {
                day: Counter(commands).most_common(3)
                for day, commands in daily_usage.items()
            }
        }
    
    def suggest_optimizations(self) -> List[Dict[str, Any]]:
        """
        Generate optimization suggestions based on usage patterns.
        
        Returns:
            List of suggestions with types and metadata
        """
        suggestions = []
        
        # Alias suggestions
        repetitive = self.get_repetitive_patterns()
        for pattern in repetitive[:3]:  # Top 3 suggestions
            suggestions.append({
                "type": "alias",
                "priority": "high" if pattern["count"] >= 5 else "medium",
                "message": (
                    f"You've used '{pattern['command']}' with the same options "
                    f"{pattern['count']} times. Create an alias?"
                ),
                "data": pattern
            })
        
        # Workflow suggestions
        sequences = self.get_command_sequences()
        for sequence in sequences[:2]:  # Top 2 workflow suggestions
            suggestions.append({
                "type": "workflow",
                "priority": "medium",
                "message": (
                    f"You often run {' → '.join(sequence['sequence'])}. "
                    f"Create a workflow?"
                ),
                "data": sequence
            })
        
        # Feature discovery suggestions
        frequency = self.get_command_frequency()
        most_used = max(frequency.items(), key=lambda x: x[1])[0] if frequency else None
        
        if most_used:
            unused = self.get_unused_options(most_used)[:2]
            for option in unused:
                suggestions.append({
                    "type": "discovery",
                    "priority": "low",
                    "message": (
                        f"Try '{most_used} {option}' - you haven't used this option yet!"
                    ),
                    "data": {"command": most_used, "option": option}
                })
        
        return suggestions
