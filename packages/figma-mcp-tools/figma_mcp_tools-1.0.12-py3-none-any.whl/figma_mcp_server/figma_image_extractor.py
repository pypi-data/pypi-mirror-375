#!/usr/bin/env python3
"""
Figma 图片获取器类
使用环境变量 FIGMA_ACCESS_TOKEN 存储访问令牌
获取指定节点的图片
"""

import requests
import json
import os
from typing import Dict, Any, List
from .file_saver import FigmaFileSaver

class FigmaImageExtractor:
    def __init__(self, access_token: str = None):
        """初始化提取器"""
        self.access_token = access_token or os.getenv("FIGMA_ACCESS_TOKEN")
        if not self.access_token:
            raise ValueError("需要提供 access_token 或设置环境变量 FIGMA_ACCESS_TOKEN")
        self.file_saver = FigmaFileSaver()
    
    def get_figma_images(self, file_key: str, node_ids: str = None, **kwargs) -> Dict[str, Any]:
        """获取Figma图片"""
        url = f"https://api.figma.com/v1/images/{file_key}"
        params = {"ids": node_ids}
        
        # 添加可选参数
        if "format" in kwargs:
            params["format"] = kwargs["format"]
        if "scale" in kwargs:
            params["scale"] = kwargs["scale"]
        if "version" in kwargs:
            params["version"] = kwargs["version"]
        if "svg_outline_text" in kwargs:
            params["svg_outline_text"] = kwargs["svg_outline_text"]
        if "svg_include_id" in kwargs:
            params["svg_include_id"] = kwargs["svg_include_id"]
        if "svg_include_node_id" in kwargs:
            params["svg_include_node_id"] = kwargs["svg_include_node_id"]
        if "svg_simplify_stroke" in kwargs:
            params["svg_simplify_stroke"] = kwargs["svg_simplify_stroke"]
        if "contents_only" in kwargs:
            params["contents_only"] = kwargs["contents_only"]
        if "use_absolute_bounds" in kwargs:
            params["use_absolute_bounds"] = kwargs["use_absolute_bounds"]
        
        headers = {"X-Figma-Token": self.access_token}
        
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"请求错误: {e}")
            return None
    
    def download_image(self, url: str, filename: str) -> bool:
        """下载图片"""
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            return True
        except requests.exceptions.RequestException as e:
            print(f"下载图片失败: {e}")
            return False
    
    def extract_images(self, file_key: str, node_ids: str, format: str = "png", scale: float = 1.0, output_dir: str = None) -> Dict[str, Any]:
        """提取图片"""
        print(f"正在获取文件 {file_key} 的图片...")
        print(f"目标节点: {node_ids}")
        print(f"图片格式: {format}")
        print(f"缩放比例: {scale}")
        
        # 获取图片信息
        images_data = self.get_figma_images(
            file_key, 
            node_ids, 
            format=format,
            scale=scale
        )
        
        if not images_data:
            return None
        
        print(f"文件名称: {images_data.get('name', 'Unknown')}")
        print(f"最后修改: {images_data.get('lastModified', 'Unknown')}")
        print(f"版本: {images_data.get('version', 'Unknown')}")
        
        # 处理图片
        images = images_data.get("images", {})
        
        if not images:
            print("未找到任何图片")
            return None
        
        print(f"\n找到 {len(images)} 个图片:")
        
        # 保存图片信息
        result = {
            "file_key": file_key,
            "file_name": images_data.get("name", ""),
            "last_modified": images_data.get("lastModified", ""),
            "version": images_data.get("version", ""),
            "target_nodes": node_ids,
            "format": format,
            "scale": scale,
            "images": {}
        }
        
        success_count = 0
        
        # 使用文件保存器创建输出目录并保存图片信息
        save_result = self.file_saver.save_images_info(file_key, result)
        output_dir = save_result["output_dir"]
        info_path = save_result["info_path"]
        
        for node_id, image_url in images.items():
            if image_url:
                # 生成文件名
                filename = os.path.join(output_dir, f"{node_id}.{format}")
                
                print(f"\n下载图片: {node_id}")
                print(f"  URL: {image_url}")
                print(f"  保存到: {filename}")
                
                # 下载图片
                if self.download_image(image_url, filename):
                    print(f"  ✅ 下载成功")
                    success_count += 1
                    
                    # 获取文件大小
                    file_size = self.file_saver.get_file_size(filename)
                    print(f"  文件大小: {file_size:.1f} KB")
                else:
                    print(f"  ❌ 下载失败")
                
                result["images"][node_id] = {
                    "url": image_url,
                    "filename": filename,
                    "status": "success" if os.path.exists(filename) else "failed"
                }
            else:
                print(f"\n节点 {node_id}: 无法生成图片")
                result["images"][node_id] = {
                    "url": None,
                    "filename": None,
                    "status": "failed"
                }
        
        print(f"\n=== 下载完成 ===")
        print(f"成功下载: {success_count}/{len(images)} 个图片")
        print(f"图片保存在: {output_dir}/")
        print(f"图片信息保存在: {info_path}")
        
        return result
    
    def download_original_images_by_node(self, file_key: str, node_id: str, format: str = "png", output_dir: str = None) -> Dict[str, Any]:
        """通过节点ID下载原始背景图片
        
        这个方法会：
        1. 获取指定节点的详细信息
        2. 提取节点中所有的imageRef
        3. 获取文件的图像映射表
        4. 下载原始S3图片（无任何样式处理，如圆角等）
        
        Args:
            file_key: Figma文件ID
            node_id: 节点ID
            format: 图片格式 (png, jpg, svg)
            output_dir: 输出目录，默认为 original_images_{file_key}
            
        Returns:
            包含下载结果的字典
        """
        print(f"正在通过nodeId获取原始图片...")
        print(f"NodeId: {node_id}")
        print(f"图片格式: {format}")
        
        try:
            # 步骤1: 获取节点详细信息，找到imageRef
            print("🔍 步骤1: 获取节点详细信息...")
            node_data = self.get_node_data(file_key, node_id)
            if not node_data:
                return {"error": f"无法获取节点 {node_id} 的数据"}
            
            # 步骤2: 从节点数据中提取imageRef
            print("🔍 步骤2: 提取imageRef...")
            image_refs = self.extract_image_refs_from_node(node_data)
            if not image_refs:
                return {"error": f"节点 {node_id} 中没有找到imageRef"}
            
            print(f"✅ 找到 {len(image_refs)} 个imageRef: {image_refs}")
            
            # 步骤3: 获取所有图像映射
            print("🔍 步骤3: 获取图像映射...")
            images_mapping = self.get_images_mapping(file_key)
            if not images_mapping:
                return {"error": "无法获取图像映射"}
            
            # 步骤4: 下载原始图片
            print("🔍 步骤4: 下载原始图片...")
            return self.download_original_images_by_refs(file_key, node_id, image_refs, images_mapping, format, output_dir)
            
        except Exception as e:
            return {"error": f"处理失败: {str(e)}"}
        
        if not images_data:
            return None
        
        print(f"文件名称: {images_data.get('name', 'Unknown')}")
        print(f"最后修改: {images_data.get('lastModified', 'Unknown')}")
        print(f"版本: {images_data.get('version', 'Unknown')}")
        
        # 处理图片
        images = images_data.get("images", {})
        
        if not images:
            print("未找到任何图片")
            return None
        
        print(f"\n找到 {len(images)} 个图片:")
        
        # 保存图片信息
        result = {
            "file_key": file_key,
            "file_name": images_data.get("name", ""),
            "last_modified": images_data.get("lastModified", ""),
            "version": images_data.get("version", ""),
            "imgref": imgref,
            "format": format,
            "scale": scale,
            "images": {}
        }
        
        success_count = 0
        
        # 使用文件保存器创建输出目录并保存图片信息
        save_result = self.file_saver.save_images_info(file_key, result)
        output_dir = save_result["output_dir"]
        info_path = save_result["info_path"]
        
        for node_id, image_url in images.items():
            if image_url:
                # 生成文件名
                filename = os.path.join(output_dir, f"{node_id}_{imgref}.{format}")
                
                print(f"\n下载图片: {node_id} (imgref: {imgref})")
                print(f"  URL: {image_url}")
                print(f"  保存到: {filename}")
                
                # 下载图片
                if self.download_image(image_url, filename):
                    print(f"  ✅ 下载成功")
                    success_count += 1
                    
                    # 获取文件大小
                    file_size = self.file_saver.get_file_size(filename)
                    print(f"  文件大小: {file_size:.1f} KB")
                else:
                    print(f"  ❌ 下载失败")
                
                result["images"][node_id] = {
                    "url": image_url,
                    "filename": filename,
                    "status": "success" if os.path.exists(filename) else "failed"
                }
            else:
                print(f"\n节点 {node_id}: 无法生成图片")
                result["images"][node_id] = {
                    "url": None,
                    "filename": None,
                    "status": "failed"
                }
        
        print(f"\n=== 下载完成 ===")
        print(f"成功下载: {success_count}/{len(images)} 个图片")
        print(f"图片保存在: {output_dir}/")
        print(f"图片信息保存在: {info_path}")
        
        return result
    
    def get_figma_file_data(self, file_key: str) -> Dict[str, Any]:
        """获取Figma文件数据"""
        url = f"https://api.figma.com/v1/files/{file_key}"
        headers = {"X-Figma-Token": self.access_token}
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"获取文件数据失败: {e}")
            return None
    
    def find_nodes_by_imgref(self, file_data: Dict[str, Any], imgref: str) -> List[Dict[str, Any]]:
        """在文件数据中查找包含特定imgref的节点"""
        matching_nodes = []
        
        def search_nodes(nodes):
            if not nodes:
                return
            
            for node in nodes:
                # 检查当前节点是否包含目标imgref
                if self.node_contains_imgref(node, imgref):
                    matching_nodes.append(node)
                
                # 递归搜索子节点
                if "children" in node:
                    search_nodes(node["children"])
        
        # 搜索所有页面
        if "document" in file_data and "children" in file_data["document"]:
            search_nodes(file_data["document"]["children"])
        
        return matching_nodes
    
    def node_contains_imgref(self, node: Dict[str, Any], imgref: str) -> bool:
        """检查节点是否包含特定的imgref"""
        # 检查节点的fills属性
        if "fills" in node:
            for fill in node["fills"]:
                if "imageRef" in fill and fill["imageRef"] == imgref:
                    return True
        
        # 检查其他可能包含imageRef的属性
        for key, value in node.items():
            if isinstance(value, dict) and "imageRef" in value and value["imageRef"] == imgref:
                return True
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict) and "imageRef" in item and item["imageRef"] == imgref:
                        return True
        
        return False
    
    def get_node_data(self, file_key: str, node_id: str) -> Dict[str, Any]:
        """获取特定节点的详细信息"""
        url = f"https://api.figma.com/v1/files/{file_key}/nodes"
        params = {"ids": node_id}
        headers = {"X-Figma-Token": self.access_token}
        
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if "nodes" in data and node_id in data["nodes"]:
                return data["nodes"][node_id]["document"]
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"获取节点数据失败: {e}")
            return None
    
    def extract_image_refs_from_node(self, node_data: Dict[str, Any]) -> List[str]:
        """从节点数据中提取所有imageRef"""
        image_refs = []
        
        def search_for_image_refs(obj):
            if isinstance(obj, dict):
                if "imageRef" in obj:
                    image_refs.append(obj["imageRef"])
                for value in obj.values():
                    search_for_image_refs(value)
            elif isinstance(obj, list):
                for item in obj:
                    search_for_image_refs(item)
        
        search_for_image_refs(node_data)
        return list(set(image_refs))  # 去重
    
    def get_images_mapping(self, file_key: str) -> Dict[str, str]:
        """获取所有图像映射"""
        url = f"https://api.figma.com/v1/files/{file_key}/images"
        headers = {"X-Figma-Token": self.access_token}
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            # 检查响应结构：可能是 {"images": {...}} 或 {"meta": {"images": {...}}}
            if "images" in data:
                return data["images"]
            elif "meta" in data and "images" in data["meta"]:
                return data["meta"]["images"]
            else:
                print(f"❌ 未找到images字段，响应结构: {list(data.keys())}")
                return {}
            
        except requests.exceptions.RequestException as e:
            print(f"获取图像映射失败: {e}")
            return {}
    
    def download_original_images_by_refs(self, file_key: str, node_id: str, image_refs: List[str], 
                                       images_mapping: Dict[str, str], format: str, output_dir: str = None) -> Dict[str, Any]:
        """根据imageRef下载原始图片"""
        if output_dir is None:
            output_dir = f"original_images_{file_key}"
        
        os.makedirs(output_dir, exist_ok=True)
        
        result = {
            "file_key": file_key,
            "node_id": node_id,
            "image_refs": image_refs,
            "format": format,
            "images": {},
            "success_count": 0,
            "output_dir": output_dir
        }
        
        for i, image_ref in enumerate(image_refs, 1):
            print(f"\n📥 [{i}/{len(image_refs)}] 处理imageRef: {image_ref[:20]}...")
            
            if image_ref not in images_mapping:
                print(f"  ❌ 未找到imageRef对应的URL")
                result["images"][image_ref] = {
                    "status": "failed",
                    "error": "未找到对应的URL"
                }
                continue
            
            image_url = images_mapping[image_ref]
            print(f"  🔗 图片URL: {image_url}")
            
            try:
                # 下载图片
                img_response = requests.get(image_url, timeout=30)
                
                if img_response.status_code == 200:
                    # 保存图片
                    filename = f"{output_dir}/{node_id}_{image_ref}.{format}"
                    with open(filename, 'wb') as f:
                        f.write(img_response.content)
                    
                    file_size = len(img_response.content)
                    print(f"  ✅ 下载成功: {filename} ({file_size:,} bytes)")
                    result["success_count"] += 1
                    
                    result["images"][image_ref] = {
                        "status": "success",
                        "filename": filename,
                        "file_size": file_size,
                        "url": image_url
                    }
                else:
                    print(f"  ❌ 下载失败: {img_response.status_code}")
                    result["images"][image_ref] = {
                        "status": "failed",
                        "error": f"HTTP {img_response.status_code}"
                    }
                    
            except Exception as e:
                print(f"  ❌ 下载异常: {e}")
                result["images"][image_ref] = {
                    "status": "failed",
                    "error": str(e)
                }
        
        print(f"\n📊 下载结果: {result['success_count']}/{len(image_refs)} 成功")
        print(f"📁 图片保存在: {output_dir}/")
        
        return result

