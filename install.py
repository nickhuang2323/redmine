
"""
Redmine 爬蟲工具安裝腳本
此腳本會自動檢查和安裝必要的相依性套件
"""
import subprocess
import sys
import os
from pathlib import Path

def check_python_version():
    """檢查 Python 版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ 錯誤: 需要 Python 3.7 或更高版本")
        print(f"   目前版本: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python 版本: {version.major}.{version.minor}.{version.micro}")
    return True

def install_packages():
    """安裝 Python 套件"""
    print("正在安裝 Python 套件...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ Python 套件安裝完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Python 套件安裝失敗: {e}")
        return False

def check_wkhtmltopdf():
    """檢查 wkhtmltopdf 是否已安裝"""
    try:
        result = subprocess.run(
            ["wkhtmltopdf", "--version"], 
            capture_output=True, 
            text=True, 
            check=True
        )
        print("✅ wkhtmltopdf 已安裝")
        print(f"   版本: {result.stdout.strip().split()[1]}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ wkhtmltopdf 未安裝")
        print("   請從以下網址下載並安裝:")
        print("   https://wkhtmltopdf.org/downloads.html")
        print("   安裝後請重新執行此腳本")
        return False

def create_new_config_example():
    """建立新版配置範例檔案"""
    config_example = """
# 新版 Redmine 爬蟲配置範例
# 使用 JSON 格式配置或環境變數

{
  "redmine": {
    "base_url": "https://redmine.etzone.net",
    "request_delay": 1.0,
    "timeout": 30,
    "max_retries": 3
  },
  "paths": {
    "output_dir": "redmine_output",
    "pdf_dir": "pdfs",
    "attachments_dir": "attachments"
  },
  "pdf": {
    "page_size": "A4",
    "wkhtmltopdf_path": "C:\\\\Program Files\\\\wkhtmltopdf\\\\bin\\\\wkhtmltopdf.exe"
  }
}
"""
    
    config_file = Path("config_example.json")
    if not config_file.exists():
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(config_example)
        print("✅ 已建立 config_example.json 範例配置檔案")
    
def main():
    """主要安裝流程"""
    print("=== Redmine 爬蟲工具安裝程式 ===")
    print()
    
    # 檢查 Python 版本
    if not check_python_version():
        return False
    
    # 檢查 requirements.txt 是否存在
    if not Path("requirements.txt").exists():
        print("❌ 錯誤: 找不到 requirements.txt 檔案")
        return False
    
    # 安裝 Python 套件
    if not install_packages():
        return False
    
    # 檢查 wkhtmltopdf
    wkhtmltopdf_ok = check_wkhtmltopdf()
    
    # 建立範例配置
    create_new_config_example()
    
    print()
    print("=== 安裝結果 ===")
    
    if wkhtmltopdf_ok:
        print("🎉 安裝完成！可以開始使用新版爬蟲工具")
        print()
        print("使用步驟:")
        print("1. 完整功能: python main.py")
        print("2. 配置設定: 編輯 config_example.json 並重命名為 config.json")
    else:
        print("⚠️  安裝未完成，請先安裝 wkhtmltopdf")
    
    return wkhtmltopdf_ok

if __name__ == "__main__":
    success = main()
    
    if not success:
        input("按 Enter 鍵結束...")
        sys.exit(1)
