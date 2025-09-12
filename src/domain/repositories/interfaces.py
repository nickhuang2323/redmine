
"""
儲存庫介面模組
定義資料存取的抽象介面
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.issue import Issue, IssueId, Attachment
from ..value_objects.common import FilePath


class IssueRepository(ABC):
    """Issue 儲存庫抽象介面"""
    
    @abstractmethod
    async def get_by_id(self, issue_id: IssueId) -> Optional[Issue]:
        """根據 ID 取得 Issue"""
        pass
    
    @abstractmethod
    async def save(self, issue: Issue) -> None:
        """儲存 Issue"""
        pass
    
    @abstractmethod
    async def exists(self, issue_id: IssueId) -> bool:
        """檢查 Issue 是否存在"""
        pass


class AttachmentRepository(ABC):
    """附件儲存庫抽象介面"""
    
    @abstractmethod
    async def download_attachment(self, attachment: Attachment, save_path: FilePath) -> bool:
        """下載附件"""
        pass
    
    @abstractmethod
    async def get_attachment_content(self, attachment: Attachment) -> bytes:
        """取得附件內容"""
        pass
    
    @abstractmethod
    async def save_attachment(self, attachment: Attachment, content: bytes, save_path: FilePath) -> bool:
        """儲存附件"""
        pass


class PdfRepository(ABC):
    """PDF 儲存庫抽象介面"""
    
    @abstractmethod
    async def generate_pdf(self, issue: Issue, output_path: FilePath) -> bool:
        """生成 PDF"""
        pass
    
    @abstractmethod
    async def pdf_exists(self, output_path: FilePath) -> bool:
        """檢查 PDF 是否已存在"""
        pass
