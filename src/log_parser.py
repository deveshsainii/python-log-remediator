import time
import os
import logging
from typing import Generator, Optional, Dict
from state_manager import StateManager

logger = logging.getLogger(__name__)

class LogParser:
    """Streams log files and directories for analysis."""
    
    def __init__(self, path: str, follow: bool = False):
        self.path = path
        self.follow = follow
        self._offsets: Dict[str, int] = {}
        self.state = StateManager()

    def stream_logs(self) -> Generator[str, None, None]:
        """Yields log lines from a file or all files in a directory."""
        if os.path.isfile(self.path):
            yield from self._read_file(self.path)
        elif os.path.isdir(self.path):
            yield from self._stream_directory()
        else:
            logger.error(f"Path not found: {self.path}")

    def _stream_directory(self) -> Generator[str, None, None]:
        """Handles directory scanning, including real-time multiplexing if follow=True."""
        logger.info(f"Monitoring directory: {self.path}")
        
        # Initial scan
        files = self._get_log_files()
        for f in files:
            yield from self._read_file(f)

        if self.follow:
            logger.info(f"Continuous monitoring enabled for {self.path}")
            while True:
                current_files = self._get_log_files()
                for file_path in current_files:
                    yield from self._read_new_lines(file_path)
                time.sleep(1) # Frequency of directory poll
        
    def _read_file(self, file_path: str) -> Generator[str, None, None]:
        """Reads a file line by line, optionally starting the 'tail' logic."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    self.state.update_stats("logs_processed")
                    yield line.strip()
                self._offsets[file_path] = f.tell()
                
                # If following a single file specifically
                if self.follow and os.path.isfile(self.path) and self.path == file_path:
                    logger.info(f"Tailing single file: {file_path}")
                    while True:
                        line = f.readline()
                        if not line:
                            time.sleep(0.1)
                            continue
                        yield line.strip()
        except Exception as e:
            logger.error(f"Error reading {file_path}: {str(e)}")

    def _read_new_lines(self, file_path: str) -> Generator[str, None, None]:
        """Reads only new content from a file using stored offsets."""
        try:
            current_size = os.path.getsize(file_path)
            last_offset = self._offsets.get(file_path, 0)

            if current_size > last_offset:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    f.seek(last_offset)
                    for line in f:
                        self.state.update_stats("logs_processed")
                        yield line.strip()
                    self._offsets[file_path] = f.tell()
            elif current_size < last_offset:
                logger.info(f"File truncated, resetting offset: {file_path}")
                self._offsets[file_path] = 0
                yield from self._read_new_lines(file_path)
        except FileNotFoundError:
            pass
        except Exception as e:
            logger.error(f"Error reading new lines from {file_path}: {str(e)}")

    def _get_log_files(self) -> list[str]:
        """Returns list of absolute paths for files in the search path."""
        files = []
        for entry in os.scandir(self.path):
            if entry.is_file():
                files.append(entry.path)
        return sorted(files)
