# Infra Desktop AI Assistant - Quick Setup Guide

## Step 1: Clone & Install

```bash
git clone https://github.com/partha-hue/inframind-desktop-ai-assistant.git
cd inframind-desktop-ai-assistant
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Step 2: Configure API Keys

### Option A: Use `.env.local` File (Recommended for Development)

1. Copy `.env.local` template:
   ```bash
   cp .env.local .env
   ```

2. Edit `.env` and add your API keys (see sections below)

3. Run the app (keys load automatically from `.env`):
   ```bash
   python main.py
   ```

### Option B: Set Environment Variables Manually (For Testing)

```powershell
$env:PICOVOICE_ACCESS_KEY = 'your_key_here'
$env:SPOTIFY_CLIENT_ID = 'your_id_here'
$env:SPOTIFY_CLIENT_SECRET = 'your_secret_here'
python main.py
```

---

## API Keys & How to Get Them

### 1. **Picovoice Wakeword Detection** (Required)

**What it does**: Recognizes the "infra" wakeword to activate voice commands

**Steps**:
1. Go to https://console.picovoice.ai/
2. Sign up for a **free account**
3. Create a new project
4. Copy your **AccessKey**
5. Add to `.env`:
   ```
   PICOVOICE_ACCESS_KEY=your_access_key_here
   ```

**Cost**: Free tier available (~10K requests/month)

---

### 2. **Spotify API** (Required for Music Control)

**What it does**: Play, pause, skip songs, control playlists

**Steps**:
1. Go to https://developer.spotify.com/dashboard
2. Log in with your Spotify account (free or premium)
3. Click **Create an App**
4. Accept terms and create the app
5. Copy **Client ID** and **Client Secret**
6. Add to `.env`:
   ```
   SPOTIFY_CLIENT_ID=your_client_id_here
   SPOTIFY_CLIENT_SECRET=your_client_secret_here
   ```

**Cost**: Free for development

---

### 3. **Google OAuth** (Required for Calendar & Contacts)

**What it does**: Sync your Google Calendar and Contacts

**Steps**:
1. Go to https://console.cloud.google.com/
2. Create a **new project**
3. Enable these APIs:
   - Google Calendar API
   - Google Contacts API
   - Google People API
4. Create **OAuth 2.0 Desktop Application** credentials
5. Download the JSON file and save as **`credentials.json`** in the project root
6. On first run, you'll be prompted to authorize via browser

**Important**: Never commit `credentials.json` to Git (it's in `.gitignore`)

**Cost**: Free

---

### 4. **Cohere AI** (Optional - for AI Enhancements)

**What it does**: AI-powered responses and intent understanding

**Steps**:
1. Go to https://dashboard.cohere.ai/
2. Sign up for free account
3. Create an API key
4. Add to `.env`:
   ```
   COHERE_API_KEY=your_api_key_here
   ```

**Cost**: Free tier available (~100K tokens/month)

---

### 5. **Android Platform Tools** (Optional - for Android Integration)

**What it does**: Control Android devices, send SMS/WhatsApp from PC

**Steps**:
1. Download from https://developer.android.com/studio/releases/platform-tools
2. Extract to a folder (e.g., `C:\Users\YourName\Downloads\platform-tools`)
3. Update `ADB_PATH` in `.env`:
   ```
   ADB_PATH=C:\path\to\platform-tools\adb.exe
   ```

**Cost**: Free

---

### 6. **BluetoothCL.exe** (Optional - for Bluetooth Control)

**What it does**: Connect/disconnect Bluetooth devices via voice

**Steps**:
1. Download from http://www.nirsoft.net/utils/bluetoothcl.html
2. Extract to a folder
3. Update `BLUETOOTHCL_PATH` in `.env`:
   ```
   BLUETOOTHCL_PATH=C:\path\to\BluetoothCL.exe
   ```

**Cost**: Free

---

## Your `.env` File Template

```bash
# Picovoice
PICOVOICE_ACCESS_KEY=pk_XXXXXXXXXXXXXXXXXXXXXXXX

# Spotify
SPOTIFY_CLIENT_ID=abc123def456ghi789
SPOTIFY_CLIENT_SECRET=xyz789uvw456pqr123abc

# Cohere (optional)
COHERE_API_KEY=xxxxx-xxxxx-xxxxx-xxxxx

# Paths (update with your paths)
ADB_PATH=C:\Users\parth\Downloads\platform-tools\adb.exe
BLUETOOTHCL_PATH=C:\Users\parth\Downloads\bluetoothcl\BluetoothCL.exe
INFRA_MODEL_PATH=C:\Users\parth\Downloads\infra_en_windows_v3_0_0\infra_en_windows_v3_0_0.ppn
GOOGLE_CREDENTIALS_FILE=credentials.json
```

---

## Running the Application

```bash
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run the app
python main.py
```

**What happens**:
1. Face detection window opens
2. Listens for "infra" wakeword
3. Processes voice commands
4. Executes tasks (play music, send messages, etc.)

---

## Troubleshooting

### "Module not found: dotenv"
```bash
pip install python-dotenv
```

### "No module named 'cv2'"
```bash
pip install opencv-python
```

### "Picovoice AccessKey is required"
- Check `.env` file exists and `PICOVOICE_ACCESS_KEY` is set
- Verify the key is correct (no typos)

### "Spotify not initialized"
- Ensure `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET` are set
- Start playing music on Spotify first

### "Google Auth failed"
- Delete `token.pickle` if it exists
- Re-run to trigger browser auth flow
- Ensure `credentials.json` is in project root

---

## Security Best Practices

✅ **DO**:
- Store API keys in `.env` file (never in code)
- Add `.env` to `.gitignore` (already done)
- Use separate keys for dev/prod environments
- Rotate keys periodically
- Use strong, unique secrets

❌ **DON'T**:
- Commit `.env` or `credentials.json` to Git
- Share API keys in chat, email, or code reviews
- Use production keys for development
- Leave access keys in public repositories

---

## Support

For issues:
1. Check the [README.md](README.md) for general info
2. Verify all `.env` variables are set correctly
3. Check console output for specific error messages
4. Test individual features (Spotify, Google, etc.) separately

---

**Last Updated**: February 3, 2026
