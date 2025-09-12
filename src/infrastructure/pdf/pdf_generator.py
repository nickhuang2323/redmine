
"""
PDF 生成實現
"""
import asyncio
from pathlib import Path
from typing import Optional
import pdfkit
from ...domain.entities.issue import Issue
from ...domain.value_objects.common import FilePath
from ...domain.repositories.interfaces import PdfRepository
from ..config.settings import config


class WkhtmltopdfPdfRepository(PdfRepository):
    """使用 wkhtmltopdf 的 PDF 儲存庫"""
    
    async def generate_pdf(self, issue: Issue, output_path: FilePath) -> bool:
        """生成 PDF"""
        try:
            # 確保輸出目錄存在
            output_path.to_path().parent.mkdir(parents=True, exist_ok=True)
            
            # 在執行緒池中執行 PDF 生成（因為 pdfkit 是同步的）
            loop = asyncio.get_event_loop()
            success = await loop.run_in_executor(
                None, 
                self._generate_pdf_sync, 
                issue, 
                output_path
            )
            
            return success
            
        except Exception as e:
            print(f"生成 PDF 失敗: {e}")
            return False
    
    def _generate_pdf_sync(self, issue: Issue, output_path: FilePath) -> bool:
        """同步生成 PDF"""
        try:
            # 處理 HTML 內容
            html_content = self._prepare_html_content(issue.html_content)
            
            # 設定 PDF 選項
            options = config.get_pdf_options()
            
            # 設定 wkhtmltopdf 配置
            pdf_config = pdfkit.configuration(wkhtmltopdf=config.pdf.wkhtmltopdf_path)
            
            # 生成 PDF
            pdfkit.from_string(
                html_content, 
                output_path.path, 
                options=options, 
                configuration=pdf_config
            )
            
            # 檢查檔案是否成功生成
            pdf_path = output_path.to_path()
            return pdf_path.exists() and pdf_path.stat().st_size > 0
            
        except Exception as e:
            print(f"同步生成 PDF 失敗: {e}")
            return False
    
    def _prepare_html_content(self, html_content: str) -> str:
        """準備 HTML 內容用於 PDF 生成"""
        # 修正相對路徑為絕對路徑
        prepared_html = html_content.replace(
            'href="/', 
            f'href="{config.redmine.base_url}/'
        )
        prepared_html = prepared_html.replace(
            'src="/', 
            f'src="{config.redmine.base_url}/'
        )
        
        return prepared_html
    
    async def pdf_exists(self, output_path: FilePath) -> bool:
        """檢查 PDF 是否已存在"""
        try:
            pdf_path = output_path.to_path()
            return pdf_path.exists() and pdf_path.stat().st_size > 0
        except Exception:
            return False
