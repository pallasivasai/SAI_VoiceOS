# ============================================================
#                    SAI VOICE OS
#              ALWAYS LISTENING WINDOWS OS
# ============================================================

import os
import re
import time
import webbrowser
import subprocess
import datetime
import urllib.parse
import platform

import speech_recognition as sr
import pyttsx3
import pyautogui


# ============================================================
# SYSTEM CHECK
# ============================================================

if platform.system().lower() != "windows":

    print("SAI Voice OS is designed for Windows.")

    raise SystemExit


# ============================================================
# SAI CONFIGURATION
# ============================================================

SAI_NAME = "SAI"

LANGUAGE = "en-IN"

LISTEN_TIMEOUT = 5

PHRASE_TIME_LIMIT = 10

VOICE_RATE = 155

VOICE_VOLUME = 1.0


# ============================================================
# SPEECH RECOGNIZER
# ============================================================

recognizer = sr.Recognizer()

recognizer.energy_threshold = 300

recognizer.dynamic_energy_threshold = True

recognizer.pause_threshold = 0.8

recognizer.phrase_threshold = 0.3

recognizer.non_speaking_duration = 0.5


# ============================================================
# TEXT TO SPEECH
# ============================================================

engine = pyttsx3.init()

engine.setProperty(
    "rate",
    VOICE_RATE
)

engine.setProperty(
    "volume",
    VOICE_VOLUME
)


# ============================================================
# FIND ENGLISH VOICE
# ============================================================

try:

    voices = engine.getProperty(
        "voices"
    )

    for voice in voices:

        voice_text = (
            voice.name
            + " "
            + voice.id
        ).lower()

        if (
            "english" in voice_text
            or "en_" in voice_text
            or "en-" in voice_text
        ):

            engine.setProperty(
                "voice",
                voice.id
            )

            break

except Exception:

    pass


# ============================================================
# SPEAK
# ============================================================

def speak(text):

    if not text:
        return

    print(
        "SAI:",
        text
    )

    try:

        engine.say(
            text
        )

        engine.runAndWait()

    except Exception as error:

        print(
            "TTS error:",
            error
        )


# ============================================================
# OPEN URL
# ============================================================

def open_url(
    url,
    name
):

    try:

        webbrowser.open(
            url,
            new=2
        )

        return (
            f"Opening {name}."
        )

    except Exception:

        return (
            f"I could not open {name}."
        )


# ============================================================
# YOUTUBE
# ============================================================

def open_youtube():

    return open_url(
        "https://www.youtube.com",
        "YouTube"
    )


# ============================================================
# GOOGLE
# ============================================================

def open_google():

    return open_url(
        "https://www.google.com",
        "Google"
    )


# ============================================================
# GOOGLE SEARCH
# ============================================================

def search_google(
    query
):

    url = (
        "https://www.google.com/search?q="
        + urllib.parse.quote(query)
    )

    return open_url(
        url,
        f"Google search for {query}"
    )


# ============================================================
# YOUTUBE SEARCH
# ============================================================

def search_youtube(
    query
):

    url = (
        "https://www.youtube.com/results?"
        "search_query="
        + urllib.parse.quote(query)
    )

    return open_url(
        url,
        f"YouTube search for {query}"
    )


# ============================================================
# OPEN NOTEPAD
# ============================================================

def open_notepad():

    try:

        subprocess.Popen(
            ["notepad.exe"]
        )

        return "Opening Notepad."

    except Exception:

        return (
            "I could not open Notepad."
        )


# ============================================================
# OPEN CALCULATOR
# ============================================================

def open_calculator():

    try:

        subprocess.Popen(
            ["calc.exe"]
        )

        return "Opening Calculator."

    except Exception:

        return (
            "I could not open Calculator."
        )


# ============================================================
# OPEN FILE EXPLORER
# ============================================================

def open_explorer():

    try:

        subprocess.Popen(
            ["explorer.exe"]
        )

        return (
            "Opening File Explorer."
        )

    except Exception:

        return (
            "I could not open File Explorer."
        )


# ============================================================
# OPEN CHROME
# ============================================================

def open_chrome():

    try:

        subprocess.Popen(
            [
                "cmd",
                "/c",
                "start",
                "chrome"
            ]
        )

        return "Opening Chrome."

    except Exception:

        return (
            "I could not open Chrome."
        )


# ============================================================
# OPEN WHATSAPP
# ============================================================

def open_whatsapp():

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

        return open_url(
            "https://web.whatsapp.com",
            "WhatsApp Web"
        )


