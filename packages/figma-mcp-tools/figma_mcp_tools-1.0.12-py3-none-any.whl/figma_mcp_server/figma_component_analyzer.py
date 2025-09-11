import os
import json
import logging
from typing import Dict, List, Any, Optional
from .file_saver import FigmaFileSaver

logger = logging.getLogger(__name__)

class FigmaComponentAnalyzer:
    """Figma组件分析器 - 专门用于分析组件层级关系和重复性"""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.file_saver = FigmaFileSaver()
        
    def analyze_component_structure(self, file_key: str, node_ids: str = "0:0", max_depth: int = 4) -> Dict[str, Any]:
        """
        分析Figma文件中的组件结构，提取层级关系和重复性信息
        
        Args:
            file_key: Figma文件ID
            node_ids: 要分析的节点ID，默认为根节点
            max_depth: 最大分析深度
            
        Returns:
            包含组件结构分析结果的字典
        """
        try:
            # 获取完整的节点信息
            from .figma_tree_extractor import FigmaTreeExtractor
            tree_extractor = FigmaTreeExtractor(self.access_token)
            result = tree_extractor.extract_tree(file_key, node_ids, max_depth)
            
            if not result or "tree_structure" not in result:
                return {"error": "Failed to extract tree structure"}
            
            tree_structure = result["tree_structure"]
            file_name = result.get("file_name", "Unknown")
            
            # 分析组件结构
            component_analysis = self._analyze_components(tree_structure)
            
            # 生成roadmap
            roadmap = self._generate_component_roadmap(component_analysis)
            
            # 识别可复用组件
            reusable_components = self._identify_reusable_components(component_analysis)
            
            analysis_result = {
                "file_name": file_name,
                "file_key": file_key,
                "analysis_summary": {
                    "total_components": component_analysis["total_components"],
                    "unique_components": component_analysis["unique_components"],
                    "reusable_candidates": len(reusable_components),
                    "max_depth": max_depth
                },
                "component_roadmap": roadmap,
                "reusable_components": reusable_components,
                "component_statistics": component_analysis["statistics"]
            }
            
            # 保存分析结果
            self._save_analysis_result(analysis_result, file_key)
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error analyzing component structure: {e}")
            return {"error": f"Analysis failed: {str(e)}"}
    
    def _analyze_components(self, tree_structure: Dict[str, Any]) -> Dict[str, Any]:
        """分析组件结构，提取层级关系和重复性"""
        components = []
        component_names = {}
        component_types = {}
        
        def extract_component_info(node: Dict[str, Any], depth: int = 0, path: str = ""):
            """递归提取组件信息"""
            node_id = node.get("id", "")
            node_name = node.get("name", "")
            node_type = node.get("type", "")
            
            # 构建完整路径
            current_path = f"{path}/{node_name}" if path else node_name
            
            component_info = {
                "id": node_id,
                "name": node_name,
                "type": node_type,
                "depth": depth,
                "path": current_path,
                "children_count": 0,
                "is_component": node_type in ["COMPONENT", "COMPONENT_SET", "INSTANCE"],
                "is_frame": node_type == "FRAME",
                "is_group": node_type == "GROUP"
            }
            
            # 统计组件名称出现次数
            if node_name:
                component_names[node_name] = component_names.get(node_name, 0) + 1
                component_types[node_name] = node_type
            
            # 处理子节点
            children = node.get("children", [])
            component_info["children_count"] = len(children)
            
            for child in children:
                extract_component_info(child, depth + 1, current_path)
            
            components.append(component_info)
        
        # 从根节点开始分析
        extract_component_info(tree_structure)
        
        # 统计信息
        statistics = {
            "total_nodes": len(components),
            "components": len([c for c in components if c["is_component"]]),
            "frames": len([c for c in components if c["is_frame"]]),
            "groups": len([c for c in components if c["is_group"]]),
            "max_depth": max([c["depth"] for c in components]) if components else 0,
            "avg_children": sum([c["children_count"] for c in components]) / len(components) if components else 0
        }
        
        return {
            "components": components,
            "component_names": component_names,
            "component_types": component_types,
            "total_components": len(components),
            "unique_components": len(set([c["name"] for c in components if c["name"]])),
            "statistics": statistics
        }
    
    def _generate_component_roadmap(self, component_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成组件roadmap，只保留层级关系和组件名称"""
        roadmap = []
        
        def add_to_roadmap(components: List[Dict[str, Any]], parent_path: str = ""):
            """递归构建roadmap"""
            for component in components:
                if component["depth"] == 0:  # 只处理根级别组件
                    roadmap_item = {
                        "name": component["name"],
                        "type": component["type"],
                        "depth": component["depth"],
                        "path": component["path"],
                        "children_count": component["children_count"],
                        "repetition_count": component_analysis["component_names"].get(component["name"], 1),
                        "is_reusable_candidate": component_analysis["component_names"].get(component["name"], 1) > 1
                    }
                    roadmap.append(roadmap_item)
        
        # 按深度排序，只保留顶层结构
        top_level_components = [c for c in component_analysis["components"] if c["depth"] <= 2]
        add_to_roadmap(top_level_components)
        
        return roadmap
    
    def _identify_reusable_components(self, component_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """识别可复用组件候选"""
        reusable_candidates = []
        component_names = component_analysis["component_names"]
        
        for name, count in component_names.items():
            if count > 1:  # 重复出现超过1次
                component_type = component_analysis["component_types"].get(name, "UNKNOWN")
                
                # 查找该组件的所有实例
                instances = [c for c in component_analysis["components"] if c["name"] == name]
                
                candidate = {
                    "name": name,
                    "type": component_type,
                    "repetition_count": count,
                    "instances": [
                        {
                            "id": inst["id"],
                            "path": inst["path"],
                            "depth": inst["depth"]
                        } for inst in instances
                    ],
                    "priority": self._calculate_reusability_priority(count, component_type, instances),
                    "suggested_action": self._suggest_action(count, component_type)
                }
                
                reusable_candidates.append(candidate)
        
        # 按优先级排序
        reusable_candidates.sort(key=lambda x: x["priority"], reverse=True)
        
        return reusable_candidates
    
    def _calculate_reusability_priority(self, count: int, component_type: str, instances: List[Dict[str, Any]]) -> int:
        """计算可复用性优先级"""
        priority = 0
        
        # 重复次数权重
        if count >= 5:
            priority += 10
        elif count >= 3:
            priority += 7
        elif count >= 2:
            priority += 5
        
        # 组件类型权重
        if component_type in ["COMPONENT", "COMPONENT_SET"]:
            priority += 3
        elif component_type == "FRAME":
            priority += 2
        elif component_type == "GROUP":
            priority += 1
        
        # 深度权重（越浅层优先级越高）
        avg_depth = sum([inst["depth"] for inst in instances]) / len(instances)
        if avg_depth <= 2:
            priority += 3
        elif avg_depth <= 4:
            priority += 2
        else:
            priority += 1
        
        return priority
    
    def _suggest_action(self, count: int, component_type: str) -> str:
        """建议操作"""
        if count >= 5:
            return "强烈建议创建可复用组件"
        elif count >= 3:
            return "建议创建可复用组件"
        elif count >= 2:
            return "考虑创建可复用组件"
        else:
            return "无需操作"
    
    def _save_analysis_result(self, analysis_result: Dict[str, Any], file_key: str):
        """保存分析结果"""
        try:
            # 保存完整分析结果
            full_result_path = self.file_saver.save_json(
                analysis_result,
                f"component_analysis_{file_key}.json",
                "component_analysis"
            )
            
            # 保存简化的roadmap
            roadmap_data = {
                "file_name": analysis_result["file_name"],
                "file_key": analysis_result["file_key"],
                "summary": analysis_result["analysis_summary"],
                "roadmap": analysis_result["component_roadmap"],
                "reusable_components": analysis_result["reusable_components"]
            }
            
            roadmap_path = self.file_saver.save_json(
                roadmap_data,
                f"component_roadmap_{file_key}.json",
                "component_roadmap"
            )
            
            logger.info(f"Component analysis saved to: {full_result_path}")
            logger.info(f"Component roadmap saved to: {roadmap_path}")
            
        except Exception as e:
            logger.error(f"Error saving analysis result: {e}")
