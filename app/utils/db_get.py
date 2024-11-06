

def get_prompt(prompt_id):
    from app.database.managers.prompt_manager import PromptManager
    db = PromptManager()
    prompt = db.get_prompt_by_prompt_id(prompt_id)
    return prompt['text']

def get_transcription(transcription_id):
    from app.database.managers.transcription_manager import TranscriptionManager
    db = TranscriptionManager()
    transcription = db.get_transcription_by_id(transcription_id)
    return transcription['text']