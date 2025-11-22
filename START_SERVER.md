# How to Start the Server

## Quick Start

### Option 1: Double-click the batch file
- Double-click `START_SERVER.bat` in Windows Explorer
- The server will start automatically

### Option 2: Command Line
1. Open Command Prompt or PowerShell
2. Navigate to the project folder:
   ```bash
   cd D:\Digigarden
   ```
3. Run:
   ```bash
   python app.py
   ```

### Option 3: Python directly
```bash
python -m flask run
```

## Access the Application

Once the server is running, open your browser and go to:
- **Main Dashboard**: http://localhost:5000
- **Plant Scanner**: http://localhost:5000/plant-scan

## Server Status

You should see output like:
```
Starting Flask app...
Server will be available at http://127.0.0.1:5000/ or http://localhost:5000/
 * Running on http://0.0.0.0:5000
 * Debug mode: on
```

## Troubleshooting

### Port 5000 Already in Use

If you get an error that port 5000 is already in use:

1. **Find what's using the port:**
   ```bash
   netstat -ano | findstr :5000
   ```

2. **Kill the process** (replace PID with the number from step 1):
   ```bash
   taskkill /PID <PID> /F
   ```

3. **Or use a different port:**
   Edit `app.py` and change:
   ```python
   app.run(host='0.0.0.0', port=5000, debug=True)
   ```
   To:
   ```python
   app.run(host='0.0.0.0', port=5001, debug=True)
   ```

### Connection Refused Error

1. **Make sure the server is running**
   - Check the terminal window - it should show "Running on..."
   - If not, start it using one of the methods above

2. **Check firewall**
   - Windows Firewall might be blocking the connection
   - Try temporarily disabling it to test

3. **Try 127.0.0.1 instead of localhost**
   - http://127.0.0.1:5000

4. **Check if Python is running**
   ```bash
   python --version
   ```

### Import Errors

If you get import errors when starting:
```bash
pip install -r requirements.txt
```

## Stopping the Server

- Press `Ctrl+C` in the terminal where the server is running
- Or close the terminal window

## Running in Background (Windows)

To run the server in the background without keeping the terminal open:

1. Create a shortcut to `START_SERVER.bat`
2. Right-click → Properties → Run: Minimized
3. Or use Task Scheduler to run it at startup

