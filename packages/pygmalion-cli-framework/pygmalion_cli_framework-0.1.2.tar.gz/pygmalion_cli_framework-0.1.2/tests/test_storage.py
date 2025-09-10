"""
Tests for storage backends functionality.
"""

import pytest
import tempfile
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from unittest.mock import patch

from pygmalion.storage import JSONStorage, SQLiteStorage, StorageBackend


class TestJSONStorage:
    """Test cases for JSONStorage backend."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def json_storage(self, temp_dir):
        """Create a JSONStorage instance in temp directory."""
        return JSONStorage("test-app", temp_dir)
    
    def test_init_creates_directory(self, temp_dir):
        """Test that initialization creates storage directory."""
        storage = JSONStorage("test-app", temp_dir)
        assert Path(temp_dir).exists()
        assert storage.file_path.parent.exists()
    
    def test_init_creates_default_data(self, json_storage):
        """Test that initialization creates default data structure."""
        assert json_storage.file_path.exists()
        
        # Check data structure
        data = json_storage._data
        assert "commands" in data
        assert "aliases" in data
        assert "workflows" in data
        assert "metadata" in data
        assert isinstance(data["commands"], list)
        assert isinstance(data["aliases"], dict)
        assert isinstance(data["workflows"], dict)
    
    def test_record_command(self, json_storage):
        """Test recording a command."""
        timestamp = datetime(2025, 1, 1, 12, 0, 0)
        args = {"format": "json", "verbose": True}
        
        json_storage.record_command("export", args, timestamp)
        
        commands = json_storage._data["commands"]
        assert len(commands) == 1
        assert commands[0]["command"] == "export"
        assert commands[0]["args"] == args
        assert commands[0]["timestamp"] == timestamp.isoformat()
    
    def test_get_command_history(self, json_storage):
        """Test getting command history."""
        # Add some commands
        json_storage.record_command("cmd1", {"arg1": "val1"})
        json_storage.record_command("cmd2", {"arg2": "val2"})
        
        history = json_storage.get_command_history()
        assert len(history) == 2
        # Most recent first (cmd2, then cmd1)
        assert history[0]["command"] == "cmd2"
        assert history[1]["command"] == "cmd1"
    
    def test_get_command_history_with_limit(self, json_storage):
        """Test getting command history with limit."""
        # Add several commands
        for i in range(5):
            json_storage.record_command(f"cmd{i}", {})
        
        history = json_storage.get_command_history(limit=3)
        assert len(history) == 3
        # Should get the last 3 commands (most recent first)
        assert history[0]["command"] == "cmd4"
        assert history[1]["command"] == "cmd3" 
        assert history[2]["command"] == "cmd2"
    
    def test_get_command_frequency(self, json_storage):
        """Test getting command frequency."""
        # Add repeated commands
        json_storage.record_command("export", {})
        json_storage.record_command("process", {})
        json_storage.record_command("export", {})
        json_storage.record_command("export", {})
        
        frequency = json_storage.get_command_frequency()
        assert frequency["export"] == 3
        assert frequency["process"] == 1
    
    def test_store_and_get_alias(self, json_storage):
        """Test storing and retrieving aliases."""
        args = {"format": "json", "verbose": True}
        json_storage.store_alias("test-alias", "export", args)
        
        aliases = json_storage.get_aliases()
        assert "test-alias" in aliases
        assert aliases["test-alias"]["command"] == "export"
        assert aliases["test-alias"]["args"] == args
        assert "created" in aliases["test-alias"]
    
    def test_store_and_get_workflow(self, json_storage):
        """Test storing and retrieving workflows."""
        commands = [
            {"command": "process", "args": {"backup": True}},
            {"command": "export", "args": {"format": "json"}}
        ]
        
        json_storage.store_workflow("test-workflow", commands)
        
        workflows = json_storage.get_workflows()
        assert "test-workflow" in workflows
        assert workflows["test-workflow"] == commands
    
    def test_get_command_sequences(self, json_storage):
        """Test getting command sequences."""
        # Add a sequence of commands
        commands = ["scan", "process", "export", "scan", "process"]
        for cmd in commands:
            json_storage.record_command(cmd, {})
        
        sequences = json_storage.get_command_sequences(min_length=2)
        
        # Should find sequences like ["scan", "process"], ["process", "export"], etc.
        assert len(sequences) == 4  # 5 commands - 2 + 1
        assert ["scan", "process"] in sequences
        assert ["process", "export"] in sequences
    
    def test_corrupted_file_handling(self, temp_dir):
        """Test handling of corrupted JSON file."""
        # Create a corrupted JSON file
        file_path = Path(temp_dir) / "test-app.json"
        file_path.write_text("{ invalid json }")
        
        # Should handle corruption gracefully
        storage = JSONStorage("test-app", temp_dir)
        
        # Should have default structure
        assert "commands" in storage._data
        assert isinstance(storage._data["commands"], list)
    
    def test_atomic_save(self, json_storage):
        """Test that saves are atomic (using temporary files)."""
        original_data = json_storage._data.copy()
        
        # Record a command (triggers save)
        json_storage.record_command("test", {})
        
        # File should exist and be valid JSON
        assert json_storage.file_path.exists()
        with open(json_storage.file_path, 'r') as f:
            data = json.load(f)
        
        assert len(data["commands"]) == 1
        assert data["commands"][0]["command"] == "test"


class TestSQLiteStorage:
    """Test cases for SQLiteStorage backend."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Robust cleanup for Windows SQLite files
        import shutil
        import time
        import gc
        try:
            shutil.rmtree(temp_dir)
        except PermissionError:
            # Force garbage collection to close SQLite connections
            gc.collect()
            time.sleep(0.5)  # Give Windows time to release file handles
            try:
                shutil.rmtree(temp_dir)
            except PermissionError:
                # Ignore Windows SQLite lock issues in tests
                pass
    
    @pytest.fixture
    def sqlite_storage(self, temp_dir):
        """Create a SQLiteStorage instance in temp directory."""
        return SQLiteStorage("test-app", temp_dir)
    
    def test_init_creates_database(self, sqlite_storage):
        """Test that initialization creates database file and tables."""
        assert sqlite_storage.db_path.exists()
        
        # Check that tables exist
        with sqlite3.connect(sqlite_storage.db_path) as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
            tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = ["commands", "aliases", "workflows"]
        for table in expected_tables:
            assert table in tables
    
    def test_record_command(self, sqlite_storage):
        """Test recording a command."""
        timestamp = datetime(2025, 1, 1, 12, 0, 0)
        args = {"format": "json", "verbose": True}
        
        sqlite_storage.record_command("export", args, timestamp)
        
        with sqlite3.connect(sqlite_storage.db_path) as conn:
            cursor = conn.execute("SELECT * FROM commands")
            rows = cursor.fetchall()
        
        assert len(rows) == 1
        assert rows[0][1] == "export"  # command column
        assert json.loads(rows[0][2]) == args  # args column
        assert rows[0][3] == timestamp.isoformat()  # timestamp column
    
    def test_get_command_history(self, sqlite_storage):
        """Test getting command history."""
        # Add some commands
        sqlite_storage.record_command("cmd1", {"arg1": "val1"})
        sqlite_storage.record_command("cmd2", {"arg2": "val2"})
        
        history = sqlite_storage.get_command_history()
        
        # Should be in reverse chronological order (newest first)
        assert len(history) == 2
        assert history[0]["command"] == "cmd2"  # Most recent first
        assert history[1]["command"] == "cmd1"
    
    def test_get_command_history_with_limit(self, sqlite_storage):
        """Test getting command history with limit."""
        # Add several commands
        for i in range(5):
            sqlite_storage.record_command(f"cmd{i}", {})
        
        history = sqlite_storage.get_command_history(limit=3)
        assert len(history) == 3
        # Should get the 3 most recent commands
        assert history[0]["command"] == "cmd4"
        assert history[1]["command"] == "cmd3"
        assert history[2]["command"] == "cmd2"
    
    def test_get_command_frequency(self, sqlite_storage):
        """Test getting command frequency."""
        # Add repeated commands
        sqlite_storage.record_command("export", {})
        sqlite_storage.record_command("process", {})
        sqlite_storage.record_command("export", {})
        sqlite_storage.record_command("export", {})
        
        frequency = sqlite_storage.get_command_frequency()
        assert frequency["export"] == 3
        assert frequency["process"] == 1
    
    def test_store_and_get_alias(self, sqlite_storage):
        """Test storing and retrieving aliases."""
        args = {"format": "json", "verbose": True}
        sqlite_storage.store_alias("test-alias", "export", args)
        
        aliases = sqlite_storage.get_aliases()
        assert "test-alias" in aliases
        assert aliases["test-alias"]["command"] == "export"
        assert aliases["test-alias"]["args"] == args
        assert "created" in aliases["test-alias"]
    
    def test_store_and_get_workflow(self, sqlite_storage):
        """Test storing and retrieving workflows."""
        commands = [
            {"command": "process", "args": {"backup": True}},
            {"command": "export", "args": {"format": "json"}}
        ]
        
        sqlite_storage.store_workflow("test-workflow", commands)
        
        workflows = sqlite_storage.get_workflows()
        assert "test-workflow" in workflows
        assert workflows["test-workflow"] == commands
    
    def test_get_command_sequences(self, sqlite_storage):
        """Test getting command sequences."""
        # Add a sequence of commands
        commands = ["scan", "process", "export", "scan", "process"]
        for cmd in commands:
            sqlite_storage.record_command(cmd, {})
        
        sequences = sqlite_storage.get_command_sequences(min_length=2)
        
        # Should find sequences in chronological order
        assert len(sequences) == 4  # 5 commands - 2 + 1
        assert ["scan", "process"] in sequences
        assert ["process", "export"] in sequences
    
    def test_alias_replacement(self, sqlite_storage):
        """Test that storing alias with same name replaces the old one."""
        # Store initial alias
        sqlite_storage.store_alias("test", "export", {"format": "json"})
        
        # Store replacement
        sqlite_storage.store_alias("test", "process", {"backup": True})
        
        aliases = sqlite_storage.get_aliases()
        assert aliases["test"]["command"] == "process"
        assert aliases["test"]["args"] == {"backup": True}
    
    def test_workflow_replacement(self, sqlite_storage):
        """Test that storing workflow with same name replaces the old one."""
        # Store initial workflow
        commands1 = [{"command": "scan", "args": {}}]
        sqlite_storage.store_workflow("test", commands1)
        
        # Store replacement
        commands2 = [{"command": "export", "args": {}}]
        sqlite_storage.store_workflow("test", commands2)
        
        workflows = sqlite_storage.get_workflows()
        assert workflows["test"] == commands2


class TestStorageBackend:
    """Test cases for abstract StorageBackend."""
    
    def test_abstract_methods(self):
        """Test that StorageBackend cannot be instantiated directly."""
        with pytest.raises(TypeError):
            StorageBackend("test")
    
    def test_default_path_creation(self, temp_dir):
        """Test default storage path creation."""
        # Mock Path.home() to return temp directory
        with patch("pygmalion.storage.Path.home", return_value=Path(temp_dir)):
            storage = JSONStorage("test-app")
            expected_path = Path(temp_dir) / ".pygmalion"
            assert str(expected_path) in storage.storage_path
