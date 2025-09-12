
"""檔案儲存相關實現"""
import os
import asyncio
from pathlib import Path
from typing import Optional
from ...domain.entities.issue import Attachment
from ...domain.value_objects.common import FilePath
from ...domain.repositories.interfaces import AttachmentRepository
from ..http.redmine_client import RedmineHttpClient
from ..config.settings import config


class FileSystemAttachmentRepository(AttachmentRepository):
    """檔案系統附件儲存庫"""
    
    def __init__(self, http_client: RedmineHttpClient):
        self._http_client = http_client
    
    async def download_attachment(self, attachment: Attachment, save_path: FilePath) -> bool:
        """下載附件到指定路徑"""
        try:
            # 確保目錄存在
            save_path.to_path().parent.mkdir(parents=True, exist_ok=True)
            
            # 下載檔案內容
            async with self._http_client as client:
                content = await client.download_file(attachment.url)
                if content is None:
                    return False
            
            # 儲存檔案
            return await self.save_attachment(attachment, content, save_path)
            
        except Exception as e:
            print(f"下載附件失敗 {attachment.filename}: {e}")
            return False
    
    async def get_attachment_content(self, attachment: Attachment) -> bytes:
        """取得附件內容"""
        async with self._http_client as client:
            content = await client.download_file(attachment.url)
            return content or b""
    
    async def save_attachment(self, attachment: Attachment, content: bytes, save_path: FilePath) -> bool:
        """儲存附件到檔案系統"""
        try:
            # 檢查檔案大小限制
            if len(content) > config.security.max_file_size:
                print(f"附件 {attachment.filename} 大小超過限制")
                return False
            
            # 檢查副檔名
            file_extension = save_path.get_extension()
            if file_extension not in config.security.allowed_file_extensions:
                print(f"不允許的檔案類型: {file_extension}")
                return False
            
            # 在執行緒池中寫入檔案
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._write_file_sync, save_path.path, content)
            
            # 更新附件大小資訊
            attachment.size = len(content)
            
            return True
            
        except Exception as e:
            print(f"儲存附件失敗 {attachment.filename}: {e}")
            return False
    
    def _write_file_sync(self, file_path: str, content: bytes) -> None:
        """同步寫入檔案"""
        with open(file_path, 'wb') as f:
            f.write(content)
    
    def _sanitize_filename(self, filename: str) -> str:
        """清理檔案名稱"""
        # 移除危險字元
        import re
        safe_filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        safe_filename = safe_filename.strip(' .')
        
        if not safe_filename:
            safe_filename = "unnamed_file"
        
        return safe_filename
