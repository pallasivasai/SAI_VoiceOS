# ============================================================
# SAI VOICEOS - COMPLETE VOICE-FIRST DESKTOP ASSISTANT
# ============================================================
#
# Voice -> Speech-to-Text -> Intent -> Function
#      -> Local Computer / Internet / GitHub / Documents
#      -> Voice Response
#
# API / TOKEN values are NOT hard-coded.
# Configure them later using environment variables.
#
# ============================================================

import os
import io
import re
import json
import base64
import random
import datetime
import urllib.request
import urllib.parse
import webbrowser as wb
import subprocess
import pathlib

import pyttsx3
import speech_recognition as sr
import pyautogui
import pyjokes
import requests
import sounddevice as sd
import scipy.io.wavfile as wav

from pypdf import PdfReader


# ============================================================
# CONFIGURATION
# ============================================================

APP_NAME = "SAI VoiceOS"

# GitHub configuration
# DO NOT put your token directly inside this Python file.

GITHUB_TOKEN = os.getenv("SAI_GITHUB_TOKEN")

GITHUB_REPOSITORY = os.getenv(
    "SAI_GITHUB_REPOSITORY",
    "YOUR_USERNAME/YOUR_REPOSITORY"
)

GITHUB_BRANCH = os.getenv(
    "SAI_GITHUB_BRANCH",
    "main"
)


# ============================================================
# TEXT TO SPEECH
# ============================================================

engine = pyttsx3.init()

voices = engine.getProperty("voices")

if voices:
    try:
        engine.setProperty(
            "voice",
            voices[0].id
        )
    except Exception:
        pass

engine.setProperty("rate", 150)
engine.setProperty("volume", 1.0)


def speak(text):
    """Speak text and also print it."""

    if not text:
        return

    text = str(text)

    print(f"\nSAI: {text}")

    try:
        engine.say(text)
        engine.runAndWait()

    except Exception as e:
        print(f"TTS error: {e}")


# ============================================================
# SPEECH TO TEXT
# ============================================================

