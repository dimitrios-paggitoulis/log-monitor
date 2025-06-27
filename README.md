# Log Monitor Application

## Purpose:

A Python application to monitor job durations from logs and report warnings or errors based on duration thresholds. It is modular, with clear separation of file reading, parsing, processing, and reporting logic.

## Functionality
1. Parses the CSV log file.
2. Identifies each job or task and tracks its start and finish times.
3. Calculates the duration of each job from the time it started to the time it finished.
4. Produces a report or output that:
   • Logs a warning if a job took longer than 5 minutes.
   • Logs an error if a job took longer than 10 minutes.

Log Structure:  
• HH:MM:SS is a timestamp in hours, minutes, and seconds.  
• The job description.  
• Each log entry is either the “START” or “END” of a process.  
• Each job has a PID associated with it e.g., 46578.  

Log files: 
• Input file: logs.log
• Output file: report.log

## Key Components:

### Constants:
LOG_FILE and REPORT_FILE specify the input and output file names.
TIME_FORMAT defines the expected time format in the logs.
WARNING_THRESHOLD and ERROR_THRESHOLD set the duration limits for warnings (5 minutes) and errors (10 minutes).

### get_log_lines:
Reads all lines from the log file and returns them as a list of strings.

###  parse_log:
Parses the log lines using the CSV reader. Each valid line is converted into a dictionary with keys: time (as a datetime object), description, event (START/END), and PID. Malformed or invalid lines are skipped.

### monitor_jobs:
Matches job START and END events by PID, calculates the duration for each job, and returns a list of job report dictionaries containing job details and duration.

### log_report:
Writes warnings to the report file for jobs that exceed the warning threshold and errors for those that exceed the error threshold. Each entry includes the PID, description, and duration.

### main:
Orchestrates the process: reads the log file, parses entries, monitors jobs, and writes the report. It also prints progress messages to the console.

# Log Monitor Application Tests

## Purpose:
This test suite ensures the reliability and correctness of the log monitoring application, covering normal operation, edge cases, and error handling.

## Description
This code is a class-based unit test suite for the log_monitor.py log monitoring application, using Python’s unittest framework. The tests verify that the log monitoring logic correctly parses log files, calculates job durations, and writes warnings or errors to a report file when jobs exceed specified time thresholds.

## Key Features:

### Test Class:
TestLogMonitor contains all test cases and uses a setUp method to prepare reusable sample log entries.

### Tested Behaviors:

#### Parsing:
test_parse_log_file_valid checks that valid log lines are parsed into the correct fields.  
test_parse_log_file_malformed ensures malformed lines are skipped.  

Job Duration Calculation:  
test_monitor_jobs verifies that job durations are calculated correctly and jobs are matched by PID.  

Reporting:  
test_log_report checks that only jobs exceeding the warning (5 minutes) or error (10 minutes) thresholds are reported, and that the correct messages are written.  
test_threshold_boundaries ensures jobs at or below the thresholds are not reported, while jobs just over the thresholds are reported as warnings or errors as appropriate.  

#### Mocking:
The tests use unittest.mock to simulate file I/O, so no actual files are read or written.

### Execution:
The test suite can be run directly as a script, and will automatically execute all test cases.


## How to Run
```bash
Run the application:
python log_monitor.py
Run the tests:
python test_log_monitor.py