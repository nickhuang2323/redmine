
from redmine_crawler import RedmineCrawler

def main():
    """主程式入口"""
    
    # ========== 請在此設定您的參數 ==========
    
    # 1. 設定你的 Redmine session cookie (必填)
    # 登入 Redmine 後，從瀏覽器開發者工具中複製 _redmine_session cookie 值
    session_cookie = "NWlZbkwzWGRvTkNJUVZmZWNyUURMZDUwUkF1TmNjV2Z0NnBtd3RGd3FJakw3QUR6MmJwcVBoR0dCU2lBbVo0by91YWdNODVwQmcwSGZwY3VCb2JlQmlCMjBTS2VXWjVqZ3J1SUpzcGQ4UG5lcTY5WWxLKzMxUjM1R04vZGdTKzVrcGtUTmplOG1tSE9jQ1U0eXNhZk9Edm9pdmxvZFhlelZhYnZqUExTb1ZxMlFmTVBJcTgzWFR5elR6RUIveFJXSXRpckw0bW1kQzdZL0FvZUtHSE4wd05RTHBDeGRBTkd0aSs0QkxRajFHbVNVN0FKcUJOSUZ0NldQKzNiRUJhZVJXYWFIV2FIVG00cWJ6R1JnR0tvdCt2aDBIdTNSbE03OTdydDlkSHlXVjd6Q3BRclJzNEFQYk9EMHpVZi9GMXRvbmpGUWpXdU9uaitPYmlwaGJWdG5NZTZmYStrSE1FUHhJenN4U1FOZUFhYVJ3R05OaVJ3b2NyTUJ3bUlOTHcrbnYxTHUvbk14bHFseGp2OEVoVFhhbUdISTl1RUFKZnp6SEJmaFVLTU1SRUV4Z21aYjFVZ2NaVS9XSmJsYlI5b1VrRWtlZ0FqVVoyUTNZYkRRVzE4RGVTYUFxR1E4T1JPdlZPSUFYaDY3bE0vVWh2LzViZ3EzWjN3M1JMZG94UmYtLXdsakkzUEJGaDZsak9LZDFDeFlyYXc9PQ%3D%3D--041e46e262bea8c192453edbbc3896d1db382897"
    
    # 2. 設定要爬取的單號列表 (必填)
    issue_numbers = [
        "31091"  # 請替換為實際的單號
    ]
    
    # 3. 設定輸出目錄 (可選，預設為 "redmine_output")
    output_directory = "redmine_output"
    
    # ========================================
    
    print("=== Redmine 爬蟲工具 ===")
    print("目標網站: https://redmine.etzone.net")
    print(f"輸出目錄: {output_directory}")
    print(f"單號數量: {len(issue_numbers)}")
    print()
    
    # 檢查必要參數
    if session_cookie == "your_redmine_session_cookie_here" or session_cookie == "請在此貼上您的新 session cookie":
        print("❌ 錯誤: 請先設定正確的 session_cookie")
        print("   1. 在瀏覽器中登入 Redmine")
        print("   2. 按 F12 開啟開發者工具")
        print("   3. 前往 Application > Cookies > https://redmine.etzone.net")
        print("   4. 找到名稱為 '_redmine_session' 的 Cookie")
        print("   5. 複製該 Cookie 的 '值' (Value) 欄位")
        print("   6. 貼上到 session_cookie 變數中")
        return
    
    if not issue_numbers or all(num == "12345" or num == "12346" or num == "12347" for num in issue_numbers):
        print("❌ 錯誤: 請設定正確的 issue_numbers")
        print("   請將 issue_numbers 列表中的範例單號替換為實際要爬取的單號")
        return
    
    # 建立爬蟲實例
    try:
        crawler = RedmineCrawler(
            session_cookie=session_cookie,
            output_dir=output_directory
        )
        
        # 測試連線
        if not crawler.test_connection():
            print("❌ 連線測試失敗，請檢查網路連線和 session cookie")
            return
        
        print("開始爬取...")
        print("=" * 50)
        
        # 執行爬取
        print("issue_numbers=", issue_numbers)
        success = crawler.crawl_issues(issue_numbers)
        
        print("=" * 50)
        if success:
            print("🎉 所有單號處理完成！")
            print(f"   PDF 檔案位置: {crawler.pdf_dir}")
            print(f"   附件檔案位置: {crawler.attachments_dir}")
        else:
            print("⚠️  部分單號處理失敗，請檢查上方的錯誤訊息")
            
    except Exception as e:
        print(f"❌ 程式執行失敗: {e}")
        print("請檢查:")
        print("1. 是否已安裝所有必要的套件 (pip install -r requirements.txt)")
        print("2. 是否已安裝 wkhtmltopdf")
        print("3. session_cookie 是否正確")


def example_single_issue():
    """單一單號爬取範例"""
    session_cookie = "your_redmine_session_cookie_here"
    issue_number = "12345"
    
    crawler = RedmineCrawler(session_cookie=session_cookie)
    
    if crawler.test_connection():
        success = crawler.crawl_issues([issue_number])
        if success:
            print(f"單號 {issue_number} 爬取完成！")


def example_batch_crawl():
    """批次爬取範例"""
    session_cookie = "your_redmine_session_cookie_here"
    
    # 從 10001 到 10010
    issue_numbers = [str(i) for i in range(10001, 10011)]
    
    crawler = RedmineCrawler(
        session_cookie=session_cookie,
        output_dir="batch_output"
    )
    
    if crawler.test_connection():
        success = crawler.crawl_issues(issue_numbers)
        print(f"批次爬取完成，成功率: {success}")


if __name__ == "__main__":
    main()
