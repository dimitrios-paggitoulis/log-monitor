import csv
from datetime import datetime, timedelta
from typing import List, Dict, Any

LOG_FILE = "logs.log"
REPORT_FILE = "report.log"
TIME_FORMAT = "%H:%M:%S"
WARNING_THRESHOLD = timedelta(minutes=5)
ERROR_THRESHOLD = timedelta(minutes=10)

def get_log_lines(filename: str) -> List[str]:
    """
    Opens the log file and reads all lines.
    
    Args:
        filename (str): The path to the log file.
    
    Returns:
        List[str]: A list of lines from the log file.
    """
    with open(filename, newline='') as f:
        return f.readlines()

def parse_log(lines: List[str]) -> List[Dict[str, Any]]:
    """
    Parses log lines and returns a list of log entry dictionaries.
    
    Each log entry is expected to be a CSV row with the following fields:
        - time (str): Timestamp in HH:MM:SS format
        - description (str): Description of the job
        - event (str): Either 'START' or 'END'
        - pid (str): Process/job ID
    
    Args:
        lines (List[str]): List of log lines to parse.
    
    Returns:
        List[Dict[str, Any]]: List of parsed log entries, each as a dictionary with keys:
            'time' (datetime), 'description' (str), 'event' (str), 'pid' (str)
    """
    entries: List[Dict[str, Any]] = []
    reader = csv.reader(lines)
    for row in reader:
        # Expecting: HH:MM:SS, Description, START/END, PID
        if len(row) < 4:
            print('Skipping malformed line: ', row)
            continue  # skip malformed lines
        time_str, description, event, pid = row
        try:
            time = datetime.strptime(time_str.strip(), TIME_FORMAT)
        except ValueError:
            print('Skiping line due to invalid time format: ', row)
            continue  # skip lines with invalid time format
        entries.append({
            "time": time,
            "description": description.strip(),
            "event": event.strip().upper(),
            "pid": pid.strip()
        })
        print('Current row:', row)
    return entries

def monitor_jobs(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Tracks jobs by PID, calculates durations, and returns a list of job reports.
    For each job, matches START and END events by PID, calculates the duration,
    and collects job information for reporting.
    
    Args:
        entries (List[Dict[str, Any]]): List of parsed log entries.
   
    Returns:
        List[Dict[str, Any]]: List of job report dictionaries, each with keys:
            'pid', 'description', 'start_time', 'end_time', 'duration'
    """
    jobs: Dict[str, Dict[str, Any]] = {}
    reports: List[Dict[str, Any]] = []
    for entry in entries:
        pid = entry["pid"]
        print('Processing job PID: ', entry["pid"], 'with description:', entry['description'], ' and event: ', entry['event'])
        if entry["event"] == "START":
            jobs[pid] = {
                "start_time": entry["time"],
                "description": entry["description"]
            }
        elif entry["event"] == "END" and pid in jobs:
            start_time = jobs[pid]["start_time"]
            end_time = entry["time"]
            duration = end_time - start_time
            reports.append({
                "pid": pid,
                "description": jobs[pid]["description"],
                "start_time": start_time,
                "end_time": end_time,
                "duration": duration
            })
            del jobs[pid]
    return reports

def log_report(reports: List[Dict[str, Any]], report_file: str) -> None:
    """
    Writes warnings and errors to the report file based on job durations.

    For each job report:
        - Logs a warning if the job took longer than 5 minutes.
        - Logs an error if the job took longer than 10 minutes.

    Args:
        reports (List[Dict[str, Any]]): List of job report dictionaries.
        report_file (str): Path to the output report file.
    """
    with open(report_file, "w") as f:
        for job in reports:
            duration_str = str(job["duration"])
            print('Checking PID ', job["pid"], ' task duration: ', job["duration"])
            if job["duration"] > ERROR_THRESHOLD:
                f.write(f"ERROR: Job {job['pid']} ({job['description']}) took {duration_str}\n")
                print(f"ERROR: Job {job['pid']} ({job['description']}) took {duration_str}\n")
            elif job["duration"] > WARNING_THRESHOLD:
                f.write(f"WARNING: Job {job['pid']} ({job['description']}) took {duration_str}\n")
                print(f"WARNING: Job {job['pid']} ({job['description']}) took {duration_str}\n")

def main() -> None:
    """
    Main entry point for the log monitoring application.
    
    Reads the log file, parses entries, monitors jobs, and writes a report
    of warnings and errors based on job durations.
    """
    print('--- Start processing!!')
    print('--- parse_log calling get_log_lines to open the file and return lines, then parses log lines and returns a list of log entry dictionaries.')
    entries = parse_log(get_log_lines(LOG_FILE))
    print('--- Calling monitor_jobs to track jobs by PID, calculate durations and return a list of job reports. ')
    reports = monitor_jobs(entries)
    print('--- Calling log_report to write warnings and errors to the report file based on job durations.')
    log_report(reports, REPORT_FILE)
    print(f"Monitoring complete. See {REPORT_FILE} for warnings and errors.")

if __name__ == "__main__":
    main()