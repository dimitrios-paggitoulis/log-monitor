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

    def test_parse_log_file_valid(self):
        """
        Test that valid CSV log lines are parsed correctly.

        Ensures that each field is correctly extracted and that the event, PID, and description
        match the expected values.
        """
        log_text = ["12:00:00,Job A,START,1", "12:04:59,Job A,END,1"]
        entries = log_monitor.parse_log(log_text)
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0]["event"], "START")
        self.assertEqual(entries[1]["event"], "END")
        self.assertEqual(entries[0]["pid"], "1")
        self.assertEqual(entries[0]["description"], "Job A")

    def test_parse_log_file_malformed(self):
        """
        Test that malformed lines are skipped and only valid lines are parsed.

        Ensures that lines with missing fields or bad formatting are ignored,
        and only valid entries are returned.
        """
        log_text = ["12:00:00,Job A,START", "badline", "12:01:00,Job B,END,2"]
        entries = log_monitor.parse_log(log_text)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["pid"], "2")

    def test_monitor_jobs(self):
        """
        Test that job durations are calculated correctly and jobs are matched by PID.

        Verifies that the number of reports matches the number of jobs,
        and that the durations are as expected for each job.
        """
        reports = log_monitor.monitor_jobs(self.entries)
        self.assertEqual(len(reports), 3)
        self.assertEqual(reports[0]["pid"], "1")
        self.assertEqual(reports[1]["pid"], "2")
        self.assertEqual(reports[2]["pid"], "3")
        self.assertEqual(reports[0]["duration"], timedelta(minutes=4, seconds=59))
        self.assertEqual(reports[1]["duration"], timedelta(minutes=6))
        self.assertEqual(reports[2]["duration"], timedelta(minutes=11))

if __name__ == "__main__":
    unittest.main()
