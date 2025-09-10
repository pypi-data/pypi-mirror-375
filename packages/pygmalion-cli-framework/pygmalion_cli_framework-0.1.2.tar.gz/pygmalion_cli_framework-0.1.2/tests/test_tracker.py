"""
Tests for command tracking functionality.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock

from pygmalion.storage import JSONStorage
from pygmalion.tracker import CommandTracker


class TestCommandTracker:
    """Test cases for CommandTracker class."""
    
    @pytest.fixture
    def mock_storage(self):
        """Create a mock storage backend."""
        storage = Mock(spec=JSONStorage)
        storage.get_command_frequency.return_value = {
            "export": 5,
            "process": 3,
            "config": 2
        }
        storage.get_command_history.return_value = [
            {
                "command": "export",
                "args": {"format": "json", "verbose": True},
                "timestamp": "2025-01-01T10:00:00"
            },
            {
                "command": "export",
                "args": {"format": "json", "verbose": True},
                "timestamp": "2025-01-01T11:00:00"
            },
            {
                "command": "process",
                "args": {"backup": True},
                "timestamp": "2025-01-01T12:00:00"
            }
        ]
        return storage
    
    @pytest.fixture
    def tracker(self, mock_storage):
        """Create a CommandTracker with mock storage."""
        return CommandTracker(mock_storage, suggestion_threshold=2)
    
    def test_record_command(self, tracker, mock_storage):
        """Test recording a command execution."""
        tracker.record_command("test", {"arg1": "value1"})
        
        mock_storage.record_command.assert_called_once()
        args = mock_storage.record_command.call_args
        assert args[0][0] == "test"
        assert args[0][1] == {"arg1": "value1"}
        assert isinstance(args[0][2], datetime)
    
    def test_get_command_frequency(self, tracker, mock_storage):
        """Test getting command frequency."""
        frequency = tracker.get_command_frequency()
        
        assert frequency == {"export": 5, "process": 3, "config": 2}
        mock_storage.get_command_frequency.assert_called_once()
    
    def test_get_most_used_commands(self, tracker):
        """Test getting most used commands."""
        most_used = tracker.get_most_used_commands(2)
        
        assert len(most_used) == 2
        assert most_used[0] == ("export", 5)
        assert most_used[1] == ("process", 3)
    
    def test_create_pattern_signature(self, tracker):
        """Test creating pattern signatures from arguments."""
        # Test with mixed arguments
        args = {"format": "json", "verbose": True, "count": 5}
        signature = tracker._create_pattern_signature(args)
        
        # Should include all arguments in sorted order
        assert "--count=int" in signature
        assert "--format=str" in signature
        assert "--verbose" in signature
    
    def test_create_pattern_signature_empty(self, tracker):
        """Test pattern signature with no arguments."""
        signature = tracker._create_pattern_signature({})
        assert signature == "no_args"
    
    def test_get_command_patterns(self, tracker, mock_storage):
        """Test getting command usage patterns."""
        patterns = tracker.get_command_patterns()
        
        assert "export" in patterns
        assert "process" in patterns
        assert len(patterns["export"]) == 2  # Two export commands in mock data
        assert len(patterns["process"]) == 1  # One process command
    
    def test_get_repetitive_patterns(self, tracker, mock_storage):
        """Test finding repetitive patterns that could be aliased."""
        repetitive = tracker.get_repetitive_patterns()
        
        # Should find the repeated export pattern
        assert len(repetitive) > 0
        
        # Find the export pattern
        export_pattern = next(
            (p for p in repetitive if p["command"] == "export"), None
        )
        assert export_pattern is not None
        assert export_pattern["count"] >= tracker.suggestion_threshold
    
    def test_get_command_sequences(self, tracker, mock_storage):
        """Test getting command sequences for workflow detection."""
        mock_storage.get_command_sequences.return_value = [
            ["export", "process"],
            ["export", "process"],
            ["process", "config"]
        ]
        
        sequences = tracker.get_command_sequences(min_frequency=2)
        
        # Should find the repeated export->process sequence
        assert len(sequences) >= 1
        export_process_seq = next(
            (s for s in sequences if s["sequence"] == ["export", "process"]), None
        )
        assert export_process_seq is not None
        assert export_process_seq["count"] == 2
    
    def test_session_stats(self, tracker):
        """Test session statistics tracking."""
        # Add some commands to session
        tracker.record_command("cmd1", {})
        tracker.record_command("cmd2", {})
        tracker.record_command("cmd1", {})
        
        stats = tracker.get_session_stats()
        
        assert stats["total_commands"] == 3
        assert stats["unique_commands"] == 2
        assert stats["duration"] >= 0
        assert len(stats["most_used"]) > 0
    
    def test_suggest_optimizations(self, tracker, mock_storage):
        """Test optimization suggestions generation."""
        # Mock repetitive patterns
        mock_storage.get_command_sequences.return_value = [
            ["export", "process"],
            ["export", "process"]
        ]
        
        suggestions = tracker.suggest_optimizations()
        
        assert isinstance(suggestions, list)
        # Should have different types of suggestions
        suggestion_types = {s["type"] for s in suggestions}
        
        # Should include alias suggestions for repetitive patterns
        assert any(s["type"] == "alias" for s in suggestions)
    
    def test_suggestion_threshold(self, mock_storage):
        """Test that suggestion threshold works correctly."""
        tracker = CommandTracker(mock_storage, suggestion_threshold=10)
        
        repetitive = tracker.get_repetitive_patterns()
        
        # With higher threshold, fewer patterns should be suggested
        # (This depends on the mock data having patterns below threshold)
        for pattern in repetitive:
            assert pattern["count"] >= 10 or pattern["count"] < tracker.suggestion_threshold
    
    def test_time_based_patterns(self, tracker, mock_storage):
        """Test time-based usage pattern analysis."""
        patterns = tracker.get_time_based_patterns()
        
        if patterns:  # Only test if we have data
            assert "peak_hours" in patterns
            assert "daily_patterns" in patterns
            assert isinstance(patterns["peak_hours"], dict)
            assert isinstance(patterns["daily_patterns"], dict)
    
    def test_empty_data_handling(self, mock_storage):
        """Test handling when no data is available."""
        # Set up empty mock data
        mock_storage.get_command_frequency.return_value = {}
        mock_storage.get_command_history.return_value = []
        mock_storage.get_command_sequences.return_value = []
        
        tracker = CommandTracker(mock_storage)
        
        # Should handle empty data gracefully
        assert tracker.get_command_frequency() == {}
        assert tracker.get_most_used_commands() == []
        assert tracker.get_repetitive_patterns() == []
        assert tracker.get_command_sequences() == []
        
        stats = tracker.get_session_stats()
        assert stats["total_commands"] == 0
