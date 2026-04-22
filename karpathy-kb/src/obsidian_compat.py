﻿import os
import json
from pathlib import Path
from typing import Dict, List, Set

class ObsidianCompat:
    """Obsidian 兼容性模块 - 增强知识图谱支持"""
    
    def __init__(self, wiki_dir='./wiki'):
        self.wiki_dir = Path(wiki_dir)
        self.obsidian_dir = self.wiki_dir / '.obsidian'
        self.obsidian_dir.mkdir(exist_ok=True)
    
    def create_obsidian_config(self):
        """创建 Obsidian 基本配置"""
        config = {
            "theme": "obsidian",
            "workspace": {
                "left": [
                    {
                        "type": "file-explorer",
                        "collapsed": False
                    },
                    {
                        "type": "search",
                        "collapsed": True
                    },
                    {
                        "type": "graph",
                        "collapsed": False
                    }
                ],
                "right": [],
                "center": [
                    {
                        "type": "markdown"
                    }
                ]
            },
            "fileExtension": "md",
            "defaultViewMode": "source",
            "showFrontmatter": True
        }
        
        config_file = self.obsidian_dir / 'app.json'
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 创建 Obsidian 配置: {config_file}")
    
    def create_graph_config(self):
        """创建知识图谱配置"""
        graph_config = {
            "collapse-filter": False,
            "colors": {
                "attachments": "#433E4C",
                "notes": "#2D6D99",
                "tags": "#992D6D"
            },
            "show-attachments": False,
            "show-tags": True,
            "show-links": True,
            "show-unlinked": False,
            "force-simulation": {
                "central-gravity": 0.1,
                "edge-length": 200,
                "edge-strength": 0.1,
                "repulsion": 1000,
                "theta": 0.1
            },
            "search": {
                "include": "",
                "exclude": ""
            },
            "zoom-level": 1,
            "lock-view": False
        }
        
        graph_file = self.obsidian_dir / 'graph.json'
        with open(graph_file, 'w', encoding='utf-8') as f:
            json.dump(graph_config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 创建图谱配置: {graph_file}")
    
    def create_tags_config(self):
        """创建标签配置"""
        tags_config = {
            "list": [
                {
                    "tag": "物联网",
                    "color": "#2D6D99"
                },
                {
                    "tag": "RFID",
                    "color": "#992D6D"
                },
                {
                    "tag": "传感器",
                    "color": "#2D996D"
                },
                {
                    "tag": "通信技术",
                    "color": "#99992D"
                },
                {
                    "tag": "边缘计算",
                    "color": "#6D2D99"
                },
                {
                    "tag": "5G",
                    "color": "#992D2D"
                }
            ]
        }
        
        tags_file = self.obsidian_dir / 'tags.json'
        with open(tags_file, 'w', encoding='utf-8') as f:
            json.dump(tags_config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 创建标签配置: {tags_file}")
    
    def create_appearance_config(self):
        """创建外观配置"""
        appearance_config = {
            "theme": "obsidian",
            "baseFontSize": 16,
            "fontFamily": "system-ui",
            "readableLineLength": True,
            "showLineNumbers": True,
            "translucentWindow": False,
            "accentColor": "#2D6D99"
        }
        
        appearance_file = self.obsidian_dir / 'appearance.json'
        with open(appearance_file, 'w', encoding='utf-8') as f:
            json.dump(appearance_config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 创建外观配置: {appearance_file}")
    
    def create_core_plugins_config(self):
        """创建核心插件配置"""
        core_plugins_config = {
            "file-explorer": True,
            "search": True,
            "graph": True,
            "backlink": True,
            "outgoing-link": True,
            "tag-pane": True,
            "properties": True
        }
        
        core_plugins_file = self.obsidian_dir / 'core-plugins.json'
        with open(core_plugins_file, 'w', encoding='utf-8') as f:
            json.dump(core_plugins_config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 创建核心插件配置: {core_plugins_file}")
    
    def create_readme(self):
        """创建 README 文件，详细说明如何使用 Obsidian 查看知识图谱"""
        readme_content = """# 物联网知识库

## 知识图谱使用指南

### 1. 打开 Obsidian

1. **下载 Obsidian**：从 [Obsidian 官网](https://obsidian.md/) 下载并安装
2. **打开仓库**：
   - 打开 Obsidian
   - 点击 "Open folder as vault"
   - 选择本目录 (wiki/)

### 2. 查看知识图谱

1. **打开图谱视图**：
   - 点击左侧边栏的图谱图标（通常是一个由点和线组成的图标）
   - 或使用快捷键 Ctrl+G (Windows/Linux) 或 Cmd+G (Mac)

2. **图谱交互**：
   - **缩放**：鼠标滚轮或触控板
   - **平移**：按住鼠标左键拖动
   - **点击节点**：查看该节点的详细信息
   - **右键点击**：打开上下文菜单

3. **图谱设置**：
   - 点击图谱右上角的设置图标
   - 调整显示选项（如显示标签、显示未链接节点等）
   - 修改力导向布局参数

### 3. 知识库结构

- **compiled_knowledge.md**：主知识库文件
- **其他文件**：按主题分类的知识页面

### 4. 双向链接

本知识库使用 Obsidian 的双向链接语法：[[概念]]

- **创建链接**：在编辑模式下输入 [[ 然后开始输入概念名称
- **查看链接**：在图谱中查看节点之间的连接
- **反向链接**：在文件底部查看哪些文件链接到了当前文件

### 5. 标签系统

知识库使用标签来组织内容：
- #物联网：物联网相关内容
- #RFID：RFID 技术相关内容
- #传感器：传感器技术相关内容
- #通信技术：通信技术相关内容
- #边缘计算：边缘计算相关内容
- #5G：5G 技术相关内容

## 自建图谱可视化（可选）

除了使用 Obsidian，您还可以使用以下工具查看知识图谱：

1. **Gephi**：开源网络分析和可视化软件
2. **Neo4j**：图形数据库，支持复杂的知识图谱查询
3. **D3.js**：使用 JavaScript 构建交互式知识图谱

### 导出图谱数据

运行以下命令导出图谱数据：
`ash
python app.py export graph
`

这将生成 graph.json 文件，可用于其他可视化工具。
"""
        
        readme_file = self.wiki_dir / 'README.md'
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print(f"✅ 创建 README: {readme_file}")
    
    def extract_graph_data(self) -> Dict:
        """提取知识图谱数据"""
        graph_data = {
            "nodes": [],
            "links": []
        }
        
        # 收集所有页面
        pages = {}
        for file in self.wiki_dir.glob('*.md'):
            if file.name == 'README.md':
                continue
            pages[file.stem] = {
                "id": file.stem,
                "label": file.stem,
                "type": "page",
                "file": str(file)
            }
        
        # 提取链接
        import re
        for page_id, page_info in pages.items():
            file_path = Path(page_info["file"])
            try:
                content = file_path.read_text(encoding='utf-8')
                # 提取 [[链接]] 格式的链接
                links = re.findall(r'D:\trae_projects\wulianwang1\karpathy-kb\[(.*?)D:\trae_projects\wulianwang1\karpathy-kb\]', content)
                for link in links:
                    # 清理链接文本
                    link_clean = link.split('|')[0].strip()
                    if link_clean in pages:
                        graph_data["links"].append({
                            "source": page_id,
                            "target": link_clean,
                            "type": "link"
                        })
            except Exception as e:
                print(f"⚠️  提取链接失败: {file_path} - {e}")
        
        # 添加节点
        for page_id, page_info in pages.items():
            graph_data["nodes"].append({
                "id": page_id,
                "label": page_info["label"],
                "type": page_info["type"]
            })
        
        return graph_data
    
    def export_graph_data(self):
        """导出图谱数据为 JSON 文件"""
        graph_data = self.extract_graph_data()
        output_file = self.wiki_dir / 'graph.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(graph_data, f, indent=2, ensure_ascii=False)
        print(f"✅ 导出图谱数据: {output_file}")
        return output_file
    
    def make_compatible(self):
        """使知识库与 Obsidian 兼容"""
        print("🔧 配置 Obsidian 兼容性...")
        self.create_obsidian_config()
        self.create_graph_config()
        self.create_tags_config()
        self.create_appearance_config()
        self.create_core_plugins_config()
        self.create_readme()
        self.export_graph_data()
        print("✅ Obsidian 兼容性配置完成！")
        print("📖 请在 Obsidian 中打开 wiki/ 目录作为仓库")
        print("🔍 打开图谱视图查看知识图谱")
