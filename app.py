import os
import secrets
from flask import Flask, render_template, flash, request, redirect, url_for, session
from database import initialize_mysql_database, populate_movies, get_movies, add_user_to_neo4j, create_connection, start_neo4j, clear_neo4j, user_exists, recommend_movies
from secret import hash_password
from queries import insert_user, check_user
from utils import get_external_ip
from datetime import timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=365)

cursor, conn = initialize_mysql_database()

# Routes
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/home")
def home():
    if 'email' in session:
        movies = get_movies()
        recommendations = recommend_movies(session['email'])
        return render_template("home.html", movies=get_movies(), recommendations=recommendations)
    else:
        flash('You must signup or login.')
        return redirect(url_for('index'))


@app.route("/signup")
def signup():
    if 'email' in session:
        return render_template("home.html", data=get_movies())
    
    return render_template("signup.html")

@app.route("/signup", methods = ['POST'])
def signup_verify():    
    email = request.form.get('InputSignUpEmail')
    password = hash_password(request.form.get('InputSignUpPassword'))
    if not user_exists(cursor, email):
        insert_user(cursor, conn, email, password)
        add_user_to_neo4j(email)
    
    session['email'] = email
    return redirect(url_for('home'))

@app.route("/login")
def login():
    if 'email' in session:
        return redirect("home.html")
    
    return render_template("login.html")

@app.route("/login", methods = ['POST'])
def login_verify():
    email = request.form.get('InputLoginEmail')
    password = hash_password(request.form.get('InputPassword'))

    # Search for the email and password in the database
    if check_user(cursor, email, password):
        session['email'] = email
        return redirect(url_for('home'))
    else:
        flash('Wrong credentials')
        return render_template("login.html")
    
@app.route("/logout")
def logout():
    session.pop('email', None)
    return redirect(url_for('index'))

@app.route('/select_movie/<movie_id>/<movie_file>')
def select_movie(movie_id, movie_file):
    # Handle the movie selection
    if 'email' in session :
        # Call a function to create a connection between the user and the selected movie
        create_connection(session['email'], movie_id)
        return redirect(f'http://34.105.214.25:81?video={movie_file}')
    else:
        return redirect(url_for('index'))

if __name__ == "__main__":
    populate_movies()
    # clear_neo4j()
    start_neo4j()
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 80)))
