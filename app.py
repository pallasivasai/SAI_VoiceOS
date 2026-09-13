"""
=========================================================
                 SAI VOICE OS
=========================================================

VOICE ONLY ACCESSIBILITY OS

STREAMLIT CLOUD
----------------
Voice input
Browser TTS
Internet
Google Search
YouTube
Wikipedia
Weather
Calculator
PDF / TXT / DOCX
GitHub

WINDOWS LOCAL
----------------
Microphone
TTS
Notepad
Calculator
Chrome
YouTube
Google
WhatsApp
Screenshot
Local Files
Music
Notes
Shutdown / Restart

NO TEXT COMMAND INPUT
=========================================================
"""

import os
import io
import re
import json
import base64
import random
import datetime
import webbrowser
import urllib.parse
import urllib.request
import subprocess
import tempfile
import platform

# =========================================================
# OPTIONAL LIBRARIES
# =========================================================

try:
    import streamlit as st
except ImportError:
    st = None

try:
    import speech_recognition as sr
except ImportError:
    sr = None

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

try:
    import pyautogui
except ImportError:
    pyautogui = None

try:
    import wikipedia
except ImportError:
    wikipedia = None

try:
    import requests
except ImportError:
    requests = None

try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None

try:
    from docx import Document
except ImportError:
    Document = None


# =========================================================
# MODE DETECTION
# =========================================================

STREAMLIT_MODE = st is not None

WINDOWS_MODE = (
    platform.system().lower() == "windows"
)


# =========================================================
# CONFIG
# =========================================================

APP_NAME = "SAI Voice OS"

GITHUB_USERNAME = os.getenv(
    "GITHUB_USERNAME",
    ""
)

GITHUB_TOKEN = os.getenv(
    "GITHUB_TOKEN",
    "" 
)


# =========================================================
# WINDOWS TTS
# =========================================================

tts_engine = None


def initialize_windows_tts():

    global tts_engine

    if pyttsx3 is None:
        return

    try:

        tts_engine = pyttsx3.init()

        voices = tts_engine.getProperty(
            "voices"
        )

        if voices:

            tts_engine.setProperty(
                "voice",
                voices[0].id
            )

        tts_engine.setProperty(
            "rate",
            150
        )

        tts_engine.setProperty(
            "volume",
            1.0
        )

    except Exception:

        tts_engine = None


# =========================================================
# WINDOWS SPEAK
# =========================================================

def speak_windows(text):

    if not text:
        return

    print(
        f"SAI: {text}"
    )

    if tts_engine is None:
        return

    try:

        tts_engine.say(text)
        tts_engine.runAndWait()

    except Exception as e:

        print(
            "TTS error:",
            e
        )


# =========================================================
# CLOUD BROWSER SPEAK
# =========================================================

def speak_cloud(text):

    if not text:
        return

    if not STREAMLIT_MODE:
        return

    javascript_text = json.dumps(
        str(text)
    )

    html = f"""
    <script>

        const message = {javascript_text};

        function speakMessage() {{

            if (
                "speechSynthesis"
                in window
            ) {{

                window.speechSynthesis.cancel();

                const utterance =
                    new SpeechSynthesisUtterance(
                        message
                    );

                utterance.lang = "en-IN";

                utterance.rate = 0.95;

                utterance.pitch = 1.0;

                utterance.volume = 1.0;

                window.speechSynthesis.speak(
                    utterance
                );
            }}

        }}

        speakMessage();

    </script>
    """

    st.components.v1.html(
        html,
        height=1
    )


# =========================================================
# UNIVERSAL SPEAK
# =========================================================

def speak(text):

    if not text:
        return

    if STREAMLIT_MODE:

        speak_cloud(text)

    else:

        speak_windows(text)


# =========================================================
# TIME
# =========================================================

def get_time():

    current_time = datetime.datetime.now().strftime(
        "%I:%M %p"
    )

    return (
        f"The current time is "
        f"{current_time}."
    )


# =========================================================
# DATE
# =========================================================

def get_date():

    now = datetime.datetime.now()

    return (
        f"Today is "
        f"{now.day} "
        f"{now.strftime('%B')} "
        f"{now.year}."
    )


# =========================================================
# CALCULATOR
# =========================================================

