#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识编译器模块
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

    print(f"Looking for .env file at: {env_path}")

    if env_path.exists():
        print(".env file found!")
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    value = value.strip()
                    if key in config:
                        config[key] = value
                        print(f"Loaded {key} = {value[:20]}...")
    else:
        print(f".env file not found at {env_path}")
        print(f"Current directory: {os.getcwd()}")
        print(f"Project root: {project_root}")

    return config

# 加载配置
config = load_api_config()
LLM_API_KEY = config['LLM_API_KEY']
LLM_MODEL = config['LLM_MODEL']
LLM_API_BASE = config['LLM_API_BASE']
WIKI_DIR = config['WIKI_DIR']

print(f"\nFinal Config:")
print(f"  API Key: {'OK' if LLM_API_KEY else 'N/A'} (length: {len(LLM_API_KEY)})")
print(f"  Model: {LLM_MODEL}")
print(f"  Base: {LLM_API_BASE}\n")

COMPILATION_PROMPT = """
你是一个知识编译器。请将以下原始资料整理成结构化的Markdown知识库。

## 任务要求：

1. 实体识别：提取所有重要概念、人名、术语，创建独立页面
2. 自动链接：使用[[双向链接]]语法连接相关概念
3. 层级结构：
   - 每个实体一个Markdown文件
   - Frontmatter包含：title, date, tags, sources
   - 正文包含：摘要、详细说明、相关链接、待探索问题
4. 冲突处理：如果多个来源信息矛盾，保留并标注争议点
5. 索引生成：创建README.md作为知识库入口

## 输出格式：
请为每个概念生成一个完整的Markdown文件内容，包括frontmatter和正文。
每个文件内容应以"--- FILE: 文件名.md ---"开头，以便我能够正确解析。

## 输出示例：

--- FILE: 物联网.md ---
---
title: "物联网"
date: 2026-04-12
tags: ["物联网", "核心概念"]
sources: ["物联网基础.txt"]
---

# 物联网

## 摘要
物联网是指通过信息传感设备，将任何物体与网络连接，实现智能化识别和管理。

## 详细说明
物联网(Internet of Things, IoT)是一种网络技术，通过信息传感设备将各种物体与互联网连接，实现智能化识别、定位、跟踪、监控和管理。

## 相关概念
- [[RFID]]
- [[传感器]]
- [[通信技术]]

## 待探索
- [ ] 物联网安全问题
- [ ] 物联网标准协议

--- FILE: RFID.md ---
---
title: "RFID"
date: 2026-04-12
tags: ["物联网", "核心技术"]
sources: ["RFID技术.txt"]
---

# RFID

## 摘要
RFID是一种非接触式自动识别技术，通过无线电波识别特定目标并读写相关数据。

## 详细说明
RFID（Radio Frequency Identification）是一种利用无线电波进行非接触式双向通信的自动识别技术。

## 相关概念
- [[物联网]]
- [[传感器]]

## 待探索
- [ ] RFID标准
- [ ] RFID应用场景

原始资料：
{raw_content}
"""

