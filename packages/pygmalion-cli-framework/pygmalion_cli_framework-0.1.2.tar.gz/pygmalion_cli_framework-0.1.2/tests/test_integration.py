"""
Integration tests for the complete Pygmalion system.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import click
from click.testing import CliRunner

import pygmalion
from pygmalion import PygmalionApp


class TestPygmalionIntegration:
    """Integration tests for the complete Pygmalion system."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Cleanup with error handling for Windows SQLite locks
        try:
            shutil.rmtree(temp_dir)
        except PermissionError:
            import time
            import gc
            gc.collect()
            time.sleep(0.2)
            try:
                shutil.rmtree(temp_dir)
            except PermissionError:
                pass  # Ignore Windows SQLite lock issues in tests
    
    @pytest.fixture
    def app(self, temp_dir):
        """Create a test Pygmalion app."""
        return PygmalionApp(
            name="test-app",
            storage_backend="json",
            storage_path=temp_dir,
            suggestion_threshold=2,  # Lower threshold for testing
            workflow_threshold=2
        )
    
    def test_basic_command_tracking(self, app):
        """Test basic command tracking functionality."""
        # Register and execute a command multiple times
        @pygmalion.command()
        @click.option('--format', default='json')
        @click.option('--verbose', is_flag=True)
        def export(format, verbose):
            return f"Exported in {format}, verbose={verbose}"
        
        app.register_command("export", export)
        
        # Execute command multiple times
        app.tracker.record_command("export", {"format": "json", "verbose": True})
        app.tracker.record_command("export", {"format": "json", "verbose": True})
        app.tracker.record_command("export", {"format": "csv", "verbose": False})
        
        # Check frequency tracking
        frequency = app.tracker.get_command_frequency()
        assert frequency["export"] == 3
        
        # Check pattern detection
        patterns = app.tracker.get_command_patterns()
        assert "export" in patterns
        assert len(patterns["export"]) == 3
    
    def test_alias_creation_and_execution(self, app):
        """Test alias creation and execution."""
        # Create a test command
        def mock_export(**kwargs):
            return f"Mock export with {kwargs}"
        
        app.register_command("export", mock_export)
        
        # Create an alias
        success = app.create_alias(
            "export-json",
            "export", 
            {"format": "json", "verbose": True},
            "Quick JSON export"
        )
        
        assert success is True
        
        # Verify alias exists
        alias = app.alias_manager.get_alias("export-json")
        assert alias is not None
        assert alias.command == "export"
        assert alias.args == {"format": "json", "verbose": True}
        
        # Test alias execution
        result = app.alias_manager.execute_alias("export-json")
        assert "format" in str(result)
        assert "verbose" in str(result)
    
    def test_workflow_creation_and_execution(self, app):
        """Test workflow creation and execution."""
        # Create test commands
        def mock_process(**kwargs):
            return f"Processed with {kwargs}"
        
        def mock_export(**kwargs):
            return f"Exported with {kwargs}"
        
        app.register_command("process", mock_process)
        app.register_command("export", mock_export)
        
        # Create workflow
        commands = [
            {"command": "process", "args": {"backup": True}},
            {"command": "export", "args": {"format": "json"}}
        ]
        
        success = app.create_workflow("process-export", commands)
        assert success is True
        
        # Verify workflow exists
        workflow = app.alias_manager.get_workflow("process-export")
        assert workflow is not None
        assert len(workflow.commands) == 2
        
        # Test workflow execution
        results = app.alias_manager.execute_workflow("process-export")
        assert len(results) == 2
        assert "backup" in str(results[0])
        assert "format" in str(results[1])
    
    def test_suggestion_system(self, app):
        """Test the suggestion system."""
        # Record repetitive command patterns
        for _ in range(3):
            app.tracker.record_command("export", {"format": "json", "verbose": True})
        
        # Get suggestions
        suggestions = app.tracker.suggest_optimizations()
        
        # Should suggest alias creation
        alias_suggestions = [s for s in suggestions if s["type"] == "alias"]
        assert len(alias_suggestions) > 0
        
        suggestion = alias_suggestions[0]
        assert suggestion["data"]["command"] == "export"
        assert suggestion["data"]["count"] >= 3
    
    def test_analytics_generation(self, app):
        """Test analytics generation."""
        # Add some test data
        commands = ["export", "process", "export", "scan", "export"]
        for cmd in commands:
            app.tracker.record_command(cmd, {})
        
        # Test various analytics methods
        frequency = app.tracker.get_command_frequency()
        assert frequency["export"] == 3
        assert frequency["process"] == 1
        assert frequency["scan"] == 1
        
        most_used = app.tracker.get_most_used_commands(2)
        assert len(most_used) == 2
        assert most_used[0] == ("export", 3)
        assert most_used[1][1] == 1  # Second most used has count 1
        
        session_stats = app.tracker.get_session_stats()
        assert session_stats["total_commands"] >= 5
        assert session_stats["unique_commands"] == 3
    
    def test_data_persistence_json(self, temp_dir):
        """Test data persistence with JSON storage."""
        # Create app and add data
        app1 = PygmalionApp(
            name="persist-test",
            storage_backend="json", 
            storage_path=temp_dir
        )
        
        app1.tracker.record_command("test", {"arg": "value"})
        app1.create_alias("test-alias", "test", {"arg": "value"})
        
        # Create new app instance (simulating restart)
        app2 = PygmalionApp(
            name="persist-test",
            storage_backend="json",
            storage_path=temp_dir
        )
        
        # Verify data persisted
        frequency = app2.tracker.get_command_frequency()
        assert frequency.get("test", 0) == 1
        
        aliases = app2.alias_manager.list_aliases()
        alias_names = [a.name for a in aliases]
        assert "test-alias" in alias_names
    
    def test_data_persistence_sqlite(self, temp_dir):
        """Test data persistence with SQLite storage."""
        # Create app and add data
        app1 = PygmalionApp(
            name="persist-test",
            storage_backend="sqlite",
            storage_path=temp_dir
        )
        
        app1.tracker.record_command("test", {"arg": "value"})
        app1.create_alias("test-alias", "test", {"arg": "value"})
        
        # Create new app instance (simulating restart)
        app2 = PygmalionApp(
            name="persist-test", 
            storage_backend="sqlite",
            storage_path=temp_dir
        )
        
        # Verify data persisted
        frequency = app2.tracker.get_command_frequency()
        assert frequency.get("test", 0) == 1
        
        aliases = app2.alias_manager.list_aliases()
        alias_names = [a.name for a in aliases]
        assert "test-alias" in alias_names
        
        # Cleanup SQLite connections
        if hasattr(app1.tracker.storage, 'close'):
            app1.tracker.storage.close()
        if hasattr(app2.tracker.storage, 'close'):
            app2.tracker.storage.close()
    
    def test_export_import_functionality(self, app, temp_dir):
        """Test data export functionality."""
        # Add test data
        app.tracker.record_command("export", {"format": "json"})
        app.create_alias("quick-export", "export", {"format": "json"})
        
        # Test JSON export
        export_path = Path(temp_dir) / "export.json"
        success = app.export_data(str(export_path), "json")
        assert success is True
        assert export_path.exists()
        
        # Verify export content
        import json
        with open(export_path) as f:
            data = json.load(f)
        
        assert "app_name" in data
        assert "commands" in data
        assert "aliases" in data
        assert len(data["commands"]) >= 1
        assert "quick-export" in data["aliases"]
    
    def test_config_management(self, app):
        """Test configuration management."""
        # Get initial config
        config = app.get_config()
        assert "name" in config
        assert "suggestion_threshold" in config
        
        # Update config
        original_threshold = config["suggestion_threshold"]
        app.update_config(suggestion_threshold=5)
        
        # Verify update
        new_config = app.get_config()
        assert new_config["suggestion_threshold"] == 5
        assert new_config["suggestion_threshold"] != original_threshold
    
    def test_cli_integration(self, app):
        """Test CLI integration with Click."""
        runner = CliRunner()
        
        # Create a simple CLI app
        @click.group()
        def cli():
            pass
        
        @pygmalion.command()
        @click.option('--format', default='json')
        def export(format):
            click.echo(f"Export format: {format}")
        
        cli.add_command(export)
        
        # Set up Pygmalion integration
        pygmalion.set_default_app(app)
        
        # Test command execution
        result = runner.invoke(cli, ['export', '--format', 'csv'])
        assert result.exit_code == 0
        assert "csv" in result.output
    
    def test_error_handling(self, app):
        """Test error handling in various scenarios."""
        # Test invalid alias creation
        assert app.create_alias("", "command", {}) is False
        assert app.create_alias("invalid name", "command", {}) is False
        
        # Test invalid workflow creation
        assert app.create_workflow("test", []) is False
        assert app.create_workflow("test", [{"invalid": "structure"}]) is False
        
        # Test non-existent alias/workflow operations
        with pytest.raises(ValueError):
            app.alias_manager.execute_alias("nonexistent")
        
        with pytest.raises(ValueError):
            app.alias_manager.execute_workflow("nonexistent")
    
    def test_adaptive_help_integration(self, app):
        """Test adaptive help system integration."""
        # Add usage data
        app.tracker.record_command("export", {"format": "json", "verbose": True})
        app.tracker.record_command("export", {"format": "json", "verbose": True})
        app.tracker.record_command("process", {"backup": True})
        
        # Create some aliases
        app.create_alias("export-json", "export", {"format": "json", "verbose": True})
        
        # Test help generation
        help_system = app.help
        
        # Test main help enhancement
        ctx = click.Context(click.Command("test"))
        original_help = "Original help text"
        enhanced_help = help_system.generate_main_help(ctx, original_help)
        
        assert "Original help text" in enhanced_help
        assert len(enhanced_help) > len(original_help)  # Should be enhanced
        
        # Test recent activity summary
        activity = help_system.get_recent_activity_summary(7)
        assert activity["total_commands"] >= 3
        assert activity["unique_commands"] >= 2
