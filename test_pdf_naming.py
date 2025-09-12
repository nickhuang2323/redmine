
"""詳細測試 PDF 檔名功能"""
import asyncio
import sys
from pathlib import Path

# 確保能找到 src 模組
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.infrastructure.factories.crawler_factory import crawler_factory
from src.domain.value_objects.common import FilePath
from src.domain.entities.issue import IssueId


async def test_pdf_naming():
    """測試 PDF 檔名功能"""
    print("🧪 測試 PDF 檔名功能...")
    
    try:
        # 建立爬蟲服務
        crawler_service = crawler_factory.create_crawler_service("")
        
        # 建立 Issue 儲存庫來測試標題提取
        issue_repo = crawler_factory.create_issue_repository("")
        
        # 測試提取 Issue 資訊
        test_issue_id = IssueId("31091")
        
        async with issue_repo._http_client as client:
            html_content = await client.get_issue_html(test_issue_id)
            if html_content:
                issue = issue_repo._parse_issue_from_html(test_issue_id, html_content)
                
                print(f"📋 Issue ID: {issue.id.value}")
                print(f"📝 提取的標題: {issue.title}")
                print(f"📄 檔名將會是: {test_issue_id.value}_{issue.title}.pdf")
                
                # 檢查檔名安全性
                from src.domain.services.crawler_service import IssueCrawlerService
                service = IssueCrawlerService(None, None, None)
                safe_title = service._sanitize_filename(issue.title)
                print(f"🛡️  安全檔名: {test_issue_id.value}_{safe_title}.pdf")
                
                return True
            else:
                print("❌ 無法取得 HTML 內容")
                return False
                
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        return False


def main():
    """主函式"""
    print("🎯 PDF 檔名功能測試")
    print("=" * 40)
    
    success = asyncio.run(test_pdf_naming())
    
    if success:
        print("\n✅ PDF 檔名功能測試通過！")
    else:
        print("\n⚠️  測試未完全成功")


if __name__ == "__main__":
    main()
