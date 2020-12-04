from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, \
    ValidationError
from flask_login import current_user
from application.models import User


class RegistrationForm(FlaskForm):
    username = StringField('Usuário', validators=[
                           DataRequired(), Length(min=4, max=20)])

    email = StringField('Email', validators=[DataRequired(), Email()])

    password = PasswordField('Senha', validators=[DataRequired()])

    confirm_password = PasswordField(
        'Confirmar Senha', validators=[DataRequired(), EqualTo('password')])

    submit = SubmitField('Criar Conta')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(
                'Esse nome de usuário já existe! Por favor, escolha outro.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError(
                'Esse email já está sendo usado! Por favor, escolha outro.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])

    password = PasswordField('Password', validators=[DataRequired()])

    remember = BooleanField('Mantenha-me Conectado')

    submit = SubmitField('Entrar')


class UpdateAccountForm(FlaskForm):
    username = StringField('Usuário', validators=[
                           DataRequired(), Length(min=4, max=20)])

    email = StringField('Email', validators=[DataRequired(), Email()])

    picture = FileField('Trocar Imagem',
                        validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Atualizar Perfil')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError(
                    'Esse usuário já existe! Insira um usuário diferente.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError(
                    'Esse email já está em uso, insira outro email.')


class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Enviar')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError("Informe um email válido!")


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Nova Senha', validators=[DataRequired()])
    confirm_password = PasswordField(
        'Confirmar Nova Senha',
        validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Mudar Senha')
