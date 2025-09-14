
"""
Redmine 爬蟲工具安裝腳本（已重構為 Windows 友善）

功能重點：
- Python 版本檢查
- 套件安裝（pip，支援 --prefer-binary，並在需要時給出 conda 建議）
- wkhtmltopdf 偵測（PATH 與常見安裝路徑）
- 建立 config 範例檔案
- 命令列介面（非互動模式支援 --yes）

此檔案主要改善 Windows 下的相容性與錯誤處理，並保留原本使用者提示。
"""

import argparse
import ctypes
import os
import subprocess
import sys
import tempfile
import urllib.request
import webbrowser
from pathlib import Path
import shutil
import re
import platform


def is_windows() -> bool:
    return os.name == 'nt'


def is_admin() -> bool:
    """在 Windows 上檢查是否為管理員（在非 Windows 平台回傳 False）。"""
    if not is_windows():
        return False
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def check_python_version(min_major=3, min_minor=7) -> bool:
    """檢查 Python 版本，回傳 True 表示版本符合需求。"""
    version = sys.version_info
    if version.major < min_major or (version.major == min_major and version.minor < min_minor):
        print("❌ 錯誤: 需要 Python {0}.{1} 或更高版本".format(min_major, min_minor))
        print(f"   目前版本: {version.major}.{version.minor}.{version.micro}")
        print("   請至 https://www.python.org/downloads/ 下載並安裝最新版本，或使用 Anaconda/Miniconda。")
        return False

    print(f"✅ Python 版本: {version.major}.{version.minor}.{version.micro}")
    return True


def open_python_downloads_page():
    url = "https://www.python.org/downloads/"
    print(f"開啟下載頁面：{url}")
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"無法自動開啟瀏覽器，請手動造訪: {url} (錯誤: {e})")


def download_and_run_installer(url: str) -> bool:
    """下載 Windows 安裝程式並以安靜模式執行（需要管理員權限）。

    注意：自動安裝會修改系統環境。若非必要，建議手動安裝。
    """
    print(f"開始下載安裝程式：{url}")
    try:
        tmp_dir = tempfile.gettempdir()
        filename = os.path.join(tmp_dir, os.path.basename(url))
        with urllib.request.urlopen(url) as response, open(filename, 'wb') as out_file:
            out_file.write(response.read())
        print(f"下載完成: {filename}")
    except Exception as e:
        print(f"下載失敗：{e}")
        return False

    if not is_windows():
        print("自動安裝僅支援 Windows，請手動安裝 Python")
        return False

    if not is_admin():
        print("警告：執行安裝需要管理員權限，請以系統管理員身分重新執行此腳本或手動執行下載之安裝程式。")
        print(f"已下載安裝檔: {filename}")
        return False

    cmd = [filename, '/quiet', 'InstallAllUsers=1', 'PrependPath=1']
    print(f"執行安裝命令: {cmd}")
    try:
        subprocess.check_call(cmd)
        print("✅ 安裝程式執行完成，請重新啟動終端機以套用 PATH。")
        return True
    except subprocess.CalledProcessError as e:
        print(f"執行安裝失敗: {e}")
        return False


def run_subprocess_stream(cmd, env=None):
    """以 streaming 模式執行 subprocess，直接把 stdout/stderr 寫到目前終端機（支援 Windows）。"""
    # 使用 creationflags 避免在 Windows 上開新視窗
    creationflags = 0
    if is_windows():
        # CREATE_NO_WINDOW = 0x08000000
        creationflags = 0x08000000

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env, creationflags=creationflags)
    try:
        for line in proc.stdout:
            try:
                sys.stdout.write(line.decode('utf-8', errors='replace'))
            except Exception:
                sys.stdout.write(str(line))
        returncode = proc.wait()
        if returncode != 0:
            raise subprocess.CalledProcessError(returncode, cmd)
        return True
    finally:
        try:
            if proc.stdout:
                proc.stdout.close()
        except Exception:
            pass


