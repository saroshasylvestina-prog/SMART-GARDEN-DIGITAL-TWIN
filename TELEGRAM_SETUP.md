# Telegram Bot Setup Guide

This guide will help you set up Telegram notifications for your Smart Garden Digital Twin.

## Step 1: Create a Telegram Bot

1. Open Telegram and search for **@BotFather**
2. Start a conversation with BotFather
3. Send the command: `/newbot`
4. Follow the instructions:
   - Choose a name for your bot (e.g., "My Garden Bot")
   - Choose a username (must end with "bot", e.g., "my_garden_bot")
5. BotFather will give you a **Bot Token** - save this!

**Example:**
```
Token: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

## Step 2: Get Your Chat ID

### Method 1: Using @userinfobot
1. Search for **@userinfobot** on Telegram
2. Start a conversation
3. It will send you your Chat ID (a number like `123456789`)

### Method 2: Using @getidsbot
1. Search for **@getidsbot** on Telegram
2. Start a conversation
3. It will send you your Chat ID

### Method 3: Using a Group
1. Create a group or use an existing one
2. Add **@getidsbot** to the group
3. It will show the group's Chat ID (negative number like `-123456789`)

## Step 3: Configure the Bot

### Option A: Environment Variables (Recommended)

Set these environment variables:

**Windows (PowerShell):**
```powershell
$env:TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
$env:TELEGRAM_CHAT_ID = "YOUR_CHAT_ID_HERE"
```

**Windows (Command Prompt):**
```cmd
set TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN_HERE
set TELEGRAM_CHAT_ID=YOUR_CHAT_ID_HERE
```

**Linux/Mac:**
```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN_HERE"
export TELEGRAM_CHAT_ID="YOUR_CHAT_ID_HERE"
```

### Option B: Edit telegram_notifier.py

Open `telegram_notifier.py` and modify these lines (around line 160):

```python
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Replace with your token
CHAT_ID = "YOUR_CHAT_ID_HERE"      # Replace with your chat ID
```

## Step 4: Install Required Library

```bash
pip install requests
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

## Step 5: Test the Connection

### Method 1: Using the Web Interface
1. Go to http://127.0.0.1:5000
2. Use the API endpoint: `/api/telegram/test` (POST request)

### Method 2: Using Python
```python
from telegram_notifier import telegram
telegram.test_connection()
```

### Method 3: Using curl
```bash
curl -X POST http://127.0.0.1:5000/api/telegram/test
```

## Step 6: Restart Flask App

After configuring, restart your Flask application:

```bash
python app.py
```

## What You'll Receive

Once configured, you'll receive Telegram messages for:

1. **Plant Alerts:**
   - Low/High Temperature
   - Low/High Humidity
   - Low/High Soil Moisture
   - Low Light
   - Poor Air Quality
   - High CO2

2. **Automated Responses:**
   - Pump turned ON (low moisture)
   - Pump turned ON (high temperature)
   - Pump turned OFF (high moisture)

3. **Status Summaries:**
   - Current sensor readings
   - Daily reports

## API Endpoints

- `GET /api/telegram/status` - Check if Telegram is configured
- `POST /api/telegram/test` - Send a test message
- `POST /api/telegram/status-summary` - Send current plant status

## Troubleshooting

### "Failed to send message"
- Check that your Bot Token is correct
- Verify your Chat ID is correct
- Make sure you've started a conversation with your bot (send `/start`)

### "Not configured"
- Set the environment variables or edit `telegram_notifier.py`
- Restart the Flask app after configuration

### Bot not responding
- Make sure you've sent `/start` to your bot first
- Check that the bot token hasn't expired
- Verify the chat ID is correct (positive for personal, negative for groups)

## Security Note

⚠️ **Never commit your Bot Token or Chat ID to version control!**

Use environment variables or a `.env` file (not included in git).

