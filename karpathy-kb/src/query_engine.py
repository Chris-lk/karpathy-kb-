#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查询引擎模块
"""

import sys
import os
import json
import urllib.request
from pathlib import Path
import time

# 确保使用 UTF-8 编码输出
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# 直接读取 .env 文件
def load_api_config():
    current_dir = Path(__file__).parent
    project_root = current_dir.parent
    env_path = project_root / '.env'

    config = {
        'LLM_API_KEY': '',
        'LLM_MODEL': 'deepseek-chat',
        'LLM_API_BASE': 'https://api.deepseek.com',
        'WIKI_DIR': './wiki'
    }

    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    value = value.strip()
                    if key in config:
                        config[key] = value

    return config

# 加载配置
config = load_api_config()
LLM_API_KEY = config['LLM_API_KEY']
LLM_MODEL = config['LLM_MODEL']
LLM_API_BASE = config['LLM_API_BASE']
WIKI_DIR = config['WIKI_DIR']

class QueryEngine:
    
    def __init__(self):
        self.wiki_dir = WIKI_DIR
        self.concepts_dir = os.path.join(self.wiki_dir, 'concepts')
        self.chat_history_file = os.path.join(self.wiki_dir, 'chat_history.json')
        self.chat_history = self._load_chat_history()
        
    def _load_chat_history(self):
        """加载对话历史"""
        if os.path.exists(self.chat_history_file):
            try:
                with open(self.chat_history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载对话历史失败: {e}")
        return []
        
    def _save_chat_history(self):
        """保存对话历史"""
        try:
            with open(self.chat_history_file, 'w', encoding='utf-8') as f:
                json.dump(self.chat_history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存对话历史失败: {e}")
            
    def _load_knowledge_base(self):
        """加载知识库内容"""
        content_parts = []
        
        # 加载概念文件
        if os.path.exists(self.concepts_dir):
            for file in os.listdir(self.concepts_dir):
                if file.endswith('.md'):
                    file_path = os.path.join(self.concepts_dir, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            content_parts.append(f"# 文件: {file}\n\n{content}")
                    except Exception as e:
                        print(f"读取文件失败: {file} - {e}")
        
        # 加载编译结果
        compiled_file = os.path.join(self.wiki_dir, 'compiled_knowledge.md')
        if os.path.exists(compiled_file):
            try:
                with open(compiled_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    content_parts.append(f"# 编译结果\n\n{content}")
            except Exception as e:
                print(f"读取编译结果失败: {e}")
        
        return '\n\n'.join(content_parts)
        
    def _call_llm(self, prompt):
        """调用 DeepSeek API"""
        if not LLM_API_KEY:
            return "API Key 未配置，请在 .env 文件中设置 LLM_API_KEY"

        url = f"{LLM_API_BASE}/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {LLM_API_KEY}"
        }
        data = {
            "model": LLM_MODEL,
            "max_tokens": 2048,
            "messages": [
                {"role": "system", "content": "你是一个基于知识库的问答助手，回答问题时要基于提供的知识库内容。"},
                {"role": "user", "content": prompt}
            ]
        }

        try:
            data_bytes = json.dumps(data).encode('utf-8')
            req = urllib.request.Request(url, data=data_bytes, headers=headers, method='POST')
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result['choices'][0]['message']['content']
        except urllib.error.HTTPError as e:
            error_msg = e.read().decode('utf-8')
            return f"API 调用失败: {e.code} - {error_msg}"
        except Exception as e:
            return f"API 调用失败: {e}"
        
    def query(self, question):
        """处理查询"""
        # 加载知识库
        knowledge_base = self._load_knowledge_base()
        
        if not knowledge_base:
            return "知识库为空，请先运行 `python app.py compile` 编译知识库"
        
        # 构建提示
        prompt = f"""
请基于以下知识库内容回答问题：

{knowledge_base}

问题: {question}

要求：
1. 基于知识库内容回答
2. 提供详细的解释
3. 使用 [[双向链接]] 连接相关概念
4. 引用知识库中的内容
"""
        
        # 调用 LLM
        response = self._call_llm(prompt)
        
        # 保存对话历史
        self.chat_history.append({
            "question": question,
            "answer": response,
            "timestamp": time.time()
        })
        # 只保留最近 10 条对话
        self.chat_history = self.chat_history[-10:]
        self._save_chat_history()
        
        return response