def calculate(expression):

    try:

        expression = expression.lower()

        expression = expression.replace(
            "multiplied by",
            "*"
        )

        expression = expression.replace(
            "divided by",
            "/"
        )

        expression = expression.replace(
            "times",
            "*"
        )

        expression = expression.replace(
            "plus",
            "+"
        )

        expression = expression.replace(
            "minus",
            "-"
        )

        expression = re.sub(
            r"[^0-9+\-*/().% ]",
            "",
            expression
        )

        if not expression.strip():

            return (
                "I could not understand "
                "the calculation."
            )

        result = eval(
            expression,
            {
                "__builtins__": {}
            },
            {}
        )

        return (
            f"The answer is {result}."
        )

    except Exception:

        return (
            "I could not calculate that."
        )


# =========================================================
# OPEN URL
# =========================================================

def open_url(url, spoken_name):

    if STREAMLIT_MODE:

        # Open from user's browser.
        # Popup blockers may prevent a new tab,
        # so navigate the parent browser if needed.

        html = f"""
        <script>

            const url = {json.dumps(url)};

            try {{

                window.open(
                    url,
                    "_blank"
                );

            }} catch (error) {{

                window.parent.location.href =
                    url;

            }}

        </script>
        """

        st.components.v1.html(
            html,
            height=1
        )

    else:

        webbrowser.open(
            url
        )

    return (
        f"Opening {spoken_name}."
    )


# =========================================================
# YOUTUBE
# =========================================================

def open_youtube():

    return open_url(
        "https://www.youtube.com",
        "YouTube"
    )


# =========================================================
# GOOGLE
# =========================================================

def open_google():

    return open_url(
        "https://www.google.com",
        "Google"
    )


# =========================================================
# GOOGLE SEARCH
# =========================================================

def google_search(query):

    url = (
        "https://www.google.com/search?q="
        + urllib.parse.quote(query)
    )

    return open_url(
        url,
        f"Google search for {query}"
    )


# =========================================================
# YOUTUBE SEARCH
# =========================================================

def youtube_search(query):

    url = (
        "https://www.youtube.com/results?"
        "search_query="
        + urllib.parse.quote(query)
    )

    return open_url(
        url,
        f"YouTube search for {query}"
    )


# =========================================================
# WIKIPEDIA
# =========================================================

def wikipedia_search(query):

    if wikipedia is None:

        return (
            "Wikipedia is not available."
        )

    try:

        result = wikipedia.summary(
            query,
            sentences=3
        )

        return result

    except Exception:

        return (
            "I could not find that "
            "on Wikipedia."
        )


# =========================================================
# WEATHER
# =========================================================

def get_weather(city):

    try:

        city_encoded = urllib.parse.quote(
            city
        )

        url = (
            f"https://wttr.in/"
            f"{city_encoded}"
            f"?format=j1"
        )

        request = urllib.request.Request(
            url,
            headers={
                "User-Agent":
                    "Mozilla/5.0"
            }
        )

        response = urllib.request.urlopen(
            request,
            timeout=10
        )

        data = json.loads(
            response.read().decode()
        )

        current = data[
            "current_condition"
        ][0]

        temperature = current[
            "temp_C"
        ]

        description = current[
            "weatherDesc"
        ][0]["value"]

        return (
            f"The current temperature "
            f"in {city} is "
            f"{temperature} degrees "
            f"Celsius with "
            f"{description}."
        )

    except Exception:

        return (
            "Sorry, I could not "
            "fetch the weather."
        )


# =========================================================
# DOCUMENT READER
# =========================================================

def read_pdf_bytes(data):

    if PdfReader is None:

        return (
            "PDF reader is not installed."
        )

    try:

        reader = PdfReader(
            io.BytesIO(data)
        )

        text = []

        for page_number, page in enumerate(
            reader.pages,
            start=1
        ):

            page_text = (
                page.extract_text()
                or ""
            )

            if page_text.strip():

                text.append(
                    f"Page {page_number}. "
                    f"{page_text}"
                )

        return "\n".join(text)

    except Exception as e:

        return (
            f"Could not read PDF. {e}"
        )


def read_txt_bytes(data):

    try:

        return data.decode(
            "utf-8",
            errors="ignore"
        )

    except Exception:

        return (
            "Could not read text file."
        )


def read_docx_bytes(data):

    if Document is None:

        return (
            "Word document reader "
            "is not installed."
        )

    temp_path = None

    try:

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".docx"
        ) as temp:

            temp.write(data)

            temp_path = temp.name

        document = Document(
            temp_path
        )

        paragraphs = []

        for paragraph in document.paragraphs:

            if paragraph.text.strip():

                paragraphs.append(
                    paragraph.text
                )

        return "\n".join(
            paragraphs
        )

    except Exception:

        return (
            "Could not read the "
            "Word document."
        )

    finally:

        if temp_path:

            try:

                os.unlink(temp_path)

            except Exception:

                pass


