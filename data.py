from flask_login import LoginManager
from itsdangerous import TimedSerializer as reset
from welcome_message import welcome_mail
from flask import Flask,redirect,url_for
from flask_login import UserMixin
import sqlite3
conn = sqlite3.connect('complain.db')
cur= conn.cursor()

login_manager = LoginManager()

class User(UserMixin):
    def __init__(self, id, email, password, preferredName, firstName, lastName, phonenumber,picture):
        self.id = id
        self.email = email
        self.password = password
        self.preferredName = preferredName
        self.firstName = firstName
        self.lastName = lastName
        self.phonenumber = phonenumber
        self.picture = picture if picture else 'user .png'
    
    
    

class Complaint:
    def __init__(self, id, user_id, title,complain):
        self.id = id
        self.user_id = user_id
        self.complain = complain
        self.title = title

cur.execute("""CREATE TABLE IF NOT EXISTS 'User'(
    id TEXT NOT NULL PRIMARY KEY UNIQUE,
    firstName TEXT NOT NULL,
    lastName TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phonenumber INTEGER NOT NULL UNIQUE,
    preferredname TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    picture TEXT             
)""")

cur.execute("""CREATE TABLE IF NOT EXISTS 'Complains'(
    id TEXT NOT NULL PRIMARY KEY UNIQUE,
    user_id TEXT NOT NULL,
    title TEXT NOT NULL,
    complain TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES User(id)    
)""")
def user_data():
    conn = sqlite3.connect('complain.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM User")
    users = cur.fetchall()
    cur.close()
    conn.close()

    
    user_objects = [User(user['id'], user['email'], user['password'] , user['preferredName'], user['firstName'], user['lastName'], user['phonenumber'], user['picture'] ) for user in users]
    return user_objects

def complain_data(user_id):
    conn = sqlite3.connect('complain.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM Complains WHERE user_id=?", (user_id,))
    complains = cur.fetchall()
    cur.close()
    conn.close()

    complain_objects = [Complaint(complain['id'], complain['user_id'], complain['title'],complain['complain']) for complain in complains]
    return complain_objects

def my_complain_data(complain_id):
    conn = sqlite3.connect('complain.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM Complains WHERE id=?", (complain_id,))
    complaint = cur.fetchone()  # Assuming you expect only one complaint for the given ID
    
    if complaint:
        complain_obj = Complaint(complaint['id'], complaint['user_id'], complaint['title'], complaint['complain'])
        return complain_obj
    else:
        return None  # Handle the case where no complaint is found for the given ID

def complains():
    conn = sqlite3.connect('complain.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM Complains")
    all_complains = cur.fetchall()
    cur.close()
    conn.close()
    
    complain_objects = [Complaint(complain['id'], complain['user_id'], complain['title'],complain['complain']) for complain in all_complains]
    return complain_objects

# sends email to the user when logged in
#method that inserts data into the data base
def add_user(id, firstName, lastName, email, phone_number, preferred_name, hashed_password):
    conn = sqlite3.connect('complain.db')
    cur = conn.cursor()
    try:
            cur.execute("INSERT INTO User ('id', 'firstName', 'lastName', 'email', 'phonenumber', 'preferredname', 'password')\
                        VALUES (?, ?, ?, ?, ?, ?, ?)", (id, firstName, lastName, email, phone_number, preferred_name, hashed_password))
            conn.commit()
            msg = 'Account created successfully.'
            welcome_mail(email)
            status = True
             # Redirect to login page with success message

    except Exception as e:
            # Handle the specific exception (e.g., SQLite integrity error) here
            msg = f"Error occurred: {e}"
            


    finally:
            conn.close()
            print(msg)

    return status

#method that add user's blog
def createBlog(id, user_id,title,complaint):
    conn = sqlite3.connect('complain.db')
    cur =conn.cursor()
    cur.execute("INSERT INTO Complains (id, user_id, title ,complain) VALUES (?, ?, ?, ?)", (id, user_id,title,complaint))
    conn.commit()
    conn.close()
    msg = "added successfully"
    return msg

def updateInfo(firstName, lastName, email, phone_number, preferred_name, picture,user_id):
    conn = sqlite3.connect('complain.db')
    cur = conn.cursor()

    try:
        cur.execute("UPDATE User SET firstName=?, lastName=?, email=?, phonenumber=?, preferredname=?,picture=? WHERE id=?",
                    (firstName, lastName, email, phone_number, preferred_name,picture,user_id))
        conn.commit()
        msg = 'User information updated successfully.'
        status = True
    except sqlite3.Error as e:
        conn.rollback()
        msg = f'Error: {e}'
        print (msg)
    finally:
        conn.close()
        return status
    
def get_username_by_email(email):
    conn = sqlite3.connect('complain.db')
    cur = conn.cursor()

    try:
        # Execute the SELECT query to retrieve the username based on the email
        cur.execute("SELECT username FROM User WHERE email=?", (email,))
        username = cur.fetchone()

        if username:
            # If the email exists in the database, cur.fetchone() will return the username
            return username[0]  # Return the first column value (username)
        else:
            # If the email doesn't exist in the database, return None or raise an exception
            return None
    except Exception as e:
        # Handle exceptions here (e.g., database errors)
        print(f"Error occurred: {e}")
        return None
    finally:
        # Make sure to close the connection after performing the operation
        conn.close()


def get_user_id_by_email(email):
    conn = sqlite3.connect('complain.db')
    cur = conn.cursor()

    try:
        # Execute the SELECT query to retrieve the username based on the email
        cur.execute("SELECT id FROM User WHERE email=?", (email,))
        username = cur.fetchone()

        if username:
            # If the email exists in the database, cur.fetchone() will return the username
            return username[0]  # Return the first column value (username)
        else:
            # If the email doesn't exist in the database, return None or raise an exception
            return None
    except Exception as e:
        # Handle exceptions here (e.g., database errors)
        print(f"Error occurred: {e}")
        return None
    finally:
        # Make sure to close the connection after performing the operation
        conn.close()