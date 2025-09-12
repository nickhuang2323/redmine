
"""
HTTP 客戶端實現
處理與 Redmine API 的通訊
"""
import aiohttp
import asyncio
from typing import Optional, Dict, Any
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from ...domain.entities.issue import Issue, IssueId, Attachment
from ...domain.repositories.interfaces import IssueRepository
from ..config.settings import config


class RedmineHttpClient:
    """Redmine HTTP 客戶端"""
    
    def __init__(self, session_cookie: str = ""):
        self._session_cookie = session_cookie
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """非同步上下文管理器進入"""
        headers = {
            'User-Agent': config.redmine.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        cookies = {}
        if self._session_cookie:
            cookies['_redmine_session'] = self._session_cookie
        
        timeout = aiohttp.ClientTimeout(total=config.redmine.timeout)
        self._session = aiohttp.ClientSession(
            headers=headers,
            cookies=cookies,
            timeout=timeout
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """非同步上下文管理器退出"""
        if self._session:
            await self._session.close()
    
    async def get_issue_html(self, issue_id: IssueId) -> Optional[str]:
        """
        取得 Issue 的 HTML 內容
        
        Args:
            issue_id: Issue ID
            
        Returns:
            HTML 內容，失敗時返回 None
        """
        if not self._session:
            raise RuntimeError("HTTP 客戶端未初始化")
        
        url = f"{config.redmine.base_url}/issues/{issue_id.value}"
        
        try:
            async with self._session.get(url) as response:
                response.raise_for_status()
                return await response.text()
        except Exception as e:
            print(f"取得 Issue HTML 失敗: {e}")
            return None
    
    async def download_file(self, url: str) -> Optional[bytes]:
        """
        下載檔案
        
        Args:
            url: 檔案 URL
            
        Returns:
            檔案內容，失敗時返回 None
        """
        if not self._session:
            raise RuntimeError("HTTP 客戶端未初始化")
        
        try:
            # 處理相對 URL
            if url.startswith('/'):
                url = urljoin(config.redmine.base_url, url)
            
            async with self._session.get(url) as response:
                response.raise_for_status()
                return await response.read()
        except Exception as e:
            print(f"下載檔案失敗 {url}: {e}")
            return None


class RedmineIssueRepository(IssueRepository):
    """Redmine Issue 儲存庫實現"""
    
    def __init__(self, http_client: RedmineHttpClient):
        self._http_client = http_client
    
    async def get_by_id(self, issue_id: IssueId) -> Optional[Issue]:
        """根據 ID 取得 Issue"""
        async with self._http_client as client:
            html_content = await client.get_issue_html(issue_id)
            if not html_content:
                return None
            
            return self._parse_issue_from_html(issue_id, html_content)
    
    async def save(self, issue: Issue) -> None:
        """儲存 Issue（此實現為空，因為我們只讀取不寫入）"""
        pass
    
    async def exists(self, issue_id: IssueId) -> bool:
        """檢查 Issue 是否存在"""
        async with self._http_client as client:
            html_content = await client.get_issue_html(issue_id)
            return html_content is not None
    
    def _parse_issue_from_html(self, issue_id: IssueId, html_content: str) -> Issue:
        """從 HTML 解析 Issue"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 解析基本資訊
        title = self._extract_title(soup)
        description = self._extract_description(soup)
        status = self._extract_status(soup)
        priority = self._extract_priority(soup)
        assignee = self._extract_assignee(soup)
        author = self._extract_author(soup)
        
        # 解析附件
        attachments = self._extract_attachments(soup)
        
        # 建立 Issue 物件
        issue = Issue(
            id=issue_id,
            title=title,
            description=description,
            status=status,
            priority=priority,
            assignee=assignee,
            author=author,
            html_content=html_content
        )
        
        # 新增附件
        for attachment in attachments:
            issue.add_attachment(attachment)
        
        return issue
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """提取標題 - 結合 content div 中的 h2 和 subject div 中的 h3"""
        title_parts = []
        
        # 首先提取 content div 中的第一個 h2 標籤
        content_div = soup.find('div', id='content')
        if content_div:
            h2_element = content_div.find('h2')
            if h2_element:
                h2_text = h2_element.get_text(strip=True)
                if h2_text:
                    title_parts.append(h2_text)
        
        # 然後提取 subject div 中的 h3 標籤
        subject_div = soup.find('div', class_='subject')
        if subject_div:
            h3_element = subject_div.find('h3')
            if h3_element:
                h3_text = h3_element.get_text(strip=True)
                if h3_text:
                    title_parts.append(h3_text)
        
        # {Issue編號}_{h2標籤內容} - {h3標籤內容}.pdf
        # 組合標題
        if title_parts:
            return " - ".join(title_parts)
        
        # 如果都沒找到，回退到原來的 h1 標籤
        title_element = soup.find('h1')
        if title_element:
            return title_element.get_text(strip=True)
        
        return ""
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """提取描述"""
        desc_element = soup.find('div', class_='description')
        if desc_element:
            return desc_element.get_text(strip=True)
        return ""
    
    def _extract_status(self, soup: BeautifulSoup) -> str:
        """提取狀態"""
        status_element = soup.find('span', class_='status')
        if status_element:
            return status_element.get_text(strip=True)
        return ""
    
    def _extract_priority(self, soup: BeautifulSoup) -> str:
        """提取優先級"""
        priority_element = soup.find('span', class_='priority')
        if priority_element:
            return priority_element.get_text(strip=True)
        return ""
    
    def _extract_assignee(self, soup: BeautifulSoup) -> str:
        """提取負責人"""
        assignee_element = soup.find('span', class_='assignee')
        if assignee_element:
            return assignee_element.get_text(strip=True)
        return ""
    
    def _extract_author(self, soup: BeautifulSoup) -> str:
        """提取作者"""
        author_element = soup.find('span', class_='author')
        if author_element:
            return author_element.get_text(strip=True)
        return ""
    
    def _extract_attachments(self, soup: BeautifulSoup) -> list:
        """提取附件"""
        attachments = []
        attachment_links = soup.find_all('a', class_='icon icon-attachment')
        
        for link in attachment_links:
            filename = link.get_text(strip=True)
            url = link.get('href', '')
            
            if filename and url:
                # 處理相對 URL
                if url.startswith('/'):
                    url = urljoin(config.redmine.base_url, url)
                
                attachment = Attachment(
                    filename=filename,
                    url=url
                )
                attachments.append(attachment)
        
        return attachments