def read_document(
    filename,
    data
):

    extension = os.path.splitext(
        filename
    )[1].lower()

    if extension == ".pdf":

        return read_pdf_bytes(
            data
        )

    if extension == ".txt":

        return read_txt_bytes(
            data
        )

    if extension == ".docx":

        return read_docx_bytes(
            data
        )

    return (
        "This document format "
        "is not supported."
    )


# =========================================================
# GITHUB HEADERS
# =========================================================

def github_headers():

    headers = {
        "Accept":
            "application/vnd.github+json"
    }

    if GITHUB_TOKEN:

        headers[
            "Authorization"
        ] = (
            f"Bearer {GITHUB_TOKEN}"
        )

    return headers


# =========================================================
# GITHUB REPOSITORIES
# =========================================================

def github_repositories():

    if requests is None:

        return []

    if not GITHUB_USERNAME:

        return []

    try:

        url = (
            "https://api.github.com/users/"
            f"{GITHUB_USERNAME}/repos"
        )

        response = requests.get(
            url,
            headers=github_headers(),
            timeout=10
        )

        if response.status_code != 200:

            return []

        data = response.json()

        return [
            repo["name"]
            for repo in data
        ]

    except Exception:

        return []


# =========================================================
# GITHUB FILE LIST
# =========================================================

def github_files(
    repository,
    path=""
):

    if requests is None:

        return []

    if not GITHUB_USERNAME:

        return []

    try:

        url = (
            "https://api.github.com/repos/"
            f"{GITHUB_USERNAME}/"
            f"{repository}/contents/"
            f"{path}"
        )

        response = requests.get(
            url,
            headers=github_headers(),
            timeout=10
        )

        if response.status_code != 200:

            return []

        return response.json()

    except Exception:

        return []


# =========================================================
# GITHUB READ FILE
# =========================================================

def github_read_file(
    repository,
    path
):

    if requests is None:

        return None

    try:

        url = (
            "https://api.github.com/repos/"
            f"{GITHUB_USERNAME}/"
            f"{repository}/contents/"
            f"{path}"
        )

        response = requests.get(
            url,
            headers=github_headers(),
            timeout=10
        )

        if response.status_code != 200:

            return None

        data = response.json()

        if data.get(
            "encoding"
        ) == "base64":

            content = base64.b64decode(
                data["content"]
            )

            return content.decode(
                "utf-8",
                errors="ignore"
            )

        return data.get(
            "content",
            ""
        )

    except Exception:

        return None


# =========================================================
# GITHUB UPLOAD
# =========================================================

def github_upload(
    repository,
    path,
    content
):

    if requests is None:

        return False

    if not GITHUB_TOKEN:

        return False

    try:

        encoded = base64.b64encode(
            content
        ).decode()

        url = (
            "https://api.github.com/repos/"
            f"{GITHUB_USERNAME}/"
            f"{repository}/contents/"
            f"{path}"
        )

        existing = requests.get(
            url,
            headers=github_headers(),
            timeout=10
        )

        payload = {
            "message":
                "Uploaded by SAI Voice OS",
            "content":
                encoded
        }

        if existing.status_code == 200:

            old_data = (
                existing.json()
            )

            payload["sha"] = (
                old_data["sha"]
            )

        response = requests.put(
            url,
            headers=github_headers(),
            json=payload,
            timeout=15
        )

        return response.status_code in [
            200,
            201
        ]

    except Exception:

        return False


# =========================================================
# WINDOWS APPLICATIONS
# =========================================================

def windows_open_application(
    app
):

    if not WINDOWS_MODE:

        return (
            "That application is "
            "available on your "
            "Windows computer."
        )

    app = app.lower()

    try:

        if "notepad" in app:

            subprocess.Popen(
                ["notepad.exe"]
            )

            return (
                "Opening Notepad."
            )

        if "calculator" in app:

            subprocess.Popen(
                ["calc.exe"]
            )

            return (
                "Opening Calculator."
            )

        if (
            "chrome" in app
            or "browser" in app
        ):

            subprocess.Popen(
                [
                    "cmd",
                    "/c",
                    "start",
                    "chrome"
                ]
            )

            return (
                "Opening Chrome."
            )

        if "explorer" in app:

            subprocess.Popen(
                ["explorer.exe"]
            )

            return (
                "Opening File Explorer."
            )

    except Exception:

        return (
            "I could not open "
            "that application."
        )

    return (
        "That application is "
        "not configured yet."
    )


