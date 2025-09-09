"""
提示词管理模块
负责管理和提供各种开发场景的标准化提示词模板
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

class PromptManager:
    def __init__(self):
        self.templates_dir = Path(__file__).parent / "templates"
        self.templates_dir.mkdir(exist_ok=True)
        self.load_default_templates()
    
    def load_default_templates(self):
        """加载默认提示词模板"""
        default_templates = {
            "git_commit": {
                "name": "Git 代码提交助手",
                "description": "帮助开发者分批次、规范化提交代码",
                "template": """帮我分批次提交代码。请先检查 git status，然后分析所有未暂存的修改，并一次性提供一个完整的、按模块或功能分组的提交计划。

计划应包含：
1. 每个批次要提交的文件列表
2. 为每个批次建议的 commit message (格式为 feat/fix: 中文描述)

请等待我确认或修改计划后再执行任何 git 命令。

注意事项：
- 遵循 Conventional Commits 规范
- commit message 使用中文描述
- 按功能模块合理分组
- 避免混合不相关的改动

{context}""",
                "tags": ["git", "提交", "代码管理"]
            },
            
            "code_review": {
                "name": "代码审查助手",
                "description": "基于团队规范进行代码质量审查",
                "template": """根据前端代码规范对以下代码进行 code review，主要关注：

规范检查：
1. **魔法值处理**：是否存在硬编码的数字、字符串等魔法值
2. **常量定义**：常量是否正确定义和使用
3. **方法注释**：方法是否有完整的JSDoc注释
4. **命名规范**：变量、方法、组件命名是否符合规范
5. **代码结构**：是否遵循团队约定的代码组织结构

业务逻辑检查：
1. **错误处理**：是否有适当的错误边界和异常处理
2. **性能优化**：是否存在明显的性能问题
3. **可维护性**：代码是否易于理解和维护
4. **测试覆盖**：是否遗漏重要的测试场景

请提供具体的改进建议和示例代码。

参考编码规范：
- 使用 PascalCase 命名组件
- 使用 camelCase 命名变量和方法
- 常量使用 UPPER_SNAKE_CASE
- 方法必须有 JSDoc 注释
- 避免使用魔法值，定义为常量

{context}""",
                "tags": ["代码审查", "质量检查", "规范"]
            },
            
            "component_reuse": {
                "name": "组件复用助手",
                "description": "帮助快速定位和复用项目中的现有组件",
                "template": """帮我复用项目中的{component_type}组件。

请执行以下步骤：

1. **查找现有组件**：
   - 在项目的 components 目录下查找相关组件
   - 分析组件的 props 接口和使用方式
   - 确定组件的适用场景

2. **生成使用代码**：
   - 提供完整的引入语句
   - 展示基本使用示例
   - 说明主要 props 的作用和类型

3. **定制建议**：
   - 如果现有组件不完全匹配需求，提供修改建议
   - 建议如何扩展组件功能
   - 提醒注意事项和最佳实践

搜索关键词：{keywords}

期望功能：{expected_features}

请在指定位置生成对应的代码，并确保：
- 正确引入组件依赖
- 使用符合团队规范的代码风格
- 添加必要的注释说明

{context}""",
                "tags": ["组件复用", "代码生成", "效率工具"]
            },
            
            "vue_component_spec": {
                "name": "Vue组件规范生成",
                "description": "基于团队编码规范生成标准Vue组件",
                "template": """请基于团队编码规范生成一个{vue_version} {component_type}组件。

组件要求：
- 组件名称：{component_name}
- Vue版本：{vue_version}
- 组件类型：{component_type}

编码规范要求：
1. **命名规范**：
   - 组件使用 PascalCase
   - props 使用 camelCase
   - 事件使用 kebab-case
   - 插槽使用 kebab-case

2. **结构规范**：
   - 使用 <script setup> 语法（Vue3）
   - props 必须定义类型和默认值
   - 导出的方法需要 JSDoc 注释
   - 样式使用 scoped

3. **代码质量**：
   - 添加适当的类型检查
   - 包含错误边界处理
   - 支持响应式设计
   - 遵循无障碍规范

4. **注释要求**：
   - 组件顶部添加功能说明
   - 复杂逻辑添加行内注释
   - props 添加描述注释

