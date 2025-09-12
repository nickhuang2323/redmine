
"""
爬蟲工廠模組
實現 Factory 和 Abstract Factory 模式
"""
from abc import ABC, abstractmethod
from ..http.redmine_client import RedmineHttpClient, RedmineIssueRepository
from ..storage.file_storage import FileSystemAttachmentRepository
from ..pdf.pdf_generator import WkhtmltopdfPdfRepository
from ...domain.services.crawler_service import IssueCrawlerService
from ...application.services.crawler_service import CrawlerService


class RepositoryFactory(ABC):
    """儲存庫抽象工廠"""
    
    @abstractmethod
    def create_issue_repository(self, http_client: RedmineHttpClient):
        """建立 Issue 儲存庫"""
        pass
    
    @abstractmethod
    def create_attachment_repository(self, http_client: RedmineHttpClient):
        """建立附件儲存庫"""
        pass
    
    @abstractmethod
    def create_pdf_repository(self):
        """建立 PDF 儲存庫"""
        pass


class RedmineRepositoryFactory(RepositoryFactory):
    """Redmine 儲存庫工廠"""
    
    def create_issue_repository(self, http_client: RedmineHttpClient):
        """建立 Redmine Issue 儲存庫"""
        return RedmineIssueRepository(http_client)
    
    def create_attachment_repository(self, http_client: RedmineHttpClient):
        """建立檔案系統附件儲存庫"""
        return FileSystemAttachmentRepository(http_client)
    
    def create_pdf_repository(self):
        """建立 wkhtmltopdf PDF 儲存庫"""
        return WkhtmltopdfPdfRepository()


class CrawlerFactory:
    """爬蟲工廠 - 主要工廠類別"""
    
    def __init__(self, repository_factory: RepositoryFactory = None):
        self._repository_factory = repository_factory or RedmineRepositoryFactory()
    
    def create_crawler_service(self, session_cookie: str = "") -> CrawlerService:
        """
        建立完整的爬蟲服務
        
        Args:
            session_cookie: Redmine 會話 cookie
            
        Returns:
            配置完成的爬蟲服務
        """
        # 建立 HTTP 客戶端
        http_client = RedmineHttpClient(session_cookie)
        
        # 建立各種儲存庫
        issue_repository = self._repository_factory.create_issue_repository(http_client)
        attachment_repository = self._repository_factory.create_attachment_repository(http_client)
        pdf_repository = self._repository_factory.create_pdf_repository()
        
        # 建立領域服務
        domain_crawler_service = IssueCrawlerService(
            issue_repository,
            attachment_repository,
            pdf_repository
        )
        
        # 建立應用服務
        app_crawler_service = CrawlerService(domain_crawler_service)
        
        return app_crawler_service
    
    def create_http_client(self, session_cookie: str = "") -> RedmineHttpClient:
        """建立 HTTP 客戶端"""
        return RedmineHttpClient(session_cookie)
    
    def create_issue_repository(self, session_cookie: str = ""):
        """建立 Issue 儲存庫"""
        http_client = self.create_http_client(session_cookie)
        return self._repository_factory.create_issue_repository(http_client)
    
    def create_attachment_repository(self, session_cookie: str = ""):
        """建立附件儲存庫"""
        http_client = self.create_http_client(session_cookie)
        return self._repository_factory.create_attachment_repository(http_client)
    
    def create_pdf_repository(self):
        """建立 PDF 儲存庫"""
        return self._repository_factory.create_pdf_repository()


# 全域工廠實例
crawler_factory = CrawlerFactory()
