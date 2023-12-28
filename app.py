import os
import secrets
import hashlib

from flask import Flask, render_template, flash, request, redirect, url_for, session
from pymongo import MongoClient
import mysql.connector

client = MongoClient('mongodb://172.17.0.3:27017/')

host = '172.17.0.4'
port = '3306'
user = 'root'
password = 'pass'
database = 'users'

# Establish a connection to the MySQL server
conn = mysql.connector.connect(host=host, port=port, user=user, password=password, database=database)

# Create a cursor object
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        email VARCHAR(255),
        password VARCHAR(255),
        admin BOOLEAN DEFAULT FALSE
    )
''')

conn.commit()

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)

def hash_password(password):
    password_bytes = password.encode('utf-8')
    sha256_hash = hashlib.sha256()
    sha256_hash.update(password_bytes)
    hashed_password = sha256_hash.hexdigest()

    return hashed_password

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/home")
def home():
    if 'email' in session:
        db = client["movies"]
        movies = db.movies.find()
        return render_template("home.html", data=movies)
    else:
        flash('You must signup or login.')
        return redirect(url_for('index'))


@app.route("/signup")
def signup():
    if 'email' in session:
        db = client["movies"]
        movies = db.movies.find()
        return render_template("home.html", data=movies)
    
    return render_template("signup.html")

@app.route("/signup", methods = ['POST'])
def signup_verify():    
    try:
        email = request.form.get('InputSignUpEmail')
        password = hash_password(request.form.get('InputSignUpPassword'))

        cursor.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (email, password))
        conn.commit()

    except mysql.connector.Error as err:
        print("Error: {}".format(err))
        return render_template("signup.html")
    
    session['email'] = email
    return redirect(url_for('home'))

@app.route("/login")
def login():
    if 'email' in session:
        db = client["movies"]
        movies = db.movies.find()
        return render_template("home.html", data=movies)
    
    return render_template("login.html")

@app.route("/login", methods = ['POST'])
def login_verify():
    email = request.form.get('InputLoginEmail')
    password = hash_password(request.form.get('InputPassword'))

    # Search for the email and password in the database
    cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
    result = cursor.fetchone()

    if result:
        session['email'] = email
        return redirect(url_for('home'))
    else:
        flash('Wrong credentials')
        return render_template("login.html")
    
@app.route("/logout")
def logout():
    session.pop('email', None)
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 80)))
