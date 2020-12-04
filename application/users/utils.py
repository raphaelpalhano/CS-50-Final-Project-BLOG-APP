import os
import secrets
from PIL import Image
from flask import url_for
from flask_mail import Message
from application import mail, app


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


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Requisição de mudança de senha',
                  sender='raphael-angel@hotmail.com', recipients=[user.email])
    msg.body = f"""Para mudar sua senha, acesse o seguinte site:
{url_for('users.reset_token', token=token, _external=True)}

Se você não fez essa requisição para mudar sua senha apenas ignore essa
mensagem e não faça nenhuma alteração.
"""
    mail.send(msg)
