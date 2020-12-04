from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


class PostForm(FlaskForm):
    title = StringField('Título', validators=[
                        DataRequired(), Length(min=4, max=120)])
    content = TextAreaField('Mensagem', validators=[
                            DataRequired(), Length(min=20, max=10000)])
    submit = SubmitField('Publicar')
