# Copyright (C) 2025 TG11
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import inspect
import os
from datetime import datetime
from pathlib import Path
from colorama import Fore, Style, init as colorama_init

def get_log_start_timestamp():
    """
    Returns a formatted timestamp string for the logging session start.

    Format: `YYYY-MM-DD-HH-MM-SS-mmm`
    Used to prefix log filenames with the session's start time.

    :return: A timestamp string for use in log filenames.
    """
    now = datetime.now()
    return now.strftime("%Y-%m-%d-%H-%M-%S-") + f"{int(now.microsecond/1000):03d}"

global LOG_START_TS

LOG_START_TS = get_log_start_timestamp()


# === Config ===
home_dir  = Path(os.getcwd())  # This should be the home folder of the app
tools_dir = Path(os.path.join(home_dir, "tools"))
logs_dir  = Path(os.path.join(home_dir, "logs"))
# === Setup ===
colorama_init(autoreset=True)

DEBUG_LEVEL     = 0
LOG_TO_FILE     = True
MAX_LOG_FILES   = 5
MAX_LOG_SIZE_MB = 2

# === Log counters ===
STATS = {
    "generated":    0,
    "skipped":      0,
    "deleted":      0,
    "errors":       0,
    "warnings":     0,
    "informative":  0,
    "verbose":      0,
    "trace":        0,
    "success":      0
}


def get_default_log_filename():
    """
    Determines a default log file name based on the calling script's filename.

    Combines the session timestamp and the name of the first non-debug file in the call stack.
    Falls back to `debug.log` if no valid file is found.

    :return: A string representing the log filename (with timestamp prefix).
    """
    for frame in inspect.stack():
        filename = frame.filename
        if not filename.endswith("debug.py") and not filename.startswith("<"):
            base = os.path.basename(filename)
            stem = os.path.splitext(base)[0]
            return f"{LOG_START_TS}_{stem}.log"
    return f"{LOG_START_TS}_debug.log"


# Set default path at import
LOG_FILE_PATH = logs_dir / get_default_log_filename()


# Ensure log directory exists
LOG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)

def set_debug_level(level: int):
    """
    Sets the global debug verbosity level.

    Debug Level Map:
    0 = Errors only
    1 = Important log events (success, skipped, warning, deleted, generated)
    2 = Informational output (info)
    3 = Verbose debugging
    4 = Trace (includes file/line)
    5 = Reserved for future use


    :param level: Integer from 0 to 3 indicating the desired verbosity.
    """
    global DEBUG_LEVEL
    DEBUG_LEVEL = max(0, min(3, int(level)))

def set_max_log_files(maxf: int):
    """
    Sets the maximum number of rotated log files to keep.

    :param maxf: Maximum number of old log files to retain.
    """
    global MAX_LOG_FILES
    MAX_LOG_FILES = max(0, min(3, int(maxf)))

def set_max_log_file_size(size: int):
    """
    Sets the maximum size (in MB) a log file can reach before rotating.

    :param size: Log file size in megabytes.
    """
    global MAX_LOG_SIZE_MB
    MAX_LOG_SIZE_MB = max(0, min(3, int(size)))

def set_log_file(path: Path):
    """
    Manually overrides the default log file path.

    Automatically creates any missing parent directories.

    :param path: Full path to the desired log file.
    """
    global LOG_FILE_PATH
    LOG_FILE_PATH = Path(path)
    LOG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)

def current_timestamp():
    """
    Returns the current timestamp in a formatted string.

    Format: `YYYY/MM/DD HH:MM:SS.mmm`

    :return: String representation of the current time.
    """
    now = datetime.now()
    return now.strftime("%Y/%m/%d %H:%M:%S.") + f"{int(now.microsecond/1000):03d}"

def rotate_logs():
    """
    Checks the current log file's size and performs rotation if needed.

    Renames the current log to .1.log, shifting older logs up to .N.log based on rotation limit.
    """
    if not LOG_FILE_PATH.exists():
        return
    if LOG_FILE_PATH.stat().st_size < MAX_LOG_SIZE_MB * 1024 * 1024:
        return

    for i in reversed(range(1, MAX_LOG_FILES)):
        prev = LOG_FILE_PATH.with_name(f"{LOG_FILE_PATH.stem}.{i}.log")
        next = LOG_FILE_PATH.with_name(f"{LOG_FILE_PATH.stem}.{i+1}.log")
        if prev.exists():
            prev.rename(next)

    LOG_FILE_PATH.rename(LOG_FILE_PATH.with_name(f"{LOG_FILE_PATH.stem}.1.log"))

def write_to_logfile(full_message: str):
    """
    Appends a formatted log message to the log file.

    Automatically rotates the log file if its size exceeds the configured limit.

    :param full_message: The fully formatted line to write to the log file.
    """
    if LOG_TO_FILE:
        rotate_logs()
        with open(LOG_FILE_PATH, "a", encoding="utf-8") as log_file:
            log_file.write(full_message + "\n")

