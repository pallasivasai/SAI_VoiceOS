# ============================================================
# SAI VOICEOS
# ONE FILE - ALWAYS LISTENING VOICE-FIRST COMPUTER
# ============================================================
#
# SAI stays ON until the user says:
#
#   "off"
#   "turn off"
#   "shutdown SAI"
#   "exit SAI"
#
# Main capabilities:
#
# 1. Always listening
# 2. Voice -> Text
# 3. Text -> Voice
# 4. Internet answers
# 5. Internet file download
# 6. GitHub file fetching
# 7. GitHub PDF reading
# 8. Local PDF reading
# 9. PDF search
# 10. Calculator
# 11. Browser
# 12. YouTube
# 13. WhatsApp
# 14. Notepad
# 15. Screenshot
# 16. Notes
# 17. Local file search
# 18. Weather
# 19. Function registry
#
# ============================================================


# ============================================================
# IMPORTS
# ============================================================

import os
import re
import io
import json
import base64
import queue
import random
import threading
import datetime
import urllib.parse
import urllib.request
import webbrowser
import subprocess
from pathlib import Path


# ============================================================
# OPTIONAL / EXTERNAL LIBRARIES
# ============================================================

try:
    import requests
except ImportError:
    requests = None

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

try:
    import speech_recognition as sr
except ImportError:
    sr = None

try:
    import sounddevice as sd
except ImportError:
    sd = None

try:
    import scipy.io.wavfile as wav
except ImportError:
    wav = None

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

try:
    import pyautogui
except ImportError:
    pyautogui = None

try:
    import pyjokes
except ImportError:
    pyjokes = None

try:
    import tkinter as tk
    from tkinter import ttk
except ImportError:
    tk = None
    ttk = None


# ============================================================
# CONFIGURATION
# ============================================================

APP_NAME = "SAI VoiceOS"

HOME = Path.home()

DOWNLOADS = HOME / "Downloads"
DESKTOP = HOME / "Desktop"
PICTURES = HOME / "Pictures"

DOWNLOADS.mkdir(
    parents=True,
    exist_ok=True
)

DESKTOP.mkdir(
    parents=True,
    exist_ok=True
)

PICTURES.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# GITHUB CONFIGURATION
# ============================================================
#
# Public GitHub files can work without token.
#
# Private repositories need:
#
# setx SAI_GITHUB_TOKEN "YOUR_TOKEN"
#
# Optional default repository:
#
# setx SAI_GITHUB_REPOSITORY "username/repository"
#
# ============================================================

GITHUB_TOKEN = os.getenv(
    "SAI_GITHUB_TOKEN",
    ""
)

DEFAULT_GITHUB_REPOSITORY = os.getenv(
    "SAI_GITHUB_REPOSITORY",
    ""
)

DEFAULT_GITHUB_BRANCH = os.getenv(
    "SAI_GITHUB_BRANCH",
    "main"
)


# ============================================================
# GLOBAL STATE
# ============================================================

SAI_RUNNING = True

ui_queue = queue.Queue()

engine = None

if pyttsx3 is not None:

    try:

        engine = pyttsx3.init()

        engine.setProperty(
            "rate",
            150
        )

        engine.setProperty(
            "volume",
            1.0
        )

    except Exception:

        engine = None


# ============================================================
# UI
# ============================================================

