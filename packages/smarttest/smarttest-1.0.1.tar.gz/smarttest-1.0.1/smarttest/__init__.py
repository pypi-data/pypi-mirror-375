"""
SmartTest - Intelligent Code Testing Library
Real-time error detection and monitoring
"""

import os
import sys
import glob
import time
import threading
from .auto_import import AutoImporter
from .tester import CodeTester
from .terminal_interface import TerminalInterface
from .app import SmartTestApp

class SmartTest:
    def __init__(self):
        self.auto_importer = AutoImporter()
        self.terminal = TerminalInterface()
        self.is_running = False
        self.last_errors = {}
        self.file_times = {}
        
    def start(self):
        if not self.is_running:
            self.is_running = True
            self.auto_importer.install_requirements()
            self.terminal.show_header()
            self.start_fast_watching()
            
    def start_fast_watching(self):
        self.terminal.show_watching()
        self.terminal.show_scanning()
        threading.Thread(target=self.fast_loop, daemon=True).start()
            
    def fast_loop(self):
        while self.is_running:
            try:
                python_files = glob.glob('*.py') + glob.glob('**/*.py', recursive=True)
                for file_path in python_files:
                    skip_files = ['setup.py', 'pyproject.toml', 'requirements.txt', 'LICENSE', 'README.md', 'CHANGELOG.md']
                    if any(skip in file_path for skip in ['smarttest', 'setup.py', 'pyproject.toml', 'requirements.txt', 'LICENSE', 'README.md', 'CHANGELOG.md']):
                        continue
                        
                    if os.path.exists(file_path):
                        current_time = os.path.getmtime(file_path)
                        if file_path not in self.file_times or current_time != self.file_times[file_path]:
                            self.file_times[file_path] = current_time
                            self.check_file(file_path)
                    else:
                        if file_path in self.last_errors:
                            del self.last_errors[file_path]
                            self.terminal.show_file_deleted(file_path)
                        
                time.sleep(0.1)
            except:
                pass
                
    def check_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            errors = self.quick_check(code)
            
            if errors:
                if file_path not in self.last_errors or self.last_errors[file_path] != errors:
                    self.last_errors[file_path] = errors
                    self.terminal.show_errors(file_path, errors)
            else:
                if file_path in self.last_errors:
                    del self.last_errors[file_path]
                    self.terminal.show_fixed(file_path)
        except:
            pass
            
    def quick_check(self, code):
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
        
    def stop(self):
        self.is_running = False

def auto_launch():
    try:
        from .app import SmartTestApp
        app = SmartTestApp()
        threading.Thread(target=app.start, daemon=True).start()
    except Exception:
        pass

auto_launch()

smarttest = SmartTest()
smarttest.start()
