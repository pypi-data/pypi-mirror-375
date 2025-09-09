"""
数据库连接和操作模块
"""

import asyncpg
import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from pathlib import Path

class DatabaseManager:
    def __init__(self, database_url: str = None):
        self.database_url = database_url or os.getenv(
            'DATABASE_URL', 
            'postgresql://mcp_user:mcp_password@localhost:5432/mcp_analytics'
        )
    
    async def get_connection(self):
        """获取数据库连接"""
        return await asyncpg.connect(self.database_url)
    
    async def init_database(self):
        """初始化数据库表结构"""
        conn = await self.get_connection()
        try:
            # 创建用户表
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    uuid VARCHAR(36) PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    name VARCHAR(255),
                    department VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建使用日志表
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS usage_logs (
                    id SERIAL PRIMARY KEY,
                    user_uuid VARCHAR(36) REFERENCES users(uuid),
                    tool_name VARCHAR(100) NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    arguments JSONB
                )
            ''')
            
            # 创建Git会话表
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS git_sessions (
                    session_id VARCHAR(36) PRIMARY KEY,
                    user_uuid VARCHAR(36) REFERENCES users(uuid),
                    repository_url TEXT NOT NULL,
                    repository_type VARCHAR(50) NOT NULL,
                    branch_name VARCHAR(100),
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            ''')
            
            # 创建代码变更表
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS code_changes (
                    id SERIAL PRIMARY KEY,
                    session_id VARCHAR(36) REFERENCES git_sessions(session_id),
                    file_path TEXT NOT NULL,
                    lines_added INTEGER DEFAULT 0,
                    lines_deleted INTEGER DEFAULT 0,
                    complexity_change INTEGER DEFAULT 0,
                    functions_added INTEGER DEFAULT 0,
                    has_type_annotations BOOLEAN DEFAULT FALSE,
                    has_error_handling BOOLEAN DEFAULT FALSE,
                    change_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建提交分析表
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS commit_analysis (
                    id SERIAL PRIMARY KEY,
                    commit_hash VARCHAR(40) UNIQUE NOT NULL,
                    session_id VARCHAR(36) REFERENCES git_sessions(session_id),
                    author_name VARCHAR(255) NOT NULL,
                    author_email VARCHAR(255) NOT NULL,
                    commit_message TEXT NOT NULL,
                    is_ai_assisted BOOLEAN DEFAULT FALSE,
                    files_changed INTEGER DEFAULT 0,
                    lines_added INTEGER DEFAULT 0,
                    lines_deleted INTEGER DEFAULT 0,
                    commit_date TIMESTAMP NOT NULL
                )
            ''')
            
            # 创建索引
            await conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_usage_logs_user_uuid 
                ON usage_logs(user_uuid)
            ''')
            
            await conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_usage_logs_timestamp 
                ON usage_logs(timestamp)
            ''')
            
            await conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_usage_logs_tool_name 
                ON usage_logs(tool_name)
            ''')
            
            await conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_git_sessions_user_uuid 
                ON git_sessions(user_uuid)
            ''')
            
            await conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_code_changes_session_id 
                ON code_changes(session_id)
            ''')
            
            await conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_commit_analysis_session_id 
                ON commit_analysis(session_id)
            ''')
            
            print("✅ 数据库表结构初始化完成")
            
        except Exception as e:
            print(f"❌ 数据库初始化失败: {e}")
            raise
        finally:
            await conn.close()
    
    async def register_user(self, uuid: str, email: str, name: str = None, department: str = None):
        """注册或更新用户"""
        conn = await self.get_connection()
        try:
            # 检查用户是否存在
            existing = await conn.fetchrow(
                "SELECT uuid FROM users WHERE uuid = $1", uuid
            )
            
            if existing:
                # 更新用户信息
                await conn.execute(
                    """UPDATE users 
                       SET email = $1, name = $2, department = $3, last_active = $4 
                       WHERE uuid = $5""",
                    email, name, department, datetime.now(), uuid
                )
                return {"status": "updated", "uuid": uuid}
            else:
                # 创建新用户
                await conn.execute(
                    """INSERT INTO users (uuid, email, name, department, created_at, last_active) 
                       VALUES ($1, $2, $3, $4, $5, $6)""",
                    uuid, email, name, department, datetime.now(), datetime.now()
                )
                return {"status": "created", "uuid": uuid}
                
        except Exception as e:
            raise Exception(f"用户注册失败: {str(e)}")
        finally:
            await conn.close()
    
    async def log_usage(self, user_uuid: str, tool_name: str, arguments: Dict[str, Any] = None):
        """记录使用日志"""
        conn = await self.get_connection()
        try:
            # 验证用户存在
            user = await conn.fetchrow(
                "SELECT uuid FROM users WHERE uuid = $1", user_uuid
            )
            if not user:
                raise Exception("用户不存在")
            
            # 插入使用记录
            await conn.execute(
                """INSERT INTO usage_logs (user_uuid, tool_name, timestamp, arguments) 
                   VALUES ($1, $2, $3, $4)""",
                user_uuid, tool_name, datetime.now(), 
                json.dumps(arguments) if arguments else None
            )
            
            # 更新用户最后活跃时间
            await conn.execute(
                "UPDATE users SET last_active = $1 WHERE uuid = $2",
                datetime.now(), user_uuid
            )
            
            return {"status": "logged"}
            
        except Exception as e:
            raise Exception(f"记录使用日志失败: {str(e)}")
        finally:
            await conn.close()
    
    async def get_user_report(self, user_uuid: str, days: int = 30):
        """获取用户使用报告"""
        conn = await self.get_connection()
        try:
            # 获取用户基本信息
            user = await conn.fetchrow(
                "SELECT * FROM users WHERE uuid = $1", user_uuid
            )
            if not user:
                raise Exception("用户不存在")
            
            # 计算时间范围
            start_date = datetime.now() - timedelta(days=days)
            
            # 总使用次数
            total_usage = await conn.fetchval(
                """SELECT COUNT(*) FROM usage_logs 
                   WHERE user_uuid = $1 AND timestamp >= $2""",
                user_uuid, start_date
            )
            
            # 工具使用统计
            tool_stats = await conn.fetch(
                """SELECT tool_name, COUNT(*) as count 
                   FROM usage_logs 
                   WHERE user_uuid = $1 AND timestamp >= $2 
                   GROUP BY tool_name 
                   ORDER BY count DESC""",
                user_uuid, start_date
            )
            
            # 每日使用趋势
            daily_usage = await conn.fetch(
                """SELECT DATE(timestamp) as date, COUNT(*) as count 
                   FROM usage_logs 
                   WHERE user_uuid = $1 AND timestamp >= $2 
                   GROUP BY DATE(timestamp) 
                   ORDER BY date""",
                user_uuid, start_date
            )
            
            return {
                "user": {
                    "uuid": user["uuid"],
                    "email": user["email"],
                    "name": user["name"],
                    "department": user["department"]
                },
                "period": f"{days} days",
                "summary": {
                    "total_usage": total_usage,
                    "tools_count": len(tool_stats),
                    "avg_daily": round(total_usage / days, 1) if days > 0 else 0
                },
                "tool_stats": [{"tool": row["tool_name"], "count": row["count"]} 
                              for row in tool_stats],
                "daily_usage": [{"date": str(row["date"]), "count": row["count"]} 
                               for row in daily_usage]
            }
            
        except Exception as e:
            raise Exception(f"获取用户报告失败: {str(e)}")
        finally:
            await conn.close()

# 全局数据库管理器实例
db_manager = DatabaseManager()