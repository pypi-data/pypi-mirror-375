#!/usr/bin/env python3
"""
LogHero - System Log Security Analyzer
A tool for detecting suspicious activities in system logs
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="AhmetX-LogHero",
    version="1.0.0",
    author="Ahmet KAHRAMAN (AhmetXHero)",
    author_email="ahmetxhero@gmail.com",
    description="System log analyzer for detecting suspicious activities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ahmetxhero/AhmetX-LogHero",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: System :: Systems Administration",
        "Topic :: Security",
    ],
    python_requires=">=3.7",
    install_requires=[
        "click>=8.0.0",
        "colorama>=0.4.4",
        "python-dateutil>=2.8.0",
        "tabulate>=0.9.0",
    ],
    entry_points={
        "console_scripts": [
            "loghero=loghero.cli:main",
        ],
    },
    keywords="log analysis security ssh brute-force system administration",
    project_urls={
        "Bug Reports": "https://github.com/ahmetxhero/AhmetX-LogHero/issues",
        "Source": "https://github.com/ahmetxhero/AhmetX-LogHero",
    },
)
