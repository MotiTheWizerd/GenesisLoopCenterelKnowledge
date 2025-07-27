"""
Rotation-aware log reader for heartbeat monitoring.
"""

import json
from pathlib import Path
from typing import Iterator, Dict, Any


class LogReader:
    """
    Rotation-aware log file reader that handles log file rotation gracefully.
    """
    
    def __init__(self, path: Path):
        """
        Initialize the log reader.
        
        Args:
            path: Path to the log file to read
        """
        self.path = path
        self._pos = 0
        self._ino = None
    
    def read(self) -> Iterator[Dict[str, Any]]:
        """
        Read new events from the log file, handling rotation.
        
        Yields:
            Dict containing parsed JSON events
        """
        if not self.path.exists():
            return
        
        try:
            with self.path.open("r", encoding="utf-8") as f:
                # Detect rotation by checking inode
                stat = self.path.stat()
                current_ino = stat.st_ino
                
                if self._ino is not None and self._ino != current_ino:
                    # File was rotated, start from beginning
                    self._pos = 0
                
                self._ino = current_ino
                
                # Seek to last position
                f.seek(self._pos)
                
                # Read new lines
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        yield json.loads(line)
                    except json.JSONDecodeError:
                        # Skip malformed JSON lines
                        continue
                
                # Update position
                self._pos = f.tell()
                
        except (OSError, IOError):
            # Handle file access errors gracefully
            pass