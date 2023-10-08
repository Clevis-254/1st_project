from flask_login import LoginManager
from itsdangerous import TimedSerializer as reset
from flask_login import UserMixin

import sqlite3
conn = sqlite3.connect('complain.db')
cur= conn.cursor()

login_manager = LoginManager()

class User(UserMixin):
    def __init__(self, id, email, password, preferredName, firstName, lastName, phonenumber):
        self.id = id
        self.email = email
        self.password = password
        self.preferredName = preferredName
        self.firstName = firstName
        self.lastName = lastName
        self.phonenumber = phonenumber
    
    
    

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
    password TEXT NOT NULL    
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

    
    user_objects = [User(user['id'], user['email'], user['password'] , user['preferredName'], user['firstName'], user['lastName'], user['phonenumber']) for user in users]
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