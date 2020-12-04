from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from application import db, bcrypt
from application.models import User, Post
from application.users.forms import (RegistrationForm, LoginForm,
                                     UpdateAccountForm,
                                     RequestResetForm, ResetPasswordForm)
from application.users.utils import save_picture, send_reset_email

# Blueprint será utilizado para modularizar, geralmente
# aplicado para projetos maiores, separando os mesmo em fragmentos.
# A principal função dele aqui será uma rota local,
# não utilizando mais a variável global, mas variável para o diretório users
# Esse users é aplicado para qualquer tipo de variável
# que tenha dentro do projeto

users = Blueprint('users', __name__)


@users.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
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

        return redirect(url_for('users.login'))

    return render_template('register.html', title='Cadastrar', form=form)

# acessar conta (login)


@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
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
                else redirect(url_for('main.index'))

        else:
            flash('Não foi possível acessar sua conta.\
                Por favor verifique seu email e senha', 'danger')
    return render_template('login.html', title='Entrar', form=form)

# rota para sair do users


@users.route('/logout')
def logout():
    logout_user()
    flash('Você acabou de desconectar da sessão.', 'warning')
    return redirect(url_for('main.index'))


@users.route('/account', methods=['GET', 'POST'])
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
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    image_file = url_for(
        'static', filename='profile_pics/' + current_user.image_file)

    return render_template('account.html', title='Conta',
                           image_file=image_file, form=form)


@users.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)


# rota requisição de troca de senha (vai gerar um token 30min)


@users.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash("Acabamos de enviar um e-mail com instruções\
              para que você possa efetuar sua alteração de senha.", 'info')
        return redirect(url_for('users.login'))
    return render_template('request_reset_pass.html', form=form,
                           title='Mudando Senha')


# rota para utilizar o POST e aplicar a alteração da senha
@users.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_token(token)
    if user is None:
        flash("Sua solicitação de troca de senha expirou.\
              Faça uma nova requisição!", 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Você acabou de mudar sua senha com sucesso!',
              'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', form=form,
                           title='Mudando Senha')
