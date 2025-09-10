"""
Tests for alias and workflow management functionality.
"""

import pytest
from unittest.mock import Mock

from pygmalion.storage import JSONStorage
from pygmalion.alias import AliasManager, Alias, Workflow


class TestAliasManager:
    """Test cases for AliasManager class."""
    
    @pytest.fixture
    def mock_storage(self):
        """Create a mock storage backend."""
        storage = Mock(spec=JSONStorage)
        storage.get_aliases.return_value = {
            "export-json": {
                "command": "export",
                "args": {"format": "json", "verbose": True},
                "description": "Export in JSON format with verbose output"
            },
            "quick-scan": {
                "command": "scan",
                "args": {"recursive": True},
                "description": "Quick recursive scan"
            }
        }
        storage.get_workflows.return_value = {
            "process-and-export": [
                {"command": "process", "args": {"backup": True}},
                {"command": "export", "args": {"format": "json"}}
            ]
        }
        return storage
    
    @pytest.fixture
    def alias_manager(self, mock_storage):
        """Create an AliasManager with mock storage."""
        return AliasManager(mock_storage)
    
    def test_create_alias_valid(self, alias_manager, mock_storage):
        """Test creating a valid alias."""
        success = alias_manager.create_alias(
            "test-alias",
            "export",
            {"format": "csv", "verbose": True},
            "Test alias description"
        )
        
        assert success is True
        mock_storage.store_alias.assert_called_once_with(
            "test-alias", "export", {"format": "csv", "verbose": True}
        )
    
    def test_create_alias_invalid_name(self, alias_manager):
        """Test creating alias with invalid name."""
        # Test names that should be invalid
        invalid_names = ["", "123invalid", "spaces not allowed", "too-long-" + "x" * 50]
        
        for name in invalid_names:
            success = alias_manager.create_alias(name, "export", {})
            assert success is False
    
    def test_create_alias_existing(self, alias_manager, mock_storage):
        """Test creating alias that already exists."""
        # Mock storage returns existing alias
        mock_storage.get_aliases.return_value = {
            "existing": {"command": "test", "args": {}}
        }
        
        success = alias_manager.create_alias("existing", "export", {})
        assert success is False
    
    def test_get_alias_existing(self, alias_manager):
        """Test getting an existing alias."""
        alias = alias_manager.get_alias("export-json")
        
        assert alias is not None
        assert isinstance(alias, Alias)
        assert alias.name == "export-json"
        assert alias.command == "export"
        assert alias.args == {"format": "json", "verbose": True}
        assert alias.description == "Export in JSON format with verbose output"
    
    def test_get_alias_nonexistent(self, alias_manager):
        """Test getting a non-existent alias."""
        alias = alias_manager.get_alias("nonexistent")
        assert alias is None
    
    def test_list_aliases(self, alias_manager):
        """Test listing all aliases."""
        aliases = alias_manager.list_aliases()
        
        assert len(aliases) == 2
        assert all(isinstance(alias, Alias) for alias in aliases)
        
        names = [alias.name for alias in aliases]
        assert "export-json" in names
        assert "quick-scan" in names
    
    def test_create_workflow_valid(self, alias_manager, mock_storage):
        """Test creating a valid workflow."""
        commands = [
            {"command": "scan", "args": {"recursive": True}},
            {"command": "process", "args": {"backup": True}},
            {"command": "export", "args": {"format": "json"}}
        ]
        
        success = alias_manager.create_workflow("test-workflow", commands)
        
        assert success is True
        mock_storage.store_workflow.assert_called_once_with("test-workflow", commands)
    
    def test_create_workflow_invalid_commands(self, alias_manager):
        """Test creating workflow with invalid commands."""
        invalid_commands = [
            [],  # Empty list
            [{"invalid": "structure"}],  # Missing required fields
            [{"command": "test"}],  # Missing args field
            [{"args": {}}],  # Missing command field
        ]
        
        for commands in invalid_commands:
            success = alias_manager.create_workflow("test", commands)
            assert success is False
    
    def test_get_workflow_existing(self, alias_manager):
        """Test getting an existing workflow."""
        workflow = alias_manager.get_workflow("process-and-export")
        
        assert workflow is not None
        assert isinstance(workflow, Workflow)
        assert workflow.name == "process-and-export"
        assert len(workflow.commands) == 2
        assert workflow.commands[0]["command"] == "process"
        assert workflow.commands[1]["command"] == "export"
    
    def test_get_workflow_nonexistent(self, alias_manager):
        """Test getting a non-existent workflow."""
        workflow = alias_manager.get_workflow("nonexistent")
        assert workflow is None
    
    def test_list_workflows(self, alias_manager):
        """Test listing all workflows."""
        workflows = alias_manager.list_workflows()
        
        assert len(workflows) == 1
        assert all(isinstance(wf, Workflow) for wf in workflows)
        assert workflows[0].name == "process-and-export"
    
    def test_suggest_alias_name(self, alias_manager, mock_storage):
        """Test alias name suggestion."""
        # Mock empty aliases to avoid conflicts
        mock_storage.get_aliases.return_value = {}
        
        # Test with simple command and args
        suggested = alias_manager.suggest_alias_name(
            "export", 
            {"format": "json", "verbose": True}
        )
        
        assert suggested == "export-format-verbose"
    
    def test_suggest_alias_name_conflict(self, alias_manager, mock_storage):
        """Test alias name suggestion with conflicts."""
        # Mock existing alias
        mock_storage.get_aliases.return_value = {
            "export-format": {"command": "export", "args": {}}
        }
        
        suggested = alias_manager.suggest_alias_name(
            "export", 
            {"format": "json"}
        )
        
        # Should add counter to avoid conflict
        assert suggested == "export-format-1"
    
    def test_suggest_workflow_name(self, alias_manager, mock_storage):
        """Test workflow name suggestion."""
        # Mock empty workflows
        mock_storage.get_workflows.return_value = {}
        
        # Test with short command sequence
        suggested = alias_manager.suggest_workflow_name(["scan", "process", "export"])
        assert suggested == "scan-process-export"
        
        # Test with long sequence
        long_sequence = ["cmd1", "cmd2", "cmd3", "cmd4", "cmd5"]
        suggested = alias_manager.suggest_workflow_name(long_sequence)
        assert suggested == "cmd1-to-cmd5"
    
    def test_register_command(self, alias_manager):
        """Test registering a command for execution."""
        mock_command = Mock()
        
        alias_manager.register_command("test-cmd", mock_command)
        
        assert "test-cmd" in alias_manager._command_registry
        assert alias_manager._command_registry["test-cmd"] == mock_command
    
    def test_execute_alias(self, alias_manager):
        """Test executing an alias."""
        # Register a mock command
        mock_command = Mock()
        mock_command.return_value = "success"
        alias_manager.register_command("export", mock_command)
        
        # Execute alias
        result = alias_manager.execute_alias("export-json")
        
        # Should call the command with alias args
        mock_command.assert_called_once_with(format="json", verbose=True)
        assert result == "success"
    
    def test_execute_alias_nonexistent(self, alias_manager):
        """Test executing non-existent alias."""
        with pytest.raises(ValueError, match="Alias 'nonexistent' not found"):
            alias_manager.execute_alias("nonexistent")
    
    def test_execute_alias_unregistered_command(self, alias_manager):
        """Test executing alias for unregistered command."""
        with pytest.raises(ValueError, match="Command 'export' not registered"):
            alias_manager.execute_alias("export-json")
    
    def test_execute_workflow(self, alias_manager):
        """Test executing a workflow."""
        # Register mock commands
        mock_process = Mock(return_value="processed")
        mock_export = Mock(return_value="exported")
        
        alias_manager.register_command("process", mock_process)
        alias_manager.register_command("export", mock_export)
        
        # Execute workflow
        results = alias_manager.execute_workflow("process-and-export")
        
        # Should execute both commands in sequence
        mock_process.assert_called_once_with(backup=True)
        mock_export.assert_called_once_with(format="json")
        
        assert results == ["processed", "exported"]
    
    def test_execute_workflow_nonexistent(self, alias_manager):
        """Test executing non-existent workflow."""
        with pytest.raises(ValueError, match="Workflow 'nonexistent' not found"):
            alias_manager.execute_workflow("nonexistent")

    def test_get_alias_suggestions(self, alias_manager):
        """Test getting alias suggestion data."""
        suggestion = alias_manager.get_alias_suggestions(
            "export",
            {"format": "json", "verbose": True},
            5
        )
        
        assert suggestion["type"] == "alias"
        assert suggestion["command"] == "export"
        assert suggestion["args"] == {"format": "json", "verbose": True}
        assert suggestion["usage_count"] == 5
        assert "suggested_name" in suggestion
        assert "description" in suggestion
    
    def test_alias_to_dict(self):
        """Test converting alias to dictionary."""
        alias = Alias(
            name="test",
            command="export",
            args={"format": "json"},
            description="Test alias"
        )
        
        data = alias.to_dict()
        
        assert data == {
            "command": "export",
            "args": {"format": "json"},
            "description": "Test alias"
        }
    
    def test_workflow_to_dict(self):
        """Test converting workflow to dictionary."""
        workflow = Workflow(
            name="test",
            commands=[{"command": "export", "args": {}}],
            description="Test workflow"
        )
        
        data = workflow.to_dict()
        
        assert data == {
            "commands": [{"command": "export", "args": {}}],
            "description": "Test workflow"
        }
