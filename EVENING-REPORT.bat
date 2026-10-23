@echo off
cd /d %~dp0
call .venv\Scripts\activate
python -m arena report --ai || python -m arena report
pause
