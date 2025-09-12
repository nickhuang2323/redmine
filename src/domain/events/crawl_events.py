
"""
領域事件模組
實現事件驅動架構
"""
from abc import ABC
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict


class DomainEvent(ABC):
    """領域事件基礎類別"""
    
    def __init__(self):
        self.occurred_at = datetime.now()
        self.event_id = f"{self.__class__.__name__}_{id(self)}"


@dataclass
class IssueProcessingStarted(DomainEvent):
    """Issue 開始處理事件"""
    issue_id: str
    
    def __post_init__(self):
        super().__init__()


@dataclass
class IssueProcessingCompleted(DomainEvent):
    """Issue 處理完成事件"""
    issue_id: str
    success: bool
    attachments_downloaded: int
    pdf_generated: bool
    
    def __post_init__(self):
        super().__init__()


@dataclass
class IssueProcessingFailed(DomainEvent):
    """Issue 處理失敗事件"""
    issue_id: str
    error_message: str
    
    def __post_init__(self):
        super().__init__()


@dataclass
class AttachmentDownloadStarted(DomainEvent):
    """附件下載開始事件"""
    issue_id: str
    filename: str
    
    def __post_init__(self):
        super().__init__()


@dataclass
class AttachmentDownloadCompleted(DomainEvent):
    """附件下載完成事件"""
    issue_id: str
    filename: str
    file_size: int
    
    def __post_init__(self):
        super().__init__()


@dataclass
class PdfGenerationStarted(DomainEvent):
    """PDF 生成開始事件"""
    issue_id: str
    
    def __post_init__(self):
        super().__init__()


@dataclass
class PdfGenerationCompleted(DomainEvent):
    """PDF 生成完成事件"""
    issue_id: str
    pdf_size: int
    
    def __post_init__(self):
        super().__init__()


@dataclass
class CrawlSessionStarted(DomainEvent):
    """爬取會話開始事件"""
    session_id: str
    total_issues: int
    
    def __post_init__(self):
        super().__init__()


@dataclass
class CrawlSessionCompleted(DomainEvent):
    """爬取會話完成事件"""
    session_id: str
    total_issues: int
    successful_issues: int
    duration_seconds: float
    
    def __post_init__(self):
        super().__init__()
