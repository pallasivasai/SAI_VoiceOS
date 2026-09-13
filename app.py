"""
SAI VOICE OS
============

Two modes:

1. STREAMLIT CLOUD
   - Voice input from browser
   - Internet search
   - Wikipedia
   - Weather
   - GitHub
   - Uploaded documents
   - PDF/TXT/DOCX reading
   - Calculator
   - Browser links
   - Web answers

2. WINDOWS LOCAL
   - Microphone
   - TTS
   - Local files
   - Notepad
   - Calculator
   - Chrome
   - Screenshot
   - Notes
   - Music
   - WhatsApp Web
   - Windows commands

The same Python file automatically detects Streamlit mode.
"""

import os
import io
import re
import json
import random
import datetime
import webbrowser
import urllib.parse
import urllib.request
import subprocess
import tempfile
import platform

# -----------------------------
# Optional imports
# -----------------------------

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

try:
    import streamlit as st
except ImportError:
    st = None


# ============================================================
# CONFIGURATION
# ============================================================

APP_NAME = "SAI Voice OS"

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME", "")

IS_STREAMLIT = st is not None


# ============================================================
# LOCAL WINDOWS TTS
# ============================================================

_engine = None


def local_tts_init():

    global _engine

    if pyttsx3 is None:
        return

    try:
        _engine = pyttsx3.init()

        voices = _engine.getProperty("voices")

        if voices:
            _engine.setProperty("voice", voices[0].id)

        _engine.setProperty("rate", 150)
        _engine.setProperty("volume", 1.0)

    except Exception:
        _engine = None


def speak_local(text):

    print(f"{APP_NAME}: {text}")

    if _engine is None:
        return

    try:
        _engine.say(text)
        _engine.runAndWait()

    except Exception as e:
        print("TTS error:", e)


# ============================================================
# STREAMLIT BROWSER TTS
# ============================================================

def speak_cloud(text):

    print(f"{APP_NAME}: {text}")

    if not IS_STREAMLIT:
        return

    # Browser speech synthesis
    html = f"""
    <script>
        const text = {json.dumps(text)};
        if ('speechSynthesis' in window) {{
            window.speechSynthesis.cancel();

            const utterance =
                new SpeechSynthesisUtterance(text);

            utterance.lang = 'en-IN';
            utterance.rate = 0.95;
            utterance.pitch = 1.0;

            window.speechSynthesis.speak(utterance);
        }}
    </script>
    """

    st.components.v1.html(
        html,
        height=1
    )


def speak(text):

    if IS_STREAMLIT:
        speak_cloud(text)
    else:
        speak_local(text)


# ============================================================
# DATE / TIME
# ============================================================

def get_time():

    current_time = datetime.datetime.now().strftime(
        "%I:%M %p"
    )

    return f"The current time is {current_time}."


def get_date():

    now = datetime.datetime.now()

    return (
        f"Today is {now.day} "
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
            "plus", "+"
        )

        expression = expression.replace(
            "minus", "-"
        )

        expression = expression.replace(
            "times", "*"
        )

        expression = expression.replace(
            "multiplied by", "*"
        )

        expression = expression.replace(
            "divided by", "/"
        )

        # Allow only calculator characters
        expression = re.sub(
            r"[^0-9+\-*/().% ]",
            "",
            expression
        )

        result = eval(
            expression,
            {
                "__builtins__": {}
            },
            {}
        )

        return f"The answer is {result}."

    except Exception:

        return "I could not calculate that."


# ============================================================
# INTERNET SEARCH
# ============================================================

def google_search(query):

    url = (
        "https://www.google.com/search?q="
        + urllib.parse.quote(query)
    )

    if not IS_STREAMLIT:
        webbrowser.open(url)

    return f"Searching Google for {query}."


def youtube_search(query):

    url = (
        "https://www.youtube.com/results?search_query="
        + urllib.parse.quote(query)
    )

    if not IS_STREAMLIT:
        webbrowser.open(url)

    return f"Searching YouTube for {query}."


# ============================================================
# WIKIPEDIA
# ============================================================

def wikipedia_search(query):

    if wikipedia is None:
        return "Wikipedia module is not installed."

    try:

        result = wikipedia.summary(
            query,
            sentences=3
        )

        return result

    except Exception:

        return "I could not find that on Wikipedia."


# ============================================================
# WEATHER
# ============================================================

def get_weather(city):

    try:

        city_encoded = urllib.parse.quote(city)

        url = (
            f"https://wttr.in/{city_encoded}"
            "?format=j1"
        )

        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0"
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

        temperature = current["temp_C"]

        description = current[
            "weatherDesc"
        ][0]["value"]

        return (
            f"The current temperature in "
            f"{city} is {temperature} "
            f"degrees Celsius with "
            f"{description}."
        )

    except Exception:

        return (
            "Sorry, I could not fetch "
            "the weather."
        )


