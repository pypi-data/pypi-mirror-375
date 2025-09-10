import os
import json
import logging
from typing import Dict, List, Any, Optional
from .file_saver import FigmaFileSaver

logger = logging.getLogger(__name__)

class FigmaSmartComponentAnalyzer:
    """基于AI的智能组件分析器 - 使用prompt分析组件可复用性"""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.file_saver = FigmaFileSaver()
        
    def analyze_with_ai_prompt(self, file_key: str, node_ids: str = "0:0", max_depth: int = 4) -> Dict[str, Any]:
        """
        使用AI prompt分析Figma文件中的组件可复用性
        
        Args:
            file_key: Figma文件ID
            node_ids: 要分析的节点ID列表，用逗号分隔
            max_depth: 最大分析深度
            
        Returns:
            包含AI分析结果的字典
        """
        try:
            # 获取节点信息
            from .figma_tree_extractor import FigmaTreeExtractor
            tree_extractor = FigmaTreeExtractor(self.access_token)
            
            # 解析节点ID列表
            node_id_list = [id.strip() for id in node_ids.split(",") if id.strip()]
            
            all_nodes_data = []
            file_name = "Unknown"
            
            # 收集所有节点数据
            for node_id in node_id_list:
                result = tree_extractor.extract_tree(file_key, node_id, max_depth)
                if result and "nodes" in result and node_id in result["nodes"]:
                    tree_structure = result["nodes"][node_id]["tree_structure"]
                    nodes = self._extract_nodes_for_analysis(tree_structure, node_id)
                    all_nodes_data.extend(nodes)
                    file_name = result.get("file_name", "Unknown")
            
            if not all_nodes_data:
                return {"error": "No valid nodes found for analysis"}
            
            # 生成AI分析prompt
            analysis_prompt = self._generate_analysis_prompt(all_nodes_data)
            
            # 模拟AI分析结果（实际项目中可以调用真实的AI API）
            ai_analysis = self._simulate_ai_analysis(all_nodes_data, analysis_prompt)
            
            # 保存分析结果
            self._save_ai_analysis_result(ai_analysis, file_key)
            
            return ai_analysis
            
        except Exception as e:
            logger.error(f"Error in AI component analysis: {e}")
            return {"error": f"AI analysis failed: {str(e)}"}
    
    def _extract_nodes_for_analysis(self, tree_structure: Dict[str, Any], source_node_id: str) -> List[Dict[str, Any]]:
        """提取用于AI分析的节点信息"""
        nodes = []
        
        def extract_node(node: Dict[str, Any], depth: int = 0, path: str = ""):
            if depth > 4:  # 限制深度
                return
            
            node_info = {
                "id": node.get("id", ""),
                "name": node.get("name", ""),
                "type": node.get("type", ""),
                "depth": depth,
                "path": f"{path}/{node.get('name', '')}" if path else node.get("name", ""),
                "source_node_id": source_node_id,
                "children_count": len(node.get("children", [])),
                "properties": self._extract_node_properties(node)
            }
            
            nodes.append(node_info)
            
            # 递归处理子节点
            for child in node.get("children", []):
                extract_node(child, depth + 1, node_info["path"])
        
        extract_node(tree_structure)
        return nodes
    
    def _extract_node_properties(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """提取节点属性信息"""
        properties = {}
        
        # 提取基本属性
        if "absoluteBoundingBox" in node:
            properties["size"] = {
                "width": node["absoluteBoundingBox"].get("width", 0),
                "height": node["absoluteBoundingBox"].get("height", 0)
            }
        
        # 提取样式信息
        if "fills" in node and node["fills"]:
            properties["has_fill"] = True
            properties["fill_type"] = node["fills"][0].get("type", "unknown")
        
        if "strokes" in node and node["strokes"]:
            properties["has_stroke"] = True
        
        # 提取文本信息
        if "characters" in node:
            properties["text_content"] = node["characters"]
            properties["text_length"] = len(node["characters"])
        
        return properties
    
    def _generate_analysis_prompt(self, nodes_data: List[Dict[str, Any]]) -> str:
        """生成AI分析prompt"""
        prompt = f"""
你是一个专业的UI/UX设计系统专家。请分析以下Figma设计文件中的组件，识别哪些组件适合抽离为可复用组件。

设计文件包含 {len(nodes_data)} 个节点，请从以下角度分析：

1. **重复性分析**：识别名称相同或功能相似的组件
2. **功能分析**：分析组件的功能和用途
3. **复杂度分析**：评估组件的复杂程度
4. **可复用性评估**：判断是否适合抽离为组件
5. **优先级排序**：按重要性排序推荐抽离的组件

节点数据：
{json.dumps(nodes_data, ensure_ascii=False, indent=2)}

请提供以下格式的分析结果：
{{
  "reusable_components": [
    {{
      "name": "组件名称",
      "type": "组件类型",
      "reusability_score": 85,
      "priority": "high/medium/low",
      "reasoning": "抽离理由",
      "suggested_name": "建议的组件名称",
      "similar_components": ["相似组件列表"],
      "usage_scenarios": ["使用场景"],
      "implementation_notes": "实现建议"
    }}
  ],
  "analysis_summary": {{
    "total_candidates": 数量,
    "high_priority": 数量,
    "medium_priority": 数量,
    "low_priority": 数量,
    "recommendations": "总体建议"
  }}
}}
"""
        return prompt
    
    def _simulate_ai_analysis(self, nodes_data: List[Dict[str, Any]], prompt: str) -> Dict[str, Any]:
        """模拟AI分析结果（实际项目中替换为真实AI调用）"""
        
        # 按名称分组分析
        name_groups = {}
        for node in nodes_data:
            name = node.get("name", "")
            if name:
                if name not in name_groups:
                    name_groups[name] = []
                name_groups[name].append(node)
        
        # 识别重复组件
        reusable_components = []
        for name, instances in name_groups.items():
            if len(instances) > 1:
                # 分析组件类型
                node_type = instances[0].get("type", "UNKNOWN")
                
                # 计算可复用性分数
                reusability_score = self._calculate_ai_reusability_score(instances)
                
                # 确定优先级
                priority = self._determine_priority(reusability_score, len(instances))
                
                # 生成推理
                reasoning = self._generate_reasoning(name, instances, node_type)
                
                # 找到相似组件
                similar_components = self._find_similar_components(name, name_groups)
                
                component_analysis = {
                    "name": name,
                    "type": node_type,
                    "reusability_score": reusability_score,
                    "priority": priority,
                    "reasoning": reasoning,
                    "suggested_name": self._suggest_component_name(name, node_type),
                    "similar_components": similar_components,
                    "usage_scenarios": self._suggest_usage_scenarios(name, node_type),
                    "implementation_notes": self._generate_implementation_notes(name, instances),
                    "instances": [
                        {
                            "id": inst["id"],
                            "path": inst["path"],
                            "source_node_id": inst["source_node_id"]
                        } for inst in instances
                    ]
                }
                
                reusable_components.append(component_analysis)
        
        # 按可复用性分数排序
        reusable_components.sort(key=lambda x: x["reusability_score"], reverse=True)
        
        # 生成分析摘要
        high_priority = len([c for c in reusable_components if c["priority"] == "high"])
        medium_priority = len([c for c in reusable_components if c["priority"] == "medium"])
        low_priority = len([c for c in reusable_components if c["priority"] == "low"])
        
        analysis_summary = {
            "total_candidates": len(reusable_components),
            "high_priority": high_priority,
            "medium_priority": medium_priority,
            "low_priority": low_priority,
            "recommendations": self._generate_overall_recommendations(reusable_components)
        }
        
        return {
            "file_key": nodes_data[0].get("source_node_id", "").split(":")[0] if nodes_data else "",
            "analyzed_nodes": len(nodes_data),
            "reusable_components": reusable_components,
            "analysis_summary": analysis_summary,
            "ai_prompt_used": prompt
        }
    
    def _calculate_ai_reusability_score(self, instances: List[Dict[str, Any]]) -> int:
        """计算AI可复用性分数"""
        score = 0
        
        # 重复次数权重
        count = len(instances)
        if count >= 5: score += 30
        elif count >= 3: score += 20
        elif count >= 2: score += 10
        
        # 跨页面权重
        source_nodes = set(inst["source_node_id"] for inst in instances)
        if len(source_nodes) >= 3: score += 25
        elif len(source_nodes) >= 2: score += 15
        
        # 组件类型权重
        node_type = instances[0].get("type", "")
        if node_type in ["COMPONENT", "COMPONENT_SET", "INSTANCE"]: score += 20
        elif node_type == "FRAME": score += 15
        elif node_type == "GROUP": score += 10
        
        # 复杂度权重
        avg_children = sum(inst["children_count"] for inst in instances) / len(instances)
        if avg_children >= 5: score += 15
        elif avg_children >= 2: score += 10
        
        return min(score, 100)  # 最高100分
    
    def _determine_priority(self, score: int, count: int) -> str:
        """确定优先级"""
        if score >= 70 and count >= 3:
            return "high"
        elif score >= 50 and count >= 2:
            return "medium"
        else:
            return "low"
    
    def _generate_reasoning(self, name: str, instances: List[Dict[str, Any]], node_type: str) -> str:
        """生成抽离理由"""
        count = len(instances)
        source_count = len(set(inst["source_node_id"] for inst in instances))
        
        if count >= 5 and source_count >= 3:
            return f"该组件在{count}个位置重复出现，跨{source_count}个页面，具有很高的复用价值"
        elif count >= 3:
            return f"该组件重复出现{count}次，适合抽离为可复用组件"
        else:
            return f"该组件出现{count}次，可考虑抽离以提高设计一致性"
    
    def _find_similar_components(self, name: str, name_groups: Dict[str, List[Dict[str, Any]]]) -> List[str]:
        """找到相似组件"""
        similar = []
        for other_name in name_groups.keys():
            if other_name != name and (name in other_name or other_name in name):
                similar.append(other_name)
        return similar[:3]  # 最多返回3个
    
    def _suggest_component_name(self, name: str, node_type: str) -> str:
        """建议组件名称"""
        if "按钮" in name or "Button" in name:
            return "Button"
        elif "导航" in name or "Nav" in name:
            return "Navigation"
        elif "卡片" in name or "Card" in name:
            return "Card"
        else:
            return name
    
    def _suggest_usage_scenarios(self, name: str, node_type: str) -> List[str]:
        """建议使用场景"""
        scenarios = []
        if "按钮" in name or "Button" in name:
            scenarios = ["表单提交", "页面跳转", "操作确认"]
        elif "导航" in name or "Nav" in name:
            scenarios = ["页面导航", "菜单展开", "面包屑导航"]
        elif "卡片" in name or "Card" in name:
            scenarios = ["信息展示", "列表项", "产品展示"]
        else:
            scenarios = ["通用组件", "界面元素"]
        return scenarios
    
    def _generate_implementation_notes(self, name: str, instances: List[Dict[str, Any]]) -> str:
        """生成实现建议"""
        return f"建议将'{name}'抽离为独立组件，支持参数化配置，确保在不同场景下的灵活使用"
    
    def _generate_overall_recommendations(self, components: List[Dict[str, Any]]) -> str:
        """生成总体建议"""
        high_count = len([c for c in components if c["priority"] == "high"])
        if high_count >= 5:
            return "发现大量高优先级可复用组件，建议优先建立设计系统"
        elif high_count >= 2:
            return "发现多个高优先级组件，建议逐步建立组件库"
        else:
            return "可复用组件较少，建议关注设计一致性"
    
    def _save_ai_analysis_result(self, analysis_result: Dict[str, Any], file_key: str):
        """保存AI分析结果"""
        try:
            # 创建输出目录
            output_dir = self.file_saver.create_output_dir("ai_analysis")
            
            # 保存完整分析结果
            full_result_path = self.file_saver.save_json_file(
                analysis_result,
                f"ai_component_analysis_{file_key}.json",
                output_dir
            )
            
            # 保存简化版本
            simplified_result = {
                "file_key": analysis_result["file_key"],
                "summary": analysis_result["analysis_summary"],
                "top_components": analysis_result["reusable_components"][:10]  # 只保留前10个
            }
            
            simplified_path = self.file_saver.save_json_file(
                simplified_result,
                f"simplified_ai_analysis_{file_key}.json",
                output_dir
            )
            
            logger.info(f"AI analysis saved to: {full_result_path}")
            logger.info(f"Simplified AI analysis saved to: {simplified_path}")
            
        except Exception as e:
            logger.error(f"Error saving AI analysis result: {e}")
