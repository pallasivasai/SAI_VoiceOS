import streamlit as st
import streamlit.components.v1 as components

import io
import re
import json
import base64
import datetime
import urllib.parse
import urllib.request
import tempfile
import os

import speech_recognition as sr


# ============================================================
# OPTIONAL LIBRARIES
# ============================================================

try:
    import requests
except Exception:
    requests = None


try:
    import wikipedia
except Exception:
    wikipedia = None


try:
    from PyPDF2 import PdfReader
except Exception:
    PdfReader = None


try:
    from docx import Document
except Exception:
    Document = None


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="SAI Voice OS",
    page_icon="🎙️",
    layout="centered"
)


# ============================================================
# HIDE STREAMLIT DEFAULT UI
# ============================================================

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

    .stDeployButton {
        display: none;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SESSION STATE
# ============================================================

if "last_response" not in st.session_state:
    st.session_state.last_response = ""

if "last_command" not in st.session_state:
    st.session_state.last_command = ""


# ============================================================
# CLOUD TTS
# ============================================================

def speak(text):

    if not text:
        return

    safe_text = json.dumps(
        str(text)
    )

    html = f"""
    <script>

        const message = {safe_text};

        function speakSAI() {{

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
                    "TTS error:",
                    error
                );

            }}

        }}

        speakSAI();

    </script>
    """

    components.html(
        html,
        height=1
    )


# ============================================================
# OPEN BROWSER PAGE
# ============================================================

def open_browser(
    url,
    name
):

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

    components.html(
        html,
        height=1
    )

    return (
        f"Opening {name}."
    )


# ============================================================
# YOUTUBE
# ============================================================

def open_youtube():

    return open_browser(
        "https://www.youtube.com",
        "YouTube"
    )


# ============================================================
# GOOGLE
# ============================================================

def open_google():

    return open_browser(
        "https://www.google.com",
        "Google"
    )


# ============================================================
# GOOGLE SEARCH
# ============================================================

def google_search(
    query
):

    url = (
        "https://www.google.com/search?q="
        + urllib.parse.quote(
            query
        )
    )

    return open_browser(
        url,
        f"Google search for {query}"
    )


# ============================================================
# YOUTUBE SEARCH
# ============================================================

def youtube_search(
    query
):

    url = (
        "https://www.youtube.com/results?"
        "search_query="
        + urllib.parse.quote(
            query
        )
    )

    return open_browser(
        url,
        f"YouTube search for {query}"
    )


# ============================================================
# TIME
# ============================================================

def get_time():

    now = datetime.datetime.now()

    return (
        "The current time is "
        + now.strftime("%I:%M %p")
        + "."
    )


# ============================================================
# DATE
# ============================================================

def get_date():

    now = datetime.datetime.now()

    return (
        "Today is "
        + now.strftime(
            "%A, %d %B %Y"
        )
        + "."
    )


# ============================================================
# CALCULATOR
# ============================================================

def calculate(
    expression
):

    try:

        expression = (
            expression
            .lower()
            .strip()
        )

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

        expression = expression.replace(
            "into",
            "*"
        )

        expression = re.sub(
            r"[^0-9+\-*/().% ]",
            "",
            expression
        )

        if not expression:

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
# WEATHER
# ============================================================

def get_weather(
    city
):

    try:

        city_encoded = (
            urllib.parse.quote(
                city
            )
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

        response = (
            urllib.request.urlopen(
                request,
                timeout=10
            )
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
# WIKIPEDIA
# ============================================================

def wikipedia_search(
    query
):

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
            "I could not find "
            "that information."
        )


# ============================================================
# GITHUB
# ============================================================

GITHUB_USERNAME = os.getenv(
    "GITHUB_USERNAME",
    ""
)

GITHUB_TOKEN = os.getenv(
    "GITHUB_TOKEN",
    ""
)


def github_headers():

    headers = {
        "Accept":
            "application/vnd.github+json"
    }

    if GITHUB_TOKEN:

        headers[
            "Authorization"
        ] = (
            "Bearer "
            + GITHUB_TOKEN
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
            + GITHUB_USERNAME
            + "/repos"
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
# PDF READER
# ============================================================

def read_pdf(
    data
):

    if PdfReader is None:

        return (
            "PDF reader is not available."
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
            "the PDF."
        )


# ============================================================
# TXT READER
# ============================================================

def read_txt(
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
            "the text file."
        )


# ============================================================
# DOCX READER
# ============================================================

def read_docx(
    data
):

    if Document is None:

        return (
            "Word document support "
            "is not available."
        )

    temporary_path = None

    try:

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".docx"
        ) as file:

            file.write(data)

            temporary_path = file.name

        document = Document(
            temporary_path
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

        if temporary_path:

            try:

                os.remove(
                    temporary_path
                )

            except Exception:

                pass


# ============================================================
# DOCUMENT READER
# ============================================================

def read_document(
    filename,
    data
):

    extension = (
        os.path.splitext(
            filename
        )[1]
        .lower()
    )

    if extension == ".pdf":

        return read_pdf(
            data
        )

    if extension == ".txt":

        return read_txt(
            data
        )

    if extension == ".docx":

        return read_docx(
            data
        )

    return (
        "I can read PDF, TXT "
        "and DOCX files."
    )


# ============================================================
# PREFIX EXTRACTOR
# ============================================================

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


# ============================================================
# COMMAND ENGINE
# ============================================================

def process_command(
    command
):

    command = (
        command
        .lower()
        .strip()
    )


    # --------------------------------------------------------
    # WAKE WORD
    # --------------------------------------------------------

    for wake_word in [
        "hey sai",
        "okay sai",
        "ok sai",
        "sai"
    ]:

        if command.startswith(
            wake_word
        ):

            command = command[
                len(wake_word):
            ].strip()

            break


    if not command:

        return (
            "Yes, I am listening."
        )


    # ========================================================
    # STOP
    # ========================================================

    if command in [
        "stop",
        "exit",
        "quit",
        "goodbye",
        "go offline"
    ]:

        return "__STOP__"


    # ========================================================
    # TIME
    # ========================================================

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


    # ========================================================
    # DATE
    # ========================================================

    if (
        command == "date"
        or
        "what is the date"
        in command
        or
        "what is today's date"
        in command
    ):

        return get_date()


    # ========================================================
    # OPEN YOUTUBE
    # ========================================================

    if (
        "open youtube"
        in command
        or
        "launch youtube"
        in command
        or
        "start youtube"
        in command
    ):

        return open_youtube()


    # ========================================================
    # OPEN GOOGLE
    # ========================================================

    if (
        "open google"
        in command
        or
        "launch google"
        in command
        or
        "start google"
        in command
    ):

        return open_google()


    # ========================================================
    # YOUTUBE SEARCH
    # ========================================================

    query = extract_after(
        command,
        [
            "search youtube for",
            "search youtube",
            "youtube search for",
            "play youtube",
            "play on youtube"
        ]
    )

    if query:

        return youtube_search(
            query
        )


    # ========================================================
    # GOOGLE SEARCH
    # ========================================================

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


    # ========================================================
    # WIKIPEDIA
    # ========================================================

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


    # ========================================================
    # WEATHER
    # ========================================================

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


    # ========================================================
    # CALCULATOR
    # ========================================================

    if command.startswith(
        "calculate"
    ):

        expression = command[
            len("calculate"):
        ].strip()

        return calculate(
            expression
        )


    # ========================================================
    # GITHUB
    # ========================================================

    if any(
        phrase in command
        for phrase in [
            "list github repositories",
            "show github repositories",
            "my github repositories"
        ]
    ):

        repositories = (
            github_repositories()
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


    # ========================================================
    # UNKNOWN
    # ========================================================

    return (
        "I heard you, but I do not "
        "understand that command yet."
    )


# ============================================================
# SPEECH RECOGNITION
# ============================================================

def recognize_audio(
    audio_bytes
):

    recognizer = sr.Recognizer()

    try:

        with sr.AudioFile(
            io.BytesIO(
                audio_bytes
            )
        ) as source:

            audio = (
                recognizer.record(
                    source
                )
            )

        command = (
            recognizer
            .recognize_google(
                audio,
                language="en-IN"
            )
        )

        return command

    except sr.UnknownValueError:

        return None

    except sr.RequestError:

        return None

    except Exception:

        return None


# ============================================================
# PROCESS VOICE
# ============================================================

def process_voice(
    audio_bytes
):

    command = recognize_audio(
        audio_bytes
    )

    if not command:

        speak(
            "Sorry, I could not "
            "understand you."
        )

        return


    response = process_command(
        command
    )


    if response == "__STOP__":

        speak(
            "SAI Voice OS is "
            "going offline."
        )

        return


    speak(
        response
    )


# ============================================================
# MAIN UI
# ============================================================

st.markdown(
    """
    <h1 style="
        text-align:center;
        font-size:48px;
    ">
        🎙️ SAI Voice OS
    </h1>
    """,
    unsafe_allow_html=True
)


st.markdown(
    """
    <p style="
        text-align:center;
        font-size:20px;
    ">
        Voice-first accessibility operating system
    </p>
    """,
    unsafe_allow_html=True
)


# ============================================================
# VOICE INPUT
# ============================================================

audio = st.audio_input(
    "🎙️ Speak to SAI"
)


# ============================================================
# PROCESS AUDIO
# ============================================================

if audio is not None:

    process_voice(
        audio.getvalue()
    )
