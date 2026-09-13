from pathlib import Path
APP_NAME = "SAI VoiceOS"
VERSION = "0.1.0"
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
WORKSPACE_DIR = BASE_DIR / "workspace"
DATA_DIR.mkdir(exist_ok=True)
WORKSPACE_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "voiceos.db"