class KnowledgeCompiler:

    def __init__(self):
        self.wiki_dir = WIKI_DIR
        self.concepts_dir = os.path.join(self.wiki_dir, 'concepts')
        self.metadata_file = os.path.join(self.wiki_dir, '.compile_metadata.json')
        os.makedirs(self.concepts_dir, exist_ok=True)
        print(f"Created concepts directory: {self.concepts_dir}")
        self._load_metadata()

    def _load_metadata(self):
        """加载编译元数据"""
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {
                'last_compile': 0,
                'processed_files': {},
                'concepts': []
            }

    def _save_metadata(self):
        """保存编译元数据"""
        self.metadata['last_compile'] = time.time()
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2)

    def compile_knowledge_base(self, incremental=True):
        """编译知识库"""
        raw_content, changed_files = self._load_raw_content(incremental)

        # 检查是否真的没有原始资料，而不是因为增量编译没有变更
        if not raw_content and not changed_files:
            # 检查 raw 目录是否真的为空
            current_dir = Path(__file__).parent
            project_root = current_dir.parent
            raw_dir = project_root / 'raw'
            all_files = os.listdir(str(raw_dir))
            txt_md_files = [f for f in all_files if f.endswith('.txt') or f.endswith('.md')]
            
            if not txt_md_files:
                print("没有找到原始资料，请在 raw/ 目录下添加 .txt 文件")
                return
            else:
                print("所有文件都已处理过，没有变更")
                return

        print(f"找到原始资料，长度: {len(raw_content)} 字符")
        print(f"变更文件: {len(changed_files)} 个")

        print("正在调用 LLM 编译知识库...")

        # 构建提示
        prompt = COMPILATION_PROMPT.format(raw_content=raw_content)
        
        # 调用 LLM
        compiled_content = self._call_llm(prompt)
        
        if compiled_content:
            print("LLM 编译完成，开始解析...")
            self._parse_and_save_compiled_content(compiled_content)
        else:
            print("LLM 调用失败，使用备用方法...")
            self._generate_concepts_from_raw(changed_files)
        
        # 配置 Obsidian 兼容性
        try:
            from src.obsidian_compat import ObsidianCompat
            obsidian = ObsidianCompat(self.wiki_dir)
            obsidian.make_compatible()
        except Exception as e:
            print(f"Obsidian 配置失败: {e}")
        
        # 保存元数据
        for file in changed_files:
            self.metadata['processed_files'][file] = time.time()
        self._save_metadata()
        
        print("知识库编译完成")

    def _load_raw_content(self, incremental):
        """加载 raw 目录下的所有文件，支持增量编译"""
        content_parts = []
        # 使用绝对路径确保能正确找到原始资料
        current_dir = Path(__file__).parent
        project_root = current_dir.parent
        raw_dir = project_root / 'raw'
        raw_dir = str(raw_dir)
        changed_files = []

        print(f"Current working directory: {os.getcwd()}")
        print(f"Project root: {project_root}")
        print(f"Raw directory: {raw_dir}")

        if not os.path.exists(raw_dir):
            print(f"Raw directory does not exist, creating: {raw_dir}")
            os.makedirs(raw_dir)
            return "", []

        print(f"Raw directory exists: {os.path.exists(raw_dir)}")
        all_files = os.listdir(raw_dir)
        print(f"All files in raw directory: {all_files}")
        
        files = [f for f in all_files if f.endswith('.txt') or f.endswith('.md')]
        print(f"Filtered files (txt/md): {files}")
        
        if not files:
            print(f"Raw directory exists but no txt/md files found: {raw_dir}")
            return "", []

        for file in files:
            file_path = os.path.join(raw_dir, file)
            file_mtime = os.path.getmtime(file_path)

            # 检查文件是否有变更
            if not incremental or file not in self.metadata['processed_files'] or file_mtime > self.metadata['processed_files'].get(file, 0):
                changed_files.append(file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    content_parts.append(f"# 文件: {file}\n\n{content}")

        return '\n\n'.join(content_parts), changed_files

    def _call_llm(self, prompt):
        """调用 DeepSeek API，带重试机制"""
        if not LLM_API_KEY:
            print("错误: API Key 未配置")
            return ""

        url = f"{LLM_API_BASE}/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {LLM_API_KEY}"
        }
        data = {
            "model": LLM_MODEL,
            "max_tokens": 8192,
            "messages": [{"role": "user", "content": prompt}]
        }

        print(f"\n调用 API: {url}")
        print(f"使用模型: {LLM_MODEL}")

        max_retries = 3
        for attempt in range(max_retries):
            try:
                data_bytes = json.dumps(data).encode('utf-8')
                req = urllib.request.Request(url, data=data_bytes, headers=headers, method='POST')
                # 增加超时时间到 120 秒
                with urllib.request.urlopen(req, timeout=120) as response:
                    result = json.loads(response.read().decode('utf-8'))
                    return result['choices'][0]['message']['content']
            except urllib.error.HTTPError as e:
                error_msg = e.read().decode('utf-8')
                print(f"API HTTP 错误 {e.code}: {error_msg}")
                return ""
            except urllib.error.URLError as e:
                print(f"网络错误 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    return ""
                import time
                time.sleep(5)  # 等待 5 秒后重试
            except Exception as e:
                print(f"API 调用失败: {e}")
                return ""

    def _parse_and_save_compiled_content(self, content):
        """解析并保存编译后的内容"""
        # 保存原始内容
        output_file = os.path.join(self.wiki_dir, 'compiled_knowledge.md')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"保存原始内容: {output_file}")

        # 尝试解析 LLM 输出的 Markdown 文件
        try:
            import re
            # 匹配 "--- FILE: 文件名.md ---" 格式
            file_pattern = re.compile(r'--- FILE: (.*?)\.md ---', re.DOTALL)
            file_matches = file_pattern.finditer(content)

            files_to_process = []
            for match in file_matches:
                start_pos = match.end()
                # 找到下一个文件标记或文件结束
                next_match = file_pattern.search(content, start_pos)
                if next_match:
                    end_pos = next_match.start()
                else:
                    end_pos = len(content)

                file_name = match.group(1)
                file_content = content[start_pos:end_pos].strip()
                files_to_process.append((file_name, file_content))

            if files_to_process:
                print(f"解析到 {len(files_to_process)} 个文件")
                for file_name, file_content in files_to_process:
                    if file_content:  # 确保内容不为空
                        file_path = os.path.join(self.concepts_dir, f"{file_name}.md")
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(file_content)
                        print(f" 保存文件: {file_path} (大小: {len(file_content)} 字符)")
                    else:
                        print(f"跳过空内容文件: {file_name}.md")
            else:
                print("未找到文件标记，使用备用方法")
                self._generate_concepts_from_raw([])

        except Exception as e:
            print(f"解析失败: {e}")
            # 作为备用，基于原始资料生成概念文件
            self._generate_concepts_from_raw([])

    def _generate_concepts_from_raw(self, changed_files):
        """从原始资料生成概念文件（备用方法）"""
        print("使用备用方法生成概念文件...")

        # 从原始文件名提取概念
        raw_dir = './raw'
        concepts = []

        for file in os.listdir(raw_dir):
            if file.endswith('.txt') or file.endswith('.md'):
                concept_name = os.path.splitext(file)[0]
                concepts.append(concept_name)

        # 为每个概念创建文件
        for concept in concepts:
            file_name = f"{concept}.md"
            file_path = os.path.join(self.concepts_dir, file_name)

            # 生成文件内容
            content = f"""---
title: "{concept}"
date: 2026-04-22
tags: ["物联网", "{concept}"]
sources: ["{concept}.txt"]
---

# {concept}

## 摘要
{concept}是物联网中的重要概念。

## 详细说明
这是 {concept} 的详细说明，基于原始资料生成。

## 相关概念
- [[物联网]]

## 待探索
- [ ] 更多关于 {concept} 的详细信息
"""

            # 保存文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"生成概念文件: {file_path}")