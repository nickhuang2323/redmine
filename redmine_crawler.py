
import requests
import os
import time
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import pdfkit
from typing import List, Optional
from src.infrastructure.config.settings import config as settings_config

class RedmineCrawler:
    def __init__(self, session_cookie: str = "", output_dir: Optional[str] = None):
        """
        初始化 Redmine 爬蟲
        
        Args:
            session_cookie: _redmine_session cookie 值
            output_dir: 輸出目錄，若未指定則使用預設值
        """
        self.base_url = settings_config.redmine.base_url
        self.session = requests.Session()
        self.output_dir = Path(output_dir or settings_config.paths.output_dir)
        
        # 設定 session cookie
        if session_cookie:
            self.session.cookies.set(
                '_redmine_session', 
                session_cookie, 
                domain='redmine.etzone.net',
                path='/',
                secure=True
            )
        
        # 設定請求標頭
        self.session.headers.update({
            'User-Agent': settings_config.redmine.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # 建立輸出目錄
        self._create_directories()
    
    def _create_directories(self):
        """建立必要的目錄結構"""
        self.pdf_dir = self.output_dir / settings_config.paths.pdf_dir
        self.attachments_dir = self.output_dir / settings_config.paths.attachments_dir
        
        self.pdf_dir.mkdir(parents=True, exist_ok=True)
        self.attachments_dir.mkdir(parents=True, exist_ok=True)
        
        print("輸出目錄已建立:")
        print(f"  PDF: {self.pdf_dir}")
        print(f"  附件: {self.attachments_dir}")
    
    def crawl_issues(self, issue_numbers: List[str]) -> bool:
        """
        爬取多個 Redmine 單號
        
        Args:
            issue_numbers: Redmine 單號列表
            
        Returns:
            是否全部成功
        """
        if not issue_numbers:
            print("錯誤: 沒有提供單號列表")
            return False
            
        print(f"開始處理 {len(issue_numbers)} 個單號")
        success_count = 0
        
        for i, issue_num in enumerate(issue_numbers, 1):
            print(f"\n[{i}/{len(issue_numbers)}] 正在處理單號: {issue_num}")
            
            try:
                if self.crawl_single_issue(issue_num):
                    success_count += 1
                    print(f"✅ 單號 {issue_num} 處理完成")
                else:
                    print(f"❌ 單號 {issue_num} 處理失敗")
                    
                # 避免請求過於頻繁
                if i < len(issue_numbers):  # 最後一個不需要等待
                    time.sleep(settings_config.redmine.request_delay)
                    
            except Exception as e:
                print(f"❌ 處理單號 {issue_num} 時發生錯誤: {e}")
        
        print(f"\n處理完成: {success_count}/{len(issue_numbers)} 個單號成功")
        return success_count == len(issue_numbers)
    
    def crawl_single_issue(self, issue_number: str) -> bool:
        """
        爬取單一 Redmine 單號
        
        Args:
            issue_number: Redmine 單號
            
        Returns:
            是否成功
        """
        url = f"{self.base_url}/issues/{issue_number}"
        
        try:
            print(f"  正在獲取網頁內容: {url}")
            
            # 獲取網頁內容
            response = self.session.get(url)
            response.raise_for_status()
            
            # 檢查是否成功載入頁面
            if "登出" in response.text or "Logout" in response.text:
                # 已登入，繼續處理
                pass
            elif "Login" in response.text or "登入" in response.text:
                print("  ⚠️  可能需要登入，請檢查 session cookie")
                return False
            
            # 解析 HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 檢查是否找到問題頁面
            if soup.find('div', class_='error') or not soup.find('div', {'id': 'content'}):
                print(f"  ⚠️  找不到單號 {issue_number} 或無權限存取")
                return False
            
            # 下載附件
            attachment_count = self._download_attachments(soup, issue_number)
            print(f"  📎 下載了 {attachment_count} 個附件")
            
            # 生成 PDF
            if self._generate_pdf(response.content, issue_number):
                print("  📄 PDF 生成成功")
            else:
                print("  ❌ PDF 生成失敗")
                return False
            
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"  ❌ 網路請求失敗: {e}")
            return False
        except Exception as e:
            print(f"  ❌ 爬取單號 {issue_number} 失敗: {e}")
            return False
    
    def _download_attachments(self, soup: BeautifulSoup, issue_number: str) -> int:
        """
        下載附件檔案
        
        Args:
            soup: BeautifulSoup 物件
            issue_number: 單號
            
        Returns:
            下載的附件數量
        """
        attachment_links = soup.find_all('a', class_='icon icon-attachment')
        
        if not attachment_links:
            return 0
        
        issue_attachment_dir = self.attachments_dir / issue_number
        issue_attachment_dir.mkdir(exist_ok=True)
        
        download_count = 0
        
        for i, link in enumerate(attachment_links):
            try:
                attachment_url = urljoin(self.base_url, link.get('href'))
                
                # 獲取檔案名稱
                filename = link.text.strip()
                if not filename:
                    # 嘗試從 URL 中提取檔案名稱
                    parsed_url = urlparse(attachment_url)
                    filename = os.path.basename(parsed_url.path) or f"attachment_{i + 1}"
                
                # 清理檔案名稱中的非法字元
                filename = self._sanitize_filename(filename)
                
                print(f"    正在下載附件: {filename}")
                
                # 下載附件
                response = self.session.get(attachment_url)
                response.raise_for_status()
                
                # 儲存檔案
                file_path = issue_attachment_dir / filename
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                
                download_count += 1
                print(f"    ✅ 已下載: {filename} ({len(response.content)} bytes)")
                
            except Exception as e:
                print(f"    ❌ 下載附件失敗: {e}")
        
        return download_count
    
    def _generate_pdf(self, html_content: bytes, issue_number: str) -> bool:
        """
        將網頁內容轉換為 PDF
        
        Args:
            html_content: HTML 內容
            issue_number: 單號
            
        Returns:
            是否成功
        """
        try:
            # 生成 PDF 檔案路徑
            pdf_path = self.pdf_dir / f"issue_{issue_number}.pdf"
            
            # 處理 HTML 內容，修正相對路徑
            html_str = html_content.decode('utf-8', errors='ignore')
            
            # 修正相對路徑為絕對路徑
            html_str = html_str.replace('href="/', f'href="{self.base_url}/')
            html_str = html_str.replace('src="/', f'src="{self.base_url}/')
            
            # 設定 PDF 選項
            # use PDF options from settings; merge cookie
            options = settings_config.get_pdf_options()
            # pdfkit expects cookie as dict in options when using from_string
            # preserve previous behavior by adding a cookie entry
            options = {**options}
            options['cookie'] = [('_redmine_session', self.session.cookies.get('_redmine_session', ''))]
            
            print(f"    正在生成 PDF: {pdf_path.name}")
            
            # 設定 wkhtmltopdf 配置
            pdf_config = pdfkit.configuration(wkhtmltopdf=settings_config.pdf.wkhtmltopdf_path)
            
            # 轉換為 PDF
            pdfkit.from_string(html_str, str(pdf_path), options=options, configuration=pdf_config)
            
            # 檢查檔案是否成功生成
            if pdf_path.exists() and pdf_path.stat().st_size > 0:
                print(f"    ✅ PDF 已生成: {pdf_path} ({pdf_path.stat().st_size} bytes)")
                return True
            else:
                print("    ❌ PDF 檔案生成失敗或檔案大小為 0")
                return False
            
        except Exception as e:
            print(f"    ❌ 生成 PDF 失敗: {e}")
            return False
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        清理檔案名稱，移除非法字元
        
        Args:
            filename: 原始檔案名稱
            
        Returns:
            清理後的檔案名稱
        """
        # 移除或替換非法字元
        illegal_chars = r'[<>:"/\\|?*]'
        filename = re.sub(illegal_chars, '_', filename)
        
        # 移除開頭和結尾的空白和點
        filename = filename.strip(' .')
        
        # 如果檔案名稱為空，給予預設名稱
        if not filename:
            filename = "unnamed_file"
        
        return filename
    
    def test_connection(self) -> bool:
        """
        測試連線和認證狀態
        
        Returns:
            是否連線成功
        """
        try:
            print("正在測試連線...")
            
            # 顯示 cookie 資訊用於調試
            cookies = dict(self.session.cookies)
            if '_redmine_session' in cookies:
                cookie_value = cookies['_redmine_session']
                print(f"使用 Cookie: {cookie_value[:50]}...（已截短）")
            else:
                print("⚠️  警告：未設定 _redmine_session cookie")
            
            # 添加更多調試信息
            print(f"目標 URL: {self.base_url}")
            print(f"User-Agent: {self.session.headers.get('User-Agent', 'None')}")
            
            response = self.session.get(self.base_url, timeout=settings_config.redmine.timeout)
            response.raise_for_status()
            
            print(f"回應狀態碼: {response.status_code}")
            print(f"回應 URL: {response.url}")
            
            # 檢查回應內容
            response_text = response.text[:1000]  # 只看前1000字符
            
            # 檢查是否已登入 - 尋找登出連結或已登入的標識
            if "登出" in response.text or "Logout" in response.text or "Sign out" in response.text:
                print("✅ 連線成功，認證狀態正常（找到登出選項）")
                return True
            elif "my/account" in response.text.lower() or "我的帳戶" in response.text:
                print("✅ 連線成功，認證狀態正常（找到帳戶選項）")
                return True
            elif "Login" in response.text or "登入" in response.text or "Sign in" in response.text:
                print("❌ 需要登入，請檢查 session cookie")
                print("回應內容片段:")
                if "form" in response_text.lower():
                    print("  → 頁面包含登入表單")
                if "password" in response_text.lower():
                    print("  → 頁面要求密碼")
                return False
            else:
                print("⚠️  無法確定登入狀態，但沒有發現明顯的登入要求")
                # 打印更多信息以便調試
                print("回應內容片段（前500字符）:")
                print(response_text[:500])
                return True
                
        except Exception as e:
            print(f"❌ 連線測試失敗: {e}")
            return False
