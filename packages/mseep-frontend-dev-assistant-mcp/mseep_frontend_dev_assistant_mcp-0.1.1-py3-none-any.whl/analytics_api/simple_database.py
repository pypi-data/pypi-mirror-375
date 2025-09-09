"""
简化版数据库模块 - 使用SQLite，无需复杂配置
适合前端开发者本地测试使用
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from pathlib import Path

class SimpleDatabaseManager:
    def __init__(self, db_path: str = None):
        """初始化SQLite数据库"""
        if db_path is None:
            # 在用户主目录创建数据库文件
            data_dir = Path.home() / ".frontend-dev-assistant"
            data_dir.mkdir(exist_ok=True)
            db_path = data_dir / "mcp_analytics.db"
        
        self.db_path = str(db_path)
        self.init_database()
        print(f"📄 使用SQLite数据库: {self.db_path}")
    
    def get_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # 支持字典式访问
        return conn
    
    def init_database(self):
        """初始化数据库表结构"""
        conn = self.get_connection()
        try:
            # 创建用户表
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    uuid TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    name TEXT,
                    department TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建使用日志表
            conn.execute('''
                CREATE TABLE IF NOT EXISTS usage_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_uuid TEXT NOT NULL,
                    tool_name TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    arguments TEXT,
                    FOREIGN KEY (user_uuid) REFERENCES users(uuid)
                )
            ''')
            
            # 创建索引
            conn.execute('CREATE INDEX IF NOT EXISTS idx_usage_logs_user_uuid ON usage_logs(user_uuid)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_usage_logs_timestamp ON usage_logs(timestamp)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_usage_logs_tool_name ON usage_logs(tool_name)')
            
            conn.commit()
            print("✅ SQLite数据库表结构初始化完成")
            
        except Exception as e:
            print(f"❌ 数据库初始化失败: {e}")
            raise
        finally:
            conn.close()
    
    def register_user(self, uuid: str, email: str, name: str = None, department: str = None):
        """注册或更新用户"""
        conn = self.get_connection()
        try:
            # 检查用户是否存在
            cursor = conn.execute("SELECT uuid FROM users WHERE uuid = ?", (uuid,))
            existing = cursor.fetchone()
            
            if existing:
                # 更新用户信息
                conn.execute(
                    "UPDATE users SET email = ?, name = ?, department = ?, last_active = ? WHERE uuid = ?",
                    (email, name, department, datetime.now().isoformat(), uuid)
                )
                status = "updated"
            else:
                # 创建新用户
                conn.execute(
                    "INSERT INTO users (uuid, email, name, department, created_at, last_active) VALUES (?, ?, ?, ?, ?, ?)",
                    (uuid, email, name, department, datetime.now().isoformat(), datetime.now().isoformat())
                )
                status = "created"
            
            conn.commit()
            return {"status": status, "uuid": uuid}
                
        except Exception as e:
            raise Exception(f"用户注册失败: {str(e)}")
        finally:
            conn.close()
    
    def log_usage(self, user_uuid: str, tool_name: str, arguments: Dict[str, Any] = None):
        """记录使用日志"""
        conn = self.get_connection()
        try:
            # 验证用户存在
            cursor = conn.execute("SELECT uuid FROM users WHERE uuid = ?", (user_uuid,))
            user = cursor.fetchone()
            if not user:
                raise Exception("用户不存在")
            
            # 插入使用记录
            conn.execute(
                "INSERT INTO usage_logs (user_uuid, tool_name, timestamp, arguments) VALUES (?, ?, ?, ?)",
                (user_uuid, tool_name, datetime.now().isoformat(), 
                 json.dumps(arguments) if arguments else None)
            )
            
            # 更新用户最后活跃时间
            conn.execute(
                "UPDATE users SET last_active = ? WHERE uuid = ?",
                (datetime.now().isoformat(), user_uuid)
            )
            
            conn.commit()
            return {"status": "logged"}
            
        except Exception as e:
            raise Exception(f"记录使用日志失败: {str(e)}")
        finally:
            conn.close()
    
    def get_user_report(self, user_uuid: str, days: int = 30):
        """获取用户使用报告"""
        conn = self.get_connection()
        try:
            # 获取用户基本信息
            cursor = conn.execute("SELECT * FROM users WHERE uuid = ?", (user_uuid,))
            user = cursor.fetchone()
            if not user:
                raise Exception("用户不存在")
            
            # 计算时间范围
            start_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            # 总使用次数
            cursor = conn.execute(
                "SELECT COUNT(*) FROM usage_logs WHERE user_uuid = ? AND timestamp >= ?",
                (user_uuid, start_date)
            )
            total_usage = cursor.fetchone()[0]
            
            # 工具使用统计
            cursor = conn.execute(
                "SELECT tool_name, COUNT(*) as count FROM usage_logs WHERE user_uuid = ? AND timestamp >= ? GROUP BY tool_name ORDER BY count DESC",
                (user_uuid, start_date)
            )
            tool_stats = [{"tool": row["tool_name"], "count": row["count"]} for row in cursor.fetchall()]
            
            # 每日使用趋势
            cursor = conn.execute(
                "SELECT DATE(timestamp) as date, COUNT(*) as count FROM usage_logs WHERE user_uuid = ? AND timestamp >= ? GROUP BY DATE(timestamp) ORDER BY date",
                (user_uuid, start_date)
            )
            daily_usage = [{"date": row["date"], "count": row["count"]} for row in cursor.fetchall()]
            
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
                "tool_stats": tool_stats,
                "daily_usage": daily_usage
            }
            
        except Exception as e:
            raise Exception(f"获取用户报告失败: {str(e)}")
        finally:
            conn.close()

# 全局简化数据库管理器实例
simple_db_manager = SimpleDatabaseManager() 