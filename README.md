# SAI VoiceOS Complete

## Streamlit Cloud

Deploy `sai_voiceos.py`.

The root `requirements.txt` installs only cloud-safe dependencies.

Add these Streamlit Secrets:

GITHUB_TOKEN = "YOUR_GITHUB_TOKEN"
GITHUB_REPOSITORY = "YOUR_USERNAME/YOUR_REPOSITORY"
GITHUB_BRANCH = "main"

## Local Windows

Install:

    pip install -r local_requirements.txt

Run:

    python sai_voiceos.py

Configure GitHub:

    setx SAI_GITHUB_TOKEN "YOUR_GITHUB_TOKEN"
    setx SAI_GITHUB_REPOSITORY "YOUR_USERNAME/YOUR_REPOSITORY"
    setx SAI_GITHUB_BRANCH "main"

Close and reopen the terminal after `setx`.

## Features

- Speech-to-text
- Text-to-speech
- Calculator
- Notepad
- Browser
- Google
- YouTube
- WhatsApp
- Screenshot
- Music
- Voice notes
- Weather
- Internet search
- Direct web answers when available
- GitHub upload/push
- GitHub download
- GitHub file listing
- GitHub PDF reading
- GitHub PDF search
- Local PDF reading
- Search inside PDF
- Text file reading
- Local file search
- Unknown commands fall back to Internet search

## Important

Streamlit Cloud runs remotely. It cannot control the user's personal Windows desktop.

The same Python file therefore contains both:
- cloud functionality
- local Windows functionality

For actual microphone, TTS, Calculator, WhatsApp Desktop, screenshot and local file control, run the file on the user's computer.
