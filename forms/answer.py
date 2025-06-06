from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired


class AnswerForm(FlaskForm):
    answer = TextAreaField('Ответ', validators=[DataRequired()])
    submit = SubmitField('Опубликовать')