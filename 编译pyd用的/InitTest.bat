@ECHO OFF

ECHO Copying test file
COPY "F:\Message_Plus\����pyd�õ�\test.py" "F:\Message_Plus\����pyd�õ�\Build\pyd\test_enable.py"
COPY "F:\Message_Plus\����pyd�õ�\test.bat" "F:\Message_Plus\����pyd�õ�\Build\pyd\test_enable.bat"

CD "F:\Message_Plus\����pyd�õ�\Build\pyd"

ECHO Starting Test file
START test_enable
START test_enable


TIMEOUT 10 /NOBREAK
TIMEOUT 5
PAUSE