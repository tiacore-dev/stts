

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

def get_audio_name(audio_id):
    from app.database.managers.audio_manager import AudioFileManager
    db = AudioFileManager()
    file = db.get_audio_by_id(audio_id)
    return file['file_name']

def get_prompt_name(prompt_id):
    from app.database.managers.prompt_manager import PromptManager
    db = PromptManager()
    prompt = db.get_prompt_by_prompt_id(prompt_id)
    return prompt['prompt_name']

def transcribed_audio(audio_id):
    from app.database.managers.audio_manager import AudioFileManager
    db = AudioFileManager()
    is_set=db.set_transcribed_audio(audio_id)
    return is_set