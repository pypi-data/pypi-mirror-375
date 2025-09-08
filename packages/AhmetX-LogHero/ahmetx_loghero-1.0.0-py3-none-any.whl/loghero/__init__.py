"""
LogHero - System Log Security Analyzer
Developed by Ahmet KAHRAMAN (AhmetXHero)
"""

__version__ = "1.0.0"
__author__ = "Ahmet KAHRAMAN (AhmetXHero)"
__email__ = "ahmetxhero@gmail.com"

from .analyzer import LogAnalyzer
from .detectors import SSHBruteForceDetector, RootAccessDetector
from .parsers import LogParser

__all__ = [
    "LogAnalyzer",
    "SSHBruteForceDetector", 
    "RootAccessDetector",
    "LogParser"
]
