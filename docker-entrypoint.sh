#!/usr/bin/env bash
set -euo pipefail

cd /app

# Detect python executable: prefer python3.12, then python3, then python
PY=""
if command -v python3.12 >/dev/null 2>&1; then
  PY=python3.12
elif command -v python3 >/dev/null 2>&1; then
  PY=python3
elif command -v python >/dev/null 2>&1; then
  PY=python
else
  echo "Error: no Python interpreter found in container. Please ensure Python is installed." >&2
  exit 1
fi

usage() {
  cat <<'EOF'
Redmine 爬蟲容器 入口說明

用法：
  docker run --rm -it image_name [install|full|pdftest|githistory]

指令：
  install     執行 install.py 以安裝或檢查相依性
  full        執行 main.py（完整爬蟲功能）
  pdftest     執行 test_pdf_naming.py（PDF 檔名測試）
  githistory  執行 git_issue_extractor_silent.py（Git History Issue 提取）
EOF
}

if [ "$#" -eq 0 ]; then
  cmd="full"
else
  cmd="$1"
fi

case "$cmd" in
  install)
    echo "執行安裝程序..."
    $PY install.py
    ;;
  full)
    echo "啟動完整功能爬蟲..."
    $PY main.py
    ;;
  pdftest)
    echo "執行 PDF 檔名測試..."
    $PY test_pdf_naming.py
    ;;
  githistory)
    echo "執行 Git History Issue 編號提取..."
    $PY git_issue_extractor_silent.py
    ;;
  -h|--help|help)
    usage
    ;;
  *)
    echo "未知指令: $cmd"
    usage
    exit 1
    ;;
esac
