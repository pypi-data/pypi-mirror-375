#!/usr/bin/env python3
"""
SmartTest Auto-Launcher
Automatically launches the application when library is imported
"""

import sys
import os
import threading
import time
from .app import SmartTestApp

def auto_launch():
    """Auto-launch SmartTest application"""
    try:
        # Check if we're in a terminal
        if sys.stdin.isatty():
            app = SmartTestApp()
            app.start()
        else:
            # If not in terminal, start in background
            app = SmartTestApp()
            threading.Thread(target=app.start, daemon=True).start()
    except Exception:
        pass

# Auto-launch when this module is imported
if __name__ != "__main__":
    auto_launch()
