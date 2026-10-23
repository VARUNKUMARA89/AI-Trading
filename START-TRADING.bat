@echo off
cd /d %~dp0
if not exist .venv call setup.bat
call .venv\Scripts\activate
python -m arena gui
pause
