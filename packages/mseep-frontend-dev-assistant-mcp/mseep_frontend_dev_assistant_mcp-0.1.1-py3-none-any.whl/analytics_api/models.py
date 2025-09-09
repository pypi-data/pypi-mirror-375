"""
Pydantic数据模型定义
"""

from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, Dict, Any, List

class UserRegister(BaseModel):
    """用户注册模型"""
    uuid: str
    email: EmailStr
    name: Optional[str] = None
    department: Optional[str] = None

class UsageLog(BaseModel):
    """使用日志模型"""
    user_uuid: str
    tool_name: str
    arguments: Optional[Dict[str, Any]] = None

class UserResponse(BaseModel):
    """用户信息响应模型"""
    uuid: str
    email: str
    name: Optional[str]
    department: Optional[str]
    created_at: datetime
    last_active: datetime

class UsageStatsResponse(BaseModel):
    """使用统计响应模型"""
    user: Dict[str, Any]
    period: str
    summary: Dict[str, Any]
    tool_stats: List[Dict[str, Any]]
    daily_usage: List[Dict[str, Any]]

class ApiResponse(BaseModel):
    """通用API响应模型"""
    status: str
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

# Git集成扩展模型
class GitSession(BaseModel):
    """Git编程会话模型"""
    session_id: str
    user_uuid: str
    repository_url: str
    repository_type: str  # gitlab, aliyun_yunxiao, github
    branch_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    is_active: bool = True

class CodeChange(BaseModel):
    """代码变更模型"""
    session_id: str
    file_path: str
    lines_added: int
    lines_deleted: int
    complexity_change: int
    functions_added: int
    has_type_annotations: bool
    has_error_handling: bool
    change_timestamp: datetime

class CommitAnalysis(BaseModel):
    """提交分析模型"""
    commit_hash: str
    session_id: Optional[str] = None
    author_name: str
    author_email: str
    commit_message: str
    is_ai_assisted: bool
    files_changed: int
    lines_added: int
    lines_deleted: int
    commit_date: datetime

class GitAnalyticsReport(BaseModel):
    """Git分析报告模型"""
    user_uuid: str
    repository_url: str
    analysis_period_days: int
    total_sessions: int
    total_commits: int
    ai_assisted_commits: int
    total_lines_added: int
    total_lines_deleted: int
    average_code_quality: float
    productivity_score: float
    generated_at: datetime