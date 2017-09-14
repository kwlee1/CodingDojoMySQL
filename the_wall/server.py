from flask import Flask, request, redirect, render_template, session, flash
import re 
import md5
from mysqlconnection import MySQLConnector
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
NAME_REGEX = re.compile(r'^[a-zA-Z]')
app = Flask(__name__)
app.secret_key = "WALL!"
mysql = MySQLConnector(app,'walldb')
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')
@app.route('/registration', methods=['POST'])
def register():
    if len(request.form['fn']) < 2:
        flash("First Name must be at least two characters",'reg')
        return redirect('/')
    elif not NAME_REGEX.match(request.form['fn']):
        flash("First and Last Name can only contain letters!",'reg')
        return redirect('/')
    if len(request.form['ln']) < 2:
        flash("Last Name must be at least two characters",'reg')
        return redirect('/')
    elif not NAME_REGEX.match(request.form['ln']):
        flash("First and Last Name can only contain letters!",'reg')
        return redirect('/')
    if not EMAIL_REGEX.match(request.form['email']):
        flash("Invalid Email Address!",'reg')
        return redirect('/')
    if not len(request.form['pw']) > 7:
        flash("Password must be at least 8 characters!",'reg')
        return redirect('/')
    if request.form['pw'] != request.form['cpw']:
        flash("Password and Password Confirmation do not match!",'reg')
        return redirect('/')
    else:
        query = "INSERT INTO users (first_name, last_name, email, password) VALUES (:fn, :ln, :email, :pw)"
        data = {
            'fn': request.form['fn'],
            'ln': request.form['ln'],
            'email': request.form['email'],
            'pw': md5.new(request.form['pw']).hexdigest()
        }
        mysql.query_db(query, data)
        name = request.form['fn'] + " " + request.form['ln']
        return render_template('success.html', name=name)
@app.route('/login', methods=['POST'])
def login(): 
    emailLog = request.form['logemail']
    passLog = request.form['logpw']
    query = "SELECT * FROM users WHERE email = :emailLog" 
    data = {'emailLog':emailLog}
    loginData = mysql.query_db(query, data)
    if loginData == []: 
        flash("Email not registered!",'login')
        return redirect('/')
    elif md5.new(passLog).hexdigest() != loginData[0]['password']:
        flash("Password incorrect!",'login')
        return redirect('/')
    else:
        session['fn'] = loginData[0]['first_name']
        session['ln'] = loginData[0]['last_name']
        session['id'] = loginData[0]['id']
        query = "UPDATE users SET updated_at = NOW()"
        mysql.query_db(query)
        return redirect('/wall')
@app.route('/wall', methods=['GET'])
def wall():
    query = "SELECT messages.id AS message_id, user_id, message, first_name, last_name, messages.updated_at AS updated_at FROM messages JOIN users ON users.id = messages.user_id ORDER BY messages.updated_at DESC"
    messages = mysql.query_db(query)
    cquery = "SELECT comments.id AS comment_id, message_id, user_id, comment, first_name, last_name, comments.updated_at AS updated_at FROM comments JOIN users ON users.id = comments.user_id ORDER BY comments.updated_at ASC"
    comments = mysql.query_db(cquery)
    user = session['fn'] + " " + session['ln']
    userid = session['id']
    return render_template('wall.html', user = user, userid = userid, messages = messages, comments=comments)
@app.route('/postmess', methods=['POST'])
def postmess():
    query = "INSERT INTO messages (user_id, message, created_at, updated_at) VALUES (:userid, :message, NOW(), NOW())"
    data = {
        'userid': session['id'],
        'message': request.form['themessage']
    }
    mysql.query_db(query, data)
    return redirect('/wall')
@app.route('/postcomm', methods=['POST'])
def postcomm():
    query = "INSERT INTO comments(message_id, user_id, comment, created_at, updated_at) VALUES (:messageid, :userid, :comment, NOW(), NOW())"
    data = {
        'messageid': request.form['messageID'],
        'userid': session['id'],
        'comment': request.form['thecomm']
    }
    mysql.query_db(query, data)
    return redirect('/wall')
@app.route('/logout')
def logout():
    session.clear()
    print session
    return redirect('/')
app.run(debug=True)