def install_packages(requirements_file: str = 'requirements.txt', prefer_binary: bool = True) -> bool:
    """安裝 Python 套件，會嘗試升級 pip/setuptools/wheel，並以 streaming 顯示安裝日誌。"""
    print("正在安裝 Python 套件...")
    env = os.environ.copy()
    env.setdefault("PYTHONIOENCODING", "utf-8")
    env.setdefault("PYTHONUTF8", "1")

    # 升級 pip 工具
    try:
        print("先升級 pip / setuptools / wheel...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"], env=env)
    except Exception as e:
        print(f"升級 pip 等工具時發生錯誤（可忽略但可能影響編譯成功）: {e}")

    # 如果 requirements 包含 aiohttp，先嘗試安裝一個已知有 Windows wheel 的新版以避免本機編譯問題
    preferred_aio_version = "3.12.15"
    aio_installed = False
    try:
        with open(requirements_file, 'r', encoding='utf-8') as f:
            req_lines = f.readlines()
    except Exception:
        req_lines = []

    has_aio = any(re.match(r"\s*aiohttp\b", ln, re.IGNORECASE) for ln in req_lines)
    req_to_install = requirements_file
    if has_aio:
        print(f"偵測到 requirements 檔包含 aiohttp，先嘗試安裝 aiohttp=={preferred_aio_version}（若有對應 Windows wheel）...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", f"aiohttp=={preferred_aio_version}"], env=env)
            aio_installed = True
            print(f"✅ 已安裝 aiohttp=={preferred_aio_version}")
        except Exception as e:
            print(f"⚠ 無法自動安裝 aiohttp=={preferred_aio_version}（繼續安裝其他套件）：{e}")

    # 若成功安裝 aiohttp，則從 requirements 建立一個臨時檔排除 aiohttp，避免重覆安裝/編譯
    if has_aio and aio_installed:
        try:
            tmp_req = Path(tempfile.gettempdir()) / 'requirements_no_aiohttp.txt'
            with open(tmp_req, 'w', encoding='utf-8') as out:
                for ln in req_lines:
                    if not re.match(r"\s*aiohttp\b", ln, re.IGNORECASE):
                        out.write(ln)
            req_to_install = str(tmp_req)
            print(f"已建立臨時 requirements（排除 aiohttp）：{req_to_install}")
        except Exception:
            # 若寫入暫存檔失敗則退回安裝原始 requirements
            req_to_install = requirements_file

    cmd = [sys.executable, "-m", "pip", "install"]
    if prefer_binary:
        cmd.append("--prefer-binary")
    cmd.extend(["-r", req_to_install])

    try:
        # 以 streaming 模式執行，讓使用者可以即時看到錯誤
        run_subprocess_stream(cmd, env=env)
        print("✅ Python 套件安裝完成")
        return True
    except subprocess.CalledProcessError:
        print("❌ Python 套件安裝失敗。請按以下步驟手動處理：")
        print()
        print("1) 先升級 pip / setuptools / wheel：")
        print("   python -m pip install --upgrade pip setuptools wheel")
        print()
        print("2) 嘗試使用二進位 wheel（優先使用預編譯版本）：")
        print("   python -m pip install --prefer-binary -r {}".format(requirements_file))
        print("   若只針對 aiohttp 嘗試： python -m pip install --prefer-binary aiohttp")
        print("   或強制只接受二進位（若有對應 wheel）： python -m pip install --only-binary=:all: aiohttp")
        print()
        print("3) 若仍失敗，考慮使用 conda（若你可以安裝 Miniconda/Anaconda）：")
        print("   conda install -c conda-forge aiohttp")
        print()
        print("4) 若要在本機編譯，請安裝 Microsoft Visual C++ Build Tools（含 Windows SDK）：")
        print("   下載: https://visualstudio.microsoft.com/visual-cpp-build-tools/")
        print("   或使用 PowerShell 靜默安裝（需以管理員執行，會耗費大量空間/時間）")
        print("   參考：Invoke-WebRequest -Uri 'https://aka.ms/vs/17/release/vs_BuildTools.exe' -OutFile vs_BuildTools.exe ; .\\vs_BuildTools.exe --add Microsoft.VisualStudio.Workload.VCTools --quiet --wait --norestart --nocache")
        print()
        print("5) 作為最後手段，可從 Gohlke 下載已建置的 wheel 並手動安裝：")
        print("   https://www.lfd.uci.edu/~gohlke/pythonlibs/")
        print()
        print("完成上述任一步驟後，請重新執行安裝腳本或手動執行 pip install。")
        return False