class SAIInterface:

    def __init__(self):

        self.root = None
        self.output = None
        self.status = None
        self.input_box = None

        if tk is None:
            return

        self.root = tk.Tk()

        self.root.title(
            "SAI VoiceOS"
        )

        self.root.geometry(
            "1000x700"
        )

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.close
        )

        self.build()

        self.root.after(
            100,
            self.process_queue
        )


    def build(self):

        title = tk.Label(
            self.root,
            text="SAI VoiceOS",
            font=("Arial", 24, "bold")
        )

        title.pack(
            pady=10
        )

        self.status = tk.Label(
            self.root,
            text="● ALWAYS LISTENING",
            font=("Arial", 12, "bold")
        )

        self.status.pack(
            pady=5
        )

        frame = tk.Frame(
            self.root
        )

        frame.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=10
        )

        scrollbar = tk.Scrollbar(
            frame
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        self.output = tk.Text(
            frame,
            wrap="word",
            font=("Consolas", 13),
            yscrollcommand=scrollbar.set,
            state="disabled"
        )

        self.output.pack(
            fill="both",
            expand=True
        )

        scrollbar.config(
            command=self.output.yview
        )

        bottom = tk.Frame(
            self.root
        )

        bottom.pack(
            fill="x",
            padx=15,
            pady=10
        )

        self.input_box = tk.Entry(
            bottom,
            font=("Arial", 14)
        )

        self.input_box.pack(
            side="left",
            fill="x",
            expand=True
        )

        self.input_box.bind(
            "<Return>",
            self.submit_text
        )

        button = tk.Button(
            bottom,
            text="Send",
            font=("Arial", 12),
            command=self.submit_text
        )

        button.pack(
            side="right",
            padx=5
        )


    def add(self, speaker, text):

        message = (
            f"\n{speaker}\n"
            f"{text}\n"
            f"{'-' * 70}\n"
        )

        if self.output is not None:

            self.output.config(
                state="normal"
            )

            self.output.insert(
                "end",
                message
            )

            self.output.see(
                "end"
            )

            self.output.config(
                state="disabled"
            )

        else:

            print(message)


    def process_queue(self):

        try:

            while True:

                item = ui_queue.get_nowait()

                if item[0] == "sai":

                    self.add(
                        "SAI",
                        item[1]
                    )

                elif item[0] == "user":

                    self.add(
                        "YOU",
                        item[1]
                    )

                elif item[0] == "status":

                    if self.status:

                        self.status.config(
                            text=item[1]
                        )

                elif item[0] == "close":

                    self.root.destroy()

                    return

        except queue.Empty:

            pass

        if self.root:

            self.root.after(
                100,
                self.process_queue
            )


    def submit_text(self, event=None):

        if not self.input_box:

            return

        text = self.input_box.get().strip()

        self.input_box.delete(
            0,
            "end"
        )

        if text:

            ui_queue.put(
                (
                    "user",
                    text
                )
            )

            threading.Thread(
                target=process_command,
                args=(text,),
                daemon=True
            ).start()


    def close(self):

        global SAI_RUNNING

        SAI_RUNNING = False

        ui_queue.put(
            (
                "close",
                ""
            )
        )


    def run(self):

        if self.root:

            self.root.mainloop()


# ============================================================
# UI INSTANCE
# ============================================================

UI = SAIInterface()


# ============================================================
# SPEAK
# ============================================================

def speak(text):

    if not text:
        return

    text = str(text)

    ui_queue.put(
        (
            "sai",
            text
        )
    )

    print(
        "SAI:",
        text
    )

    if engine is None:

        return

    try:

        engine.say(
            text
        )

        engine.runAndWait()

    except Exception as exc:

        print(
            "TTS error:",
            exc
        )


# ============================================================
# STATUS
# ============================================================

def set_status(text):

    ui_queue.put(
        (
            "status",
            text
        )
    )


# ============================================================
# ALWAYS LISTENING
# ============================================================

def listen_once():

    if (
        sd is None
        or sr is None
        or wav is None
    ):

        return None

    recognizer = sr.Recognizer()

    sample_rate = 44100

    # Small chunks make SAI continuously listen.
    seconds = 4

    try:

        set_status(
            "● ALWAYS LISTENING"
        )

        recording = sd.rec(
            int(
                seconds
                * sample_rate
            ),
            samplerate=sample_rate,
            channels=1,
            dtype="int16"
        )

        sd.wait()

        buffer = io.BytesIO()

        wav.write(
            buffer,
            sample_rate,
            recording
        )

        buffer.seek(0)

        with sr.AudioFile(
            buffer
        ) as source:

            audio = recognizer.record(
                source
            )

        query = recognizer.recognize_google(
            audio,
            language="en-in"
        )

        query = query.lower().strip()

        if query:

            ui_queue.put(
                (
                    "user",
                    query
                )
            )

            return query

    except sr.UnknownValueError:

        pass

    except sr.RequestError as exc:

        print(
            "Speech service error:",
            exc
        )

    except Exception as exc:

        print(
            "Microphone error:",
            exc
        )

    return None


def voice_loop():

    global SAI_RUNNING

    while SAI_RUNNING:

        query = listen_once()

        if not SAI_RUNNING:

            break

        if query:

            process_command(
                query
            )


# ============================================================
# INTERNET SEARCH
# ============================================================

def internet_search(query):

    query = query.strip()

    if not query:

        return

    encoded = urllib.parse.quote_plus(
        query
    )

    url = (
        "https://www.google.com/search?q="
        + encoded
    )

    try:

        webbrowser.open(
            url
        )

        speak(
            f"I opened internet search results for {query}."
        )

    except Exception:

        speak(
            "I could not open internet search."
        )


# ============================================================
# INTERNET ANSWER
# ============================================================

def internet_answer(query):

    """
    First try DuckDuckGo Instant Answer API.
    If no direct answer exists, open web search.
    """

    query = query.strip()

    if not query:

        return

    speak(
        f"Checking the internet for {query}."
    )

    try:

        encoded = urllib.parse.quote_plus(
            query
        )

        url = (
            "https://api.duckduckgo.com/"
            "?q="
            + encoded
            + "&format=json"
            + "&no_html=1"
            + "&skip_disambig=1"
        )

        request = urllib.request.Request(
            url,
            headers={
                "User-Agent":
                "SAI-VoiceOS/1.0"
            }
        )

        with urllib.request.urlopen(
            request,
            timeout=10
        ) as response:

            data = json.loads(
                response.read().decode(
                    "utf-8"
                )
            )

        answer = (
            data.get(
                "AbstractText",
                ""
            )
            or ""
        ).strip()

        if answer:

            speak(
                answer[:1800]
            )

            return

        related = []

        for item in data.get(
            "RelatedTopics",
            []
        )[:5]:

            if (
                isinstance(
                    item,
                    dict
                )
                and item.get("Text")
            ):

                related.append(
                    item["Text"]
                )

        if related:

            speak(
                " ".join(
                    related
                )[:1800]
            )

            return

    except Exception as exc:

        print(
            "Internet answer error:",
            exc
        )

    # Fallback
    internet_search(
        query
    )


# ============================================================
# INTERNET FILE DOWNLOAD
# ============================================================

def download_from_internet(
    url,
    filename=None
):

    try:

        url = url.strip()

        if not filename:

            parsed = urllib.parse.urlparse(
                url
            )

            filename = Path(
                parsed.path
            ).name

        if not filename:

            filename = (
                "sai_download"
            )

        destination = (
            DOWNLOADS
            / filename
        )

        speak(
            "Downloading the file from the internet."
        )

        request = urllib.request.Request(
            url,
            headers={
                "User-Agent":
                "Mozilla/5.0"
            }
        )

        with urllib.request.urlopen(
            request,
            timeout=60
        ) as response:

            data = response.read()

        destination.write_bytes(
            data
        )

        speak(
            f"Downloaded successfully to {destination}."
        )

        return str(
            destination
        )

    except Exception as exc:

        print(
            "Download error:",
            exc
        )

        speak(
            "I could not download that file."
        )

        return None


# ============================================================
# GITHUB URL PARSER
# ============================================================

def parse_github_path(
    github_path
):

    """
    Supports:

    owner/repo/file.pdf

    owner/repo/folder/file.pdf

    https://github.com/owner/repo/blob/main/file.pdf

    https://github.com/owner/repo/raw/main/file.pdf

    https://raw.githubusercontent.com/owner/repo/main/file.pdf
    """

    github_path = github_path.strip()

    # Raw GitHub URL
    if (
        github_path.startswith(
            "https://raw.githubusercontent.com/"
        )
    ):

        parts = urllib.parse.urlparse(
            github_path
        ).path.strip("/").split("/")

        if len(parts) >= 4:

            owner = parts[0]
            repo = parts[1]
            branch = parts[2]
            path = "/".join(
                parts[3:]
            )

            return (
                owner,
                repo,
                branch,
                path
            )

    # Normal GitHub URL
    if (
        github_path.startswith(
            "https://github.com/"
        )
    ):

        parts = urllib.parse.urlparse(
            github_path
        ).path.strip("/").split("/")

        if len(parts) >= 4:

            owner = parts[0]
            repo = parts[1]

            if parts[2] in (
                "blob",
                "raw"
            ):

                branch = parts[3]

                path = "/".join(
                    parts[4:]
                )

                return (
                    owner,
                    repo,
                    branch,
                    path
                )

    # owner/repo/path
    parts = github_path.strip(
        "/"
    ).split(
        "/"
    )

    if len(parts) >= 3:

        owner = parts[0]
        repo = parts[1]

        path = "/".join(
            parts[2:]
        )

        return (
            owner,
            repo,
            DEFAULT_GITHUB_BRANCH,
            path
        )

    # Default repository
    if DEFAULT_GITHUB_REPOSITORY:

        default_parts = (
            DEFAULT_GITHUB_REPOSITORY
            .split("/")
        )

        if len(default_parts) == 2:

            return (
                default_parts[0],
                default_parts[1],
                DEFAULT_GITHUB_BRANCH,
                github_path.strip("/")
            )

    return None


# ============================================================
# GITHUB FILE DOWNLOAD
# ============================================================

def download_from_github(
    github_path
):

    parsed = parse_github_path(
        github_path
    )

    if not parsed:

        speak(
            "I could not understand the GitHub path."
        )

        return None

    owner, repo, branch, path = parsed

    try:

        # Use GitHub raw URL for public files.
        raw_url = (
            "https://raw.githubusercontent.com/"
            f"{owner}/{repo}/{branch}/{path}"
        )

        headers = {
            "User-Agent":
            "SAI-VoiceOS/1.0"
        }

        if GITHUB_TOKEN:

            headers[
                "Authorization"
            ] = (
                f"Bearer {GITHUB_TOKEN}"
            )

        request = urllib.request.Request(
            raw_url,
            headers=headers
        )

        with urllib.request.urlopen(
            request,
            timeout=30
        ) as response:

            data = response.read()

        filename = Path(
            path
        ).name

        destination = (
            DOWNLOADS
            / filename
        )

        destination.write_bytes(
            data
        )

        speak(
            f"GitHub file downloaded to {destination}."
        )

        return str(
            destination
        )

    except Exception as exc:

        print(
            "GitHub download error:",
            exc
        )

        speak(
            "I could not fetch that GitHub file."
        )

        return None


# ============================================================
# GITHUB FILE READER
# ============================================================

def read_github_file(
    github_path
):

    local_file = download_from_github(
        github_path
    )

    if not local_file:

        return

    extension = (
        Path(
            local_file
        )
        .suffix
        .lower()
    )

    if extension == ".pdf":

        read_pdf(
            local_file
        )

    elif extension in (
        ".txt",
        ".md",
        ".csv",
        ".json",
        ".py",
        ".html",
        ".xml"
    ):

        read_text_file(
            local_file
        )

    else:

        speak(
            f"I downloaded {Path(local_file).name}. "
            "This file type is not a text document."
        )


# ============================================================
# PDF READER
# ============================================================

def read_pdf(
    pdf_path,
    page_number=None
):

    if PdfReader is None:

        speak(
            "PDF support is not installed."
        )

        return

    pdf_path = Path(
        pdf_path
    ).expanduser().resolve()

    if not pdf_path.exists():

        speak(
            "I could not find that PDF."
        )

        return

    try:

        reader = PdfReader(
            str(pdf_path)
        )

        total = len(
            reader.pages
        )

        if page_number is not None:

            if (
                page_number < 1
                or page_number > total
            ):

                speak(
                    f"The PDF has {total} pages."
                )

                return

            text = (
                reader
                .pages[
                    page_number - 1
                ]
                .extract_text()
                or ""
            )

            if not text.strip():

                speak(
                    "That page has no extractable text."
                )

                return

            speak(
                text[:5000]
            )

            return

        speak(
            f"The PDF contains {total} pages."
        )

        for number, page in enumerate(
            reader.pages,
            start=1
        ):

            text = (
                page.extract_text()
                or ""
            )

            if not text.strip():

                continue

            speak(
                f"Page {number}."
            )

            # Read in chunks
            for start in range(
                0,
                len(text),
                1200
            ):

                speak(
                    text[
                        start:
                        start + 1200
                    ]
                )

    except Exception as exc:

        print(
            "PDF error:",
            exc
        )

        speak(
            "I could not read the PDF."
        )


# ============================================================
# SEARCH INSIDE PDF
# ============================================================

def search_pdf(
    pdf_path,
    search_term
):

    if PdfReader is None:

        speak(
            "PDF support is not installed."
        )

        return

    pdf_path = Path(
        pdf_path
    ).expanduser().resolve()

    if not pdf_path.exists():

        speak(
            "I could not find that PDF."
        )

        return

    try:

        reader = PdfReader(
            str(pdf_path)
        )

        matches = []

        for number, page in enumerate(
            reader.pages,
            start=1
        ):

            text = (
                page.extract_text()
                or ""
            )

            if (
                search_term.lower()
                in text.lower()
            ):

                matches.append(
                    (
                        number,
                        text
                    )
                )

        if not matches:

            speak(
                f"I could not find {search_term} in the PDF."
            )

            return

        speak(
            f"I found {search_term} "
            f"on {len(matches)} page(s)."
        )

        for number, text in matches:

            position = text.lower().find(
                search_term.lower()
            )

            start = max(
                0,
                position - 350
            )

            end = min(
                len(text),
                position + 1200
            )

            speak(
                f"Page {number}."
            )

            speak(
                text[start:end]
            )

    except Exception as exc:

        print(
            "PDF search error:",
            exc
        )

        speak(
            "I could not search the PDF."
        )


# ============================================================
# TEXT FILE READER
# ============================================================

def read_text_file(
    file_path
):

    file_path = Path(
        file_path
    ).expanduser().resolve()

    if not file_path.exists():

        speak(
            "I could not find that file."
        )

        return

    try:

        text = file_path.read_text(
            encoding="utf-8",
            errors="ignore"
        )

        if not text.strip():

            speak(
                "The file is empty."
            )

            return

        for start in range(
            0,
            len(text),
            1500
        ):

            speak(
                text[
                    start:
                    start + 1500
                ]
            )

    except Exception as exc:

        print(
            "Text reader error:",
            exc
        )

        speak(
            "I could not read that file."
        )


# ============================================================
# CALCULATOR
# ============================================================

def calculate(
    expression
):

    expression = expression.lower()

    replacements = {

        "multiplied by": "*",
        "multiply by": "*",
        "times": "*",

        "plus": "+",
        "minus": "-",

        "divided by": "/",
        "divide by": "/",

        "over": "/"

    }

    for word, symbol in replacements.items():

        expression = expression.replace(
            word,
            symbol
        )

    expression = re.sub(
        r"(?<=\d)\s*x\s*(?=\d)",
        "*",
        expression
    )

    expression = expression.replace(
        "what is",
        ""
    )

    expression = expression.replace(
        "calculate",
        ""
    )

    expression = expression.replace(
        "?",
        ""
    )

    # Security:
    # Only mathematical characters allowed.
    cleaned = re.sub(
        r"[^0-9+\-*/().%\s]",
        "",
        expression
    )

    if not cleaned.strip():

        speak(
            "I could not understand the calculation."
        )

        return

    try:

        result = eval(
            cleaned,
            {
                "__builtins__":
                {}
            },
            {}
        )

        if (
            isinstance(
                result,
                float
            )
            and result.is_integer()
        ):

            result = int(
                result
            )

        speak(
            f"The answer is {result}."
        )

    except Exception:

        speak(
            "Sorry, I could not calculate that."
        )


# ============================================================
# WINDOWS APPLICATIONS
# ============================================================

def open_calculator():

    speak(
        "Opening Calculator."
    )

    try:

        subprocess.Popen(
            ["calc.exe"]
        )

    except Exception:

        os.system(
            "start calc"
        )


def open_notepad():

    speak(
        "Opening Notepad."
    )

    try:

        subprocess.Popen(
            ["notepad.exe"]
        )

    except Exception:

        speak(
            "I could not open Notepad."
        )


def open_browser():

    speak(
        "Opening the browser."
    )

    webbrowser.open(
        "https://www.google.com/"
    )


def open_google():

    speak(
        "Opening Google."
    )

    webbrowser.open(
        "https://www.google.com/"
    )


def open_youtube():

    speak(
        "Opening YouTube."
    )

    webbrowser.open(
        "https://www.youtube.com/"
    )


def search_youtube(
    topic
):

    url = (
        "https://www.youtube.com/results"
        "?search_query="
        + urllib.parse.quote_plus(
            topic
        )
    )

    webbrowser.open(
        url
    )

    speak(
        f"Searching YouTube for {topic}."
    )


def open_whatsapp():

    speak(
        "Opening WhatsApp."
    )

    try:

        os.startfile(
            "whatsapp:"
        )

        return

    except Exception:

        pass

    webbrowser.open(
        "https://web.whatsapp.com/"
    )


# ============================================================
# SCREENSHOT
# ============================================================

def take_screenshot():

    if pyautogui is None:

        speak(
            "Screenshot support is not installed."
        )

        return

    try:

        image = pyautogui.screenshot()

        path = (
            PICTURES
            / "sai_voiceos_screenshot.png"
        )

        image.save(
            path
        )

        speak(
            f"Screenshot saved to {path}."
        )

    except Exception:

        speak(
            "I could not take the screenshot."
        )


# ============================================================
# NOTES
# ============================================================

def write_note(
    text
):

    path = (
        DESKTOP
        / "sai_voiceos_notes.txt"
    )

    timestamp = datetime.datetime.now().strftime(
        "%Y-%m-%d %H:%M"
    )

    try:

        with open(
            path,
            "a",
            encoding="utf-8"
        ) as file:

            file.write(
                f"[{timestamp}] {text}\n"
            )

        speak(
            "The note has been saved."
        )

    except Exception:

        speak(
            "I could not save the note."
        )


# ============================================================
# LOCAL FILE SEARCH
# ============================================================

def find_local_file(
    filename
):

    speak(
        f"Searching your computer for {filename}."
    )

    matches = []

    try:

        for root, dirs, files in os.walk(
            HOME
        ):

            dirs[:] = [
                d
                for d in dirs
                if d.lower()
                not in {
                    "appdata",
                    "node_modules",
                    ".git"
                }
            ]

            for file in files:

                if (
                    filename.lower()
                    in file.lower()
                ):

                    matches.append(
                        Path(root)
                        / file
                    )

                    if len(matches) >= 10:

                        break

            if len(matches) >= 10:

                break

    except Exception as exc:

        print(
            "File search error:",
            exc
        )

    if not matches:

        speak(
            f"I could not find {filename}."
        )

        return

    speak(
        f"I found {len(matches)} file(s)."
    )

    for path in matches:

        speak(
            str(path)
        )


# ============================================================
# WEATHER
# ============================================================

def weather(
    city="Guntur"
):

    try:

        encoded = urllib.parse.quote(
            city
        )

        url = (
            f"https://wttr.in/"
            f"{encoded}?format=j1"
        )

        request = urllib.request.Request(
            url,
            headers={
                "User-Agent":
                "SAI-VoiceOS/1.0"
            }
        )

        with urllib.request.urlopen(
            request,
            timeout=10
        ) as response:

            data = json.loads(
                response.read().decode(
                    "utf-8"
                )
            )

        current = (
            data[
                "current_condition"
            ][0]
        )

        temperature = current[
            "temp_C"
        ]

        description = current[
            "weatherDesc"
        ][0]["value"]

        speak(
            f"The current temperature in "
            f"{city} is {temperature} degrees Celsius "
            f"with {description}."
        )

    except Exception:

        speak(
            "I could not get the weather."
        )


# ============================================================
# JOKE
# ============================================================

def tell_joke():

    if pyjokes is None:

        speak(
            "Joke support is not installed."
        )

        return

    try:

        speak(
            pyjokes.get_joke()
        )

    except Exception:

        speak(
            "I could not get a joke."
        )


# ============================================================
# GITHUB -> PDF -> READ
# ============================================================

def github_pdf(
    github_path
):

    local_file = download_from_github(
        github_path
    )

    if local_file:

        read_pdf(
            local_file
        )


# ============================================================
# GITHUB -> PDF -> SEARCH
# ============================================================

def github_pdf_search(
    github_path,
    search_term
):

    local_file = download_from_github(
        github_path
    )

    if local_file:

        search_pdf(
            local_file,
            search_term
        )


# ============================================================
# COMMAND HELP
# ============================================================

def show_help():

    speak(
        "You can ask me to open applications, "
        "calculate numbers, search the internet, "
        "download files, read PDFs, search PDFs, "
        "read GitHub files, search GitHub PDFs, "
        "take screenshots, write notes, "
        "find local files, or tell you the weather."
    )


# ============================================================
# FUNCTION REGISTRY
# ============================================================
#
# THIS IS THE IMPORTANT PART.
#
# Every capability has a function.
#
# Future functions can be added here.
#
# ============================================================

SAI_FUNCTIONS = {

    "calculator":
        calculate,

    "internet_search":
        internet_search,

    "internet_answer":
        internet_answer,

    "internet_download":
        download_from_internet,

    "github_download":
        download_from_github,

    "github_read":
        read_github_file,

    "github_pdf":
        github_pdf,

    "github_pdf_search":
        github_pdf_search,

    "pdf_read":
        read_pdf,

    "pdf_search":
        search_pdf,

    "text_read":
        read_text_file,

    "local_file_search":
        find_local_file,

    "open_calculator":
        open_calculator,

    "open_notepad":
        open_notepad,

    "open_browser":
        open_browser,

    "open_google":
        open_google,

    "open_youtube":
        open_youtube,

    "youtube_search":
        search_youtube,

    "open_whatsapp":
        open_whatsapp,

    "screenshot":
        take_screenshot,

    "write_note":
        write_note,

    "weather":
        weather,

    "joke":
        tell_joke,

    "help":
        show_help

}


# ============================================================
# COMMAND PROCESSOR
# ============================================================

def process_command(
    query
):

    global SAI_RUNNING

    if not query:

        return

    query = query.strip()

    # --------------------------------------------------------
    # OFF
    # --------------------------------------------------------

    if query in (
        "off",
        "turn off",
        "switch off",
        "shutdown sai",
        "exit sai",
        "quit sai",
        "stop sai"
    ):

        speak(
            "SAI VoiceOS is turning off."
        )

        SAI_RUNNING = False

        return


    # --------------------------------------------------------
    # HELP
    # --------------------------------------------------------

    if (
        query == "help"
        or "what can you do" in query
    ):

        show_help()

        return


    # --------------------------------------------------------
    # TIME
    # --------------------------------------------------------

    if (
        query == "time"
        or "what time is it" in query
    ):

        current = datetime.datetime.now().strftime(
            "%I:%M %p"
        )

        speak(
            f"The current time is {current}."
        )

        return


    # --------------------------------------------------------
    # DATE
    # --------------------------------------------------------

    if (
        query == "date"
        or "what is the date" in query
    ):

        today = datetime.datetime.now().strftime(
            "%d %B %Y"
        )

        speak(
            f"Today's date is {today}."
        )

        return


    # --------------------------------------------------------
    # CALCULATOR
    # --------------------------------------------------------

    if (
        re.search(
            r"\d+\s*(?:\+|-|\*|/|x|×)\s*\d+",
            query
        )
        or query.startswith(
            "calculate "
        )
        or (
            "what is " in query
            and any(
                word in query
                for word in [
                    "plus",
                    "minus",
                    "times",
                    "divided"
                ]
            )
        )
    ):

        calculate(
            query
        )

        return


    # --------------------------------------------------------
    # WEATHER
    # --------------------------------------------------------

    if "weather" in query:

        match = re.search(
            r"weather\s+(?:in|at|for)\s+(.+)",
            query
        )

        if match:

            weather(
                match.group(1).strip()
            )

        else:

            weather()

        return


    # --------------------------------------------------------
    # OPEN CALCULATOR
    # --------------------------------------------------------

    if (
        "open calculator" in query
        or "open calc" in query
    ):

        open_calculator()

        return


    # --------------------------------------------------------
    # OPEN NOTEPAD
    # --------------------------------------------------------

    if "open notepad" in query:

        open_notepad()

        return


    # --------------------------------------------------------
    # OPEN WHATSAPP
    # --------------------------------------------------------

    if "open whatsapp" in query:

        open_whatsapp()

        return


    # --------------------------------------------------------
    # OPEN YOUTUBE
    # --------------------------------------------------------

    if "open youtube" in query:

        open_youtube()

        return


    # --------------------------------------------------------
    # SEARCH YOUTUBE
    # --------------------------------------------------------

    if (
        "search youtube for" in query
        or "youtube search" in query
        or "play on youtube" in query
    ):

        topic = query

        for phrase in [
            "search youtube for",
            "youtube search",
            "play on youtube"
        ]:

            topic = topic.replace(
                phrase,
                ""
            )

        search_youtube(
            topic.strip()
        )

        return


    # --------------------------------------------------------
    # OPEN BROWSER
    # --------------------------------------------------------

    if (
        "open browser" in query
        or "open chrome" in query
    ):

        open_browser()

        return


    # --------------------------------------------------------
    # GOOGLE SEARCH
    # --------------------------------------------------------

    if (
        "search google for" in query
        or "search on google" in query
    ):

        topic = query

        topic = topic.replace(
            "search google for",
            ""
        )

        topic = topic.replace(
            "search on google",
            ""
        )

        internet_search(
            topic.strip()
        )

        return


    # --------------------------------------------------------
    # INTERNET DOWNLOAD
    # --------------------------------------------------------
    #
    # Example:
    #
    # download https://example.com/file.pdf
    #
    # --------------------------------------------------------

    if (
        query.startswith(
            "download "
        )
        or "download this file" in query
    ):

        url = query

        url = url.replace(
            "download this file",
            ""
        )

        url = url.replace(
            "download",
            ""
        )

        url = url.strip()

        if (
            url.startswith(
                "http://"
            )
            or url.startswith(
                "https://"
            )
        ):

            download_from_internet(
                url
            )

        else:

            speak(
                "Please give me the internet file URL."
            )

        return


    # --------------------------------------------------------
    # GITHUB READ
    # --------------------------------------------------------
    #
    # Examples:
    #
    # read github owner/repo/file.pdf
    #
    # read this github file
    #
    # --------------------------------------------------------

    if (
        "read github" in query
        or "read this github file" in query
        or "read github file" in query
    ):

        path = query

        for phrase in [
            "read this github file",
            "read github file",
            "read github"
        ]:

            path = path.replace(
                phrase,
                ""
            )

        path = path.strip()

        if path:

            read_github_file(
                path
            )

        else:

            speak(
                "Please give me the GitHub repository path."
            )

        return


    # --------------------------------------------------------
    # GITHUB PDF SEARCH
    # --------------------------------------------------------

    if (
        "search github pdf" in query
        or "find in github pdf" in query
    ):

        speak(
            "Tell me the GitHub PDF path."
        )

        path = listen_once()

        if not path:

            return

        speak(
            "What should I search for?"
        )

        term = listen_once()

        if term:

            github_pdf_search(
                path,
                term
            )

        return


    # --------------------------------------------------------
    # LOCAL PDF
    # --------------------------------------------------------

    if (
        "read pdf" in query
        or "read this pdf" in query
    ):

        path = query

        path = path.replace(
            "read this pdf",
            ""
        )

        path = path.replace(
            "read pdf",
            ""
        )

        path = path.strip()

        if path:

            read_pdf(
                path
            )

        else:

            speak(
                "Please give me the PDF file path."
            )

        return


    # --------------------------------------------------------
    # PDF SEARCH
    # --------------------------------------------------------

    if (
        "search in pdf" in query
        or "find in pdf" in query
    ):

        speak(
            "Tell me the PDF path."
        )

        path = listen_once()

        if not path:

            return

        speak(
            "What should I search for?"
        )

        term = listen_once()

        if term:

            search_pdf(
                path,
                term
            )

        return


    # --------------------------------------------------------
    # FIND LOCAL FILE
    # --------------------------------------------------------

    if (
        "find file" in query
        or "search for file" in query
    ):

        name = query

        name = name.replace(
            "find file",
            ""
        )

        name = name.replace(
            "search for file",
            ""
        )

        name = name.strip()

        if name:

            find_local_file(
                name
            )

        return


    # --------------------------------------------------------
    # SCREENSHOT
    # --------------------------------------------------------

    if "screenshot" in query:

        take_screenshot()

        return


    # --------------------------------------------------------
    # NOTE
    # --------------------------------------------------------

    if (
        query.startswith(
            "note "
        )
        or query.startswith(
            "write note "
        )
    ):

        note = query

        note = note.replace(
            "write note ",
            ""
        )

        note = note.replace(
            "note ",
            ""
        )

        write_note(
            note.strip()
        )

        return


    # --------------------------------------------------------
    # JOKE
    # --------------------------------------------------------

    if (
        "tell me a joke" in query
        or query == "joke"
    ):

        tell_joke()

        return


    # --------------------------------------------------------
    # GENERIC OPEN
    # --------------------------------------------------------

    if query.startswith(
        "open "
    ):

        app = query[
            len("open "):
        ].strip()

        if "calculator" in app:

            open_calculator()

        elif "notepad" in app:

            open_notepad()

        elif "whatsapp" in app:

            open_whatsapp()

        elif "youtube" in app:

            open_youtube()

        elif (
            "browser" in app
            or "chrome" in app
        ):

            open_browser()

        elif "google" in app:

            open_google()

        else:

            speak(
                f"I don't have a local function "
                f"for {app} yet."
            )

            internet_search(
                f"how to open {app}"
            )

        return


    # --------------------------------------------------------
    # GENERAL INTERNET QUESTION
    # --------------------------------------------------------

    internet_answer(
        query
    )


# ============================================================
# STARTUP
# ============================================================

def startup():

    speak(
        "Welcome to SAI VoiceOS."
    )

    speak(
        "I am always listening."
    )

    speak(
        "You can ask me anything or ask me "
        "to control your computer."
    )

    speak(
        "Say off whenever you want me to stop."
    )


# ============================================================
# MAIN
# ============================================================

def main():

    global SAI_RUNNING

    startup()

    # Voice listening thread
    threading.Thread(
        target=voice_loop,
        daemon=True
    ).start()

    # UI thread stays in main thread
    if UI.root:

        UI.run()

    else:

        # Fallback terminal mode
        while SAI_RUNNING:

            try:

                query = input(
                    "\nYOU: "
                ).strip()

                if query:

                    process_command(
                        query
                    )

            except KeyboardInterrupt:

                SAI_RUNNING = False

                break

    speak(
        "SAI VoiceOS has stopped."
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()