# ============================================================
# SCREENSHOT
# ============================================================

def take_screenshot():

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
# CURRENT TIME
# ============================================================

def current_time():

    now = datetime.datetime.now()

    return (
        "The current time is "
        + now.strftime("%I:%M %p")
        + "."
    )


# ============================================================
# CURRENT DATE
# ============================================================

def current_date():

    now = datetime.datetime.now()

    return (
        "Today is "
        + now.strftime("%A, %d %B %Y")
        + "."
    )


# ============================================================
# CALCULATOR
# ============================================================

def calculate(
    expression
):

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

        expression = expression.replace(
            "into",
            "*"
        )

        expression = expression.replace(
            "point",
            "."
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
# SYSTEM VOLUME
# ============================================================

def volume_up():

    try:

        for _ in range(5):

            pyautogui.press(
                "volumeup"
            )

        return (
            "Volume increased."
        )

    except Exception:

        return (
            "I could not change the volume."
        )


def volume_down():

    try:

        for _ in range(5):

            pyautogui.press(
                "volumedown"
            )

        return (
            "Volume decreased."
        )

    except Exception:

        return (
            "I could not change the volume."
        )


def mute_volume():

    try:

        pyautogui.press(
            "volumemute"
        )

        return (
            "Volume muted."
        )

    except Exception:

        return (
            "I could not mute the volume."
        )


# ============================================================
# LOCK WINDOWS
# ============================================================

def lock_windows():

    try:

        subprocess.run(
            [
                "rundll32.exe",
                "user32.dll,LockWorkStation"
            ]
        )

        return (
            "Locking the computer."
        )

    except Exception:

        return (
            "I could not lock the computer."
        )


# ============================================================
# OPEN WEBSITE
# ============================================================

def open_website(
    name,
    url
):

    return open_url(
        url,
        name
    )


# ============================================================
# EXTRACT AFTER PREFIX
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
# REMOVE WAKE WORD
# ============================================================

def remove_wake_word(
    command
):

    wake_words = [
        "sai",
        "hey sai",
        "ok sai",
        "okay sai"
    ]

    command = command.strip()

    for wake in wake_words:

        if command.startswith(
            wake
        ):

            command = command[
                len(wake):
            ].strip()

            break

    return command


# ============================================================
# COMMAND PROCESSOR
# ============================================================

def process_command(
    original_command
):

    command = (
        original_command
        .lower()
        .strip()
    )

    # --------------------------------------------------------
    # REMOVE WAKE WORD
    # --------------------------------------------------------

    command = remove_wake_word(
        command
    )

    if not command:

        return (
            "Yes, I am listening."
        )


    # ========================================================
    # EXIT
    # ========================================================

    if command in [
        "exit",
        "quit",
        "shutdown sai",
        "stop listening",
        "go offline",
        "goodbye"
    ]:

        return "__EXIT__"


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

        return current_time()


    # ========================================================
    # DATE
    # ========================================================

    if (
        command == "date"
        or
        "what is today's date"
        in command
        or
        "what is the date"
        in command
    ):

        return current_date()


    # ========================================================
    # YOUTUBE
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
    # GOOGLE
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
            "play on youtube",
            "play youtube"
        ]
    )

    if query:

        return search_youtube(
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

        return search_google(
            query
        )


    # ========================================================
    # NOTEPAD
    # ========================================================

    if (
        "open notepad"
        in command
        or
        "start notepad"
        in command
    ):

        return open_notepad()


    # ========================================================
    # CALCULATOR APP
    # ========================================================

    if (
        "open calculator"
        in command
        or
        "start calculator"
        in command
    ):

        return open_calculator()


    # ========================================================
    # CALCULATION
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
    # CHROME
    # ========================================================

    if (
        "open chrome"
        in command
        or
        "start chrome"
        in command
    ):

        return open_chrome()


    # ========================================================
    # FILE EXPLORER
    # ========================================================

    if (
        "open file explorer"
        in command
        or
        "open explorer"
        in command
    ):

        return open_explorer()


    # ========================================================
    # WHATSAPP
    # ========================================================

    if (
        "open whatsapp"
        in command
    ):

        return open_whatsapp()


    # ========================================================
    # SCREENSHOT
    # ========================================================

    if (
        "take screenshot"
        in command
        or
        command == "screenshot"
    ):

        return take_screenshot()


    # ========================================================
    # VOLUME UP
    # ========================================================

    if (
        "increase volume"
        in command
        or
        "volume up"
        in command
        or
        "turn up volume"
        in command
    ):

        return volume_up()


    # ========================================================
    # VOLUME DOWN
    # ========================================================

    if (
        "decrease volume"
        in command
        or
        "volume down"
        in command
        or
        "turn down volume"
        in command
    ):

        return volume_down()


    # ========================================================
    # MUTE
    # ========================================================

    if (
        "mute"
        in command
        or
        "mute volume"
        in command
    ):

        return mute_volume()


    # ========================================================
    # LOCK
    # ========================================================

    if (
        "lock computer"
        in command
        or
        "lock the computer"
        in command
        or
        "lock my computer"
        in command
    ):

        return lock_windows()


    # ========================================================
    # OPEN COMMON WEBSITES
    # ========================================================

    if (
        command == "open github"
    ):

        return open_website(
            "GitHub",
            "https://github.com"
        )


    if (
        command == "open gmail"
    ):

        return open_website(
            "Gmail",
            "https://mail.google.com"
        )


    if (
        command == "open facebook"
    ):

        return open_website(
            "Facebook",
            "https://www.facebook.com"
        )


    if (
        command == "open linkedin"
    ):

        return open_website(
            "LinkedIn",
            "https://www.linkedin.com"
        )


    # ========================================================
    # UNKNOWN COMMAND
    # ========================================================

    return (
        "I heard you, but I do not "
        "know how to perform that "
        "action yet."
    )


# ============================================================
# MICROPHONE CALIBRATION
# ============================================================

def calibrate_microphone():

    print()
    print(
        "Calibrating microphone..."
    )

    try:

        with sr.Microphone() as source:

            recognizer.adjust_for_ambient_noise(
                source,
                duration=2
            )

        print(
            "Microphone ready."
        )

    except Exception as error:

        print(
            "Microphone initialization error:",
            error
        )

        speak(
            "I could not access "
            "the microphone."
        )

        raise


# ============================================================
# ALWAYS LISTEN
# ============================================================

def listen_forever():

    calibrate_microphone()

    speak(
        "SAI Voice OS is ready. "
        "I am listening."
    )

    while True:

        try:

            # ------------------------------------------------
            # MICROPHONE ALWAYS ACTIVE
            # ------------------------------------------------

            with sr.Microphone() as source:

                print()
                print(
                    "🎙️ Listening..."
                )

                try:

                    audio = recognizer.listen(
                        source,
                        timeout=LISTEN_TIMEOUT,
                        phrase_time_limit=PHRASE_TIME_LIMIT
                    )

                except sr.WaitTimeoutError:

                    continue


            # ------------------------------------------------
            # SPEECH RECOGNITION
            # ------------------------------------------------

            print(
                "Recognizing..."
            )

            try:

                command = (
                    recognizer
                    .recognize_google(
                        audio,
                        language=LANGUAGE
                    )
                )

            except sr.UnknownValueError:

                # Nothing understandable.
                # Immediately listen again.

                continue

            except sr.RequestError:

                speak(
                    "Speech recognition "
                    "service is unavailable. "
                    "I will keep listening."
                )

                time.sleep(2)

                continue


            # ------------------------------------------------
            # COMMAND
            # ------------------------------------------------

            command = (
                command
                .lower()
                .strip()
            )

            print(
                "USER:",
                command
            )


            # ------------------------------------------------
            # PROCESS
            # ------------------------------------------------

            response = process_command(
                command
            )


            # ------------------------------------------------
            # EXIT
            # ------------------------------------------------

            if response == "__EXIT__":

                speak(
                    "SAI Voice OS is "
                    "going offline."
                )

                break


            # ------------------------------------------------
            # ANSWER
            # ------------------------------------------------

            speak(
                response
            )


            # ------------------------------------------------
            # IMPORTANT
            # ------------------------------------------------
            # After speaking,
            # automatically return to listening.
            # ------------------------------------------------

            time.sleep(0.3)


        except KeyboardInterrupt:

            speak(
                "SAI Voice OS is "
                "going offline."
            )

            break


        except Exception as error:

            print(
                "System error:",
                error
            )

            time.sleep(1)

            continue


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print(
        "=========================================="
    )

    print(
        "          SAI VOICE OS"
    )

    print(
        "       ALWAYS LISTENING MODE"
    )

    print(
        "=========================================="
    )

    print()

    print(
        "Microphone will start automatically."
    )

    print(
        "No manual microphone ON/OFF required."
    )

    print()

    listen_forever()


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    main()
