"""Helpers to run the seedfinder and lava checker as subprocesses."""
import os
import subprocess
import sys
import threading

from .paths import DATA_DIR, LAVA_CHECKER_JAR, PROJECT_DIR, SEED_EXE, SEED_UNIX


def find_seed_executable():
    """Return the path to the compiled seedfinder binary."""
    if os.path.exists(SEED_EXE):
        return SEED_EXE
    if os.path.exists(SEED_UNIX):
        return SEED_UNIX
    return None


def run_seedfinder(threads, callback=None):
    """Start the seedfinder in a new console window."""
    exe = find_seed_executable()
    if not exe:
        return None, "seed.exe not found. Compile the seedfinder first."
    cmd = [exe, str(threads)]
    proc = subprocess.Popen(
        cmd,
        cwd=PROJECT_DIR,
        creationflags=subprocess.CREATE_NEW_CONSOLE,
    )
    if callback:
        callback(f"Started seedfinder with {threads} thread(s).")
    return proc, None


def run_seedfinder_streaming(threads, on_line=None, on_done=None):
    """Start the seedfinder and stream its output line-by-line.

    Returns a Popen object that the caller can terminate to stop the search.
    """
    exe = find_seed_executable()
    if not exe:
        if on_done:
            on_done("seed.exe not found. Compile the seedfinder first.")
        return None

    cmd = [exe, str(threads)]
    proc = subprocess.Popen(
        cmd,
        cwd=PROJECT_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    def _reader():
        try:
            for line in proc.stdout:
                if on_line:
                    on_line(line.rstrip("\n"))
        except Exception as exc:
            if on_line:
                on_line(f"[reader error: {exc}]")
        finally:
            proc.stdout.close()
        if on_done:
            on_done(None)

    threading.Thread(target=_reader, daemon=True).start()
    return proc


def run_lavachecker(callback=None):
    """Start the lava checker in a new console window."""
    if not os.path.exists(LAVA_CHECKER_JAR):
        return None, "Lava checker jar not found."
    cmd = ["java", "-jar", LAVA_CHECKER_JAR]
    proc = subprocess.Popen(
        cmd,
        cwd=PROJECT_DIR,
        creationflags=subprocess.CREATE_NEW_CONSOLE,
    )
    if callback:
        callback("Started lava checker.")
    return proc, None


def save_filter(filter_code):
    """Write the filter code to data/filter.txt."""
    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, "filter.txt")
    with open(path, "w") as f:
        f.write(filter_code)
    return path


def load_filter_history():
    """Load the filter history file as a list of entries."""
    path = os.path.join(DATA_DIR, "filterhistory.txt")
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return f.read().split("\n\n")
