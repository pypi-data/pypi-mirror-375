"""
Alias and workflow management for Pygmalion.

Handles creation, storage, and execution of command aliases
and multi-command workflows.
"""

import re
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass

from .storage import StorageBackend


@dataclass
class Alias:
    """Represents a command alias."""
    name: str
    command: str
    args: Dict[str, Any]
    description: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert alias to dictionary for storage."""
        return {
            "command": self.command,
            "args": self.args,
            "description": self.description
        }


@dataclass
class Workflow:
    """Represents a multi-command workflow."""
    name: str
    commands: List[Dict[str, Any]]
    description: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert workflow to dictionary for storage."""
        return {
            "commands": self.commands,
            "description": self.description
        }


class AliasManager:
    """Manages command aliases and workflows."""
    
    def __init__(self, storage: StorageBackend):
        """
        Initialize alias manager.
        
        Args:
            storage: Storage backend for persistence
        """
        self.storage = storage
        self._command_registry = {}  # Will store actual Click commands
    
    def register_command(self, name: str, command_func: Callable) -> None:
        """
        Register a Click command for alias execution.
        
        Args:
            name: Command name
            command_func: Click command function
        """
        self._command_registry[name] = command_func
    
    def create_alias(self, alias_name: str, command: str, args: Dict[str, Any],
                    description: Optional[str] = None) -> bool:
        """
        Create a new command alias.
        
        Args:
            alias_name: Name for the alias
            command: Original command name
            args: Command arguments and options
            description: Optional description
            
        Returns:
            True if alias was created successfully
        """
        # Validate alias name
        if not self._is_valid_alias_name(alias_name):
            return False
        
        # Check if alias already exists
        existing_aliases = self.storage.get_aliases()
        if alias_name in existing_aliases:
            return False
        
        # Store alias
        alias_data = {
            "command": command,
            "args": args,
            "description": description
        }
        
        self.storage.store_alias(alias_name, command, args)
        return True
    
    def _is_valid_alias_name(self, name: str) -> bool:
        """Validate alias name format."""
        # Allow alphanumeric, hyphens, underscores
        pattern = r'^[a-zA-Z][a-zA-Z0-9_-]*$'
        return bool(re.match(pattern, name)) and len(name) <= 50
    
    def get_alias(self, alias_name: str) -> Optional[Alias]:
        """
        Get an alias by name.
        
        Args:
            alias_name: Name of the alias
            
        Returns:
            Alias object or None if not found
        """
        aliases = self.storage.get_aliases()
        alias_data = aliases.get(alias_name)
        
        if not alias_data:
            return None
        
        return Alias(
            name=alias_name,
            command=alias_data["command"],
            args=alias_data["args"],
            description=alias_data.get("description")
        )
    
    def list_aliases(self) -> List[Alias]:
        """Get all aliases."""
        aliases = self.storage.get_aliases()
        
        return [
            Alias(
                name=name,
                command=data["command"],
                args=data["args"],
                description=data.get("description")
            )
            for name, data in aliases.items()
        ]
    
    def delete_alias(self, alias_name: str) -> bool:
        """
        Delete an alias.
        
        Args:
            alias_name: Name of alias to delete
            
        Returns:
            True if alias was deleted
        """
        # Note: This would require extending the storage interface
        # For now, this is a placeholder
        # In a full implementation, we'd add delete methods to storage
        return True
    
    def execute_alias(self, alias_name: str, additional_args: Optional[Dict[str, Any]] = None) -> Any:
        """
        Execute an alias command.
        
        Args:
            alias_name: Name of alias to execute
            additional_args: Additional arguments to merge
            
        Returns:
            Result of command execution
        """
        alias = self.get_alias(alias_name)
        if not alias:
            raise ValueError(f"Alias '{alias_name}' not found")
        
        # Get the registered command function
        command_func = self._command_registry.get(alias.command)
        if not command_func:
            raise ValueError(f"Command '{alias.command}' not registered")
        
        # Merge arguments
        final_args = alias.args.copy()
        if additional_args:
            final_args.update(additional_args)
        
        # Execute command with merged arguments
        # This is a simplified version - real implementation would need
        # to properly handle Click's parameter system
        return command_func(**final_args)
    
    def create_workflow(self, workflow_name: str, commands: List[Dict[str, Any]],
                       description: Optional[str] = None) -> bool:
        """
        Create a multi-command workflow.
        
        Args:
            workflow_name: Name for the workflow
            commands: List of commands with their arguments
            description: Optional description
            
        Returns:
            True if workflow was created successfully
        """
        # Validate workflow name
        if not self._is_valid_alias_name(workflow_name):
            return False
        
        # Check if workflow already exists
        existing_workflows = self.storage.get_workflows()
        if workflow_name in existing_workflows:
            return False
        
        # Validate commands
        if not commands or not all(self._validate_workflow_command(cmd) for cmd in commands):
            return False
        
        # Store workflow
        self.storage.store_workflow(workflow_name, commands)
        return True
    
    def _validate_workflow_command(self, command: Dict[str, Any]) -> bool:
        """Validate a workflow command structure."""
        return (
            isinstance(command, dict) and
            "command" in command and
            "args" in command and
            isinstance(command["command"], str) and
            isinstance(command["args"], dict)
        )
    
    def get_workflow(self, workflow_name: str) -> Optional[Workflow]:
        """
        Get a workflow by name.
        
        Args:
            workflow_name: Name of the workflow
            
        Returns:
            Workflow object or None if not found
        """
        workflows = self.storage.get_workflows()
        commands = workflows.get(workflow_name)
        
        if not commands:
            return None
        
        return Workflow(
            name=workflow_name,
            commands=commands,
            description=None  # Could be extended to store descriptions
        )
    
    def list_workflows(self) -> List[Workflow]:
        """Get all workflows."""
        workflows = self.storage.get_workflows()
        
        return [
            Workflow(
                name=name,
                commands=commands,
                description=None
            )
            for name, commands in workflows.items()
        ]
    
    def execute_workflow(self, workflow_name: str, 
                        additional_args: Optional[Dict[str, Any]] = None) -> List[Any]:
        """
        Execute a workflow.
        
        Args:
            workflow_name: Name of workflow to execute
            additional_args: Additional arguments for all commands
            
        Returns:
            List of results from each command
        """
        workflow = self.get_workflow(workflow_name)
        if not workflow:
            raise ValueError(f"Workflow '{workflow_name}' not found")
        
        results = []
        
        for command_spec in workflow.commands:
            command_name = command_spec["command"]
            command_args = command_spec["args"].copy()
            
            # Merge additional arguments if provided
            if additional_args:
                command_args.update(additional_args)
            
            # Get and execute command
            command_func = self._command_registry.get(command_name)
            if not command_func:
                raise ValueError(f"Command '{command_name}' not registered")
            
            result = command_func(**command_args)
            results.append(result)
        
        return results
    
    def suggest_alias_name(self, command: str, args: Dict[str, Any]) -> str:
        """
        Suggest a name for an alias based on command and arguments.
        
        Args:
            command: Command name
            args: Command arguments
            
        Returns:
            Suggested alias name
        """
        # Start with command name
        parts = [command]
        
        # Add significant arguments
        for key, value in args.items():
            if isinstance(value, bool) and value:
                # For flags, add the flag name
                parts.append(key.replace("-", ""))
            elif value is not None and not isinstance(value, bool):
                # For non-bool values, add parameter name
                parts.append(key.replace("-", ""))
        
        # Join parts and ensure it's a valid name
        suggested = "-".join(parts)[:30]  # Limit length
        
        # Ensure it doesn't conflict with existing aliases
        existing_aliases = self.storage.get_aliases()
        counter = 1
        original_suggested = suggested
        
        while suggested in existing_aliases:
            suggested = f"{original_suggested}-{counter}"
            counter += 1
        
        return suggested
    
    def suggest_workflow_name(self, commands: List[str]) -> str:
        """
        Suggest a name for a workflow based on command sequence.
        
        Args:
            commands: List of command names
            
        Returns:
            Suggested workflow name
        """
        if len(commands) <= 3:
            # For short sequences, join command names
            suggested = "-".join(commands)
        else:
            # For longer sequences, use first and last
            suggested = f"{commands[0]}-to-{commands[-1]}"
        
        # Ensure it doesn't conflict with existing workflows
        existing_workflows = self.storage.get_workflows()
        counter = 1
        original_suggested = suggested
        
        while suggested in existing_workflows:
            suggested = f"{original_suggested}-{counter}"
            counter += 1
        
        return suggested
    
    def get_alias_suggestions(self, command: str, args: Dict[str, Any], 
                            usage_count: int) -> Dict[str, Any]:
        """
        Get suggestion data for creating an alias.
        
        Args:
            command: Command name
            args: Command arguments
            usage_count: How many times this pattern was used
            
        Returns:
            Suggestion data dictionary
        """
        suggested_name = self.suggest_alias_name(command, args)
        
        return {
            "type": "alias",
            "suggested_name": suggested_name,
            "command": command,
            "args": args,
            "usage_count": usage_count,
            "description": f"Shortcut for '{command}' with specific options"
        }
