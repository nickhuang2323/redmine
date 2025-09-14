## 容器化使用說明

此專案包含 `Dockerfile`，會建立一個基於 Python 3.12 的容器，並在映像建立期間安裝 Python 相依套件與 wkhtmltopdf，提供一個 entrypoint 來執行與 `start.bat` 相同的動作。

建立映像（在專案根目錄執行）：

```bash
# 可在 build 時以 build-arg 指定容器內預期的 wkhtmltopdf 路徑 (預設 /usr/local/bin/wkhtmltopdf)
docker build --build-arg WKHTMLTOPDF_PATH=/usr/local/bin/wkhtmltopdf -t redmine-crawler:latest .
```

互動方式執行容器並執行安裝步驟：

```bash
docker run --rm -it redmine-crawler:latest install
```

執行完整爬蟲：

```bash
docker run --rm -it redmine-crawler:latest full
```

注意事項
- Dockerfile 使用針對 Ubuntu Jammy 的 wkhtmltopdf prebuilt .deb（版本 0.12.6-1）。如需其他版本或發行版，請調整下載 URL。
- 若在 Windows 上執行 Docker，建議使用 Docker Desktop 或 WSL2 後端以獲得最佳相容性。
- Dockerfile 會在映像建立時安裝 `requirements.txt`，如果你頻繁修改 Python 相依套件，建議改為在容器啟動時安裝或在開發模式掛載原始碼並在容器內運行 `pip install -r requirements.txt`，以加速開發迭代。

常見的 build 問題與排除（針對 wkhtmltopdf 下載 / 安裝失敗）

- 問題症狀：在執行 `docker build` 時卡在類似下面的步驟，並出現 wget 或 dpkg 的錯誤：

  => ERROR [3/8] RUN wget -O /tmp/wkhtml.deb "https://github.com/wkhtmltopdf/..." ...

  排查建議：
  1) 檢查主機能否存取該 URL（網路、防火牆或 GitHub rate limit 可能導致下載失敗）：

	  # PowerShell 範例
	  Invoke-WebRequest -Uri "https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.jammy_amd64.deb" -OutFile wkhtml.deb

	  如果在主機也無法下載，請檢查網路或改用可存取的鏡像（或先手動下載並將檔案放到 build context）。

  2) 若 dpkg 安裝失敗（缺少相依套件），可以在 Dockerfile 中加入嘗試修復的步驟（目前 Dockerfile 會在 dpkg 失敗時嘗試 `apt-get -f install -y`）：

	  docker build --no-cache -t redmine-crawler:latest .

	  如果仍失敗，考慮改用 Ubuntu Jammy 基底（`FROM ubuntu:22.04`）以確保 .deb 的相容性，或使用發行版官方套件。

  3) 快速替代方案：將 wkhtmltopdf 二進位放在本機並在 build 時 COPY 到映像中。範例：

	  # 將事先下載的 wkhtmltox_0.12.6-1.jammy_amd64.deb 放在專案根目錄
	  docker build -t redmine-crawler:latest .

	  Dockerfile 補充片段（示意）：

	  # ...
	  COPY wkhtmltox_0.12.6-1.jammy_amd64.deb /tmp/wkhtml.deb
	  RUN dpkg -i /tmp/wkhtml.deb || (apt-get -f install -y && dpkg -i /tmp/wkhtml.deb)

	4) 最後手段：在容器啟動時不安裝 wkhtmltopdf，而改以 volume 掛載主機上已安裝的 wkhtmltopdf 執行檔；或使用另一個已包含 wkhtmltopdf 的映像作為 base image。

掛載與環境變數範例

若在主機已安裝 wkhtmltopdf，建議把主機執行檔直接掛載到容器的 `/usr/local/bin/wkhtmltopdf`，並透過環境變數告知程式使用該路徑：

```bash
# 假設主機上的可執行檔為 /usr/local/bin/wkhtmltopdf
docker run --rm -it -v /usr/local/bin/wkhtmltopdf:/usr/local/bin/wkhtmltopdf -e WKHTMLTOPDF_PATH=/usr/local/bin/wkhtmltopdf redmine-crawler:latest full
```

如果在 Windows 上使用 Docker Desktop 並希望掛載 Windows 的 wkhtmltopdf，可先把可執行檔複製到一個資料夾（例如 C:\wkhtml\wkhtmltopdf.exe），然後以 WSL2 相容路徑或透過 Docker Desktop 的檔案分享功能掛載到容器：

```powershell
# Windows PowerShell 範例：假設你已將 wkhtmltopdf.exe 複製到 C:\wkhtml\wkhtmltopdf.exe
docker run --rm -it -v C:\wkhtml\wkhtmltopdf.exe:/usr/local/bin/wkhtmltopdf -e WKHTMLTOPDF_PATH=/usr/local/bin/wkhtmltopdf redmine-crawler:latest full
```

檢查並自動下載（PowerShell 範例）

若你在 Windows 上，下面的 PowerShell 片段會先檢查專案根是否有 `wkhtmltox_0.12.6-1.jammy_amd64.deb`，若沒有則自動下載：

```powershell
# 在專案根執行
if (-Not (Test-Path -Path .\wkhtmltox_0.12.6-1.jammy_amd64.deb)) {
	Write-Host "wkhtml .deb not found, downloading..."
	Invoke-WebRequest -Uri "https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.jammy_amd64.deb" -OutFile .\wkhtmltox_0.12.6-1.jammy_amd64.deb
} else {
	Write-Host "wkhtml .deb already present"
}

# 或使用 repo 中的 helper
.
# 你也可以使用 start-docker.bat prepare，它會做相同的檢查並嘗試下載
```

若要在 Windows PowerShell 上重試 build，範例指令：

```powershell
# 刪除舊映像然後重新建置
docker image rm redmine-crawler:latest -f; docker build -t redmine-crawler:latest .
```

如果你想讓我直接把 Dockerfile 改為使用 `ubuntu:22.04` 基底或把 wkhtmltopdf 改成 COPY 本地檔案的流程，我可以替你套用修改並嘗試再次 build（請告訴我要採用哪一種策略）。
