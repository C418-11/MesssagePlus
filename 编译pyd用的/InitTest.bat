@ECHO OFF

ECHO Copying test file
COPY "F:\Message_Plus\编译pyd用的\test.py" "F:\Message_Plus\编译pyd用的\Build\pyd\test_enable.py"
COPY "F:\Message_Plus\编译pyd用的\test.bat" "F:\Message_Plus\编译pyd用的\Build\pyd\test_enable.bat"

CD "F:\Message_Plus\编译pyd用的\Build\pyd"

ECHO Starting Test file
START test_enable
START test_enable


TIMEOUT 10 /NOBREAK
TIMEOUT 5
PAUSE