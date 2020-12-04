from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from application import db, app
from application.models import Post
from application.posts.forms import PostForm

# Veja que cada diretório sua configuração local posts=posts; users=users

posts = Blueprint('posts', __name__)


@posts.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data,
                    author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Conteúdo publicado com sucesso!', 'success')
        return redirect(url_for('main.index'))
    return render_template('posting.html', title='Novas Postagens',
                           form=form, legend='Nova Postagem')

# rota para verificar o acesso do usuário ao post específico


@posts.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


# rota para modificar o post
@posts.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
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
        return redirect(url_for('posts.post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('posting.html',
                           title='Alterando Informações da Postagem',
                           form=form, legend='Alterar Informações')

# Rota para excluir o post


@posts.route("/post/<int:post_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)  # criar página de erro.
    db.session.delete(post)
    db.session.commit()
    flash("Postagem deletada com sucesso!", 'success')
    return redirect(url_for('main.index'))
