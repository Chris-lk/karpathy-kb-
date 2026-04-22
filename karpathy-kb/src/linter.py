﻿import os
import re
from pathlib import Path

class KnowledgeLinter:
    def __init__(self, wiki_dir='./wiki'):
        self.wiki_dir = wiki_dir
        # 排除这些根页面
        self.exclude_pages = {'README', 'Index', 'index', 'Home', 'compiled_knowledge'}
    
    def lint(self):
        """检查知识库健康状况"""
        issues = []
        
        if not os.path.exists(self.wiki_dir):
            return ["错误: wiki 目录不存在"]
        
        # 检查死链
        dead_links = self._check_dead_links()
        if dead_links:
            issues.extend([f"死链: {link}" for link in dead_links])
        
        # 检查孤立页面（排除根页面）
        orphaned_pages = self._check_orphaned_pages()
        orphaned_filtered = [p for p in orphaned_pages if p not in self.exclude_pages]
        if orphaned_filtered:
            issues.extend([f"孤立页面: {page}" for page in orphaned_filtered])
        
        # 检查空页面
        empty_pages = self._check_empty_pages()
        if empty_pages:
            issues.extend([f"空页面: {page}" for page in empty_pages])
        
        if not issues:
            return ["✅ 知识库健康状况良好！"]
        return issues
    
    def _check_dead_links(self):
        """检查死链"""
        dead_links = []
        all_pages = set()
        
        # 收集所有页面名称
        for file in os.listdir(self.wiki_dir):
            if file.endswith('.md'):
                page_name = os.path.splitext(file)[0]
                all_pages.add(page_name)
        
        # 检查每个文件中的链接
        for file in os.listdir(self.wiki_dir):
            if file.endswith('.md'):
                file_path = os.path.join(self.wiki_dir, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 匹配 [[链接]] 格式
                    links = re.findall(r'-Force\[(.*?)-Force\]', content)
                    for link in links:
                        if link not in all_pages:
                            dead_links.append(f"{file} -> {link}")
        
        return dead_links
    
    def _check_orphaned_pages(self):
        """检查孤立页面（没有被其他页面链接）"""
        all_pages = set()
        linked_pages = set()
        
        # 收集所有页面名称
        for file in os.listdir(self.wiki_dir):
            if file.endswith('.md'):
                page_name = os.path.splitext(file)[0]
                all_pages.add(page_name)
        
        # 收集被链接的页面
        for file in os.listdir(self.wiki_dir):
            if file.endswith('.md'):
                file_path = os.path.join(self.wiki_dir, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    links = re.findall(r'-Force\[(.*?)-Force\]', content)
                    linked_pages.update(links)
        
        # 孤立页面 = 所有页面 - 被链接的页面
        orphaned = all_pages - linked_pages
        return list(orphaned)
    
    def _check_empty_pages(self):
        """检查空页面"""
        empty_pages = []
        
        for file in os.listdir(self.wiki_dir):
            if file.endswith('.md'):
                file_path = os.path.join(self.wiki_dir, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if not content or len(content) < 50:
                        empty_pages.append(file)
        
        return empty_pages
