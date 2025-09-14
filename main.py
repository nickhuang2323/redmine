
"""
新版 Redmine 爬蟲主程式
使用分層架構和設計模式重新實現
"""
import asyncio
import sys
from pathlib import Path
import os

# 確保能找到 src 模組
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.infrastructure.factories.crawler_factory import crawler_factory
from src.infrastructure.events.event_system import (
    event_bus,
    ConsoleEventHandler,
    LoggingEventHandler,
    StatisticsEventHandler,
)
from src.infrastructure.config.settings import config
from src.domain.value_objects.common import CrawlRequest, FilePath


async def main():
    """主程式入口"""
    try:
        print("🚀 新版 Redmine 爬蟲啟動")
        print("=" * 50)

        # 設定事件處理器
        console_handler = ConsoleEventHandler()
        logging_handler = LoggingEventHandler()
        stats_handler = StatisticsEventHandler()

        event_bus.subscribe_all(console_handler)
        event_bus.subscribe_all(logging_handler)
        event_bus.subscribe_all(stats_handler)

        # 檢查配置
        validation_errors = config.validate_configuration()
        if validation_errors:
            print("❌ 配置驗證失敗:")
            for error in validation_errors:
                print(f"  - {error}")
            return False

        # 取得 session cookie：優先使用配置中的值，若未配置則提示並要求輸入
        session_cookie = config.redmine.session_cookie if getattr(config, 'redmine', None) and getattr(config.redmine, 'session_cookie', None) else None
        if session_cookie:
            # 直接印出從設定讀取到的完整 session cookie
            print(f"🔒 已從配置讀取 Redmine session cookie: {session_cookie}")
        else:
            print("⚠️ 未在配置中找到 Redmine session cookie。建議可透過環境變數 REDMINE_SESSION_COOKIE 或設定檔設定以避免每次輸入。")
            session_cookie = input("請輸入 Redmine session cookie (可留空): ").strip()

        # 取得要爬取的單號
        issue_numbers_input = input("請輸入要爬取的單號 (用逗號分隔): ").strip()
        if not issue_numbers_input:
            print("❌ 未提供單號")
            return False

        issue_numbers = [
            num.strip() for num in issue_numbers_input.split(",") if num.strip()
        ]

        # 建立爬蟲服務
        crawler_service = crawler_factory.create_crawler_service(session_cookie)

        # 設定事件處理
        async def event_publisher(event):
            await event_bus.publish(event)

        crawler_service._crawler_service._publish_event = event_publisher

        # 建立爬取請求
        crawl_request = CrawlRequest(
            issue_numbers=issue_numbers,
            output_directory=FilePath(config.paths.output_dir),
            session_cookie=session_cookie,
        )

        print(f"📋 準備爬取 {len(issue_numbers)} 個單號")
        print(f"📂 輸出目錄: {config.paths.output_dir}")
        print("=" * 50)

        # 執行爬取
        result = await crawler_service.crawl_issues(crawl_request)

        print("=" * 50)
        print("📊 爬取結果:")
        print(f"  ✅ 成功: {result.successful_issues}/{result.total_issues}")
        print(f"  ❌ 失敗: {result.failed_issues}")
        print(f"  📎 附件: {result.attachments_downloaded} 個")
        print(f"  📄 PDF: {result.pdfs_generated} 個")
        print(f"  📈 成功率: {result.success_rate:.1%}")

        # 顯示統計資料
        stats = stats_handler.get_statistics()
        print("\n📈 詳細統計:")
        for key, value in stats.items():
            print(f"  {key}: {value}")

        return result.is_fully_successful

    except KeyboardInterrupt:
        print("\n\n⚠️  用戶中斷操作")
        return False
    except Exception as e:
        print(f"\n❌ 程式執行錯誤: {e}")
        import traceback

        traceback.print_exc()
        return False


def sync_main():
    """同步主程式包裝器"""
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ 程式啟動失敗: {e}")
        sys.exit(1)


if __name__ == "__main__":
    sync_main()
