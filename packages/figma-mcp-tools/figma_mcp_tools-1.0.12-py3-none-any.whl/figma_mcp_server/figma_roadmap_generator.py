import os
import json
import logging
from typing import Dict, List, Any, Optional
from .file_saver import FigmaFileSaver

logger = logging.getLogger(__name__)

class FigmaRoadmapGenerator:
    """Figma节点信息Roadmap生成器 - 专门用于生成简化的节点层级关系图"""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.file_saver = FigmaFileSaver()
        
    def generate_node_roadmap(self, file_key: str, node_ids: str = "0:0", max_depth: int = 4) -> Dict[str, Any]:
        """
        生成Figma文件的节点信息roadmap，只保留层级关系和节点名称
        
        Args:
            file_key: Figma文件ID
            node_ids: 要分析的节点ID列表，用逗号分隔，默认为根节点
            max_depth: 最大分析深度
            
        Returns:
            包含节点roadmap的字典
        """
        try:
            # 解析节点ID列表
            node_id_list = [id.strip() for id in node_ids.split(",") if id.strip()]
            
            # 获取完整的节点信息
            from .figma_tree_extractor import FigmaTreeExtractor
            tree_extractor = FigmaTreeExtractor(self.access_token)
            
            all_roadmaps = []
            all_statistics = []
            file_name = "Unknown"
            
            # 为每个节点ID生成roadmap
            for node_id in node_id_list:
                result = tree_extractor.extract_tree(file_key, node_id, max_depth)
                
                if not result or "nodes" not in result or node_id not in result["nodes"]:
                    continue
                
                tree_structure = result["nodes"][node_id]["tree_structure"]
                file_name = result.get("file_name", "Unknown")
                
                # 生成roadmap
                roadmap = self._extract_roadmap_structure(tree_structure, max_depth, node_id)
                all_roadmaps.extend(roadmap)
                
                # 统计信息
                statistics = self._calculate_roadmap_statistics(roadmap)
                all_statistics.append(statistics)
            
            # 合并统计信息
            combined_statistics = self._merge_statistics(all_statistics)
            
            # 分析跨页面重复性
            cross_page_analysis = self._analyze_cross_page_reusability(all_roadmaps)
            
            roadmap_result = {
                "file_name": file_name,
                "file_key": file_key,
                "max_depth": max_depth,
                "analyzed_node_ids": node_id_list,
                "roadmap_summary": {
                    "total_nodes": combined_statistics["total_nodes"],
                    "unique_node_names": combined_statistics["unique_node_names"],
                    "max_depth_found": combined_statistics["max_depth_found"],
                    "node_types": combined_statistics["node_types"],
                    "cross_page_reusable_candidates": len(cross_page_analysis["reusable_candidates"])
                },
                "node_roadmap": all_roadmaps,
                "cross_page_analysis": cross_page_analysis,
                "node_statistics": combined_statistics
            }
            
            # 保存roadmap结果
            self._save_roadmap_result(roadmap_result, file_key)
            
            return roadmap_result
            
        except Exception as e:
            logger.error(f"Error generating node roadmap: {e}")
            return {"error": f"Roadmap generation failed: {str(e)}"}
    
    def _extract_roadmap_structure(self, tree_structure: Dict[str, Any], max_depth: int, source_node_id: str = "") -> List[Dict[str, Any]]:
        """提取简化的roadmap结构，只保留层级关系和节点名称"""
        roadmap = []
        
        def extract_node_info(node: Dict[str, Any], depth: int = 0, path: str = ""):
            """递归提取节点信息"""
            if depth > max_depth:
                return
            
            node_id = node.get("id", "")
            node_name = node.get("name", "")
            node_type = node.get("type", "")
            
            # 构建完整路径
            current_path = f"{path}/{node_name}" if path else node_name
            
            # 只保留关键信息
            node_info = {
                "id": node_id,
                "name": node_name,
                "type": node_type,
                "depth": depth,
                "path": current_path,
                "children_count": 0,
                "source_node_id": source_node_id  # 记录来源节点ID
            }
            
            # 处理子节点
            children = node.get("children", [])
            node_info["children_count"] = len(children)
            
            # 添加到roadmap
            roadmap.append(node_info)
            
            # 递归处理子节点
            for child in children:
                extract_node_info(child, depth + 1, current_path)
        
        # 从根节点开始提取
        extract_node_info(tree_structure)
        
        return roadmap
    
    def _calculate_roadmap_statistics(self, roadmap: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算roadmap统计信息"""
        if not roadmap:
            return {
                "total_nodes": 0,
                "unique_node_names": 0,
                "max_depth_found": 0,
                "node_types": {}
            }
        
        # 统计节点类型
        node_types = {}
        for node in roadmap:
            node_type = node.get("type", "UNKNOWN")
            node_types[node_type] = node_types.get(node_type, 0) + 1
        
        # 统计唯一节点名称
        unique_names = set([node.get("name", "") for node in roadmap if node.get("name")])
        
        # 最大深度
        max_depth_found = max([node.get("depth", 0) for node in roadmap])
        
        return {
            "total_nodes": len(roadmap),
            "unique_node_names": len(unique_names),
            "max_depth_found": max_depth_found,
            "node_types": node_types
        }
    
    def _merge_statistics(self, statistics_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """合并多个统计信息"""
        if not statistics_list:
            return {
                "total_nodes": 0,
                "unique_node_names": 0,
                "max_depth_found": 0,
                "node_types": {}
            }
        
        merged = {
            "total_nodes": sum(stat["total_nodes"] for stat in statistics_list),
            "unique_node_names": 0,
            "max_depth_found": max(stat["max_depth_found"] for stat in statistics_list),
            "node_types": {}
        }
        
        # 合并节点类型统计
        for stat in statistics_list:
            for node_type, count in stat["node_types"].items():
                merged["node_types"][node_type] = merged["node_types"].get(node_type, 0) + count
        
        return merged
    
    def _analyze_cross_page_reusability(self, all_roadmaps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析跨页面重复性"""
        # 按名称分组
        name_groups = {}
        for node in all_roadmaps:
            name = node.get("name", "")
            if name:
                if name not in name_groups:
                    name_groups[name] = []
                name_groups[name].append(node)
        
        # 识别重复的组件
        reusable_candidates = []
        for name, instances in name_groups.items():
            if len(instances) > 1:
                # 按来源节点ID分组
                source_groups = {}
                for instance in instances:
                    source_id = instance.get("source_node_id", "")
                    if source_id not in source_groups:
                        source_groups[source_id] = []
                    source_groups[source_id].append(instance)
                
                # 如果跨多个来源节点，说明是跨页面重复
                if len(source_groups) > 1:
                    candidate = {
                        "name": name,
                        "type": instances[0].get("type", "UNKNOWN"),
                        "total_occurrences": len(instances),
                        "cross_page_occurrences": len(source_groups),
                        "source_nodes": list(source_groups.keys()),
                        "instances": instances,
                        "priority": self._calculate_cross_page_priority(len(instances), len(source_groups), instances[0].get("type", ""))
                    }
                    reusable_candidates.append(candidate)
        
        # 按优先级排序
        reusable_candidates.sort(key=lambda x: x["priority"], reverse=True)
        
        return {
            "reusable_candidates": reusable_candidates,
            "total_cross_page_candidates": len(reusable_candidates)
        }
    
    def _calculate_cross_page_priority(self, total_count: int, cross_page_count: int, node_type: str) -> int:
        """计算跨页面可复用性优先级"""
        priority = 0
        
        # 总出现次数权重
        if total_count >= 5:
            priority += 10
        elif total_count >= 3:
            priority += 7
        elif total_count >= 2:
            priority += 5
        
        # 跨页面次数权重
        if cross_page_count >= 3:
            priority += 8
        elif cross_page_count >= 2:
            priority += 5
        
        # 节点类型权重
        if node_type in ["COMPONENT", "COMPONENT_SET", "INSTANCE"]:
            priority += 3
        elif node_type == "FRAME":
            priority += 2
        elif node_type == "GROUP":
            priority += 1
        
        return priority
    
    def _save_roadmap_result(self, roadmap_result: Dict[str, Any], file_key: str):
        """保存roadmap结果"""
        try:
            # 创建输出目录
            output_dir = self.file_saver.create_output_dir("node_roadmap")
            
            # 保存完整roadmap结果
            full_result_path = self.file_saver.save_json_file(
                roadmap_result,
                f"node_roadmap_{file_key}.json",
                output_dir
            )
            
            # 保存简化的roadmap（只包含关键信息）
            simplified_roadmap = {
                "file_name": roadmap_result["file_name"],
                "file_key": roadmap_result["file_key"],
                "summary": roadmap_result["roadmap_summary"],
                "roadmap": roadmap_result["node_roadmap"]
            }
            
            simplified_path = self.file_saver.save_json_file(
                simplified_roadmap,
                f"simplified_roadmap_{file_key}.json",
                output_dir
            )
            
            logger.info(f"Node roadmap saved to: {full_result_path}")
            logger.info(f"Simplified roadmap saved to: {simplified_path}")
            
        except Exception as e:
            logger.error(f"Error saving roadmap result: {e}")
