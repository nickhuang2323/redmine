# Redmine 爬蟲工具 v2.0

一個採用現代分層架構和設計模式的 Redmine Issue 爬蟲工具，可以自動下載 Issue 內容、附件並生成 PDF 報告，並將 PDF 報告匯入至 Google NotebookLM 進行相關文件內容查詢。

## 🚀 快速開始

### 一、建置環境

1. 下載 Python 3.13.7 https://www.python.org/downloads/release/python-3137/

2. 確認安裝的路徑，C:\Users\<user_name>\AppData\Local\Programs\Python\Python313

3. 建立 .venv python 開發環境

    3-1. 建立一個資料夾 py-project

    3-2. 用 command 進入資料夾 cd py-project

    3-3. 執行 C:\Users\<user_name>\AppData\Local\Programs\Python\Python313\python.exe -m venv .venv

    3-4. 將該專案移至 py-project 資料夾中

    3-5.  wkhtmltopdf，執行專案中的 redmine/wkhtmltox-0.12.6-1.msvc2015-win64.exe

    3-6. 用 command 執行 ./start.bat

    3-7. 執行 1，進行相關套件安裝


### 二、取得檔案 Git History 相關的 Redmine 單號

1. 用 command 執行 ./start.bat
2. 執行 2，從 Git History Issue 編號提取
3. 設定 MoneyIn 專案根目錄位置，ex: D:\MoneyIn
4. 設定 要擷取哪個檔案的 Git History，ex: D:\MoneyIn\...\XXController.cs
5. 複製單號 ex:12345,67890，先找記事本貼著

### 三、將相關單號的網站內容匯出成 PDF

1. 獲取 Session Cookie

    在使用爬蟲之前，需要從瀏覽器獲取 Redmine 的 session cookie：
    * 在瀏覽器中登入 Redmine
    * 開啟開發者工具 (F12)
    * 前往 Network 或 Application 標籤
    * 找到 `_redmine_session` cookie 值
    * 複製 cookie 值用於爬蟲設定

2. 設定 REDMINE_SESSION_COOKIE 環境變數

    * 環境變數設定

      * Linux / macOS

        ```bash
        # Redmine 設定
        export REDMINE_SESSION_COOKIE="_redmine_session"
        ```

      * Command
          ```
          set MY_ENV=test

          # 永久設定
          setx MY_ENV "test"

          # 查看
          echo %PATH%
          ```


      * PowerShell

        ```shell
        $env:REDMINE_SESSION_COOKIE="test111111"


        # 永久設定
        setx REDMINE_SESSION_COOKIE "test"

        # 查看
        echo $env:REDMINE_SESSION_COOKIE
        ```

3. 用 command 執行 ./start.bat，執行 3 匯出 PDF 流程

4. 輸入剛複製的爬取的單號，多個單號請用逗號分隔 (例如: 12345,67890)

5. 檔案會輸出至 `redmine_output/` 目錄下

    ```
    redmine_output/
    ├── pdfs/                          # PDF 檔案
    │   ├── 12345_Issue標題.pdf
    │   └── 67890_另一個Issue.pdf
    └── attachments/                   # 附件檔案
        ├── 12345/                     # 按 Issue 編號分組
        │   ├── attachment1.jpg
        │   └── document.pdf
        └── 67890/
            └── screenshot.png
    ```


## 🔍 故障排除

### 常見問題

**1. Python 套件安裝失敗**

```bash
# 升級 pip
pip install --upgrade pip

# 使用國內鏡像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

**2. wkhtmltopdf 找不到**
- 確認 wkhtmltopdf 已正確安裝
- 檢查配置檔案中的路徑設定
- Windows 用戶確認是否安裝在 `C:\Program Files\wkhtmltopdf\`

**3. Cookie 過期**
- 重新登入 Redmine 獲取新的 session cookie
- 檢查 cookie 格式是否正確

**4. 網路連線問題**
- 檢查防火牆設定
- 確認可以存取 Redmine 服務器
- 調整 `request_delay` 和 `timeout` 設定

**5. PDF 生成失敗**
- 檢查 wkhtmltopdf 是否正常運作：`wkhtmltopdf --version`
- 確認有足夠的磁碟空間
- 檢查輸出目錄權限
