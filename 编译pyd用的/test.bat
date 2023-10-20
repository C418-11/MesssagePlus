@ECHO OFF

START powershell "F:\Message_Plus\venv312\Scripts\python.exe" test_enable.py"
TIMEOUT 2 /NOBREAK
EXIT