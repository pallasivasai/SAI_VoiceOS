"""
SAI VoiceOS - Complete single-file version

Cloud:
    streamlit run sai_voiceos.py

Local Windows:
    python sai_voiceos.py

Cloud mode handles Internet, GitHub and PDF files.
Local mode additionally handles microphone, TTS, Windows apps,
screenshots, local files and voice commands.
"""

import os
import io
import re
import json
import base64
import random
import datetime
import subprocess
import urllib.parse
import urllib.request
import webbrowser as wb
from pathlib import Path

import requests
from pypdf import PdfReader

# Optional local-only packages. The cloud app can start without them.
try:
    import streamlit as st
except ImportError:
    st = None

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
    import pyautogui
except ImportError:
    pyautogui = None

try:
    import pyjokes
except ImportError:
    pyjokes = None


APP_NAME = "SAI VoiceOS"

GITHUB_TOKEN = os.getenv("SAI_GITHUB_TOKEN", "")
GITHUB_REPOSITORY = os.getenv(
    "SAI_GITHUB_REPOSITORY",
    "YOUR_USERNAME/YOUR_REPOSITORY"
)
GITHUB_BRANCH = os.getenv("SAI_GITHUB_BRANCH", "main")


def get_github_config():
    token = GITHUB_TOKEN
    repo = GITHUB_REPOSITORY
    branch = GITHUB_BRANCH

    if st is not None:
        try:
            token = token or st.secrets.get("GITHUB_TOKEN", "")
            repo = st.secrets.get("GITHUB_REPOSITORY", repo)
            branch = st.secrets.get("GITHUB_BRANCH", branch)
        except Exception:
            pass

    return token, repo, branch


# ============================================================
# VOICE
# ============================================================

engine = None

if pyttsx3 is not None:
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty("voices")
        if voices:
            engine.setProperty("voice", voices[0].id)
        engine.setProperty("rate", 150)
        engine.setProperty("volume", 1.0)
    except Exception:
        engine = None


def speak(text):
    if not text:
        return

    text = str(text)
    print("SAI:", text)

    if engine is not None:
        try:
            engine.say(text)
            engine.runAndWait()
        except Exception:
            pass


def take_command():
    if sd is None or sr is None or wav is None:
        speak("Local microphone is not available in this environment.")
        return None

    recognizer = sr.Recognizer()
    rate = 44100
    seconds = 5

    print("Listening...")

    try:
        recording = sd.rec(
            int(seconds * rate),
            samplerate=rate,
            channels=1,
            dtype="int16"
        )
        sd.wait()

        buffer = io.BytesIO()
        wav.write(buffer, rate, recording)
        buffer.seek(0)

        with sr.AudioFile(buffer) as source:
            audio = recognizer.record(source)

        query = recognizer.recognize_google(
            audio,
            language="en-in"
        ).lower().strip()

        print("YOU:", query)
        return query

    except sr.UnknownValueError:
        speak("Sorry, I could not understand that.")
    except sr.RequestError:
        speak("Speech recognition service is unavailable.")
    except Exception as exc:
        print("Microphone error:", exc)

    return None


# ============================================================
# BASIC ACTIONS
# ============================================================

def tell_time():
    speak(
        "The current time is "
        + datetime.datetime.now().strftime("%I:%M %p")
    )


def tell_date():
    speak(
        "Today's date is "
        + datetime.datetime.now().strftime("%d %B %Y")
    )


def calculate(expression):
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
    }

    for word, symbol in replacements.items():
        expression = expression.replace(word, symbol)

    expression = re.sub(r"(?<=\d)\s*x\s*(?=\d)", "*", expression)
    expression = expression.replace("what is", "")
    expression = expression.replace("calculate", "")
    expression = expression.replace("?", "")

    cleaned = re.sub(
        r"[^0-9+\-*/().%\s]",
        "",
        expression
    )

    if not cleaned.strip():
        speak("I could not understand the calculation.")
        return

    try:
        result = eval(cleaned, {"__builtins__": {}}, {})
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        speak(f"The answer is {result}.")
    except Exception:
        speak("Sorry, I could not calculate that.")


def open_calculator():
    speak("Opening Calculator.")
    try:
        subprocess.Popen(["calc.exe"])
    except Exception:
        os.system("start calc")


