@echo off

chcp 65001

REM 新版 Redmine 爬蟲工具批次執行檔

echo ================================================
echo        新版 Redmine 爬蟲工具啟動器
echo ================================================
echo.

REM 檢查 Python 是否已安裝
python --version >nul 2>&1
if errorlevel 1 (
    echo 錯誤: 找不到 Python
    echo 請確認已安裝 Python 3.7 或更高版本
    echo 下載網址: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 顯示選項
echo 請選擇操作:
echo.
echo 1. 安裝/檢查相依性
echo 2. Git History Issue 編號提取
echo 3. 將 Redmine 單匯出成 PDF
echo.

set /p choice="請輸入選項 (1-3): "

if "%choice%"=="1" goto install
if "%choice%"=="2" goto githistory
if "%choice%"=="3" goto fullversion
goto invalid

:install
echo.
echo 正在執行安裝程序...
python install.py
goto end

:fullversion
echo.
echo 啟動 Redmine單匯出成 PDF 流程...
python main.py
goto end

:pdftest
echo.
echo 測試 PDF 檔名功能...
python test_pdf_naming.py
goto end

:githistory
echo.
echo 啟動 Git History Issue 編號提取工具...
echo 只回傳符合 refs #編號 格式的單號字串
echo.
python git_issue_extractor_silent.py
goto end

:invalid
echo.
echo 無效的選項，請重新執行
pause
exit /b 1

:end
echo.
pause
