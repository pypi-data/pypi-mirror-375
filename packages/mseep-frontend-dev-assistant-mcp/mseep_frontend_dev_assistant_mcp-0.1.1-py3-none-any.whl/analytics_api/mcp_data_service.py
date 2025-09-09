"""
MCP数据收集和存储服务
将MCP调用数据存储到数据库中
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from .database import DatabaseManager
from .git_analyzer import GitAnalyzer

class MCPDataService:
    """MCP数据服务"""
    
    def __init__(self, database_url: str = None):
        self.db = DatabaseManager(database_url)
        self.git_analyzer = GitAnalyzer()
    
    async def init_service(self):
        """初始化服务"""
        await self.db.init_database()
    
    async def register_user(self, user_info: Dict[str, Any]) -> Dict[str, Any]:
        """注册用户"""
        return await self.db.register_user(
            uuid=user_info.get('uuid', str(uuid.uuid4())),
            email=user_info['email'],
            name=user_info.get('name'),
            department=user_info.get('department')
        )
    
    async def record_mcp_call(self, user_uuid: str, tool_name: str, 
                            arguments: Dict[str, Any] = None,
                            execution_time: float = 0,
                            success: bool = True,
                            error_message: str = None) -> Dict[str, Any]:
        """记录MCP工具调用"""
        try:
            # 记录基础使用日志
            await self.db.log_usage(user_uuid, tool_name, arguments)
            
            # 如果是git相关工具，进行额外分析
            if 'git' in tool_name.lower():
                await self._analyze_git_context(user_uuid, tool_name, arguments)
            
            return {
                'status': 'success',
                'message': 'MCP调用记录成功',
                'data': {
                    'user_uuid': user_uuid,
                    'tool_name': tool_name,
                    'timestamp': datetime.now().isoformat(),
                    'execution_time': execution_time,
                    'success': success
                }
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'记录MCP调用失败: {str(e)}'
            }
    
    async def _analyze_git_context(self, user_uuid: str, tool_name: str, 
                                 arguments: Dict[str, Any]):
        """分析git上下文并记录会话"""
        try:
            # 获取仓库信息
            repo_info = self.git_analyzer.get_repo_info()
            
            if not repo_info.get('remote_url'):
                return  # 不是git仓库，跳过
            
            # 创建或更新git会话
            session_id = await self._get_or_create_git_session(
                user_uuid, repo_info
            )
            
            # 如果是提交相关的操作，分析提交信息
            if 'commit' in tool_name.lower():
                await self._analyze_recent_commits(session_id)
            
            # 分析当前代码变更
            await self._analyze_current_changes(session_id)
            
        except Exception as e:
            print(f"Git上下文分析失败: {e}")
    
    async def _get_or_create_git_session(self, user_uuid: str, 
                                       repo_info: Dict[str, Any]) -> str:
        """获取或创建git会话"""
        conn = await self.db.get_connection()
        try:
            # 检查是否有活跃的会话
            existing_session = await conn.fetchrow(
                """SELECT session_id FROM git_sessions 
                   WHERE user_uuid = $1 AND repository_url = $2 AND is_active = TRUE
                   ORDER BY start_time DESC LIMIT 1""",
                user_uuid, repo_info['remote_url']
            )
            
            if existing_session:
                return existing_session['session_id']
            
            # 创建新会话
            session_id = str(uuid.uuid4())
            await conn.execute(
                """INSERT INTO git_sessions 
                   (session_id, user_uuid, repository_url, repository_type, 
                    branch_name, start_time, is_active)
                   VALUES ($1, $2, $3, $4, $5, $6, $7)""",
                session_id, user_uuid, repo_info['remote_url'],
                repo_info.get('repository_type', 'unknown'),
                repo_info.get('current_branch', 'unknown'),
                datetime.now(), True
            )
            
            return session_id
            
        finally:
            await conn.close()
    
    async def _analyze_recent_commits(self, session_id: str):
        """分析最近的提交"""
        commits = self.git_analyzer.get_commit_history(since_days=1)
        
        if not commits:
            return
        
        conn = await self.db.get_connection()
        try:
            for commit in commits:
                # 检查提交是否已存在
                existing = await conn.fetchrow(
                    "SELECT commit_hash FROM commit_analysis WHERE commit_hash = $1",
                    commit['hash']
                )
                
                if not existing:
                    await conn.execute(
                        """INSERT INTO commit_analysis 
                           (commit_hash, session_id, author_name, author_email,
                            commit_message, is_ai_assisted, commit_date)
                           VALUES ($1, $2, $3, $4, $5, $6, $7)""",
                        commit['hash'], session_id, commit['author_name'],
                        commit['author_email'], commit['message'],
                        commit['is_ai_assisted'], 
                        datetime.fromisoformat(commit['date'].replace(' ', 'T', 1))
                    )
        finally:
            await conn.close()
    
    async def _analyze_current_changes(self, session_id: str):
        """分析当前代码变更"""
        status = self.git_analyzer.get_status()
        
        if status.get('total_changes', 0) == 0:
            return
        
        conn = await self.db.get_connection()
        try:
            # 分析每个修改的文件
            for file_path in status.get('modified_files', []):
                changes = self.git_analyzer.get_file_changes(file_path)
                
                if 'error' not in changes:
                    # 记录代码变更
                    await conn.execute(
                        """INSERT INTO code_changes 
                           (session_id, file_path, lines_added, lines_deleted, 
                            change_timestamp)
                           VALUES ($1, $2, $3, $4, $5)""",
                        session_id, file_path, 
                        changes['lines_added'], changes['lines_deleted'],
                        datetime.now()
                    )
        finally:
            await conn.close()
    
    async def get_user_analytics(self, user_uuid: str, days: int = 30) -> Dict[str, Any]:
        """获取用户分析数据"""
        conn = await self.db.get_connection()
        try:
            # 基础使用统计
            usage_stats = await conn.fetch(
                """SELECT tool_name, COUNT(*) as count,
                          DATE(timestamp) as date
                   FROM usage_logs 
                   WHERE user_uuid = $1 AND timestamp >= $2
                   GROUP BY tool_name, DATE(timestamp)
                   ORDER BY date DESC""",
                user_uuid, datetime.now() - timedelta(days=days)
            )
            
            # Git会话统计
            git_stats = await conn.fetch(
                """SELECT gs.repository_url, gs.repository_type,
                          COUNT(DISTINCT gs.session_id) as sessions,
                          COUNT(ca.commit_hash) as commits,
                          SUM(CASE WHEN ca.is_ai_assisted THEN 1 ELSE 0 END) as ai_commits
                   FROM git_sessions gs
                   LEFT JOIN commit_analysis ca ON gs.session_id = ca.session_id
                   WHERE gs.user_uuid = $1 AND gs.start_time >= $2
                   GROUP BY gs.repository_url, gs.repository_type""",
                user_uuid, datetime.now() - timedelta(days=days)
            )
            
            # 代码变更统计
            code_stats = await conn.fetchrow(
                """SELECT COUNT(*) as total_changes,
                          SUM(lines_added) as total_lines_added,
                          SUM(lines_deleted) as total_lines_deleted
                   FROM code_changes cc
                   JOIN git_sessions gs ON cc.session_id = gs.session_id
                   WHERE gs.user_uuid = $1 AND cc.change_timestamp >= $2""",
                user_uuid, datetime.now() - timedelta(days=days)
            )
            
            return {
                'user_uuid': user_uuid,
                'analysis_period_days': days,
                'usage_stats': [dict(row) for row in usage_stats],
                'git_stats': [dict(row) for row in git_stats],
                'code_stats': dict(code_stats) if code_stats else {},
                'generated_at': datetime.now().isoformat()
            }
            
        finally:
            await conn.close()
    
    async def get_team_analytics(self, department: str = None, days: int = 30) -> Dict[str, Any]:
        """获取团队分析数据"""
        conn = await self.db.get_connection()
        try:
            where_clause = "WHERE ul.timestamp >= $1"
            params = [datetime.now() - timedelta(days=days)]
            
            if department:
                where_clause += " AND u.department = $2"
                params.append(department)
            
            # 团队使用统计
            team_stats = await conn.fetch(f"""
                SELECT u.department, ul.tool_name, 
                       COUNT(*) as usage_count,
                       COUNT(DISTINCT u.uuid) as active_users
                FROM users u
                JOIN usage_logs ul ON u.uuid = ul.user_uuid
                {where_clause}
                GROUP BY u.department, ul.tool_name
                ORDER BY usage_count DESC
            """, *params)
            
            # 团队Git活动
            git_activity = await conn.fetch(f"""
                SELECT u.department, gs.repository_type,
                       COUNT(DISTINCT gs.session_id) as sessions,
                       COUNT(ca.commit_hash) as commits,
                       AVG(CASE WHEN ca.is_ai_assisted THEN 1.0 ELSE 0.0 END) as ai_assistance_rate
                FROM users u
                JOIN git_sessions gs ON u.uuid = gs.user_uuid
                LEFT JOIN commit_analysis ca ON gs.session_id = ca.session_id
                {where_clause.replace('ul.timestamp', 'gs.start_time')}
                GROUP BY u.department, gs.repository_type
            """, *params)
            
            return {
                'department': department or 'all',
                'analysis_period_days': days,
                'team_stats': [dict(row) for row in team_stats],
                'git_activity': [dict(row) for row in git_activity],
                'generated_at': datetime.now().isoformat()
            }
            
        finally:
            await conn.close()
    
    async def close(self):
        """关闭服务"""
        # 数据库连接会自动关闭，这里预留给其他清理工作
        pass 