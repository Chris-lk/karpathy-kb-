﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿import os
import sys
from pathlib import Path

# 获取项目根目录
ROOT_DIR = Path(__file__).parent.parent

# 全局变量
LLM_API_KEY = ''
LLM_MODEL = 'deepseek-chat'
LLM_API_BASE = 'https://api.deepseek.com'
WIKI_DIR = './wiki'

# 直接从 .env 文件读取配置
env_path = ROOT_DIR / '.env'
print(f"Looking for .env at: {env_path}")

if env_path.exists():
    print(".env file found!")
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    value = value.strip()
                    print(f"Loaded: {key} = {value[:20]}...")
                    
                    # 直接设置全局变量
                    if key == 'LLM_API_KEY':
                        LLM_API_KEY = value
                    elif key == 'LLM_MODEL':
                        LLM_MODEL = value
                    elif key == 'LLM_API_BASE':
                        LLM_API_BASE = value
                    elif key == 'WIKI_DIR':
                        WIKI_DIR = value
else:
    print(f".env file not found at {env_path}")

# 提示词模板
COMPILATION_PROMPT = """
请将以下原始内容编译成结构化的知识库。要求：
1. 使用 Markdown 格式
2. 每个页面开头包含 frontmatter（--- 包裹的 YAML 格式）
3. frontmatter 包含：title, tags, created_date
4. 使用双向链接 [[链接]] 连接相关概念
5. 内容要结构化、清晰

原始内容：
{raw_content}
"""

QUERY_SYSTEM_PROMPT = """
你是一个知识库助手。请严格基于提供的知识库内容回答问题，不要使用预训练知识。
如果知识库中没有相关信息，请明确说明。
"""

LINT_PROMPT = """
请检查以下知识库内容是否存在矛盾或不一致：
{content}
"""

# 调试信息
print(f"\nConfiguration:")
print(f"  API Base: {LLM_API_BASE}")
print(f"  Model: {LLM_MODEL}")
print(f"  API Key: {'✓ FOUND' if LLM_API_KEY else '✗ MISSING'} (length: {len(LLM_API_KEY) if LLM_API_KEY else 0})")
print(f"  API Key first 10 chars: {LLM_API_KEY[:10] if LLM_API_KEY else 'None'}...")
print(f"  Wiki Dir: {WIKI_DIR}\n")
