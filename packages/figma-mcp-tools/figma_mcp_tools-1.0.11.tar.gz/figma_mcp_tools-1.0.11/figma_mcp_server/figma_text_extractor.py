#!/usr/bin/env python3
"""
Figma 文本提取器类
专门用于从Figma节点中提取文本内容
"""

import requests
import json
import os
from typing import List, Dict, Any
try:
    from .file_saver import FigmaFileSaver
except ImportError:
    from file_saver import FigmaFileSaver

class FigmaTextExtractor:
    def __init__(self, access_token: str = None):
        """初始化文本提取器"""
        self.access_token = access_token or os.getenv("FIGMA_ACCESS_TOKEN")
        if not self.access_token:
            raise ValueError("需要提供 access_token 或设置环境变量 FIGMA_ACCESS_TOKEN")
        self.file_saver = FigmaFileSaver()
    
    def get_figma_file(self, file_key: str) -> Dict[str, Any]:
        """获取Figma文件信息"""
        url = f"https://api.figma.com/v1/files/{file_key}"
        headers = {"X-Figma-Token": self.access_token}
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"请求错误: {e}")
            return None
    
    def extract_text_from_node(self, node: Dict[str, Any], depth: int = 0, max_depth: int = 4) -> List[Dict[str, Any]]:
        """递归提取节点中的文本信息"""
        text_nodes = []
        
        # 检查当前节点是否为文本节点
        if node.get("type") == "TEXT":
            text_info = {
                "id": node.get("id"),
                "name": node.get("name"),
                "type": node.get("type"),
                "depth": depth,
                "characters": node.get("characters", ""),
                "style": node.get("style", {}),
                "fills": node.get("fills", []),
                "strokes": node.get("strokes", []),
                "effects": node.get("effects", []),
                "absoluteBoundingBox": node.get("absoluteBoundingBox"),
                "constraints": node.get("constraints"),
                "layoutMode": node.get("layoutMode"),
                "primaryAxisSizingMode": node.get("primaryAxisSizingMode"),
                "counterAxisSizingMode": node.get("counterAxisSizingMode"),
                "primaryAxisAlignItems": node.get("primaryAxisAlignItems"),
                "counterAxisAlignItems": node.get("counterAxisAlignItems"),
                "paddingLeft": node.get("paddingLeft"),
                "paddingRight": node.get("paddingRight"),
                "paddingTop": node.get("paddingTop"),
                "paddingBottom": node.get("paddingBottom"),
                "itemSpacing": node.get("itemSpacing"),
                "cornerRadius": node.get("cornerRadius"),
                "strokeWeight": node.get("strokeWeight"),
                "strokeAlign": node.get("strokeAlign"),
                "opacity": node.get("opacity"),
                "blendMode": node.get("blendMode"),
                "isMask": node.get("isMask"),
                "styles": node.get("styles", {}),
                "boundVariables": node.get("boundVariables", {}),
                "overrides": node.get("overrides", [])
            }
            text_nodes.append(text_info)
        
        # 如果达到最大深度，停止递归
        if depth >= max_depth:
            return text_nodes
        
        # 递归处理子节点
        children = node.get("children", [])
        for child in children:
            child_text_nodes = self.extract_text_from_node(child, depth + 1, max_depth)
            text_nodes.extend(child_text_nodes)
        
        return text_nodes
    
    def extract_texts(self, file_key: str, node_ids: str, max_depth: int = 4) -> Dict[str, Any]:
        """提取指定节点的文本内容"""
        print(f"正在获取文件 {file_key} 的文本内容...")
        print(f"目标节点: {node_ids}")
        print(f"最大深度: {max_depth}")
        
        # 获取Figma文件信息
        file_data = self.get_figma_file(file_key)
        if not file_data:
            return None
        
        document = file_data.get("document")
        if not document:
            print("未找到文档数据")
            return None
        
        print(f"文件名称: {file_data.get('name', 'Unknown')}")
        
        # 解析节点ID列表
        target_node_ids = [node_id.strip() for node_id in node_ids.split(",")]
        
        # 提取文本信息
        all_text_nodes = []
        found_nodes = []
        not_found_nodes = []
        
        for node_id in target_node_ids:
            # 查找指定节点
            target_node = self.find_node_by_id(document, node_id)
            if target_node:
                found_nodes.append(node_id)
                text_nodes = self.extract_text_from_node(target_node, depth=0, max_depth=max_depth)
                all_text_nodes.extend(text_nodes)
                print(f"✅ 找到节点 {node_id}: {len(text_nodes)} 个文本节点")
            else:
                not_found_nodes.append(node_id)
                print(f"❌ 未找到节点 {node_id}")
        
        # 按节点ID分组文本
        texts_by_node = {}
        for text_node in all_text_nodes:
            # 找到文本节点所属的根节点
            root_node_id = self.find_root_node_id(document, text_node["id"])
            if root_node_id not in texts_by_node:
                texts_by_node[root_node_id] = []
            texts_by_node[root_node_id].append(text_node)
        
        # 创建结果结构
        result = {
            "file_key": file_key,
            "file_name": file_data.get("name", ""),
            "last_modified": file_data.get("lastModified", ""),
            "version": file_data.get("version", ""),
            "target_nodes": node_ids,
            "max_depth": max_depth,
            "found_nodes": found_nodes,
            "not_found_nodes": not_found_nodes,
            "total_text_nodes": len(all_text_nodes),
            "texts_by_node": texts_by_node,
            "all_text_nodes": all_text_nodes,
            "text_summary": {
                "total_characters": sum(len(node.get("characters", "")) for node in all_text_nodes),
                "unique_texts": len(set(node.get("characters", "") for node in all_text_nodes)),
                "text_nodes_count": len(all_text_nodes)
            }
        }
        
        # 输出结果
        if all_text_nodes:
            print(f"\n找到 {len(all_text_nodes)} 个文本节点:")
            
            for node_id, texts in texts_by_node.items():
                print(f"\n📝 节点 {node_id} ({len(texts)} 个文本):")
                for i, text_node in enumerate(texts, 1):
                    characters = text_node.get("characters", "")
                    print(f"  {i}. {characters[:50]}{'...' if len(characters) > 50 else ''}")
            
            print(f"\n📊 文本统计:")
            print(f"  总字符数: {result['text_summary']['total_characters']}")
            print(f"  唯一文本数: {result['text_summary']['unique_texts']}")
            print(f"  文本节点数: {result['text_summary']['text_nodes_count']}")
        else:
            print("未找到任何文本节点")
        
        return result
    
    def find_node_by_id(self, node: Dict[str, Any], target_id: str) -> Dict[str, Any]:
        """递归查找指定ID的节点"""
        if node.get("id") == target_id:
            return node
        
        children = node.get("children", [])
        for child in children:
            result = self.find_node_by_id(child, target_id)
            if result:
                return result
        
        return None
    
    def find_root_node_id(self, node: Dict[str, Any], target_id: str, current_root: str = None) -> str:
        """递归查找文本节点所属的根节点ID"""
        if current_root is None:
            current_root = node.get("id")
        
        if node.get("id") == target_id:
            return current_root
        
        children = node.get("children", [])
        for child in children:
            result = self.find_root_node_id(child, target_id, current_root)
            if result:
                return result
        
        return None

def main():
    """主函数 - 保持向后兼容"""
    import sys
    
    # 检查命令行参数
    if len(sys.argv) < 3:
        print("使用方法: python3 figma_text_extractor.py <file_key> <node_ids> [max_depth]")
        print("示例: python3 figma_text_extractor.py your_figma_file_key_here")
        print("示例: python3 figma_text_extractor.py your_figma_file_key_here your_node_id_here")
        print("示例: python3 figma_text_extractor.py your_figma_file_key_here your_node_id_here 4")
        print("\n请确保设置了环境变量 FIGMA_ACCESS_TOKEN")
        sys.exit(1)
    
    file_key = sys.argv[1]
    node_ids = sys.argv[2]
    max_depth = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    
    try:
        extractor = FigmaTextExtractor()
        result = extractor.extract_texts(file_key, node_ids, max_depth)
        
        if result:
            # 使用文件保存器保存文本信息
            save_result = extractor.file_saver.save_text_info(file_key, result)
            text_path = save_result["text_path"]
            summary_path = save_result["summary_path"]
            
            print(f"\n文本信息已保存到: {text_path}")
            print(f"文本摘要已保存到: {summary_path}")
    
    except ValueError as e:
        print(f"错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