def open_notepad():
    speak("Opening Notepad.")
    try:
        subprocess.Popen(["notepad.exe"])
    except Exception:
        speak("I could not open Notepad.")


def open_browser():
    speak("Opening the browser.")
    wb.open("https://www.google.com/")


def open_google():
    speak("Opening Google.")
    wb.open("https://www.google.com/")


def open_youtube():
    speak("Opening YouTube.")
    wb.open("https://www.youtube.com/")


def play_on_youtube(topic):
    if not topic:
        return open_youtube()

    url = (
        "https://www.youtube.com/results?search_query="
        + urllib.parse.quote_plus(topic)
    )
    wb.open(url)
    speak(f"Searching YouTube for {topic}.")


def open_whatsapp():
    speak("Opening WhatsApp.")
    try:
        os.startfile("whatsapp:")
        return
    except Exception:
        pass
    wb.open("https://web.whatsapp.com/")


def take_screenshot():
    if pyautogui is None:
        speak("Screenshot is available only on the local agent.")
        return

    try:
        image = pyautogui.screenshot()
        folder = Path.home() / "Pictures"
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / "sai_voiceos_screenshot.png"
        image.save(path)
        speak("Screenshot captured successfully.")
        print("Saved:", path)
    except Exception as exc:
        print(exc)
        speak("I could not take the screenshot.")


def play_music(song_name=""):
    folder = Path.home() / "Music"

    if not folder.exists():
        speak("I could not find your Music folder.")
        return

    extensions = (".mp3", ".wav", ".flac", ".m4a", ".aac")

    songs = [
        x for x in folder.iterdir()
        if x.is_file() and x.suffix.lower() in extensions
    ]

    if song_name:
        songs = [
            x for x in songs
            if song_name.lower() in x.name.lower()
        ]

    if not songs:
        speak("I could not find that song.")
        return

    song = random.choice(songs)

    try:
        os.startfile(str(song))
        speak(f"Playing {song.name}.")
    except Exception:
        speak("I could not play that song.")


def write_note():
    speak("What would you like me to write?")
    note = take_command()

    if not note:
        return

    path = Path.home() / "Desktop" / "sai_voiceos_notes.txt"
    path.parent.mkdir(parents=True, exist_ok=True)

    stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    with open(path, "a", encoding="utf-8") as file:
        file.write(f"[{stamp}] {note}\n")

    speak("Your note has been saved to the desktop.")


def tell_joke():
    if pyjokes is None:
        speak("Jokes are not installed.")
        return
    try:
        speak(pyjokes.get_joke())
    except Exception:
        speak("I could not find a joke.")


def get_weather(city="Guntur"):
    try:
        encoded = urllib.parse.quote(city)
        url = f"https://wttr.in/{encoded}?format=j1"
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "SAI-VoiceOS/1.0"}
        )

        with urllib.request.urlopen(request, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))

        current = data["current_condition"][0]
        temp = current["temp_C"]
        desc = current["weatherDesc"][0]["value"]

        speak(
            f"The current temperature in {city} is "
            f"{temp} degrees Celsius with {desc}."
        )
    except Exception as exc:
        print("Weather error:", exc)
        speak("I could not get the weather right now.")


# ============================================================
# INTERNET
# ============================================================

def internet_search(query):
    url = (
        "https://www.google.com/search?q="
        + urllib.parse.quote_plus(query)
    )
    wb.open(url)
    speak("I opened the search results.")


def web_answer(query):
    try:
        url = (
            "https://api.duckduckgo.com/?q="
            + urllib.parse.quote_plus(query)
            + "&format=json&no_html=1&skip_disambig=1"
        )

        request = urllib.request.Request(
            url,
            headers={"User-Agent": "SAI-VoiceOS/1.0"}
        )

        with urllib.request.urlopen(request, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))

        answer = (data.get("AbstractText") or "").strip()

        if answer:
            speak(answer[:1500])
            return answer

        related = []
        for item in data.get("RelatedTopics", [])[:5]:
            if isinstance(item, dict) and item.get("Text"):
                related.append(item["Text"])

        if related:
            speak(" ".join(related)[:1500])
            return " ".join(related)

    except Exception as exc:
        print("Web error:", exc)

    internet_search(query)
    return None


# ============================================================
# GITHUB
# ============================================================

