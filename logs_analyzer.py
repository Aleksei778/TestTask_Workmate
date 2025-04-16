import argparse
import os
import sys
from typing import Tuple, Dict
from collections import defaultdict
import re
from enum import Enum

class LogLevel(Enum):
    INFO = "INFO"
    ERROR = "ERROR"
    DEBUG = "DEBUG"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"

class HandlersReport:
    def __init__(self):
        self.handlers: Dict[str, Dict[str, LogLevel]] = defaultdict(lambda: {
            LogLevel.INFO: 0,
            LogLevel.ERROR: 0,
            LogLevel.DEBUG: 0,
            LogLevel.CRITICAL: 0,
            LogLevel.WARNING: 0
        })
        self.total_requests = 0

    def process_line(self, line: str) -> Tuple[str, str] | None:
        pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} (\w+) django\.request: (?:.*?|GET|POST|PUT|DELETE|PATCH) (\/[^\s]*)'
    
        match = re.search(pattern, line)
        if match:
            log_level_str  = match.group(1)  # Уровень логирования (INFO, ERROR и т.д.)
            log_level = LogLevel(log_level_str)
            url_path = match.group(2)   # URL путь
            
            if log_level not in [lvl for lvl in LogLevel]:
                return

            self.handlers[url_path][log_level] += 1
            self.total_requests += 1

    def process_log_file(self, file_path: str):
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                self.process_line(line)

    def merge_other_handler(self, other_handler: 'HandlersReport') -> 'HandlersReport':
        for url_path, logs_levels in other_handler.handlers.items():
            for log_level, count in logs_levels.items():
                self.handlers[url_path][log_level] += count
        
        self.total_requests += other_handler.total_requests

    def print_info(self) -> str:
        if not self.handlers:
            return "No requests found in logs"
        
        result = [f"Total request: {self.total_requests}\n"]

        result.append(f"{'HANDLER':<20}\t{'DEBUG':<7}\t{'INFO':<7}\t{'WARNING':<7}\t{'ERROR':<7}\t{'CRITICAL':<7}")

        for url_path in self.handlers:
            level_counts = self.handlers[url_path]
            row = f"{url_path:<20}\t"
            
            for level in [LogLevel.DEBUG, LogLevel.INFO, LogLevel.WARNING, LogLevel.ERROR, LogLevel.CRITICAL]:
                count = level_counts[level]
                row += f"{count:<7}\t"

            result.append(row)
        
        return "\n".join(result)