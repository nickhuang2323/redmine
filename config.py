
import os

class Config:
    """配置設定"""
    
    # Redmine 設定
    REDMINE_BASE_URL = "https://redmine.etzone.net"
    
    # 輸出目錄設定
    OUTPUT_DIR = "redmine_output"
    PDF_DIR = "pdfs"
    ATTACHMENTS_DIR = "attachments"
    
    # 請求設定
    REQUEST_DELAY = 1  # 請求間隔秒數
    TIMEOUT = 30  # 請求超時時間
    
    # PDF 生成設定
    PDF_OPTIONS = {
        'page-size': 'A4',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'encoding': "UTF-8",
        'no-outline': None,
        'enable-local-file-access': None,
        'javascript-delay': 1000
    }
    
    # wkhtmltopdf 執行檔路徑
    WKHTMLTOPDF_PATH = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
    
    # 使用者代理字串
    USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
