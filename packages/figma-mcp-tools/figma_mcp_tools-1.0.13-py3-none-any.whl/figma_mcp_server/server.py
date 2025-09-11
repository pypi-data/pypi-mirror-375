#!/usr/bin/env python3
"""
Figma MCP Server
将Figma工具功能暴露为MCP工具，供AI助手调用
"""

import asyncio
import json
import os
import sys
import logging
from typing import Any, Dict, List, Optional
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# 导入我们的Figma工具类
from .figma_tree_extractor import FigmaTreeExtractor
from .figma_image_extractor import FigmaImageExtractor
from .figma_frame_extractor import FigmaFrameExtractor
from .figma_node_lister import FigmaNodeLister
from .figma_text_extractor import FigmaTextExtractor
from .figma_component_analyzer import FigmaComponentAnalyzer
from .figma_roadmap_generator import FigmaRoadmapGenerator
from .figma_smart_component_analyzer import FigmaSmartComponentAnalyzer
from .file_saver import FigmaFileSaver

# MCP相关导入
try:
    from mcp.server import Server
    from mcp.server.models import InitializationOptions
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        Tool,
        TextContent,
        ImageContent,
        EmbeddedResource,
    )
except ImportError:
    print("请先安装MCP: pip install mcp")
    sys.exit(1)

# 创建MCP服务器
server = Server("figma-tools")

# Define prompts list
FIGMA_PROMPTS = [
    {
        "name": "figma_analysis",
        "description": "分析Figma设计文件的结构和内容",
        "arguments": {
            "type": "object",
            "properties": {
                "file_key": {
                    "type": "string",
                    "description": "Figma文件的唯一标识符"
                },
                "analysis_type": {
                    "type": "string",
                    "description": "分析类型：structure（结构分析）、content（内容分析）、complete（完整分析）",
                    "enum": ["structure", "content", "complete"],
                    "default": "complete"
                }
            },
            "required": ["file_key"]
        }
    },
    {
        "name": "figma_text_extraction",
        "description": "提取Figma设计文件中的文本内容",
        "arguments": {
            "type": "object",
            "properties": {
                "file_key": {
                    "type": "string",
                    "description": "Figma文件的唯一标识符"
                },
                "node_ids": {
                    "type": "string",
                    "description": "要分析的节点ID，用逗号分隔"
                },
                "extract_style": {
                    "type": "boolean",
                    "description": "是否提取文本样式信息",
                    "default": True
                }
            },
            "required": ["file_key"]
        }
    },
    {
        "name": "figma_image_export",
        "description": "导出Figma设计文件中的图片资源",
        "arguments": {
            "type": "object",
            "properties": {
                "file_key": {
                    "type": "string",
                    "description": "Figma文件的唯一标识符"
                },
                "node_ids": {
                    "type": "string",
                    "description": "要导出的节点ID，用逗号分隔"
                },
                "format": {
                    "type": "string",
                    "description": "图片格式：png、jpg、svg、pdf",
                    "default": "png"
                },
                "scale": {
                    "type": "number",
                    "description": "图片缩放比例：0.01-4",
                    "default": 1.0
                }
            },
            "required": ["file_key"]
        }
    },
    {
        "name": "figma_design_review",
        "description": "对Figma设计文件进行设计审查",
        "arguments": {
            "type": "object",
            "properties": {
                "file_key": {
                    "type": "string",
                    "description": "Figma文件的唯一标识符"
                },
                "review_aspects": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["layout", "typography", "colors", "spacing", "accessibility", "consistency"]
                    },
                    "description": "要审查的设计方面",
                    "default": ["layout", "typography", "colors"]
                }
            },
            "required": ["file_key"]
        }
    }
]

