from dataclasses import dataclass
from .database import init_db, save_command, fetch_history
from .intents import detect_intent
from .safety import requires_confirmation
from .os_actions import system_status, list_workspace, create_folder, open_application

@dataclass
class CommandResult:
    success: bool
    message: str
    intent: str

class SAICommandEngine:
    def __init__(self):
        init_db()

    def execute(self, command):
        intent, args = detect_intent(command)
        if requires_confirmation(intent):
            msg = "This action requires explicit confirmation and is disabled in the MVP."
            save_command(command,intent,"BLOCKED",msg)
            return CommandResult(False,msg,intent)

        if intent == "HELP":
            msg = "Try: help, system status, list files, create folder Projects, open calculator."
        elif intent == "SYSTEM_STATUS":
            msg = system_status()
        elif intent == "LIST_FILES":
            msg = list_workspace()
        elif intent == "CREATE_FOLDER":
            msg = create_folder(args["name"])
        elif intent == "OPEN_APPLICATION":
            msg = open_application(args["name"])
        else:
            msg = "I did not understand. Say 'help' for supported commands."

        status = "SUCCESS" if intent != "UNKNOWN" else "UNKNOWN"
        save_command(command,intent,status,msg)
        return CommandResult(intent != "UNKNOWN",msg,intent)

    def history(self):
        return fetch_history()
