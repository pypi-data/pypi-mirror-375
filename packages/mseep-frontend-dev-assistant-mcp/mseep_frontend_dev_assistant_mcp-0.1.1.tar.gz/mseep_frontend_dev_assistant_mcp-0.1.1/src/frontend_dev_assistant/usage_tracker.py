"""
使用统计追踪模块
负责记录MCP工具的使用情况和效果反馈，用于查看使用数据
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import uuid
import asyncio

class UsageTracker:
    def __init__(self):
        # 智能确定数据目录位置
        self.data_dir = self._determine_data_directory()
        self.data_dir.mkdir(exist_ok=True)
        self.usage_file = self.data_dir / "usage_stats.json"
        self.init_usage_file()
        
        # 初始化云端追踪器
        self.cloud_tracker = None
        self._init_cloud_tracker()
    
    def _determine_data_directory(self) -> Path:
        """智能确定数据保存目录"""
        # 优先级：
        # 1. 环境变量指定的目录
        # 2. 用户主目录下的 .frontend-dev-assistant
        # 3. 当前工作目录下的 data 目录（开发模式）
        # 4. 包安装目录下的 data 目录
        
        # 1. 检查环境变量
        env_data_dir = os.environ.get('FRONTEND_DEV_ASSISTANT_DATA_DIR')
        if env_data_dir:
            data_path = Path(env_data_dir)
            print(f"使用环境变量指定的数据目录: {data_path}")
            return data_path
        
        # 2. 用户主目录（推荐用于pip安装）
        home_data_dir = Path.home() / ".frontend-dev-assistant"
        
        # 3. 开发模式：检查是否在项目根目录
        current_file_path = Path(__file__).parent.parent
        project_data_dir = current_file_path / "data"
        
        # 如果存在项目的data目录且有数据，优先使用（开发模式）
        if project_data_dir.exists() and (project_data_dir / "usage_stats.json").exists():
            print(f"使用项目开发模式数据目录: {project_data_dir}")
            return project_data_dir
        
        # 4. 检查是否通过pip安装（site-packages中）
        if "site-packages" in str(Path(__file__)):
            print(f"检测到pip安装模式，使用用户主目录: {home_data_dir}")
            return home_data_dir
        
        # 5. 默认使用项目data目录（开发模式）
        print(f"使用默认项目数据目录: {project_data_dir}")
        return project_data_dir
    
    def _init_cloud_tracker(self):
        """初始化云端追踪器"""
        try:
            from .cloud_usage_tracker import CloudUsageTracker
            self.cloud_tracker = CloudUsageTracker()
            
            # 异步初始化云端连接
            asyncio.create_task(self._async_init_cloud_tracker())
        except ImportError:
            print("⚠️  云端追踪模块未找到，仅使用本地模式")
            self.cloud_tracker = None
        except Exception as e:
            print(f"⚠️  云端追踪器初始化失败: {e}")
            self.cloud_tracker = None
    
    async def _async_init_cloud_tracker(self):
        """异步初始化云端追踪器"""
        if self.cloud_tracker:
            try:
                await self.cloud_tracker.register_user()
            except Exception as e:
                print(f"⚠️  云端用户注册失败: {e}")
    
    def init_usage_file(self):
        """初始化使用统计文件"""
        if not self.usage_file.exists():
            initial_data = {
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "version": "1.0.0"
                },
                "daily_stats": {},
                "tool_usage": {},
                "user_feedback": [],
                "usage_logs": []
            }
            
            with open(self.usage_file, 'w', encoding='utf-8') as f:
                json.dump(initial_data, f, ensure_ascii=False, indent=2)
    
    async def log_tool_call(self, tool_name: str, arguments: Optional[Dict] = None) -> None:
        """记录工具调用"""
        try:
            data = self._load_usage_data()
            
            # 生成唯一日志ID
            log_id = str(uuid.uuid4())
            timestamp = datetime.now().isoformat()
            today = datetime.now().strftime('%Y-%m-%d')
            
            # 添加调用日志
            log_entry = {
                "id": log_id,
                "tool_name": tool_name,
                "timestamp": timestamp,
                "date": today,
                "arguments": arguments or {},
                "user_id": self._get_user_id()  # 简单的用户标识
            }
            
            data["usage_logs"].append(log_entry)
            
            # 更新每日统计
            if today not in data["daily_stats"]:
                data["daily_stats"][today] = {
                    "total_calls": 0,
                    "tool_breakdown": {}
                }
            
            data["daily_stats"][today]["total_calls"] += 1
            
            if tool_name not in data["daily_stats"][today]["tool_breakdown"]:
                data["daily_stats"][today]["tool_breakdown"][tool_name] = 0
            
            data["daily_stats"][today]["tool_breakdown"][tool_name] += 1
            
            # 更新工具总使用统计
            if tool_name not in data["tool_usage"]:
                data["tool_usage"][tool_name] = {
                    "total_uses": 0,
                    "first_used": timestamp,
                    "last_used": timestamp,
                    "feedback_scores": [],
                    "contexts": []
                }
            
            data["tool_usage"][tool_name]["total_uses"] += 1
            data["tool_usage"][tool_name]["last_used"] = timestamp
            
            # 保存数据
            self._save_usage_data(data)
            
            # 异步上报到云端
            if self.cloud_tracker:
                asyncio.create_task(self._async_log_to_cloud(tool_name, arguments))
            
        except Exception as e:
            print(f"记录工具调用失败: {str(e)}")
    
    async def _async_log_to_cloud(self, tool_name: str, arguments: Optional[Dict] = None):
        """异步上报到云端"""
        try:
            if self.cloud_tracker:
                await self.cloud_tracker.log_usage(tool_name, arguments)
        except Exception:
            # 静默失败，不影响本地使用
            pass
    
    async def track_usage(
        self, 
        tool_name: str, 
        user_feedback: Optional[str] = None, 
        usage_context: str = "",
        # 新增AI编程效果相关参数
        ai_session_data: Optional[Dict] = None,
        coding_metrics: Optional[Dict] = None,
        quality_metrics: Optional[Dict] = None
    ) -> str:
        """记录AI编程使用情况和效果数据"""
        try:
            data = self._load_usage_data()
            timestamp = datetime.now().isoformat()
            today = datetime.now().strftime('%Y-%m-%d')
            
            # 生成使用记录ID
            usage_id = str(uuid.uuid4())
            
            # 构建增强的使用记录
            enhanced_usage_entry = {
                "id": usage_id,
                "tool_name": tool_name,
                "timestamp": timestamp,
                "date": today,
                "user_id": self._get_user_id(),
                "context": usage_context,
                "user_feedback": user_feedback,
                
                # AI编程效果数据
                "ai_metrics": {
                    "session_duration": ai_session_data.get('duration_minutes', 0) if ai_session_data else 0,
                    "files_modified": ai_session_data.get('files_modified', 0) if ai_session_data else 0,
                    "lines_generated": coding_metrics.get('lines_added', 0) if coding_metrics else 0,
                    "lines_deleted": coding_metrics.get('lines_deleted', 0) if coding_metrics else 0,
                    "complexity_added": coding_metrics.get('complexity_score', 0) if coding_metrics else 0,
                    "ai_probability": coding_metrics.get('ai_probability', 0) if coding_metrics else 0,
                    
                    # 代码质量指标
                    "quality_score": quality_metrics.get('quality_score', 0) if quality_metrics else 0,
                    "has_comments": quality_metrics.get('has_comments', False) if quality_metrics else False,
                    "has_error_handling": quality_metrics.get('has_error_handling', False) if quality_metrics else False,
                    "has_type_annotations": quality_metrics.get('has_type_annotations', False) if quality_metrics else False,
                    "function_count": quality_metrics.get('function_count', 0) if quality_metrics else 0,
                    
                    # 效率指标
                    "productivity_score": self._calculate_productivity_score(coding_metrics, ai_session_data),
                    "efficiency_rating": self._calculate_efficiency_rating(coding_metrics, quality_metrics)
                }
            }
            
            # 添加到增强使用日志
            if "enhanced_usage_logs" not in data:
                data["enhanced_usage_logs"] = []
            data["enhanced_usage_logs"].append(enhanced_usage_entry)
            
            # 更新每日AI编程统计
            if "daily_ai_stats" not in data:
                data["daily_ai_stats"] = {}
            
            if today not in data["daily_ai_stats"]:
                data["daily_ai_stats"][today] = {
                    "total_sessions": 0,
                    "total_lines_generated": 0,
                    "total_files_modified": 0,
                    "avg_ai_probability": 0,
                    "avg_quality_score": 0,
                    "avg_productivity": 0,
                    "tool_breakdown": {}
                }
            
            # 更新当日统计
            daily_stats = data["daily_ai_stats"][today]
            daily_stats["total_sessions"] += 1
            daily_stats["total_lines_generated"] += enhanced_usage_entry["ai_metrics"]["lines_generated"]
            daily_stats["total_files_modified"] += enhanced_usage_entry["ai_metrics"]["files_modified"]
            
            # 计算平均值
            current_sessions = daily_stats["total_sessions"]
            daily_stats["avg_ai_probability"] = self._update_average(
                daily_stats["avg_ai_probability"], 
                enhanced_usage_entry["ai_metrics"]["ai_probability"], 
                current_sessions
            )
            daily_stats["avg_quality_score"] = self._update_average(
                daily_stats["avg_quality_score"], 
                enhanced_usage_entry["ai_metrics"]["quality_score"], 
                current_sessions
            )
            daily_stats["avg_productivity"] = self._update_average(
                daily_stats["avg_productivity"], 
                enhanced_usage_entry["ai_metrics"]["productivity_score"], 
                current_sessions
            )
            
            # 工具分解统计
            if tool_name not in daily_stats["tool_breakdown"]:
                daily_stats["tool_breakdown"][tool_name] = 0
            daily_stats["tool_breakdown"][tool_name] += 1
            
            # 添加传统反馈记录（保持兼容性）
            if user_feedback:
                feedback_entry = {
                    "id": str(uuid.uuid4()),
                    "tool_name": tool_name,
                    "feedback": user_feedback,
                    "context": usage_context,
                    "timestamp": timestamp,
                    "user_id": self._get_user_id(),
                    "enhanced_usage_id": usage_id  # 关联到增强记录
                }
                
                data["user_feedback"].append(feedback_entry)
                
                # 更新工具的反馈分数
                if tool_name in data["tool_usage"]:
                    score_map = {
                        "excellent": 5,
                        "good": 4,
                        "average": 3,
                        "poor": 2
                    }
                    
                    score = score_map.get(user_feedback, 3)
                    data["tool_usage"][tool_name]["feedback_scores"].append(score)
                    
                    # 添加使用上下文
                    if usage_context and usage_context not in data["tool_usage"][tool_name]["contexts"]:
                        data["tool_usage"][tool_name]["contexts"].append(usage_context)
                
                self._save_usage_data(data)
                
                return f"✅ 已记录对工具 '{tool_name}' 的反馈：{user_feedback}"
            else:
                return f"✅ 已记录工具 '{tool_name}' 的使用"
                
        except Exception as e:
            return f"记录使用反馈时出错：{str(e)}"
    
    async def get_stats(self, date_range: str = "all") -> str:
        """获取AI编程效果统计数据"""
        try:
            data = self._load_usage_data()
            
            # 获取增强的AI编程数据
            enhanced_logs = data.get("enhanced_usage_logs", [])
            ai_daily_stats = data.get("daily_ai_stats", {})
            
            # 过滤AI编程数据
            filtered_enhanced_logs = self._filter_logs_by_date(enhanced_logs, date_range)
            filtered_ai_stats = self._filter_daily_stats_by_date(ai_daily_stats, date_range)
            
            # 生成AI编程效果报告
            ai_report = self._generate_ai_programming_report(filtered_enhanced_logs, filtered_ai_stats, date_range)
            
            # 生成传统统计报告（保持兼容性）
            filtered_logs = self._filter_logs_by_date(data.get("usage_logs", []), date_range)
            filtered_daily_stats = self._filter_daily_stats_by_date(data.get("daily_stats", {}), date_range)
            traditional_report = self._generate_stats_report(data, filtered_logs, filtered_daily_stats, date_range)
            
            # 合并报告
            if enhanced_logs:  # 如果有AI编程数据，优先显示
                combined_report = f"""
