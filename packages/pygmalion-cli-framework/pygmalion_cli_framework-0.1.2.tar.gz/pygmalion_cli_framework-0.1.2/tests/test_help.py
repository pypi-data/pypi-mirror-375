"""
Tests for adaptive help system functionality.
"""

import pytest
from unittest.mock import Mock, MagicMock
import click

from pygmalion.tracker import CommandTracker
from pygmalion.alias import AliasManager, Alias, Workflow
from pygmalion.help import AdaptiveHelp


class TestAdaptiveHelp:
    """Test cases for AdaptiveHelp class."""
    
    @pytest.fixture
    def mock_tracker(self):
        """Create a mock command tracker."""
        tracker = Mock(spec=CommandTracker)
        tracker.get_command_frequency.return_value = {
            "export": 15,
            "process": 12,
            "config": 8,
            "scan": 5
        }
        tracker.get_most_used_commands.return_value = [
            ("export", 15),
            ("process", 12),
            ("config", 8)
        ]
        tracker.get_command_patterns.return_value = {
            "export": [
                {
                    "pattern": "--format=str --verbose",
                    "args": {"format": "json", "verbose": True},
                    "timestamp": "2025-01-01T10:00:00"
                },
                {
                    "pattern": "--format=str --verbose",
                    "args": {"format": "json", "verbose": True},
                    "timestamp": "2025-01-01T11:00:00"
                },
                {
                    "pattern": "--format=str",
                    "args": {"format": "csv"},
                    "timestamp": "2025-01-01T12:00:00"
                }
            ]
        }
        tracker.get_repetitive_patterns.return_value = [
            {
                "command": "export",
                "pattern": "--format=str --verbose",
                "count": 8,
                "example_args": {"format": "json", "verbose": True},
                "suggestion_score": 0.8
            }
        ]
        tracker.suggest_optimizations.return_value = [
            {
                "type": "alias",
                "priority": "high",
                "message": "Create alias for 'export --format json --verbose'?",
                "data": {"command": "export", "count": 8}
            },
            {
                "type": "workflow", 
                "priority": "medium",
                "message": "Create workflow for 'process → export'?",
                "data": {"sequence": ["process", "export"]}
            },
            {
                "type": "discovery",
                "priority": "low", 
                "message": "Try 'export --compress' - you haven't used this option yet!",
                "data": {"command": "export", "option": "--compress"}
            }
        ]
        tracker.get_unused_options.return_value = ["--compress", "--parallel"]
        return tracker
    
    @pytest.fixture
    def mock_alias_manager(self):
        """Create a mock alias manager."""
        manager = Mock(spec=AliasManager)
        manager.list_aliases.return_value = [
            Alias("export-json", "export", {"format": "json", "verbose": True}, "Quick JSON export"),
            Alias("quick-scan", "scan", {"recursive": True}, "Recursive scan")
        ]
        manager.list_workflows.return_value = [
            Workflow("process-export", [
                {"command": "process", "args": {"backup": True}},
                {"command": "export", "args": {"format": "json"}}
            ], "Process and export workflow")
        ]
        manager.suggest_alias_name.return_value = "export-json-verbose"
        manager.suggest_workflow_name.return_value = "process-and-export"
        manager.create_alias.return_value = True
        manager.create_workflow.return_value = True
        return manager
    
    @pytest.fixture
    def adaptive_help(self, mock_tracker, mock_alias_manager):
        """Create an AdaptiveHelp instance."""
        return AdaptiveHelp(mock_tracker, mock_alias_manager)
    
    def test_generate_main_help(self, adaptive_help):
        """Test generating enhanced main help."""
        ctx = Mock(spec=click.Context)
        original_help = "Original help text"
        
        enhanced_help = adaptive_help.generate_main_help(ctx, original_help)
        
        assert "Original help text" in enhanced_help
        assert "Your Most Used Commands:" in enhanced_help
        assert "export" in enhanced_help
        assert "Available Shortcuts:" in enhanced_help
        assert "Suggestions:" in enhanced_help
    
    def test_generate_usage_section(self, adaptive_help, mock_tracker):
        """Test generating usage analytics section."""
        section = adaptive_help._generate_usage_section()
        
        assert section is not None
        assert "Your Most Used Commands:" in section
        assert "export" in section
        assert "15 times" in section or "times" in section
    
    def test_generate_usage_section_empty(self, mock_tracker, mock_alias_manager):
        """Test usage section with no data."""
        mock_tracker.get_command_frequency.return_value = {}
        mock_tracker.get_most_used_commands.return_value = []
        
        adaptive_help = AdaptiveHelp(mock_tracker, mock_alias_manager)
        section = adaptive_help._generate_usage_section()
        
        assert section is None
    
    def test_generate_aliases_section(self, adaptive_help):
        """Test generating aliases section."""
        section = adaptive_help._generate_aliases_section()
        
        assert section is not None
        assert "Available Shortcuts:" in section
        assert "export-json" in section
        assert "quick-scan" in section
    
    def test_generate_aliases_section_empty(self, mock_tracker, mock_alias_manager):
        """Test aliases section with no aliases."""
        mock_alias_manager.list_aliases.return_value = []
        
        adaptive_help = AdaptiveHelp(mock_tracker, mock_alias_manager)
        section = adaptive_help._generate_aliases_section()
        
        assert section is None
    
    def test_generate_suggestions_section(self, adaptive_help):
        """Test generating suggestions section."""
        section = adaptive_help._generate_suggestions_section()
        
        assert section is not None
        assert "Suggestions:" in section
        assert "Create alias" in section or "Create workflow" in section
    
    def test_generate_suggestions_section_empty(self, mock_tracker, mock_alias_manager):
        """Test suggestions section with no suggestions."""
        mock_tracker.suggest_optimizations.return_value = []
        
        adaptive_help = AdaptiveHelp(mock_tracker, mock_alias_manager)
        section = adaptive_help._generate_suggestions_section()
        
        assert section is None
    
    def test_format_args_for_display(self, adaptive_help):
        """Test formatting arguments for display."""
        # Test with mixed argument types
        args = {"format": "json", "verbose": True, "count": 5}
        formatted = adaptive_help._format_args_for_display(args)
        
        assert "--format=json" in formatted
        assert "--verbose" in formatted
        assert "--count=5" in formatted
    
    def test_format_args_for_display_empty(self, adaptive_help):
        """Test formatting empty arguments."""
        formatted = adaptive_help._format_args_for_display({})
        assert formatted == ""
    
    def test_generate_command_help(self, adaptive_help):
        """Test generating enhanced help for specific command."""
        ctx = Mock(spec=click.Context)
        original_help = "Original command help"
        
        enhanced_help = adaptive_help.generate_command_help(ctx, "export", original_help)
        
        assert "Original command help" in enhanced_help
        # Should include command-specific patterns and suggestions
        assert enhanced_help != original_help  # Should be enhanced
    
    def test_generate_command_patterns_section(self, adaptive_help):
        """Test generating command patterns section."""
        section = adaptive_help._generate_command_patterns_section("export")
        
        assert section is not None
        assert "How you usually use 'export':" in section
        assert "--format=str --verbose" in section or "format" in section
    
    def test_generate_command_patterns_section_no_data(self, adaptive_help, mock_tracker):
        """Test command patterns section with no data."""
        mock_tracker.get_command_patterns.return_value = {}
        
        section = adaptive_help._generate_command_patterns_section("nonexistent")
        assert section is None
    
    def test_generate_command_suggestions_section(self, adaptive_help):
        """Test generating command-specific suggestions."""
        section = adaptive_help._generate_command_suggestions_section("export")
        
        assert section is not None
        assert "Tips:" in section
    
    def test_get_smart_completions(self, adaptive_help):
        """Test smart completion suggestions."""
        ctx = Mock(spec=click.Context)
        param = Mock(spec=click.Parameter)
        
        completions = adaptive_help.get_smart_completions(ctx, param, "ex")
        
        # Should return some completions (specific implementation depends on mock setup)
        assert isinstance(completions, list)
    
    def test_get_recent_activity_summary(self, adaptive_help, mock_tracker):
        """Test getting recent activity summary."""
        # Mock recent command history
        mock_tracker.storage = Mock()
        mock_tracker.storage.get_command_history.return_value = [
            {
                "command": "export",
                "timestamp": "2025-01-08T10:00:00"  # Recent date
            },
            {
                "command": "process", 
                "timestamp": "2025-01-08T11:00:00"
            }
        ]
        
        summary = adaptive_help.get_recent_activity_summary(7)
        
        assert "total_commands" in summary
        assert "unique_commands" in summary
        assert "days" in summary
        assert summary["days"] == 7
    
    def test_get_recent_activity_summary_no_data(self, adaptive_help, mock_tracker):
        """Test activity summary with no recent data."""
        mock_tracker.storage = Mock()
        mock_tracker.storage.get_command_history.return_value = []
        
        summary = adaptive_help.get_recent_activity_summary(7)
        
        assert summary["total_commands"] == 0
        assert summary["days"] == 7
    
    def test_get_suggestion_icon(self, adaptive_help):
        """Test getting icons for suggestion types."""
        assert adaptive_help._get_suggestion_icon("alias") == "🔗"
        assert adaptive_help._get_suggestion_icon("workflow") == "🔄"
        assert adaptive_help._get_suggestion_icon("discovery") == "🌟"
        assert adaptive_help._get_suggestion_icon("unknown") == "💡"
    
    @pytest.mark.parametrize("suggestion_type,expected_icon", [
        ("alias", "🔗"),
        ("workflow", "🔄"),
        ("discovery", "🌟"),
        ("unknown", "💡")
    ])
    def test_suggestion_icons(self, adaptive_help, suggestion_type, expected_icon):
        """Test suggestion icon mapping."""
        icon = adaptive_help._get_suggestion_icon(suggestion_type)
        assert icon == expected_icon
    
    def test_show_interactive_suggestions_no_suggestions(self, adaptive_help, mock_tracker):
        """Test interactive suggestions with no suggestions available."""
        mock_tracker.suggest_optimizations.return_value = []
        
        # This would normally print to console - we're testing it doesn't crash
        try:
            adaptive_help.show_interactive_suggestions()
        except Exception as e:
            pytest.fail(f"show_interactive_suggestions raised {e} unexpectedly")
    
    def test_get_peak_day(self, adaptive_help):
        """Test finding peak usage day."""
        from datetime import datetime
        
        commands = [
            {"timestamp": "2025-01-01T10:00:00"},
            {"timestamp": "2025-01-01T11:00:00"},
            {"timestamp": "2025-01-02T10:00:00"},
            {"timestamp": "2025-01-01T12:00:00"}  # 2025-01-01 has 3 commands
        ]
        
        peak_day, peak_count = adaptive_help._get_peak_day(commands)
        
        assert peak_count == 3
        assert "2025-01-01" in peak_day
    
    def test_get_peak_day_empty(self, adaptive_help):
        """Test peak day with empty command list."""
        peak_day, peak_count = adaptive_help._get_peak_day([])
        
        assert peak_day == "None"
        assert peak_count == 0
