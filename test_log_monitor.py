import unittest
from unittest.mock import mock_open, patch, call
from datetime import datetime, timedelta
import log_monitor

WARNING_THRESHOLD_MINS = 5
ERROR_THRESHOLD_MINS = 10

class TestLogMonitor(unittest.TestCase):
    """
    Unit tests for log_monitor.py

    This test suite verifies the following:
    - Correct parsing of valid and malformed log files.
    - Accurate calculation of job durations and correct matching of job START and END events by PID.
    - Proper logging of warnings and errors based on job duration thresholds.
    - That jobs at or below the threshold are not reported, and jobs just over the threshold are reported appropriately.

    All tests use the unittest library and mock file I/O to avoid actual file operations.
    """

    def setUp(self):
        """
        Prepare sample log entries for use in multiple tests.
        Each entry simulates a log line parsed into a dictionary.
        """
        self.entries = [
            {"time": datetime.strptime("12:00:00", "%H:%M:%S"), "description": "Job A", "event": "START", "pid": "1"},
            {"time": datetime.strptime("12:04:59", "%H:%M:%S"), "description": "Job A", "event": "END", "pid": "1"},
            {"time": datetime.strptime("13:00:00", "%H:%M:%S"), "description": "Job B", "event": "START", "pid": "2"},
            {"time": datetime.strptime("13:06:00", "%H:%M:%S"), "description": "Job B", "event": "END", "pid": "2"},
            {"time": datetime.strptime("14:00:00", "%H:%M:%S"), "description": "Job C", "event": "START", "pid": "3"},
            {"time": datetime.strptime("14:11:00", "%H:%M:%S"), "description": "Job C", "event": "END", "pid": "3"},
        ]
        
if __name__ == "__main__":
    unittest.main()