def main():
    """主函数 - 保持向后兼容"""
    import sys
    
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("使用方法: python3 figma_image_extractor.py <file_key> [node_ids] [format] [scale]")
        print("示例: python3 figma_image_extractor.py your_figma_file_key_here")
        print("示例: python3 figma_image_extractor.py your_figma_file_key_here your_node_id_here")
        print("示例: python3 figma_image_extractor.py your_figma_file_key_here your_node_id_here png 2")
        print("\n格式选项: jpg, png, svg, pdf")
        print("缩放选项: 0.01-4 (默认1)")
        print("\n请确保设置了环境变量 FIGMA_ACCESS_TOKEN")
        sys.exit(1)
    
    file_key = sys.argv[1]
    
    # 检查是否提供了node_ids
    if len(sys.argv) > 2:
        node_ids = sys.argv[2]
    else:
        print("错误: 请提供节点ID")
        print("使用方法: python3 figma_image_extractor.py <file_key> <node_ids> [format] [scale]")
        print("提示: 使用 list_nodes_depth2 工具获取节点ID")
        sys.exit(1)
    
    # 获取格式参数
    image_format = "png"  # 默认格式
    if len(sys.argv) > 3:
        image_format = sys.argv[3]
    
    # 获取缩放参数
    scale = 1  # 默认缩放
    if len(sys.argv) > 4:
        try:
            scale = float(sys.argv[4])
        except ValueError:
            print("缩放参数必须是数字")
            sys.exit(1)
    
    try:
        extractor = FigmaImageExtractor()
        result = extractor.extract_images(file_key, node_ids, image_format, scale)
        
        if not result:
            sys.exit(1)
    
    except ValueError as e:
        print(f"错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
