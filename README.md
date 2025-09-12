# Redmine 爬蟲工具 v2.0

一個採用現代分層架構和設計模式的 Redmine Issue 爬蟲工具，可以自動下載 Issue 內容、附件並生成 PDF 報告。

## 🌟 主要特色

- 🏗️ **分層架構**：採用 DDD (領域驅動設計) 三層架構
- 🎨 **設計模式**：實現多種設計模式 (Singleton, Factory, Repository, Observer)
- ⚡ **非同步處理**：使用 aiohttp 提升爬取效能
- 📄 **智慧 PDF 命名**：根據 HTML h2/h3 標籤自動命名 PDF
- 🔧 **統一配置管理**：支援環境變數和 JSON 配置檔案
- 📊 **事件驅動**：即時進度追蹤和日誌記錄
- 🛡️ **錯誤處理**：完善的例外處理和重試機制

## 📋 系統需求

### 必要環境
- **Python**: 3.7 或更高版本
- **作業系統**: Windows 10/11, macOS, Linux
- **網路**: 可存取目標 Redmine 服務器

### 外部工具
- **wkhtmltopdf**: PDF 生成工具
  - Windows: [下載連結](https://wkhtmltopdf.org/downloads.html)
  - macOS: `brew install wkhtmltopdf`
  - Ubuntu/Debian: `sudo apt-get install wkhtmltopdf`
  - CentOS/RHEL: `sudo yum install wkhtmltopdf`

## 🚀 快速開始

### 統一啟動方式 (推薦)

**最簡單的開始方式：**
```bash
# Windows 用戶
start.bat
```

`start.bat` 提供完整的功能選單：
1. **安裝檢查** - 自動安裝和檢查所有依賴套件
2. **完整功能** - 進階用戶的完整爬蟲功能
3. **測試功能** - PDF 檔名測試
4. **說明文件** - 查看架構說明

### 手動安裝 (可選)

如果您偏好手動控制安裝過程：

#### 步驟 1: 安裝 Python 依賴

```bash
# 安裝套件
pip install -r requirements.txt
```

#### 步驟 2: 安裝 wkhtmltopdf

**Windows:**
1. 從 [官方網站](https://wkhtmltopdf.org/downloads.html) 下載 wkhtmltopdf
2. 安裝到預設位置 `C:\Program Files\wkhtmltopdf\`
3. 或自訂安裝路徑並在配置中指定

**macOS:**
```bash
brew install wkhtmltopdf
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install wkhtmltopdf
```

## 📖 使用指南

### 獲取 Session Cookie

在使用爬蟲之前，需要從瀏覽器獲取 Redmine 的 session cookie：

1. 在瀏覽器中登入 Redmine
2. 開啟開發者工具 (F12)
3. 前往 Network 或 Application 標籤
4. 找到 `_redmine_session` cookie 值
5. 複製 cookie 值用於爬蟲設定

### 執行方式

#### 1. 統一啟動入口 (推薦)
```bash
# Windows
start.bat
```
提供多種選項：
- 安裝/檢查相依性
- 快速啟動爬蟲 (適合新手)
- 完整功能爬蟲 (進階設定)
- PDF 檔名測試
- 開啟架構說明

**選項說明：**
- **選項 1**: 安裝和檢查系統相依性
- **選項 2**: 快速啟動 - 互動式介面，逐步引導設定
- **選項 3**: 完整功能 - 支援進階設定和批次處理
- **選項 4**: PDF 檔名測試
- **選項 5**: 查看架構文件

#### 2. 直接執行 (進階用戶)
如果您已經熟悉系統，也可以直接執行：
```bash
python main.py
```

## 🔧 配置選項

### 環境變數設定
```bash
# Redmine 設定
export REDMINE_BASE_URL="https://your-redmine.com"
export REDMINE_TIMEOUT="30"
export REDMINE_REQUEST_DELAY="1.0"

# 路徑設定
export OUTPUT_DIR="redmine_output"
export PDF_DIR="pdfs"
export ATTACHMENTS_DIR="attachments"

# PDF 設定
export PDF_PAGE_SIZE="A4"
export WKHTMLTOPDF_PATH="/usr/local/bin/wkhtmltopdf"
```

### JSON 配置檔案
詳細的配置選項請參考 `config_example.json`

## 📁 輸出結構

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

## 🧪 測試

### 執行架構測試
```bash
python example_usage.py
```

### 執行 PDF 命名測試
```bash
python test_pdf_naming.py
```

### 單元測試 (如果已設定)
```bash
pytest tests/
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

### 日誌檢查

程式執行時會產生詳細的日誌資訊，包括：
- 網路請求狀態
- 檔案下載進度
- 錯誤訊息和堆疊追蹤
- 效能統計資料

## 🏗️ 架構說明

此專案採用現代軟體架構設計，詳細說明請參考 [ARCHITECTURE.md](ARCHITECTURE.md)

### 主要架構特色
- **分層設計**: Application → Domain → Infrastructure
- **設計模式**: 實現 6 種設計模式
- **依賴注入**: 鬆耦合的組件設計
- **事件驅動**: 即時進度追蹤
- **配置管理**: 統一的設定系統

## 🤝 貢獻指南

1. Fork 此專案
2. 建立功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交變更 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

## 📄 授權條款

此專案採用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 檔案

## 📞 支援與回饋

- 🐛 **問題回報**: [GitHub Issues](https://github.com/your-repo/issues)
- 💡 **功能建議**: [GitHub Discussions](https://github.com/your-repo/discussions)
- 📧 **聯絡我們**: your-email@example.com

## 📈 版本紀錄

### v2.0.0 (2024-12-XX)
- 🎉 全新的分層架構設計
- ✨ 實現多種設計模式
- ⚡ 非同步爬蟲處理
- 📄 智慧 PDF 命名
- 🔧 統一配置管理
- 📊 事件驅動架構

### v1.x (歷史版本)
- 基礎爬蟲功能
- 簡單的 PDF 生成
- 單執行緒處理

---

**快速開始**: 執行 `start.bat` 選擇您需要的功能！
