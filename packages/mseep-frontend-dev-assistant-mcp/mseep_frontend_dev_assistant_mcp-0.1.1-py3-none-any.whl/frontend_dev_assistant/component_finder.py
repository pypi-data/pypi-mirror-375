"""
Vue组件查找器模块
负责在项目中查找和分析可复用的Vue组件
"""

import os
import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

# 配置日志
logger = logging.getLogger(__name__)

class ComponentFinder:
    def __init__(self):
        """初始化组件查找器"""
        pass
    
    async def find_reusable_components(
        self, 
        project_path: str, 
        component_type: Optional[str] = None,
        search_keywords: List[str] = None
    ) -> str:
        """
        在项目中查找可复用的组件
        
        Args:
            project_path: 项目根目录路径
            component_type: 组件类型过滤（可选）
            search_keywords: 搜索关键词列表（可选）
        
        Returns:
            格式化的组件查找结果
        """
        
        try:
            project_dir = Path(project_path)
            if not project_dir.exists():
                return f"❌ 项目路径不存在: {project_path}"
            
            # 查找所有组件文件
            component_files = self._find_component_files(project_dir)
            
            if not component_files:
                return f"📂 在项目 {project_path} 中未找到任何Vue组件文件"
            
            # 分析组件
            components = []
            for file_path in component_files:
                component_info = self._analyze_component_file(file_path)
                if component_info:
                    components.append(component_info)
            
            if not components:
                return f"📂 在项目中找到 {len(component_files)} 个文件，但没有识别到有效的Vue组件"
            
            # 智能过滤
            filtered_components = self._intelligent_component_filter(
                components, component_type, search_keywords
            )
            
            # 生成结果
            if not filtered_components:
                suggestions = self._generate_search_suggestions(components, search_keywords)
                return f"""
## 🔍 组件搜索结果

未找到匹配的组件。

**搜索条件：**
- 项目路径：{project_path}
- 组件类型：{component_type or '任意'}
- 搜索关键词：{search_keywords or '无'}

**发现的组件总数：** {len(components)} 个

{suggestions}
"""
            
            return self._format_component_suggestions(filtered_components)
            
        except Exception as e:
            logger.error(f"查找组件时出错: {str(e)}")
            return f"❌ 查找组件时出错: {str(e)}"
    
    def _find_component_files(self, project_dir: Path) -> List[Path]:
        """查找项目中的组件文件"""
        component_files = []
        
        # 搜索模式
        patterns = [
            "**/*.vue",
            "**/components/**/*.js",
            "**/components/**/*.ts",
            "**/components/**/*.jsx",
            "**/components/**/*.tsx"
        ]
        
        def should_exclude_path(path: Path) -> bool:
            """判断是否应该排除该路径"""
            exclude_patterns = [
                "node_modules", ".git", "dist", "build", ".nuxt", 
                ".next", "coverage", ".cache", "tmp", "temp",
                "__pycache__", ".pytest_cache"
            ]
            
            path_str = str(path).lower()
            return any(pattern in path_str for pattern in exclude_patterns)
        
        try:
            for pattern in patterns:
                for file_path in project_dir.glob(pattern):
                    if file_path.is_file() and not should_exclude_path(file_path):
                        component_files.append(file_path)
            
            # 去重并排序
            component_files = sorted(list(set(component_files)))
            logger.info(f"找到 {len(component_files)} 个组件文件")
            
        except Exception as e:
            logger.error(f"搜索组件文件时出错: {str(e)}")
        
        return component_files
    
    def _analyze_component_file(self, file_path: Path) -> Optional[Dict]:
        """分析单个组件文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否是有效的UI组件
            if not self._is_valid_ui_component(content, file_path):
                return None
            
            # 提取组件信息
            component_name = self._extract_component_name(file_path)
            props, events = self._extract_props_and_events(content)
            slots = self._extract_slots(content)
            description = self._extract_description(content)
            component_type = self._guess_component_type(component_name, content, file_path)
            features = self._extract_features(content)
            
            return {
                "name": component_name,
                "file_path": str(file_path),
                "relative_path": str(file_path.relative_to(file_path.parts[0])),
                "type": component_type,
                "description": description,
                "props": props,
                "events": events,
                "slots": slots,
                "features": features,
                "file_size": file_path.stat().st_size,
                "modified_time": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
            }
            
        except Exception as e:
            logger.error(f"分析组件文件 {file_path} 时出错: {str(e)}")
            return None
    
    def _is_valid_ui_component(self, content: str, file_path: Path) -> bool:
        """判断是否是有效的UI组件"""
        
        # Vue文件检查
        if file_path.suffix == '.vue':
            return '<template>' in content and ('<script>' in content or '<script setup>' in content)
        
        # JS/TS文件检查
        ui_indicators = [
            r'export\s+default\s*{.*template',
            r'render\s*\(',
            r'createElement\s*\(',
            r'h\s*\(',
            r'return\s+React\.createElement',
            r'return\s+<\w+',
            r'jsx',
            r'tsx'
        ]
        
        for pattern in ui_indicators:
            if re.search(pattern, content, re.IGNORECASE | re.DOTALL):
                return True
        
        return False
    
    def _extract_component_name(self, file_path: Path) -> str:
        """提取组件名称"""
        name = file_path.stem
        
        # 特殊处理
        if name.lower() in ['index', 'main']:
            name = file_path.parent.name
        
        return self._to_pascal_case(name)
    
    def _to_pascal_case(self, text: str) -> str:
        """转换为PascalCase"""
        # 处理多种分隔符
        words = re.split(r'[-_\s.]+', text)
        return ''.join(word.capitalize() for word in words if word)
    
    def _extract_props_and_events(self, content: str) -> Tuple[List[Dict], List[str]]:
        """提取props和events"""
        props = self._extract_props_enhanced(content)
        events = self._extract_events_enhanced(content)
        return props, events
    
    def _extract_props_enhanced(self, content: str) -> List[Dict]:
        """增强的props提取"""
        props = []
        
        # Vue3 script setup props
        script_setup_match = re.search(r'<script\s+setup[^>]*>(.*?)</script>', content, re.DOTALL)
        if script_setup_match:
            script_content = script_setup_match.group(1)
            
            # defineProps
            props_match = re.search(r'defineProps\s*\(\s*({.*?}|\[.*?\])', script_content, re.DOTALL)
            if props_match:
                props_str = props_match.group(1)
                props.extend(self._parse_props_object(props_str))
        
        # Vue2/3 options API
        options_match = re.search(r'props\s*:\s*({.*?}|\[.*?\])', content, re.DOTALL)
        if options_match:
            props_str = options_match.group(1)
            props.extend(self._parse_props_object(props_str))
        
        return props
    
    def _parse_props_object(self, props_content: str) -> List[Dict]:
        """解析props对象"""
        props = []
        
        # 简单的props数组格式
        if props_content.strip().startswith('['):
            array_props = re.findall(r'["\'](\w+)["\']', props_content)
            for prop in array_props:
                props.append({
                    "name": prop,
                    "type": "any",
                    "required": False,
                    "default": None
                })
            return props
        
        # 对象格式props
        prop_matches = re.finditer(r'(\w+)\s*:\s*({[^}]*}|\w+)', props_content)
        for match in prop_matches:
            prop_name = match.group(1)
            prop_def = match.group(2)
            
            prop_info = {
                "name": prop_name,
                "type": "any",
                "required": False,
                "default": None
            }
            
            # 提取类型
            if 'String' in prop_def:
                prop_info["type"] = "string"
            elif 'Number' in prop_def:
                prop_info["type"] = "number"
            elif 'Boolean' in prop_def:
                prop_info["type"] = "boolean"
            elif 'Array' in prop_def:
                prop_info["type"] = "array"
            elif 'Object' in prop_def:
                prop_info["type"] = "object"
            
            # 提取required
            if 'required:' in prop_def and 'true' in prop_def:
                prop_info["required"] = True
            
            # 提取默认值
            default_match = re.search(r'default\s*:\s*([^,}]+)', prop_def)
            if default_match:
                prop_info["default"] = default_match.group(1).strip()
            
            props.append(prop_info)
        
        return props
    
    def _extract_events_enhanced(self, content: str) -> List[str]:
        """增强的事件提取"""
        events = []
        
        # $emit 调用
        emit_matches = re.finditer(r'\$emit\s*\(\s*["\']([^"\']+)["\']', content)
        for match in emit_matches:
            events.append(match.group(1))
        
        # defineEmits (Vue3)
        emits_match = re.search(r'defineEmits\s*\(\s*\[([^\]]+)\]', content)
        if emits_match:
            emits_str = emits_match.group(1)
            event_matches = re.findall(r'["\']([^"\']+)["\']', emits_str)
            events.extend(event_matches)
        
        # emits选项
        emits_option_match = re.search(r'emits\s*:\s*\[([^\]]+)\]', content)
        if emits_option_match:
            emits_str = emits_option_match.group(1)
            event_matches = re.findall(r'["\']([^"\']+)["\']', emits_str)
            events.extend(event_matches)
        
        return list(set(events))  # 去重
    
    def _extract_slots(self, content: str) -> List[str]:
        """提取插槽信息"""
        slots = []
        
        # <slot> 标签
        slot_matches = re.finditer(r'<slot\s+name=["\']([^"\']+)["\']', content)
        for match in slot_matches:
            slots.append(match.group(1))
        
        # 默认插槽
        if '<slot>' in content or '<slot/>' in content:
            slots.append('default')
        
        return list(set(slots))
    
    def _extract_description(self, content: str) -> str:
        """提取组件描述"""
        # 从注释中提取
        comment_desc = self._extract_component_level_comment(content)
        if comment_desc:
            return comment_desc
        
        # 智能生成描述
        return self._generate_smart_description(content)
    
    def _extract_component_level_comment(self, content: str) -> str:
        """提取组件级别的注释"""
        patterns = [
            r'/\*\*\s*\n?\s*\*\s*([^\n*]+)',  # JSDoc注释
            r'//\s*([^\n]+)',  # 单行注释
            r'<!--\s*([^-]+)\s*-->'  # HTML注释
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                desc = match.group(1).strip()
                if len(desc) > 10:  # 过滤掉过短的注释
                    return desc
        
        return ""
    
    def _generate_smart_description(self, content: str) -> str:
        """智能生成组件描述"""
        template_features = self._analyze_template_features(content)
        interaction_capabilities = self._analyze_interaction_capabilities(content)
        
        if template_features or interaction_capabilities:
            return f"{template_features} {interaction_capabilities}".strip()
        
        return "Vue组件"
    
    def _analyze_template_features(self, content: str) -> str:
        """分析模板特性"""
        features = []
        
        if re.search(r'<form|@submit', content):
            features.append("表单")
        if re.search(r'<table|<thead|<tbody', content):
            features.append("表格")
        if re.search(r'v-for|:key', content):
            features.append("列表")
        if re.search(r'<input|<select|<textarea', content):
            features.append("输入")
        if re.search(r'<button|@click', content):
            features.append("交互")
        if re.search(r'<img|image', content):
            features.append("图片")
        
        return "包含" + "、".join(features) + "功能" if features else ""
    
    def _analyze_interaction_capabilities(self, content: str) -> str:
        """分析交互能力"""
        capabilities = []
        
        if re.search(r'\$emit|defineEmits', content):
            capabilities.append("事件通信")
        if re.search(r'props|defineProps', content):
            capabilities.append("属性配置")
        if re.search(r'<slot', content):
            capabilities.append("内容插槽")
        if re.search(r'v-model', content):
            capabilities.append("双向绑定")
        
        return "支持" + "、".join(capabilities) if capabilities else ""
    
    def _extract_features(self, content: str) -> List[str]:
        """提取组件特性"""
        features = []
        
        # 基础特性检测
        if re.search(r'v-model', content):
            features.append("双向数据绑定")
        if re.search(r'<slot', content):
            features.append("插槽支持")
        if re.search(r'\$emit|defineEmits', content):
            features.append("事件通信")
        if re.search(r'watch|computed', content):
            features.append("响应式数据")
        if re.search(r'scoped', content):
            features.append("样式隔离")
        if re.search(r'async|await|Promise', content):
            features.append("异步处理")
        if re.search(r'props|defineProps', content):
            features.append("属性配置")
        if re.search(r'typescript|ts|interface', content):
            features.append("TypeScript")
        
        return features
    
    def _guess_component_type(self, name: str, content: str, file_path: Path) -> str:
        """推测组件类型"""
        name_lower = name.lower()
        content_lower = content.lower()
        
        # 基于名称推测
        type_keywords = {
            "table": ["table", "grid", "list", "data"],
            "form": ["form", "input", "field", "edit"],
            "modal": ["modal", "dialog", "popup", "overlay"],
            "card": ["card", "panel", "item"],
            "button": ["button", "btn", "action"],
            "navigation": ["nav", "menu", "header", "sidebar"],
            "layout": ["layout", "container", "wrapper"],
            "display": ["show", "display", "view", "preview"]
        }
        
        for comp_type, keywords in type_keywords.items():
            if any(keyword in name_lower for keyword in keywords):
                return comp_type
        
        # 基于内容推测
        if re.search(r'<table|<thead|<tbody|<tr|<td', content):
            return "table"
        elif re.search(r'<form|<input|<select|<textarea', content):
            return "form"
        elif re.search(r'v-show|v-if.*modal|position.*fixed|z-index', content):
            return "modal"
        elif re.search(r'<nav|<menu|router-link', content):
            return "navigation"
        elif re.search(r'<button|@click.*button', content):
            return "button"
        
        return "component"
    
    def _intelligent_component_filter(
        self, 
        components: List[Dict], 
        component_type: Optional[str],
        keywords: Optional[List[str]]
    ) -> List[Dict]:
        """智能组件过滤"""
        if not component_type and not keywords:
            return components[:10]  # 返回前10个
        
        # 计算相似度分数
        scored_components = []
        for component in components:
            score = self._calculate_component_similarity(component, component_type, keywords)
            if score > 0:
                component["similarity_score"] = score
                scored_components.append(component)
        
        # 按分数排序
        scored_components.sort(key=lambda x: x["similarity_score"], reverse=True)
        
        return scored_components[:8]  # 返回最相关的8个
    
    def _calculate_component_similarity(
        self, 
        component: Dict, 
        target_type: Optional[str], 
        keywords: Optional[List[str]]
    ) -> float:
        """计算组件相似度"""
        score = 0.0
        
        # 类型匹配 (40%权重)
        if target_type:
            type_score = self._calculate_type_similarity(component, target_type)
            score += type_score * 0.4
        
        # 关键词匹配 (60%权重)
        if keywords:
            component_text = self._build_component_full_text(component)
            keyword_score = self._calculate_keyword_similarity(component_text, keywords)
            score += keyword_score * 0.6
        
        return min(score, 1.0)
    
    def _build_component_full_text(self, component: Dict) -> str:
        """构建组件的全文本用于搜索"""
        texts = [
            component.get("name", ""),
            component.get("description", ""),
            component.get("type", ""),
            " ".join(component.get("features", [])),
            " ".join([prop.get("name", "") for prop in component.get("props", [])]),
            " ".join(component.get("events", [])),
            component.get("relative_path", "")
        ]
        return " ".join(texts).lower()
    
    def _calculate_type_similarity(self, component: Dict, target_type: str) -> float:
        """计算类型相似度"""
        component_type = component.get("type", "").lower()
        target_type = target_type.lower()
        
        if component_type == target_type:
            return 1.0
        
        # 类型别名映射
        type_aliases = {
            "table": ["grid", "list", "data"],
            "form": ["input", "field", "edit"],
            "modal": ["dialog", "popup", "overlay"],
            "button": ["btn", "action"],
            "navigation": ["nav", "menu"]
        }
        
        for main_type, aliases in type_aliases.items():
            if target_type == main_type and component_type in aliases:
                return 0.8
            if component_type == main_type and target_type in aliases:
                return 0.8
        
        return 0.0
    
    def _calculate_keyword_similarity(self, component_text: str, keywords: List[str]) -> float:
        """计算关键词相似度"""
        if not keywords:
            return 0.0
        
        total_score = 0.0
        for keyword in keywords:
            keyword_lower = keyword.lower()
            
            # 精确匹配
            if keyword_lower in component_text:
                total_score += 1.0
            # 模糊匹配
            elif self._fuzzy_match(keyword_lower, component_text) > 0.7:
                total_score += 0.7
        
        return min(total_score / len(keywords), 1.0)
    
    def _fuzzy_match(self, keyword: str, text: str) -> float:
        """模糊匹配算法"""
        words = text.split()
        max_similarity = 0.0
        
        for word in words:
            similarity = self._string_similarity(keyword, word)
            max_similarity = max(max_similarity, similarity)
        
        return max_similarity
    
    def _string_similarity(self, s1: str, s2: str) -> float:
        """计算字符串相似度"""
        if not s1 or not s2:
            return 0.0
        
        # 简单的编辑距离相似度
        len1, len2 = len(s1), len(s2)
        if len1 == 0 or len2 == 0:
            return 0.0
        
        # 包含关系
        if s1 in s2 or s2 in s1:
            return 0.8
        
        # 字符重叠度
        common_chars = set(s1) & set(s2)
        total_chars = set(s1) | set(s2)
        
        if total_chars:
            return len(common_chars) / len(total_chars)
        
        return 0.0
    
    def _generate_search_suggestions(self, all_components: List[Dict], keywords: Optional[List[str]]) -> str:
        """生成搜索建议"""
        # 统计组件类型
        type_counts = {}
        for comp in all_components:
            comp_type = comp.get("type", "unknown")
            type_counts[comp_type] = type_counts.get(comp_type, 0) + 1
        
        suggestions = ["**💡 搜索建议：**\n"]
        
        # 推荐常见类型
        common_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        if common_types:
            suggestions.append("**可用的组件类型：**")
            for comp_type, count in common_types:
                suggestions.append(f"- `{comp_type}` ({count}个)")
        
        # 推荐常见关键词
        all_features = []
        for comp in all_components:
            all_features.extend(comp.get("features", []))
        
        if all_features:
            feature_counts = {}
            for feature in all_features:
                feature_counts[feature] = feature_counts.get(feature, 0) + 1
            
            common_features = sorted(feature_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            suggestions.append("\n**常见功能特性：**")
            for feature, count in common_features:
                suggestions.append(f"- `{feature}` ({count}个组件)")
        
        return "\n".join(suggestions)
    
    def _format_component_suggestions(self, components: List[Dict]) -> str:
        """格式化组件建议"""
        if not components:
            return "未找到匹配的组件"
        
        result = [f"## 🎯 找到 {len(components)} 个匹配的组件\n"]
        
        for i, comp in enumerate(components, 1):
            score = comp.get("similarity_score", 0)
            
            result.append(f"### {i}. {comp['name']} ⭐ {score:.1%}")
            result.append(f"**路径：** `{comp['relative_path']}`")
            result.append(f"**类型：** {comp['type']}")
            result.append(f"**描述：** {comp['description']}")
            
            # Props信息
            if comp.get('props'):
                result.append("**Props：**")
                for prop in comp['props'][:3]:  # 只显示前3个
                    required = "必需" if prop.get("required") else "可选"
                    default = f" (默认: {prop.get('default')})" if prop.get('default') else ""
                    result.append(f"- `{prop['name']}`: {prop['type']} - {required}{default}")
                
                if len(comp['props']) > 3:
                    result.append(f"- ... 还有 {len(comp['props']) - 3} 个props")
            
            # 功能特性
            if comp.get('features'):
                features_str = "、".join(comp['features'][:4])
                if len(comp['features']) > 4:
                    features_str += f"等{len(comp['features'])}项特性"
                result.append(f"**特性：** {features_str}")
            
            # 使用示例
            result.append("**使用示例：**")
            result.append("```vue")
            result.append(f"<{self._to_kebab_case(comp['name'])}")
            
            # 生成props示例
            if comp.get('props'):
                for prop in comp['props'][:2]:  # 只显示前2个prop
                    if prop.get('type') == 'string':
                        result.append(f'  {self._to_kebab_case(prop["name"])}="示例值"')
                    elif prop.get('type') == 'boolean':
                        result.append(f'  {self._to_kebab_case(prop["name"])}')
                    elif prop.get('type') == 'number':
                        result.append(f'  :{self._to_kebab_case(prop["name"])}="123"')
            
            result.append("/>")
            result.append("```")
            result.append("")
        
        result.append("---")
        result.append("💡 **提示：** 建议复制现有组件代码进行修改，而不是从零开始编写")
        
        return "\n".join(result)
    
    def _to_kebab_case(self, text: str) -> str:
        """转换为kebab-case"""
        # 处理PascalCase到kebab-case
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1-\2', text)
        return re.sub('([a-z0-9])([A-Z])', r'\1-\2', s1).lower()

# 为了保持向后兼容，创建一个别名
ComponentGenerator = ComponentFinder 