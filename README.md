# 🎙️ SAI VoiceOS

An accessibility-focused, voice-first computing environment designed for blind and visually impaired users.

## Current MVP
This is the first engineering prototype, not a replacement operating system.

- Streamlit prototype UI
- Natural-language command routing
- Safe application launching
- Voice-style folder creation
- Workspace file listing
- System status
- SQLite command history
- Safety architecture

## Architecture

Voice → Speech-to-Text → AI/Intent → Safety/Permissions → OS/Browser/File Action → Text-to-Speech

## Example commands
- `help`
- `system status`
- `list files`
- `create folder Projects`
- `open calculator`
- `open notepad`

## Run

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Roadmap
1. Real microphone + speech-to-text
2. Text-to-speech
3. Windows accessibility APIs / screen reader
4. OCR and screen understanding
5. Browser, documents, email and messaging controls
6. Safety confirmations and permissions
7. SAI VoiceOS desktop shell
8. Linux-based accessibility environment
9. Android accessibility application

## Security principle
The AI should never have unrestricted OS access. It should produce a structured intent, which passes permission and safety checks before an approved tool executes the action.

This project is an early prototype and requires accessibility, privacy, security and usability testing before production use.