def check_wkhtmltopdf(custom_path: str = None) -> (bool, str):
    """檢查 wkhtmltopdf 是否可用。回傳 (bool, path_or_message)。"""
    import shutil

    candidates = []
    # 優先使用傳入的自訂路徑
    if custom_path:
        candidates.append(custom_path)

    # 若環境變數有設定，加入候選
    if os.getenv('WKHTMLTOPDF_PATH'):
        candidates.append(os.getenv('WKHTMLTOPDF_PATH'))

    # 先檢查 PATH 中的可執行檔
    found = shutil.which('wkhtmltopdf')
    if found:
        candidates.append(found)

    # 常見預設安裝路徑（Windows）
    if is_windows():
        candidates.extend([
            r"C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe",
            r"C:\\Program Files (x86)\\wkhtmltopdf\\bin\\wkhtmltopdf.exe",
        ])

    # 容器與 Linux 常見路徑
    candidates.extend([
        "/usr/local/bin/wkhtmltopdf",
        "/usr/bin/wkhtmltopdf",
        "/opt/wkhtmltopdf/bin/wkhtmltopdf",
    ])

    # 嘗試每個候選，並以 --version 驗證
    for path in candidates:
        if not path:
            continue
        try:
            if Path(path).exists() and os.access(path, os.X_OK):
                result = subprocess.run([path, '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                out = result.stdout.decode('utf-8', errors='replace') if result.stdout else ''
                ver = out.strip().split()[-1] if out else 'unknown'
                return True, f"已安裝 ({path}) 版本: {ver}"
        except Exception:
            # 若該檔案存在但執行失敗，繼續嘗試其他 candidate
            continue

    msg = (
        "wkhtmltopdf 未偵測到。請安裝或將可執行檔放入容器，\n"
        "建議做法：\n"
        " 1) 設定環境變數 WKHTMLTOPDF_PATH 指向可執行檔 (可在 docker run 時使用 -e WKHTMLTOPDF_PATH=/usr/local/bin/wkhtmltopdf)\n"
        " 2) 或在 docker run 時把主機的執行檔掛載到容器，例如：\n"
        "    docker run -v /path/to/wkhtmltopdf:/usr/local/bin/wkhtmltopdf -e WKHTMLTOPDF_PATH=/usr/local/bin/wkhtmltopdf ...\n"
        " 3) 或在映像建立時透過 build-arg 指定路徑：docker build --build-arg WKHTMLTOPDF_PATH=/usr/local/bin/wkhtmltopdf .\n"
    )
    return False, msg


def create_new_config_example():
    """建立新版配置範例檔案（若不存在）。"""
    config_example = r"""
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
        "wkhtmltopdf_path": "/usr/local/bin/wkhtmltopdf"  # 在容器中預設路徑，可由 WKHTMLTOPDF_PATH 環境變數覆蓋
    }
}
"""
    config_file = Path('config_example.json')
    if not config_file.exists():
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(config_example)
        print("✅ 已建立 config_example.json 範例配置檔案")


def parse_args():
    p = argparse.ArgumentParser(description='Redmine 爬蟲工具安裝程式（Windows 友善）')
    p.add_argument('--yes', '-y', action='store_true', help='跳過互動提示，自動同意')
    p.add_argument('--skip-wkhtmltopdf', action='store_true', help='跳過 wkhtmltopdf 偵測')
    p.add_argument('--requirements-file', default='requirements.txt', help='requirements 檔案路徑')
    p.add_argument('--no-prefer-binary', dest='prefer_binary', action='store_false', help='不要使用 --prefer-binary')
    p.add_argument('--wkhtmltopdf-path', default=None, help='指定 wkhtmltopdf 執行檔路徑')
    p.add_argument(
        '--install-python',
        nargs='?',
        const='3.12.0',
        default=None,
        help=(
            '在 Windows 上自動安裝 Python：'
            ' 指定版本（例如 3.12.0）會從 python.org 下載對應的安裝檔並嘗試靜默安裝；'
            ' 使用值 "store" 則會開啟 Microsoft Store 的 Python 頁面。預設版本為 3.12.0。'
        ),
    )
    return p.parse_args()


def main():
    print('=== Redmine 爬蟲工具安裝程式 (Windows 友善) ===')
    args = parse_args()

    # 檢查 Python 版本
    if not check_python_version():
        # 若使用者要求自動安裝 Python，嘗試處理（僅在 Windows 有意義）
        if args.install_python and is_windows():
            choice = args.install_python
            if choice.lower() == 'store':
                # 開啟 Microsoft Store 的 Python 頁面（Windows 11 使用者友善）
                store_url = 'ms-windows-store://pdp/?productid=9PJPW5LDXLZ5'
                print(f"開啟 Microsoft Store Python 頁面: {store_url}")
                try:
                    webbrowser.open(store_url)
                except Exception:
                    print('無法以 URI 開啟 Microsoft Store，將開啟 python.org 下載頁面作為替代')
                    open_python_downloads_page()
                return False
            else:
                # 預設從 python.org 下載指定版本的安裝檔
                version = choice
                arch = platform.machine().lower()
                if 'arm' in arch:
                    arch_suffix = 'arm64'
                else:
                    arch_suffix = 'amd64'
                filename = f"python-{version}-{arch_suffix}.exe"
                url = f"https://www.python.org/ftp/python/{version}/{filename}"
                print(f"嘗試自動下載並安裝 Python {version} ({arch_suffix}) 從: {url}")
                success = download_and_run_installer(url)
                if not success:
                    print('自動安裝失敗，請改為手動安裝或使用 Microsoft Store。')
                    open_python_downloads_page()
                return success
        return False

    req_path = Path(args.requirements_file)
    if not req_path.exists():
        print(f"❌ 找不到 requirements 檔案: {req_path}")
        return False

    ok = install_packages(requirements_file=str(req_path), prefer_binary=args.prefer_binary)
    if not ok:
        print("套件安裝失敗，請先解決套件相依性後再重試。")
        return False

    wk_ok = True
    wk_msg = ''
    if not args.skip_wkhtmltopdf:
        wk_ok, wk_msg = check_wkhtmltopdf(custom_path=args.wkhtmltopdf_path)
        if wk_ok:
            print(f"✅ wkhtmltopdf: {wk_msg}")
        else:
            print(f"❌ {wk_msg}")

    create_new_config_example()

    print('\n=== 安裝結果 ===')
    if wk_ok:
        print('🎉 安裝完成！可以開始使用新版爬蟲工具')
        print('\n使用步驟:')
        print('1. 完整功能: python main.py')
        print('2. 配置設定: 編輯 config_example.json 並重命名為 config.json（或直接使用 src/infrastructure/config/settings.py 中的 ConfigManager，環境變數可覆蓋設定）')
    else:
        print('⚠️  安裝未完成，請先安裝 wkhtmltopdf（或使用 --skip-wkhtmltopdf 跳過）')

    return wk_ok


if __name__ == '__main__':
    success = main()
    if not success:
        # 在互動式執行時停留，非必須
        try:
            if sys.stdin and sys.stdin.isatty():
                input('按 Enter 鍵結束...')
        except Exception:
            pass
        sys.exit(1)
