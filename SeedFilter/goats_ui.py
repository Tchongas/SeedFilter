import os
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox, scrolledtext


PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))


def run_in_terminal(cmd):
    """Run a command in a new visible console window."""
    return subprocess.Popen(
        cmd,
        cwd=PROJECT_DIR,
        creationflags=subprocess.CREATE_NEW_CONSOLE,
    )


def run_command(cmd, label="Command"):
    """Run a command and capture output into the text box."""
    output_box.insert(tk.END, f"\n>>> {label}\n")
    output_box.insert(tk.END, f"$ {' '.join(cmd)}\n")
    output_box.see(tk.END)
    root.update()

    try:
        proc = subprocess.run(
            cmd,
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True,
            check=False,
        )
        output_box.insert(tk.END, proc.stdout)
        if proc.stderr:
            output_box.insert(tk.END, proc.stderr)
        output_box.insert(tk.END, f"\n[exit code {proc.returncode}]\n")
    except FileNotFoundError as exc:
        output_box.insert(tk.END, f"ERROR: {exc}\n")
        output_box.insert(
            tk.END,
            "Make sure the required program is installed and on PATH.\n",
        )
    except Exception as exc:
        output_box.insert(tk.END, f"ERROR: {exc}\n")

    output_box.see(tk.END)


def configure_filter():
    run_command([sys.executable, "config.py"], "Configure filter")


def compile_seedfinder():
    run_command(["compile.bat"], "Compile seedfinder")


def run_seedfinder():
    threads = thread_var.get().strip()
    if not threads:
        threads = "1"
    run_command(["run.bat", threads], "Run seedfinder")


def run_lavachecker():
    run_command(["java", "-jar", "jar/lava_checker.jar"], "Lava checker")


def edit_config():
    path = os.path.join(PROJECT_DIR, "config.py")
    if os.path.exists(path):
        os.startfile(path)
    else:
        messagebox.showerror("Error", "config.py not found.")


def open_data_folder():
    os.startfile(os.path.join(PROJECT_DIR, "data"))


root = tk.Tk()
root.title("GoATS - Minecraft Seed Finder")
root.geometry("700x500")
root.minsize(600, 400)

frame = tk.Frame(root)
frame.pack(pady=10, padx=10, fill=tk.X)

header = tk.Label(
    frame,
    text="GoATS - Minecraft Seed Finder",
    font=("Segoe UI", 16, "bold"),
)
header.pack()

sub = tk.Label(
    frame,
    text="Configure filters in config.py, then compile and run.",
    font=("Segoe UI", 9),
)
sub.pack()

btn_frame = tk.Frame(root)
btn_frame.pack(pady=10, padx=10)

buttons = [
    ("Edit config.py", edit_config),
    ("Generate filter", configure_filter),
    ("Compile", compile_seedfinder),
    ("Run", run_seedfinder),
    ("Lava checker", run_lavachecker),
    ("Open data folder", open_data_folder),
]

for text, command in buttons:
    tk.Button(btn_frame, text=text, width=18, command=command).pack(
        side=tk.LEFT, padx=4
    )

thread_frame = tk.Frame(root)
thread_frame.pack(pady=4, padx=10, fill=tk.X)

tk.Label(thread_frame, text="Threads:").pack(side=tk.LEFT)
thread_var = tk.StringVar(value="1")
tk.Entry(thread_frame, textvariable=thread_var, width=8).pack(side=tk.LEFT, padx=4)

output_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Consolas", 9))
output_box.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

status = tk.Label(
    root,
    text="Ready. If buttons are gray, run this script from the project folder.",
    bd=1,
    relief=tk.SUNKEN,
    anchor=tk.W,
)
status.pack(side=tk.BOTTOM, fill=tk.X)

root.mainloop()
