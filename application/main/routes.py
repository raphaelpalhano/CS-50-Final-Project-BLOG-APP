from flask import render_template, request, Blueprint, flash
from application.models import Post

# Veja que cada diretório sua configuração local posts=posts; users=users;
# main=main

main = Blueprint('main', __name__)


@main.route('/', methods=['GET', 'POST'], defaults={"page": 1})
@main.route('/<int:page>', methods=['GET', 'POST'])
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

    return render_template('index.html', posts=posts, title='Painel Principal')


@main.route('/about')
def about():
    return render_template('about.html', title='Sobre')

