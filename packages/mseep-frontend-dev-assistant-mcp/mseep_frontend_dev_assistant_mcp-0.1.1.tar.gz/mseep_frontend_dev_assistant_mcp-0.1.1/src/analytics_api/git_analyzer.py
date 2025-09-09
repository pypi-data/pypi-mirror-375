"""
简化的Git分析器
专注于核心git分析功能，与数据库集成
"""

import subprocess
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

class GitAnalyzer:
    """简化的Git仓库分析器"""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path).resolve()
        
    def run_git_command(self, command: List[str]) -> Tuple[bool, str]:
        """执行git命令"""
        try:
            result = subprocess.run(
                ['git'] + command,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0, result.stdout.strip()
        except Exception as e:
            return False, str(e)
    
    def get_repo_info(self) -> Dict[str, Any]:
        """获取仓库基本信息"""
        info = {}
        
        # 获取远程仓库URL
        success, remote_url = self.run_git_command(['config', '--get', 'remote.origin.url'])
        if success:
            info['remote_url'] = remote_url
            info['repository_type'] = self._detect_repo_type(remote_url)
        
        # 获取当前分支
        success, branch = self.run_git_command(['branch', '--show-current'])
        if success:
            info['current_branch'] = branch
        
        # 获取最后一次提交
        success, last_commit = self.run_git_command(['log', '-1', '--format=%H|%an|%ad|%s'])
        if success and last_commit:
            parts = last_commit.split('|', 3)
            if len(parts) >= 4:
                info['last_commit'] = {
                    'hash': parts[0],
                    'author': parts[1],
                    'date': parts[2],
                    'message': parts[3]
                }
        
        return info
    
    def _detect_repo_type(self, remote_url: str) -> str:
        """检测仓库类型"""
        if 'github.com' in remote_url:
            return 'github'
        elif 'gitlab' in remote_url:
            return 'gitlab'
        elif 'yunxiao' in remote_url or 'aliyun' in remote_url:
            return 'aliyun_yunxiao'
        else:
            return 'unknown'
    
    def get_status(self) -> Dict[str, Any]:
        """获取仓库状态"""
        success, status_output = self.run_git_command(['status', '--porcelain'])
        
        if not success:
            return {'error': 'Failed to get git status'}
        
        modified_files = []
        new_files = []
        deleted_files = []
        
        for line in status_output.split('\n'):
            if not line.strip():
                continue
                
            status = line[:2]
            filepath = line[3:]
            
            if status.startswith('M'):
                modified_files.append(filepath)
            elif status.startswith('A') or status.startswith('??'):
                new_files.append(filepath)
            elif status.startswith('D'):
                deleted_files.append(filepath)
        
        return {
            'modified_files': modified_files,
            'new_files': new_files,
            'deleted_files': deleted_files,
            'total_changes': len(modified_files) + len(new_files) + len(deleted_files)
        }
    
    def get_commit_history(self, since_days: int = 7, author: str = None) -> List[Dict[str, Any]]:
        """获取提交历史"""
        command = ['log', '--since', f'{since_days} days ago', '--format=%H|%an|%ae|%ad|%s']
        
        if author:
            command.extend(['--author', author])
        
        success, log_output = self.run_git_command(command)
        
        if not success:
            return []
        
        commits = []
        for line in log_output.split('\n'):
            if line.strip():
                parts = line.split('|', 4)
                if len(parts) >= 5:
                    commit = {
                        'hash': parts[0],
                        'author_name': parts[1],
                        'author_email': parts[2],
                        'date': parts[3],
                        'message': parts[4],
                        'is_ai_assisted': self._detect_ai_assisted_commit(parts[4])
                    }
                    commits.append(commit)
        
        return commits
    
    def _detect_ai_assisted_commit(self, commit_message: str) -> bool:
        """检测AI辅助的提交"""
        ai_keywords = [
            'ai', 'cursor', 'copilot', 'claude', 'gpt', 'assistant',
            '自动生成', '代码生成', 'auto-generated'
        ]
        
        message_lower = commit_message.lower()
        return any(keyword in message_lower for keyword in ai_keywords)
    
    def analyze_commit_patterns(self, commits: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析提交模式"""
        if not commits:
            return {}
        
        # 基本统计
        total_commits = len(commits)
        ai_assisted_commits = sum(1 for c in commits if c.get('is_ai_assisted'))
        
        # 作者统计
        authors = {}
        for commit in commits:
            author = commit['author_name']
            if author not in authors:
                authors[author] = {'total': 0, 'ai_assisted': 0}
            authors[author]['total'] += 1
            if commit.get('is_ai_assisted'):
                authors[author]['ai_assisted'] += 1
        
        # 提交消息模式分析
        commit_types = {}
        for commit in commits:
            message = commit['message']
            commit_type = self._extract_commit_type(message)
            if commit_type not in commit_types:
                commit_types[commit_type] = 0
            commit_types[commit_type] += 1
        
        return {
            'total_commits': total_commits,
            'ai_assisted_commits': ai_assisted_commits,
            'ai_assistance_rate': ai_assisted_commits / total_commits if total_commits > 0 else 0,
            'authors': authors,
            'commit_types': commit_types,
            'most_active_author': max(authors.items(), key=lambda x: x[1]['total'])[0] if authors else None
        }
    
    def _extract_commit_type(self, message: str) -> str:
        """提取提交类型"""
        patterns = {
            'feat': r'^feat[(\[]',
            'fix': r'^fix[(\[]',
            'docs': r'^docs[(\[]',
            'style': r'^style[(\[]',
            'refactor': r'^refactor[(\[]',
            'test': r'^test[(\[]',
            'chore': r'^chore[(\[]',
            'config': r'^config[(\[]',
            'clean': r'^clean[(\[]'
        }
        
        message_lower = message.lower()
        for commit_type, pattern in patterns.items():
            if re.match(pattern, message_lower):
                return commit_type
        
        return 'other'
    
    def get_file_changes(self, file_path: str) -> Dict[str, Any]:
        """获取文件变更统计"""
        success, diff_output = self.run_git_command(['diff', 'HEAD', '--', file_path])
        
        if not success:
            return {'error': f'Failed to get diff for {file_path}'}
        
        lines_added = 0
        lines_deleted = 0
        
        for line in diff_output.split('\n'):
            if line.startswith('+') and not line.startswith('+++'):
                lines_added += 1
            elif line.startswith('-') and not line.startswith('---'):
                lines_deleted += 1
        
        return {
            'file_path': file_path,
            'lines_added': lines_added,
            'lines_deleted': lines_deleted,
            'total_changes': lines_added + lines_deleted
        } 