import re

def detect_intent(command):
    text = command.lower().strip()
    if text in {"help","commands","what can you do"}:
        return "HELP", {}
    if text in {"status","system status","computer status"}:
        return "SYSTEM_STATUS", {}
    if "list files" in text or "show files" in text or "what files" in text:
        return "LIST_FILES", {}
    m = re.match(r"(?:create|make)\s+(?:a\s+)?folder(?:\s+(?:called|named))?\s+(.+)", text)
    if m:
        return "CREATE_FOLDER", {"name": m.group(1).strip()}
    m = re.match(r"(?:open|launch|start)\s+(.+)", text)
    if m:
        return "OPEN_APPLICATION", {"name": m.group(1).strip()}
    return "UNKNOWN", {}
