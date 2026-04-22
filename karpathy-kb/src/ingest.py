﻿﻿﻿import os
import re
import requests
from pathlib import Path
from typing import Optional, List

class Ingestor:
    """多格式文档导入器 - 支持 PDF、网页、Markdown"""
    
    def __init__(self, raw_dir='./raw'):
        self.raw_dir = Path(raw_dir)
        self.raw_dir.mkdir(exist_ok=True)
    
    def ingest_pdf(self, pdf_path: str) -> Optional[str]:
        """导入 PDF 文件"""
        try:
            from pypdf import PdfReader
            reader = PdfReader(pdf_path)
            content = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    content.append(text)
            
            output_file = self.raw_dir / f"{Path(pdf_path).stem}.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"# 来源: {pdf_path}\n\n")
                f.write('\n'.join(content))
            print(f"✅ PDF 导入成功: {output_file}")
            return str(output_file)
        except ImportError:
            print("❌ 请安装 pypdf: pip install pypdf")
            return None
        except Exception as e:
            print(f"❌ PDF 导入失败: {e}")
            return None
    
    def ingest_webpage(self, url: str) -> Optional[str]:
        """导入网页内容"""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # 简单提取文本
            text = response.text
            text = re.sub(r'<[^>]+>', ' ', text)
            text = re.sub(r'\s+', ' ', text)
            
            # 提取标题
            title_match = re.search(r'<title>(.*?)</title>', response.text, re.IGNORECASE)
            title = title_match.group(1) if title_match else 'webpage'
            title = re.sub(r'[\\/*?:"<>|]', '', title)[:50]
            
            output_file = self.raw_dir / f"{title}.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"# 来源: {url}\n\n")
                f.write(text[:20000])  # 限制长度
            print(f"✅ 网页导入成功: {output_file}")
            return str(output_file)
        except Exception as e:
            print(f"❌ 网页导入失败: {e}")
            return None
    
    def ingest_markdown(self, file_path: str) -> Optional[str]:
        """导入 Markdown 文件"""
        try:
            import shutil
            dest = self.raw_dir / Path(file_path).name
            shutil.copy(file_path, dest)
            print(f"✅ Markdown 导入成功: {dest}")
            return str(dest)
        except Exception as e:
            print(f"❌ 导入失败: {e}")
            return None
    
    def ingest_text(self, content: str, filename: str) -> str:
        """直接导入文本内容"""
        output_file = self.raw_dir / filename
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ 文本导入成功: {output_file}")
        return str(output_file)
    
    def list_raw_files(self) -> List[str]:
        """列出所有原始文件"""
        return [str(f) for f in self.raw_dir.glob('*') if f.is_file()]