def github_headers(token):
    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def github_ready():
    token, repo, branch = get_github_config()

    if not token:
        speak("GitHub token is not configured.")
        return None

    if not repo or repo.startswith("YOUR_USERNAME"):
        speak("GitHub repository is not configured.")
        return None

    return token, repo, branch


def github_upload(local_file, github_path, message="SAI VoiceOS upload"):
    config = github_ready()
    if not config:
        return False

    token, repo, branch = config
    local_file = Path(local_file).expanduser().resolve()

    if not local_file.exists():
        speak("I could not find the local file.")
        return False

    try:
        content = base64.b64encode(
            local_file.read_bytes()
        ).decode("utf-8")

        url = (
            f"https://api.github.com/repos/{repo}/contents/"
            f"{github_path.lstrip('/')}"
        )

        headers = github_headers(token)

        check = requests.get(
            url,
            headers=headers,
            params={"ref": branch},
            timeout=15
        )

        payload = {
            "message": message,
            "content": content,
            "branch": branch,
        }

        if check.status_code == 200:
            payload["sha"] = check.json()["sha"]

        response = requests.put(
            url,
            headers=headers,
            json=payload,
            timeout=30
        )

        if response.status_code in (200, 201):
            speak(
                f"The file was successfully pushed to GitHub "
                f"at {github_path}."
            )
            return True

        print(response.status_code, response.text)
        speak("I could not push the file to GitHub.")
        return False

    except Exception as exc:
        print("GitHub upload error:", exc)
        speak("GitHub upload failed.")
        return False


def github_download(github_path, local_path=None):
    config = github_ready()
    if not config:
        return False

    token, repo, branch = config

    try:
        url = (
            f"https://api.github.com/repos/{repo}/contents/"
            f"{github_path.lstrip('/')}"
        )

        response = requests.get(
            url,
            headers=github_headers(token),
            params={"ref": branch},
            timeout=15
        )

        if response.status_code != 200:
            speak("I could not find that GitHub file.")
            return False

        data = response.json()
        content = base64.b64decode(data["content"])

        if not local_path:
            local_path = (
                Path.home()
                / "Downloads"
                / Path(github_path).name
            )

        local_path = Path(local_path).expanduser().resolve()
        local_path.parent.mkdir(parents=True, exist_ok=True)
        local_path.write_bytes(content)

        speak(f"The file was downloaded to {local_path}.")
        return True

    except Exception as exc:
        print("GitHub download error:", exc)
        speak("I could not download the GitHub file.")
        return False


def github_list(path=""):
    config = github_ready()
    if not config:
        return []

    token, repo, branch = config

    try:
        url = (
            f"https://api.github.com/repos/{repo}/contents/"
            f"{path.lstrip('/')}"
        )

        response = requests.get(
            url,
            headers=github_headers(token),
            params={"ref": branch},
            timeout=15
        )

        if response.status_code != 200:
            speak("I could not list that GitHub path.")
            return []

        data = response.json()
        if not isinstance(data, list):
            data = [data]

        return data

    except Exception as exc:
        print("GitHub list error:", exc)
        speak("I could not list GitHub files.")
        return []


def read_github_pdf(github_path):
    local_path = (
        Path.home()
        / "Downloads"
        / Path(github_path).name
    )

    if github_download(github_path, local_path):
        read_pdf(local_path)


def search_github_pdf(github_path, term):
    local_path = (
        Path.home()
        / "Downloads"
        / Path(github_path).name
    )

    if github_download(github_path, local_path):
        search_in_pdf(local_path, term)


# ============================================================
# PDF / FILES
# ============================================================

def pdf_pages(source):
    if isinstance(source, (str, Path)):
        reader = PdfReader(str(source))
    else:
        reader = PdfReader(io.BytesIO(source))

    return [
        (number, page.extract_text() or "")
        for number, page in enumerate(reader.pages, start=1)
    ]


def read_pdf(path, page_number=None):
    path = Path(path).expanduser().resolve()

    if not path.exists():
        speak("I could not find that PDF.")
        return

    try:
        pages = pdf_pages(path)

        if page_number is not None:
            if page_number < 1 or page_number > len(pages):
                speak(f"The PDF has {len(pages)} pages.")
                return

            text = pages[page_number - 1][1]
            speak(text[:5000] or "No extractable text on that page.")
            return

        speak(f"This PDF contains {len(pages)} pages.")

        for number, text in pages:
            if not text.strip():
                continue

            print(f"\n===== PAGE {number} =====\n{text}")

            for start in range(0, len(text), 1200):
                speak(text[start:start + 1200])

    except Exception as exc:
        print("PDF error:", exc)
        speak("I could not read that PDF.")