# =========================================================
# WINDOWS WHATSAPP
# =========================================================

def open_whatsapp():

    if WINDOWS_MODE:

        try:

            subprocess.Popen(
                [
                    "cmd",
                    "/c",
                    "start",
                    "whatsapp:"
                ]
            )

            return (
                "Opening WhatsApp."
            )

        except Exception:

            pass

    return open_url(
        "https://web.whatsapp.com",
        "WhatsApp Web"
    )


# =========================================================
# WINDOWS SCREENSHOT
# =========================================================

def windows_screenshot():

    if not WINDOWS_MODE:

        return (
            "Screenshot is available "
            "when SAI Voice OS is running "
            "on your Windows computer."
        )

    if pyautogui is None:

        return (
            "Screenshot support "
            "is not installed."
        )

    try:

        pictures = os.path.expanduser(
            "~/Pictures"
        )

        os.makedirs(
            pictures,
            exist_ok=True
        )

        filename = (
            "SAI_Screenshot_"
            + datetime.datetime.now().strftime(
                "%Y%m%d_%H%M%S"
            )
            + ".png"
        )

        path = os.path.join(
            pictures,
            filename
        )

        image = pyautogui.screenshot()

        image.save(path)

        return (
            "Screenshot taken "
            "successfully."
        )

    except Exception:

        return (
            "I could not take "
            "the screenshot."
        )


# =========================================================
# WINDOWS LOCAL FILES
# =========================================================

def get_local_files():

    if not WINDOWS_MODE:

        return []

    documents = os.path.expanduser(
        "~/Documents"
    )

    try:

        return os.listdir(
            documents
        )

    except Exception:

        return []


# =========================================================
# READ LOCAL FILE
# =========================================================

def read_local_file(filename):

    if not WINDOWS_MODE:

        return (
            "Local files are available "
            "when SAI Voice OS is running "
            "on your Windows computer."
        )

    documents = os.path.expanduser(
        "~/Documents"
    )

    path = os.path.join(
        documents,
        filename
    )

    if not os.path.exists(path):

        return (
            "I could not find that file "
            "in your Documents folder."
        )

    try:

        extension = os.path.splitext(
            filename
        )[1].lower()

        if extension == ".txt":

            with open(
                path,
                "r",
                encoding="utf-8",
                errors="ignore"
            ) as file:

                return file.read()

        if extension == ".pdf":

            with open(
                path,
                "rb"
            ) as file:

                return read_pdf_bytes(
                    file.read()
                )

        if extension == ".docx":

            with open(
                path,
                "rb"
            ) as file:

                return read_docx_bytes(
                    file.read()
                )

        return (
            "I can currently read "
            "PDF, TXT and DOCX files."
        )

    except Exception:

        return (
            "I could not read "
            "that file."
        )


# =========================================================
# WINDOWS NOTES
# =========================================================

def save_local_note(note):

    if not WINDOWS_MODE:

        return (
            "Notes are available "
            "in Windows local mode."
        )

    try:

        desktop = os.path.expanduser(
            "~/Desktop"
        )

        os.makedirs(
            desktop,
            exist_ok=True
        )

        path = os.path.join(
            desktop,
            "SAI_Notes.txt"
        )

        timestamp = datetime.datetime.now().strftime(
            "%Y-%m-%d %H:%M"
        )

        with open(
            path,
            "a",
            encoding="utf-8"
        ) as file:

            file.write(
                f"[{timestamp}] "
                f"{note}\n"
            )

        return (
            "Your note has been "
            "saved to the desktop."
        )

    except Exception:

        return (
            "I could not save "
            "the note."
        )


# =========================================================
# WINDOWS MICROPHONE
# =========================================================

def listen_windows():

    if sr is None:

        return None

    recognizer = sr.Recognizer()

    try:

        with sr.Microphone() as source:

            print(
                "Listening..."
            )

            recognizer.adjust_for_ambient_noise(
                source,
                duration=0.5
            )

            audio = recognizer.listen(
                source,
                timeout=8,
                phrase_time_limit=12
            )

        print(
            "Recognizing..."
        )

        command = (
            recognizer
            .recognize_google(
                audio,
                language="en-IN"
            )
        )

        return command.lower()

    except sr.UnknownValueError:

        speak(
            "Sorry, I could not "
            "understand you."
        )

    except sr.WaitTimeoutError:

        pass

    except sr.RequestError:

        speak(
            "Speech recognition "
            "service is unavailable."
        )

    except Exception as e:

        print(
            "Microphone error:",
            e
        )

    return None


