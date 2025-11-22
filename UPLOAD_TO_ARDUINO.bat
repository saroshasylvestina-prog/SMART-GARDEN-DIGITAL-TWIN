@echo off
echo ========================================
echo UPLOAD ARDUINO CODE - AUTOMATED
echo ========================================
echo.

REM Check if Arduino IDE is installed
set ARDUINO_PATH=
if exist "%LOCALAPPDATA%\Arduino IDE\Arduino IDE.exe" (
    set "ARDUINO_PATH=%LOCALAPPDATA%\Arduino IDE\Arduino IDE.exe"
) else if exist "%ProgramFiles%\Arduino\arduino.exe" (
    set "ARDUINO_PATH=%ProgramFiles%\Arduino\arduino.exe"
) else if exist "%ProgramFiles(x86)%\Arduino\arduino.exe" (
    set "ARDUINO_PATH=%ProgramFiles(x86)%\Arduino\arduino.exe"
)

if defined ARDUINO_PATH (
    echo Found Arduino IDE at: %ARDUINO_PATH%
    echo.
    echo Opening Arduino IDE with pump control code...
    echo.
    start "" "%ARDUINO_PATH%" "arduino_pump_control.ino"
    echo.
    echo ========================================
    echo Arduino IDE should now be open!
    echo.
    echo NEXT STEPS (DO THESE MANUALLY):
    echo ========================================
    echo 1. In Arduino IDE, check:
    echo    - Tools -^> Board -^> Arduino Uno (or your board)
    echo    - Tools -^> Port -^> COM5 (or your Arduino port)
    echo.
    echo 2. Click the UPLOAD button (arrow -^> icon)
    echo    OR press Ctrl+U
    echo.
    echo 3. Wait for "Done uploading" message
    echo.
    echo 4. Close Serial Monitor if it opens
    echo.
    echo 5. Close Arduino IDE
    echo.
    echo 6. Restart your Flask app
    echo ========================================
) else (
    echo Arduino IDE not found in common locations.
    echo.
    echo Please:
    echo 1. Open Arduino IDE manually
    echo 2. File -^> Open -^> Select arduino_pump_control.ino
    echo 3. Tools -^> Board -^> Select your board
    echo 4. Tools -^> Port -^> Select COM5 (or your port)
    echo 5. Click Upload button
    echo.
)

pause

