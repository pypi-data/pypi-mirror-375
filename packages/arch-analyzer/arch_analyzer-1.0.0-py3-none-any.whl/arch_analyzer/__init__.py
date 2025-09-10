"""
Architecture Analyzer

基于Claude Code的源码架构设计质量分析工具，支持多维度架构缺陷检测。
"""

__version__ = "1.0.0"
__author__ = "Arch Analyzer Team"
__email__ = ""
__description__ = "基于Claude Code的源码架构设计质量分析工具，支持多维度架构缺陷检测"

from .cli import ArchAnalyzer

__all__ = ["ArchAnalyzer", "__version__"]