# ============================================================
# DOCUMENT READER
# ============================================================

def read_pdf_bytes(data):

    if PdfReader is None:
        return "PDF reader is not installed."

    try:

        pdf = PdfReader(
            io.BytesIO(data)
        )

        text = []

        for index, page in enumerate(
            pdf.pages
        ):

            page_text = page.extract_text()

            if page_text:

                text.append(
                    f"Page {index + 1}\n"
                    f"{page_text}"
                )

        return "\n\n".join(text)

    except Exception as e:

        return f"Could not read PDF: {e}"


def read_txt_bytes(data):

    try:

        return data.decode(
            "utf-8",
            errors="ignore"
        )

    except Exception as e:

        return f"Could not read text file: {e}"


def read_docx_bytes(data):

    if Document is None:
        return "DOCX reader is not installed."

    try:

        temp = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".docx"
        )

        temp.write(data)
        temp.close()

        document = Document(
            temp.name
        )

        text = []

        for paragraph in document.paragraphs:

            if paragraph.text.strip():

                text.append(
                    paragraph.text
                )

        os.unlink(temp.name)

        return "\n".join(text)

    except Exception as e:

        return f"Could not read DOCX: {e}"


def read_uploaded_document(
    filename,
    data
):

    extension = os.path.splitext(
        filename
    )[1].lower()

    if extension == ".pdf":

        return read_pdf_bytes(data)

    if extension == ".txt":

        return read_txt_bytes(data)

    if extension == ".docx":

        return read_docx_bytes(data)

    return (
        "This document format is "
        "not supported yet."
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

        headers["Authorization"] = (
            f"Bearer {GITHUB_TOKEN}"
        )

    return headers


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

        data = response.json()

        return [
            repo["name"]
            for repo in data
        ]

    except Exception:

        return []


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

        if data.get("encoding") == "base64":

            import base64

            content = base64.b64decode(
                data["content"]
            )

            return content.decode(
                "utf-8",
                errors="ignore"
            )

        return data.get("content", "")

    except Exception:

        return None


def github_upload_file(
    repository,
    path,
    content,
    commit_message="Upload from SAI Voice OS"
):

    if requests is None:
        return False, "Requests is not installed."

    if not GITHUB_TOKEN:
        return False, "GitHub token is not configured."

    try:

        import base64

        encoded = base64.b64encode(
            content
        ).decode()

        url = (
            "https://api.github.com/repos/"
            f"{GITHUB_USERNAME}/"
            f"{repository}/contents/"
            f"{path}"
        )

        # Check whether file exists
        existing = requests.get(
            url,
            headers=github_headers(),
            timeout=10
        )

        payload = {
            "message": commit_message,
            "content": encoded
        }

        if existing.status_code == 200:

            old_data = existing.json()

            payload["sha"] = old_data["sha"]

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

            return True, "File uploaded to GitHub."

        return (
            False,
            f"GitHub error: {response.status_code}"
        )

    except Exception as e:

        return False, str(e)


# ============================================================
# WINDOWS LOCAL FILES
# ============================================================

def local_documents():

    if platform.system() != "Windows":

        return []

    path = os.path.expanduser(
        "~/Documents"
    )

    try:

        return os.listdir(path)

    except Exception:

        return []


def open_windows_application(
    application
):

    if platform.system() != "Windows":

        return (
            "Windows applications are "
            "available only in local mode."
        )

    application = application.lower()

    if "notepad" in application:

        subprocess.Popen(
            ["notepad.exe"]
        )

        return "Opening Notepad."

    if "calculator" in application:

        subprocess.Popen(
            ["calc.exe"]
        )

        return "Opening Calculator."

    if (
        "chrome" in application
        or "browser" in application
    ):

        subprocess.Popen(
            ["cmd", "/c", "start", "chrome"]
        )

        return "Opening Chrome."

    return (
        "That Windows application "
        "is not mapped yet."
    )


# ============================================================
# WINDOWS SCREENSHOT
# ============================================================

def take_screenshot():

    if pyautogui is None:

        return (
            "Screenshot module is not installed."
        )

    if platform.system() != "Windows":

        return (
            "Screenshot is available "
            "in Windows local mode."
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
            "sai_screenshot_"
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
            f"Screenshot saved as {path}."
        )

    except Exception as e:

        return f"Screenshot failed: {e}"


# ============================================================
# WINDOWS MICROPHONE
# ============================================================

def listen_windows():

    if sr is None:

        return None

    recognizer = sr.Recognizer()

    try:

        with sr.Microphone() as source:

            print("Listening...")

            recognizer.adjust_for_ambient_noise(
                source,
                duration=0.5
            )

            audio = recognizer.listen(
                source,
                timeout=5,
                phrase_time_limit=10
            )

        print("Recognizing...")

        text = recognizer.recognize_google(
            audio,
            language="en-IN"
        )

        print("YOU:", text)

        return text.lower()

    except Exception as e:

        print("Voice error:", e)

        speak(
            "I could not understand "
            "your voice."
        )

        return None


# ============================================================
# WINDOWS WHATSAPP
# ============================================================

def open_whatsapp():

    if platform.system() != "Windows":

        return (
            "WhatsApp desktop is available "
            "in Windows local mode."
        )

    try:

        subprocess.Popen(
            [
                "cmd",
                "/c",
                "start",
                "whatsapp:"
            ]
        )

        return "Opening WhatsApp."

    except Exception:

        webbrowser.open(
            "https://web.whatsapp.com"
        )

        return "Opening WhatsApp Web."


# ============================================================
# COMMAND PROCESSOR
# ============================================================

def process_command(command):

    command = command.lower().strip()

    if not command:
        return "I did not hear a command."

    # EXIT

    if command in [
        "exit",
        "quit",
        "go offline",
        "stop"
    ]:

        return "__EXIT__"

    # TIME

    if "what time" in command:
        return get_time()

    if command == "time":
        return get_time()

    # DATE

    if "what is the date" in command:
        return get_date()

    if command == "date":
        return get_date()

    # CALCULATOR

    if command.startswith("calculate"):

        expression = command[
            len("calculate"):
        ].strip()

        return calculate(expression)

    # WINDOWS APPS

    if (
        "open notepad" in command
        and not IS_STREAMLIT
    ):

        return open_windows_application(
            "notepad"
        )

    if (
        "open calculator" in command
        and not IS_STREAMLIT
    ):

        return open_windows_application(
            "calculator"
        )

    if (
        "open chrome" in command
        and not IS_STREAMLIT
    ):

        return open_windows_application(
            "chrome"
        )

    # WHATSAPP

    if (
        "open whatsapp" in command
        and not IS_STREAMLIT
    ):

        return open_whatsapp()

    # SCREENSHOT

    if (
        "take screenshot" in command
        or "screenshot" in command
    ):

        if IS_STREAMLIT:

            return (
                "Screenshot is available "
                "when SAI Voice OS is running "
                "on your Windows computer."
            )

        return take_screenshot()

    # GOOGLE

    if command.startswith(
        "search google for"
    ):

        query = command.replace(
            "search google for",
            "",
            1
        ).strip()

        return google_search(query)

    if command.startswith("search"):

        query = command.replace(
            "search",
            "",
            1
        ).strip()

        return google_search(query)

    # YOUTUBE

    if command.startswith(
        "play on youtube"
    ):

        query = command.replace(
            "play on youtube",
            "",
            1
        ).strip()

        return youtube_search(query)

    # WIKIPEDIA

    if command.startswith(
        "wikipedia"
    ):

        query = command.replace(
            "wikipedia",
            "",
            1
        ).strip()

        return wikipedia_search(query)

    # WEATHER

    if "weather" in command:

        city = "Guntur"

        words = command.split()

        if "in" in words:

            index = words.index("in")

            if index + 1 < len(words):

                city = " ".join(
                    words[index + 1:]
                )

        return get_weather(city)

    # GITHUB

    if (
        "list github repositories"
        in command
    ):

        repos = (
            github_list_repositories()
        )

        if not repos:

            return (
                "I could not retrieve "
                "your GitHub repositories."
            )

        return (
            "Your GitHub repositories are: "
            + ", ".join(repos)
        )

    # UNKNOWN

    return (
        "I understand the command, "
        "but that feature has not been "
        "implemented yet."
    )


# ============================================================
# STREAMLIT UI
# ============================================================

def streamlit_app():

    st.set_page_config(
        page_title="SAI Voice OS",
        page_icon="🎙️",
        layout="wide"
    )

    st.title("🎙️ SAI Voice OS")

    st.caption(
        "Voice-first accessibility operating system"
    )

    # -------------------------
    # Sidebar
    # -------------------------

    st.sidebar.title("SAI Voice OS")

    st.sidebar.info(
        """
Cloud Mode

Available:
• Internet
• Search
• Wikipedia
• Weather
• GitHub
• PDF
• TXT
• DOCX
• Calculator

Windows-only:
• Microphone hardware
• Local files
• Screenshot
• WhatsApp desktop
• Windows applications
"""
    )

    # -------------------------
    # Session State
    # -------------------------

    if "history" not in st.session_state:

        st.session_state.history = []

    if "document_text" not in st.session_state:

        st.session_state.document_text = ""

    # -------------------------
    # Voice Input
    # -------------------------

    st.header("🎤 Voice Command")

    audio = st.audio_input(
        "Speak to SAI"
    )

    if audio is not None:

        if sr is None:

            st.error(
                "SpeechRecognition is not installed."
            )

        else:

            try:

                recognizer = sr.Recognizer()

                audio_bytes = (
                    audio.getvalue()
                )

                with sr.AudioFile(
                    io.BytesIO(audio_bytes)
                ) as source:

                    recorded_audio = (
                        recognizer.record(source)
                    )

                command = (
                    recognizer
                    .recognize_google(
                        recorded_audio,
                        language="en-IN"
                    )
                )

                command = command.lower()

                st.write(
                    f"**You:** {command}"
                )

                response = process_command(
                    command
                )

                if response == "__EXIT__":

                    response = (
                        "SAI Voice OS is going offline."
                    )

                st.session_state.history.append(
                    {
                        "user": command,
                        "sai": response
                    }
                )

                st.success(response)

                speak_cloud(response)

            except Exception as e:

                st.error(
                    f"Voice recognition failed: {e}"
                )

    # -------------------------
    # Text Command
    # -------------------------

    st.header("⌨️ Text Command")

    command = st.text_input(
        "Type a command"
    )

    if st.button("Run Command"):

        if command:

            response = process_command(
                command
            )

            st.session_state.history.append(
                {
                    "user": command,
                    "sai": response
                }
            )

            st.success(response)

            speak_cloud(response)

    # -------------------------
    # Documents
    # -------------------------

    st.header("📄 Documents")

    uploaded_file = st.file_uploader(
        "Upload PDF / TXT / DOCX",
        type=[
            "pdf",
            "txt",
            "docx"
        ]
    )

    if uploaded_file is not None:

        data = uploaded_file.read()

        text = read_uploaded_document(
            uploaded_file.name,
            data
        )

        st.session_state.document_text = text

        st.success(
            f"{uploaded_file.name} loaded."
        )

    if st.session_state.document_text:

        st.text_area(
            "Document content",
            st.session_state.document_text,
            height=400
        )

        if st.button(
            "🔊 Read Document"
        ):

            text = (
                st.session_state.document_text
            )

            # Limit browser speech size
            text_to_speak = text[:5000]

            speak_cloud(
                text_to_speak
            )

    # -------------------------
    # GitHub
    # -------------------------

    st.header("🐙 GitHub")

    if GITHUB_USERNAME:

        repos = (
            github_list_repositories()
        )

        if repos:

            repository = st.selectbox(
                "Repository",
                repos
            )

            if st.button(
                "List Repository Files"
            ):

                files = (
                    github_list_files(
                        repository
                    )
                )

                if files:

                    for item in files:

                        st.write(
                            f"{item['type']}: "
                            f"{item['path']}"
                        )

                else:

                    st.warning(
                        "No files found."
                    )

            github_file = st.file_uploader(
                "Upload a file to GitHub",
                key="github_upload"
            )

            github_path = st.text_input(
                "GitHub destination path",
                placeholder="documents/file.pdf"
            )

            if st.button(
                "Upload to GitHub"
            ):

                if github_file and github_path:

                    content = (
                        github_file.read()
                    )

                    success, message = (
                        github_upload_file(
                            repository,
                            github_path,
                            content
                        )
                    )

                    if success:

                        st.success(message)

                    else:

                        st.error(message)

        else:

            st.warning(
                "No GitHub repositories found."
            )

    else:

        st.info(
            "Set GITHUB_USERNAME and "
            "GITHUB_TOKEN in Streamlit Secrets."
        )

    # -------------------------
    # Command History
    # -------------------------

    st.header("🧠 Conversation")

    for item in reversed(
        st.session_state.history
    ):

        st.write(
            f"👤 **You:** {item['user']}"
        )

        st.write(
            f"🤖 **SAI:** {item['sai']}"
        )

        st.divider()


# ============================================================
# WINDOWS MODE
# ============================================================

def windows_mode():

    local_tts_init()

    speak(
        "Welcome to SAI Voice OS. "
        "Windows local mode is active."
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
                "SAI Voice OS is going offline."
            )

            break

        print(
            f"SAI: {response}"
        )

        speak(response)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    # If executed using:
    #
    # streamlit run sai_voiceos.py
    #
    # Streamlit mode runs.

    if IS_STREAMLIT:

        streamlit_app()

    else:

        windows_mode()
