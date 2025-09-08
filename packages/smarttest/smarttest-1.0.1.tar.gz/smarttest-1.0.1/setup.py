#!/usr/bin/env python3
"""
SmartTest - Intelligent Code Testing Library
Setup script for PyPI distribution
"""

from setuptools import setup, find_packages
import os

# Read README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="smarttest",
    version="1.0.1",
    author="SmartTest Team",
    author_email="team@smarttest.dev",
    description="Intelligent Python code testing library with real-time error detection",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/smarttest/smarttest",
    project_urls={
        "Bug Reports": "https://github.com/smarttest/smarttest/issues",
        "Source": "https://github.com/smarttest/smarttest",
        "Documentation": "https://smarttest.readthedocs.io/",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Environment :: X11 Applications",
        "Environment :: Win32 (MS Windows)",
        "Environment :: MacOS X",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=0.5",
            "myst-parser>=0.15",
        ],
    },
    entry_points={
        "console_scripts": [
            "smarttest=smarttest.cli:main",
            "smarttest-app=smarttest.app:main",
        ],
    },
    keywords=[
        "python",
        "testing",
        "code-quality",
        "error-detection",
        "real-time",
        "monitoring",
        "development",
        "tools",
        "linter",
        "static-analysis",
    ],
    include_package_data=True,
    zip_safe=False,
    platforms=["any"],
    license="MIT",
    maintainer="SmartTest Team",
    maintainer_email="team@smarttest.dev",
)
