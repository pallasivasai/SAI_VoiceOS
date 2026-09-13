import os
import io
import re
import json
import base64
import time
import queue
import threading
import datetime
import webbrowser
import urllib.parse
import urllib.request
import subprocess
import tempfile
import platform

import streamlit as st

from streamlit_webrtc import (
    webrtc_streamer,
    WebRtcMode,
    AudioProcessorBase,
    RTCConfiguration,
    MediaStreamConstraints
)

import numpy as np
import speech_recognition as sr


# ============================================================
# OPTIONAL WINDOWS MODULES
# ============================================================

IS_WINDOWS = (
    platform.system().lower() == "windows"
)


pyautogui = None
pyttsx3 = None
wikipedia = None
requests = None
PdfReader = None
Document = None


# ------------------------------------------------------------
# pyautogui ONLY ON WINDOWS
# ------------------------------------------------------------

if IS_WINDOWS:

    try:
        import pyautogui
    except Exception:
        pyautogui = None


# ------------------------------------------------------------
# pyttsx3 ONLY ON WINDOWS
# ------------------------------------------------------------

if IS_WINDOWS:

    try:
        import pyttsx3
    except Exception:
        pyttsx3 = None


# ------------------------------------------------------------
# Wikipedia
# ------------------------------------------------------------

try:
    import wikipedia
except Exception:
    wikipedia = None


# ------------------------------------------------------------
# Requests
# ------------------------------------------------------------

try:
    import requests
except Exception:
    requests = None


# ------------------------------------------------------------
# PDF
# ------------------------------------------------------------

try:
    from PyPDF2 import PdfReader
except Exception:
    PdfReader = None


# ------------------------------------------------------------
# DOCX
# ------------------------------------------------------------

try:
    from docx import Document
except Exception:
    Document = None


# ============================================================
# CONFIGURATION
# ============================================================

APP_NAME = "SAI Voice OS"

GITHUB_USERNAME = os.getenv(
    "GITHUB_USERNAME",
    ""
)

GITHUB_TOKEN = os.getenv(
    "GITHUB_TOKEN",
    ""
)


# ============================================================
# SESSION STATE
# ============================================================

if "last_response" not in st.session_state:
    st.session_state.last_response = ""

if "last_command" not in st.session_state:
    st.session_state.last_command = ""

if "speaking" not in st.session_state:
    st.session_state.speaking = False


# ============================================================
# WINDOWS TTS
# ============================================================

tts_engine = None


def initialize_windows_tts():

    global tts_engine

    if not IS_WINDOWS:
        return

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


# ============================================================
# CLOUD TTS
# ============================================================

def cloud_speak(text):

    if not text:
        return

    safe_text = json.dumps(
        str(text)
    )

    html = f"""
    <script>

    const text = {safe_text};

    function speakNow() {{

        if ("speechSynthesis" in window) {{

            window.speechSynthesis.cancel();

            const utterance =
                new SpeechSynthesisUtterance(text);

            utterance.lang = "en-IN";
            utterance.rate = 0.95;
            utterance.pitch = 1.0;
            utterance.volume = 1.0;

            window.speechSynthesis.speak(
                utterance
            );
        }}

    }}

    speakNow();

    </script>
    """

    st.components.v1.html(
        html,
        height=1
    )


# ============================================================
# WINDOWS TTS
# ============================================================

def windows_speak(text):

    if not text:
        return

    if tts_engine is None:
        return

    try:

        tts_engine.say(
            text
        )

        tts_engine.runAndWait()

    except Exception:
        pass


# ============================================================
# UNIVERSAL SPEAK
# ============================================================

def speak(text):

    if not text:
        return

    if IS_WINDOWS and not st.runtime.exists():

        windows_speak(text)

    else:

        cloud_speak(text)


# ============================================================
# TIME
# ============================================================

def get_time():

    current_time = (
        datetime.datetime.now()
        .strftime("%I:%M %p")
    )

    return (
        f"The current time is "
        f"{current_time}."
    )


# ============================================================
# DATE
# ============================================================

def get_date():

    now = datetime.datetime.now()

    return (
        f"Today is "
        f"{now.day} "
        f"{now.strftime('%B')} "
        f"{now.year}."
    )


# ============================================================
# CALCULATOR
# ============================================================

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


# ============================================================
# BROWSER ACTION
# ============================================================

