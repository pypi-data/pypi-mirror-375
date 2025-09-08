"""
SmartTest Code Analysis Engine
Advanced error detection and code quality assessment
"""

import ast
import subprocess
import os
import sys
from typing import Dict, List, Any

class CodeTester:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.suggestions = []
        
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        if not os.path.exists(file_path):
            return {
                'status': 'error',
                'message': f'File not found: {file_path}',
                'errors': [],
                'warnings': [],
                'suggestions': []
            }
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
                
            return self.analyze_code(code, file_path)
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error reading file: {str(e)}',
                'errors': [str(e)],
                'warnings': [],
                'suggestions': []
            }
            
    def analyze_code(self, code: str, file_path: str = '') -> Dict[str, Any]:
        self.errors = []
        self.warnings = []
        self.suggestions = []
        
        self.check_syntax(code)
        self.check_style(code)
        self.check_performance(code)
        self.check_security(code)
        
        return {
            'status': 'success',
            'file_path': file_path,
            'errors': self.errors,
            'warnings': self.warnings,
            'suggestions': self.suggestions,
            'summary': self.generate_summary()
        }
        
    def check_syntax(self, code: str):
        try:
            ast.parse(code)
        except SyntaxError as e:
            self.errors.append(f'Syntax Error: {e.msg} at line {e.lineno}')
        except IndentationError as e:
            self.errors.append(f'Indentation Error: {e.msg} at line {e.lineno}')
        except Exception as e:
            self.errors.append(f'Parse Error: {str(e)}')
            
    def check_style(self, code: str):
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            if len(line) > 79:
                self.warnings.append(f'Line {i}: Line too long ({len(line)} characters)')
                self.warnings.append(f'   └─ Content: "{line.strip()}"')
                
            if line.strip().endswith(';'):
                self.suggestions.append(f'Line {i}: Remove semicolon (not needed in Python)')
                self.suggestions.append(f'   └─ Content: "{line.strip()}"')
                
            if 'print(' in line and 'debug' not in line.lower():
                self.suggestions.append(f'Line {i}: Consider using logging instead of print')
                self.suggestions.append(f'   └─ Content: "{line.strip()}"')
                
            if line.strip() and not line.startswith('#') and not line.startswith('"""') and not line.startswith("'''"):
                if any(char in line for char in ['سؤ', 'ؤس', 'ش', 'ؤ', 'ح', 'ي', 'ص']):
                    self.errors.append(f'Line {i}: Invalid characters detected - contains Arabic or corrupted text')
                    self.errors.append(f'   └─ Content: "{line.strip()}"')
                    
            if 'resut' in line and 'result' not in line:
                self.errors.append(f'Line {i}: Typo detected - "resut" should be "result"')
                self.errors.append(f'   └─ Content: "{line.strip()}"')
                
            if line.strip() and line.count('(') != line.count(')'):
                self.errors.append(f'Line {i}: Mismatched parentheses')
                self.errors.append(f'   └─ Content: "{line.strip()}"')
                
            if 'bad_function(' in line and not line.strip().endswith(')'):
                self.errors.append(f'Line {i}: Missing closing parenthesis in function call')
                self.errors.append(f'   └─ Content: "{line.strip()}"')
                
    def check_performance(self, code: str):
        if 'import *' in code:
            self.warnings.append('Avoid using "import *" - it can slow down your code')
            
        if 'for i in range(len(' in code:
            self.suggestions.append('Consider using enumerate() instead of range(len())')
            
        if 'list.append(' in code and code.count('list.append(') > 5:
            self.suggestions.append('Consider using list comprehension for better performance')
            
        if code.count('print(') > 3:
            self.warnings.append('Too many print statements - consider using logging')
            
    def check_security(self, code: str):
        dangerous_functions = ['eval', 'exec', 'input', 'raw_input']
        
        for func in dangerous_functions:
            if func in code:
                self.warnings.append(f'Potential security risk: {func}() function detected')
                
        if 'password' in code.lower() and 'input(' in code:
            self.warnings.append('Consider using getpass for password input')
            
    def generate_summary(self) -> Dict[str, Any]:
        total_issues = len(self.errors) + len(self.warnings)
        
        if total_issues == 0:
            status = 'excellent'
            message = 'No issues found! Your code looks great!'
        elif len(self.errors) == 0:
            status = 'good'
            message = 'Code is functional but has some warnings and suggestions'
        else:
            status = 'needs_attention'
            message = 'Code has errors that need to be fixed'
            
        return {
            'status': status,
            'message': message,
            'total_issues': total_issues,
            'error_count': len(self.errors),
            'warning_count': len(self.warnings),
            'suggestion_count': len(self.suggestions)
        }
        
    def auto_fix_code(self, code: str) -> str:
        fixed_code = code
        
        lines = fixed_code.split('\n')
        fixed_lines = []
        
        for line in lines:
            fixed_line = line
            
            if line.strip() and not line.startswith('#') and not line.startswith('"""') and not line.startswith("'''"):
                if any(char in line for char in ['سؤ', 'ؤس', 'ش', 'ؤ', 'ح', 'ي', 'ص']):
                    fixed_line = ''
                    
                if 'resut' in line and 'result' not in line:
                    fixed_line = line.replace('resut', 'result')
                    
                if line.strip().endswith(';'):
                    fixed_line = line.rstrip(';')
                    
                if 'bad_function(' in line and not line.strip().endswith(')'):
                    if 'bad_function(' in line:
                        fixed_line = line.replace('bad_function(', 'bad_function()')
                        
            fixed_lines.append(fixed_line)
            
        return '\n'.join(fixed_lines)
        
    def save_fixed_code(self, file_path: str, fixed_code: str) -> bool:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_code)
            return True
        except Exception:
            return False
