# Infra Desktop AI Assistant

A Windows-based voice AI assistant with face detection, smart home control, Spotify integration, WhatsApp messaging, and more.

## Features

- **Voice Commands**: Activate with wakeword "infra" and give commands in natural language
- **Face Detection**: Real-time face detection with expression tracking
- **Spotify Control**: Play, pause, skip, shuffle, and manage playlists
- **WhatsApp Integration**: Send messages and make calls via voice command
- **Google Calendar & Contacts**: Sync and manage your Google Calendar and Contacts
- **Smart Home**: Control brightness, volume, Wi-Fi, Bluetooth devices
- **Microsoft Store**: Search and install apps hands-free
- **Alerts & Reminders**: Set time-based alerts and reminders
- **YouTube Search**: Find and open YouTube videos by voice

## Prerequisites

- **Python 3.9+** (ideally 3.10+)
- **Windows 10/11** with Bluetooth and microphone support
- **Git** for cloning the repository

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/partha-hue/inframind-desktop-ai-assistant.git
cd inframind-desktop-ai-assistant
```

### 2. Create & Activate Virtual Environment

```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up API Keys & Credentials

#### A. Picovoice (Wakeword Detection)

1. Go to [Picovoice Console](https://console.picovoice.ai/)
2. Sign up and create a project
3. Copy your **AccessKey**
4. Set environment variable:
   ```powershell
   $env:PICOVOICE_ACCESS_KEY='your_access_key_here'
   ```

#### B. Spotify

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create an app and get **Client ID** and **Client Secret**
3. Set environment variables:
   ```powershell
   $env:SPOTIFY_CLIENT_ID='your_client_id'
   $env:SPOTIFY_CLIENT_SECRET='your_client_secret'
   ```

#### C. Google OAuth (Calendar & Contacts)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable **Google Calendar API** and **Google Contacts API**
4. Create an **OAuth 2.0 Desktop Application** credential
5. Download the JSON file and rename it to `credentials.json` in the project root
6. On first run, the app will open a browser for you to authorize access

#### D. Cohere API (Optional - for AI features)

1. Go to [Cohere Dashboard](https://dashboard.cohere.ai/)
2. Create an API key
3. Set environment variable:
   ```powershell
   $env:COHERE_API_KEY='your_api_key'
   ```

#### E. Bluetooth Control (Optional - for Windows)

1. Download [BluetoothCL.exe](http://www.nirsoft.net/utils/bluetoothcl.html)
2. Update `BLUETOOTHCL_PATH` in `main.py` to match your installation location

#### F. Android Debug Bridge (Optional - for Android integration)

1. Download [Android Platform Tools](https://developer.android.com/studio/releases/platform-tools)
2. Update `ADB_PATH` in `main.py` to match your installation location

### 5. (Optional) Create .env File

Copy `.env.example` to `.env` and fill in your values:

```powershell
cp .env.example .env
```

Then load variables before running:

```powershell
# PowerShell - Load from .env (you'll need to parse it manually or use a tool)
# Or just set them directly as shown above
```

## Running the App

```bash
python main.py
```

The app will:
1. Start listening for the wakeword **"infra"**
2. Open a face detection window
3. Wait for voice commands
4. Execute the recognized command and speak back the result

## Voice Commands

### Music / Spotify
- "play [song name]"
- "pause music"
- "next song"
- "volume up" / "volume down"
- "shuffle on"

### Contacts & Messaging
- "add contact [name] [phone number]"
- "send WhatsApp message to [name] [message]"
- "call [name]"

### Smart Home
- "turn on Wi-Fi" / "turn off Wi-Fi"
- "connect to Wi-Fi [network name]"
- "set brightness to [0-100]"
- "list Bluetooth devices"
- "connect to [device name]"

### Productivity
- "open word"
- "search Google for [query]"
- "show my calendar"
- "sync Google contacts"

### System
- "what time is it"
- "set alert in 10 minutes to [reminder]"
- "shutdown"

## Troubleshooting

### Wakeword Not Detected
- Ensure `PICOVOICE_ACCESS_KEY` is set correctly
- Check microphone is working: `nircmd.exe changesysvolume 1000` (test volume)

### Spotify Not Initializing
- Verify `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET` are set
- Start playing something on Spotify first

### Face Detection Window Crash
- Ensure OpenCV is installed: `pip install opencv-python`
- Check webcam permissions in Windows Settings

### Google Auth Issues
- Delete `token.pickle` and run again to re-authorize
- Ensure `credentials.json` exists in project root

## Project Structure

```
inframind-desktop-ai-assistant/
├── main.py                  # Main application entry point
├── requirements.txt         # Python dependencies
├── credentials.json         # Google OAuth credentials (DO NOT COMMIT)
├── credentials.example.json # Example Google OAuth structure
├── .env.example             # Example environment variables
├── .gitignore               # Ignore sensitive files
├── contacts.json            # Saved contacts
├── bt_devices.json          # Saved Bluetooth device mappings
├── token.pickle             # Google OAuth token (auto-generated)
└── README.md                # This file
```

## Security Notes

- **Never commit** `credentials.json`, `.env`, or `token.pickle` to version control
- Store all API keys as environment variables
- Keep secrets in a secure location (e.g., password manager)
- Revoke/rotate keys if accidentally exposed

## Contributing

Feel free to fork and submit pull requests for improvements!

## License

MIT License - see LICENSE file for details

## Support

For issues, questions, or feature requests, please open an issue on GitHub.

---

**Created by**: Partha Chakraborty  
**Last Updated**: February 3, 2026
