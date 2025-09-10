"""
Storage backends for Pygmalion command tracking and analytics.

Provides JSON and SQLite storage options for command history, 
aliases, and usage analytics.
"""

import json
import sqlite3
import os
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import tempfile


class StorageBackend(ABC):
    """Abstract base class for storage backends."""
    
    def __init__(self, app_name: str, storage_path: Optional[str] = None):
        """
        Initialize storage backend.
        
        Args:
            app_name: Name of the application
            storage_path: Custom storage path (optional)
        """
        self.app_name = app_name
        self.storage_path = storage_path or self._get_default_path()
        self._ensure_storage_dir()
    
    def _get_default_path(self) -> str:
        """Get default storage path in user's home directory."""
        home = Path.home()
        return str(home / ".pygmalion")
    
    def _ensure_storage_dir(self) -> None:
        """Ensure storage directory exists."""
        Path(self.storage_path).mkdir(parents=True, exist_ok=True)
    
    @abstractmethod
    def record_command(self, command: str, args: Dict[str, Any], 
                      timestamp: Optional[datetime] = None) -> None:
        """Record a command execution."""
        pass
    
    @abstractmethod
    def get_command_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get command execution history."""
        pass
    
    @abstractmethod
    def get_command_frequency(self) -> Dict[str, int]:
        """Get frequency count for each command."""
        pass
    
    @abstractmethod
    def store_alias(self, alias: str, command: str, args: Dict[str, Any]) -> None:
        """Store a command alias."""
        pass
    
    @abstractmethod
    def get_aliases(self) -> Dict[str, Dict[str, Any]]:
        """Get all stored aliases."""
        pass
    
    @abstractmethod
    def get_command_sequences(self, min_length: int = 2) -> List[List[str]]:
        """Get sequences of commands for workflow detection."""
        pass
    
    @abstractmethod
    def store_workflow(self, name: str, commands: List[Dict[str, Any]]) -> None:
        """Store a command workflow."""
        pass
    
    @abstractmethod
    def get_workflows(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all stored workflows."""
        pass


class JSONStorage(StorageBackend):
    """JSON file-based storage backend."""
    
    def __init__(self, app_name: str, storage_path: Optional[str] = None):
        super().__init__(app_name, storage_path)
        self.file_path = Path(self.storage_path) / f"{app_name}.json"
        self._data = self._load_data()
        # Ensure file is created on initialization
        if not self.file_path.exists():
            self._save_data()
    
    def _load_data(self) -> Dict[str, Any]:
        """Load data from JSON file."""
        if not self.file_path.exists():
            return {
                "commands": [],
                "aliases": {},
                "workflows": {},
                "metadata": {
                    "created": datetime.now().isoformat(),
                    "version": "0.1.0"
                }
            }
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            # Return default structure if file is corrupted
            return {
                "commands": [],
                "aliases": {},
                "workflows": {},
                "metadata": {
                    "created": datetime.now().isoformat(),
                    "version": "0.1.0"
                }
            }
    
    def _save_data(self) -> None:
        """Save data to JSON file."""
        try:
            # Use temporary file for atomic writes
            temp_file = tempfile.NamedTemporaryFile(
                mode='w', 
                delete=False, 
                dir=self.storage_path,
                suffix='.tmp',
                encoding='utf-8'
            )
            
            json.dump(self._data, temp_file, indent=2, default=str)
            temp_file.close()
            
            # Atomic move
            if os.name == 'nt':  # Windows
                if self.file_path.exists():
                    self.file_path.unlink()
                Path(temp_file.name).replace(self.file_path)
            else:  # Unix-like
                Path(temp_file.name).replace(self.file_path)
                
        except Exception as e:
            # Clean up temp file if it exists
            temp_path = Path(temp_file.name)
            if temp_path.exists():
                temp_path.unlink()
            raise e
    
    def record_command(self, command: str, args: Dict[str, Any], 
                      timestamp: Optional[datetime] = None) -> None:
        """Record a command execution."""
        if timestamp is None:
            timestamp = datetime.now()
        
        command_record = {
            "command": command,
            "args": args,
            "timestamp": timestamp.isoformat(),
        }
        
        self._data["commands"].append(command_record)
        self._save_data()
    
    def get_command_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get command execution history."""
        commands = list(reversed(self._data["commands"]))  # Most recent first
        if limit:
            commands = commands[:limit]
        return commands
    
    def get_command_frequency(self) -> Dict[str, int]:
        """Get frequency count for each command."""
        frequency = {}
        for record in self._data["commands"]:
            cmd = record["command"]
            frequency[cmd] = frequency.get(cmd, 0) + 1
        return frequency
    
    def store_alias(self, alias: str, command: str, args: Dict[str, Any]) -> None:
        """Store a command alias."""
        self._data["aliases"][alias] = {
            "command": command,
            "args": args,
            "created": datetime.now().isoformat()
        }
        self._save_data()
    
    def get_aliases(self) -> Dict[str, Dict[str, Any]]:
        """Get all stored aliases."""
        return self._data["aliases"]
    
    def get_command_sequences(self, min_length: int = 2) -> List[List[str]]:
        """Get sequences of commands for workflow detection."""
        commands = [record["command"] for record in self._data["commands"]]
        sequences = []
        
        for i in range(len(commands) - min_length + 1):
            sequence = commands[i:i + min_length]
            sequences.append(sequence)
        
        return sequences
    
    def store_workflow(self, name: str, commands: List[Dict[str, Any]]) -> None:
        """Store a command workflow."""
        self._data["workflows"][name] = {
            "commands": commands,
            "created": datetime.now().isoformat()
        }
        self._save_data()
    
    def get_workflows(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all stored workflows."""
        return {
            name: data["commands"] 
            for name, data in self._data["workflows"].items()
        }


