import datetime
import difflib
import json
import os
import pickle
import platform
import re
import subprocess
import sys
import tempfile
import threading
import time
import urllib.parse
import webbrowser
from ctypes import cast, POINTER
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
import cv2
import numpy as np
import pvporcupine
import pyaudio
import pyttsx3
import screen_brightness_control as sbc
import speech_recognition as sr
import spotipy
from comtypes import CLSCTX_ALL
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from gtts import gTTS
from playsound import playsound
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from spotipy.oauth2 import SpotifyOAuth

CONTACTS_FILE = "contacts.json"
CONTACTS = {}

SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/contacts.readonly",
]

FACE_ENCODINGS_FILE = "known_faces.pkl"
FACE_PERMISSIONS = {
    "partha": ["all"],  # Full access
    "family": ["spotify", "volume", "brightness", "whatsapp"],
    "guest": ["youtube", "search", "time"]
}
FACE_RECOGNITION_ACTIVE = True

CURRENT_EXPRESSION = "no_face"
LAST_EXPRESSION_TIME = 0
ALERTS = []  # list of dicts: {"time": datetime, "message": str, "done": bool}
ALERT_LOCK = threading.Lock()

INFRA_MODEL_PATH = r"C:\Users\parth\Downloads\infra_en_windows_v3_0_0\infra_en_windows_v3_0_0.ppn"
ACCESS_KEY = os.getenv("PICOVOICE_ACCESS_KEY")

ADB_PATH = r"C:\Users\parth\Downloads\platform-tools-latest-windows\platform-tools\adb.exe"
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "http://127.0.0.1:8000/callback")

sp = None
try:
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope="user-modify-playback-state user-read-playback-state user-read-currently-playing"
    ))
except Exception as e:
    print("Warning: Spotify not initialized:", e)



LANGUAGES = {'en': {'sr': 'en-IN', 'gtts': 'en', 'name': 'English'}}

COMMAND_MAP = {
    'en': [

        ("sync google contacts", "sync_contacts"),
        ("update google contacts", "sync_contacts"),
        ("import google contact", "sync_contacts"),
        ("how do i look", "expression_status"),
        ("send whatsapp on pc to, send whatsapp from pc to", "wa_send_windows"),
        ("send whatsapp message on windows to", "wa_send_windows"),
        ("send whatsapp from pc to", "wa_send_windows"),
        ("send whatsapp on pc to", "wa_send_windows"),
        ("send whatsapp message to", "wa_send_message"),
        ("whatsapp message to", "wa_send_message"),
        ("send message on whatsapp to", "wa_send_message"),
        ("call on whatsapp", "wa_call"),
        ("whatsapp call", "wa_call"),
        ("send whatsapp message to", "wa_send_message"),
        ("whatsapp message to", "wa_send_message"),
        ("send message on whatsapp to", "wa_send_message"),
        ("call on whatsapp", "wa_call"),
        ("whatsapp call", "wa_call"),
        ("send whatsapp message to", "wa_send_message"),
        ("whatsapp message to", "wa_send_message"),
        ("send message on whatsapp to", "wa_send_message"),
        ("call on whatsapp", "wa_call"),
        ("whatsapp call", "wa_call"),
        ("open word", "open_word"),
        ("open excel", "open_excel"),
        ("open powerpoint", "open_powerpoint"),
        ("microsoft word", "open_word"),
        ("open power point", "open_powerpoint"),
        ("ms word", "open_word"),
        ("ms excel", "open_excel"),

        ("microsoft powerpoint", "open_powerpoint"),
        ("search google for", "search_google"),
        ("google search", "search_google"),
        ("open website", "open_website"),
        (" google search for", "search_google"),
        ("open web site", "open_website"),
        ("open site", "open_website"),
        ("site", "open_website"),
        ("i am infra, i'm infra, this is infra", "smalltalk_who_are_you"),
        ("how are you", "smalltalk_how_are_you"),
        ("how r u", "smalltalk_how_are_you"),
        ("how are u", "smalltalk_how_are_you"),
        ("tell me about you", "smalltalk_who_are_you"),
        ("who are you", "smalltalk_who_are_you"),
        ("what are you", "smalltalk_who_are_you"),
        ("thanks", "smalltalk_thanks"),
        ("thank you", "smalltalk_thanks"),
        ("happy birthday", "smalltalk_birthday"),
        ("congratulation", "smalltalk_congrats"),
        ("congratulations", "smalltalk_congrats"),
        ("congrats", "smalltalk_congrats"),

        (" microsoft store", "ms_store_open"),
        ("search store for", "ms_store_search"),
        ("install from store", "ms_store_install"),
        ("open store", "ms_store_open"),
        ("search microsoft store for", "ms_store_search"),
        ("install app from store", "ms_store_install"),
        ("shutdown", "shutdown"),
        ("shut down", "shutdown"),
        ("power off", "shutdown"),
        ("turn off computer", "shutdown"),
        ("remind me in", "add_alert"),
        ("set alert in", "add_alert"),
        ("set reminder in", "add_alert"),
        ("list alerts", "list_alerts"),
        ("my alerts", "list_alerts"),
        ("clear alerts", "clear_alerts"),
        ("delete alerts", "clear_alerts"),
        ("open whatsapp", "wa_desktop"),
        ("open whatsapp desktop", "wa_desktop"),
        ("whatsapp desktop", "wa_desktop"),
        ("open whatsapp web", "wa_web"),
        ("whatsapp web", "wa_web"),
        ("connect to wifi", "wifi_connect_voice"),
        ("connect to wi-fi", "wifi_connect_voice"),
        ("connect wifi", "wifi_connect_voice"),
        ("connect wi-fi", "wifi_connect_voice"),
        ("connect to wi fi", "wifi_connect_voice"),
        ("connect wi fi", "wifi_connect_voice"),
        ("connect to wifi", "wifi_connect_voice"),
        ("connect wifi", "wifi_connect_voice"),
        ("connect wifi to", "wifi_connect_voice"),

        ("calendar", "google_calendar"),
        ("my event", "google_calendar"),
        ("my next event", "google_calendar"),
        ("read events", "google_calendar"),
        ("turn on wifi", "wifi_on"),
        ("wifi on", "wifi_on"),
        ("enable wifi", "wifi_on"),
        ("turn off wifi", "wifi_off"),
        ("wifi off", "wifi_off"),
        ("disable wifi", "wifi_off"),
        ("connect to wifi", "wifi_connect"),
        ("disconnect wifi", "wifi_disconnect"),
        ("list bluetooth devices", "bt_list"),
        ("my bluetooth devices", "bt_list"),
        ("what bluetooth devices", "bt_list"),
        ("open bluetooth settings", "bt_settings"),
        ("connect to headset", "bt_connect_headset"),
        ("disconnect headset", "bt_disconnect_headset"),
        ("connect to speaker", "bt_connect_speaker"),
        ("disconnect speaker", "bt_disconnect_speaker"),
        ("connect new device", "bt_settings"),
        ("message|send sms to", "sms_contact"),
        ("add contact", "add_contact"),
        ("call", "call_contact"),
        ("volume up", "volume_up"),
        ("volume down", "volume_down"),
        ("set volume to", "set_volume"),
        ("make it louder", "volume_up"),
        ("make it softer", "volume_down"),
        ("play some music", "spotify_play_radio"),
        ("play something", "spotify_play_radio"),
        ("play next", "spotify_next"),
        ("next song", "spotify_next"),
        ("skip", "spotify_next"),
        ("previous song", "spotify_prev"),
        ("play previous", "spotify_prev"),
        ("go back", "spotify_prev"),
        ("pause music", "spotify_pause"),
        ("pause spotify", "spotify_pause"),
        ("pause song", "spotify_pause"),
        ("stop music", "spotify_pause"),
        ("stop playing", "spotify_pause"),
        ("resume music", "spotify_resume"),
        ("resume spotify", "spotify_resume"),
        ("resume song", "spotify_resume"),
        ("continue music", "spotify_resume"),
        ("shuffle on", "spotify_shuffle_on"),
        ("shuffle off", "spotify_shuffle_off"),
        ("repeat song", "spotify_repeat_one"),
        ("repeat on", "spotify_repeat_on"),
        ("repeat off", "spotify_repeat_off"),
        ("play top hits", "spotify_play_top"),
        ("play my favorite songs", "spotify_play_favorites"),
        ("play workout songs", "spotify_play_workout"),
        ("play classical music", "spotify_play_classical"),
        ("queue", "spotify_queue"),
        ("add to queue", "spotify_queue"),
        ("what is playing", "spotify_current"),
        ("what song is playing", "spotify_current"),
        ("what's playing", "spotify_current"),
        ("now playing", "spotify_current"),
        ("play artist", "spotify_play_artist"),
        ("play playlist", "spotify_play_playlist"),
        ("play genre", "spotify_play_genre"),
        ("play", "spotify_play"),
        ("set brightness to", "set_brightness"),
        ("adjust brightness to", "set_brightness"),
        ("brightness up", "brightness_up"),
        ("increase brightness", "brightness_up"),
        ("brightness down", "brightness_down"),
        ("decrease brightness", "brightness_down"),
        ("play on youtube", "yt_search"),
        ("search youtube", "yt_search"),
        ("search youtube for", "yt_search"),
        ("show videos for", "yt_search"),
        ("open youtube", "yt_search"),
        ("mute", "mute"),
        ("unmute", "unmute"),
        ("what time", "time"),
        ("tell me a joke", "joke"),
        ("joke", "joke"),
        ("time", "time"),
    ]
}

