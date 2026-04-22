import os
import sys
from pathlib import Path
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

class KnowledgeExporter:
    def __init__(self, wiki_dir='./wiki', output_dir='./exports'):
        self.wiki_dir = Path(wiki_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self._setup_fonts()
    
    def _setup_fonts(self):
        """设置中文字体"""
        try:
            # 尝试使用系统字体
            # 在 Windows 系统上，通常有以下中文字体
            font_paths = [
                r'C:\Windows\Fonts\simhei.ttf',      # 黑体
                r'C:\Windows\Fonts\simsun.ttc',      # 宋体
                r'C:\Windows\Fonts\simkai.ttf',      # 楷体
            ]
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    font_name = os.path.basename(font_path).split('.')[0]
                    pdfmetrics.registerFont(TTFont(font_name, font_path))
                    print(f"✅ 注册字体: {font_name}")
                    self.font_name = font_name
                    return
            
            # 如果没有找到系统字体，使用默认字体
            print("⚠️  未找到中文字体，使用默认字体")
            self.font_name = 'Helvetica'
        except Exception as e:
            print(f"❌ 字体设置失败: {e}")
            self.font_name = 'Helvetica'
    
    def export_html(self):
        """导出为 HTML 格式"""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>物联网知识库</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    margin: 40px; 
                    line-height: 1.6;
                }
                .container {
                    max-width: 1000px;
                    margin: 0 auto;
                }
                .page { 
                    margin-bottom: 60px; 
                    border-bottom: 2px solid #e0e0e0; 
                    padding-bottom: 30px;
                }
                h1 { 
                    color: #2c3e50;
                    border-bottom: 1px solid #3498db;
                    padding-bottom: 10px;
                }
                h2 { 
                    color: #34495e;
                    margin-top: 30px;
                }
                h3 { 
                    color: #7f8c8d;
                }
                .frontmatter { 
                    background: #f8f9fa; 
                    padding: 15px; 
                    border-radius: 8px;
                    margin-bottom: 20px;
                    border-left: 4px solid #3498db;
                }
                code { 
                    background: #f0f0f0; 
                    padding: 2px 5px; 
                    border-radius: 3px;
                }
                pre {
                    background: #f5f5f5;
                    padding: 15px;
                    border-radius: 8px;
                    overflow-x: auto;
                }
                ul, ol {
                    margin-left: 20px;
                }
                li {
                    margin-bottom: 8px;
                }
                .link {
                    color: #3498db;
                    text-decoration: none;
                }
                .link:hover {
                    text-decoration: underline;
                }
                .footer {
                    margin-top: 50px;
                    padding-top: 20px;
                    border-top: 1px solid #e0e0e0;
                    text-align: center;
                    color: #7f8c8d;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>物联网知识库</h1>
                <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>页面数量: {len(list(self.wiki_dir.glob("*.md")))}</p>
        """
        
        # 读取所有 Markdown 文件
        for md_file in sorted(self.wiki_dir.glob("*.md")):
            content = md_file.read_text(encoding='utf-8')
            filename = md_file.stem
            
            # 简单的 Markdown 到 HTML 转换
            html_content += f"""
                <div class="page">
                    <h2>{filename}</h2>
                    <pre>{content}</pre>
                </div>
            """
        
        html_content += """
                <div class="footer">
                    <p>知识库导出工具</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # 生成文件名
        output_file = self.output_dir / f"knowledge_base_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        output_file.write_text(html_content, encoding='utf-8')
        print(f"✅ HTML 导出成功: {output_file}")
        return output_file
    
    def export_markdown(self):
        """导出为 Markdown 格式"""
        # 生成文件名
        output_file = self.output_dir / f"knowledge_base_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        # 准备内容
        md_content = f"""# 物联网知识库
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
页面数量: {len(list(self.wiki_dir.glob('*.md')))}

"""
        
        # 读取所有 Markdown 文件
        for md_file in sorted(self.wiki_dir.glob("*.md")):
            content = md_file.read_text(encoding='utf-8')
            filename = md_file.stem
            
            # 添加页面标题和内容
            md_content += f"## {filename}\n\n"
            md_content += content
            md_content += "\n\n" + "=" * 80 + "\n\n"
        
        # 写入文件
        output_file.write_text(md_content, encoding='utf-8')
        print(f"✅ Markdown 导出成功: {output_file}")
        return output_file
    
    def export_pdf(self):
        """使用 reportlab 导出为 PDF 格式"""
        # 生成文件名
        output_file = self.output_dir / f"knowledge_base_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # 创建 PDF 文档
        doc = SimpleDocTemplate(
            str(output_file),
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # 准备内容
        story = []
        styles = getSampleStyleSheet()
        
        # 创建支持中文的样式
        normal_style = ParagraphStyle(
            'NormalChinese',
            parent=styles['Normal'],
            fontName=self.font_name,
            fontSize=12,
            leading=18
        )
        
        title_style = ParagraphStyle(
            'TitleChinese',
            parent=styles['Title'],
            fontName=self.font_name,
            fontSize=24,
            leading=30
        )
        
        heading1_style = ParagraphStyle(
            'Heading1Chinese',
            parent=styles['Heading1'],
            fontName=self.font_name,
            fontSize=18,
            leading=24
        )
        
        # 添加标题
        title = Paragraph("物联网知识库", title_style)
        story.append(title)
        story.append(Spacer(1, 20))
        
        # 添加生成信息
        info = f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>"
        info += f"页面数量: {len(list(self.wiki_dir.glob('*.md')))}"
        info_para = Paragraph(info, normal_style)
        story.append(info_para)
        story.append(Spacer(1, 30))
        
        # 读取所有 Markdown 文件
        for md_file in sorted(self.wiki_dir.glob("*.md")):
            content = md_file.read_text(encoding='utf-8')
            filename = md_file.stem
            
            # 添加页面标题
            page_title = Paragraph(filename, heading1_style)
            story.append(page_title)
            story.append(Spacer(1, 15))
            
            # 添加内容（使用普通段落而非预格式化，避免乱码）
            # 将内容按行分割，逐行处理
            lines = content.split('\n')
            for line in lines:
                if line.strip():
                    para = Paragraph(line, normal_style)
                    story.append(para)
                story.append(Spacer(1, 6))
            
            story.append(Spacer(1, 40))
        
        # 生成 PDF
        try:
            doc.build(story)
            print(f"✅ PDF 导出成功: {output_file}")
            return output_file
        except Exception as e:
            print(f"❌ PDF 导出失败: {e}")
            return None
    
    def export(self, format='html'):
        """通用导出方法"""
        if format.lower() == 'html':
            return self.export_html()
        elif format.lower() == 'pdf':
            return self.export_pdf()
        elif format.lower() == 'md' or format.lower() == 'markdown':
            return self.export_markdown()
        else:
            print(f"❌ 不支持的格式: {format}")
            return None

if __name__ == "__main__":
    exporter = KnowledgeExporter()
    
    # 解析命令行参数
    if len(sys.argv) > 1:
        format = sys.argv[1]
        exporter.export(format)
    else:
        # 默认导出为 HTML
        exporter.export('html')