组件功能特性：{features}

请生成完整的组件代码，包括：
- 完整的 Vue 单文件组件
- TypeScript 类型定义（如适用）
- 使用示例和文档

{context}""",
                "tags": ["Vue组件", "代码生成", "编码规范"]
            },
            
            "project_environment_troubleshooting": {
                "name": "项目环境排查助手",
                "description": "系统性排查和解决老项目环境配置问题",
                "template": """帮我排查这个项目的环境配置问题。请按以下步骤进行系统性分析：

## 📋 第一步：收集基础信息

请提供以下信息（我将逐步分析）：

1. **项目信息**：
   - 项目根目录的 package.json 文件内容
   - 是否存在 package-lock.json 或 yarn.lock 文件
   - 项目技术栈（Vue2/Vue3/Taro/小程序等）

2. **环境信息**：
   - 当前 Node.js 版本 (`node -v`)
   - 当前 npm/yarn 版本 (`npm -v` 或 `yarn -v`)
   - 操作系统（Windows/macOS/Linux）

3. **问题描述**：
   - 具体的报错信息（完整错误日志）
   - 执行的命令（npm install, npm run dev 等）
   - 问题出现的环节（安装依赖、启动项目、打包构建）

## 🔍 第二步：问题诊断分析

我将基于你们团队的技术栈重点检查：

**Vue2项目常见问题：**
- node-sass 版本与 Node 版本兼容性
- webpack 4.x 配置问题
- Element UI 等依赖版本冲突

**Vue3项目常见问题：**
- Vite 版本要求
- TypeScript 配置兼容性
- 组合式API相关包版本

**Taro项目特殊检查：**
- Taro CLI 版本与 Node 版本匹配
- 多端构建配置问题
- 原生模块编译问题

**小程序项目分析：**
- 开发者工具版本要求
- npm 构建配置检查
- 平台差异处理

## 🛠️ 第三步：提供解决方案

基于诊断结果，我将提供：

1. **推荐的 Node 版本**（基于项目依赖分析）
2. **详细的修复步骤**（针对具体问题）
3. **环境配置文档**（供团队成员参考）
4. **预防措施**（避免类似问题）

## 📝 第四步：生成项目环境说明

最终输出标准化的环境配置文档，包含：
- 环境要求说明
- 快速启动步骤
- 常见问题解决方案
- 团队开发环境统一建议

---

请先提供第一步要求的基础信息，我将开始分析。

{context}""",
                "tags": ["环境配置", "问题排查", "团队协作", "老项目维护"]
            }
        }
        
        # 保存默认模板到文件
        templates_file = self.templates_dir / "default_templates.json"
        
        # 检查现有文件是否包含所有默认模板
        should_update = True
        if templates_file.exists():
            try:
                with open(templates_file, 'r', encoding='utf-8') as f:
                    existing_templates = json.load(f)
                # 检查是否包含所有默认模板
                if all(key in existing_templates for key in default_templates.keys()):
                    should_update = False
            except (json.JSONDecodeError, KeyError):
                should_update = True
        
        if should_update:
            with open(templates_file, 'w', encoding='utf-8') as f:
                json.dump(default_templates, f, ensure_ascii=False, indent=2)
    
    async def get_template(self, prompt_type: str, context: str = "") -> str:
        """获取指定类型的提示词模板"""
        try:
            templates_file = self.templates_dir / "default_templates.json"
            with open(templates_file, 'r', encoding='utf-8') as f:
                templates = json.load(f)
            
            if prompt_type not in templates:
                return f"未找到类型为 '{prompt_type}' 的提示词模板"
            
            template_data = templates[prompt_type]
            template = template_data["template"]
            
            # 记录使用统计到单独的文件
            usage_stats = self._load_usage_stats()
            if prompt_type not in usage_stats:
                usage_stats[prompt_type] = {"usage_count": 0, "last_used": None}
            
            usage_stats[prompt_type]["usage_count"] += 1
            usage_stats[prompt_type]["last_used"] = datetime.now().isoformat()
            
            # 保存使用统计到单独文件
            self._save_usage_stats(usage_stats)
            
            # 替换上下文变量
            if context:
                template = template.replace("{context}", f"\n附加上下文：\n{context}")
            else:
                template = template.replace("{context}", "")
            
            # 构建返回信息
            result = f"""
