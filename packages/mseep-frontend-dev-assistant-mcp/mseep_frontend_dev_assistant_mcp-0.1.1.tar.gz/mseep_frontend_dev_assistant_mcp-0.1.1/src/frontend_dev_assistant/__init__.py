#!/usr/bin/env python3
"""
前端开发助手 MCP 服务器
提供代码生成、组件查找、Git管理等功能
"""

import json
import logging
from typing import Any, Dict, List, Optional
from mcp.server import Server
from mcp.types import Tool, TextContent
from .call_tracker import call_tracker

__version__ = "0.1.0"
__author__ = "Frontend Dev Team"
__description__ = "前端开发提示词智能助手 MCP服务器 - 专为前端团队设计的AI开发助手"

__all__ = []

# 核心模块导入
# 具体工具实现在主服务器中
