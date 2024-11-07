from flask_wtf import FlaskForm
from wtforms import StringField, FileField, SubmitField
from wtforms.validators import DataRequired

class AudioForm(FlaskForm):
    prompt = StringField('Введите промпт', validators=[DataRequired()])
    audio = FileField('Загрузите аудио', validators=[DataRequired()])
    submit = SubmitField('Отправить')