# Bluetooth configuration
BLUETOOTHCL_PATH = r"C:\Users\parth\Downloads\bluetoothcl\BluetoothCL.exe"
BT_MAPPING_FILE = r"C:\Users\parth\PycharmProjects\pythonProject8\bt_devices.json"
ON_WINDOWS = platform.system().lower() == "windows"


def load_bt_mapping():
    """Load saved Bluetooth device mappings from JSON file"""
    if os.path.exists(BT_MAPPING_FILE):
        try:
            with open(BT_MAPPING_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_bt_mapping(devices):
    """Save Bluetooth device mappings to JSON file"""
    with open(BT_MAPPING_FILE, 'w') as f:
        json.dump(devices, f, indent=2)


BLUETOOTH_DEVICES = load_bt_mapping()


def sync_contacts_from_google(max_contacts: int = 1500) -> str:
    """
    Fetch Google Contacts (names + phone numbers) and store in contacts.json.
    """
    load_contacts()  # ensure CONTACTS is loaded

    # Reuse your existing token.pickle / credentials flow
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    try:
        service = build("people", "v1", credentials=creds)
        results = service.people().connections().list(
            resourceName="people/me",
            pageSize=max_contacts,
            personFields="names,phoneNumbers",
        ).execute()  # <-- removed [0]
    except HttpError as err:
        print(err)
        return "Could not sync Google contacts."

    connections = results.get("connections", [])
    imported = 0

    for person in connections:
        names = person.get("names", [])
        phones = person.get("phoneNumbers", [])
        if not names or not phones:
            continue

        display_name = names[0].get("displayName")
        phone = phones[0]
        number = phone.get("value") or phone.get("canonicalForm")
        if not display_name or not number:
            continue

        key = display_name.strip().lower()
        CONTACTS[key] = number.strip()
        imported += 1

    save_contacts()
    return f"Imported {imported} contacts from Google."


def load_contacts():
    """Load contacts from JSON file into CONTACTS dict."""
    global CONTACTS
    if os.path.exists(CONTACTS_FILE):
        try:
            with open(CONTACTS_FILE, "r", encoding="utf-8") as f:
                CONTACTS = json.load(f)
        except Exception:
            CONTACTS = {}
    else:
        CONTACTS = {}


def save_contacts():
    """Save current CONTACTS dict to JSON file."""
    try:
        with open(CONTACTS_FILE, "w", encoding="utf-8") as f:
            json.dump(CONTACTS, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print("Failed to save contacts:", e)


def shutdown_pc():
    try:
        # Windows shutdown command, force close apps, 30 seconds delay
        subprocess.run("shutdown /s /t 30 /f", shell=True)
        return "Shutting down your computer in 30 seconds. Please save your work."
    except Exception as e:
        return f"Failed to shutdown computer: {e}"


def speak(text, lang_code='en', gender='female'):
    if not text:
        return
    lang_info = LANGUAGES.get(lang_code, LANGUAGES['en'])
    gtts_code = lang_info.get('gtts', 'en')
    try:
        tts = gTTS(text=text, lang=gtts_code)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            tts.save(fp.name)
            mp3_path = fp.name
        playsound(mp3_path)
        os.remove(mp3_path)
    except Exception as e:
        print("TTS error:", e)
        try:
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
        except Exception as e2:
            print("Fallback TTS error:", e2)


def listen(sr_lang='en-IN', timeout=8, phrase_time_limit=10):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎧 Listening...")
        r.adjust_for_ambient_noise(source, duration=0.4)
        try:
            audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        except sr.WaitTimeoutError:
            print("⏳ Listening timeout")
            return ""
    try:
        query = r.recognize_google(audio, language=sr_lang)
        print("🟢 Recognized:", query)
        return query
    except sr.UnknownValueError:
        print("❌ Could not understand.")
        return ""
    except sr.RequestError as e:
        print("⚠ Speech recognition unavailable:", e)
        return ""


# Add face recognition functions
def face_recognition_loop():
    """Background face detection + rough 'expression' (presence type)."""
    global FACE_RECOGNITION_ACTIVE, CURRENT_EXPRESSION, LAST_EXPRESSION_TIME

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    face_cascade = cv2.CascadeClassifier(cascade_path)

    if face_cascade.empty():
        print("Failed to load Haar cascade for face detection.")
        FACE_RECOGNITION_ACTIVE = False
        return

    while FACE_RECOGNITION_ACTIVE:
        ret, frame = cap.read()
        if not ret:
            time.sleep(0.1)
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(80, 80)
        )

        # Simple "expression" based on how many faces are visible
        if len(faces) == 0:
            CURRENT_EXPRESSION = "no_face"
        elif len(faces) == 1:
            CURRENT_EXPRESSION = "focused"
        else:
            CURRENT_EXPRESSION = "group"
        LAST_EXPRESSION_TIME = time.time()

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Show current expression text on screen
        cv2.putText(
            frame,
            f"Expr: {CURRENT_EXPRESSION}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2,
        )

        cv2.imshow("Infra AI - Face Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        time.sleep(0.03)

    cap.release()
    cv2.destroyAllWindows()


def describe_expression() -> str:
    """Return a user-friendly description of CURRENT_EXPRESSION."""
    if CURRENT_EXPRESSION == "no_face":
        return "I can't see you right now."
    if CURRENT_EXPRESSION == "focused":
        return "You look focused in front of the screen."
    if CURRENT_EXPRESSION == "group":
        return "I see more than one person in front of the camera."
    return "You look okay."


def extract_name_from_text(text: str) -> str:
    """
    Very simple name extractor for phrases like:
    'happy birthday Rahul', 'congratulations to Priya', 'congrats Rohit'.
    """
    if not text:
        return ""
    q = text.lower()
    # common prefixes to strip
    prefixes = [
        "happy birthday to",
        "happy birthday",
        "congratulations to",
        "congratulations",
        "congrats to",
        "congrats",
    ]
    for p in prefixes:
        if q.startswith(p):
            name = text[len(p):].strip()
            return name
    return ""


def add_contact(query):
    match = re.search(r'add contact ([\w ]+) (\+\d+)', query.lower())
    if match:
        name = match.group(1).strip().lower()
        number = match.group(2).strip()
        CONTACTS[name] = number
        return f"Contact '{name.title()}' added with number {number}."
    return "Say: 'add contact Alice +919876543210' to add new contact."


def ms_store_open() -> str:
    # Opens the Microsoft Store home page
    try:
        # Protocol works on modern Windows
        os.system("start ms-windows-store:")
        return "Opening Microsoft Store."
    except Exception as e:
        return f"Could not open Microsoft Store: {e}"


def ms_store_search_app(app_name: str) -> str:
    if not app_name.strip():
        return "Please say the app name to search in Microsoft Store."
    # Use search protocol
    try:
        # Encode spaces as %20
        query = app_name.strip().replace(" ", "%20")
        os.system(f"start ms-windows-store://search/?query={query}")
        return f"Searching Microsoft Store for {app_name}."
    except Exception as e:
        return f"Could not search Microsoft Store: {e}"


def ms_store_install_app(app_name: str) -> str:
    """
    Safer behavior: open search results and let you click Install.
    Full automatic installation via script is possible but not 100% reliable and
    can be risky, so this keeps you in control.
    """
    if not app_name.strip():
        return "Please say the app name you want to install from Microsoft Store."
    # Re‑use search function, user clicks Install
    msg = ms_store_search_app(app_name)
    return msg + " Please click Install on the app you want."


def alert_watcher():
    while True:
        now = datetime.now()
        with ALERT_LOCK:
            for alert in ALERTS:
                if not alert["done"] and now >= alert["time"]:
                    speak(f"Alert: {alert['message']}")
                    alert["done"] = True
        time.sleep(5)  # check every 5 seconds


def add_alert_from_speech(query):
    # Examples: "remind me in 10 minutes to drink water"
    #           "set alert in 1 hour to check oven"
    m = re.search(r'(remind me|set alert)\s+in\s+(\d+)\s+(seconds?|minutes?|hours?)\s*(.*)', query, re.I)
    if not m:
        return "Say: remind me in 10 minutes to drink water."

    amount = int(m.group(2))
    unit = m.group(3).lower()
    msg = m.group(4).strip() or "Reminder."

    delta = None
    if "second" in unit:
        delta = timedelta(seconds=amount)
    elif "minute" in unit:
        delta = timedelta(minutes=amount)
    elif "hour" in unit:
        delta = timedelta(hours=amount)
    else:
        return "Use seconds, minutes, or hours for alerts."

    when = datetime.now() + delta
    with ALERT_LOCK:
        ALERTS.append({"time": when, "message": msg, "done": False})

    return f"Alert set in {amount} {unit} for: {msg}"


def list_alerts():
    with ALERT_LOCK:
        if not ALERTS:
            return "You have no alerts set."
        lines = []
        for i, a in enumerate(ALERTS, 1):
            status = "done" if a["done"] else "pending"
            lines.append(f"{i}. {a['time'].strftime('%H:%M:%S')} - {a['message']} ({status})")
    return "Current alerts: " + " | ".join(lines)


def clear_alerts():
    with ALERT_LOCK:
        ALERTS.clear()
    return "All alerts cleared."


def whatsapp_send_message(query: str) -> str:
    # pattern: send whatsapp message to NAME MESSAGE...
    m = re.search(r"(?:send|whatsapp) message to (.+)", query.lower())
    if not m:
        return "Please say: send WhatsApp message to [name] [your message]."
    rest = m.group(1).strip()
    parts = rest.split(" ", 1)
    if len(parts) < 2:
        return "Please include the message text after the contact name."
    name, msg = parts[0].lower(), parts[1].strip()
    number = CONTACTS.get(name)
    if not number:
        return f"Contact {name} not found. Say add contact {name} number to add."

    try:
        cmd = f"\"{ADB_PATH}\" shell am start -a android.intent.action.SENDTO -d sms:{number} --es sms_body \"{msg}\""
        subprocess.run(cmd, shell=True)
        return f"Opening WhatsApp or SMS screen for {name} with your message. Please tap send on your phone."
    except Exception as e:
        return f"Could not send WhatsApp message: {e}"


def whatsapp_call_contact(query: str) -> str:
    # pattern: whatsapp call NAME / call on whatsapp NAME
    m = re.search(r"(?:whatsapp call|call on whatsapp) (.+)", query.lower())
    if not m:
        return "Please say: WhatsApp call [name]."
    name = m.group(1).strip().lower()
    number = CONTACTS.get(name)
    if not number:
        return f"Contact {name} not found. Say add contact {name} number to add."

    try:
        # This opens WhatsApp call UI for that number on Android if WhatsApp handles tel/wa links
        cmd = f"\"{ADB_PATH}\" shell am start -a android.intent.action.VIEW -d \"tel:{number}\""
        subprocess.run(cmd, shell=True)
        return f"Starting WhatsApp or phone call screen for {name}. Please confirm the call on your phone."
    except Exception as e:
        return f"Could not start WhatsApp call: {e}"


def open_word() -> str:
    try:
        # Works if WINWORD.EXE is on PATH or registered
        subprocess.Popen("start winword", shell=True)
        return "Opening Microsoft Word."
    except Exception as e:
        return f"Could not open Word: {e}"


def open_excel() -> str:
    try:
        subprocess.Popen("start excel", shell=True)
        return "Opening Microsoft Excel."
    except Exception as e:
        return f"Could not open Excel: {e}"


def open_powerpoint() -> str:
    try:
        subprocess.Popen("start powerpnt", shell=True)
        return "Opening Microsoft PowerPoint."
    except Exception as e:
        return f"Could not open PowerPoint: {e}"


def call_contact(query):
    match = re.search(r'call ([\w ]+)', query.lower())
    name = match.group(1).strip().lower() if match else ""
    number = CONTACTS.get(name)
    if not number:
        return f"Contact '{name}' not found. Say 'add contact [name] [number]' to add."
    try:
        result = os.system(f'"{ADB_PATH}" shell am start -a android.intent.action.CALL -d tel:{number}')
        return f"Calling {name.title()} at {number}."
    except Exception as e:
        return f"Failed to call {name.title()}: {e}"


def google_search(query: str) -> str:
    # Remove the command keywords to isolate the search term
    search_term = re.sub(r"^(search google for|google search for|google search)\s*", "", query, flags=re.I).strip()
    if not search_term:
        return "Please tell me what you want to search on Google."
    url = f"https://www.google.com/search?q={search_term.replace(' ', '+')}"
    webbrowser.open(url)
    return f"Searching Google for {search_term}."


def open_website(query: str) -> str:
    # Remove the command keywords first
    site = re.sub(
        r"^(open website|open web site|open site|open)\s*",
        "",
        query,
        flags=re.I,
    ).strip()

    if not site:
        return "Please specify the website you want to open."

    # If user said just a name like 'facebook', 'YouTube', etc.
    # map some common names to full URLs
    shortcuts = {
        "facebook": "https://www.facebook.com",
        "youtube": "https://www.youtube.com",
        "google": "https://www.google.com",
        "instagram": "https://www.instagram.com",
        "twitter": "https://twitter.com",
    }
    if site.lower() in shortcuts:
        url = shortcuts[site.lower()]
    else:
        # If it already looks like a domain (has a dot) but no scheme, add https://
        if "." in site and not site.startswith(("http://", "https://")):
            url = "https://" + site
        # If no dot, treat as a Google search instead of a domain
        elif "." not in site:
            url = "https://www.google.com/search?q=" + site.replace(" ", "+")
        else:
            url = site

    webbrowser.open(url)
    return f"Opening website {url}."


def sms_contact(query):
    match = re.search(r"(message|send sms to)\s*([\w ]+):?\s*(.*)", query.lower())
    name = match.group(2).strip().lower() if match else ""
    msg = match.group(3).strip() if match and match.group(3) else "Hello!"
    number = CONTACTS.get(name)
    if not number:
        return f"Contact '{name}' not found. Say 'add contact [name] [number]' to add."
    try:
        result = os.system(
            f'"{ADB_PATH}" shell am start -a android.intent.action.SENDTO -d sms:{number} --es sms_body "{msg}"')
        if result == 0:
            return f"SMS to {name.title()} ({number}): '{msg}'. Please confirm/send on your phone."
        else:
            return "SMS sending failed. Check your phone connection."
    except Exception as e:
        return f"Could not send SMS: {e}"


def control_brightness(action, value=None):
    try:
        current = sbc.get_brightness(display=0)
        current = current[0] if isinstance(current, list) else current
        step = 10
        if action == "set" and value is not None:
            if 0 <= value <= 100:
                sbc.set_brightness(value)
                return f"Brightness set to {value}%."
            return "Brightness value must be between 0 and 100."
        if action == "up":
            new_brightness = min(current + step, 100)
            sbc.set_brightness(new_brightness)
            return f"Brightness increased to {new_brightness}%."
        if action == "down":
            new_brightness = max(current - step, 0)
            sbc.set_brightness(new_brightness)
            return f"Brightness decreased to {new_brightness}%."
        return "Unknown brightness action."
    except Exception as e:
        return f"Brightness control error: {e}"


def get_default_volume():
    enumerator = AudioUtilities.GetDeviceEnumerator()
    devices = enumerator.EnumAudioEndpoints(0, 1)
    device = devices.Item(0)
    interface = device.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    return volume


def control_volume(action):
    try:
        volume = get_default_volume()
        current = volume.GetMasterVolumeLevelScalar()
        step = 0.2
        if action == "up":
            volume.SetMasterVolumeLevelScalar(min(current + step, 1.0), None)
        elif action == "down":
            volume.SetMasterVolumeLevelScalar(max(current - step, 0.0), None)
        elif action == "mute":
            volume.SetMute(1, None)
        elif action == "unmute":
            volume.SetMute(0, None)
        return f"Volume {action}."
    except Exception as e:
        return f"Volume control error: {e}"


def set_volume(percent):
    try:
        volume = get_default_volume()
        scalar = min(max(float(percent), 0), 100) / 100.0
        volume.SetMasterVolumeLevelScalar(scalar, None)
        return f"Volume set to {percent}%."
    except Exception as e:
        return f"Volume control error: {e}"


def get_google_calendar_events(max_events=5):
    creds = None
    # Use token.pickle to reuse credentials, creates on first run
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=max_events, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        speak("No upcoming events found in your Google Calendar.")
        return "No upcoming events found."
    detailed_events = []
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        summary = event.get('summary', "No Title")
        location = event.get('location', "No location")
        desc = event.get('description', "No description")
        text = f"Event: {summary}, at {start}. Location: {location}. Details: {desc}"
        detailed_events.append(text)
    spoken = "Next events: " + " -- ".join(detailed_events)
    speak(spoken)
    return "\n\n".join(detailed_events)


def wifi_toggle(on=True):
    interface = "Wi-Fi"
    cmd = f'netsh interface set interface name="{interface}" admin={"enabled" if on else "disabled"}'
    subprocess.run(cmd, shell=True)
    return f"Wi-Fi turned {'on' if on else 'off'}."


def wifi_connect(profile_or_ssid):
    cmd = f'netsh wlan connect name="{profile_or_ssid}"'
    subprocess.run(cmd, shell=True)
    return f"Connecting to Wi-Fi network: {profile_or_ssid}"


def wifi_disconnect():
    cmd = 'netsh wlan disconnect'
    subprocess.run(cmd, shell=True)
    return "Wi-Fi disconnected."


def normalize_phone_for_wa(raw: str) -> str:
    """Keep only digits, assume raw already includes country code."""
    return re.sub(r"\D", "", raw)


def find_best_contact(spoken_name: str, cutoff: float = 0.6) -> str:
    """Fuzzy‑match spoken name to CONTACTS keys."""
    load_contacts()
    if not spoken_name:
        return ""
    spoken = spoken_name.lower().strip()
    if spoken in CONTACTS:
        return spoken
    keys = list(CONTACTS.keys())
    best = difflib.get_close_matches(spoken, keys, n=1, cutoff=cutoff)
    return best[0] if best else ""


def whatsapp_send_windows_from_command(command: str) -> str:
    """
    Handle commands like:
      - send whatsapp on pc to sobuj good night
      - send whatsapp on pc to number 918327692524 good night
    Opens WhatsApp Desktop/Web with chat + pre‑filled message.
    """
    q = command.lower().strip()

    # 1) number pattern
    m_num = re.search(r"send whatsapp .* to number (\d+)\s+(.*)", q)
    if m_num:
        raw_number = m_num.group(1).strip()
        message = m_num.group(2).strip()
        return whatsapp_send_windows_to_number(raw_number, message)

    # 2) contact pattern
    m_ct = re.search(r"send whatsapp .* to ([a-zA-Z0-9_]+)\s+(.*)", q)
    if m_ct:
        contact_name = m_ct.group(1).strip()
        message = m_ct.group(2).strip()
        return whatsapp_send_windows_to_contact(contact_name, message)

    return ("Please say: 'send WhatsApp on PC to [name] [message]' "
            "or 'send WhatsApp on PC to number [phone] [message]'.")


def whatsapp_send_windows_to_contact(contact_name: str, message: str) -> str:
    """Send via saved contact (with fuzzy name)."""
    best = find_best_contact(contact_name)
    if not best:
        return (f"Contact '{contact_name}' not found. "
                f"Say 'add contact {contact_name} +91...' to add.")

    number = CONTACTS[best]
    wa_number = normalize_phone_for_wa(number)
    if not wa_number:
        return f"Stored number for {best} is invalid for WhatsApp."

    if not message.strip():
        url = f"https://wa.me/{wa_number}"
        webbrowser.open(url)
        return f"Opening WhatsApp chat with {best}. Please type your message."

    encoded_msg = urllib.parse.quote(message.strip())
    url = f"https://wa.me/{wa_number}?text={encoded_msg}"
    webbrowser.open(url)
    return f"Opening WhatsApp chat with {best} and filling your message."


def whatsapp_send_windows_to_number(raw_number: str, message: str) -> str:
    """Send to any phone number, without needing a saved contact."""
    wa_number = normalize_phone_for_wa(raw_number)
    if not wa_number:
        return "The phone number looks invalid for WhatsApp."

    if not message.strip():
        url = f"https://wa.me/{wa_number}"
        webbrowser.open(url)
        return f"Opening WhatsApp chat with {wa_number}. Please type your message."

    encoded_msg = urllib.parse.quote(message.strip())
    url = f"https://wa.me/{wa_number}?text={encoded_msg}"
    webbrowser.open(url)
    return f"Opening WhatsApp chat with {wa_number} and filling your message."


# ===== BLUETOOTH FUNCTIONS (FIXED) =====

def open_bt_settings():
    """Opens Bluetooth settings on Windows or Android"""
    if ON_WINDOWS:
        os.system("start ms-settings:bluetooth")
    else:
        os.system(f'"{ADB_PATH}" shell am start -a android.settings.BLUETOOTH_SETTINGS')
    return "Bluetooth settings opened."


def connect_bluetooth_device(name):
    """Connect to a Bluetooth device by nickname"""
    mac_addr = BLUETOOTH_DEVICES.get(name.lower())
    if not mac_addr:
        return f"No known Bluetooth device named '{name}'. Say 'map bluetooth devices' to set up nicknames."

    if ON_WINDOWS:
        if not os.path.exists(BLUETOOTHCL_PATH):
            return "Error: BluetoothCL.exe not found. Download from NirSoft website."

        try:
            cmd = f'"{BLUETOOTHCL_PATH}" /connect {mac_addr}'
            subprocess.run(cmd, shell=True, timeout=30)
            return f"Connecting to {name.title()} ({mac_addr})..."
        except subprocess.TimeoutExpired:
            return f"Connection to {name.title()} timed out. Please check Bluetooth is enabled."
        except Exception as e:
            return f"Failed to connect: {e}"
    else:
        open_bt_settings()
        return "Android cannot auto-connect via voice. Please select device in Bluetooth settings."


def disconnect_bluetooth_device(name):
    """Disconnect from a Bluetooth device by nickname"""
    mac_addr = BLUETOOTH_DEVICES.get(name.lower())
    if not mac_addr:
        return f"No known Bluetooth device named '{name}'. Say 'map bluetooth devices' to set up nicknames."

    if ON_WINDOWS:
        if not os.path.exists(BLUETOOTHCL_PATH):
            return "Error: BluetoothCL.exe not found. Download from NirSoft website."

        try:
            cmd = f'"{BLUETOOTHCL_PATH}" /disconnect {mac_addr}'
            subprocess.run(cmd, shell=True, timeout=10)
            return f"Disconnecting from {name.title()} ({mac_addr})..."
        except subprocess.TimeoutExpired:
            return f"Disconnection from {name.title()} timed out."
        except Exception as e:
            return f"Failed to disconnect: {e}"
    else:
        open_bt_settings()
        return "Android cannot auto-disconnect via voice. Please use Bluetooth settings."


def list_bluetooth_devices_windows():
    """List all paired Bluetooth devices using BluetoothCL.exe (NirSoft)."""
    if not os.path.exists(BLUETOOTHCL_PATH):
        return f"BluetoothCL.exe not found at: {BLUETOOTHCL_PATH}"

    try:
        print("🔍 Scanning Bluetooth devices (this may take a moment)...")
        result = subprocess.run(
            [BLUETOOTHCL_PATH],
            capture_output=True,
            text=True,
            timeout=30
        )
        mac_regex = r"([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})"
        device_lines = []
        for line in result.stdout.splitlines():
            if re.search(mac_regex, line):
                parts = line.split()
                if len(parts) >= 5:
                    mac = parts[0]
                    name = " ".join(parts[4:])
                    device_lines.append(f"{name} ({mac})")
        if device_lines:
            device_list = "; ".join(device_lines)
            return f"Your paired Bluetooth devices: {device_list}"
        else:
            print("DEBUG: OUTPUT FOLLOWS FOR DEBUGGING:")
            print(repr(result.stdout))  # See what BluetoothCL actually returned
            return "No paired Bluetooth devices found. Make sure Bluetooth is enabled and devices are paired."
    except Exception as e:
        return f"Failed to scan Bluetooth devices: {e}"


def list_and_map_bluetooth_devices():
    """Interactive setup: List devices and let user assign nicknames (robust/no file version)"""
    if not ON_WINDOWS:
        return "Bluetooth mapping via voice is only supported on Windows."
    if not os.path.exists(BLUETOOTHCL_PATH):
        return "BluetoothCL.exe not found. Download from NirSoft website."

    # 1. Speak and scan
    speak("Scanning Bluetooth devices. Please wait., ")
    print("🔍 Scanning Bluetooth devices (this may take up to 15 seconds)...")
    try:
        result = subprocess.run(
            [BLUETOOTHCL_PATH],
            cwd=os.path.dirname(BLUETOOTHCL_PATH),
            capture_output=True,
            text=True,
            timeout=30
        )
    except subprocess.TimeoutExpired:
        speak("Bluetooth scan timed out. Please enable Bluetooth and try again.", )
        return ("Bluetooth scan timed out. Please:\n"
                "1. Enable Bluetooth in Windows Settings\n"
                "2. Wait a moment and say 'map bluetooth devices' again")
    except Exception as e:
        speak("Failed to scan Bluetooth devices., en")
        return f"Scan failed: {e}"

    # 2. Parse devices from stdout (no file)
    macline = r"^([0-9A-Fa-f:-]{17})\s+(\S+)\s+(\S+)\s+(.+)$"
    devices = []
    for line in result.stdout.splitlines():
        match = re.match(macline, line)
        if match:
            mac = match.group(1)
            name = match.group(4).strip()
            devices.append((name, mac))

    if not devices:
        speak("No paired Bluetooth devices found., ")
        return "No devices found. Make sure devices are paired in Windows Settings."

    device_names = ", ".join(name for name, _ in devices)
    speak(f"Found {len(devices)}")
    speak(f"devices: {device_names}, lang-en")
    speak("Say 'add nickname for device name'. Example: add buds for OnePlus, ")

    # 3. Interactive mapping
    mapping_count = 0
    for _ in range(len(devices) + 2):
        command = listen(sr_lang='en-IN', timeout=10, phrase_time_limit=8)
        if not command:
            continue

        if any(word in command.lower() for word in ['done', 'finish', 'exit']):
            break

        match = re.search(r'add\s+([\w\s]+?)\s+for\s+([\w\d\s]+)', command.lower(), re.I)
        if match:
            nickname = match.group(1).strip()
            device_name = match.group(2).strip()
            for name, mac in devices:
                # Partial or fuzzy match logic:
                if device_name in name.lower() or name.lower() in device_name:
                    BLUETOOTH_DEVICES[nickname] = mac
                    save_bt_mapping(BLUETOOTH_DEVICES)
                    speak(f"Nickname '{nickname}' saved for {name}", "en")
                    mapping_count += 1
                    break
            else:
                speak(f"No device matching '{device_name}', en")
        else:
            speak("I didn't understand. Say: add nickname for device name, en")

    if mapping_count > 0:
        add_dynamic_bt_commands()
        return f"Bluetooth setup complete. Mapped {mapping_count} device(s). Say 'connect to [nickname]' to use."
    else:
        return "No devices were mapped."


def add_dynamic_bt_commands():
    """Dynamically add connect/disconnect commands for each mapped device"""
    for nickname in BLUETOOTH_DEVICES.keys():
        connect_phrase = f"connect to {nickname}"
        disconnect_phrase = f"disconnect {nickname}"

        if (connect_phrase, f"bt_connect_{nickname}") not in COMMAND_MAP['en']:
            COMMAND_MAP['en'].append((connect_phrase, f"bt_connect_{nickname}"))

        if (disconnect_phrase, f"bt_disconnect_{nickname}") not in COMMAND_MAP['en']:
            COMMAND_MAP['en'].append((disconnect_phrase, f"bt_disconnect_{nickname}"))


def get_wifi_profiles():
    """Return list of profile names from 'netsh wlan show profiles'."""
    result = subprocess.run(
        "netsh wlan show profiles",
        shell=True, capture_output=True, text=True
    )
    profiles = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if line.lower().startswith("all user profile"):
            # line like: All User Profile     : MONDAL_JIO
            parts = line.split(":", 1)
            if len(parts) == 2:
                profiles.append(parts[1].strip())
    return profiles


def find_best_profile(spoken_name, profiles, cutoff=0.6):
    if not spoken_name:
        return None

    spoken_norm = spoken_name.lower().strip()

    # Manual alias for tricky Unicode SSID
    if "ujjwal" in spoken_norm:
        for p in profiles:
            if "ＵＪＪＷＡＬ" in p:  # your exact full-width name
                return p

    norm_map = {}
    for p in profiles:
        norm = p.lower().replace("_", " ").replace("-", " ").strip()
        norm_map[norm] = p

    norm_keys = list(norm_map.keys())
    best = difflib.get_close_matches(spoken_norm, norm_keys, n=1, cutoff=cutoff)
    if not best:
        return None
    return norm_map[best[0]]


def wifi_connect_voice(query):
    """
    Voice Wi-Fi connect that works with all your profile types:
    MONDAL_JIO, Partha, OPPO A3 5G, ＵＪＪＷＡＬ, Ajay 4G, Jio True5G, etc.
    """
    match = re.search(r'connect\s+(?:to\s+)?wi[-\s]?fi\s+(.+)', query, re.I)
    spoken_name = match.group(1).strip() if match and match.group(1) else ""
    if not spoken_name:
        speak("Please say: 'connect to Wi-Fi' followed by the network name.")
        return "Please say: 'connect to Wi-Fi [network name]'."

    profiles = get_wifi_profiles()
    best_profile = find_best_profile(spoken_name, profiles)

    print("[DEBUG] Spoken Wi-Fi name:", repr(spoken_name))
    print("[DEBUG] Available profiles:", profiles)
    print("[DEBUG] Matched profile:", repr(best_profile))

    if not best_profile:
        speak("I couldn't find a similar Wi-Fi profile. Please try again or connect once from Windows Wi-Fi.")
        return f"No matching Wi-Fi profile found for '{spoken_name}'."

    cmd = f'netsh wlan connect name="{best_profile}"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    stdout = result.stdout.lower()
    print("[DEBUG] netsh stdout:", repr(result.stdout))
    print("[DEBUG] netsh stderr:", repr(result.stderr))

    if "connection request was completed successfully" in stdout or "successfully" in stdout:
        speak(f"Connected to Wi-Fi network {best_profile}.")
        return f"Connected to Wi-Fi network: {best_profile}"

    if "the profile" in stdout and "is not found" in stdout:
        speak(
            f"The Wi-Fi profile {best_profile} seems invalid. I'll open Wi-Fi settings so you can fix it.")
        os.system("start ms-settings:network-wifi")
        return f'The Wi-Fi profile "{best_profile}" was not found. Please check in Windows Settings.'

    if "interface" in stdout and ("is not" in stdout or "disabled" in stdout):
        speak("Wi-Fi is turned off or unavailable. Please enable Wi-Fi and try again.")
        return "Wi-Fi interface is disabled or not available. Please enable Wi-Fi."

    if "already connected" in stdout:
        speak(f"You are already connected to {best_profile}.")
        return f"Already connected to: {best_profile}"

    speak(
        f"Unable to connect to Wi-Fi {best_profile}. Please check in Windows Wi-Fi settings.")
    return f"Could not connect to Wi-Fi: {best_profile}. Check Windows Wi-Fi settings."


def open_whatsapp_desktop():
    """
    Try to open WhatsApp Desktop on Windows.
    Adjust the path/executable name if needed.
    """
    try:
        # Easiest if whatsapp.exe is on PATH or registered as an app
        subprocess.Popen(["cmd", "/C", "start", "whatsapp:"], shell=True)
        return "Opening WhatsApp Desktop."
    except Exception as e:
        return f"Could not open WhatsApp Desktop: {e}"


def open_whatsapp_web():
    """
    Open WhatsApp Web in default browser.
    """
    try:
        webbrowser.open("https://web.whatsapp.com")
        return "Opening WhatsApp Web in your browser."
    except Exception as e:
        return f"Could not open WhatsApp Web: {e}"


# ===== SPOTIFY FUNCTIONS =====

def get_active_device():
    try:
        devices = sp.devices()['devices']
        return devices[0]['id'] if devices else None
    except Exception:
        return None


def spotify_play(song):
    try:
        if not song.strip():
            return "Please say a song, artist, or playlist to play."
        results = sp.search(q=song, type='track', limit=1)
        if results['tracks']['items']:
            track_uri = results['tracks']['items'][0]['uri']
            did = get_active_device()
            if not did:
                return "No active Spotify device found."
            sp.start_playback(uris=[track_uri], device_id=did)
            return f"Playing '{song}' on Spotify."
        return f"Could not find '{song}' on Spotify."
    except Exception as e:
        return f"Could not play requested track on Spotify: {e}"


def spotify_play_radio():
    try:
        did = get_active_device()
        if not did:
            return "No active Spotify device found."
        sp.start_playback(device_id=did)
        return "Playing some music on Spotify."
    except Exception:
        return "Couldn't play Spotify radio."


def spotify_pause():
    try:
        sp.pause_playback()
        return "Paused Spotify."
    except Exception:
        return "Could not pause Spotify."


def spotify_resume():
    try:
        sp.start_playback()
        return "Resumed Spotify."
    except Exception:
        return "Could not resume Spotify."


def spotify_next():
    try:
        sp.next_track()
        return "Playing next song on Spotify."
    except Exception:
        return "Could not skip to next track."


def spotify_prev():
    try:
        sp.previous_track()
        return "Went back to previous song on Spotify."
    except Exception:
        return "Could not go to previous track."


def spotify_shuffle_on():
    try:
        sp.shuffle(True)
        return "Shuffle is now on."
    except Exception:
        return "Could not turn shuffle on."


def spotify_shuffle_off():
    try:
        sp.shuffle(False)
        return "Shuffle is now off."
    except Exception:
        return "Could not turn shuffle off."


def spotify_repeat_one():
    try:
        sp.repeat('track')
        return "Repeat is now set to this song."
    except Exception:
        return "Could not repeat the current song."


def spotify_repeat_on():
    try:
        sp.repeat('context')
        return "Repeat is now on."
    except Exception:
        return "Could not turn repeat on."


def spotify_repeat_off():
    try:
        sp.repeat('off')
        return "Repeat is now off."
    except Exception:
        return "Could not turn repeat off."


def spotify_current():
    try:
        curr = sp.current_playback()
        if curr and curr.get("item"):
            song = curr['item']['name']
            artist = curr['item']['artists'][0]['name']
            return f"Currently playing: {song} by {artist}."
        else:
            return "Nothing is currently playing."
    except Exception:
        return "Could not get current Spotify track."


def spotify_play_top():
    return spotify_play("Top Hits")


def spotify_play_favorites():
    return spotify_play("Your Top Songs")


def spotify_play_workout():
    return spotify_play("Workout")


def spotify_play_classical():
    return spotify_play("Classical Essentials")


def spotify_play_artist(query):
    match = re.search(r"play artist (.+)", query)
    artist = match.group(1) if match else ""
    return spotify_play(artist)


def spotify_play_playlist(query):
    match = re.search(r"play playlist (.+)", query)
    playlist = match.group(1) if match else ""
    return spotify_play(playlist)


def spotify_play_genre(query):
    match = re.search(r"play genre (.+)", query)
    genre = match.group(1) if match else ""
    return spotify_play(genre)


def spotify_queue(song):
    try:
        if not song.strip():
            return "Please say a song to queue."
        results = sp.search(q=song, type='track', limit=1)
        if results['tracks']['items']:
            track_uri = results['tracks']['items'][0]['uri']
            sp.add_to_queue(track_uri)
            return f"Queued '{song}' to Spotify."
        return "Could not find that song to queue."
    except Exception:
        return "Failed to add song to queue."


def play_youtube_song(song):
    url = f"https://www.youtube.com/results?search_query={song.replace(' ', '+')}" if song else "https://www.youtube.com"
    speak("Searching YouTube in your browser.", )
    webbrowser.open(url)
    return f"Opened YouTube search for '{song}' in your browser."


# ===== MAIN COMMAND HANDLER =====

def perform_task(query, lang_code='en'):
    q = query.lower().strip()
    command_map = COMMAND_MAP.get(lang_code[:2], COMMAND_MAP['en'])
    matched = None

    for phrase, intent in command_map:
        triggers = [p.strip() for p in phrase.split('|')]
        if any(t in q for t in triggers):
            matched = intent
            break

    if not matched:
        matched = q

    # Contact management
    if matched == "add_contact":
        return add_contact(q)
    if matched == "call_contact":
        return call_contact(q)
    if matched == "sms_contact":
        return sms_contact(q)
    if matched == "google_calendar":
        return get_google_calendar_events(3)
    # Volume control
    if matched == 'volume_up':
        return control_volume("up")
    if matched == 'volume_down':
        return control_volume("down")
    if matched == 'set_volume':
        match = re.search(r'set volume to (\d+)', q)
        if match:
            return set_volume(match.group(1))
        return "Please specify a volume level 0-100."
    if matched == 'mute':
        return control_volume("mute")
    if matched == 'unmute':
        return control_volume("unmute")

    # Brightness control
    if matched == 'set_brightness':
        match = re.search(r'(\d{1,3})\s*%?', q)
        if match:
            return control_brightness("set", int(match.group(1)))
        return "Specify a brightness value between 0-100."
    if matched == 'brightness_up':
        return control_brightness("up")
    if matched == 'brightness_down':
        return control_brightness("down")

    # Spotify controls
    if matched == 'spotify_play':
        song_match = re.search(r'play (.+?)( on spotify)?$', q, re.IGNORECASE)
        song = song_match.group(1) if song_match else ''
        return spotify_play(song)
    if matched == 'spotify_play_radio':
        return spotify_play_radio()
    if matched == 'spotify_pause':
        return spotify_pause()
    if matched == 'spotify_resume':
        return spotify_resume()
    if matched == 'spotify_next':
        return spotify_next()
    if matched == 'spotify_prev':
        return spotify_prev()
    if matched == 'spotify_current':
        return spotify_current()
    if matched == 'spotify_shuffle_on':
        return spotify_shuffle_on()
    if matched == 'spotify_shuffle_off':
        return spotify_shuffle_off()
    if matched == 'spotify_repeat_one':
        return spotify_repeat_one()
    if matched == 'spotify_repeat_on':
        return spotify_repeat_on()
    if matched == 'spotify_repeat_off':
        return spotify_repeat_off()
    if matched == 'spotify_play_top':
        return spotify_play_top()
    if matched == 'spotify_play_favorites':
        return spotify_play_favorites()
    if matched == 'spotify_play_workout':
        return spotify_play_workout()
    if matched == 'spotify_play_classical':
        return spotify_play_classical()
    if matched == 'spotify_play_artist':
        return spotify_play_artist(q)
    if matched == 'spotify_play_playlist':
        return spotify_play_playlist(q)
    if matched == 'spotify_play_genre':
        return spotify_play_genre(q)
    if matched == 'spotify_queue':
        match = re.search(r'queue (.+)', q)
        song = match.group(1) if match else ''
        return spotify_queue(song)
    if matched == "search_google":
        return google_search(query)

    if matched == "open_website":
        return open_website(query)
    if matched == "expression_status":
        return describe_expression()
    if matched == "sync_contacts":
        return sync_contacts_from_google()

    # YouTube
    if matched == 'yt_search':
        match = re.search(r'(youtube|search youtube for|show videos for|play on youtube)\s*(.*)', q)
        song = match.group(2).strip() if match else ''
        return play_youtube_song(song)
    # --- Small talk / identity responses ---
    if matched == "smalltalk_how_are_you":
        return "I am good, thank you for asking. How can I help you?"

    if matched == "smalltalk_who_are_you":
        return ("I am Infra, an AI assistant. "
                "I was created by AI and data engineer Partha Chakraborty.")

    if matched == "smalltalk_thanks":
        return "You are welcome."

    if matched == "smalltalk_birthday":
        name = extract_name_from_text(query)
        if name:
            return f"Happy birthday, {name}! Many many happy returns of the day."
        else:
            return "Happy birthday! Many many happy returns of the day."

    if matched == "smalltalk_congrats":
        name = extract_name_from_text(query)
        if name:
            return f"Congratulations, {name}! Wishing you more success ahead."
        else:
            return "Congratulations! Wishing you more success ahead."
    # Office apps
    if matched == "open_word":
        return open_word()
    if matched == "open_excel":
        return open_excel()
    if matched == "open_powerpoint":
        return open_powerpoint()
    if matched == "wa_send_message":
        return whatsapp_send_message(query)

    if matched == "wa_call":
        return whatsapp_call_contact(query)

    # Wi-Fi controls
    if "shutdown" in q or "shut down" in q or "power off" in q or "turn off computer" in q:
        return shutdown_pc()
    # Bluetooth mapping setup
    if "map bluetooth" in q or "setup bluetooth" in q:
        result = list_and_map_bluetooth_devices()
        add_dynamic_bt_commands()
        return result

    # Dynamic Bluetooth connect/disconnect
    for nickname, mac in BLUETOOTH_DEVICES.items():
        if f"connect to {nickname}" in q or f"connect {nickname}" in q:
            return connect_bluetooth_device(nickname)
        if f"disconnect {nickname}" in q or f"disconnect from {nickname}" in q:
            return disconnect_bluetooth_device(nickname)

    # Bluetooth device list
    if matched == "bt_list":
        return list_bluetooth_devices_windows()

    # Bluetooth settings
    if matched == "bt_settings":
        return open_bt_settings()
    if matched == "wifi_connect_voice":
        return wifi_connect_voice(query)
    if matched == "wifi_connect_voice":
        return wifi_connect_voice(query)
    if matched == "wa_desktop":
        return open_whatsapp_desktop()
    if matched == "wa_web":
        return open_whatsapp_web()
    if matched == "add_alert":
        return add_alert_from_speech(query)
    if matched == "list_alerts":
        return list_alerts()
    if matched == "clear_alerts":
        return clear_alerts()
    if matched == "wa_send_windows":
        return whatsapp_send_windows_from_command(query)

    # Microsoft Store controls
    if matched == "ms_store_open":
        return ms_store_open()

    if matched == "ms_store_search":
        # e.g. "search store for whatsapp"
        m = re.search(r"search (?:microsoft )?store for (.+)", q)
        app = m.group(1).strip() if m else ""
        return ms_store_search_app(app)

    if matched == "ms_store_install":
        # e.g. "install from store whatsapp"
        m = re.search(r"install (?:app )?from store (.+)", q)
        app = m.group(1).strip() if m else ""
        return ms_store_install_app(app)

    # Misc
    if matched == 'time':
        now = datetime.datetime.now().strftime("%I:%M %p")
        return f"The current time is {now}"
    if matched == 'joke':
        return "Why do programmers prefer dark mode? Because light attracts bugs!"

    return "Sorry, I didn't understand."


# ===== MAIN LOOP =====

ACTIVE_HOTWORDS = ['infra']


def main():
    global FACE_RECOGNITION_ACTIVE
    global FACE_RECOGNITION_ACTIVE
    load_contacts()
    lang_code = 'en'
    sr_lang = LANGUAGES[lang_code]['sr']
    ai_gender = 'female'

    # Load saved Bluetooth mappings and restore commands
    add_dynamic_bt_commands()

    # Start alert watcher thread
    watcher_thread = threading.Thread(target=alert_watcher, daemon=True)
    watcher_thread.start()

    # Start face detection thread (no training / identity)
    face_thread = threading.Thread(target=face_recognition_loop, daemon=True)
    face_thread.start()

    porcupine = None
    try:
        if ACCESS_KEY:
            porcupine = pvporcupine.create(
                access_key=ACCESS_KEY,
                keyword_paths=[INFRA_MODEL_PATH]
            )
    except Exception as e:
        print("Wakeword engine setup failed:", e)
        speak("Wakeword engine failed. Please check configuration.", lang_code, ai_gender)

    if porcupine:
        pa = pyaudio.PyAudio()
        audio_stream = pa.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length
        )

        print(f"Say {', '.join(ACTIVE_HOTWORDS)} to activate.")
        print("Face detection ACTIVE - window will open.")
        speak(f"I'm always listening for {', '.join(ACTIVE_HOTWORDS)}. Face detection enabled.")

        try:
            while True:
                pcm = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
                pcm = np.frombuffer(pcm, dtype=np.int16).tolist()

                keyword_index = porcupine.process(pcm)
                if keyword_index >= 0:
                    wakeword = ACTIVE_HOTWORDS[keyword_index]
                    print(f"Wakeword '{wakeword}' detected!")
                    speak("yes??")

                    command = listen(sr_lang=sr_lang)
                    if not command:
                        continue

                    command_low = command.lower().strip()

                    if any(token in command_low for token in ['exit', 'stop', 'quit']):
                        speak("Goodbye!")
                        break

                    result = perform_task(command, lang_code)
                    if result:
                        speak(result)
                    else:
                        print("No action taken or empty input.")

        finally:
            FACE_RECOGNITION_ACTIVE = False
            audio_stream.stop_stream()
            audio_stream.close()
            pa.terminate()
            porcupine.delete()
            cv2.destroyAllWindows()
    else:
        print("Wakeword disabled (no valid ACCESS_KEY). Face detection ACTIVE - running in background.")
        speak("Wakeword is disabled. Face detection is running.", lang_code, ai_gender)
        try:
            while True:
                time.sleep(5)
        except KeyboardInterrupt:
            print("Exiting.")
            FACE_RECOGNITION_ACTIVE = False
            cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
