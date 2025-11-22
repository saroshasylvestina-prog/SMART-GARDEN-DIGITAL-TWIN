@echo off
echo ========================================
echo ARDUINO CODE UPLOAD HELPER
echo ========================================
echo.
echo This will open Arduino IDE with the clean pump control code.
echo.
echo IMPORTANT STEPS:
echo 1. Arduino IDE will open with the code
echo 2. Select your board: Tools -^> Board -^> Arduino Uno
echo 3. Select COM port: Tools -^> Port -^> COM5
echo 4. Click Upload button (or press Ctrl+U)
echo 5. Wait for "Done uploading"
echo 6. Close Serial Monitor if it opens
echo.
echo Press any key to open Arduino IDE...
pause >nul

REM Try to open Arduino IDE with the .ino file
if exist "arduino_pump_control_clean.ino" (
    echo Opening arduino_pump_control_clean.ino in Arduino IDE...
    start "" "arduino_pump_control_clean.ino"
) else if exist "arduino_pump_control.ino" (
    echo Opening arduino_pump_control.ino in Arduino IDE...
    start "" "arduino_pump_control.ino"
) else (
    echo ERROR: Arduino .ino file not found!
    echo Please make sure arduino_pump_control_clean.ino exists in this folder.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Arduino IDE should now be open.
echo.
echo NEXT STEPS:
echo 1. Check Tools -^> Board (should be Arduino Uno)
echo 2. Check Tools -^> Port (should be COM5)
echo 3. Click Upload button (arrow icon) or press Ctrl+U
echo 4. Wait for "Done uploading" message
echo 5. Close Serial Monitor
echo 6. Close Arduino IDE
echo.
echo After uploading, restart your Flask app.
echo ========================================
pause

