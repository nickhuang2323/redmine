# 建置 `launcher.exe`（說明）

這個專案包含一個 Python 啟動器 `launcher.py`，功能與原本的 `start.bat` 相同。你可以使用 PyInstaller 把它包成單一的 exe，方便在 Windows 上直接執行。

簡單步驟：

1. 打開 PowerShell（或 cmd）並切換到專案根目錄。
2. 執行 `build_launcher_exe.bat`（需要能安裝 Python 套件）：

```powershell
.\build_launcher_exe.bat
```

3. 完成後在 `dist\launcher.exe` 可找到生成的執行檔。

備註：
- 若你希望讓 exe 包含其他資源或非 Python 檔案，請參考 PyInstaller 的 `--add-data` 選項。
- 生成的 exe 仍會以內嵌的 Python 進程執行專案內的其他 .py 檔案；若你想把整個專案打包成一個單檔，需額外設定和測試。

注意：自動包含 `requirements.txt`

在此專案的打包腳本 `build_launcher_exe.bat` 中，預設會把 `requirements.txt` 一併當作資料檔加入到資料型的 exe（例如 `launcher_with_data.exe` 與 `launcher_full.exe`）。這樣做的理由：
- 如果在目標環境需要檢視或重建相依時，內含的 `requirements.txt` 能提供套件版本資訊。
- 對於某些透過路徑讀取或外部工具需要檔案的情況，將 `requirements.txt` 內建可以避免找不到檔案。

如果你不想把 `requirements.txt` 包入 exe，可以編輯 `build_launcher_exe.bat`，移除 `--add-data "requirements.txt;."` 參數，然後重新執行建置腳本。


# 功能上差別
launcher.exe
內容：只把啟動器與被 PyInstaller 自動分析需要的模組打包進 exe（通常包含許多第三方套件與 import 到的模組）。
優點：檔案較小、打包時間較短。
風險/限制：若你的程式在執行時以「相對路徑直接讀取 src 下的檔案或以 subprocess 執行 repo 內的 .py 檔」，在沒有同目錄的原始 src 時可能會發生找不到檔案或模組的錯誤（因為某些資源不是以 module import 的方式被 PyInstaller 自動捕捉）。
launcher_with_data.exe
內容：除了基本內容外，額外把整個 src 資料夾與 config_example.json 當作「資料檔案」加入 exe（PyInstaller 會把它們打包成內嵌資源，運行時會解壓到臨時目錄供程式使用）。
優點：更加「自包含」且對於以路徑載入檔案或需要原始檔案的程式流程更穩定（例如程式以相對路徑讀取設定、模板或直接執行其它 .py）。
缺點：檔案較大（因為包含整個 src），打包時間較長。