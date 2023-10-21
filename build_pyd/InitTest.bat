@ECHO OFF

ECHO Copying test file
COPY ".\test.py" ".\Build\pyd\test_enable.py"
COPY ".\test.bat" ".\Build\pyd\test_enable.bat"

CD ".\Build\pyd"

ECHO Starting Test file
START test_enable
START test_enable


TIMEOUT 10 /NOBREAK
PAUSE
EXIT