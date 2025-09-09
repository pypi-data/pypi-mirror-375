#!/usr/bin/env python3
"""
MCP调用追踪中间件
自动记录所有MCP工具调用，无需手动调用track_usage
"""

import json
import time
import asyncio
import os
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
from functools import wraps

class MCPCallTracker:
    def __init__(self, data_dir: Optional[Path] = None):
        """初始化MCP调用追踪器"""
        if data_dir is None:
            # 使用与UsageTracker相同的数据目录策略
            data_dir = self._determine_data_directory()
        
        self.data_dir = data_dir
        self.data_dir.mkdir(exist_ok=True)
        self.calls_file = self.data_dir / "mcp_calls.json"
        self._init_calls_file()
    
    def _determine_data_directory(self) -> Path:
        """确定数据保存目录"""
        # 1. 环境变量
        env_data_dir = os.environ.get('FRONTEND_DEV_ASSISTANT_DATA_DIR')
        if env_data_dir:
            return Path(env_data_dir)
        
        # 2. 开发模式：项目目录
        current_file_path = Path(__file__).parent.parent
        project_data_dir = current_file_path / "data"
        
        if project_data_dir.exists():
            return project_data_dir
        
        # 3. 用户主目录
        return Path.home() / ".frontend-dev-assistant"
    
    def _init_calls_file(self):
        """初始化调用记录文件"""
        if not self.calls_file.exists():
            initial_data = {
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "version": "1.0.0",
                    "tracker_type": "automatic_mcp_calls"
                },
                "calls": [],
                "daily_stats": {},
                "tool_stats": {}
            }
            
            with open(self.calls_file, 'w', encoding='utf-8') as f:
                json.dump(initial_data, f, ensure_ascii=False, indent=2)
    
    def _load_calls_data(self) -> Dict[str, Any]:
        """加载调用数据"""
        try:
            with open(self.calls_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self._init_calls_file()
            return self._load_calls_data()
    
    def _save_calls_data(self, data: Dict[str, Any]):
        """保存调用数据"""
        try:
            with open(self.calls_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 保存MCP调用数据失败: {e}")
    
    async def record_call(
        self, 
        tool_name: str, 
        arguments: Optional[Dict] = None,
        execution_time: float = 0,
        success: bool = True,
        error_message: Optional[str] = None,
        result_size: int = 0
    ):
        """记录MCP工具调用"""
        try:
            data = self._load_calls_data()
            timestamp = datetime.now().isoformat()
            today = datetime.now().strftime('%Y-%m-%d')
            hour = datetime.now().hour
            
            # 创建调用记录
            call_record = {
                "id": f"{int(time.time() * 1000)}_{tool_name}",  # 简单的ID生成
                "tool_name": tool_name,
                "timestamp": timestamp,
                "date": today,
                "hour": hour,
                "arguments": arguments or {},
                "execution_time_ms": round(execution_time * 1000, 2),
                "success": success,
                "error_message": error_message,
                "result_size_bytes": result_size,
                "user_agent": "cursor-mcp"  # 可以后续优化识别调用来源
            }
            
            # 添加到调用列表
            data["calls"].append(call_record)
            
            # 更新每日统计
            if today not in data["daily_stats"]:
                data["daily_stats"][today] = {
                    "total_calls": 0,
                    "successful_calls": 0,
                    "failed_calls": 0,
                    "total_execution_time_ms": 0,
                    "avg_execution_time_ms": 0,
                    "tool_breakdown": {},
                    "hourly_distribution": {str(h): 0 for h in range(24)}
                }
            
            daily_stat = data["daily_stats"][today]
            daily_stat["total_calls"] += 1
            daily_stat["total_execution_time_ms"] += call_record["execution_time_ms"]
            daily_stat["avg_execution_time_ms"] = daily_stat["total_execution_time_ms"] / daily_stat["total_calls"]
            daily_stat["hourly_distribution"][str(hour)] += 1
            
            if success:
                daily_stat["successful_calls"] += 1
            else:
                daily_stat["failed_calls"] += 1
            
            if tool_name not in daily_stat["tool_breakdown"]:
                daily_stat["tool_breakdown"][tool_name] = 0
            daily_stat["tool_breakdown"][tool_name] += 1
            
            # 更新工具统计
            if tool_name not in data["tool_stats"]:
                data["tool_stats"][tool_name] = {
                    "total_calls": 0,
                    "successful_calls": 0,
                    "failed_calls": 0,
                    "first_used": timestamp,
                    "last_used": timestamp,
                    "avg_execution_time_ms": 0,
                    "total_execution_time_ms": 0,
                    "common_arguments": {},
                    "error_patterns": []
                }
            
            tool_stat = data["tool_stats"][tool_name]
            tool_stat["total_calls"] += 1
            tool_stat["last_used"] = timestamp
            tool_stat["total_execution_time_ms"] += call_record["execution_time_ms"]
            tool_stat["avg_execution_time_ms"] = tool_stat["total_execution_time_ms"] / tool_stat["total_calls"]
            
            if success:
                tool_stat["successful_calls"] += 1
            else:
                tool_stat["failed_calls"] += 1
                if error_message and len(tool_stat["error_patterns"]) < 10:  # 限制错误记录数量
                    tool_stat["error_patterns"].append({
                        "error": error_message,
                        "timestamp": timestamp,
                        "arguments": arguments
                    })
            
            # 分析常用参数（只保留前5个最常用的）
            if arguments:
                for key, value in arguments.items():
                    if key not in tool_stat["common_arguments"]:
                        tool_stat["common_arguments"][key] = {}
                    
                    value_str = str(value)[:50]  # 限制长度
                    if value_str not in tool_stat["common_arguments"][key]:
                        tool_stat["common_arguments"][key][value_str] = 0
                    tool_stat["common_arguments"][key][value_str] += 1
                    
                    # 只保留使用频率最高的5个值
                    if len(tool_stat["common_arguments"][key]) > 5:
                        sorted_items = sorted(
                            tool_stat["common_arguments"][key].items(), 
                            key=lambda x: x[1], 
                            reverse=True
                        )[:5]
                        tool_stat["common_arguments"][key] = dict(sorted_items)
            
            # 限制调用记录数量，避免文件过大
            if len(data["calls"]) > 1000:
                # 保留最近的1000条记录
                data["calls"] = data["calls"][-1000:]
            
            # 保存数据
            self._save_calls_data(data)
            
        except Exception as e:
            # 静默失败，不影响MCP工具正常使用
            print(f"⚠️ 记录MCP调用失败: {e}")
    
    def create_call_wrapper(self):
        """创建调用包装器装饰器"""
        def call_wrapper(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                success = True
                error_message = None
                result = None
                result_size = 0
                
                try:
                    result = await func(*args, **kwargs)
                    
                    # 估算结果大小
                    if result:
                        try:
                            result_size = len(str(result).encode('utf-8'))
                        except:
                            result_size = 0
                    
                    return result
                    
                except Exception as e:
                    success = False
                    error_message = str(e)
                    raise
                    
                finally:
                    execution_time = time.time() - start_time
                    
                    # 尝试从函数调用中提取工具名称和参数
                    tool_name = "unknown"
                    arguments = {}
                    
                    # 如果是MCP工具调用，尝试提取信息
                    if len(args) >= 2 and isinstance(args[1], str):
                        tool_name = args[1]  # 第二个参数通常是工具名称
                    
                    if len(args) >= 3 and isinstance(args[2], dict):
                        arguments = args[2]  # 第三个参数通常是参数字典
                    
                    # 异步记录调用
                    asyncio.create_task(self.record_call(
                        tool_name=tool_name,
                        arguments=arguments,
                        execution_time=execution_time,
                        success=success,
                        error_message=error_message,
                        result_size=result_size
                    ))
            
            return wrapper
        return call_wrapper
    
    def get_stats_summary(self, days: int = 7) -> Dict[str, Any]:
        """获取统计摘要"""
        try:
            data = self._load_calls_data()
            
            # 计算时间范围
            from datetime import datetime, timedelta
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # 过滤最近N天的数据
            recent_calls = [
                call for call in data["calls"]
                if datetime.fromisoformat(call["timestamp"]) >= start_date
            ]
            
            if not recent_calls:
                return {"message": f"最近{days}天没有MCP调用记录"}
            
            # 基础统计
            total_calls = len(recent_calls)
            successful_calls = sum(1 for call in recent_calls if call["success"])
            failed_calls = total_calls - successful_calls
            avg_execution_time = sum(call["execution_time_ms"] for call in recent_calls) / total_calls
            
            # 工具使用排行
            tool_usage = {}
            for call in recent_calls:
                tool_name = call["tool_name"]
                if tool_name not in tool_usage:
                    tool_usage[tool_name] = 0
                tool_usage[tool_name] += 1
            
            top_tools = sorted(tool_usage.items(), key=lambda x: x[1], reverse=True)[:5]
            
            # 时间分布
            hourly_calls = {}
            for call in recent_calls:
                hour = call["hour"]
                if hour not in hourly_calls:
                    hourly_calls[hour] = 0
                hourly_calls[hour] += 1
            
            peak_hour = max(hourly_calls.items(), key=lambda x: x[1]) if hourly_calls else (0, 0)
            
            return {
                "time_range": f"最近{days}天",
                "total_calls": total_calls,
                "success_rate": f"{successful_calls/total_calls*100:.1f}%" if total_calls > 0 else "0%",
                "failed_calls": failed_calls,
                "avg_execution_time_ms": round(avg_execution_time, 2),
                "top_tools": top_tools,
                "peak_hour": f"{peak_hour[0]}点 ({peak_hour[1]}次调用)",
                "daily_average": round(total_calls / days, 1)
            }
            
        except Exception as e:
            return {"error": f"获取统计数据失败: {e}"}
    
    def detailed_context_test(self, tool_name: str, params: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        详细测试：记录MCP调用时能获取到的所有信息
        用于分析MCP工具的上下文获取能力
        """
        timestamp = datetime.now().isoformat()
        
        # 收集所有可能的上下文信息
        context_data = {
            "timestamp": timestamp,
            "tool_name": tool_name,
            "received_params": params,
            "additional_kwargs": kwargs,
            
            # 环境信息
            "environment": {
                "cwd": os.getcwd(),
                "user": os.getenv("USER") or os.getenv("USERNAME"),
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
                "platform": sys.platform,
            },
            
            # 进程信息
            "process_info": {
                "pid": os.getpid(),
                "parent_pid": os.getppid() if hasattr(os, 'getppid') else None,
            },
            
            # 检查是否有任何隐藏的上下文
            "hidden_context": {
                "globals_keys": list(globals().keys()),
                "locals_keys": list(locals().keys()) if 'locals' in dir() else [],
                "env_vars": {k: v for k, v in os.environ.items() if 'CURSOR' in k or 'CLAUDE' in k or 'MCP' in k},
            },
            
            # 检查调用栈
            "call_stack_info": self._get_call_stack_info(),
            
            # 参数详细分析
            "params_analysis": {
                "param_count": len(params),
                "param_types": {k: type(v).__name__ for k, v in params.items()},
                "param_sizes": {k: len(str(v)) for k, v in params.items()},
                "has_long_text": any(len(str(v)) > 100 for v in params.values()),
            }
        }
        
        # 保存到专门的测试文件
        test_file = self.data_dir / "context_test_log.jsonl"
        try:
            with open(test_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(context_data, ensure_ascii=False) + "\n")
        except Exception as e:
            logging.error(f"保存上下文测试数据失败: {e}")
        
        # 同时打印到控制台（如果有的话）
        print("="*50)
        print("MCP上下文测试数据:")
        print(json.dumps(context_data, indent=2, ensure_ascii=False))
        print("="*50)
        
        return context_data
    
    def _get_call_stack_info(self) -> Dict[str, Any]:
        """获取调用栈信息"""
        import inspect
        
        stack_info = {
            "stack_depth": 0,
            "functions": [],
            "files": []
        }
        
        try:
            stack = inspect.stack()
            stack_info["stack_depth"] = len(stack)
            
            for frame_info in stack[:10]:  # 只取前10层
                stack_info["functions"].append({
                    "function": frame_info.function,
                    "filename": os.path.basename(frame_info.filename),
                    "lineno": frame_info.lineno,
                })
                
                if frame_info.filename not in stack_info["files"]:
                    stack_info["files"].append(os.path.basename(frame_info.filename))
                    
        except Exception as e:
            stack_info["error"] = str(e)
            
        return stack_info

# 创建全局追踪器实例
call_tracker = MCPCallTracker()

def track_mcp_calls(func):
    """MCP调用追踪装饰器"""
    return call_tracker.create_call_wrapper()(func) 