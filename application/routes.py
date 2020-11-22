import os
import secrets
from PIL import Image
from flask import render_template,  url_for, flash, redirect, request, abort
from application import app, db, bcrypt
from application.forms import RegistrationForm, LoginForm, UpdateAccountForm, \
    PostForm
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

# Postform é a class que contém a instância
# de formulário de postagem (title, content)


@app.route('/', methods=['GET', 'POST'], defaults={"page": 1})
@app.route('/<int:page>', methods=['GET', 'POST'])
def index(page):
    page = page
    pages = 5
    posts = Post.query.order_by(
        Post.date_posted.desc()).paginate(page, pages, error_out=False)
    if request.method == 'POST' and 'tag' in request.form:
        tag = request.form["tag"]
        search = "%{}%".format(tag)
        posts = Post.query.filter(Post.title.like(search)).paginate(
            per_page=pages, error_out=False)
        result = Post.query.filter(Post.title.like(search)).count()
        flash(f"A pesquisa encontrou {result} resultado.", 'info')

        return render_template('index.html', posts=posts, tag=tag)

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


@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data,
                    author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Conteúdo publicado com sucesso!', 'success')
        return redirect(url_for('index'))
    return render_template('posting.html', title='Novas Postagens',
                           form=form, legend='Nova Postagem')


@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)  # criar página de erro.
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash("Postagem atualizada com sucesso!", 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('posting.html',
                           title='Alterando Informações da Postagem',
                           form=form, legend='Alterar Informações')


@app.route("/post/<int:post_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)  # criar página de erro.
    db.session.delete(post)
    db.session.commit()
    flash("Postagem deletada com sucesso!", 'success')
    return redirect(url_for('index'))