def search_in_pdf(path, term):
    path = Path(path).expanduser().resolve()

    if not path.exists():
        speak("I could not find that PDF.")
        return

    try:
        pages = pdf_pages(path)
        matches = [
            (number, text)
            for number, text in pages
            if term.lower() in text.lower()
        ]

        if not matches:
            speak(f"I could not find {term} in the PDF.")
            return

        speak(
            f"I found {term} on {len(matches)} page(s)."
        )

        for number, text in matches:
            position = text.lower().find(term.lower())
            start = max(0, position - 350)
            end = min(len(text), position + 1100)

            speak(f"Page {number}.")
            speak(text[start:end])

    except Exception as exc:
        print("PDF search error:", exc)
        speak("I could not search the PDF.")


def read_text_file(path):
    path = Path(path).expanduser().resolve()

    if not path.exists():
        speak("I could not find that file.")
        return

    try:
        text = path.read_text(
            encoding="utf-8",
            errors="ignore"
        )
        speak(text[:6000] or "The file is empty.")
    except Exception as exc:
        print(exc)
        speak("I could not read that file.")


def find_local_file(name, folder=None):
    folder = Path(folder or Path.home()).expanduser()

    matches = []

    try:
        for root, dirs, files in os.walk(folder):
            dirs[:] = [
                d for d in dirs
                if d.lower() not in {
                    "appdata",
                    "node_modules",
                    ".git"
                }
            ]

            for filename in files:
                if name.lower() in filename.lower():
                    matches.append(Path(root) / filename)

                    if len(matches) >= 10:
                        break

            if len(matches) >= 10:
                break

    except Exception as exc:
        print(exc)

    if not matches:
        speak(f"I could not find {name}.")
        return []

    speak(f"I found {len(matches)} matching files.")

    for path in matches:
        print(path)

    return matches


# ============================================================
# COMMAND ENGINE
# ============================================================

def handle_command(query):
    if not query:
        return True

    query = query.lower().strip()

    if any(x in query for x in [
        "exit",
        "quit",
        "go offline",
        "stop listening"
    ]):
        speak("SAI VoiceOS is going offline. Goodbye.")
        return False

    if (
        query == "time"
        or "what time is it" in query
        or "current time" in query
    ):
        tell_time()
        return True

    if (
        query == "date"
        or "what is the date" in query
        or "today's date" in query
    ):
        tell_date()
        return True

    if (
        re.search(r"\d+\s*(?:\+|-|\*|/|x|×)\s*\d+", query)
        or query.startswith("calculate ")
    ):
        calculate(query)
        return True

    if "weather" in query:
        match = re.search(
            r"weather\s+(?:in|at|for)\s+(.+)",
            query
        )
        get_weather(
            match.group(1).strip()
            if match else "Guntur"
        )
        return True

    if "open calculator" in query or "open calc" in query:
        open_calculator()
        return True

    if "open notepad" in query:
        open_notepad()
        return True

    if "open whatsapp" in query:
        open_whatsapp()
        return True

    if "open youtube" in query:
        open_youtube()
        return True

    if "search youtube for" in query or "play on youtube" in query:
        topic = (
            query
            .replace("search youtube for", "")
            .replace("play on youtube", "")
            .strip()
        )
        play_on_youtube(topic)
        return True

    if "open browser" in query or "open chrome" in query:
        open_browser()
        return True

    if "open google" in query:
        open_google()
        return True

    if "search on google" in query or "google search" in query:
        topic = (
            query
            .replace("search on google", "")
            .replace("google search", "")
            .strip()
        )
        internet_search(topic)
        return True

    if "screenshot" in query:
        take_screenshot()
        return True

    if "play music" in query:
        play_music(
            query.replace("play music", "").strip()
        )
        return True

    if "write a note" in query or "take a note" in query:
        write_note()
        return True

    if "tell me a joke" in query:
        tell_joke()
        return True

    if "list github files" in query or "show github files" in query:
        items = github_list()
        if items:
            speak(
                "I found: "
                + ", ".join(
                    item.get("name", "")
                    for item in items[:20]
                )
            )
        return True

    if "read pdf from github" in query or "read github pdf" in query:
        speak("Tell me the GitHub PDF path.")
        path = take_command()
        if path:
            read_github_pdf(path)
        return True

    if "search github pdf" in query or "find in github pdf" in query:
        speak("Tell me the GitHub PDF path.")
        path = take_command()
        if not path:
            return True

        speak("What should I search for?")
        term = take_command()

        if term:
            search_github_pdf(path, term)

        return True

    if "download from github" in query or "download github file" in query:
        speak("Tell me the GitHub file path.")
        path = take_command()

        if path:
            github_download(path)

        return True

    if "push to github" in query or "upload to github" in query:
        speak("Tell me the complete local file path.")
        local = take_command()

        if not local:
            return True

        speak("Tell me the GitHub folder path.")
        folder = take_command()

        if not folder:
            return True

        github_path = (
            folder.rstrip("/")
            + "/"
            + Path(local).name
        )

        github_upload(
            local,
            github_path,
            f"SAI VoiceOS: upload {Path(local).name}"
        )
        return True

    if "read this pdf" in query or "read pdf" in query:
        speak("Tell me the complete PDF path.")
        path = take_command()

        if path:
            read_pdf(path)

        return True

    if "search in pdf" in query or "find in pdf" in query:
        speak("Tell me the PDF path.")
        path = take_command()

        if not path:
            return True

        speak("What should I search for?")
        term = take_command()

        if term:
            search_in_pdf(path, term)

        return True

    if "find file" in query or "search for file" in query:
        name = (
            query
            .replace("find file", "")
            .replace("search for file", "")
            .strip()
        )

        if name:
            find_local_file(name)

        return True

    if query.startswith("open "):
        app = query.replace("open ", "", 1).strip()

        if "calculator" in app:
            open_calculator()
        elif "notepad" in app:
            open_notepad()
        elif "whatsapp" in app:
            open_whatsapp()
        elif "youtube" in app:
            open_youtube()
        elif "browser" in app or "chrome" in app:
            open_browser()
        else:
            speak(
                f"I do not have a local action for {app}. "
                "I will search the internet."
            )
            internet_search(f"how to open {app}")

        return True

    # Important: unknown questions go to the Internet.
    web_answer(query)
    return True


