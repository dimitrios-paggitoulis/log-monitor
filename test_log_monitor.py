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

    def test_log_report(self):
        """
        Test that log_report writes warnings and errors for jobs exceeding thresholds,
        and does not write for jobs under the threshold.

        Checks that only jobs exceeding the warning or error thresholds are reported,
        and that the correct messages are written to the report.
        """
        reports = [
            {"pid": "1", "description": "Job A", "duration": timedelta(minutes=4, seconds=59)},
            {"pid": "2", "description": "Job B", "duration": timedelta(minutes=6)},
            {"pid": "3", "description": "Job C", "duration": timedelta(minutes=11)},
        ]
        m = mock_open()
        with patch("builtins.open", m):
            log_monitor.log_report(reports, "report.log")
        handle = m()
        handle.write.assert_has_calls([
            call("WARNING: Job 2 (Job B) took 0:06:00\n"),
            call("ERROR: Job 3 (Job C) took 0:11:00\n"),
        ], any_order=True)
        written = "".join(call_arg[0][0] for call_arg in handle.write.call_args_list)
        self.assertNotIn("Job 1", written)

    def test_threshold_boundaries(self):
        """
        Test that jobs just over 5 minutes log a warning,
        jobs just over 10 minutes log an error,
        and jobs at or below thresholds are not reported.

        - Job D: exactly 5 min (no log)
        - Job E: just over 5 min (warning)
        - Job F: exactly 10 min (warning)
        - Job G: just over 10 min (error)
        """
        reports = [
            {"pid": "4", "description": "Job D", "duration": timedelta(minutes=WARNING_THRESHOLD_MINS)},           # Exactly warning threshold: no log
            {"pid": "5", "description": "Job E", "duration": timedelta(minutes=WARNING_THRESHOLD_MINS, seconds=1)},# Just over warning threshold: warning
            {"pid": "6", "description": "Job F", "duration": timedelta(minutes=ERROR_THRESHOLD_MINS)},          # Exactly error threshold: warning
            {"pid": "7", "description": "Job G", "duration": timedelta(minutes=ERROR_THRESHOLD_MINS, seconds=1)} # Just over error threshold: error
        ]
        m = mock_open()
        with patch("builtins.open", m):
            log_monitor.log_report(reports, "report.log")
        handle = m()
        written = "".join(call_arg[0][0] for call_arg in handle.write.call_args_list)
        self.assertNotIn("Job D", written)  # No log for exactly 5 min
        self.assertIn("WARNING: Job 5 (Job E)", written)  # Warning for just over 5 min
        self.assertIn("WARNING: Job 6 (Job F)", written)  # Warning for exactly 10 min
        self.assertIn("ERROR: Job 7 (Job G)", written)    # Error for just over 10 min

if __name__ == "__main__":
    unittest.main()
