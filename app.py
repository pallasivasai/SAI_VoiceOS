"""
===========================================================
                    SAI VOICE OS
===========================================================

VOICE-FIRST ACCESSIBILITY OPERATING SYSTEM

CLOUD / STREAMLIT
-----------------
Voice input
Voice response
Calculator
Internet search
Wikipedia
Weather
YouTube
Google
PDF
TXT
DOCX
GitHub

WINDOWS LOCAL
-----------------
Microphone
Voice response
Notepad
Calculator
Chrome
YouTube
Google
WhatsApp
Screenshot
Local files
Local documents
Notes
Music

IMPORTANT:
-----------
pyautogui is imported ONLY on Windows.
It is never imported on Streamlit Cloud.

NO TEXT COMMAND INPUT.
===========================================================
"""

# =========================================================
# STANDARD LIBRARIES
# =========================================================

import os
import io
import re
import json
import base64
import datetime
import webbrowser
import urllib.parse
import urllib.request
import subprocess
import tempfile
import platform


# =========================================================
# STREAMLIT
# =========================================================

try:
    import streamlit as st
except ImportError:
    st = None


# =========================================================
# DETECT ENVIRONMENT
# =========================================================

IS_WINDOWS = (
    platform.system().lower() == "windows"
)

IS_STREAMLIT = (
    st is not None
)


# =========================================================
# SPEECH RECOGNITION
# =========================================================

try:
    import speech_recognition as sr
except ImportError:
    sr = None


# =========================================================
# WINDOWS TTS
# ONLY USED ON WINDOWS
# =========================================================

pyttsx3 = None
tts_engine = None

if IS_WINDOWS:

    try:
        import pyttsx3

    except Exception:
        pyttsx3 = None


# =========================================================
# WINDOWS SCREENSHOT
# VERY IMPORTANT:
# DO NOT IMPORT PYAutoGUI ON STREAMLIT CLOUD
# =========================================================

pyautogui = None

if IS_WINDOWS:

    try:
        import pyautogui

    except Exception:
        pyautogui = None


# =========================================================
# WIKIPEDIA
# =========================================================

try:
    import wikipedia
except ImportError:
    wikipedia = None


# =========================================================
# REQUESTS
# =========================================================

try:
    import requests
except ImportError:
    requests = None


# =========================================================
# PDF
# =========================================================

try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None


# =========================================================
# DOCX
# =========================================================

try:
    from docx import Document
except ImportError:
    Document = None


# =========================================================
# CONFIGURATION
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
# WINDOWS TTS INITIALIZATION
# =========================================================

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

            # Use first available voice
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

    except Exception as error:

        print(
            "TTS initialization error:",
            error
        )

        tts_engine = None


# =========================================================
# WINDOWS SPEAK
# =========================================================

def speak_windows(text):

    if not text:
        return

    print(
        "SAI:",
        text
    )

    if tts_engine is None:
        return

    try:

        tts_engine.say(
            text
        )

        tts_engine.runAndWait()

    except Exception as error:

        print(
            "TTS error:",
            error
        )


# =========================================================
# CLOUD BROWSER SPEAK
#
# Uses browser SpeechSynthesis.
#
# No text output is required for the user.
# =========================================================

