import os
import secrets
from PIL import Image
from flask import render_template,  url_for, flash, redirect, request
from application import app, db, bcrypt
from application.forms import RegistrationForm, LoginForm, UpdateAccountForm
from application.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required


# form metodo de formulário, que irá gerar automaticamente no HTML
# RegistrationForm é a instância de formulário de registro

# flash para gerar uma mensagem de aviso

# url_for vai acessar a função direta da aplicação
#  e sincronizar o html com flask

# login_required é a função que estabelecerá a condição de estar logado
# para acessar o conteúdo

# UpdateAccountForm é uma que se aplica para
# atualizar o perfil do usuário

# os é forma do sistema operacional pode
# ser utilizado para verificar a extensão do arquivo


posts = [

    {
        'author': 'Jair Messias Bolsonaro',
        'title': 'Blog Post 1',
        'content': 'First post content',
        'date_posted': 'Novembro, 02, 2020'
    },

    {
        'author': 'Donald Trump',
        'title': 'Blog Post 2',
        'content': 'Second post content',
        'date_posted': 'Novembro, 03, 2020'
    }
]


@app.route('/')
def index():
    return render_template('index.html', posts=posts, title='Inicío')


@app.route('/about')
def about():

    return render_template('about.html', title='Sobre')


# flash Vai  gerar mensagem de alerta que a conta foi criada com sucesso.
    # redirect (url_for('index')) está acessando a função index
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data,
                    password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Conta criada com sucesso! Você já pode efetuar o login',
              'success')

        return redirect(url_for('login'))

    return render_template('register.html', title='Cadastrar', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,
                                               form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash(f'Seja Bem vindo ao Direito Sem Preconceito {user.username}',
                  'success')
            return redirect(next_page) if next_page \
                else redirect(url_for('index'))

        else:
            flash('Não foi possível acessar sua conta.\
                Por favor verifique seu email e senha', 'danger')
    return render_template('login.html', title='Entrar', form=form)


@app.route('/logout')
def logout():
    logout_user()
    flash('Você acabou de desconectar da sessão.', 'warning')
    return redirect(url_for('index'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path,
                                'static/profile_pics',
                                picture_fn)
    form_picture.save(picture_path)

    output_size = (125, 125)
    new_img = Image.open(form_picture)
    new_img.thumbnail(output_size)
    new_img.save(picture_path)

    return picture_fn


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Perfil atualizado com sucesso!", 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    image_file = url_for(
        'static', filename='profile_pics/' + current_user.image_file)

    return render_template('account.html', title='Conta',
                           image_file=image_file, form=form)
