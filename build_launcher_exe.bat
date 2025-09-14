@echo off
REM Build script to create a single-file exe for launcher.py using PyInstaller
REM Usage: run this script in an elevated cmd or powershell as needed.

chcp 65001

python -m pip install --upgrade pip
python -m pip install pyinstaller

REM Remove previous build/dist if exist
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist launcher.spec del /f launcher.spec

REM Create exe (onefile, console)
REM Ensure the Python Scripts directory (where pyinstaller.exe is installed) is on PATH.
REM We detect it via a small Python snippet and append it to PATH for this session.
for /f "delims=" %%p in ('python -c "import sysconfig; print(sysconfig.get_path(\"scripts\"))"') do set PY_SCRIPTS=%%p
echo Detected Python scripts dir: %PY_SCRIPTS%
if defined PY_SCRIPTS (
	REM Use CALL to expand PATH at execution time to avoid parse errors if PATH contains special chars
	call set "PATH=%%PATH%%;%PY_SCRIPTS%"
) else (
	echo Warning: could not detect Python scripts dir; pyinstaller may not be found on PATH.
)

REM Use %%~dp0 (batch file directory) so add-data references are absolute and work regardless of current working dir.
REM Windows add-data syntax inside the argument: SOURCE;DEST (use ; as separator)
REM 檢查 extras\wkhtmltopdf 是否存在，若存在則準備額外的 --add-data / --add-binary 參數
set "EXTRA_ADD_ARGS="
if exist "%~dp0extras\wkhtmltopdf" (
	echo Found extras\wkhtmltopdf - will include it into the bundle.
	REM 包含整個資料夾作為資料
	set EXTRA_ADD_ARGS=--add-data="%~dp0extras\wkhtmltopdf;extras\wkhtmltopdf"
	REM 若存在 bin\wkhtmltopdf.exe，將此可執行加入為 binary（確保可執行權限在非 Windows 平台）
	if exist "%~dp0extras\wkhtmltopdf\bin\wkhtmltopdf.exe" (
		REM NOTE: PyInstaller expects SOURCE:DEST. Use the --add-binary=SOURCE:DEST form and quote the whole arg after the = to avoid parsing issues.
		REM On Windows the PyInstaller add-binary separator between source and dest is ':' and when passing via cmd we should use --add-binary=SOURCE:DEST (no extra inner quotes).
		REM Build a properly quoted argument and append it to EXTRA_ADD_ARGS.
		set WK_EXE=%~dp0extras\wkhtmltopdf\bin\wkhtmltopdf.exe
		set WK_DEST=extras\wkhtmltopdf\bin
		REM Use ';' as separator on Windows and quote the whole token so PyInstaller receives one argument ("source;dest").
		set EXTRA_ADD_ARGS=%EXTRA_ADD_ARGS% --add-binary="%WK_EXE%;%WK_DEST%"
	)
)

python -m PyInstaller --onefile --console --name launcher --add-data "%~dp0requirements.txt;." %EXTRA_ADD_ARGS% launcher.py

echo.
echo Build complete (basic). The exe will be in the dist\ folder as launcher.exe

echo.
echo Now building intermediate variant that includes project data (src, config_example.json and requirements.txt) into the exe.
echo This helps the exe find project modules and bundled metadata when not relying on external .py files.
python -m PyInstaller --onefile --console --name launcher_with_data --add-data "%~dp0src;src" --add-data "%~dp0config_example.json;." --add-data "%~dp0requirements.txt;." %EXTRA_ADD_ARGS% launcher.py

echo.
echo Optional: To include wkhtmltopdf/wkhtmltoimage binary (if you want everything bundled), place the executables and libs under extras\wkhtmltopdf\
echo This script will include the entire extras\wkhtmltopdf folder into the exe when present.
REM Check extras relative to the batch file directory
if exist "%~dp0extras\wkhtmltopdf" (
	echo Found extras\wkhtmltopdf - building full bundle (launcher_full.exe) with extras included...
	python -m PyInstaller --onefile --console --name launcher_full --add-data "%~dp0src;src" --add-data "%~dp0config_example.json;." --add-data "%~dp0requirements.txt;." %EXTRA_ADD_ARGS% launcher.py
) else (
	echo extras\wkhtmltopdf not found. To include it, put wkhtmltopdf/wkhtmltoimage and supporting libs under extras\wkhtmltopdf (next to this batch file) then re-run this script.
)

:after_wkhtml

echo.
echo All done. Find outputs in dist\ (launcher.exe, launcher_with_data.exe)
pause
