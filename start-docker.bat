@echo off
REM start-docker.bat - Windows helper to build and run the redmine-crawler Docker image
REM Usage:
REM   build:     start-docker.bat build
REM   run full:  start-docker.bat run full C:\path\to\outdir
REM   run install: start-docker.bat run install

set IMAGE_NAME=redmine-crawler:latest

:parse
if "%1"=="" goto help
if /I "%1"=="build" goto build
if /I "%1"=="run" goto run
if /I "%1"=="prepare" goto prepare

eg echo Unknown command: %1
goto help

:build
echo Removing existing image (if any)...
docker image rm %IMAGE_NAME% -f >nul 2>&1 || echo no existing image
echo Building image %IMAGE_NAME% ...
docker build -t %IMAGE_NAME% .
goto end

:run
REM second arg is subcommand: full | install | pdftest | ...
if "%2"=="" (
n	echo Missing run subcommand. Examples: full, install, pdftest
	goto end
)
set SUBCMD=%2

REM optional third arg: host output directory for mounting (Windows path)
set HOST_OUT=%3
if not "%HOST_OUT%"=="" (
	REM normalize backslashes for docker on Windows; Docker Desktop / WSL2 can accept Windows paths
	set HOST_OUT_ARG=-v "%HOST_OUT%:/app/out"
) else (
	set HOST_OUT_ARG=
)
echo Running container: %IMAGE_NAME% %SUBCMD%
docker run --rm -it %HOST_OUT_ARG% %IMAGE_NAME% %SUBCMD%
goto end

:prepare
echo Checking for wkhtmltox_0.12.6-1.jammy_amd64.deb in current directory...
if exist wkhtmltox_0.12.6-1.jammy_amd64.deb (
	echo Found wkhtmltox_0.12.6-1.jammy_amd64.deb
	goto end
)

echo File not found. Downloading from GitHub releases...
powershell -Command "try { Invoke-WebRequest -Uri 'https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-2/wkhtmltox_0.12.6.1-2.jammy_amd64.deb' -OutFile 'wkhtmltox_0.12.6-1.jammy_amd64.deb' -UseBasicParsing; Write-Host 'Download complete' } catch { Write-Host 'Download failed:' $_.Exception.Message; exit 1 }"
if exist wkhtmltox_0.12.6-1.jammy_amd64.deb (
	echo Download succeeded.
) else (
	echo Download failed. Please download manually and place the .deb in this folder.
)
goto end

:help
echo.
echo Usage: start-docker.bat ^<command^> [args]
echo.
echo Commands:
echo   build                Build the docker image (removes existing image first)
echo   run ^<subcmd^> ^[host_out_dir^]  Run container with subcommand (full, install, pdftest). Optionally mount host output dir to /app/out.
echo.
echo Examples:
echo   start-docker.bat build
echo   start-docker.bat run full C:\Users\you\redmine_out
echo   start-docker.bat run install
echo.
echo Notes:
echo - On Windows, use Docker Desktop with WSL2 backend for best compatibility.
echo - If using a bind mount from Windows, ensure directory exists and Docker has permission to access it.
echo - If wkhtmltopdf is missing inside the container, see DOCKER.md for troubleshooting.
goto end

:end
pause
