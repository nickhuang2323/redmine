
"""
領域實體 - Issue
代表 Redmine 中的單一問題
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class IssueId:
    """問題 ID 值物件"""
    value: str
    
    def __post_init__(self):
        if not self.value or not self.value.strip():
            raise ValueError("Issue ID 不能為空")
        
        # 確保 ID 是字串型態
        self.value = str(self.value).strip()


@dataclass
class Attachment:
    """附件值物件"""
    filename: str
    url: str
    size: Optional[int] = None
    content_type: Optional[str] = None
    
    def __post_init__(self):
        if not self.filename or not self.filename.strip():
            raise ValueError("附件檔名不能為空")
        
        if not self.url or not self.url.strip():
            raise ValueError("附件 URL 不能為空")


@dataclass
class Issue:
    """
    Issue 領域實體
    代表 Redmine 系統中的單一問題
    """
    id: IssueId
    title: str = ""
    description: str = ""
    status: str = ""
    priority: str = ""
    assignee: str = ""
    author: str = ""
    created_date: Optional[datetime] = None
    updated_date: Optional[datetime] = None
    attachments: List[Attachment] = field(default_factory=list)
    custom_fields: Dict[str, Any] = field(default_factory=dict)
    html_content: str = ""
    
    def add_attachment(self, attachment: Attachment) -> None:
        """新增附件"""
        if attachment not in self.attachments:
            self.attachments.append(attachment)
    
    def remove_attachment(self, filename: str) -> bool:
        """移除附件"""
        for attachment in self.attachments:
            if attachment.filename == filename:
                self.attachments.remove(attachment)
                return True
        return False
    
    def get_attachment(self, filename: str) -> Optional[Attachment]:
        """取得指定檔名的附件"""
        for attachment in self.attachments:
            if attachment.filename == filename:
                return attachment
        return None
    
    def has_attachments(self) -> bool:
        """檢查是否有附件"""
        return len(self.attachments) > 0
    
    def get_attachment_count(self) -> int:
        """取得附件數量"""
        return len(self.attachments)
    
    def update_custom_field(self, field_name: str, value: Any) -> None:
        """更新自訂欄位"""
        self.custom_fields[field_name] = value
    
    def get_custom_field(self, field_name: str, default: Any = None) -> Any:
        """取得自訂欄位值"""
        return self.custom_fields.get(field_name, default)
    
    def is_valid(self) -> bool:
        """檢查 Issue 是否有效"""
        return bool(self.id.value and self.title)
    
    def __str__(self) -> str:
        return f"Issue({self.id.value}): {self.title}"
    
    def __repr__(self) -> str:
        return f"Issue(id={self.id.value}, title='{self.title[:50]}...')"
