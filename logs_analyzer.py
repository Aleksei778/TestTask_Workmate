from typing import Dict
from collections import defaultdict
import re
from abc import abstractmethod, ABC

LOG_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")

class ReportFabric(ABC):
    @abstractmethod
    def process_line(self, line: str):
        pass

    @abstractmethod
    def process_log_file(self, filepath: str):
        pass

    @abstractmethod
    def merge_results(self, other_report) -> 'ReportFabric':
        pass

    @abstractmethod
    def generate_report(self) -> str:
        pass

def create_default_log_counters() -> Dict[str, int]:
    return {level: 0 for level in LOG_LEVELS}

class HandlersReport(ReportFabric):
    def __init__(self):
        self.handlers: Dict[str, Dict[str, int]] = defaultdict(create_default_log_counters)
        self.total_requests = 0

    def process_line(self, line: str):
        pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} (\w+) django\.request: (?:.*?|GET|POST|PUT|DELETE|PATCH) (\/[^\s]*)'
    
        match = re.search(pattern, line)
        if match:
            log_level  = match.group(1)  # Уровень логирования (INFO, ERROR и т.д.)

            if log_level not in LOG_LEVELS:
                return

            url_path = match.group(2)   # URL путь

            self.handlers[url_path][log_level] += 1
            self.total_requests += 1

            return (log_level, url_path)

    def process_log_file(self, file_path: str):
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                self.process_line(line)

    def merge_results(self, other_report) -> 'ReportFabric':
        if hasattr(other_report, 'handlers') and hasattr(other_report, 'total_requests'):
            for url_path, logs_levels in other_report.handlers.items():
                for log_level, count in logs_levels.items():
                    self.handlers[url_path][log_level] += count
            
            self.total_requests += other_report.total_requests

        return self

    def generate_report(self) -> str:
        if not self.handlers:
            return "No requests found in logs"
        
        result = []
        
        header = f"{'HANDLER':<40}"
        for level in LOG_LEVELS:
            header += f"{level:<10}"
        result.append(header)
        
        for url_path in sorted(self.handlers.keys()):
            level_counts = self.handlers[url_path]
            row = f"{url_path:<40}"
            
            for level in LOG_LEVELS:
                count = level_counts[level]
                row += f"{count:<10}"
            
            result.append(row)
        
        result.append(f"\nTotal requests: {self.total_requests}")
        
        return "\n".join(result)