# Define tool list
FIGMA_TOOLS = [
    {
        "name": "extract_figma_tree",
        "title": "Extract Figma Tree Structure",
        "description": "Extract complete tree structure information of Figma nodes",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_key": {
                    "type": "string",
                    "description": "Unique identifier of the Figma file"
                },
                "node_ids": {
                    "type": "string", 
                    "description": "Node IDs, separated by commas. Use list_nodes_depth2 tool to get node IDs"
                },
                "depth": {
                    "type": "integer",
                    "description": "Tree structure depth, default 4",
                    "default": 4
                }
            },
            "required": ["file_key", "node_ids"]
        }
    },
    {
        "name": "download_figma_images",
        "title": "Download Figma Images",
        "description": "Download images of Figma nodes",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_key": {
                    "type": "string",
                    "description": "Unique identifier of the Figma file"
                },
                "node_ids": {
                    "type": "string",
                    "description": "Node IDs, separated by commas. Use list_nodes_depth2 tool to get node IDs"
                },
                "format": {
                    "type": "string",
                    "description": "Image format: png, jpg, svg, pdf",
                    "default": "png"
                },
                "scale": {
                    "type": "number",
                    "description": "Scale ratio: 0.01-4",
                    "default": 1.0
                }
            },
            "required": ["file_key", "node_ids"]
        }
    },
    {
        "name": "get_complete_node_data",
        "title": "Get Complete Node Data",
        "description": "Get complete data of Figma nodes (tree structure + images) and organize into folders. Output structure designed for AI understanding: nodesinfo.json provides structured data, image files provide visual reference. ⚠️ Note: This tool will consume a lot of API quota, recommend using list_nodes_depth2 to get node IDs first",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_key": {
                    "type": "string",
                    "description": "Unique identifier of the Figma file"
                },
                "node_ids": {
                    "type": "string",
                    "description": "Node IDs, separated by commas. Use list_nodes_depth2 tool to get node IDs"
                },
                "image_format": {
                    "type": "string",
                    "description": "Image format: png, jpg, svg, pdf",
                    "default": "png"
                },
                "image_scale": {
                    "type": "number",
                    "description": "Image scale ratio: 0.01-4",
                    "default": 1.0
                },
                "tree_depth": {
                    "type": "integer",
                    "description": "Tree structure depth",
                    "default": 4
                }
            },
            "required": ["file_key", "node_ids"]
        }
    },
    {
        "name": "extract_frame_nodes",
        "title": "Extract Frame Nodes",
        "description": "Extract Frame node information from Figma file",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_key": {
                    "type": "string",
                    "description": "Unique identifier of the Figma file"
                },
                "max_depth": {
                    "type": "integer",
                    "description": "Maximum depth, default 2",
                    "default": 2
                }
            },
            "required": ["file_key"]
        }
    },
    {
        "name": "list_nodes_depth2",
        "title": "List Nodes",
        "description": "List all node IDs and names in Figma file (depth limited to 2), help users find needed nodes",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_key": {
                    "type": "string",
                    "description": "Unique identifier of the Figma file"
                },
                "node_types": {
                    "type": "string",
                    "description": "Node types to include, separated by commas (e.g.: FRAME,COMPONENT,TEXT), leave empty for all types",
                    "default": ""
                }
            },
            "required": ["file_key"]
        }
    },
    {
        "name": "extract_text_content",
        "title": "Extract Text Content",
        "description": "Extract text content from Figma nodes, including text characters, styles, and formatting information",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_key": {
                    "type": "string",
                    "description": "Unique identifier of the Figma file"
                },
                "node_ids": {
                    "type": "string",
                    "description": "Node IDs, separated by commas. Use list_nodes_depth2 tool to get node IDs"
                },
                "max_depth": {
                    "type": "integer",
                    "description": "Maximum depth to search for text nodes, default 4",
                    "default": 4
                }
            },
            "required": ["file_key", "node_ids"]
        }
    },
    {
        "name": "figma_analysis",
        "title": "Figma Analysis",
        "description": "分析Figma设计文件的结构和内容",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_key": {
                    "type": "string",
                    "description": "Figma文件的唯一标识符"
                },
                "analysis_type": {
                    "type": "string",
                    "description": "分析类型：structure（结构分析）、content（内容分析）、complete（完整分析）",
                    "enum": ["structure", "content", "complete"],
                    "default": "complete"
                }
            },
            "required": ["file_key"]
        }
    },
    {
        "name": "figma_design_review",
        "title": "Figma Design Review",
        "description": "对Figma设计文件进行设计审查",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_key": {
                    "type": "string",
                    "description": "Figma文件的唯一标识符"
                },
                "review_aspects": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["layout", "typography", "colors", "spacing", "accessibility", "consistency"]
                    },
                    "description": "要审查的设计方面",
                    "default": ["layout", "typography", "colors"]
                }
            },
            "required": ["file_key"]
        }
    },
                    {
                    "name": "project_summary",
                    "title": "Project Summary",
                    "description": "根据项目文字内容总结项目相关信息",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "file_key": {
                                "type": "string",
                                "description": "Figma文件的唯一标识符"
                            },
                            "summary_type": {
                                "type": "string",
                                "description": "总结类型：overview（概览）、business（业务）、content（内容）、structure（结构）",
                                "enum": ["overview", "business", "content", "structure"],
                                "default": "overview"
                            },
                            "max_text_length": {
                                "type": "integer",
                                "description": "最大文本长度限制",
                                "default": 500
                            }
                        },
                        "required": ["file_key"]
                    }
                },
                {
                    "name": "analyze_component_structure",
                    "title": "Analyze Component Structure",
                    "description": "分析Figma文件中的组件结构，提取层级关系和重复性信息，识别可复用组件",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "file_key": {
                                "type": "string",
                                "description": "Figma文件的唯一标识符"
                            },
                            "node_ids": {
                                "type": "string",
                                "description": "要分析的节点ID，默认为根节点",
                                "default": "0:0"
                            },
                            "max_depth": {
                                "type": "integer",
                                "description": "最大分析深度",
                                "default": 4
                            }
                        },
                        "required": ["file_key"]
                    }
                },
                {
                    "name": "generate_node_roadmap",
                    "title": "Generate Node Roadmap",
                    "description": "生成Figma文件的节点信息roadmap，分析跨页面重复性，识别可复用组件",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "file_key": {
                                "type": "string",
                                "description": "Figma文件的唯一标识符"
                            },
                            "node_ids": {
                                "type": "string",
                                "description": "要分析的节点ID列表，用逗号分隔，支持跨页面分析",
                                "default": "0:0"
                            },
                            "max_depth": {
                                "type": "integer",
                                "description": "最大分析深度",
                                "default": 4
                            }
                        },
                        "required": ["file_key"]
                    }
                },
                {
                    "name": "smart_component_analysis",
                    "title": "Smart Component Analysis",
                    "description": "使用AI智能分析Figma组件可复用性，提供详细的分析报告和建议",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "file_key": {
                                "type": "string",
                                "description": "Figma文件的唯一标识符"
                            },
                            "node_ids": {
                                "type": "string",
                                "description": "要分析的节点ID列表，用逗号分隔，支持跨页面分析",
                                "default": "0:0"
                            },
                            "max_depth": {
                                "type": "integer",
                                "description": "最大分析深度",
                                "default": 4
                            }
                        },
                        "required": ["file_key"]
                    }
                },
    {
        "name": "download_original_images_by_node",
        "title": "Download Original Images by Node ID",
        "description": "Download original background images from a Figma node (without any styling like rounded corners). This method extracts imageRef from the node and downloads the raw S3 images.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_key": {
                    "type": "string",
                    "description": "Unique identifier of the Figma file"
                },
                "node_id": {
                    "type": "string",
                    "description": "Node ID - the method will extract imageRef from this node and download original images"
                },
                "format": {
                    "type": "string",
                    "description": "Image format: png, jpg, svg, pdf",
                    "default": "png"
                }
            },
            "required": ["file_key", "node_id"]
        }
    }

]