class SQLiteStorage(StorageBackend):
    """SQLite database storage backend."""
    
    def __init__(self, app_name: str, storage_path: Optional[str] = None):
        super().__init__(app_name, storage_path)
        self.db_path = Path(self.storage_path) / f"{app_name}.db"
        self._init_db()
    
    def close(self):
        """Close database connections (for testing cleanup)."""
        # Force SQLite to close all connections by connecting and closing
        import gc
        gc.collect()  # Force garbage collection
        try:
            conn = sqlite3.connect(self.db_path)
            conn.close()
        except:
            pass
    
    def _init_db(self) -> None:
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS commands (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    command TEXT NOT NULL,
                    args TEXT NOT NULL,  -- JSON encoded
                    timestamp TEXT NOT NULL
                );
                
                CREATE TABLE IF NOT EXISTS aliases (
                    alias TEXT PRIMARY KEY,
                    command TEXT NOT NULL,
                    args TEXT NOT NULL,  -- JSON encoded
                    created TEXT NOT NULL
                );
                
                CREATE TABLE IF NOT EXISTS workflows (
                    name TEXT PRIMARY KEY,
                    commands TEXT NOT NULL,  -- JSON encoded
                    created TEXT NOT NULL
                );
                
                CREATE INDEX IF NOT EXISTS idx_commands_timestamp 
                ON commands(timestamp);
                
                CREATE INDEX IF NOT EXISTS idx_commands_command 
                ON commands(command);
            """)
    
    def record_command(self, command: str, args: Dict[str, Any], 
                      timestamp: Optional[datetime] = None) -> None:
        """Record a command execution."""
        if timestamp is None:
            timestamp = datetime.now()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO commands (command, args, timestamp) VALUES (?, ?, ?)",
                (command, json.dumps(args), timestamp.isoformat())
            )
    
    def get_command_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get command execution history."""
        with sqlite3.connect(self.db_path) as conn:
            if limit:
                cursor = conn.execute(
                    "SELECT command, args, timestamp FROM commands "
                    "ORDER BY timestamp DESC LIMIT ?",
                    (limit,)
                )
            else:
                cursor = conn.execute(
                    "SELECT command, args, timestamp FROM commands "
                    "ORDER BY timestamp DESC"
                )
            
            return [
                {
                    "command": row[0],
                    "args": json.loads(row[1]),
                    "timestamp": row[2]
                }
                for row in cursor.fetchall()
            ]
    
    def get_command_frequency(self) -> Dict[str, int]:
        """Get frequency count for each command."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT command, COUNT(*) FROM commands GROUP BY command"
            )
            return dict(cursor.fetchall())
    
    def store_alias(self, alias: str, command: str, args: Dict[str, Any]) -> None:
        """Store a command alias."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO aliases (alias, command, args, created) "
                "VALUES (?, ?, ?, ?)",
                (alias, command, json.dumps(args), datetime.now().isoformat())
            )
    
    def get_aliases(self) -> Dict[str, Dict[str, Any]]:
        """Get all stored aliases."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT alias, command, args, created FROM aliases"
            )
            
            return {
                row[0]: {
                    "command": row[1],
                    "args": json.loads(row[2]),
                    "created": row[3]
                }
                for row in cursor.fetchall()
            }
    
    def get_command_sequences(self, min_length: int = 2) -> List[List[str]]:
        """Get sequences of commands for workflow detection."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT command FROM commands ORDER BY timestamp"
            )
            
            commands = [row[0] for row in cursor.fetchall()]
            sequences = []
            
            for i in range(len(commands) - min_length + 1):
                sequence = commands[i:i + min_length]
                sequences.append(sequence)
            
            return sequences
    
    def store_workflow(self, name: str, commands: List[Dict[str, Any]]) -> None:
        """Store a command workflow."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO workflows (name, commands, created) "
                "VALUES (?, ?, ?)",
                (name, json.dumps(commands), datetime.now().isoformat())
            )
    
    def get_workflows(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all stored workflows."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT name, commands FROM workflows")
            
            return {
                row[0]: json.loads(row[1])
                for row in cursor.fetchall()
            }
