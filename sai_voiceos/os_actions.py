import platform
import subprocess
from pathlib import Path
from .config import WORKSPACE_DIR

def system_status():
    return f"Operating system: {platform.system()} {platform.release()}."

def list_workspace():
    items = sorted(p.name for p in WORKSPACE_DIR.iterdir())
    return "The SAI workspace is empty." if not items else "I found: " + ", ".join(items)

def create_folder(name):
    safe_name = Path(name).name.strip()
    if not safe_name:
        return "Folder name is empty."
    (WORKSPACE_DIR / safe_name).mkdir(exist_ok=True)
    return f"Folder '{safe_name}' is ready."

def open_application(name):
    name = name.lower().strip()
    if platform.system() == "Windows":
        mapping = {"calculator":"calc.exe","notepad":"notepad.exe"}
        cmd = mapping.get(name)
        if not cmd:
            return f"I don't have a safe launcher mapping for '{name}'."
        subprocess.Popen(cmd, shell=False)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open","-a",name])
    else:
        subprocess.Popen([name])
    return f"Opening {name}."
