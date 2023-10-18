from flask import url_for
from flask_mail import Mail
from flask_mail import Message
from flask_login import LoginManager
from email.message import EmailMessage
from datetime import datetime, timedelta
from data import get_username_by_email,get_user_id_by_email
import re
import jwt
import ssl
import smtplib

def generate_token(user_id, username,app):
        expiration_time = datetime.utcnow() + timedelta(minutes=30)
        payload = {'user_id': user_id, 'username': username, 'exp': expiration_time}
        token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
        return token

    # sends reset token
def send_email(email,app):
    username = get_username_by_email(email)
    user_id = get_user_id_by_email(email)
    token_data = generate_token(user_id, username,app)
    token = token_data
    mail = EmailMessage()
    mail['From'] = 'noreply@demo.com'
    mail['To'] = [email]
    body=f'''
            Hello comrade ... to reset your password visit the following link
            {url_for('reset_password', token=token, _external=True)}
            If you did not make this request then simply ignore and delete it.'''
    mail['Subject'] = 'Password Reset Request'
    mail.set_content(body)
        # the code below is used to send an automatic email by the use of smtp
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login('noreplyokoa@gmail.com', 'gjli nggj rwzs menu')
            smtp.sendmail('norepldemo@gmail.com', email, mail.as_string())