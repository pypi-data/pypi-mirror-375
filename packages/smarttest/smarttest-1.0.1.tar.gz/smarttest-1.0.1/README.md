# SmartTest - Intelligent Code Testing Library

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Downloads](https://img.shields.io/badge/downloads-1000+-orange.svg)](https://pypi.org/project/smarttest)
[![Version](https://img.shields.io/badge/version-1.0.1-blue.svg)](https://pypi.org/project/smarttest)

## 🚀 Overview

**SmartTest** is an intelligent Python code testing library that automatically detects errors, warnings, and potential issues in your code. It provides real-time monitoring with instant error detection and automatic error hiding when issues are resolved.

## ✨ Features

- **🔍 Real-time Error Detection** - Instantly detects errors as you code
- **⚡ Ultra Fast Performance** - Checks files every 0.1 seconds
- **🎯 Smart Analysis** - Finds syntax errors, typos, and potential issues
- **🔄 Auto-hide Errors** - Errors disappear automatically when fixed
- **📁 Multi-file Support** - Monitors all Python files in your project
- **🎨 Beautiful Terminal Interface** - Colorful, easy-to-read output
- **🚀 Zero Configuration** - Works out of the box

## 📦 Installation

```bash
pip install smarttest
```

## 🎯 Quick Start

### Auto-Launch Application

```python
import smarttest
# 🚀 SmartTest application launches automatically!
# No need to do anything else - it starts monitoring immediately
```

### Command Line

```bash
# Start monitoring
smarttest

# Launch desktop app
smarttest-app
```

### Manual Usage

```python
from smarttest import SmartTest

# Create instance manually
smarttest = SmartTest()
smarttest.start()
```

## 🔧 How It Works

1. **Auto Launch** - SmartTest starts automatically when imported
2. **File Scanning** - Scans all `.py` files in your project
3. **Real-time Monitoring** - Watches for file changes every 0.1 seconds
4. **Error Detection** - Instantly detects and displays errors
5. **Auto-hide** - Errors disappear when fixed

## 📊 Error Types Detected

### Syntax Errors
- Invalid characters and corrupted text
- Mismatched parentheses
- Missing closing brackets
- Indentation errors

### Code Quality Issues
- Typos in variable names
- Unused semicolons
- Long lines (over 79 characters)
- Security risks (eval, exec)

### Performance Warnings
- Too many print statements
- Inefficient loops
- Import * usage

## 🎨 Terminal Output

```
🧠 SmartTest - Simple Error Detection
=====================================
👀 Watching for errors...
📝 Edit any .py file to see errors
⏹️ Press Ctrl+C to stop
🔍 Scanning all Python files...

❌ test_file.py: 4 errors
   • Line 25: Invalid characters
   • Line 30: Typo - "resut" should be "result"
   ... 2 more

✅ Fixed: test_file.py
🎉 No more errors!
```

## 🛠️ Advanced Usage

### Custom Error Detection

```python
from smarttest import SmartTest

# Create custom instance
smarttest = SmartTest()

# Check specific file
results = smarttest.check_file('my_file.py')

# Stop monitoring
smarttest.stop()
```

### Error Types

```python
# Syntax errors
if line.count('(') != line.count(')'):
    errors.append('Mismatched parentheses')

# Typos
if 'resut' in line and 'result' not in line:
    errors.append('Typo detected')

# Invalid characters
if any(char in line for char in ['سؤ', 'ؤس', 'ش']):
    errors.append('Invalid characters')
```

## 📁 Project Structure

```
smarttest/
├── __init__.py          # Main library
├── auto_import.py       # Auto dependency installer
├── terminal_interface.py # Beautiful terminal output
├── tester.py           # Core testing engine
└── reporter.py         # Report generation
```

## 🔧 Configuration

SmartTest works with minimal configuration:

```python
# Auto-installs required packages
requirements = ['colorama']

# Monitors all Python files
patterns = ['*.py', '**/*.py']

# Fast checking interval
check_interval = 0.1  # seconds
```

## 🚀 Performance

- **⚡ Ultra Fast** - 0.1 second check interval
- **💾 Lightweight** - Only 1 dependency (colorama)
- **🔄 Efficient** - Only checks modified files
- **📊 Smart** - Avoids duplicate error reporting

## 🎯 Use Cases

### Development
- Real-time error detection during coding
- Code quality monitoring
- Team development standards

### Code Review
- Pre-commit error checking
- Automated quality assurance
- Continuous integration

### Learning
- Educational tool for Python beginners
- Error pattern recognition
- Best practices enforcement



### Development Setup

```bash
git clone https://github.com/En-Hussain/smarttest.git
cd smarttest
pip install -e .
python demo_smarttest.py
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by modern code analysis tools
- Built for the Python community
- Designed for simplicity and performance

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/En-Hussain/smarttest/issues)
- **Discussions**: [GitHub Discussions](https://github.com/En-Hussain/smarttest/discussions)
- **Email**: hsn.nati3@gmail.com

## 🔮 Roadmap

- [ ] Web interface
- [ ] IDE integration
- [ ] Custom rule engine
- [ ] Team collaboration features
- [ ] Advanced reporting

---

**Made with ❤️ for Python developers**

*SmartTest v1.0.1 - Making code better, one error at a time*