class FigmaMCPServer:
    def __init__(self):
        # Auto-setup virtual environment path
        self.setup_environment()
        
        self.access_token = os.getenv("FIGMA_ACCESS_TOKEN")
        if not self.access_token:
            print("Warning: FIGMA_ACCESS_TOKEN environment variable not set")
        
        self.tree_extractor = FigmaTreeExtractor(self.access_token) if self.access_token else None
        self.image_extractor = FigmaImageExtractor(self.access_token) if self.access_token else None
        self.frame_extractor = FigmaFrameExtractor(self.access_token) if self.access_token else None
        self.node_lister = FigmaNodeLister(self.access_token) if self.access_token else None
        self.text_extractor = FigmaTextExtractor(self.access_token) if self.access_token else None
        self.component_analyzer = FigmaComponentAnalyzer(self.access_token) if self.access_token else None
        self.roadmap_generator = FigmaRoadmapGenerator(self.access_token) if self.access_token else None
        self.smart_component_analyzer = FigmaSmartComponentAnalyzer(self.access_token) if self.access_token else None
        self.file_saver = FigmaFileSaver()
    
    def setup_environment(self):
        """Setup environment, including virtual environment path"""
        # Get current script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Check if virtual environment exists
        venv_path = os.path.join(script_dir, "figma_env")
        if os.path.exists(venv_path):
            # Add virtual environment site-packages to Python path
            if sys.platform == "win32":
                site_packages = os.path.join(venv_path, "Lib", "site-packages")
            else:
                site_packages = os.path.join(venv_path, "lib", "python3.10", "site-packages")
            
            if os.path.exists(site_packages):
                sys.path.insert(0, site_packages)
        
        # Add current directory to Python path
        if script_dir not in sys.path:
            sys.path.insert(0, script_dir)
    
    def get_node_name(self, tree_data: Dict[str, Any], node_id: str) -> str:
        """Get node name from tree structure data"""
        try:
            if "nodes" in tree_data and node_id in tree_data["nodes"]:
                node_name = tree_data["nodes"][node_id].get("name", "")
                return node_name.replace(':', '_').replace('/', '_').replace('\\', '_').strip() or f"node_{node_id.replace(':', '_')}"
            return f"node_{node_id.replace(':', '_')}"
        except Exception:
            return f"node_{node_id.replace(':', '_')}"
    
    def organize_files(self, file_key: str, node_ids: str, node_name: str, tree_result: Dict, image_result: Dict) -> Dict[str, Any]:
        """Organize files to specified folder"""
        import shutil
        
        # Create target folder
        first_node_id = node_ids.split(",")[0]
        target_dir = f"{node_name}_{first_node_id}"
        os.makedirs(target_dir, exist_ok=True)
        
        result = {
            "target_dir": target_dir,
            "files": {}
        }
        
        # Save tree structure file
        tree_file = f"{target_dir}/nodesinfo.json"
        with open(tree_file, 'w', encoding='utf-8') as f:
            json.dump(tree_result, f, indent=2, ensure_ascii=False)
        result["files"]["nodesinfo"] = tree_file
        
        # Process image files
        if image_result and "images" in image_result:
            for node_id, image_info in image_result["images"].items():
                if image_info.get("status") == "success" and image_info.get("filename"):
                    # Move image file to target directory
                    old_path = image_info["filename"]
                    new_path = f"{target_dir}/{node_id}.{image_result.get('format', 'png')}"
                    if os.path.exists(old_path):
                        shutil.move(old_path, new_path)
                        result["files"]["image"] = new_path
        
        return result

# 创建Figma MCP服务器实例（延迟初始化）
figma_server = None

