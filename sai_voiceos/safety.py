DANGEROUS_INTENTS = {
    "DELETE_FILE","DELETE_FOLDER","SHUTDOWN","RESTART","SEND_MESSAGE","SEND_EMAIL"
}
def requires_confirmation(intent):
    return intent in DANGEROUS_INTENTS
