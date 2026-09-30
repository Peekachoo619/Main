@echo off
setlocal
cd /d "%~dp0"
title Google Flow for Claude - Installer
echo ============================================
echo   Google Flow for Claude - one-click setup
echo ============================================
echo.

where node >nul 2>nul
if errorlevel 1 (
  echo Node.js is not installed. Installing it now...
  winget install -e --id OpenJS.NodeJS.LTS --accept-source-agreements --accept-package-agreements
  echo.
  echo Node.js was installed. Please CLOSE this window and double-click INSTALL.bat again.
  pause
  exit /b
)

set /p EMAIL=Type your Google email and press Enter (example: you@gmail.com): 

echo.
echo Installing (1-2 minutes)...
set PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1
call npm install --no-audit --no-fund
if errorlevel 1 (
  echo npm install failed. Take a screenshot of this window and send it to Claude.
  pause
  exit /b
)

node scripts\setup-windows.mjs "%EMAIL%"
echo.
echo ============================================
echo  DONE. Now:
echo   1. Fully QUIT Claude Desktop (right-click its tray icon ^> Quit) and open it again.
echo   2. In Claude, type: Use google-flow to open Flow
echo   3. A Chrome window opens. Sign in to Google there ONCE.
echo ============================================
pause
