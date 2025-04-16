import pytest
from collections import defaultdict
from unittest.mock import patch
import os
import sys

from main import process_log_file
from logs_analyzer import (
    HandlersReport,
    LogLevel,
    create_default_log_counters
)

@pytest.fixture
def log_file(tmp_path):
    log_content = "2025-04-16 12:00:00,123 INFO django.request: GET /api/users/\n2025-04-16 12:00:01,456 ERROR django.request: POST /api/login/\n2025-04-16 12:00:02,789 WARNING django.request: GET /api/orders/\n2025-04-16 12:00:03,012 INVALID django.request: GET /api/test/"

    log_path = tmp_path / "test_log.log"
    log_path.write_text(log_content)

    return str(log_path)

def test_handlers_report_process_line():
    analyzer = HandlersReport()
    
    line = "2025-03-28 12:44:46,000 INFO django.request: GET /api/v1/reviews/ 204 OK [192.168.1.59]"
    result = analyzer.process_line(line=line)

    assert result == (LogLevel.INFO, "/api/v1/reviews/")
    assert analyzer.handlers["/api/v1/reviews/"][LogLevel.INFO] == 1
    assert analyzer.total_requests == 1

    line_invalid = "2023-10-10 12:00:00,123 INVALID django.request: GET /api/test/"
    result_invalid = analyzer.process_line(line=line_invalid)
    
    assert result_invalid is None
    assert "/api/test/" not in analyzer.handlers
    assert analyzer.total_requests == 1

def test_handlers_report_process_log_file(log_file):
    analyzer = HandlersReport()
    
    analyzer.process_log_file(log_file)
    
    assert analyzer.total_requests == 3
    assert analyzer.handlers["/api/users/"][LogLevel.INFO] == 1
    assert analyzer.handlers["/api/login/"][LogLevel.ERROR] == 1
    assert analyzer.handlers["/api/orders/"][LogLevel.WARNING] == 1

def test_handlers_report_merge_other_handler():
    analyzer1 = HandlersReport()
    analyzer1.process_line("2023-10-10 12:00:00,123 INFO django.request: GET /api/users/")

    analyzer2 = HandlersReport()
    analyzer2.process_line("2023-10-10 12:00:01,456 ERROR django.request: GET /api/users/")

    analyzer1.merge_other_handler(analyzer2)
    
    assert analyzer1.handlers["/api/users/"][LogLevel.INFO] == 1
    assert analyzer1.handlers["/api/users/"][LogLevel.ERROR] == 1
    assert analyzer1.total_requests == 2

def test_handlers_print_info_empty():
    analyzer = HandlersReport()
    
    assert analyzer.print_info() == "No requests found in logs"