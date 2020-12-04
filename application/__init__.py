import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail


# SECRET_KEY chave para configuração dos cookie de segurança, aplicado
# para lembrar o usuário da entrada automática, e salvar os dados
# A configuração do app.config['SQLALCHEMY']
# está definindo o caminho em relação a o arquivo blog.db
# instância do DB, pode utilizar para
# montar a estrutura do banco de dados
# -=========================================-#
# Função flask irá criar a instância para inicalização do application
# função SQLAlchemy, irá aplicar as tables para o usuário e posts
# Bcrypt é o método de hash para password, gerando segurança para o usuário
# flask_login é o modulo que irá criar a instância para o usuário,
# por meio da função LoginManager.

# =============================================#
# flask_mail é a extensão de API para gerar o servidor de email com TLS
# Vai ter um servidor específico para esse email de troca de senha
# com a porta 587 e usuário e senha para acessar.

app = Flask(__name__)
app.config['SECRET_KEY'] = '1c8e5a7647c74da5d98be7c624c9f373'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
login_manager.login_message = 'Faça o login para acessar esse conteúdo!'
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER')
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS')
mail = Mail(app)

from application.users.routes import users
from application.posts.routes import posts
from application.main.routes import main
from application.errors.handlers import errors

app.register_blueprint(users)
app.register_blueprint(posts)
app.register_blueprint(main)
app.register_blueprint(errors)