# =========================================================
# EXTRACT QUERY
# =========================================================

def remove_prefix(
    command,
    prefixes
):

    for prefix in prefixes:

        if command.startswith(prefix):

            return command[
                len(prefix):
            ].strip()

    return ""


# =========================================================
# COMMAND ENGINE
# =========================================================

def process_command(command):

    if not command:

        return (
            "I did not hear a command."
        )


    command = command.lower().strip()


    # -----------------------------------------------------
    # EXIT
    # -----------------------------------------------------

    if command in [
        "exit",
        "quit",
        "stop",
        "go offline",
        "goodbye"
    ]:

        return "__EXIT__"


    # -----------------------------------------------------
    # TIME
    # -----------------------------------------------------

    if (
        "what time" in command
        or command == "time"
    ):

        return get_time()


    # -----------------------------------------------------
    # DATE
    # -----------------------------------------------------

    if (
        "what is the date" in command
        or command == "date"
    ):

        return get_date()


    # -----------------------------------------------------
    # YOUTUBE
    # -----------------------------------------------------

    if any(
        phrase in command
        for phrase in [
            "open youtube",
            "launch youtube",
            "start youtube"
        ]
    ):

        return open_youtube()


    # -----------------------------------------------------
    # GOOGLE
    # -----------------------------------------------------

    if any(
        phrase in command
        for phrase in [
            "open google",
            "launch google",
            "start google"
        ]
    ):

        return open_google()


    # -----------------------------------------------------
    # GOOGLE SEARCH
    # -----------------------------------------------------

    query = remove_prefix(
        command,
        [
            "search google for",
            "search google",
            "google search for"
        ]
    )

    if query:

        return google_search(
            query
        )


    # -----------------------------------------------------
    # YOUTUBE SEARCH
    # -----------------------------------------------------

    query = remove_prefix(
        command,
        [
            "search youtube for",
            "search youtube",
            "play on youtube",
            "play youtube"
        ]
    )

    if query:

        return youtube_search(
            query
        )


    # -----------------------------------------------------
    # WIKIPEDIA
    # -----------------------------------------------------

    query = remove_prefix(
        command,
        [
            "wikipedia",
            "search wikipedia for"
        ]
    )

    if query:

        return wikipedia_search(
            query
        )


    # -----------------------------------------------------
    # WEATHER
    # -----------------------------------------------------

    if "weather" in command:

        city = "Guntur"

        match = re.search(
            r"weather(?:\s+in)?\s+(.+)",
            command
        )

        if match:

            city = match.group(
                1
            ).strip()

        return get_weather(
            city
        )


    # -----------------------------------------------------
    # CALCULATOR
    # -----------------------------------------------------

    if command.startswith(
        "calculate"
    ):

        expression = command[
            len("calculate"):
        ].strip()

        return calculate(
            expression
        )


    if (
        "open calculator"
        in command
        or
        "open the calculator"
        in command
    ):

        if WINDOWS_MODE:

            return windows_open_application(
                "calculator"
            )

        return (
            "The calculator is "
            "available on your Windows "
            "computer."
        )


    # -----------------------------------------------------
    # NOTEPAD
    # -----------------------------------------------------

    if (
        "open notepad"
        in command
    ):

        return windows_open_application(
            "notepad"
        )


    # -----------------------------------------------------
    # CHROME
    # -----------------------------------------------------

    if (
        "open chrome"
        in command
    ):

        return windows_open_application(
            "chrome"
        )


    # -----------------------------------------------------
    # WHATSAPP
    # -----------------------------------------------------

    if (
        "open whatsapp"
        in command
    ):

        return open_whatsapp()


    # -----------------------------------------------------
    # SCREENSHOT
    # -----------------------------------------------------

    if (
        "take screenshot"
        in command
        or
        command == "screenshot"
    ):

        return windows_screenshot()


    # -----------------------------------------------------
    # LOCAL FILES
    # -----------------------------------------------------

    if any(
        phrase in command
        for phrase in [
            "list my files",
            "show my files",
            "list files",
            "show files",
            "what files do i have"
        ]
    ):

        files = get_local_files()

        if not files:

            return (
                "I could not find any "
                "files in your Documents folder."
            )

        readable_files = files[:10]

        return (
            f"I found {len(files)} files. "
            f"The first files are "
            + ", ".join(
                readable_files
            )
        )


    # -----------------------------------------------------
    # READ LOCAL FILE
    # -----------------------------------------------------

    match = re.search(
        r"(?:read|open)\s+(?:file\s+)?(.+)",
        command
    )

    if match:

        filename = match.group(
            1
        ).strip()

        # Don't interpret normal commands as filenames
        if not filename.startswith(
            (
                "youtube",
                "google",
                "calculator",
                "notepad",
                "whatsapp"
            )
        ):

            return read_local_file(
                filename
            )


    # -----------------------------------------------------
    # GITHUB REPOSITORIES
    # -----------------------------------------------------

    if (
        "list github repositories"
        in command
        or
        "show my github repositories"
        in command
        or
        "my github repositories"
        in command
    ):

        repos = (
            github_repositories()
        )

        if not repos:

            return (
                "I could not retrieve "
                "your GitHub repositories."
            )

        return (
            "Your GitHub repositories are "
            + ", ".join(repos)
        )


    # -----------------------------------------------------
    # GITHUB FILES
    # -----------------------------------------------------

    match = re.search(
        r"(?:list|show)\s+files\s+in\s+github\s+(.+)",
        command
    )

    if match:

        repository = match.group(
            1
        ).strip()

        files = github_files(
            repository
        )

        if not files:

            return (
                "I could not find files "
                "in that repository."
            )

        names = []

        for item in files[:10]:

            names.append(
                item.get(
                    "name",
                    "unknown"
                )
            )

        return (
            "The files are "
            + ", ".join(names)
        )


    # -----------------------------------------------------
    # UNKNOWN
    # -----------------------------------------------------

    return (
        "I do not understand that "
        "command yet."
    )


