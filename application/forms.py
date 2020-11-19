from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, \
    TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, \
    ValidationError
from application.models import User

# Criando o campo de usuário da classe form
# validators garatem que o campo não ficará vazio
# DataRequired se aplicar como bool para verificar
# se está vazio ou não o campo de text.

# Lenght irá verificar se a string username está com min 2 e max 20 caracteres.

# Email é um verificador de email, se é válido ou não.

# Equalto aplica para verificar se o password
# é igual ao confirm passsword

# Passwordfiel função que irá gerar
# as regras de um password

# SubmitFiel é o botão para enviar as informações.

# BooleanField será utilizado como um botão que salva
#  automatícamente os dados de entrada.

# Security será necessário uma chave,
# para proteger contra a modificação de cookeis


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
                    'Esse usuário já existe, insira um nome diferente.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError(
                    'Esse email já está em uso, insira outro email.')


class PostForm(FlaskForm):
    title = StringField('Título', validators=[
                        DataRequired(), Length(min=4, max=120)])
    content = TextAreaField('Mensagem', validators=[
                            DataRequired(), Length(min=20, max=10000)])
    submit = SubmitField('Publicar')