def speak_cloud(text):

    if not text:
        return

    if not IS_STREAMLIT:
        return

    safe_text = json.dumps(
        str(text)
    )

    html = f"""
    <script>

        const message = {safe_text};

        function speakNow() {{

            try {{

                if (
                    "speechSynthesis"
                    in window
                ) {{

                    window.speechSynthesis.cancel();

                    const speech =
                        new SpeechSynthesisUtterance(
                            message
                        );

                    speech.lang = "en-IN";

                    speech.rate = 0.95;

                    speech.pitch = 1.0;

                    speech.volume = 1.0;

                    window.speechSynthesis.speak(
                        speech
                    );

                }}

            }} catch (error) {{

                console.log(
                    "Speech error:",
                    error
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


# =========================================================
# UNIVERSAL SPEAK
# =========================================================

def speak(text):

    if not text:
        return

    if IS_WINDOWS and not IS_STREAMLIT:

        speak_windows(text)

    elif IS_STREAMLIT:

        speak_cloud(text)

    else:

        print(
            "SAI:",
            text
        )


# =========================================================
# TIME
# =========================================================

def get_time():

    current_time = (
        datetime.datetime.now()
        .strftime("%I:%M %p")
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
# CLOUD URL ACTION
# =========================================================

def cloud_open_url(
    url,
    name
):

    if IS_STREAMLIT:

        # Browser-side attempt.
        # Browser popup policies can prevent
        # automatic external tab opening.

        safe_url = json.dumps(
            url
        )

        html = f"""
        <script>

            const url = {safe_url};

            try {{

                window.open(
                    url,
                    "_blank"
                );

            }} catch (error) {{

                console.log(error);

            }}

        </script>
        """

        st.components.v1.html(
            html,
            height=1
        )

    return (
        f"Opening {name}."
    )


# =========================================================
# OPEN YOUTUBE
# =========================================================

def open_youtube():

    if IS_WINDOWS and not IS_STREAMLIT:

        webbrowser.open(
            "https://www.youtube.com"
        )

        return (
            "Opening YouTube."
        )

    return cloud_open_url(
        "https://www.youtube.com",
        "YouTube"
    )


# =========================================================
# OPEN GOOGLE
# =========================================================

def open_google():

    if IS_WINDOWS and not IS_STREAMLIT:

        webbrowser.open(
            "https://www.google.com"
        )

        return (
            "Opening Google."
        )

    return cloud_open_url(
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

    if IS_WINDOWS and not IS_STREAMLIT:

        webbrowser.open(
            url
        )

        return (
            f"Searching Google for "
            f"{query}."
        )

    return cloud_open_url(
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

    if IS_WINDOWS and not IS_STREAMLIT:

        webbrowser.open(
            url
        )

        return (
            f"Searching YouTube for "
            f"{query}."
        )

    return cloud_open_url(
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

    except wikipedia.exceptions.DisambiguationError:

        return (
            "There are multiple Wikipedia "
            "results. Please be more specific."
        )

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

        encoded_city = (
            urllib.parse.quote(city)
        )

        url = (
            f"https://wttr.in/"
            f"{encoded_city}"
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


# =========================================================
# PDF READER
# =========================================================

def read_pdf_bytes(
    data
):

    if PdfReader is None:

        return (
            "PDF reader is not installed."
        )

    try:

        reader = PdfReader(
            io.BytesIO(data)
        )

        pages = []

        for number, page in enumerate(
            reader.pages,
            start=1
        ):

            text = (
                page.extract_text()
                or ""
            )

            if text.strip():

                pages.append(
                    f"Page {number}. "
                    f"{text}"
                )

        if not pages:

            return (
                "I could not extract "
                "text from this PDF."
            )

        return "\n".join(
            pages
        )

    except Exception:

        return (
            "I could not read "
            "this PDF."
        )


# =========================================================
# TXT READER
# =========================================================

def read_txt_bytes(
    data
):

    try:

        return data.decode(
            "utf-8",
            errors="ignore"
        )

    except Exception:

        return (
            "I could not read "
            "this text file."
        )


# =========================================================
# DOCX READER
# =========================================================

def read_docx_bytes(
    data
):

    if Document is None:

        return (
            "Word document support "
            "is not installed."
        )

    temp_path = None

    try:

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".docx"
        ) as temporary:

            temporary.write(
                data
            )

            temp_path = (
                temporary.name
            )

        document = Document(
            temp_path
        )

        paragraphs = []

        for paragraph in (
            document.paragraphs
        ):

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


# =========================================================
# DOCUMENT READER
# =========================================================

def read_document(
    filename,
    data
):

    extension = (
        os.path.splitext(
            filename
        )[1].lower()
    )

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
        "I can currently read "
        "PDF, TXT and DOCX files."
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

def github_list_repositories():

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

        repositories = (
            response.json()
        )

        return [
            repo["name"]
            for repo in repositories
        ]

    except Exception:

        return []


# =========================================================
# GITHUB FILE LIST
# =========================================================

def github_list_files(
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

            decoded = (
                base64.b64decode(
                    data["content"]
                )
            )

            return decoded.decode(
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

def github_upload_file(
    repository,
    path,
    content
):

    if requests is None:

        return (
            False,
            "Requests library is unavailable."
        )

    if not GITHUB_USERNAME:

        return (
            False,
            "GitHub username is not configured."
        )

    if not GITHUB_TOKEN:

        return (
            False,
            "GitHub token is not configured."
        )

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

        if response.status_code in [
            200,
            201
        ]:

            return (
                True,
                "File uploaded successfully."
            )

        return (
            False,
            "GitHub upload failed."
        )

    except Exception:

        return (
            False,
            "GitHub upload failed."
        )


# =========================================================
# WINDOWS APPLICATIONS
# =========================================================

def open_windows_application(
    application
):

    if not IS_WINDOWS:

        return (
            "This application is available "
            "on your Windows computer."
        )

    application = (
        application.lower()
    )

    try:

        if "notepad" in application:

            subprocess.Popen(
                ["notepad.exe"]
            )

            return (
                "Opening Notepad."
            )

        if "calculator" in application:

            subprocess.Popen(
                ["calc.exe"]
            )

            return (
                "Opening Calculator."
            )

        if "chrome" in application:

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

        if "explorer" in application:

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

    return cloud_open_url(
        "https://web.whatsapp.com",
        "WhatsApp Web"
    )


# =========================================================
# WINDOWS SCREENSHOT
# =========================================================

def take_windows_screenshot():

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


# =========================================================
# WINDOWS LOCAL FILES
# =========================================================

def get_windows_documents():

    if not IS_WINDOWS:

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
# READ WINDOWS LOCAL FILE
# =========================================================

def read_windows_file(
    filename
):

    if not IS_WINDOWS:

        return (
            "Local files are available "
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
            "I could not find "
            "that file."
        )

    try:

        extension = (
            os.path.splitext(
                filename
            )[1].lower()
        )

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
# WINDOWS NOTE
# =========================================================

def save_windows_note(
    note
):

    if not IS_WINDOWS:

        return (
            "Notes are available "
            "on your Windows computer."
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

        timestamp = (
            datetime.datetime.now()
            .strftime(
                "%Y-%m-%d %H:%M"
            )
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
            "your note."
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

        print(
            "Recognized command:",
            command
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

    except Exception as error:

        print(
            "Microphone error:",
            error
        )

    return None


# =========================================================
# COMMAND PREFIX HELPER
# =========================================================

def extract_after(
    command,
    prefixes
):

    for prefix in prefixes:

        if command.startswith(
            prefix
        ):

            return command[
                len(prefix):
            ].strip()

    return ""


# =========================================================
# MAIN COMMAND ENGINE
# =========================================================

def process_command(
    command
):

    if not command:

        return (
            "I did not hear a command."
        )


    command = (
        command
        .lower()
        .strip()
    )


    # =====================================================
    # EXIT
    # =====================================================

    if command in [
        "exit",
        "quit",
        "stop",
        "go offline",
        "goodbye"
    ]:

        return "__EXIT__"


    # =====================================================
    # TIME
    # =====================================================

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


    # =====================================================
    # DATE
    # =====================================================

    if (
        command == "date"
        or
        "what is the date"
        in command
        or
        "today's date"
        in command
    ):

        return get_date()


    # =====================================================
    # OPEN YOUTUBE
    # =====================================================

    if any(
        phrase in command
        for phrase in [
            "open youtube",
            "launch youtube",
            "start youtube"
        ]
    ):

        return open_youtube()


    # =====================================================
    # OPEN GOOGLE
    # =====================================================

    if any(
        phrase in command
        for phrase in [
            "open google",
            "launch google",
            "start google"
        ]
    ):

        return open_google()


    # =====================================================
    # SEARCH GOOGLE
    # =====================================================

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


    # =====================================================
    # SEARCH YOUTUBE
    # =====================================================

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


    # =====================================================
    # WIKIPEDIA
    # =====================================================

    query = extract_after(
        command,
        [
            "search wikipedia for",
            "search wikipedia",
            "wikipedia"
        ]
    )

    if query:

        return wikipedia_search(
            query
        )


    # =====================================================
    # WEATHER
    # =====================================================

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


    # =====================================================
    # CALCULATE
    # =====================================================

    if command.startswith(
        "calculate"
    ):

        expression = command[
            len("calculate"):
        ].strip()

        return calculate(
            expression
        )


    # =====================================================
    # OPEN CALCULATOR
    # =====================================================

    if (
        "open calculator"
        in command
    ):

        if IS_WINDOWS:

            return open_windows_application(
                "calculator"
            )

        return (
            "The calculator is "
            "available on your Windows "
            "computer."
        )


    # =====================================================
    # OPEN NOTEPAD
    # =====================================================

    if (
        "open notepad"
        in command
    ):

        if IS_WINDOWS:

            return open_windows_application(
                "notepad"
            )

        return (
            "Notepad is available "
            "on your Windows computer."
        )


    # =====================================================
    # OPEN CHROME
    # =====================================================

    if (
        "open chrome"
        in command
    ):

        if IS_WINDOWS:

            return open_windows_application(
                "chrome"
            )

        return (
            "Chrome is available "
            "on your Windows computer."
        )


    # =====================================================
    # OPEN FILE EXPLORER
    # =====================================================

    if (
        "open file explorer"
        in command
        or
        "open explorer"
        in command
    ):

        if IS_WINDOWS:

            return open_windows_application(
                "explorer"
            )

        return (
            "File Explorer is available "
            "on your Windows computer."
        )


    # =====================================================
    # WHATSAPP
    # =====================================================

    if (
        "open whatsapp"
        in command
    ):

        return open_whatsapp()


    # =====================================================
    # SCREENSHOT
    # =====================================================

    if (
        "take screenshot"
        in command
        or
        command == "screenshot"
    ):

        return take_windows_screenshot()


    # =====================================================
    # LIST LOCAL FILES
    # =====================================================

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

        files = (
            get_windows_documents()
        )

        if not files:

            return (
                "I could not find "
                "any files."
            )

        files = files[:10]

        return (
            "I found "
            f"{len(files)} files. "
            "Some of them are "
            + ", ".join(files)
        )


    # =====================================================
    # GITHUB REPOSITORIES
    # =====================================================

    if any(
        phrase in command
        for phrase in [
            "list github repositories",
            "show github repositories",
            "my github repositories"
        ]
    ):

        repositories = (
            github_list_repositories()
        )

        if not repositories:

            return (
                "I could not retrieve "
                "your GitHub repositories."
            )

        return (
            "Your GitHub repositories "
            "are "
            + ", ".join(
                repositories
            )
        )


    # =====================================================
    # UNKNOWN COMMAND
    # =====================================================

    return (
        "I do not understand "
        "that command yet."
    )


# =========================================================
# CLOUD AUDIO → TEXT
# =========================================================

def recognize_cloud_audio(
    audio_bytes
):

    if sr is None:

        return None

    recognizer = sr.Recognizer()

    try:

        with sr.AudioFile(
            io.BytesIO(
                audio_bytes
            )
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

        return command.lower()

    except sr.UnknownValueError:

        return None

    except sr.RequestError:

        return None

    except Exception:

        return None


# =========================================================
# CLOUD VOICE COMMAND
# =========================================================

def process_cloud_voice(
    audio_bytes
):

    command = recognize_cloud_audio(
        audio_bytes
    )

    if not command:

        response = (
            "Sorry, I could not "
            "understand you."
        )

        speak_cloud(
            response
        )

        return


    response = process_command(
        command
    )

    if response == "__EXIT__":

        response = (
            "SAI Voice OS is "
            "going offline."
        )

    speak_cloud(
        response
    )


# =========================================================
# STREAMLIT APP
# =========================================================

def streamlit_app():

    st.set_page_config(
        page_title="SAI Voice OS",
        page_icon="🎙️",
        layout="centered"
    )


    # =====================================================
    # HIDE NORMAL STREAMLIT UI
    # =====================================================

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

        </style>
        """,
        unsafe_allow_html=True
    )


    # =====================================================
    # VOICE INPUT ONLY
    # =====================================================

    audio = st.audio_input(
        "Speak to SAI"
    )


    if audio is not None:

        process_cloud_voice(
            audio.getvalue()
        )


# =========================================================
# WINDOWS LOCAL APPLICATION
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
# ENTRY POINT
# =========================================================

if __name__ == "__main__":

    # -----------------------------------------------------
    # STREAMLIT CLOUD
    # -----------------------------------------------------

    if IS_STREAMLIT:

        streamlit_app()

    # -----------------------------------------------------
    # WINDOWS LOCAL
    # -----------------------------------------------------

    elif IS_WINDOWS:

        windows_app()

    # -----------------------------------------------------
    # OTHER
    # -----------------------------------------------------

    else:

        print(
            "SAI Voice OS requires "
            "Windows or Streamlit."
        )
