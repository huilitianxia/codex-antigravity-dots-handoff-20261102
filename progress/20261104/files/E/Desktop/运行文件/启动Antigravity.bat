@echo off
set "HTTP_PROXY=http://127.0.0.1:7890"
set "HTTPS_PROXY=http://127.0.0.1:7890"
set "NO_PROXY=localhost,127.0.0.1,::1"

start "" "%LOCALAPPDATA%\Programs\Antigravity\Antigravity.exe"