import os
from flask_login import LoginManager
from flask_login import UserMixin
from flask import Flask, render_template,request,redirect,url_for,jsonify,current_app,flash
from werkzeug.security import generate_password_hash , check_password_hash
from flask_bcrypt import Bcrypt
from flask_login import login_user, current_user, logout_user, login_required
from send_messages import send_email
from data import user_data, complain_data,my_complain_data,complains ,add_user ,createBlog , updateInfo,get_username_by_email
import nanoid
import re
import jwt
from datetime import datetime, timedelta
import sqlite3

DATABASE = 'complain.db'


ALLOWED_EXTENXIONS = set(["txt", "pdf", "png", "jpg", "jpeg", "gif"])
PASSWORD_REGEX = "^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$"
app = Flask(__name__)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

app.config['SECRET_KEY'] = '22d27bb95ddd691968c24880f6e12e0b'

#creating an ssl context which will be used to send an automatic email
@login_manager.user_loader
def load_user(user_id):
    users = user_data()
    user = next((user for user in users if user.id == user_id), None)
    return user

@app.route("/")
def hello():
    return render_template ('base.html')

@app.route("/home")
@login_required
def home():
    data = complains()
    return render_template ('home.html' , all_complains = data)
@app.route("/createaccount", methods=['GET', 'POST'])
def createAccount():
    if current_user.is_authenticated:
        return redirect (url_for('home'))
    if request.method == 'GET':
        return render_template('create.html')
    if request.method == 'POST':
        id = nanoid.generate()
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        email = request.form.get('email')
        phone_number = request.form.get('phoneNumber')
        preferred_name = request.form.get('preferredName')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        # Validate form data (you can add more validation as needed)
        if not firstName or not lastName or not email or not phone_number or not preferred_name or not password:
            error_msg = 'All fields are required.'
            return render_template('create.html', error=error_msg)
        #checking password length
        if len(password) < 8:
            return render_template('create.html', show_short_password=True)
        if password != confirm_password:
            return render_template("create.html", show_different_password=True)
        password_regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$'
        if not re.match(password_regex, password):
            return render_template('create.html', show_weak_password=True)
        users = user_data()
        for user in users:
            users = user_data()
        for user in users:
            if user.email == email:  # Access 'email' attribute directly from the User object
                return render_template('create.html', show_email_exist=True)

            if user.preferredName == preferred_name:  # Access 'preferredName' attribute directly from the User object
                return render_template('create.html', show_name_exist=True)
            # displays error message to the user of they exist
        
        # Hash the password before storing it in the database
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        status = add_user(id, firstName, lastName, email, phone_number, preferred_name, hashed_password)
        if status :
            current_user.is_authenticated
            return redirect (url_for('home'))
        else:
            return redirect(url_for('createAccount'))
        
@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect (url_for('home'))
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        users = user_data()
        user = next((user for user in users if user.email == email), None)
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            next_page = request.args.get('next') 
            # goes to the next page if exists after one logs in
            return redirect (next_page) if next_page else redirect(url_for('home'))
        else:
            return render_template('login.html', show_forgot_password=True)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('hello'))

@app.route("/myposts", methods=['GET'])
@login_required
def myposts():
    if request.method == 'GET':
        user_complaints = complain_data(current_user.id)
        return render_template('myposts.html', complaints=user_complaints)
@app.route("/write",methods=['GET','POST'])
@login_required
def writepost():
    if request.method == 'GET':
        return render_template('write.html')
    if request.method == 'POST':
        id = nanoid.generate()
        complaint = request.form.get('complaint')
        title = request.form.get('title')
        user_id = current_user.id
        createBlog(id, user_id,title,complaint)
        return redirect(url_for('myposts'))
@app.route("/myaccount",methods=['GET','POST'])
@login_required
def myaccount():#
    if request.method == 'GET':
        return render_template("profile.html")
    if request.method == 'POST':
        user_id = current_user.id

        conn = sqlite3.connect('complain.db')
        cur = conn.cursor()

        cur.execute("DELETE FROM User WHERE id=?", (user_id,))
        conn.commit()
        conn.close()
        logout_user()  # Log out the user after account deletion
        return redirect(url_for('hello'))
        
@app.route("/save", methods=['POST'])
@login_required
def save():
    user_id = request.form.get('user_id')
    firstName = request.form.get('firstName')
    lastName = request.form.get('lastName')
    email = request.form.get('email')
    phone_number = request.form.get('phoneNumber')
    preferred_name = request.form.get('preferredName')

    updateInfo(firstName, lastName, email, phone_number, preferred_name, user_id)
    return redirect(url_for('myaccount'))

@app.route("/update")
@login_required
def update():
    return render_template ("updateform.html")

@app.route("/forgot",methods=['GET','POST'])
def forgotpassword():
    # TODO check if account exists
    if request.method == 'GET':
        return render_template('forgotpass.html')
    if request.method == 'POST':
        email = request.form.get('email')
        conn = sqlite3.connect('complain.db')
        cur = conn.cursor()
        cur.execute("SELECT id FROM User WHERE email=?", (email,))
        user_id = cur.fetchone()  # Retrieve the user_id associated with the email
        conn.close()

        if user_id:
            send_email(email,app)  # Pass the retrieved user_id and email to send_email function
        # Add logic here to handle the case where the email doesn't exist in the database
        return redirect(url_for('forgotpassword'))


#an app route that is used to reset password
@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_password(token):
    def verify_token(token):
        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            return payload.get('user_id')  # Return user_id if the token is valid, None otherwise
        except jwt.ExpiredSignatureError:
            return 'expired token'
        except jwt.InvalidTokenError:
            return 'invalid token'

    user_id = verify_token(token)

    if user_id is None:
        flash('The confirmation link has expired.', category='danger')
        return redirect(url_for('forgotpassword'))

    if request.method == 'GET':
        return render_template('changepassword.html')

    if request.method == 'POST':
        password = request.form.get('password')
        conn = sqlite3.connect('complain.db')
        cur = conn.cursor()

        try:
            # Hash the new password before storing it in the database
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            cur.execute("UPDATE User SET password=? WHERE id=?", (hashed_password, user_id))
            conn.commit()
            msg = 'User password updated successfully.'
            print(msg)
        except sqlite3.Error as e:
            conn.rollback()
            msg = f'Error: {e}'
            print(msg)
        finally:
            conn.close()
            return redirect(url_for('login'))

@app.route("/fullpost/<id>")
def fullpost(id):
        complaint = my_complain_data(id)  # Assuming you have a function to fetch complaint data by ID
        return render_template('post.html', complain=complaint)
@app.route("/myfullpost/<id>", methods=['GET','POST'])
@login_required
def my_fullpost(id):
    if request.method == 'GET':
        complaint = my_complain_data(id)  # Assuming you have a function to fetch complaint data by ID
        return render_template('mypost.html', complain=complaint)
    if request.method == 'POST':
        post_id = request.form.get('id')

        post_id = id

        conn = sqlite3.connect('complain.db')
        cur = conn.cursor()

        cur.execute("DELETE FROM Complains WHERE id=?", (post_id,))
        conn.commit()
        conn.close()
        return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)