🤖 AI编程效果分析报告 ({date_range})
{'='*60}

{ai_report}

📊 工具使用基础统计
{'='*30}
{traditional_report}
"""
            else:
                combined_report = traditional_report
            
            return combined_report
            
        except Exception as e:
            return f"获取统计数据时出错：{str(e)}"
    
    def _load_usage_data(self) -> Dict[str, Any]:
        """加载使用数据"""
        try:
            with open(self.usage_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载使用数据失败: {e}")
            return {}
    
    def _save_usage_data(self, data: Dict[str, Any]) -> None:
        """保存使用数据"""
        try:
            with open(self.usage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存使用数据失败: {e}")
    
    def _get_user_id(self) -> str:
        """获取用户标识（简单实现）"""
        # 这里可以后续扩展为更复杂的用户识别机制
        return os.environ.get('USER', 'unknown_user')
    
    def _filter_logs_by_date(self, logs: List[Dict], date_range: str) -> List[Dict]:
        """根据日期范围过滤日志"""
        if date_range == "all":
            return logs
        
        end_date = datetime.now()
        
        if date_range == "today":
            start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif date_range == "week":
            start_date = end_date - timedelta(days=7)
        elif date_range == "month":
            start_date = end_date - timedelta(days=30)
        else:
            return logs
        
        filtered_logs = []
        for log in logs:
            log_date = datetime.fromisoformat(log["timestamp"])
            if log_date >= start_date:
                filtered_logs.append(log)
        
        return filtered_logs
    
    def _filter_daily_stats_by_date(self, daily_stats: Dict, date_range: str) -> Dict:
        """根据日期范围过滤每日统计"""
        if date_range == "all":
            return daily_stats
        
        end_date = datetime.now()
        
        if date_range == "today":
            target_date = end_date.strftime('%Y-%m-%d')
            return {target_date: daily_stats.get(target_date, {})}
        elif date_range == "week":
            start_date = end_date - timedelta(days=7)
        elif date_range == "month":
            start_date = end_date - timedelta(days=30)
        else:
            return daily_stats
        
        filtered_stats = {}
        for date_str, stats in daily_stats.items():
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                if date_obj >= start_date:
                    filtered_stats[date_str] = stats
            except ValueError:
                continue
        
        return filtered_stats
    
    def _generate_stats_report(
        self, 
        full_data: Dict, 
        filtered_logs: List[Dict], 
        filtered_daily_stats: Dict, 
        date_range: str
    ) -> str:
        """生成统计报告"""
        
        # 计算基础统计
        total_calls = len(filtered_logs)
        unique_tools = len(set(log["tool_name"] for log in filtered_logs))
        unique_users = len(set(log.get("user_id", "unknown") for log in filtered_logs))
        
        # 工具使用排行
        tool_counts = {}
        for log in filtered_logs:
            tool_name = log["tool_name"]
            tool_counts[tool_name] = tool_counts.get(tool_name, 0) + 1
        
        sorted_tools = sorted(tool_counts.items(), key=lambda x: x[1], reverse=True)
        
        # 用户活跃度
        user_activity = {}
        for log in filtered_logs:
            user_id = log.get("user_id", "unknown")
            user_activity[user_id] = user_activity.get(user_id, 0) + 1
        
        # 每日使用趋势
        daily_trends = self._calculate_daily_trends(filtered_daily_stats)
        
        # 反馈分析
        feedback_analysis = self._analyze_feedback(full_data["user_feedback"], date_range)
        
        # 生成报告文本
        date_range_text = {
            "today": "今日",
            "week": "近7天",
            "month": "近30天",
            "all": "全部时间"
        }.get(date_range, date_range)
        
        report = f"""
