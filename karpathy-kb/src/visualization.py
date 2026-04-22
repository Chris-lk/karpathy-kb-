#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识图谱可视化模块
"""

import sys
import os
import json
import webbrowser
from pathlib import Path
from datetime import datetime

# 确保使用 UTF-8 编码输出
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

class KnowledgeGraph:
    """知识图谱生成器 - 可视化知识库关系"""
    
    def __init__(self, wiki_dir='./wiki'):
        self.wiki_dir = Path(wiki_dir)
        self.graph_dir = self.wiki_dir / 'graph'
        self.graph_dir.mkdir(exist_ok=True)
        self.nodes = {}
        self.links = []
        self.stats = {}
    
    def extract_graph_data(self):
        """提取图谱数据"""
        print("提取图谱数据...")
        
        # 收集页面
        pages = []
        for root, dirs, files in os.walk(self.wiki_dir):
            for file in files:
                if file.endswith('.md') and file != 'README.md':
                    file_path = os.path.join(root, file)
                    label = os.path.splitext(file)[0]
                    pages.append((label, file_path))
        
        print(f"找到 {len(pages)} 个页面")
        
        # 创建节点
        for label, file_path in pages:
            self.nodes[label] = {
                "id": label,
                "label": label,
                "type": "page",
                "file": file_path,
                "in_links": 0,
                "out_links": 0
            }
        
        # 提取链接
        for label, file_path in pages:
            try:
                # 读取文件内容
                with open(file_path, 'rb') as f:
                    content_bytes = f.read()
                
                # 尝试不同编码
                encodings = ['utf-8', 'gbk', 'latin-1']
                content = None
                for encoding in encodings:
                    try:
                        content = content_bytes.decode(encoding)
                        break
                    except:
                        continue
                
                if not content:
                    print(f"  无法读取 {label}")
                    continue
                
                # 查找链接
                links_found = []
                for other_label, _ in pages:
                    if other_label != label and other_label in content:
                        links_found.append(other_label)
                
                print(f"  {label}: 找到 {len(links_found)} 个链接")
                
                # 添加链接
                for link in links_found:
                    self.links.append({
                        "source": label,
                        "target": link,
                        "type": "link"
                    })
                    self.nodes[label]["out_links"] += 1
                    self.nodes[link]["in_links"] += 1
                
            except Exception as e:
                print(f"  处理 {label} 时出错: {e}")
        
        print(f"\n图谱数据: {len(self.nodes)} 个节点, {len(self.links)} 条链接")
    
    def calculate_stats(self):
        """计算统计信息"""
        print("计算统计信息...")
        
        # 基本统计
        total_pages = len(self.nodes)
        total_links = len(self.links)
        avg_degree = (total_links * 2) / total_pages if total_pages > 0 else 0
        
        # 最受引用的页面
        most_cited = sorted(
            self.nodes.values(),
            key=lambda x: x["in_links"],
            reverse=True
        )[:5]
        
        # 引用最多的页面
        most_linking = sorted(
            self.nodes.values(),
            key=lambda x: x["out_links"],
            reverse=True
        )[:5]
        
        # 孤立页面
        isolated = [
            node["label"] for node in self.nodes.values()
            if node["in_links"] + node["out_links"] == 0
        ]
        
        self.stats = {
            "generated_at": datetime.now().isoformat(),
            "total_pages": total_pages,
            "total_links": total_links,
            "avg_degree": round(avg_degree, 2),
            "most_cited": [{"name": n["label"], "count": n["in_links"]} for n in most_cited],
            "most_linking": [{"name": n["label"], "count": n["out_links"]} for n in most_linking],
            "isolated_pages": isolated
        }
        
        return self.stats
    
    def export_d3_html(self):
        """导出 D3.js 可视化页面"""
        print("导出 D3.js 可视化页面...")
        
        # 准备 D3.js 数据
        d3_nodes = [{"id": n["label"], "in_degree": n["in_links"], "out_degree": n["out_links"]} for n in self.nodes.values()]
        d3_links = [{"source": l["source"], "target": l["target"]} for l in self.links]
        
        html_content = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>知识图谱</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 0;
            background: #1a1a1a;
        }
        .container { display: flex; height: 100vh; }
        .sidebar {
            width: 300px;
            background: #2d2d2d;
            color: white;
            padding: 20px;
            overflow-y: auto;
        }
        .graph-container { flex: 1; }
        h1 { font-size: 18px; margin-bottom: 20px; color: #3498db; }
        .stat-item { margin: 10px 0; padding: 10px; background: #3d3d3d; border-radius: 5px; }
        .node { stroke: #fff; stroke-width: 1.5px; cursor: pointer; }
        .node:hover { stroke: #3498db; stroke-width: 3px; }
        .link { stroke: #999; stroke-opacity: 0.6; }
        .node-label { 
            fill: white; 
            font-size: 12px;
            pointer-events: none;
        }
        .tooltip {
            position: absolute;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 10px;
            border-radius: 5px;
            pointer-events: none;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="sidebar">
            <h1>知识图谱统计</h1>
            <div class="stat-item" id="stats"></div>
        </div>
        <div class="graph-container" id="graph"></div>
    </div>
    
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <script>
        // 图谱数据
        const nodes = ''' + json.dumps(d3_nodes, ensure_ascii=False) + ''';
        const links = ''' + json.dumps(d3_links, ensure_ascii=False) + ''';
        
        // 统计数据
        const stats = ''' + json.dumps(self.stats, ensure_ascii=False) + ''';
        
        // 渲染统计信息
        document.getElementById('stats').innerHTML = `
            <p><strong>总页面数:</strong> ${stats.total_pages}</p>
            <p><strong>总链接数:</strong> ${stats.total_links}</p>
            <p><strong>平均度数:</strong> ${stats.avg_degree}</p>
            <p><strong>最受引用:</strong></p>
            <ul>${stats.most_cited.map(item => `<li>${item.name}: ${item.count}</li>`).join('')}</ul>
            <p><strong>引用最多:</strong></p>
            <ul>${stats.most_linking.map(item => `<li>${item.name}: ${item.count}</li>`).join('')}</ul>
            <p><strong>孤立页面:</strong> ${stats.isolated_pages.length}</p>
        `;
        
        // 创建 SVG
        const width = document.getElementById('graph').clientWidth;
        const height = document.getElementById('graph').clientHeight;
        
        const svg = d3.select('#graph')
            .append('svg')
            .attr('width', width)
            .attr('height', height);
        
        // 创建力导向图
        const simulation = d3.forceSimulation(nodes)
            .force('link', d3.forceLink(links).id(d => d.id).distance(100))
            .force('charge', d3.forceManyBody().strength(-300))
            .force('center', d3.forceCenter(width / 2, height / 2));
        
        // 创建链接
        const link = svg.append('g')
            .selectAll('line')
            .data(links)
            .enter()
            .append('line')
            .attr('class', 'link');
        
        // 创建节点
        const node = svg.append('g')
            .selectAll('circle')
            .data(nodes)
            .enter()
            .append('circle')
            .attr('class', 'node')
            .attr('r', d => Math.max(5, Math.min(15, d.in_degree + 5)))
            .style('fill', d => d.in_degree > 0 ? '#3498db' : '#e74c3c');
        
        // 添加标签
        const label = svg.append('g')
            .selectAll('text')
            .data(nodes)
            .enter()
            .append('text')
            .attr('class', 'node-label')
            .text(d => d.id)
            .attr('dx', 12)
            .attr('dy', 4);
        
        // 创建提示框
        const tooltip = d3.select('body')
            .append('div')
            .attr('class', 'tooltip')
            .style('opacity', 0);
        
        // 鼠标事件
        node.on('mouseover', function(event, d) {
            tooltip.transition()
                .duration(200)
                .style('opacity', .9);
            tooltip.html(`
                <strong>${d.id}</strong><br/>
                入度: ${d.in_degree}<br/>
                出度: ${d.out_degree}
            `)
                .style('left', (event.pageX + 10) + 'px')
                .style('top', (event.pageY - 28) + 'px');
        })
        .on('mouseout', function() {
            tooltip.transition()
                .duration(500)
                .style('opacity', 0);
        });
        
        // 力导向图更新
        simulation.on('tick', () => {
            link
                .attr('x1', d => d.source.x)
                .attr('y1', d => d.source.y)
                .attr('x2', d => d.target.x)
                .attr('y2', d => d.target.y);
            
            node
                .attr('cx', d => d.x = Math.max(10, Math.min(width - 10, d.x)))
                .attr('cy', d => d.y = Math.max(10, Math.min(height - 10, d.y)));
            
            label
                .attr('x', d => d.x)
                .attr('y', d => d.y);
        });
    </script>
</body>
</html>'''
        
        # 保存 HTML 文件
        html_path = self.graph_dir / 'graph.html'
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"导出 D3.js 可视化页面: {html_path}")
        return str(html_path)
    
    def export_gephi_csv(self):
        """导出 Gephi 兼容的 CSV 文件"""
        print("导出 Gephi 兼容的 CSV 文件...")
        
        # 节点 CSV
        nodes_csv = "Id,Label,InDegree,OutDegree\n"
        for node in self.nodes.values():
            nodes_csv += f"{node['label']},{node['label']},{node['in_links']},{node['out_links']}\n"
        
        # 链接 CSV
        links_csv = "Source,Target,Type\n"
        for link in self.links:
            links_csv += f"{link['source']},{link['target']},Undirected\n"
        
        # 保存文件
        nodes_path = self.graph_dir / 'nodes.csv'
        links_path = self.graph_dir / 'links.csv'
        
        with open(nodes_path, 'w', encoding='utf-8') as f:
            f.write(nodes_csv)
        
        with open(links_path, 'w', encoding='utf-8') as f:
            f.write(links_csv)
        
        print(f"导出 Gephi 节点文件: {nodes_path}")
        print(f"导出 Gephi 链接文件: {links_path}")
        return str(self.graph_dir)
    
    def export_obsidian_json(self):
        """导出 Obsidian 图谱数据"""
        print("导出 Obsidian 图谱数据...")
        
        obsidian_graph = {
            "directed": False,
            "multigraph": False,
            "graph": {},
            "nodes": [{"id": node["label"]} for node in self.nodes.values()],
            "links": [{"source": link["source"], "target": link["target"]} for link in self.links]
        }
        
        json_path = self.graph_dir / 'obsidian_graph.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(obsidian_graph, f, indent=2, ensure_ascii=False)
        
        print(f"导出 Obsidian 图谱数据: {json_path}")
        return str(json_path)
    
    def generate_all(self, open_browser=True):
        """生成所有图谱文件"""
        print("开始生成知识图谱...")
        
        # 提取数据
        self.extract_graph_data()
        
        # 计算统计
        self.calculate_stats()
        
        # 导出文件
        html_path = self.export_d3_html()
        self.export_gephi_csv()
        self.export_obsidian_json()
        
        # 保存统计信息
        stats_path = self.graph_dir / 'stats.json'
        with open(stats_path, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, indent=2, ensure_ascii=False)
        
        print(f"保存统计信息: {stats_path}")
        print("知识图谱生成完成")
        
        # 打开浏览器
        if open_browser and os.path.exists(html_path):
            webbrowser.open(f'file://{html_path}')
            print(f"已打开浏览器: {html_path}")