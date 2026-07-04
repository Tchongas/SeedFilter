"""Resolve project paths, supporting normal Python and PyInstaller bundles."""
import os
import sys


if getattr(sys, "frozen", False):
    # PyInstaller extraction directory.
    PROJECT_DIR = sys._MEIPASS
else:
    PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(PROJECT_DIR, "data")
JAR_DIR = os.path.join(PROJECT_DIR, "jar")
LAVA_CHECKER_JAR = os.path.join(JAR_DIR, "lava_checker.jar")
SEED_EXE = os.path.join(PROJECT_DIR, "seed.exe")
SEED_UNIX = os.path.join(PROJECT_DIR, "seed")