def browser_open(
    url,
    spoken_name
):

    html = f"""
    <script>

        const url =
            {json.dumps(url)};

        window.open(
            url,
            "_blank"
        );

    </script>
    """

    st.components.v1.html(
        html,
        height=1
    )

    return (
        f"Opening {spoken_name}."
    )


# ============================================================
# YOUTUBE
# ============================================================

def open_youtube():

    return browser_open(
        "https://www.youtube.com",
        "YouTube"
    )


# ============================================================
# GOOGLE
# ============================================================

def open_google():

    return browser_open(
        "https://www.google.com",
        "Google"
    )


# ============================================================
# GOOGLE SEARCH
# ============================================================

def google_search(query):

    url = (
        "https://www.google.com/search?q="
        + urllib.parse.quote(query)
    )

    return browser_open(
        url,
        f"Google search for {query}"
    )


# ============================================================
# YOUTUBE SEARCH
# ============================================================

def youtube_search(query):

    url = (
        "https://www.youtube.com/results?"
        "search_query="
        + urllib.parse.quote(query)
    )

    return browser_open(
        url,
        f"YouTube search for {query}"
    )


# ============================================================
# WIKIPEDIA
# ============================================================

def wikipedia_search(query):

    if wikipedia is None:

        return (
            "Wikipedia is not available."
        )

    try:

        return wikipedia.summary(
            query,
            sentences=3
        )

    except Exception:

        return (
            "I could not find that "
            "on Wikipedia."
        )


# ============================================================
# WEATHER
# ============================================================

