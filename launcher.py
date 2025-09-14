# -*- coding: utf-8 -*-
"""
簡單的 Python 啟動器，功能等同於原本的 start.bat
會呼叫專案中的其他 Python 腳本：install.py, main.py, test_pdf_naming.py, git_issue_extractor_silent.py

此檔案設計為可被 PyInstaller 打包成單一 exe。
"""
import sys
import os
import shutil

# 我們將直接匯入專案中的模組並呼叫它們的 entrypoints，這樣 PyInstaller 可以把所有模組包含到同一個 exe。


def print_header():
    print('=' * 47)
    print('       新版 Redmine 爬蟲工具啟動器')
    print('=' * 47)
    print()


def run_install():
    try:
        # install.py 的 main() 已定義為回傳 bool
        import install

        return install.main()
    except Exception as e:
        print(f"執行 install 發生錯誤: {e}")
        return False


# --- 新增：處理 PyInstaller single-file 解壓路徑與資源定位 ---
def bundled_path(*path_parts):
    """回傳在 frozen (PyInstaller single-file) 或 開發環境下的資源實際路徑。

    - 如果被 PyInstaller 打包成 single-file，資源會在執行時被解壓到 sys._MEIPASS。
    - 否則使用檔案所在資料夾（專案 root）作為 base。
    """
    base = getattr(sys, "_MEIPASS", None)
    if base is None:
        # 在開發環境時，假設 launcher.py 位於專案根目錄
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, *path_parts)


def _frozen_initialization():
    """在被 PyInstaller 打包成 single-file 時，調整環境：
    - 把打包進來的 `src` 加入 sys.path，讓內部模組可以 import
    - 把 extras\wkhtmltopdf\bin（若存在）加入 PATH，讓 subprocess 可以找到 wkhtmltopdf
    - 可選：將工作目錄切換到 base（避免相對路徑錯亂）
    """
    if not getattr(sys, "frozen", False):
        return

    # base 解壓資料夾（_MEIPASS）
    base = getattr(sys, "_MEIPASS", None)
    if not base:
        return

    # 把 base/src 加到 sys.path（若存在）
    src_path = os.path.join(base, "src")
    if os.path.isdir(src_path) and src_path not in sys.path:
        sys.path.insert(0, src_path)

    # 將 extras\wkhtmltopdf\bin 加到 PATH（Windows）或 extras/wkhtmltopdf/bin 加到 PATH
    wk_bin = os.path.join(base, "extras", "wkhtmltopdf", "bin")
    if os.path.isdir(wk_bin):
        # 在 PATH 前端加入，確保優先使用打包內的二進位
        old_path = os.environ.get("PATH", "")
        if wk_bin not in old_path:
            os.environ["PATH"] = wk_bin + os.pathsep + old_path

    # 可選：將工作目錄切換到 base，減少相對路徑問題
    try:
        os.chdir(base)
    except Exception:
        pass


# 立即執行 frozen 初始化（模組匯入後立刻設好環境）
_frozen_initialization()


def run_fullversion():
    try:
        import main as main_module

        # 優先使用 run_main()（我們新增的函式），避免 main.sync_main() 呼叫 sys.exit
        if hasattr(main_module, 'run_main'):
            return main_module.run_main()
        if hasattr(main_module, 'sync_main'):
            # fallback，但 sync_main 可能會 sys.exit
            main_module.sync_main()
            return True
        elif hasattr(main_module, 'main'):
            # 若 main 是 coroutine
            import asyncio

            asyncio.run(main_module.main())
            return True
        else:
            print('找不到 main 的 entrypoint')
            return False
    except SystemExit:
        # main.sync_main 可能呼叫 sys.exit
        return True
    except Exception as e:
        print(f"執行 main 發生錯誤: {e}")
        return False


def run_pdftest():
    try:
        import test_pdf_naming

        if hasattr(test_pdf_naming, 'main'):
            test_pdf_naming.main()
            return True
        else:
            print('找不到 test_pdf_naming 的 main()')
            return False
    except Exception as e:
        print(f"執行 test_pdf_naming 發生錯誤: {e}")
        return False


def run_githistory():
    try:
        import git_issue_extractor_silent as git_tool

        # 使用非暫停（pause_on_exit=False）模式避免最後阻塞
        if hasattr(git_tool, 'main'):
            git_tool.main(pause_on_exit=False)
            return True
        else:
            print('找不到 git_issue_extractor_silent 的 main()')
            return False
    except Exception as e:
        print(f"執行 git_issue_extractor_silent 發生錯誤: {e}")
        return False


def main():
    os.system('chcp 65001 >nul 2>&1') if os.name == 'nt' else None

    print_header()

    while True:
        print('請選擇操作:')
        print()
        print('1. 安裝/檢查相依性')
        print('2. 完整功能爬蟲')
        print('3. PDF 檔名測試')
        print('4. Git History Issue 編號提取')
        print()
        choice = input('請輸入選項 (1-4), 或輸入 q 離開: ').strip()

        if choice.lower() == 'q':
            print('離開')
            break

        if choice == '1':
            print('\n啟動: install.py ...')
            run_install()
        elif choice == '2':
            print('\n啟動: main.py ...')
            run_fullversion()
        elif choice == '3':
            print('\n啟動: test_pdf_naming.py ...')
            run_pdftest()
        elif choice == '4':
            print('\n啟動: git_issue_extractor_silent.py ...')
            run_githistory()
        else:
            print('無效的選項，請重新輸入')

        print()

    print('Bye')


if __name__ == '__main__':
    main()