📋 **{template_data['name']}**

{template_data['description']}

---

{template}

---
💡 使用次数：{usage_stats[prompt_type]['usage_count']} | 标签：{', '.join(template_data['tags'])}
"""
            return result
            
        except Exception as e:
            return f"获取提示词模板时出错：{str(e)}"
    
    def _load_usage_stats(self) -> dict:
        """加载使用统计数据"""
        stats_file = self.templates_dir / "usage_stats.json"
        if stats_file.exists():
            try:
                with open(stats_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def _save_usage_stats(self, stats: dict) -> None:
        """保存使用统计数据"""
        stats_file = self.templates_dir / "usage_stats.json"
        try:
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存使用统计失败: {e}")
    
    async def add_custom_template(self, name: str, template: str, description: str = "", tags: List[str] = None) -> str:
        """添加自定义提示词模板"""
        try:
            custom_file = self.templates_dir / "custom_templates.json"
            
            # 加载现有自定义模板
            if custom_file.exists():
                with open(custom_file, 'r', encoding='utf-8') as f:
                    custom_templates = json.load(f)
            else:
                custom_templates = {}
            
            # 添加新模板
            custom_templates[name] = {
                "name": name,
                "description": description,
                "template": template,
                "tags": tags or [],
                "usage_count": 0,
                "last_used": None,
                "created_at": datetime.now().isoformat()
            }
            
            # 保存
            with open(custom_file, 'w', encoding='utf-8') as f:
                json.dump(custom_templates, f, ensure_ascii=False, indent=2)
            
            return f"✅ 自定义提示词模板 '{name}' 已添加成功"
            
        except Exception as e:
            return f"添加自定义模板时出错：{str(e)}"
    
    async def list_templates(self) -> List[str]:
        """列出所有可用的提示词模板名称"""
        try:
            template_names = []
            
            # 加载默认模板
            templates_file = self.templates_dir / "default_templates.json"
            if templates_file.exists():
                with open(templates_file, 'r', encoding='utf-8') as f:
                    templates = json.load(f)
                template_names.extend(templates.keys())
            
            # 加载自定义模板
            custom_file = self.templates_dir / "custom_templates.json"
            if custom_file.exists():
                with open(custom_file, 'r', encoding='utf-8') as f:
                    custom_templates = json.load(f)
                template_names.extend(custom_templates.keys())
            
            return template_names
            
        except Exception as e:
            print(f"列出模板时出错：{str(e)}")
            return []
    
    async def get_template_details(self) -> str:
        """获取所有模板的详细信息（用于显示）"""
        try:
            result = "📚 **可用的提示词模板**\n\n"
            
            # 加载使用统计
            usage_stats = self._load_usage_stats()
            
            # 加载默认模板
            templates_file = self.templates_dir / "default_templates.json"
            if templates_file.exists():
                with open(templates_file, 'r', encoding='utf-8') as f:
                    templates = json.load(f)
                
                result += "## 默认模板\n"
                for key, template in templates.items():
                    usage_count = usage_stats.get(key, {}).get('usage_count', 0)
                    result += f"- **{key}**: {template['name']}\n"
                    result += f"  {template['description']}\n"
                    result += f"  使用次数: {usage_count} | 标签: {', '.join(template['tags'])}\n\n"
            
            # 加载自定义模板
            custom_file = self.templates_dir / "custom_templates.json"
            if custom_file.exists():
                with open(custom_file, 'r', encoding='utf-8') as f:
                    custom_templates = json.load(f)
                
                if custom_templates:
                    result += "## 自定义模板\n"
                    for key, template in custom_templates.items():
                        usage_count = usage_stats.get(key, {}).get('usage_count', 0)
                        result += f"- **{key}**: {template['name']}\n"
                        result += f"  {template['description']}\n"
                        result += f"  使用次数: {usage_count} | 标签: {', '.join(template['tags'])}\n\n"
            
            return result
            
        except Exception as e:
            return f"获取模板详情时出错：{str(e)}" 