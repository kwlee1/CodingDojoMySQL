from flask import Flask, request, redirect, render_template, session, flash
import re 
from mysqlconnection import MySQLConnector
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
app = Flask(__name__)
app.secret_key = "FINE!"
mysql = MySQLConnector(app,'email_validationdb')
@app.route('/', methods=['GET'])
def index():
    query = "SELECT * FROM emails"
    emails = mysql.query_db(query)
    return render_template('index.html', emails=emails)
@app.route('/emails', methods=['POST'])
def create():
    if not EMAIL_REGEX.match(request.form['email']):
        flash("Email is not valid!")
        return redirect('/')
    else:
        new_email = request.form['email']
        query = "INSERT INTO emails (email, date) VALUES (:email, NOW())"
        data = {
            'email': new_email
            }
        mysql.query_db(query, data)
        new_query = "SELECT * FROM emails"
        emails = mysql.query_db(new_query)
        return render_template('success.html', new_email=new_email, emails=emails)
@app.route('/success')
def success(): 
    query = "SELECT * FROM emails"
    emails = mysql.query_db(query)
    return render_template('success.html', emails=emails)
app.run(debug=True)