# =========================================================
# CLOUD VOICE PROCESSING
# =========================================================

def process_cloud_audio(
    audio_bytes
):

    if sr is None:

        return (
            "Speech recognition "
            "is not installed."
        )

    try:

        recognizer = sr.Recognizer()

        with sr.AudioFile(
            io.BytesIO(audio_bytes)
        ) as source:

            audio = recognizer.record(
                source
            )

        command = (
            recognizer
            .recognize_google(
                audio,
                language="en-IN"
            )
        )

        response = process_command(
            command
        )

        if response == "__EXIT__":

            return (
                "SAI Voice OS is "
                "going offline."
            )

        return response

    except sr.UnknownValueError:

        return (
            "Sorry, I could not "
            "understand you."
        )

    except sr.RequestError:

        return (
            "Speech recognition "
            "service is unavailable."
        )

    except Exception as e:

        return (
            "I could not process "
            "your voice command."
        )


# =========================================================
# STREAMLIT UI
# =========================================================

def streamlit_app():

    st.set_page_config(
        page_title="SAI Voice OS",
        page_icon="🎙️",
        layout="centered"
    )


    # -----------------------------------------------------
    # MINIMAL UI
    # -----------------------------------------------------

    st.markdown(
        """
        <style>

        #MainMenu {
            visibility: hidden;
        }

        footer {
            visibility: hidden;
        }

        header {
            visibility: hidden;
        }

        .stApp {
            text-align: center;
        }

        </style>
        """,
        unsafe_allow_html=True
    )


    # -----------------------------------------------------
    # VOICE ONLY INTRO
    # -----------------------------------------------------

    if "started" not in st.session_state:

        st.session_state.started = False


    if "last_response" not in st.session_state:

        st.session_state.last_response = ""


    # -----------------------------------------------------
    # MICROPHONE
    # -----------------------------------------------------

    audio = st.audio_input(
        "🎙️"
    )


    if audio is not None:

        response = process_cloud_audio(
            audio.getvalue()
        )

        st.session_state.last_response = (
            response
        )

        speak_cloud(
            response
        )


# =========================================================
# WINDOWS MODE
# =========================================================

def windows_app():

    initialize_windows_tts()

    speak(
        "Welcome to SAI Voice OS."
    )

    speak(
        "Voice mode is active."
    )

    while True:

        command = listen_windows()

        if not command:

            continue

        response = process_command(
            command
        )

        if response == "__EXIT__":

            speak(
                "SAI Voice OS is "
                "going offline."
            )

            break

        speak(
            response
        )


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    if STREAMLIT_MODE:

        streamlit_app()

    else:

        windows_app()