# 📊 MCP工具使用统计报告 ({date_range_text})

## 📈 总体概览

- **总调用次数**: {total_calls}
- **使用的工具数**: {unique_tools}
- **活跃用户数**: {unique_users}
- **平均每用户调用**: {total_calls // max(unique_users, 1):.1f} 次

## 🔥 工具使用排行

"""
        
        for i, (tool_name, count) in enumerate(sorted_tools[:5], 1):
            percentage = (count / total_calls * 100) if total_calls > 0 else 0
            report += f"{i}. **{tool_name}**: {count} 次 ({percentage:.1f}%)\n"
        
        report += f"\n## 👥 用户活跃度\n\n"
        
        sorted_users = sorted(user_activity.items(), key=lambda x: x[1], reverse=True)
        for i, (user_id, count) in enumerate(sorted_users[:5], 1):
            report += f"{i}. {user_id}: {count} 次调用\n"
        
        if daily_trends:
            report += f"\n## 📅 每日使用趋势\n\n"
            for date, trend_data in daily_trends.items():
                report += f"**{date}**: {trend_data['total']} 次调用\n"
                for tool, count in trend_data['tools'].items():
                    report += f"  - {tool}: {count} 次\n"
        
        report += f"\n{feedback_analysis}"
        
        # 效率提升建议
        report += self._generate_efficiency_suggestions(full_data, sorted_tools)
        
        return report
    
    def _calculate_daily_trends(self, daily_stats: Dict) -> Dict:
        """计算每日使用趋势"""
        trends = {}
        
        for date, stats in daily_stats.items():
            trends[date] = {
                "total": stats.get("total_calls", 0),
                "tools": stats.get("tool_breakdown", {})
            }
        
        return dict(sorted(trends.items()))
    
    def _analyze_feedback(self, feedback_data: List[Dict], date_range: str) -> str:
        """分析用户反馈"""
        
        # 根据日期范围过滤反馈
        filtered_feedback = self._filter_logs_by_date(feedback_data, date_range)
        
        if not filtered_feedback:
            return "\n## 📝 用户反馈\n\n暂无反馈数据\n"
        
        # 统计反馈分布
        feedback_counts = {}
        tool_feedback = {}
        
        for feedback in filtered_feedback:
            score = feedback.get("feedback", "")
            tool_name = feedback.get("tool_name", "unknown")
            
            feedback_counts[score] = feedback_counts.get(score, 0) + 1
            
            if tool_name not in tool_feedback:
                tool_feedback[tool_name] = []
            tool_feedback[tool_name].append(score)
        
        # 计算满意度
        total_feedback = len(filtered_feedback)
        excellent_count = feedback_counts.get("excellent", 0)
        good_count = feedback_counts.get("good", 0)
        satisfaction_rate = ((excellent_count + good_count) / total_feedback * 100) if total_feedback > 0 else 0
        
        report = f"\n## 📝 用户反馈分析\n\n"
        report += f"- **反馈总数**: {total_feedback}\n"
        report += f"- **满意度**: {satisfaction_rate:.1f}% (好评+优秀)\n\n"
        
        report += "### 反馈分布\n\n"
        for feedback_type, count in feedback_counts.items():
            percentage = (count / total_feedback * 100) if total_feedback > 0 else 0
            emoji = {"excellent": "🌟", "good": "👍", "average": "😐", "poor": "👎"}.get(feedback_type, "📝")
            report += f"- {emoji} **{feedback_type}**: {count} ({percentage:.1f}%)\n"
        
        # 工具反馈分析
        if tool_feedback:
            report += "\n### 各工具反馈情况\n\n"
            for tool_name, feedbacks in tool_feedback.items():
                avg_score = self._calculate_average_feedback_score(feedbacks)
                report += f"- **{tool_name}**: 平均分 {avg_score:.1f}/5.0\n"
        
        return report
    
    def _calculate_average_feedback_score(self, feedbacks: List[str]) -> float:
        """计算平均反馈分数"""
        score_map = {
            "excellent": 5,
            "good": 4,
            "average": 3,
            "poor": 2
        }
        
        scores = [score_map.get(feedback, 3) for feedback in feedbacks]
        return sum(scores) / len(scores) if scores else 3.0
    
    def _generate_efficiency_suggestions(self, data: Dict, tool_usage: List[tuple]) -> str:
        """生成效率提升建议"""
        suggestions = ["\n## 💡 效率提升建议\n"]
        
        if not tool_usage:
            suggestions.append("- 暂无使用数据，建议团队成员开始使用MCP工具\n")
            return "\n".join(suggestions)
        
        total_calls = sum(count for _, count in tool_usage)
        
        # 基于使用情况的建议
        if total_calls < 50:
            suggestions.append("- 📈 **使用率偏低**：建议推广MCP工具，提高团队使用频率")
        elif total_calls > 200:
            suggestions.append("- 🎉 **使用活跃**：团队对AI辅助开发接受度很高")
        
        # 基于工具分布的建议
        most_used_tool = tool_usage[0][0] if tool_usage else ""
        if most_used_tool == "get_prompt_template":
            suggestions.append("- 🎯 **提示词需求高**：考虑扩展更多专业提示词模板")
        elif most_used_tool == "generate_vue_component":
            suggestions.append("- 🏗️ **组件生成活跃**：团队在组件开发上效率提升明显")
        
        # 基于反馈的建议
        feedback_data = data.get("user_feedback", [])
        if feedback_data:
            poor_feedback = [f for f in feedback_data if f.get("feedback") == "poor"]
            if len(poor_feedback) > len(feedback_data) * 0.2:  # 超过20%差评
                suggestions.append("- ⚠️ **改进需求**：有较多差评反馈，需要分析和改进工具功能")
        
        # 使用模式建议
        if len(tool_usage) == 1:
            suggestions.append("- 🔧 **功能探索**：团队主要使用单一功能，建议尝试其他工具")
        
        suggestions.append("- 📊 **持续监控**：建议定期查看使用统计，调整MCP工具配置")
        
        return "\n".join(suggestions) + "\n"
    
    async def export_usage_data(self, format_type: str = "json") -> str:
        """导出使用数据"""
        try:
            data = self._load_usage_data()
            
            if format_type == "json":
                export_file = self.data_dir / f"usage_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                
                with open(export_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                return f"✅ 使用数据已导出到: {export_file}"
                
            elif format_type == "csv":
                # 这里可以实现CSV导出逻辑
                return "CSV导出功能待实现"
                
            else:
                return f"不支持的导出格式: {format_type}"
                
        except Exception as e:
            return f"导出数据时出错：{str(e)}"
    

    
 
    
    # 新增的AI编程效果分析方法
    def _calculate_productivity_score(self, coding_metrics: Optional[Dict], ai_session_data: Optional[Dict]) -> float:
        """计算生产力分数"""
        if not coding_metrics and not ai_session_data:
            return 0.0
            
        score = 0.0
        
        # 基于代码行数的生产力
        lines_added = coding_metrics.get('lines_added', 0) if coding_metrics else 0
        if lines_added > 0:
            score += min(lines_added / 50, 1.0) * 0.4  # 最多40分
        
        # 基于会话时间的效率
        session_duration = ai_session_data.get('duration_minutes', 0) if ai_session_data else 0
        if session_duration > 0 and lines_added > 0:
            lines_per_minute = lines_added / session_duration
            score += min(lines_per_minute / 2, 1.0) * 0.3  # 最多30分
        
        # 基于文件数量的并行处理能力
        files_modified = ai_session_data.get('files_modified', 0) if ai_session_data else 0
        if files_modified > 1:
            score += min(files_modified / 5, 1.0) * 0.3  # 最多30分
        
        return round(score, 2)
    
    def _calculate_efficiency_rating(self, coding_metrics: Optional[Dict], quality_metrics: Optional[Dict]) -> str:
        """计算效率评级"""
        if not coding_metrics and not quality_metrics:
            return "未知"
            
        efficiency_score = 0
        
        # 代码质量影响效率
        quality_score = quality_metrics.get('quality_score', 0) if quality_metrics else 0
        efficiency_score += quality_score * 0.4
        
        # AI概率影响效率（适度使用AI更高效）
        ai_probability = coding_metrics.get('ai_probability', 0) if coding_metrics else 0
        if 0.3 <= ai_probability <= 0.8:  # 适度使用AI
            efficiency_score += 30
        elif ai_probability > 0.8:  # 过度依赖AI
            efficiency_score += 15
        else:  # 很少使用AI
            efficiency_score += 10
        
        # 复杂度控制
        complexity = coding_metrics.get('complexity_score', 0) if coding_metrics else 0
        if complexity < 10:
            efficiency_score += 20
        elif complexity < 20:
            efficiency_score += 10
        
        # 评级
        if efficiency_score >= 80:
            return "优秀"
        elif efficiency_score >= 60:
            return "良好"
        elif efficiency_score >= 40:
            return "一般"
        else:
            return "需改进"
    
    def _update_average(self, current_avg: float, new_value: float, count: int) -> float:
        """更新平均值"""
        if count <= 1:
            return new_value
        return round((current_avg * (count - 1) + new_value) / count, 3)
    
    def _generate_ai_programming_report(self, enhanced_logs: List[Dict], ai_stats: Dict, date_range: str) -> str:
        """生成AI编程效果报告"""
        if not enhanced_logs:
            return "📭 暂无AI编程数据"
        
        # 基础统计
        total_sessions = len(enhanced_logs)
        total_lines = sum(log['ai_metrics']['lines_generated'] for log in enhanced_logs)
        total_files = sum(log['ai_metrics']['files_modified'] for log in enhanced_logs)
        
        # 平均指标
        avg_ai_probability = sum(log['ai_metrics']['ai_probability'] for log in enhanced_logs) / total_sessions
        avg_quality_score = sum(log['ai_metrics']['quality_score'] for log in enhanced_logs) / total_sessions
        avg_productivity = sum(log['ai_metrics']['productivity_score'] for log in enhanced_logs) / total_sessions
        
        # 效率分布
        efficiency_ratings = [log['ai_metrics']['efficiency_rating'] for log in enhanced_logs]
        rating_counts = {}
        for rating in efficiency_ratings:
            rating_counts[rating] = rating_counts.get(rating, 0) + 1
        
        # 代码质量分析
        quality_indicators = {
            'with_comments': sum(1 for log in enhanced_logs if log['ai_metrics']['has_comments']),
            'with_error_handling': sum(1 for log in enhanced_logs if log['ai_metrics']['has_error_handling']),
            'with_type_annotations': sum(1 for log in enhanced_logs if log['ai_metrics']['has_type_annotations'])
        }
        
        # 工具使用分布
        tool_usage = {}
        for log in enhanced_logs:
            tool = log['tool_name']
            tool_usage[tool] = tool_usage.get(tool, 0) + 1
        
        # 生成报告
        report = f"""
📈 基础指标
  • 编程会话总数：{total_sessions} 次
  • 代码行数生成：{total_lines} 行
  • 文件修改总数：{total_files} 个
  • 平均会话时长：{sum(log['ai_metrics']['session_duration'] for log in enhanced_logs) / total_sessions:.1f} 分钟

🎯 AI使用效果
  • AI辅助概率：{avg_ai_probability:.1%}
  • 代码质量分数：{avg_quality_score:.1f}/100
  • 生产力评分：{avg_productivity:.2f}/1.0

💡 代码质量分析
  • 包含注释：{quality_indicators['with_comments']}/{total_sessions} ({quality_indicators['with_comments']/total_sessions:.1%})
  • 错误处理：{quality_indicators['with_error_handling']}/{total_sessions} ({quality_indicators['with_error_handling']/total_sessions:.1%})
  • 类型注解：{quality_indicators['with_type_annotations']}/{total_sessions} ({quality_indicators['with_type_annotations']/total_sessions:.1%})

⚡ 效率评级分布
"""
        
        for rating, count in rating_counts.items():
            percentage = count / total_sessions
            report += f"  • {rating}：{count} 次 ({percentage:.1%})\n"
        
        report += f"""
🛠️ 工具使用分布
"""
        
        for tool, count in sorted(tool_usage.items(), key=lambda x: x[1], reverse=True):
            percentage = count / total_sessions
            report += f"  • {tool}：{count} 次 ({percentage:.1%})\n"
        
        # 添加改进建议
        suggestions = self._generate_ai_programming_suggestions(enhanced_logs, avg_quality_score, avg_ai_probability)
        if suggestions:
            report += f"""
💡 改进建议
{suggestions}
"""
        
        return report
    
    def _generate_ai_programming_suggestions(self, enhanced_logs: List[Dict], avg_quality: float, avg_ai_prob: float) -> str:
        """生成AI编程改进建议"""
        suggestions = []
        
        # 代码质量建议
        if avg_quality < 60:
            suggestions.append("  • 建议增加代码注释和错误处理，提高代码质量")
        
        # AI使用建议
        if avg_ai_prob > 0.8:
            suggestions.append("  • AI依赖度较高，建议适当增加手工编码练习")
        elif avg_ai_prob < 0.3:
            suggestions.append("  • AI使用率较低，可以尝试更多AI辅助功能")
        
        # 效率建议
        low_productivity_sessions = [log for log in enhanced_logs if log['ai_metrics']['productivity_score'] < 0.3]
        if len(low_productivity_sessions) > len(enhanced_logs) * 0.3:
            suggestions.append("  • 部分会话生产力较低，建议优化开发流程")
        
        # 复杂度建议
        high_complexity_sessions = [log for log in enhanced_logs if log['ai_metrics']['complexity_added'] > 20]
        if high_complexity_sessions:
            suggestions.append("  • 注意控制代码复杂度，考虑重构复杂的代码块")
        
        return "\n".join(suggestions) if suggestions else "  • 当前开发效果良好，继续保持！" 