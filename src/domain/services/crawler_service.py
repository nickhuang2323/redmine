
"""
領域服務模組
包含跨越多個聚合的業務邏輯
"""
from typing import List, Optional
from ..entities.issue import Issue, IssueId, Attachment
from ..value_objects.common import CrawlRequest, CrawlResult, FilePath
from ..repositories.interfaces import IssueRepository, AttachmentRepository, PdfRepository
from ..events.crawl_events import (
    IssueProcessingStarted, IssueProcessingCompleted, IssueProcessingFailed,
    AttachmentDownloadStarted, AttachmentDownloadCompleted,
    PdfGenerationStarted, PdfGenerationCompleted
)


class IssueCrawlerService:
    """Issue 爬取領域服務"""
    
    def __init__(
        self,
        issue_repository: IssueRepository,
        attachment_repository: AttachmentRepository,
        pdf_repository: PdfRepository
    ):
        self._issue_repository = issue_repository
        self._attachment_repository = attachment_repository
        self._pdf_repository = pdf_repository
        self._event_handlers: List = []
    
    def add_event_handler(self, handler) -> None:
        """新增事件處理器"""
        self._event_handlers.append(handler)
    
    def _publish_event(self, event) -> None:
        """發布事件"""
        import asyncio
        for handler in self._event_handlers:
            try:
                if asyncio.iscoroutinefunction(handler.handle):
                    # 如果在事件循環中，創建任務
                    try:
                        loop = asyncio.get_running_loop()
                        loop.create_task(handler.handle(event))
                    except RuntimeError:
                        # 沒有運行的事件循環，同步執行
                        asyncio.run(handler.handle(event))
                else:
                    handler.handle(event)
            except Exception as e:
                print(f"事件處理錯誤: {e}")
    
    async def process_issue(self, issue_id: IssueId, output_directory: FilePath) -> bool:
        """
        處理單一 Issue
        
        Args:
            issue_id: Issue ID
            output_directory: 輸出目錄
            
        Returns:
            是否處理成功
        """
        try:
            # 發布開始處理事件
            self._publish_event(IssueProcessingStarted(issue_id.value))
            
            # 取得 Issue
            issue = await self._issue_repository.get_by_id(issue_id)
            if not issue:
                self._publish_event(IssueProcessingFailed(
                    issue_id.value, 
                    f"找不到 Issue: {issue_id.value}"
                ))
                return False
            
            # 處理附件
            attachments_downloaded = await self._process_attachments(
                issue, output_directory
            )
            
            # 生成 PDF
            pdf_generated = await self._generate_pdf(issue, output_directory)
            
            # 儲存 Issue
            await self._issue_repository.save(issue)
            
            # 發布完成事件
            self._publish_event(IssueProcessingCompleted(
                issue_id.value,
                True,
                attachments_downloaded,
                pdf_generated
            ))
            
            return True
            
        except Exception as e:
            self._publish_event(IssueProcessingFailed(
                issue_id.value,
                str(e)
            ))
            return False
    
    async def _process_attachments(self, issue: Issue, output_directory: FilePath) -> int:
        """處理附件下載"""
        downloaded_count = 0
        
        for attachment in issue.attachments:
            try:
                # 發布下載開始事件
                self._publish_event(AttachmentDownloadStarted(
                    issue.id.value,
                    attachment.filename
                ))
                
                # 建立附件儲存路徑
                attachment_dir = output_directory.to_path() / "attachments" / issue.id.value
                attachment_path = FilePath(str(attachment_dir / attachment.filename))
                
                # 下載附件
                success = await self._attachment_repository.download_attachment(
                    attachment, attachment_path
                )
                
                if success:
                    downloaded_count += 1
                    # 發布下載完成事件
                    self._publish_event(AttachmentDownloadCompleted(
                        issue.id.value,
                        attachment.filename,
                        attachment.size or 0
                    ))
                
            except Exception as e:
                print(f"下載附件失敗 {attachment.filename}: {e}")
        
        return downloaded_count
    
    async def _generate_pdf(self, issue: Issue, output_directory: FilePath) -> bool:
        """生成 PDF"""
        try:
            # 發布 PDF 生成開始事件
            self._publish_event(PdfGenerationStarted(issue.id.value))
            
            # 建立 PDF 路徑 - 使用 Issue 標題作為檔名
            pdf_dir = output_directory.to_path() / "pdfs"
            
            # 清理標題作為檔名，如果沒有標題則使用 issue ID
            if issue.title:
                safe_title = self._sanitize_filename(issue.title)
                pdf_filename = f"{issue.id.value}_{safe_title}.pdf"
            else:
                pdf_filename = f"issue_{issue.id.value}.pdf"
            
            pdf_path = FilePath(str(pdf_dir / pdf_filename))
            
            # 生成 PDF
            success = await self._pdf_repository.generate_pdf(issue, pdf_path)
            
            if success:
                # 發布 PDF 生成完成事件
                self._publish_event(PdfGenerationCompleted(
                    issue.id.value,
                    pdf_path.to_path().stat().st_size if pdf_path.to_path().exists() else 0
                ))
            
            return success
            
        except Exception as e:
            print(f"生成 PDF 失敗: {e}")
            return False
    
    def _sanitize_filename(self, filename: str) -> str:
        """清理檔案名稱，移除非法字元"""
        import re
        # 移除或替換非法字元
        illegal_chars = r'[<>:"/\\|?*]'
        filename = re.sub(illegal_chars, '_', filename)
        
        # 移除開頭和結尾的空白和點
        filename = filename.strip(' .')
        
        # 限制檔名長度
        if len(filename) > 100:
            filename = filename[:100]
        
        # 如果檔案名稱為空，給予預設名稱
        if not filename:
            filename = "unnamed_file"
        
        return filename


class CrawlValidationService:
    """爬取驗證服務"""
    
    @staticmethod
    def validate_crawl_request(request: CrawlRequest) -> List[str]:
        """
        驗證爬取請求
        
        Returns:
            錯誤訊息列表，空列表表示驗證通過
        """
        errors = []
        
        # 驗證問題編號
        if not request.issue_numbers:
            errors.append("問題編號列表不能為空")
        
        for issue_num in request.issue_numbers:
            if not str(issue_num).strip():
                errors.append(f"無效的問題編號: {issue_num}")
        
        # 驗證輸出目錄
        try:
            output_path = request.output_directory.to_path()
            if not output_path.parent.exists():
                errors.append(f"輸出目錄的父目錄不存在: {output_path.parent}")
        except Exception as e:
            errors.append(f"無效的輸出目錄路徑: {e}")
        
        return errors
    
    @staticmethod
    def validate_issue_id(issue_id: str) -> bool:
        """驗證 Issue ID 格式"""
        if not issue_id or not str(issue_id).strip():
            return False
        
        # 可以在這裡加入更多的格式驗證邏輯
        try:
            int(issue_id)  # 檢查是否為數字
            return True
        except ValueError:
            return False