def get_weather(city):

    try:

        city_encoded = (
            urllib.parse.quote(city)
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

        current = (
            data[
                "current_condition"
            ][0]
        )

        temperature = (
            current["temp_C"]
        )

        description = (
            current[
                "weatherDesc"
            ][0]["value"]
        )

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


# ============================================================
# GITHUB
# ============================================================

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


# ============================================================
# DOCUMENT READER
# ============================================================

def read_pdf(data):

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

    except Exception:

        return (
            "I could not read the PDF."
        )


def read_txt(data):

    try:

        return data.decode(
            "utf-8",
            errors="ignore"
        )

    except Exception:

        return (
            "I could not read "
            "the text file."
        )


def read_docx(data):

    if Document is None:

        return (
            "DOCX reader is not installed."
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
            "I could not read "
            "the Word document."
        )

    finally:

        if temp_path:

            try:
                os.remove(
                    temp_path
                )
            except Exception:
                pass


# ============================================================
# WINDOWS APPS
# ============================================================

def open_windows_app(
    app
):

    if not IS_WINDOWS:

        return (
            f"{app} is available "
            "on your Windows computer."
        )

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

        if "chrome" in app:

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


# ============================================================
# WHATSAPP
# ============================================================

def open_whatsapp():

    if IS_WINDOWS:

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

    return browser_open(
        "https://web.whatsapp.com",
        "WhatsApp Web"
    )


# ============================================================
# SCREENSHOT
# ============================================================

def take_screenshot():

    if not IS_WINDOWS:

        return (
            "Screenshot is available "
            "on your Windows computer."
        )

    if pyautogui is None:

        return (
            "Screenshot support "
            "is not available."
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

        image.save(
            path
        )

        return (
            "Screenshot taken successfully."
        )

    except Exception:

        return (
            "I could not take "
            "the screenshot."
        )


# ============================================================
# COMMAND PREFIX
# ============================================================

def extract_after(
    command,
    prefixes
):

    for prefix in prefixes:

        if command.startswith(prefix):

            return command[
                len(prefix):
            ].strip()

    return ""


# ============================================================
# INTENT ENGINE
# ============================================================

def process_command(
    command
):

    if not command:

        return (
            "I did not hear you."
        )


    command = (
        command
        .lower()
        .strip()
    )


    # --------------------------------------------------------
    # EXIT
    # --------------------------------------------------------

    if command in [
        "exit",
        "quit",
        "stop",
        "go offline",
        "goodbye"
    ]:

        return "__EXIT__"


    # --------------------------------------------------------
    # TIME
    # --------------------------------------------------------

    if (
        command == "time"
        or
        "what time is it"
        in command
        or
        "what is the time"
        in command
    ):

        return get_time()


    # --------------------------------------------------------
    # DATE
    # --------------------------------------------------------

    if (
        command == "date"
        or
        "what is the date"
        in command
    ):

        return get_date()


    # --------------------------------------------------------
    # YOUTUBE
    # --------------------------------------------------------

    if any(
        phrase in command
        for phrase in [
            "open youtube",
            "launch youtube",
            "start youtube"
        ]
    ):

        return open_youtube()


    # --------------------------------------------------------
    # GOOGLE
    # --------------------------------------------------------

    if any(
        phrase in command
        for phrase in [
            "open google",
            "launch google",
            "start google"
        ]
    ):

        return open_google()


    # --------------------------------------------------------
    # GOOGLE SEARCH
    # --------------------------------------------------------

    query = extract_after(
        command,
        [
            "search google for",
            "search google",
            "google search for",
            "google search"
        ]
    )

    if query:

        return google_search(
            query
        )


    # --------------------------------------------------------
    # YOUTUBE SEARCH
    # --------------------------------------------------------

    query = extract_after(
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


    # --------------------------------------------------------
    # WIKIPEDIA
    # --------------------------------------------------------

    query = extract_after(
        command,
        [
            "search wikipedia for",
            "wikipedia"
        ]
    )

    if query:

        return wikipedia_search(
            query
        )


    # --------------------------------------------------------
    # WEATHER
    # --------------------------------------------------------

    if "weather" in command:

        city = "Guntur"

        match = re.search(
            r"weather\s+(?:in\s+)?(.+)",
            command
        )

        if match:

            city = (
                match.group(1)
                .strip()
            )

        return get_weather(
            city
        )


    # --------------------------------------------------------
    # CALCULATOR
    # --------------------------------------------------------

    if command.startswith(
        "calculate"
    ):

        expression = command[
            len("calculate"):
        ].strip()

        return calculate(
            expression
        )


    # --------------------------------------------------------
    # NOTEPAD
    # --------------------------------------------------------

    if "open notepad" in command:

        return open_windows_app(
            "notepad"
        )


    # --------------------------------------------------------
    # CALCULATOR APP
    # --------------------------------------------------------

    if (
        "open calculator"
        in command
    ):

        return open_windows_app(
            "calculator"
        )


    # --------------------------------------------------------
    # CHROME
    # --------------------------------------------------------

    if "open chrome" in command:

        return open_windows_app(
            "chrome"
        )


    # --------------------------------------------------------
    # FILE EXPLORER
    # --------------------------------------------------------

    if (
        "open file explorer"
        in command
        or
        "open explorer"
        in command
    ):

        return open_windows_app(
            "explorer"
        )


    # --------------------------------------------------------
    # WHATSAPP
    # --------------------------------------------------------

    if "open whatsapp" in command:

        return open_whatsapp()


    # --------------------------------------------------------
    # SCREENSHOT
    # --------------------------------------------------------

    if (
        "take screenshot"
        in command
        or
        command == "screenshot"
    ):

        return take_screenshot()


    # --------------------------------------------------------
    # GITHUB
    # --------------------------------------------------------

    if any(
        phrase in command
        for phrase in [
            "list github repositories",
            "show github repositories",
            "my github repositories"
        ]
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
            "Your GitHub repositories "
            "are "
            + ", ".join(repos)
        )


    # --------------------------------------------------------
    # UNKNOWN
    # --------------------------------------------------------

    return (
        "I do not understand "
        "that command yet."
    )


# ============================================================
# AUDIO PROCESSOR
# ============================================================

class SAIProcessor(
    AudioProcessorBase
):

    def __init__(self):

        self.audio_queue = queue.Queue()

    def recv(
        self,
        frame
    ):

        try:

            audio = frame.to_ndarray()

            self.audio_queue.put(
                audio.copy()
            )

        except Exception:
            pass

        return frame


# ============================================================
# GLOBAL AUDIO QUEUE
# ============================================================

if "audio_queue" not in st.session_state:

    st.session_state.audio_queue = queue.Queue()


# ============================================================
# SPEECH WORKER
# ============================================================

def speech_worker(
    processor
):

    recognizer = sr.Recognizer()

    audio_buffer = []

    last_audio_time = time.time()

    while True:

        try:

            audio = (
                processor.audio_queue.get(
                    timeout=1
                )
            )

            audio_buffer.append(
                audio
            )

            last_audio_time = (
                time.time()
            )

            # Keep approximately
            # a manageable rolling buffer

            if len(audio_buffer) > 50:

                audio_buffer.pop(0)

        except queue.Empty:

            # No audio received
            # continue listening

            continue

        # ----------------------------------------------------
        # Process only periodically
        # ----------------------------------------------------

        if len(audio_buffer) < 15:

            continue

        try:

            combined = np.concatenate(
                audio_buffer,
                axis=0
            )

            # Convert to mono
            if combined.ndim > 1:

                combined = np.mean(
                    combined,
                    axis=1
                )

            # Normalize
            combined = np.asarray(
                combined,
                dtype=np.float32
            )

            maximum = np.max(
                np.abs(combined)
            )

            if maximum == 0:

                continue

            combined = (
                combined / maximum
            )

            # ------------------------------------------------
            # Simple voice activity check
            # ------------------------------------------------

            volume = np.mean(
                np.abs(combined)
            )

            if volume < 0.01:

                continue

            # ------------------------------------------------
            # WAV conversion
            # ------------------------------------------------

            import wave

            wav_buffer = (
                io.BytesIO()
            )

            with wave.open(
                wav_buffer,
                "wb"
            ) as wav_file:

                wav_file.setnchannels(
                    1
                )

                wav_file.setsampwidth(
                    2
                )

                wav_file.setframerate(
                    48000
                )

                pcm = (
                    combined * 32767
                ).astype(
                    np.int16
                )

                wav_file.writeframes(
                    pcm.tobytes()
                )

            wav_buffer.seek(0)

            # ------------------------------------------------
            # Speech recognition
            # ------------------------------------------------

            with sr.AudioFile(
                wav_buffer
            ) as source:

                audio_data = (
                    recognizer.record(
                        source
                    )
                )

            try:

                command = (
                    recognizer
                    .recognize_google(
                        audio_data,
                        language="en-IN"
                    )
                )

            except Exception:

                audio_buffer.clear()

                continue

            if not command:

                audio_buffer.clear()

                continue

            command = command.lower().strip()

            # ------------------------------------------------
            # Prevent repeated same command
            # ------------------------------------------------

            if (
                command
                == st.session_state.last_command
            ):

                audio_buffer.clear()

                continue

            st.session_state.last_command = (
                command
            )

            # ------------------------------------------------
            # Execute
            # ------------------------------------------------

            response = process_command(
                command
            )

            if response == "__EXIT__":

                response = (
                    "Voice mode is stopping."
                )

            st.session_state.last_response = (
                response
            )

            # ------------------------------------------------
            # Answer
            # ------------------------------------------------

            cloud_speak(
                response
            )

            # ------------------------------------------------
            # IMPORTANT:
            # Clear buffer and continue listening
            # ------------------------------------------------

            audio_buffer.clear()

        except Exception:

            audio_buffer.clear()

            continue


# ============================================================
# MAIN STREAMLIT APP
# ============================================================

def main():

    st.set_page_config(
        page_title="SAI Voice OS",
        page_icon="🎙️",
        layout="centered"
    )


    # ========================================================
    # HIDE STREAMLIT UI
    # ========================================================

    st.markdown(
        """
        <style>

        #MainMenu {
            visibility: hidden;
        }

        header {
            visibility: hidden;
        }

        footer {
            visibility: hidden;
        }

        .stApp {
            background: white;
        }

        </style>
        """,
        unsafe_allow_html=True
    )


    # ========================================================
    # VOICE OS
    # ========================================================

    st.markdown(
        """
        <h1 style="text-align:center;">
            🎙️ SAI Voice OS
        </h1>
        """,
        unsafe_allow_html=True
    )


    # ========================================================
    # CONTINUOUS MICROPHONE
    # ========================================================

    rtc_configuration = RTCConfiguration(
        {
            "iceServers": [
                {
                    "urls": [
                        "stun:stun.l.google.com:19302"
                    ]
                }
            ]
        }
    )


    ctx = webrtc_streamer(
        key="sai_voice_os",

        mode=WebRtcMode.SENDONLY,

        rtc_configuration=rtc_configuration,

        media_stream_constraints={
            "video": False,
            "audio": True
        },

        audio_processor_factory=SAIProcessor,

        async_processing=True
    )


    # ========================================================
    # START SPEECH PROCESSOR
    # ========================================================

    if ctx.state.playing:

        if (
            "worker_started"
            not in st.session_state
        ):

            st.session_state.worker_started = True

            worker = threading.Thread(
                target=speech_worker,
                args=(ctx.audio_processor,),
                daemon=True
            )

            worker.start()


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()
