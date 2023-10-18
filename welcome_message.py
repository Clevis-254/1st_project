
from flask_mail import Mail
from flask_mail import Message
from flask_login import LoginManager
from email.message import EmailMessage
import ssl
import smtplib

def welcome_mail(email):
        msg = EmailMessage()
        msg['From'] = 'noreply@demo.com'
        msg['To'] = [email]
        body=f'''
           Welcome to complaint. where you can write anything you want. We are exited to welcome 
           you to our family. so whenever you feel like complaining just write whatever you want and 
            we will help you to get your complaint'''
        msg['Subject'] = 'WELCOME TO COMPLAINT'
        msg.set_content(body)
        # the code below is used to send an automatic email by the use of smtp
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login('noreplyokoa@gmail.com', 'gjli nggj rwzs menu')
            smtp.sendmail('norepldemo@gmail.com', email, msg.as_string())