# ============================================================
# STREAMLIT CLOUD UI
# ============================================================

def cloud_app():
    st.set_page_config(
        page_title="SAI VoiceOS",
        page_icon="🎙️",
        layout="wide"
    )

    st.title("🎙️ SAI VoiceOS")
    st.caption(
        "Voice-first accessibility environment: "
        "Internet + GitHub + PDF + Local Agent"
    )

    tab_web, tab_github, tab_pdf, tab_files = st.tabs(
        ["🌐 Internet", "🐙 GitHub", "📄 PDF", "📂 Files"]
    )

    with tab_web:
        st.header("Internet")

        query = st.text_input(
            "Ask SAI anything",
            placeholder="What is artificial intelligence?"
        )

        c1, c2 = st.columns(2)

        with c1:
            if st.button(
                "Get Web Answer",
                use_container_width=True
            ) and query.strip():
                web_answer(query)

        with c2:
            if st.button(
                "Open Search",
                use_container_width=True
            ) and query.strip():
                encoded = urllib.parse.quote_plus(query)
                st.link_button(
                    "Open Google",
                    f"https://www.google.com/search?q={encoded}"
                )

    with tab_github:
        st.header("GitHub File Manager")

        token, repo, branch = get_github_config()

        st.write(
            f"Repository: `{repo or 'Not configured'}` | "
            f"Branch: `{branch}`"
        )

        uploaded = st.file_uploader(
            "Choose a file to push to GitHub",
            type=None
        )

        github_path = st.text_input(
            "GitHub path",
            placeholder="documents/resume.pdf"
        )

        if st.button(
            "Push File to GitHub",
            use_container_width=True
        ):
            if not uploaded or not github_path.strip():
                st.warning("Choose a file and enter its GitHub path.")
            else:
                temp_dir = Path("/tmp/sai_voiceos")
                temp_dir.mkdir(exist_ok=True)
                temp = temp_dir / uploaded.name
                temp.write_bytes(uploaded.getvalue())

                github_upload(
                    temp,
                    github_path.strip(),
                    f"SAI VoiceOS: upload {uploaded.name}"
                )

        st.divider()

        list_path = st.text_input(
            "GitHub folder to list",
            placeholder="documents"
        )

        if st.button(
            "List GitHub Files",
            use_container_width=True
        ):
            items = github_list(list_path.strip())

            if items:
                for item in items:
                    icon = "📁" if item.get("type") == "dir" else "📄"
                    st.write(
                        f"{icon} `{item.get('path', item.get('name', ''))}`"
                    )
            else:
                st.info("No files found.")

        st.divider()

        download_path = st.text_input(
            "GitHub file to download",
            placeholder="documents/resume.pdf"
        )

        if st.button(
            "Prepare GitHub Download",
            use_container_width=True
        ):
            if download_path.strip():
                data = github_download(download_path.strip())

                if data is not False and data is not None:
                    st.download_button(
                        "⬇️ Download File",
                        data=data,
                        file_name=Path(download_path).name,
                        mime="application/octet-stream"
                    )

    with tab_pdf:
        st.header("PDF Reader")

        pdf = st.file_uploader(
            "Upload PDF",
            type=["pdf"]
        )

        if pdf:
            data = pdf.getvalue()

            try:
                pages = pdf_pages(data)

                st.success(
                    f"PDF loaded: {len(pages)} page(s)."
                )

                page = st.number_input(
                    "Page number (0 = entire PDF)",
                    min_value=0,
                    max_value=len(pages),
                    value=0,
                    step=1
                )

                if st.button(
                    "Read PDF",
                    use_container_width=True
                ):
                    if page == 0:
                        text = "\n\n".join(
                            f"===== PAGE {n} =====\n{text}"
                            for n, text in pages
                        )
                    else:
                        text = pages[page - 1][1]

                    st.text_area(
                        "Extracted text",
                        text,
                        height=500
                    )

                term = st.text_input(
                    "Search inside PDF",
                    placeholder="artificial intelligence"
                )

                if st.button(
                    "Find in PDF",
                    use_container_width=True
                ) and term.strip():
                    matches = [
                        (n, text)
                        for n, text in pages
                        if term.lower() in text.lower()
                    ]

                    if not matches:
                        st.info("No match found.")
                    else:
                        st.success(
                            f"Found on {len(matches)} page(s)."
                        )
                        for n, text in matches:
                            position = text.lower().find(term.lower())
                            start = max(0, position - 400)
                            end = min(len(text), position + 1200)
                            st.markdown(f"### Page {n}")
                            st.write(text[start:end])

            except Exception as exc:
                st.error(f"PDF error: {exc}")

    with tab_files:
        st.header("File Reader")

        uploaded = st.file_uploader(
            "Upload a text file",
            type=["txt", "md", "csv", "json", "py"]
        )

        if uploaded:
            raw = uploaded.getvalue()

            try:
                text = raw.decode("utf-8", errors="ignore")

                st.text_area(
                    "File content",
                    text,
                    height=500
                )

            except Exception as exc:
                st.error(str(exc))

    st.divider()

    st.subheader("Architecture")

    st.code(
        """VOICE
  |
  v
Speech-to-Text
  |
  v
SAI Intent Engine
  |
  +--> Local Windows Agent
  |      Calculator
  |      Notepad
  |      Browser
  |      WhatsApp
  |      Screenshot
  |      Local Files
  |      TTS
  |
  +--> Internet
  |      Search
  |      Web Answers
  |
  +--> GitHub
  |      Upload / Push
  |      Download
  |      List
  |      Read PDF
  |
  +--> Documents
         PDF Reader
         PDF Search

  |
  v
Voice / Text Response
""",
        language="text"
    )

    st.info(
        "Streamlit Cloud is remote. It cannot directly open your "
        "personal Windows Calculator, WhatsApp Desktop, microphone "
        "or screen. Run this same file locally for those capabilities."
    )


# ============================================================
# LOCAL APP
# ============================================================

def local_app():
    speak(
        "Welcome to SAI VoiceOS. "
        "I am ready for your command."
    )

    while True:
        query = take_command()

        if query and not handle_command(query):
            break


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    # When started with `streamlit run`, Streamlit exists and
    # the script is executed by Streamlit.
    # When started with `python`, use the local voice agent.
    if st is None:
        local_app()
    else:
        # Streamlit sets this environment variable.
        if os.environ.get("STREAMLIT_SERVER_PORT"):
            cloud_app()
        else:
            # Normal python execution: local agent.
            local_app()
