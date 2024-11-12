# В новом файле, например, app/database/event_listeners.py

from sqlalchemy import event
from app.database.db_globals import Session  # Ваша сессия базы данных
from app.models.audio import AudioFile
from app.models.transcription import Transcription

# Функция для обновления флага transcribed
def update_transcribed_status(audio_id, session):
    transcription_exists = session.query(Transcription).filter_by(audio_id=audio_id).first() is not None
    session.query(AudioFile).filter_by(audio_id=audio_id).update(
        {"transcribed": transcription_exists}
    )
    session.commit()

# Слушатели для событий Transcription
@event.listens_for(Transcription, 'after_insert')
@event.listens_for(Transcription, 'after_delete')
def after_transcription_change(mapper, connection, target):
    with Session() as db_session:
        update_transcribed_status(target.audio_id, db_session)

@event.listens_for(Transcription, 'after_update')
def after_transcription_update(mapper, connection, target):
    if 'audio_id' in target.__dict__:
        with Session() as db_session:
            update_transcribed_status(target.audio_id, db_session)
