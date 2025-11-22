@echo off
echo ========================================
echo RESTARTING FLASK APP WITH ARDUINO
echo ========================================
echo.

echo [STEP 1] Checking for running Flask app...
tasklist /FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq *app.py*" 2>NUL | find /I "python.exe" >NUL
if %ERRORLEVEL% == 0 (
    echo Found running Flask app, stopping...
    taskkill /F /IM python.exe /T 2>NUL
    timeout /t 2 /nobreak >NUL
)

echo.
echo [STEP 2] Checking COM ports...
python -c "import serial.tools.list_ports; ports = serial.tools.list_ports.comports(); print('Available ports:'); [print(f'  {p.device}: {p.description}') for p in ports]" 2>NUL

echo.
echo [STEP 3] IMPORTANT: Make sure Arduino Serial Monitor is CLOSED!
echo Press any key when ready to start Flask app...
pause >NUL

echo.
echo [STEP 4] Starting Flask app...
echo.
python app.py

pause

