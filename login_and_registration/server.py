from flask import Flask, request, redirect, render_template, session, flash
import re 
from mysqlconnection import MySQLConnector
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
NAME_REGEX = re.compile(r'^[a-zA-Z]')
app = Flask(__name__)
app.secret_key = "FINE!"
mysql = MySQLConnector(app,'login_registrationdb')
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')
@app.route('/registration', methods=['POST'])
def login():
    if len(request.form['fn']) < 2:
        flash("First Name must be at least two characters")
        return redirect('/')
    elif not NAME_REGEX.match(request.form['fn']):
        flash("First and Last Name can only contain letters!")
        return redirect('/')
    if len(request.form['ln']) < 2:
        flash("Last Name must be at least two characters")
        return redirect('/')
    elif not NAME_REGEX.match(request.form['ln']):
        flash("First and Last Name can only contain letters!")
        return redirect('/')
    if not EMAIL_REGEX.match(request.form['email']):
        flash("Invalid Email Address!")
        return redirect('/')
    if not len(request.form['pw']) > 7:
        flash("Password must be at least 8 characters!")
        return redirect('/')
    if request.form['pw'] != request.form['cpw']:
        flash("Password and Password Confirmation do not match!")
        return redirect('/')
    # else if email doesn't match regular expression display an "invalid email address" message
    else:
        query = "INSERT INTO users (first_name, last_name, email, password) VALUES (:fn, :ln, :email, :pw)"
        data = {
            'fn': request.form['fn'],
            'ln': request.form['ln'],
            'email': request.form['email'],
            'pw': request.form['pw']
        }
        mysql.query_db(query, data)
        name = request.form['fn'] + " " + request.form['ln']
        return render_template('success.html', name=name)
@app.route('/success')
def success(): 
    return render_template('success.html')
app.run(debug=True)
