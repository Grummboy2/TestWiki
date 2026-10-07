@echo off
cd /d "%~dp0"
node tools\visual-editor-server.js
if errorlevel 1 pause