def get_figma_server():
    """Get Figma server instance (lazy initialization)"""
    global figma_server
    if figma_server is None:
        figma_server = FigmaMCPServer()
    return figma_server

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available tools"""
    try:
        tools = []
        for tool_def in FIGMA_TOOLS:
            tools.append(Tool(**tool_def))
        
        return tools
    except Exception as e:
        logger.error(f"handle_list_tools error: {e}")
        raise

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> list[TextContent | ImageContent]:
    """Handle tool calls"""
    try:
        if name == "extract_figma_tree":
            return await handle_extract_tree(arguments)
        elif name == "download_figma_images":
            return await handle_download_images(arguments)
        elif name == "download_original_images_by_node":
            return await handle_download_by_imgref(arguments)
        elif name == "get_complete_node_data":
            return await handle_complete_data(arguments)
        elif name == "extract_frame_nodes":
            return await handle_extract_frames(arguments)
        elif name == "list_nodes_depth2":
            return await handle_list_nodes(arguments)
        elif name == "extract_text_content":
            return await handle_extract_text(arguments)
        elif name == "figma_analysis":
            return await handle_figma_analysis(arguments)
        elif name == "figma_design_review":
            return await handle_figma_design_review(arguments)
        elif name == "project_summary":
            return await handle_project_summary(arguments)
        elif name == "analyze_component_structure":
            return await handle_analyze_component_structure(arguments)
        elif name == "generate_node_roadmap":
            return await handle_generate_node_roadmap(arguments)
        elif name == "smart_component_analysis":
            return await handle_smart_component_analysis(arguments)
        else:
            logger.warning(f"Unknown tool: {name}")
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    except Exception as e:
        logger.error(f"handle_call_tool error: {e}")
        return [TextContent(type="text", text=f"Error executing tool: {str(e)}")]


async def handle_analyze_component_structure(arguments: Dict[str, Any]) -> list[TextContent]:
    """Handle component structure analysis"""
    file_key = arguments["file_key"]
    node_ids = arguments.get("node_ids", "0:0")
    max_depth = arguments.get("max_depth", 4)
    
    figma_server = get_figma_server()
    if not figma_server.component_analyzer:
        return [TextContent(type="text", text="Error: FIGMA_ACCESS_TOKEN not set")]
    
    result = figma_server.component_analyzer.analyze_component_structure(file_key, node_ids, max_depth)
    if not result or "error" in result:
        return [TextContent(type="text", text=f"Failed to analyze component structure: {result.get('error', 'Unknown error')}")]
    
    # 构建输出信息
    summary = result["analysis_summary"]
    reusable_components = result["reusable_components"]
    
    output_lines = [f"🔍 Component Structure Analysis Report\n"]
    output_lines.append(f"File: {result['file_name']}")
    output_lines.append(f"Total Components: {summary['total_components']}")
    output_lines.append(f"Unique Components: {summary['unique_components']}")
    output_lines.append(f"Reusable Candidates: {summary['reusable_candidates']}")
    output_lines.append(f"Max Depth: {summary['max_depth']}")
    
    if reusable_components:
        output_lines.append(f"\n🎯 Top Reusable Component Candidates:")
        for i, component in enumerate(reusable_components[:5], 1):
            output_lines.append(f"  {i}. {component['name']} ({component['type']})")
            output_lines.append(f"     • Repetition Count: {component['repetition_count']}")
            output_lines.append(f"     • Priority Score: {component['priority']}")
            output_lines.append(f"     • Suggested Action: {component['suggested_action']}")
            output_lines.append(f"     • Instances: {len(component['instances'])} locations")
    
    output_lines.append(f"\n📁 Analysis files saved:")
    output_lines.append(f"  • Component Analysis: component_analysis_{file_key}.json")
    output_lines.append(f"  • Component Roadmap: component_roadmap_{file_key}.json")
    
    return [
        TextContent(
            type="text", 
            text="\n".join(output_lines)
        )
    ]


async def handle_generate_node_roadmap(arguments: Dict[str, Any]) -> list[TextContent]:
    """Handle node roadmap generation"""
    file_key = arguments["file_key"]
    node_ids = arguments.get("node_ids", "0:0")
    max_depth = arguments.get("max_depth", 4)
    
    figma_server = get_figma_server()
    if not figma_server.roadmap_generator:
        return [TextContent(type="text", text="Error: FIGMA_ACCESS_TOKEN not set")]
    
    result = figma_server.roadmap_generator.generate_node_roadmap(file_key, node_ids, max_depth)
    if not result or "error" in result:
        return [TextContent(type="text", text=f"Failed to generate node roadmap: {result.get('error', 'Unknown error')}")]
    
    # 构建输出信息
    summary = result["roadmap_summary"]
    cross_page_analysis = result["cross_page_analysis"]
    analyzed_node_ids = result["analyzed_node_ids"]
    
    output_lines = [f"🗺️ Node Roadmap Generation Report\n"]
    output_lines.append(f"File: {result['file_name']}")
    output_lines.append(f"Analyzed Node IDs: {', '.join(analyzed_node_ids)}")
    output_lines.append(f"Total Nodes: {summary['total_nodes']}")
    output_lines.append(f"Unique Node Names: {summary['unique_node_names']}")
    output_lines.append(f"Max Depth Found: {summary['max_depth_found']}")
    output_lines.append(f"Cross-page Reusable Candidates: {summary['cross_page_reusable_candidates']}")
    
    if cross_page_analysis["reusable_candidates"]:
        output_lines.append(f"\n🎯 Top Cross-page Reusable Candidates:")
        for i, candidate in enumerate(cross_page_analysis["reusable_candidates"][:5], 1):
            output_lines.append(f"  {i}. {candidate['name']} ({candidate['type']})")
            output_lines.append(f"     • Total Occurrences: {candidate['total_occurrences']}")
            output_lines.append(f"     • Cross-page Occurrences: {candidate['cross_page_occurrences']}")
            output_lines.append(f"     • Priority Score: {candidate['priority']}")
            output_lines.append(f"     • Source Nodes: {', '.join(candidate['source_nodes'][:3])}{'...' if len(candidate['source_nodes']) > 3 else ''}")
    
    output_lines.append(f"\n📁 Roadmap files saved:")
    output_lines.append(f"  • Node Roadmap: node_roadmap_{file_key}.json")
    output_lines.append(f"  • Simplified Roadmap: simplified_roadmap_{file_key}.json")
    
    return [
        TextContent(
            type="text", 
            text="\n".join(output_lines)
        )
    ]


async def handle_smart_component_analysis(arguments: Dict[str, Any]) -> list[TextContent]:
    """Handle smart component analysis with AI"""
    file_key = arguments["file_key"]
    node_ids = arguments.get("node_ids", "0:0")
    max_depth = arguments.get("max_depth", 4)
    
    figma_server = get_figma_server()
    if not figma_server.smart_component_analyzer:
        return [TextContent(type="text", text="Error: FIGMA_ACCESS_TOKEN not set")]
    
    result = figma_server.smart_component_analyzer.analyze_with_ai_prompt(file_key, node_ids, max_depth)
    if not result or "error" in result:
        return [TextContent(type="text", text=f"Failed to perform smart analysis: {result.get('error', 'Unknown error')}")]
    
    # 构建输出信息
    summary = result["analysis_summary"]
    reusable_components = result["reusable_components"]
    analyzed_nodes = result["analyzed_nodes"]
    
    output_lines = [f"🤖 AI Smart Component Analysis Report\n"]
    output_lines.append(f"File Key: {result['file_key']}")
    output_lines.append(f"Analyzed Nodes: {analyzed_nodes}")
    output_lines.append(f"Total Candidates: {summary['total_candidates']}")
    output_lines.append(f"High Priority: {summary['high_priority']}")
    output_lines.append(f"Medium Priority: {summary['medium_priority']}")
    output_lines.append(f"Low Priority: {summary['low_priority']}")
    
    if reusable_components:
        output_lines.append(f"\n🎯 Top AI-Recommended Components:")
        for i, component in enumerate(reusable_components[:5], 1):
            output_lines.append(f"  {i}. {component['name']} ({component['type']})")
            output_lines.append(f"     • Reusability Score: {component['reusability_score']}/100")
            output_lines.append(f"     • Priority: {component['priority'].upper()}")
            output_lines.append(f"     • Reasoning: {component['reasoning']}")
            output_lines.append(f"     • Suggested Name: {component['suggested_name']}")
            output_lines.append(f"     • Usage Scenarios: {', '.join(component['usage_scenarios'])}")
            if component['similar_components']:
                output_lines.append(f"     • Similar Components: {', '.join(component['similar_components'])}")
            output_lines.append(f"     • Implementation: {component['implementation_notes']}")
    
    output_lines.append(f"\n💡 AI Recommendations:")
    output_lines.append(f"  {summary['recommendations']}")
    
    output_lines.append(f"\n📁 Analysis files saved:")
    output_lines.append(f"  • AI Analysis: ai_component_analysis_{file_key}.json")
    output_lines.append(f"  • Simplified Analysis: simplified_ai_analysis_{file_key}.json")
    
    return [
        TextContent(
            type="text", 
            text="\n".join(output_lines)
        )
    ]


async def handle_extract_tree(arguments: Dict[str, Any]) -> list[TextContent]:
    """Handle tree structure extraction"""
    file_key = arguments["file_key"]
    node_ids = arguments["node_ids"]
    depth = arguments.get("depth", 4)
    
    figma_server = get_figma_server()
    if not figma_server.tree_extractor:
        return [TextContent(type="text", text="Error: FIGMA_ACCESS_TOKEN not set")]
    
    result = figma_server.tree_extractor.extract_tree(file_key, node_ids, depth)
    if not result:
        return [TextContent(type="text", text="Failed to extract tree structure")]
    
    # 使用文件保存器保存树结构
    try:
        save_result = figma_server.file_saver.save_tree_structure(file_key, result, node_ids)
        tree_path = save_result["tree_path"]
        stats_path = save_result["stats_path"]
        return [
            TextContent(
                type="text", 
                text=f"✅ Tree structure extraction successful!\n\n📁 Tree file: {tree_path}\n📊 Stats file: {stats_path}\n📊 Total nodes: {result['analysis']['total_nodes']}\n📋 Node type statistics: {json.dumps(result['analysis']['node_counts'], ensure_ascii=False, indent=2)}"
            )
        ]
    except Exception as e:
        logger.error(f"Failed to save tree files: {e}")
        return [
            TextContent(
                type="text", 
                text=f"⚠️ Tree structure extraction completed but file generation failed!\n\n📊 Total nodes: {result['analysis']['total_nodes']}\n📋 Node type statistics: {json.dumps(result['analysis']['node_counts'], ensure_ascii=False, indent=2)}\n\nError: {str(e)}"
            )
        ]

async def handle_download_images(arguments: Dict[str, Any]) -> list[TextContent]:
    """Handle image download"""
    file_key = arguments["file_key"]
    node_ids = arguments["node_ids"]
    format = arguments.get("format", "png")
    scale = arguments.get("scale", 1.0)
    
    figma_server = get_figma_server()
    if not figma_server.image_extractor:
        return [TextContent(type="text", text="Error: FIGMA_ACCESS_TOKEN not set")]
    
    result = figma_server.image_extractor.extract_images(file_key, node_ids, format, scale)
    if not result:
        return [TextContent(type="text", text="Failed to download images")]
    
    success_count = sum(1 for img in result["images"].values() if img.get("status") == "success")
    total_count = len(result["images"])
    
    return [
        TextContent(
            type="text", 
            text=f"✅ Image download completed!\n\nSuccessfully downloaded: {success_count}/{total_count} images\nFormat: {format}\nScale: {scale}\nImages saved in: images_{file_key}/"
        )
    ]

async def handle_download_by_imgref(arguments: Dict[str, Any]) -> list[TextContent]:
    """Handle original image download by node ID"""
    file_key = arguments["file_key"]
    node_id = arguments["node_id"]
    format = arguments.get("format", "png")
    
    figma_server = get_figma_server()
    if not figma_server.image_extractor:
        return [TextContent(type="text", text="Error: FIGMA_ACCESS_TOKEN not set")]
    
    result = figma_server.image_extractor.download_original_images_by_node(file_key, node_id, format)
    if not result:
        return [TextContent(type="text", text="Failed to download images by imgref")]
    
    success_count = sum(1 for img in result["images"].values() if img.get("status") == "success")
    total_count = len(result["images"])
    
    return [
        TextContent(
            type="text", 
            text=f"✅ Original image download completed!\n\nNode ID: {node_id}\nSuccessfully downloaded: {success_count}/{total_count} original images\nFormat: {format}\nImages saved in: original_images_{file_key}/"
        )
    ]

async def handle_complete_data(arguments: Dict[str, Any]) -> list[TextContent]:
    """Handle complete data retrieval"""
    file_key = arguments["file_key"]
    node_ids = arguments["node_ids"]
    image_format = arguments.get("image_format", "png")
    image_scale = arguments.get("image_scale", 1.0)
    tree_depth = arguments.get("tree_depth", 4)
    
    figma_server = get_figma_server()
    if not figma_server.tree_extractor or not figma_server.image_extractor:
        return [TextContent(type="text", text="Error: FIGMA_ACCESS_TOKEN not set")]
    
    # Step 1: Get tree structure
    tree_result = figma_server.tree_extractor.extract_tree(file_key, node_ids, tree_depth)
    if not tree_result:
        return [TextContent(type="text", text="Failed to get tree structure")]
    
    # Step 2: Get node name
    first_node_id = node_ids.split(",")[0]
    node_name = figma_server.get_node_name(tree_result, first_node_id)
    
    # Step 3: Download images
    image_result = figma_server.image_extractor.extract_images(file_key, node_ids, image_format, image_scale)
    if not image_result:
        return [TextContent(type="text", text="Failed to download images")]
    
    # Step 4: Organize files
    organize_result = figma_server.organize_files(file_key, node_ids, node_name, tree_result, image_result)
    
    return [
        TextContent(
            type="text", 
            text=f"✅ Complete data retrieval successful!\n\n📁 Output folder: {organize_result['target_dir']}\n📊 Total nodes: {tree_result['analysis']['total_nodes']}\n🖼️ Image format: {image_format}\n📏 Scale ratio: {image_scale}\n\nIncluded files:\n- nodesinfo.json (node details)\n- nodesstatus.json (node statistics)\n- image.json (image information)\n- summary.json (summary information)\n- Image files"
        )
    ]

async def handle_extract_frames(arguments: Dict[str, Any]) -> list[TextContent]:
    """Handle Frame node extraction"""
    file_key = arguments["file_key"]
    max_depth = arguments.get("max_depth", 2)
    
    figma_server = get_figma_server()
    if not figma_server.frame_extractor:
        return [TextContent(type="text", text="Error: FIGMA_ACCESS_TOKEN not set")]
    
    result = figma_server.frame_extractor.extract_frames(file_key, max_depth)
    if not result:
        return [TextContent(type="text", text="Failed to extract Frame nodes")]
    
    frame_count = len(result["pages"])
    
    # 使用文件保存器保存Frame信息
    try:
        save_result = figma_server.file_saver.save_frame_info(file_key, result, max_depth)
        output_path = save_result["detailed_path"]
        simple_output_path = save_result["simple_path"]
    except Exception as e:
        logger.error(f"Failed to save frame files: {e}")
        output_path = "failed_to_save"
        simple_output_path = "failed_to_save"
    
    return [
        TextContent(
            type="text", 
            text=f"✅ Frame node extraction successful!\n\n📋 Found {frame_count} Frame nodes (depth={max_depth}):\n" + "\n".join([f"- {page['pageInfo']['name']} (ID: {page['pageInfo']['frameId']})" for page in result["pages"]]) + f"\n\n📁 Detailed result saved to: {output_path}\n📁 Simplified result saved to: {simple_output_path}"
        )
    ]

async def handle_list_nodes(arguments: Dict[str, Any]) -> list[TextContent]:
    """Handle node list retrieval"""
    file_key = arguments["file_key"]
    node_types = arguments.get("node_types", "")
    
    figma_server = get_figma_server()
    if not figma_server.node_lister:
        return [TextContent(type="text", text="Error: FIGMA_ACCESS_TOKEN not set")]
    
    result = figma_server.node_lister.list_nodes(file_key, node_types, max_depth=2)
    if not result:
        return [TextContent(type="text", text="Failed to get node list")]
    
    # 使用文件保存器保存节点列表
    try:
        save_result = figma_server.file_saver.save_node_list(file_key, result, 2)
        output_path = save_result["detailed_path"]
        simple_output_path = save_result["simple_path"]
    except Exception as e:
        logger.error(f"Failed to save node list files: {e}")
        output_path = "failed_to_save"
        simple_output_path = "failed_to_save"
    
    # Build output text
    output_lines = [f"✅ Node list retrieval successful!\n"]
    output_lines.append(f"File: {result['file_name']}")
    output_lines.append(f"Total nodes: {result['total_nodes']} (depth=2)")
    
    if node_types:
        output_lines.append(f"Filtered types: {node_types}")
    
    output_lines.append("\n📋 Node list:")
    
    # Output nodes by type
    for node_type, nodes in result["nodes_by_type"].items():
        output_lines.append(f"\n📁 {node_type} ({len(nodes)} items):")
        for node in nodes:
            indent = "  " * node["depth"]
            output_lines.append(f"{indent}- {node['name']} (ID: {node['id']})")
    
    output_lines.append(f"\n📁 Detailed result saved to: {output_path}")
    output_lines.append(f"📁 Simplified result saved to: {simple_output_path}")
    
    return [
        TextContent(
            type="text", 
            text="\n".join(output_lines)
        )
    ]

async def handle_extract_text(arguments: Dict[str, Any]) -> list[TextContent]:
    """Handle text content extraction"""
    file_key = arguments["file_key"]
    node_ids = arguments["node_ids"]
    max_depth = arguments.get("max_depth", 4)
    
    figma_server = get_figma_server()
    if not figma_server.text_extractor:
        return [TextContent(type="text", text="Error: FIGMA_ACCESS_TOKEN not set")]
    
    result = figma_server.text_extractor.extract_texts(file_key, node_ids, max_depth)
    if not result:
        return [TextContent(type="text", text="Failed to extract text content")]
    
    # 使用文件保存器保存文本信息
    try:
        save_result = figma_server.file_saver.save_text_info(file_key, result)
        text_path = save_result["text_path"]
        summary_path = save_result["summary_path"]
    except Exception as e:
        logger.error(f"Failed to save text files: {e}")
        text_path = "failed_to_save"
        summary_path = "failed_to_save"
    
    # Build output text
    output_lines = [f"✅ Text content extraction successful!\n"]
    output_lines.append(f"File: {result['file_name']}")
    output_lines.append(f"Target nodes: {result['target_nodes']}")
    output_lines.append(f"Max depth: {result['max_depth']}")
    output_lines.append(f"Found nodes: {len(result['found_nodes'])}")
    output_lines.append(f"Not found nodes: {len(result['not_found_nodes'])}")
    output_lines.append(f"Total text nodes: {result['total_text_nodes']}")
    
    if result['text_summary']:
        summary = result['text_summary']
        output_lines.append(f"Total characters: {summary['total_characters']}")
        output_lines.append(f"Unique texts: {summary['unique_texts']}")
    
    if result['texts_by_node']:
        output_lines.append("\n📝 Text content by node:")
        for node_id, texts in result['texts_by_node'].items():
            output_lines.append(f"\n📁 Node {node_id} ({len(texts)} texts):")
            for i, text_node in enumerate(texts[:5], 1):  # 只显示前5个
                characters = text_node.get("characters", "")
                preview = characters[:50] + "..." if len(characters) > 50 else characters
                output_lines.append(f"  {i}. {preview}")
            if len(texts) > 5:
                output_lines.append(f"  ... and {len(texts) - 5} more texts")
    
    output_lines.append(f"\n📁 Text info saved to: {text_path}")
    output_lines.append(f"📁 Text summary saved to: {summary_path}")
    
    return [
        TextContent(
            type="text", 
            text="\n".join(output_lines)
        )
    ]

async def handle_prompt(prompt_name: str, arguments: Dict[str, Any]) -> list[TextContent]:
    """Handle prompt execution"""
    figma_server = get_figma_server()
    
    if prompt_name == "figma_analysis":
        return await handle_figma_analysis(arguments)
    elif prompt_name == "figma_text_extraction":
        return await handle_figma_text_extraction_prompt(arguments)
    elif prompt_name == "figma_image_export":
        return await handle_figma_image_export_prompt(arguments)
    elif prompt_name == "figma_design_review":
        return await handle_figma_design_review(arguments)
    else:
        return [TextContent(type="text", text=f"Unknown prompt: {prompt_name}")]

async def handle_figma_analysis(arguments: Dict[str, Any]) -> list[TextContent]:
    """Handle Figma analysis prompt"""
    file_key = arguments["file_key"]
    analysis_type = arguments.get("analysis_type", "complete")
    
    figma_server = get_figma_server()
    if not figma_server.node_lister:
        return [TextContent(type="text", text="Error: FIGMA_ACCESS_TOKEN not set")]
    
    # 获取节点列表
    result = figma_server.node_lister.list_nodes(file_key, "", max_depth=2)
    if not result:
        return [TextContent(type="text", text="Failed to get node list")]
    
    output_lines = [f"🔍 Figma Analysis Report\n"]
    output_lines.append(f"File: {result['file_name']}")
    output_lines.append(f"Analysis Type: {analysis_type}")
    output_lines.append(f"Total Nodes: {result['total_nodes']}")
    
    if analysis_type in ["structure", "complete"]:
        output_lines.append("\n📊 Structure Analysis:")
        for node_type, nodes in result["nodes_by_type"].items():
            output_lines.append(f"  • {node_type}: {len(nodes)} nodes")
    
    if analysis_type in ["content", "complete"]:
        # 获取文本内容
        if result["nodes_by_type"].get("TEXT"):
            text_nodes = result["nodes_by_type"]["TEXT"]
            output_lines.append(f"\n📝 Content Analysis:")
            output_lines.append(f"  • Text nodes: {len(text_nodes)}")
            if len(text_nodes) > 0:
                output_lines.append(f"  • Sample text nodes:")
                for i, node in enumerate(text_nodes[:3], 1):
                    output_lines.append(f"    {i}. {node['name']} (ID: {node['id']})")
    
    output_lines.append(f"\n💡 Recommendations:")
    output_lines.append(f"  • Use 'list_nodes_depth2' to explore specific node types")
    output_lines.append(f"  • Use 'extract_text_content' for detailed text analysis")
    output_lines.append(f"  • Use 'download_figma_images' to export visual assets")
    
    return [
        TextContent(
            type="text", 
            text="\n".join(output_lines)
        )
    ]

async def handle_figma_text_extraction_prompt(arguments: Dict[str, Any]) -> list[TextContent]:
    """Handle Figma text extraction prompt"""
    file_key = arguments["file_key"]
    node_ids = arguments.get("node_ids", "")
    extract_style = arguments.get("extract_style", True)
    
    if not node_ids:
        # 如果没有指定节点ID，先获取所有文本节点
        figma_server = get_figma_server()
        if not figma_server.node_lister:
            return [TextContent(type="text", text="Error: FIGMA_ACCESS_TOKEN not set")]
        
        result = figma_server.node_lister.list_nodes(file_key, "TEXT", max_depth=2)
        if not result or not result["nodes_by_type"].get("TEXT"):
            return [TextContent(type="text", text="No text nodes found in the file")]
        
        text_nodes = result["nodes_by_type"]["TEXT"]
        node_ids = ",".join([node["id"] for node in text_nodes[:5]])  # 取前5个文本节点
    
    # 调用文本提取工具
    return await handle_extract_text({
        "file_key": file_key,
        "node_ids": node_ids,
        "max_depth": 4
    })

async def handle_figma_image_export_prompt(arguments: Dict[str, Any]) -> list[TextContent]:
    """Handle Figma image export prompt"""
    file_key = arguments["file_key"]
    node_ids = arguments.get("node_ids", "")
    format = arguments.get("format", "png")
    scale = arguments.get("scale", 1.0)
    
    if not node_ids:
        # 如果没有指定节点ID，先获取所有FRAME节点
        figma_server = get_figma_server()
        if not figma_server.node_lister:
            return [TextContent(type="text", text="Error: FIGMA_ACCESS_TOKEN not set")]
        
        result = figma_server.node_lister.list_nodes(file_key, "FRAME", max_depth=2)
        if not result or not result["nodes_by_type"].get("FRAME"):
            return [TextContent(type="text", text="No frame nodes found in the file")]
        
        frame_nodes = result["nodes_by_type"]["FRAME"]
        node_ids = ",".join([node["id"] for node in frame_nodes[:3]])  # 取前3个框架节点
    
    # 调用图片下载工具
    return await handle_download_images({
        "file_key": file_key,
        "node_ids": node_ids,
        "format": format,
        "scale": scale
    })

async def handle_figma_design_review(arguments: Dict[str, Any]) -> list[TextContent]:
    """Handle Figma design review prompt"""
    file_key = arguments["file_key"]
    review_aspects = arguments.get("review_aspects", ["layout", "typography", "colors"])
    
    figma_server = get_figma_server()
    if not figma_server.node_lister:
        return [TextContent(type="text", text="Error: FIGMA_ACCESS_TOKEN not set")]
    
    # 获取节点信息
    result = figma_server.node_lister.list_nodes(file_key, "", max_depth=2)
    if not result:
        return [TextContent(type="text", text="Failed to get node list")]
    
    output_lines = [f"🎨 Design Review Report\n"]
    output_lines.append(f"File: {result['file_name']}")
    output_lines.append(f"Review Aspects: {', '.join(review_aspects)}")
    output_lines.append(f"Total Nodes: {result['total_nodes']}")
    
    # 分析各个设计方面
    for aspect in review_aspects:
        output_lines.append(f"\n📋 {aspect.title()} Analysis:")
        
        if aspect == "layout":
            frame_count = len(result["nodes_by_type"].get("FRAME", []))
            group_count = len(result["nodes_by_type"].get("GROUP", []))
            output_lines.append(f"  • Frames: {frame_count}")
            output_lines.append(f"  • Groups: {group_count}")
            output_lines.append(f"  • Layout complexity: {'High' if frame_count > 10 else 'Medium' if frame_count > 5 else 'Low'}")
        
        elif aspect == "typography":
            text_count = len(result["nodes_by_type"].get("TEXT", []))
            output_lines.append(f"  • Text elements: {text_count}")
            if text_count > 0:
                output_lines.append(f"  • Typography density: {'High' if text_count > 20 else 'Medium' if text_count > 10 else 'Low'}")
        
        elif aspect == "colors":
            # 这里可以添加颜色分析逻辑
            output_lines.append(f"  • Color analysis requires detailed node inspection")
            output_lines.append(f"  • Use 'extract_figma_tree' for detailed color information")
        
        elif aspect == "spacing":
            output_lines.append(f"  • Spacing analysis requires detailed node inspection")
            output_lines.append(f"  • Use 'extract_figma_tree' for spacing information")
        
        elif aspect == "accessibility":
            output_lines.append(f"  • Accessibility analysis requires detailed inspection")
            output_lines.append(f"  • Check for proper contrast ratios and text sizes")
        
        elif aspect == "consistency":
            output_lines.append(f"  • Consistency analysis requires detailed inspection")
            output_lines.append(f"  • Compare similar elements across the design")
    
    output_lines.append(f"\n💡 Next Steps:")
    output_lines.append(f"  • Use 'extract_figma_tree' for detailed analysis")
    output_lines.append(f"  • Use 'extract_text_content' for typography review")
    output_lines.append(f"  • Use 'download_figma_images' to export for further review")
    
    return [
        TextContent(
            type="text", 
            text="\n".join(output_lines)
        )
    ]

async def handle_project_summary(arguments: Dict[str, Any]) -> list[TextContent]:
    """Handle project summary generation"""
    file_key = arguments["file_key"]
    summary_type = arguments.get("summary_type", "overview")
    max_text_length = arguments.get("max_text_length", 500)
    
    figma_server = get_figma_server()
    if not figma_server.text_extractor:
        return [TextContent(type="text", text="Error: FIGMA_ACCESS_TOKEN not set")]
    
    # 获取文本内容
    result = figma_server.text_extractor.extract_texts(file_key, "0:0,0:1", 4)
    if not result:
        return [TextContent(type="text", text="Failed to extract text content")]
    
    # 收集所有文本
    all_texts = []
    for node_texts in result.get("texts_by_node", {}).values():
        for text_node in node_texts:
            characters = text_node.get("characters", "")
            if characters and len(characters.strip()) > 0:
                all_texts.append(characters.strip())
    
    if not all_texts:
        return [TextContent(type="text", text="No text content found in the project")]
    
    # 合并文本
    combined_text = " ".join(all_texts[:50])  # 限制前50个文本
    if len(combined_text) > max_text_length:
        combined_text = combined_text[:max_text_length] + "..."
    
    output_lines = [f"📋 Project Summary Report\n"]
    output_lines.append(f"File: {result['file_name']}")
    output_lines.append(f"Summary Type: {summary_type}")
    output_lines.append(f"Total Text Elements: {len(all_texts)}")
    output_lines.append(f"Text Length: {len(combined_text)} characters")
    
    if summary_type == "overview":
        output_lines.append(f"\n🔍 Overview Summary:")
        output_lines.append(f"  • Project appears to be a {_detect_project_type(combined_text)}")
        output_lines.append(f"  • Main focus: {_extract_main_focus(combined_text)}")
        output_lines.append(f"  • Key features: {_extract_key_features(combined_text)}")
        
    elif summary_type == "business":
        output_lines.append(f"\n💼 Business Summary:")
        output_lines.append(f"  • Business type: {_extract_business_type(combined_text)}")
        output_lines.append(f"  • Target audience: {_extract_target_audience(combined_text)}")
        output_lines.append(f"  • Services: {_extract_services(combined_text)}")
        
    elif summary_type == "content":
        output_lines.append(f"\n📝 Content Summary:")
        output_lines.append(f"  • Content themes: {_extract_content_themes(combined_text)}")
        output_lines.append(f"  • Key messages: {_extract_key_messages(combined_text)}")
        output_lines.append(f"  • Content style: {_extract_content_style(combined_text)}")
        
    elif summary_type == "structure":
        output_lines.append(f"\n🏗️ Structure Summary:")
        output_lines.append(f"  • Content sections: {_extract_content_sections(all_texts)}")
        output_lines.append(f"  • Navigation elements: {_extract_navigation_elements(all_texts)}")
        output_lines.append(f"  • Call-to-action elements: {_extract_cta_elements(all_texts)}")
    
    output_lines.append(f"\n📄 Sample Content:")
    output_lines.append(f"  {combined_text[:200]}...")
    
    return [
        TextContent(
            type="text", 
            text="\n".join(output_lines)
        )
    ]

async def main():
    """Main function"""
def _detect_project_type(text: str) -> str:
    """检测项目类型"""
    text_lower = text.lower()
    if any(word in text_lower for word in ["军事", "国防", "军旅", "训练"]):
        return "军事教育培训项目"
    elif any(word in text_lower for word in ["教育", "培训", "学习"]):
        return "教育培训项目"
    elif any(word in text_lower for word in ["网站", "网页", "官网"]):
        return "网站项目"
    elif any(word in text_lower for word in ["应用", "app", "软件"]):
        return "应用软件项目"
    else:
        return "商业项目"

def _extract_main_focus(text: str) -> str:
    """提取主要焦点"""
    text_lower = text.lower()
    if "军事" in text_lower:
        return "军事文化传播和国防教育"
    elif "教育" in text_lower:
        return "教育培训服务"
    elif "服务" in text_lower:
        return "专业服务提供"
    else:
        return "商业服务"

def _extract_key_features(text: str) -> str:
    """提取关键特性"""
    features = []
    text_lower = text.lower()
    if "专业" in text_lower:
        features.append("专业性")
    if "团队" in text_lower:
        features.append("团队协作")
    if "培训" in text_lower:
        features.append("培训服务")
    if "教育" in text_lower:
        features.append("教育功能")
    return ", ".join(features) if features else "核心业务功能"

def _extract_business_type(text: str) -> str:
    """提取业务类型"""
    text_lower = text.lower()
    if "军事" in text_lower:
        return "军事教育培训机构"
    elif "教育" in text_lower:
        return "教育培训机构"
    elif "服务" in text_lower:
        return "专业服务机构"
    else:
        return "商业机构"

def _extract_target_audience(text: str) -> str:
    """提取目标受众"""
    text_lower = text.lower()
    if "青少年" in text_lower:
        return "青少年群体"
    elif "学生" in text_lower:
        return "学生群体"
    elif "企业" in text_lower:
        return "企业客户"
    else:
        return "一般用户"

def _extract_services(text: str) -> str:
    """提取服务内容"""
    services = []
    text_lower = text.lower()
    if "培训" in text_lower:
        services.append("培训服务")
    if "教育" in text_lower:
        services.append("教育服务")
    if "咨询" in text_lower:
        services.append("咨询服务")
    if "营会" in text_lower:
        services.append("营会活动")
    return ", ".join(services) if services else "核心服务"

def _extract_content_themes(text: str) -> str:
    """提取内容主题"""
    themes = []
    text_lower = text.lower()
    if "军事" in text_lower:
        themes.append("军事文化")
    if "教育" in text_lower:
        themes.append("教育培训")
    if "团队" in text_lower:
        themes.append("团队建设")
    if "专业" in text_lower:
        themes.append("专业服务")
    return ", ".join(themes) if themes else "核心主题"

def _extract_key_messages(text: str) -> str:
    """提取关键信息"""
    messages = []
    text_lower = text.lower()
    if "专业" in text_lower:
        messages.append("专业性")
    if "品质" in text_lower:
        messages.append("品质保证")
    if "服务" in text_lower:
        messages.append("优质服务")
    return ", ".join(messages) if messages else "核心价值"

def _extract_content_style(text: str) -> str:
    """提取内容风格"""
    text_lower = text.lower()
    if "专业" in text_lower and "正式" in text_lower:
        return "专业正式"
    elif "友好" in text_lower or "亲切" in text_lower:
        return "友好亲切"
    else:
        return "标准商务"

def _extract_content_sections(texts: list) -> str:
    """提取内容章节"""
    sections = []
    for text in texts:
        if any(word in text for word in ["首页", "关于", "服务", "联系"]):
            sections.append(text[:10])
    return ", ".join(sections[:5]) if sections else "主要章节"

def _extract_navigation_elements(texts: list) -> str:
    """提取导航元素"""
    nav_elements = []
    for text in texts:
        if any(word in text for word in ["首页", "关于", "服务", "产品", "联系"]):
            nav_elements.append(text)
    return ", ".join(nav_elements[:5]) if nav_elements else "导航菜单"

def _extract_cta_elements(texts: list) -> str:
    """提取行动号召元素"""
    cta_elements = []
    for text in texts:
        if any(word in text for word in ["联系", "咨询", "了解", "查看", "立即"]):
            cta_elements.append(text)
    return ", ".join(cta_elements[:5]) if cta_elements else "行动号召"



async def main():
    """Main function"""
    logger.info("Figma MCP server starting")
    
    # Check environment variables
    if not os.getenv("FIGMA_ACCESS_TOKEN"):
        logger.warning("FIGMA_ACCESS_TOKEN not set")
        print("Warning: FIGMA_ACCESS_TOKEN environment variable not set")
        print("Please set: export FIGMA_ACCESS_TOKEN='your_token_here'")
    else:
        logger.info("FIGMA_ACCESS_TOKEN is set")
    
    init_options = server.create_initialization_options()
    
    # Start MCP server
    try:
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                init_options,
            )
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
