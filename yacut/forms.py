from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class URLForm(FlaskForm):
    original_link = StringField(
        'Введите длинную ссылку',
        validators=[DataRequired(message='Обязательное поле')]
    )
    custom_id = StringField(
        'Напишите короткий идентификатор',
        validators=[Length(0, 16,
                           message='Максимальная длина 16 символов')]
    )
    submit = SubmitField('Создать')
