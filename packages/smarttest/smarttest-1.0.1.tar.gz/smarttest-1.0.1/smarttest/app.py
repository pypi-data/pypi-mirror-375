#!/usr/bin/env python3
"""
SmartTest Desktop Application
Auto-launches when library is installed
"""

import sys
import os
import threading
import time
from .terminal_interface import TerminalInterface

class SmartTestApp:
    def __init__(self):
        self.terminal = TerminalInterface()
        self.running = False
        self.last_errors = {}
        self.file_times = {}
        
    def start(self):
        self.running = True
        self.terminal.show_header()
        self.terminal.show_instructions()
        
        monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        monitor_thread.start()
        
        try:
            while self.running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.stop()
    
    def _monitor_loop(self):
        while self.running:
            try:
                python_files = []
                skip_files = ['setup.py', 'pyproject.toml', 'requirements.txt', 'LICENSE', 'README.md', 'CHANGELOG.md']
                for root, dirs, files in os.walk('.'):
                    if 'smarttest' in root:
                        continue
                    for file in files:
                        if file.endswith('.py') and not any(skip in file for skip in skip_files):
                            python_files.append(os.path.join(root, file))
                
                for file_path in python_files:
                    if os.path.exists(file_path):
                        errors = self._check_file(file_path)
                        if errors:
                            if file_path not in self.last_errors or self.last_errors[file_path] != errors:
                                self.last_errors[file_path] = errors
                                self.terminal.show_errors(file_path, errors)
                        else:
                            if file_path in self.last_errors:
                                del self.last_errors[file_path]
                                self.terminal.show_fixed(file_path)
                    else:
                        if file_path in self.last_errors:
                            del self.last_errors[file_path]
                            self.terminal.show_file_deleted(file_path)
                
                time.sleep(0.1)
                
            except Exception as e:
                pass
    
    def _check_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            errors = []
            lines = code.split('\n')
            
            for i, line in enumerate(lines, 1):
                if any(char in line for char in ['سؤ', 'ؤس', 'ش', 'ؤ', 'ح', 'ي', 'ص']):
                    errors.append(f'Line {i}: Invalid characters')
                if 'resut' in line and 'result' not in line:
                    errors.append(f'Line {i}: Typo - "resut" should be "result"')
                if line.strip() and line.count('(') != line.count(')'):
                    errors.append(f'Line {i}: Mismatched parentheses')
                if 'bad_function(' in line and not line.strip().endswith(')'):
                    errors.append(f'Line {i}: Missing closing parenthesis')
                    
            return errors
        except:
            return []
    
    def stop(self):
        self.running = False
        self.terminal.show_goodbye()

def main():
    app = SmartTestApp()
    app.start()

if __name__ == "__main__":
    main()
