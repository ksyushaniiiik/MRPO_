@echo off
chcp 65001 >nul
python -m pip install -r requirements.txt pyinstaller
pyinstaller --onefile --windowed --name ObuvSystem --add-data "resources;resources" run.py
pause