def log(msg: str, level: int = 1, tag: str = "DEBUG", color: str = Fore.WHITE, show_trace: bool = False):
    """
    The core logging function that handles printing and file writing.

    Adds a timestamp, colored tag, and optionally file/line trace. Honors the global debug level.

    :param msg: The message to log.
    :param level: The debug level required for this message to display.
    :param tag: The label (e.g., "INFO", "ERROR") shown in brackets.
    :param color: The colorama color to use for the tag.
    :param show_trace: If True, appends file:line trace to the log message.
    """
    if DEBUG_LEVEL >= level:
        timestamp = current_timestamp()
        trace_info = ""
        if show_trace:
            frame = inspect.stack()[2]
            filename = os.path.basename(frame.filename)
            line = frame.lineno
            trace_info = f"{Fore.LIGHTBLACK_EX} ({filename}:{line}){Style.RESET_ALL}"

        formatted_tag = f"[{tag}]".ljust(9)
        output = f"{Fore.LIGHTBLACK_EX}[{timestamp}]{Style.RESET_ALL} {color}{formatted_tag}{Style.RESET_ALL} | {msg}{trace_info}"
        print(output)

        log_line = f"[{timestamp}] {formatted_tag} | {msg}"
        if show_trace:
            log_line += f" ({filename}:{line})"
        write_to_logfile(log_line)


# === Public log levels ===
def error(msg: str):
    """
    Logs a critical error message.
    Always displayed at DEBUG_LEVEL >= 0.
    """
    STATS["errors"] += 1
    log(msg, level=0, tag="ERROR", color=Fore.RED)


def info(msg: str):
    """
    Logs a standard informational message.
    Displayed at DEBUG_LEVEL >= 2.
    """
    STATS["informative"] += 1
    log(msg, level=2, tag="INFO", color=Fore.CYAN)


def verbose(msg: str):
    """
    Logs detailed debug information.
    Displayed at DEBUG_LEVEL >= 3.
    """
    STATS["verbose"] += 1
    log(msg, level=3, tag="VERBOSE", color=Fore.YELLOW)


def trace(msg: str):
    """
    Logs ultra-detailed trace messages, including file and line number.
    Displayed at DEBUG_LEVEL >= 4.
    """
    STATS["trace"] += 1
    log(msg, level=4, tag="TRACE", color=Fore.MAGENTA, show_trace=True)


def skipped(path: str | Path):
    """
    Logs when a file is intentionally skipped (e.g., ignored by config).
    Displayed at DEBUG_LEVEL >= 1.
    """
    STATS["skipped"] += 1
    log(f"Ignored: {path}", level=1, tag="SKIPPED", color=Fore.BLUE)


def generated(path: str | Path):
    """
    Logs when a file has been successfully generated.
    Displayed at DEBUG_LEVEL >= 1.
    """
    STATS["generated"] += 1
    log(f"Generated: {path}", level=1, tag="GENERATED", color=Fore.GREEN)


def deleted(path: str | Path):
    """
    Logs when a file has been deleted (e.g., as cleanup).
    Displayed at DEBUG_LEVEL >= 1.
    """
    STATS["deleted"] += 1
    log(f"Deleted: {path}", level=1, tag="DELETED", color=Fore.LIGHTRED_EX)


def success(msg: str):
    """
    Logs a success status message (generic, task complete, etc).
    Displayed at DEBUG_LEVEL >= 1.
    """
    STATS["success"] += 1
    log(msg, level=1, tag="SUCCESS", color=Fore.LIGHTGREEN_EX)


def warning(msg: str):
    """
    Logs a warning message (non-fatal issue).
    Displayed at DEBUG_LEVEL >= 1.
    """
    STATS["warnings"] += 1
    log(msg, level=1, tag="WARNING", color=Fore.LIGHTYELLOW_EX)


def summary():
    log("Summary of actions:", tag="SUMMARY", color=Fore.LIGHTCYAN_EX, level=1)
    for key, label, color in [
        ("generated",   "Generated", Fore.LIGHTGREEN_EX),
        ("skipped",     "Skipped",   Fore.LIGHTBLUE_EX),
        ("deleted",     "Deleted",   Fore.LIGHTRED_EX),
        ("warnings",    "Warnings",  Fore.LIGHTYELLOW_EX),
        ("success",     "Successes", Fore.GREEN),
        ("informative", "Info",      Fore.CYAN),
        ("verbose",     "Verbose",   Fore.YELLOW),
        ("trace",       "Traces",    Fore.MAGENTA),
        ("errors",      "Errors",    Fore.RED),
    ]:
        count = STATS.get(key, 0)
        log(f"{label}: {count}", tag="SUMMARY", color=color, level=1)


