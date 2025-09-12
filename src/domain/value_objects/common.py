
"""
值物件模組
包含系統中的不可變值物件
"""
from dataclasses import dataclass
from typing import List
from pathlib import Path


@dataclass(frozen=True)
class FilePath:
    """檔案路徑值物件"""
    path: str
    
    def __post_init__(self):
        if not self.path or not self.path.strip():
            raise ValueError("檔案路徑不能為空")
    
    def to_path(self) -> Path:
        """轉換為 Path 物件"""
        return Path(self.path)
    
    def get_extension(self) -> str:
        """取得副檔名"""
        return Path(self.path).suffix.lower()
    
    def get_filename(self) -> str:
        """取得檔案名稱"""
        return Path(self.path).name
    
    def is_pdf(self) -> bool:
        """檢查是否為 PDF 檔案"""
        return self.get_extension() == '.pdf'


@dataclass(frozen=True)
class CrawlRequest:
    """爬取請求值物件"""
    issue_numbers: List[str]
    output_directory: FilePath
    session_cookie: str = ""
    
    def __post_init__(self):
        if not self.issue_numbers:
            raise ValueError("問題編號列表不能為空")
        
        # 驗證每個問題編號
        for issue_num in self.issue_numbers:
            if not issue_num or not str(issue_num).strip():
                raise ValueError(f"無效的問題編號: {issue_num}")
    
    def get_issue_count(self) -> int:
        """取得問題數量"""
        return len(self.issue_numbers)


@dataclass(frozen=True)
class CrawlResult:
    """爬取結果值物件"""
    total_issues: int
    successful_issues: int
    failed_issues: int
    attachments_downloaded: int
    pdfs_generated: int
    
    @property
    def success_rate(self) -> float:
        """成功率"""
        if self.total_issues == 0:
            return 0.0
        return self.successful_issues / self.total_issues
    
    @property
    def is_fully_successful(self) -> bool:
        """是否完全成功"""
        return self.successful_issues == self.total_issues
    
    def __str__(self) -> str:
        return (f"CrawlResult(成功: {self.successful_issues}/{self.total_issues}, "
                f"附件: {self.attachments_downloaded}, PDF: {self.pdfs_generated})")


@dataclass(frozen=True)
class ProcessingStatistics:
    """處理統計值物件"""
    start_time: str
    end_time: str
    duration_seconds: float
    bytes_downloaded: int
    
    def get_download_speed(self) -> float:
        """計算下載速度 (bytes/sec)"""
        if self.duration_seconds <= 0:
            return 0.0
        return self.bytes_downloaded / self.duration_seconds