def take_command():

    recognizer = sr.Recognizer()

    sample_rate = 44100
    seconds = 5

    print("\n" + "=" * 60)
    print("Listening...")
    print("=" * 60)

    try:

        recording = sd.rec(
            int(seconds * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype="int16"
        )

        sd.wait()

        print("Processing audio...")

        audio_buffer = io.BytesIO()

        wav.write(
            audio_buffer,
            sample_rate,
            recording
        )

        audio_buffer.seek(0)

        with sr.AudioFile(audio_buffer) as source:

            audio = recognizer.record(source)

    except Exception as e:

        print(f"Microphone error: {e}")

        speak(
            "Microphone access failed. "
            "Please check your microphone."
        )

        return None

    try:

        print("Recognizing...")

        query = recognizer.recognize_google(
            audio,
            language="en-in"
        )

        query = query.lower().strip()

        print(f"\nYOU: {query}")

        return query

    except sr.UnknownValueError:

        speak(
            "Sorry, I could not understand that."
        )

        return None

    except sr.RequestError:

        speak(
            "Speech recognition service is unavailable."
        )

        return None

    except Exception as e:

        print(
            f"Speech recognition error: {e}"
        )

        return None


# ============================================================
# GREETING
# ============================================================

def wishme():

    hour = datetime.datetime.now().hour

    speak(
        f"Welcome to {APP_NAME}."
    )

    if 4 <= hour < 12:

        speak("Good morning.")

    elif 12 <= hour < 16:

        speak("Good afternoon.")

    elif 16 <= hour < 22:

        speak("Good evening.")

    else:

        speak("Good night.")

    speak(
        "I am ready. "
        "You can ask me questions, "
        "search the internet, "
        "control your computer, "
        "or manage your GitHub files."
    )


# ============================================================
# TIME
# ============================================================

def tell_time():

    current_time = datetime.datetime.now().strftime(
        "%I:%M %p"
    )

    speak(
        f"The current time is {current_time}."
    )


# ============================================================
# DATE
# ============================================================

def tell_date():

    now = datetime.datetime.now()

    current_date = now.strftime(
        "%d %B %Y"
    )

    speak(
        f"Today's date is {current_date}."
    )


# ============================================================
# CALCULATOR
# ============================================================

def calculate(expression):

    if not expression:

        speak(
            "I could not understand the calculation."
        )

        return

    expression = expression.lower()

    replacements = {

        "multiplied by": "*",
        "multiply by": "*",
        "times": "*",
        "plus": "+",
        "minus": "-",
        "divided by": "/",
        "divide by": "/",
        "over": "/",
        "power": "**",
        "modulo": "%",
        "percent": "%"

    }

    for word, symbol in replacements.items():

        expression = expression.replace(
            word,
            symbol
        )

    # Handle x as multiplication
    expression = re.sub(
        r"(?<=\d)\s*x\s*(?=\d)",
        "*",
        expression
    )

    # Remove question words
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

    # Only allow mathematical characters
    cleaned = re.sub(
        r"[^0-9+\-*/().%\s]",
        "",
        expression
    )

    if not cleaned.strip():

        speak(
            "That does not look like a valid calculation."
        )

        return

    try:

        result = eval(
            cleaned,
            {
                "__builtins__": {}
            },
            {}
        )

        if isinstance(result, float):

            if result.is_integer():

                result = int(result)

        speak(
            f"The answer is {result}."
        )

    except Exception as e:

        print(
            f"Calculator error: {e}"
        )

        speak(
            "Sorry, I could not calculate that."
        )


# ============================================================
# INTERNET SEARCH
# ============================================================

def internet_search(query):

    if not query:

        speak(
            "What would you like me to search for?"
        )

        return

    speak(
        f"Searching the internet for {query}."
    )

    encoded = urllib.parse.quote_plus(
        query
    )

    url = (
        "https://www.google.com/search?q="
        + encoded
    )

    try:

        wb.open(url)

        speak(
            "I opened the search results."
        )

    except Exception as e:

        print(
            f"Internet search error: {e}"
        )

        speak(
            "I could not open the search results."
        )


# ============================================================
# INTERNET ANSWER
# ============================================================

def web_answer(query):

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
            f"?q={encoded}"
            "&format=json"
            "&no_html=1"
            "&skip_disambig=1"
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

        answer = data.get(
            "AbstractText",
            ""
        ).strip()

        if answer:

            if len(answer) > 1000:

                answer = (
                    answer[:1000]
                    + "..."
                )

            speak(answer)

            return

        # Related topics fallback
        related = data.get(
            "RelatedTopics",
            []
        )

        results = []

        for item in related[:5]:

            if isinstance(item, dict):

                text = item.get(
                    "Text",
                    ""
                ).strip()

                if text:

                    results.append(text)

        if results:

            answer = " ".join(results)

            if len(answer) > 1000:

                answer = (
                    answer[:1000]
                    + "..."
                )

            speak(answer)

            return

        speak(
            "I could not find a direct answer. "
            "I will open the search results."
        )

        internet_search(query)

    except Exception as e:

        print(
            f"Web answer error: {e}"
        )

        speak(
            "I could not get a direct web answer. "
            "I will open the search results."
        )

        internet_search(query)


# ============================================================
# WEATHER
# ============================================================

def get_weather(city="Guntur"):

    try:

        speak(
            f"Checking the weather for {city}."
        )

        encoded_city = urllib.parse.quote(
            city
        )

        url = (
            f"https://wttr.in/"
            f"{encoded_city}?format=j1"
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
            timeout=10
        ) as response:

            data = json.loads(
                response.read().decode(
                    "utf-8"
                )
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

        report = (
            f"The current temperature "
            f"in {city} is "
            f"{temperature} degrees Celsius "
            f"with {description}."
        )

        speak(report)

    except Exception as e:

        print(
            f"Weather error: {e}"
        )

        speak(
            "Sorry, I could not get "
            "the weather right now."
        )


# ============================================================
# GOOGLE
# ============================================================

def open_google():

    speak(
        "Opening Google."
    )

    wb.open(
        "https://www.google.com/"
    )


# ============================================================
# BROWSER
# ============================================================

def open_browser():

    speak(
        "Opening the browser."
    )

    try:

        wb.open(
            "https://www.google.com/"
        )

    except Exception:

        speak(
            "I could not open the browser."
        )


# ============================================================
# YOUTUBE
# ============================================================

def open_youtube():

    speak(
        "Opening YouTube."
    )

    wb.open(
        "https://www.youtube.com/"
    )


def play_on_youtube(topic):

    if not topic:

        open_youtube()

        return

    speak(
        f"Searching YouTube for {topic}."
    )

    encoded = urllib.parse.quote_plus(
        topic
    )

    url = (
        "https://www.youtube.com/results"
        "?search_query="
        + encoded
    )

    wb.open(url)


# ============================================================
# WHATSAPP
# ============================================================

def open_whatsapp():

    speak(
        "Opening WhatsApp."
    )

    # Try WhatsApp Desktop
    try:

        os.startfile(
            "whatsapp:"
        )

        return

    except Exception:
        pass

    # Fallback to WhatsApp Web
    try:

        wb.open(
            "https://web.whatsapp.com/"
        )

    except Exception:

        speak(
            "I could not open WhatsApp."
        )


# ============================================================
# CALCULATOR APP
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

        try:

            os.system(
                "start calc"
            )

        except Exception:

            speak(
                "I could not open Calculator."
            )


# ============================================================
# NOTEPAD
# ============================================================

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


# ============================================================
# GENERIC APPLICATION
# ============================================================

def open_application(app_name):

    app_name = app_name.lower().strip()

    if (
        "calculator" in app_name
        or "calc" in app_name
    ):

        open_calculator()

    elif (
        "notepad" in app_name
        or "text editor" in app_name
    ):

        open_notepad()

    elif "whatsapp" in app_name:

        open_whatsapp()

    elif "youtube" in app_name:

        open_youtube()

    elif (
        "browser" in app_name
        or "chrome" in app_name
    ):

        open_browser()

    elif "google" in app_name:

        open_google()

    else:

        speak(
            f"I don't have a local action "
            f"for {app_name} yet."
        )

        speak(
            "I will search the internet instead."
        )

        internet_search(
            f"how to open {app_name}"
        )


# ============================================================
# SCREENSHOT
# ============================================================

def take_screenshot():

    try:

        image = pyautogui.screenshot()

        pictures = os.path.join(
            os.path.expanduser("~"),
            "Pictures"
        )

        os.makedirs(
            pictures,
            exist_ok=True
        )

        path = os.path.join(
            pictures,
            "sai_voiceos_screenshot.png"
        )

        image.save(path)

        speak(
            "Screenshot captured successfully."
        )

        print(
            f"Screenshot saved to: {path}"
        )

    except Exception as e:

        print(
            f"Screenshot error: {e}"
        )

        speak(
            "I could not take the screenshot."
        )


# ============================================================
# MUSIC
# ============================================================

def play_music(song_name=""):

    music_folder = os.path.join(
        os.path.expanduser("~"),
        "Music"
    )

    if not os.path.exists(
        music_folder
    ):

        speak(
            "I could not find your Music folder."
        )

        return

    try:

        songs = os.listdir(
            music_folder
        )

    except Exception:

        speak(
            "I could not access your Music folder."
        )

        return

    extensions = (
        ".mp3",
        ".wav",
        ".flac",
        ".m4a",
        ".aac"
    )

    songs = [
        song
        for song in songs
        if song.lower().endswith(
            extensions
        )
    ]

    if song_name:

        matching = [
            song
            for song in songs
            if song_name.lower()
            in song.lower()
        ]

        songs = matching

    if not songs:

        speak(
            "I could not find that song."
        )

        return

    song = random.choice(
        songs
    )

    try:

        os.startfile(
            os.path.join(
                music_folder,
                song
            )
        )

        speak(
            f"Playing {song}."
        )

    except Exception:

        speak(
            "I could not play that song."
        )


# ============================================================
# NOTES
# ============================================================

def write_note():

    speak(
        "What would you like me to write?"
    )

    note = take_command()

    if not note:

        speak(
            "I could not catch the note."
        )

        return

    desktop = os.path.join(
        os.path.expanduser("~"),
        "Desktop"
    )

    os.makedirs(
        desktop,
        exist_ok=True
    )

    note_path = os.path.join(
        desktop,
        "sai_voiceos_notes.txt"
    )

    timestamp = datetime.datetime.now().strftime(
        "%Y-%m-%d %H:%M"
    )

    try:

        with open(
            note_path,
            "a",
            encoding="utf-8"
        ) as file:

            file.write(
                f"[{timestamp}] "
                f"{note}\n"
            )

        speak(
            "Your note has been saved "
            "to the desktop."
        )

    except Exception as e:

        print(
            f"Note error: {e}"
        )

        speak(
            "I could not save the note."
        )


# ============================================================
# JOKE
# ============================================================

def tell_joke():

    try:

        joke = pyjokes.get_joke()

        speak(joke)

    except Exception:

        speak(
            "Sorry, I could not find a joke."
        )


# ============================================================
# GITHUB CONFIG CHECK
# ============================================================

def github_ready():

    if not GITHUB_TOKEN:

        speak(
            "GitHub is not configured yet. "
            "Please add your GitHub token."
        )

        return False

    if (
        not GITHUB_REPOSITORY
        or GITHUB_REPOSITORY.startswith(
            "YOUR_USERNAME"
        )
    ):

        speak(
            "Please configure your GitHub repository."
        )

        return False

    return True


# ============================================================
# GITHUB UPLOAD
# ============================================================

def upload_to_github(
    local_file,
    github_path,
    commit_message="SAI VoiceOS file upload"
):

    if not github_ready():

        return False

    local_file = os.path.abspath(
        os.path.expanduser(
            local_file
        )
    )

    if not os.path.exists(
        local_file
    ):

        speak(
            "I could not find the local file."
        )

        return False

    try:

        with open(
            local_file,
            "rb"
        ) as file:

            file_data = file.read()

        encoded_content = (
            base64.b64encode(
                file_data
            ).decode("utf-8")
        )

        url = (
            "https://api.github.com/repos/"
            f"{GITHUB_REPOSITORY}/contents/"
            f"{github_path}"
        )

        headers = {

            "Accept":
            "application/vnd.github+json",

            "Authorization":
            f"Bearer {GITHUB_TOKEN}",

            "X-GitHub-Api-Version":
            "2022-11-28"

        }

        # Check if file already exists
        check = requests.get(
            url,
            headers=headers,
            params={
                "ref": GITHUB_BRANCH
            },
            timeout=15
        )

        payload = {

            "message":
            commit_message,

            "content":
            encoded_content,

            "branch":
            GITHUB_BRANCH

        }

        # Existing file -> SHA required
        if check.status_code == 200:

            existing = check.json()

            payload["sha"] = (
                existing["sha"]
            )

        response = requests.put(
            url,
            headers=headers,
            json=payload,
            timeout=30
        )

        if response.status_code in (
            200,
            201
        ):

            speak(
                "The file was successfully "
                f"pushed to GitHub at "
                f"{github_path}."
            )

            return True

        print(
            "GitHub upload error:",
            response.status_code,
            response.text
        )

        speak(
            "I could not push the file to GitHub."
        )

        return False

    except Exception as e:

        print(
            f"GitHub upload error: {e}"
        )

        speak(
            "There was an error while "
            "uploading the file to GitHub."
        )

        return False


# ============================================================
# GITHUB DOWNLOAD
# ============================================================

def download_from_github(
    github_path,
    local_path
):

    if not github_ready():

        return False

    try:

        url = (
            "https://api.github.com/repos/"
            f"{GITHUB_REPOSITORY}/contents/"
            f"{github_path}"
        )

        headers = {

            "Accept":
            "application/vnd.github+json",

            "Authorization":
            f"Bearer {GITHUB_TOKEN}",

            "X-GitHub-Api-Version":
            "2022-11-28"

        }

        response = requests.get(
            url,
            headers=headers,
            params={
                "ref": GITHUB_BRANCH
            },
            timeout=15
        )

        if response.status_code != 200:

            print(
                response.status_code,
                response.text
            )

            speak(
                "I could not find that "
                "file on GitHub."
            )

            return False

        data = response.json()

        if data.get(
            "encoding"
        ) != "base64":

            speak(
                "GitHub returned an unsupported "
                "file format."
            )

            return False

        content = base64.b64decode(
            data["content"]
        )

        local_path = os.path.abspath(
            os.path.expanduser(
                local_path
            )
        )

        parent = os.path.dirname(
            local_path
        )

        if parent:

            os.makedirs(
                parent,
                exist_ok=True
            )

        with open(
            local_path,
            "wb"
        ) as file:

            file.write(content)

        speak(
            f"The file has been downloaded "
            f"to {local_path}."
        )

        return True

    except Exception as e:

        print(
            f"GitHub download error: {e}"
        )

        speak(
            "I could not download the "
            "GitHub file."
        )

        return False


# ============================================================
# GITHUB LIST FILES
# ============================================================

def list_github_files(
    github_path=""
):

    if not github_ready():

        return

    try:

        url = (
            "https://api.github.com/repos/"
            f"{GITHUB_REPOSITORY}/contents/"
            f"{github_path}"
        )

        headers = {

            "Accept":
            "application/vnd.github+json",

            "Authorization":
            f"Bearer {GITHUB_TOKEN}",

            "X-GitHub-Api-Version":
            "2022-11-28"

        }

        response = requests.get(
            url,
            headers=headers,
            params={
                "ref": GITHUB_BRANCH
            },
            timeout=15
        )

        if response.status_code != 200:

            speak(
                "I could not access that "
                "GitHub path."
            )

            return

        data = response.json()

        if not isinstance(
            data,
            list
        ):

            speak(
                "That GitHub path is a file, "
                "not a folder."
            )

            return

        if not data:

            speak(
                "That GitHub folder is empty."
            )

            return

        print(
            "\nGitHub files:"
        )

        names = []

        for item in data:

            name = item.get(
                "name",
                ""
            )

            item_type = item.get(
                "type",
                ""
            )

            if item_type == "dir":

                names.append(
                    f"folder {name}"
                )

            else:

                names.append(
                    name
                )

        for name in names:

            print(
                f"- {name}"
            )

        speak(
            "I found the following files: "
            + ", ".join(names[:20])
        )

    except Exception as e:

        print(
            f"GitHub list error: {e}"
        )

        speak(
            "I could not list the GitHub files."
        )


# ============================================================
# PDF READER
# ============================================================

def read_pdf(
    pdf_path,
    page_number=None
):

    pdf_path = os.path.abspath(
        os.path.expanduser(
            pdf_path
        )
    )

    if not os.path.exists(
        pdf_path
    ):

        speak(
            "I could not find that PDF."
        )

        return

    if not pdf_path.lower().endswith(
        ".pdf"
    ):

        speak(
            "That file is not a PDF."
        )

        return

    try:

        reader = PdfReader(
            pdf_path
        )

        total_pages = len(
            reader.pages
        )

        print(
            f"PDF pages: {total_pages}"
        )

        # Read a particular page
        if page_number is not None:

            if (
                page_number < 1
                or page_number > total_pages
            ):

                speak(
                    f"The PDF has "
                    f"{total_pages} pages."
                )

                return

            page = reader.pages[
                page_number - 1
            ]

            text = (
                page.extract_text()
                or ""
            )

            if not text.strip():

                speak(
                    "I could not extract text "
                    "from that page."
                )

                return

            speak(
                text[:5000]
            )

            return

        # Entire PDF
        speak(
            f"This PDF contains "
            f"{total_pages} pages."
        )

        for index, page in enumerate(
            reader.pages,
            start=1
        ):

            text = (
                page.extract_text()
                or ""
            )

            if not text.strip():

                continue

            print(
                f"\n===== PAGE {index} ====="
            )

            print(text)

            # Speak page by page
            chunks = [
                text[i:i + 1200]
                for i in range(
                    0,
                    len(text),
                    1200
                )
            ]

            for chunk in chunks:

                speak(chunk)

    except Exception as e:

        print(
            f"PDF error: {e}"
        )

        speak(
            "I could not read that PDF."
        )


# ============================================================
# SEARCH INSIDE PDF
# ============================================================

def search_in_pdf(
    pdf_path,
    search_text
):

    pdf_path = os.path.abspath(
        os.path.expanduser(
            pdf_path
        )
    )

    if not os.path.exists(
        pdf_path
    ):

        speak(
            "I could not find that PDF."
        )

        return

    try:

        reader = PdfReader(
            pdf_path
        )

        matches = []

        for page_number, page in enumerate(
            reader.pages,
            start=1
        ):

            text = (
                page.extract_text()
                or ""
            )

            if (
                search_text.lower()
                in text.lower()
            ):

                matches.append(
                    (
                        page_number,
                        text
                    )
                )

        if not matches:

            speak(
                f"I could not find "
                f"{search_text} "
                f"inside the PDF."
            )

            return

        speak(
            f"I found {search_text} "
            f"on {len(matches)} page(s)."
        )

        for page_number, text in matches:

            print(
                f"\nMatch on page "
                f"{page_number}"
            )

            position = text.lower().find(
                search_text.lower()
            )

            if position == -1:

                snippet = text[:1000]

            else:

                start = max(
                    0,
                    position - 300
                )

                end = min(
                    len(text),
                    position + 1000
                )

                snippet = text[
                    start:end
                ]

            speak(
                f"Page {page_number}."
            )

            speak(
                snippet
            )

    except Exception as e:

        print(
            f"PDF search error: {e}"
        )

        speak(
            "I could not search that PDF."
        )


# ============================================================
# TEXT FILE READER
# ============================================================

def read_text_file(
    file_path
):

    file_path = os.path.abspath(
        os.path.expanduser(
            file_path
        )
    )

    if not os.path.exists(
        file_path
    ):

        speak(
            "I could not find that file."
        )

        return

    try:

        with open(
            file_path,
            "r",
            encoding="utf-8",
            errors="ignore"
        ) as file:

            text = file.read()

        if not text.strip():

            speak(
                "The file is empty."
            )

            return

        speak(
            text[:5000]
        )

    except Exception as e:

        print(
            f"Text file error: {e}"
        )

        speak(
            "I could not read that file."
        )


# ============================================================
# DOWNLOAD FILE FROM INTERNET
# ============================================================

def download_file(
    url,
    destination
):

    try:

        destination = os.path.abspath(
            os.path.expanduser(
                destination
            )
        )

        parent = os.path.dirname(
            destination
        )

        if parent:

            os.makedirs(
                parent,
                exist_ok=True
            )

        speak(
            "Downloading the file."
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
            timeout=30
        ) as response:

            data = response.read()

        with open(
            destination,
            "wb"
        ) as file:

            file.write(data)

        speak(
            "The file has been downloaded."
        )

        print(
            f"Downloaded: {destination}"
        )

        return True

    except Exception as e:

        print(
            f"Download error: {e}"
        )

        speak(
            "I could not download that file."
        )

        return False


# ============================================================
# READ PDF DIRECTLY FROM GITHUB
# ============================================================

def read_github_pdf(
    github_path,
    local_path=None
):

    if not local_path:

        filename = os.path.basename(
            github_path
        )

        local_path = os.path.join(
            os.path.expanduser(
                "~"
            ),
            "Downloads",
            filename
        )

    success = download_from_github(
        github_path,
        local_path
    )

    if success:

        read_pdf(
            local_path
        )


# ============================================================
# SEARCH GITHUB PDF
# ============================================================

def search_github_pdf(
    github_path,
    search_text
):

    filename = os.path.basename(
        github_path
    )

    local_path = os.path.join(
        os.path.expanduser("~"),
        "Downloads",
        filename
    )

    success = download_from_github(
        github_path,
        local_path
    )

    if success:

        search_in_pdf(
            local_path,
            search_text
        )


# ============================================================
# GITHUB + LOCAL FILE WORKFLOW
# ============================================================

def push_file_to_github_workflow(
    local_file,
    github_folder
):

    filename = os.path.basename(
        local_file
    )

    github_path = (
        github_folder.rstrip("/")
        + "/"
        + filename
    )

    return upload_to_github(
        local_file,
        github_path,
        f"SAI VoiceOS: upload {filename}"
    )


# ============================================================
# NAME
# ============================================================

NAME_FILE = "assistant_name.txt"


def load_name():

    try:

        with open(
            NAME_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            name = file.read().strip()

            if name:

                return name

    except FileNotFoundError:

        pass

    return "SAI"


def set_name():

    speak(
        "What would you like to call me?"
    )

    name = take_command()

    if not name:

        speak(
            "I could not catch the name."
        )

        return

    try:

        with open(
            NAME_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(name)

        speak(
            f"Alright. You can call me {name}."
        )

    except Exception:

        speak(
            "I could not save the name."
        )


# ============================================================
# LOCAL FILE SEARCH
# ============================================================

def find_local_file(
    filename,
    search_folder=None
):

    if not search_folder:

        search_folder = os.path.expanduser(
            "~"
        )

    search_folder = os.path.abspath(
        search_folder
    )

    speak(
        f"Searching for {filename}."
    )

    matches = []

    try:

        for root, dirs, files in os.walk(
            search_folder
        ):

            # Ignore heavy/system folders
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

                if filename.lower() in file.lower():

                    matches.append(
                        os.path.join(
                            root,
                            file
                        )
                    )

                    if len(matches) >= 10:

                        break

            if len(matches) >= 10:

                break

    except Exception as e:

        print(
            f"File search error: {e}"
        )

    if not matches:

        speak(
            f"I could not find {filename}."
        )

        return []

    speak(
        f"I found {len(matches)} matching file(s)."
    )

    for path in matches:

        print(path)

    return matches


# ============================================================
# SAFETY CONFIRMATION
# ============================================================

def ask_confirmation(action):

    speak(
        f"This action will {action}. "
        "Do you want me to continue?"
    )

    answer = take_command()

    if not answer:

        return False

    positive = [
        "yes",
        "yeah",
        "yep",
        "confirm",
        "continue",
        "do it",
        "proceed"
    ]

    return any(
        word in answer
        for word in positive
    )


# ============================================================
# SHUTDOWN
# ============================================================

def shutdown_computer():

    if not ask_confirmation(
        "shut down your computer"
    ):

        speak(
            "Shutdown cancelled."
        )

        return

    speak(
        "Shutting down the computer."
    )

    os.system(
        "shutdown /s /f /t 1"
    )


# ============================================================
# RESTART
# ============================================================

def restart_computer():

    if not ask_confirmation(
        "restart your computer"
    ):

        speak(
            "Restart cancelled."
        )

        return

    speak(
        "Restarting the computer."
    )

    os.system(
        "shutdown /r /f /t 1"
    )


# ============================================================
# FUNCTION REGISTRY
# ============================================================

SAI_FUNCTIONS = {

    "time":
        tell_time,

    "date":
        tell_date,

    "calculator":
        open_calculator,

    "notepad":
        open_notepad,

    "browser":
        open_browser,

    "google":
        open_google,

    "youtube":
        open_youtube,

    "whatsapp":
        open_whatsapp,

    "screenshot":
        take_screenshot,

    "weather":
        get_weather,

    "music":
        play_music,

    "note":
        write_note,

    "joke":
        tell_joke,

    "internet_search":
        internet_search,

    "web_answer":
        web_answer,

    "pdf_reader":
        read_pdf,

    "pdf_search":
        search_in_pdf,

    "text_reader":
        read_text_file,

    "github_upload":
        upload_to_github,

    "github_download":
        download_from_github,

    "github_list":
        list_github_files,

    "github_pdf_reader":
        read_github_pdf,

    "github_pdf_search":
        search_github_pdf,

    "local_file_search":
        find_local_file,

}


# ============================================================
# COMMAND HANDLER
# ============================================================

def handle_command(query):

    if not query:

        return True

    query = query.lower().strip()

    # --------------------------------------------------------
    # EXIT
    # --------------------------------------------------------

    if any(
        phrase in query
        for phrase in [
            "exit",
            "quit",
            "go offline",
            "stop listening"
        ]
    ):

        speak(
            "SAI VoiceOS is going offline. Goodbye."
        )

        return False

    # --------------------------------------------------------
    # TIME
    # --------------------------------------------------------

    if (
        "what time is it" in query
        or query == "time"
        or "current time" in query
    ):

        tell_time()

        return True

    # --------------------------------------------------------
    # DATE
    # --------------------------------------------------------

    if (
        "what is the date" in query
        or "today's date" in query
        or query == "date"
    ):

        tell_date()

        return True

    # --------------------------------------------------------
    # CALCULATOR
    # --------------------------------------------------------

    math_match = re.search(
        r"\d+(?:\s*(?:\+|-|\*|/|x|×)\s*\d+)+",
        query
    )

    if math_match:

        calculate(
            query
        )

        return True

    if (
        query.startswith("calculate ")
        or "what is " in query
        and any(
            operator in query
            for operator in [
                "+",
                "-",
                "*",
                "/",
                "times",
                "plus",
                "minus"
            ]
        )
    ):

        calculate(
            query
        )

        return True

    # --------------------------------------------------------
    # WEATHER
    # --------------------------------------------------------

    if "weather" in query:

        match = re.search(
            r"weather\s+(?:in|at|for)\s+(.+)",
            query
        )

        if match:

            city = match.group(1).strip()

            get_weather(city)

        else:

            get_weather()

        return True

    # --------------------------------------------------------
    # OPEN YOUTUBE
    # --------------------------------------------------------

    if "open youtube" in query:

        open_youtube()

        return True

    # --------------------------------------------------------
    # YOUTUBE SEARCH
    # --------------------------------------------------------

    if (
        "play on youtube" in query
        or "search youtube for" in query
        or "youtube search" in query
    ):

        topic = query

        for phrase in [
            "play on youtube",
            "search youtube for",
            "youtube search"
        ]:

            topic = topic.replace(
                phrase,
                ""
            )

        play_on_youtube(
            topic.strip()
        )

        return True

    # --------------------------------------------------------
    # WHATSAPP
    # --------------------------------------------------------

    if "open whatsapp" in query:

        open_whatsapp()

        return True

    # --------------------------------------------------------
    # CALCULATOR APP
    # --------------------------------------------------------

    if (
        "open calculator" in query
        or "open calc" in query
    ):

        open_calculator()

        return True

    # --------------------------------------------------------
    # NOTEPAD
    # --------------------------------------------------------

    if (
        "open notepad" in query
        or "open text editor" in query
    ):

        open_notepad()

        return True

    # --------------------------------------------------------
    # BROWSER
    # --------------------------------------------------------

    if (
        "open browser" in query
        or "open chrome" in query
    ):

        open_browser()

        return True

    # --------------------------------------------------------
    # GOOGLE
    # --------------------------------------------------------

    if "open google" in query:

        open_google()

        return True

    # --------------------------------------------------------
    # GOOGLE SEARCH
    # --------------------------------------------------------

    if (
        "search on google" in query
        or "search google for" in query
        or "google search" in query
    ):

        search_query = query

        for phrase in [
            "search on google",
            "search google for",
            "google search"
        ]:

            search_query = (
                search_query
                .replace(
                    phrase,
                    ""
                )
            )

        internet_search(
            search_query.strip()
        )

        return True

    # ========================================================
    # GITHUB
    # ========================================================

    # --------------------------------------------------------
    # List GitHub files
    # --------------------------------------------------------

    if (
        "list github files" in query
        or "show github files" in query
        or "list my github files" in query
    ):

        list_github_files()

        return True

    # --------------------------------------------------------
    # Read GitHub PDF
    # --------------------------------------------------------

    if (
        "read pdf from github" in query
        or "read github pdf" in query
    ):

        speak(
            "Tell me the GitHub PDF path."
        )

        github_path = take_command()

        if github_path:

            read_github_pdf(
                github_path
            )

        return True

    # --------------------------------------------------------
    # Search GitHub PDF
    # --------------------------------------------------------

    if (
        "search github pdf" in query
        or "find in github pdf" in query
    ):

        speak(
            "Tell me the GitHub PDF path."
        )

        github_path = take_command()

        if not github_path:

            return True

        speak(
            "What should I search for?"
        )

        search_text = take_command()

        if search_text:

            search_github_pdf(
                github_path,
                search_text
            )

        return True

    # --------------------------------------------------------
    # Download GitHub file
    # --------------------------------------------------------

    if (
        "download from github" in query
        or "download github file" in query
    ):

        speak(
            "Tell me the GitHub file path."
        )

        github_path = take_command()

        if not github_path:

            return True

        filename = os.path.basename(
            github_path
        )

        destination = os.path.join(
            os.path.expanduser("~"),
            "Downloads",
            filename
        )

        download_from_github(
            github_path,
            destination
        )

        return True

    # --------------------------------------------------------
    # Upload file to GitHub
    # --------------------------------------------------------

    if (
        "upload to github" in query
        or "push to github" in query
        or "upload file to github" in query
    ):

        speak(
            "Tell me the complete local file path."
        )

        local_file = take_command()

        if not local_file:

            return True

        speak(
            "Tell me the GitHub folder path."
        )

        github_folder = take_command()

        if not github_folder:

            return True

        push_file_to_github_workflow(
            local_file,
            github_folder
        )

        return True

    # ========================================================
    # PDF
    # ========================================================

    # --------------------------------------------------------
    # Read local PDF
    # --------------------------------------------------------

    if (
        "read this pdf" in query
        or "read pdf" in query
    ):

        speak(
            "Tell me the complete PDF file path."
        )

        pdf_path = take_command()

        if pdf_path:

            read_pdf(
                pdf_path
            )

        return True

    # --------------------------------------------------------
    # Read PDF page
    # --------------------------------------------------------

    if (
        "read page" in query
        and "pdf" in query
    ):

        speak(
            "Tell me the PDF file path."
        )

        pdf_path = take_command()

        if not pdf_path:

            return True

        speak(
            "Which page number?"
        )

        page_text = take_command()

        try:

            page_number = int(
                re.search(
                    r"\d+",
                    page_text
                ).group()
            )

            read_pdf(
                pdf_path,
                page_number
            )

        except Exception:

            speak(
                "I could not understand "
                "the page number."
            )

        return True

    # --------------------------------------------------------
    # Search local PDF
    # --------------------------------------------------------

    if (
        "search in pdf" in query
        or "find in pdf" in query
    ):

        speak(
            "Tell me the PDF file path."
        )

        pdf_path = take_command()

        if not pdf_path:

            return True

        speak(
            "What should I search for?"
        )

        search_text = take_command()

        if search_text:

            search_in_pdf(
                pdf_path,
                search_text
            )

        return True

    # ========================================================
    # LOCAL FILES
    # ========================================================

    if (
        "find file" in query
        or "search for file" in query
        or "find a file" in query
    ):

        filename = query

        for phrase in [
            "find file",
            "search for file",
            "find a file"
        ]:

            filename = filename.replace(
                phrase,
                ""
            )

        filename = filename.strip()

        if filename:

            find_local_file(
                filename
            )

        else:

            speak(
                "Tell me the file name."
            )

        return True

    # ========================================================
    # NOTES
    # ========================================================

    if (
        "write a note" in query
        or "take a note" in query
        or "make a note" in query
    ):

        write_note()

        return True

    # ========================================================
    # SCREENSHOT
    # ========================================================

    if "screenshot" in query:

        take_screenshot()

        return True

    # ========================================================
    # MUSIC
    # ========================================================

    if "play music" in query:

        song = query.replace(
            "play music",
            ""
        ).strip()

        play_music(
            song
        )

        return True

    # ========================================================
    # JOKE
    # ========================================================

    if (
        "tell me a joke" in query
        or "make me laugh" in query
    ):

        tell_joke()

        return True

    # ========================================================
    # NAME
    # ========================================================

    if (
        "change your name" in query
        or "change your name to" in query
    ):

        set_name()

        return True

    # ========================================================
    # SYSTEM
    # ========================================================

    if (
        "shutdown computer" in query
        or "shut down computer" in query
    ):

        shutdown_computer()

        return True

    if (
        "restart computer" in query
        or "restart the computer" in query
    ):

        restart_computer()

        return True

    # ========================================================
    # GENERIC OPEN COMMAND
    # ========================================================

    if (
        query.startswith("open ")
        or query.startswith("launch ")
        or query.startswith("start ")
    ):

        app_name = query

        for prefix in [
            "open ",
            "launch ",
            "start "
        ]:

            if app_name.startswith(prefix):

                app_name = app_name[
                    len(prefix):
                ]

                break

        open_application(
            app_name.strip()
        )

        return True

    # ========================================================
    # GENERAL INTERNET QUESTION
    # ========================================================

    question_starters = [

        "who is",
        "what is",
        "what are",
        "where is",
        "when is",
        "why is",
        "why are",
        "how is",
        "how are",
        "how do",
        "how can",
        "tell me about",
        "latest",
        "current",
        "today",
        "news about",
        "information about"

    ]

    if any(
        query.startswith(
            starter
        )
        for starter in question_starters
    ):

        web_answer(
            query
        )

        return True

    # ========================================================
    # FALLBACK
    # ========================================================

    # Anything SAI does not recognize
    # goes to the internet.

    speak(
        "I don't have a local action "
        "for that yet. "
        "I will check the internet."
    )

    web_answer(
        query
    )

    return True


# ============================================================
# MAIN
# ============================================================

def main():

    wishme()

    while True:

        query = take_command()

        if not query:

            continue

        should_continue = handle_command(
            query
        )

        if not should_continue:

            break


# ============================================================
# START SAI VOICEOS
# ============================================================

if __name__ == "__main__":

    main()
