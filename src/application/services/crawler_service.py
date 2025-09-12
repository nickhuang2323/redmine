
"""
應用服務模組
協調領域邏輯並提供外部介面
"""
import asyncio
import time
from typing import List
from ...domain.entities.issue import IssueId
from ...domain.value_objects.common import CrawlRequest, CrawlResult, FilePath
from ...domain.services.crawler_service import IssueCrawlerService, CrawlValidationService
from ...domain.events.crawl_events import CrawlSessionStarted, CrawlSessionCompleted
from ...infrastructure.config.settings import config


class CrawlerService:
    """爬蟲應用服務"""
    
    def __init__(self, crawler_service: IssueCrawlerService):
        self._crawler_service = crawler_service
        self._session_id = ""
    
    async def crawl_issues(self, crawl_request: CrawlRequest) -> CrawlResult:
        """
        爬取多個 Issues
        
        Args:
            crawl_request: 爬取請求
            
        Returns:
            爬取結果
        """
        # 驗證請求
        validation_errors = CrawlValidationService.validate_crawl_request(crawl_request)
        if validation_errors:
            raise ValueError(f"請求驗證失敗: {', '.join(validation_errors)}")
        
        # 產生會話 ID
        self._session_id = f"crawl_{int(time.time())}"
        
        # 發布會話開始事件
        start_event = CrawlSessionStarted(self._session_id, crawl_request.get_issue_count())
        self._crawler_service._publish_event(start_event)
        
        start_time = time.time()
        successful_count = 0
        failed_count = 0
        
        try:
            # 處理每個 Issue
            for issue_number in crawl_request.issue_numbers:
                try:
                    issue_id = IssueId(issue_number)
                    success = await self._crawler_service.process_issue(
                        issue_id, crawl_request.output_directory
                    )
                    
                    if success:
                        successful_count += 1
                    else:
                        failed_count += 1
                    
                    # 請求延遲
                    await asyncio.sleep(config.redmine.request_delay)
                    
                except Exception as e:
                    print(f"處理 Issue {issue_number} 時發生錯誤: {e}")
                    failed_count += 1
            
            # 計算結果
            end_time = time.time()
            duration = end_time - start_time
            
            result = CrawlResult(
                total_issues=crawl_request.get_issue_count(),
                successful_issues=successful_count,
                failed_issues=failed_count,
                attachments_downloaded=0,  # 這個需要從事件中計算
                pdfs_generated=successful_count  # 假設成功的都有生成 PDF
            )
            
            # 發布會話完成事件
            complete_event = CrawlSessionCompleted(
                self._session_id,
                crawl_request.get_issue_count(),
                successful_count,
                duration
            )
            self._crawler_service._publish_event(complete_event)
            
            return result
            
        except Exception as e:
            # 發布失敗事件
            complete_event = CrawlSessionCompleted(
                self._session_id,
                crawl_request.get_issue_count(),
                successful_count,
                time.time() - start_time
            )
            self._crawler_service._publish_event(complete_event)
            raise e
    
    async def crawl_single_issue(self, issue_number: str, output_directory: str) -> bool:
        """
        爬取單一 Issue
        
        Args:
            issue_number: Issue 編號
            output_directory: 輸出目錄
            
        Returns:
            是否成功
        """
        # 建立請求
        crawl_request = CrawlRequest(
            issue_numbers=[issue_number],
            output_directory=FilePath(output_directory)
        )
        
        # 執行爬取
        result = await self.crawl_issues(crawl_request)
        
        return result.successful_issues > 0
    
    def add_event_handler(self, handler) -> None:
        """新增事件處理器"""
        self._crawler_service.add_event_handler(handler)
