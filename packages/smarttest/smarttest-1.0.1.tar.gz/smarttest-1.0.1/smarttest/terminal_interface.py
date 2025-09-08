"""
SmartTest Terminal Interface
Real-time error display and monitoring
"""

import os
import sys
from colorama import init, Fore, Back, Style

init(autoreset=True)

class TerminalInterface:
    def __init__(self):
        self.colors = {
            'header': Fore.CYAN + Style.BRIGHT,
            'success': Fore.GREEN + Style.BRIGHT,
            'error': Fore.RED + Style.BRIGHT,
            'warning': Fore.YELLOW + Style.BRIGHT,
            'info': Fore.BLUE + Style.BRIGHT,
            'suggestion': Fore.MAGENTA + Style.BRIGHT,
            'reset': Style.RESET_ALL
        }
        
    def show_header(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{self.colors['header']}")
        print("🧠 SmartTest - Simple Error Detection")
        print("=" * 50)
        print(f"{self.colors['reset']}")
        
    def show_watching(self):
        print(f"{self.colors['info']}👀 Watching for errors...")
        print(f"{self.colors['info']}📝 Edit any .py file to see errors")
        print(f"{self.colors['info']}⏹️ Press Ctrl+C to stop")
        print(f"{self.colors['reset']}")
        
    def show_scanning(self):
        print(f"{self.colors['info']}🔍 Scanning all Python files...")
        print(f"{self.colors['reset']}")
        
    def show_errors(self, file_path, errors):
        print(f"\n{self.colors['error']}❌ {file_path}: {len(errors)} errors")
        for error in errors[:2]:
            print(f"   • {error}")
        if len(errors) > 2:
            print(f"   ... {len(errors) - 2} more")
        print(f"{self.colors['reset']}")
        
    def show_fixed(self, file_path):
        print(f"\n{self.colors['success']}✅ Fixed: {file_path}")
        print(f"{self.colors['success']}🎉 No more errors!")
        print(f"{self.colors['reset']}")
        
    def show_file_deleted(self, file_path):
        print(f"\n{self.colors['warning']}🗑️ Deleted: {file_path}")
        print(f"{self.colors['reset']}")
        
    def show_error(self, message):
        print(f"{self.colors['error']}❌ {message}")
        print(f"{self.colors['reset']}")
        
    def show_no_files(self):
        print(f"{self.colors['warning']}⚠️ No Python files found in current directory")
        print(f"{self.colors['info']}💡 Create a .py file to test SmartTest")
        print(f"{self.colors['reset']}")
        
    def show_auto_fixed(self, file_path):
        print(f"{self.colors['success']}🔧 Auto-fixed: {file_path}")
        print(f"{self.colors['info']}✅ File has been automatically corrected!")
        print(f"{self.colors['reset']}")
        
    def show_watching_started(self):
        print(f"{self.colors['success']}")
        print("👀 File Watching Started!")
        print("=" * 50)
        print(f"{self.colors['info']}🔄 SmartTest is now watching for file changes...")
        print(f"{self.colors['info']}📝 Edit any .py file to see real-time analysis!")
        print(f"{self.colors['info']}⏹️ Press Ctrl+C to stop watching")
        print(f"{self.colors['reset']}")
        
    def show_file_changed(self, file_path):
        print(f"\n{self.colors['info']}📝 File changed: {file_path}")
        print(f"{self.colors['info']}🔍 Analyzing changes...")
        print(f"{self.colors['reset']}")
        
    def show_watching_error(self, error_msg):
        print(f"{self.colors['error']}❌ File watching error: {error_msg}")
        print(f"{self.colors['warning']}⚠️ Continuing without file watching...")
        print(f"{self.colors['reset']}")
        
    def show_complete(self):
        print(f"{self.colors['success']}")
        print("🎊 SmartTest Analysis Complete!")
        print("=" * 50)
        print(f"{self.colors['info']}💡 SmartTest found and analyzed all Python files")
        print(f"{self.colors['info']}⚠️ Fix the issues above to improve your code")
        print(f"{self.colors['reset']}")
        
    def show_instructions(self):
        print(f"{self.colors['info']}👀 Watching for errors...")
        print(f"{self.colors['info']}📝 Edit any .py file to see errors")
        print(f"{self.colors['info']}⏹️ Press Ctrl+C to stop")
        print(f"{self.colors['reset']}")
        
    def show_goodbye(self):
        print(f"\n{self.colors['success']}👋 SmartTest stopped!")
        print(f"{self.colors['info']}Thanks for using SmartTest! 🎉")
        print(f"{self.colors['reset']}")
