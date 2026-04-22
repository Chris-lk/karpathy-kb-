#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Karpathy 知识库构建工具
本地知识管理 + 检索 + 知识图谱可视化系统
"""

import sys
import os
import json
import webbrowser
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set
import re

# 确保使用 UTF-8 编码输出
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# 设置环境变量确保中文显示正常
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUTF8'] = '1'

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

def print_banner():
    print("=" * 60)
    print("Karpathy 知识库构建工具 v2.0")
    print("=" * 60)

def main():
    if len(sys.argv) < 2:
        print_banner()
        print("\n可用命令:")
        print("  python app.py compile              # 编译构建知识库")
        print("  python app.py query <问题>         # 向知识库提问")
        print("  python app.py lint                 # 检查知识库格式")
        print("  python app.py export [html|pdf|md|graph] # 导出文件")
        print("  python app.py ingest --file <路径> # 导入文档")
        print("  python app.py obsidian             # 生成Obsidian兼容格式")
        print("  python app.py graph                # 生成知识图谱可视化")
        print("\n示例:")
        print("  python app.py query '什么是RFID?'")
        print("  python app.py export pdf")
        print("  python app.py export graph")
        print("  python app.py graph")
        return
    
    command = sys.argv[1]
    
    if command == "compile":
        print_banner()
        print("\n开始编译知识库...\n")
        from src.compiler import KnowledgeCompiler
        compiler = KnowledgeCompiler()
        compiler.compile_knowledge_base()
        print("\n知识库编译完成")
    
    elif command == "query":
        if len(sys.argv) < 3:
            print("请输入查询问题")
            return
        question = ' '.join(sys.argv[2:])
        print_banner()
        print(f"\n查询: {question}\n")
        from src.query_engine import QueryEngine
        engine = QueryEngine()
        answer = engine.query(question)
        print(f"\n回答:\n{answer}\n")
    
    elif command == "lint":
        print_banner()
        print("\n开始检查知识库...\n")
        from src.linter import KnowledgeLinter
        linter = KnowledgeLinter()
        issues = linter.lint()
        if issues:
            print("发现问题:")
            for issue in issues:
                print(f"  {issue}")
        else:
            print("知识库格式完全正常")
    
    elif command == "export":
        # 默认导出HTML
        format = 'html'
        if len(sys.argv) > 2:
            format = sys.argv[2].lower()
        
        if format not in ['html', 'pdf', 'md', 'markdown', 'graph']:
            print(f"不支持的格式: {format}")
            print("  支持格式: html, pdf, md, markdown, graph")
            return
        
        print_banner()
        print(f"\n开始导出 {format.upper()} 格式...\n")
        
        from src.export import KnowledgeExporter
        exporter = KnowledgeExporter()
        
        if format == 'html':
            result = exporter.export_html()
        elif format == 'pdf':
            result = exporter.export_pdf()
        elif format == 'graph':
            result = exporter.export_graph()
        else:
            result = exporter.export_markdown()
        
        if result:
            print(f"\n导出成功")
            print(f"文件路径: {result}")
        else:
            print(f"\n导出失败")
    
    elif command == "ingest":
        if len(sys.argv) < 4 or sys.argv[2] != '--file':
            print("用法: python app.py ingest --file <文件路径>")
            return
        
        file_path = sys.argv[3]
        from src.ingest import Ingestor
        ingestor = Ingestor()
        
        if file_path.endswith('.pdf'):
            ingestor.ingest_pdf(file_path)
        elif file_path.startswith('http'):
            ingestor.ingest_webpage(file_path)
        else:
            ingestor.ingest_markdown(file_path)
    
    elif command == "obsidian":
        print_banner()
        print("\n开始生成Obsidian兼容格式...\n")
        from src.obsidian_compat import ObsidianCompat
        obsidian = ObsidianCompat()
        obsidian.make_compatible()
        print("\nObsidian 兼容格式生成完成")
        print("请将 wiki/ 目录导入Obsidian使用")
    
    elif command == "graph":
        print_banner()
        from src.visualization import KnowledgeGraph
        kg = KnowledgeGraph()
        kg.generate_all()
    
    else:
        print(f"未知命令: {command}")
        print("请运行 'python app.py' 查看帮助")

if __name__ == "__main__":
    main()