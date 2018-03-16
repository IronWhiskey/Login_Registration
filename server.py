from flask import Flask, render_template, request, redirect, flash, session
from mysqlconnection import MySQLConnector
import md5
import re
import datetime

app = Flask(__name__)
# our index route will handle rendering our form
app.secret_key='keepItSecret'
mysql = MySQLConnector(app, 'registration')

@app.route('/')
def index():
    # if 'user_id' not in session: 
    #     session['user'] = ''
    return render_template("index.html")


@app.route('/validate', methods=['POST'])
def validate():

    notValid = False
    # get first name and last name from form
    firstName = request.form['firstName']
    lastName = request.form['lastName']
     # get email from form
    email = request.form['email']
      # get 1st password entry
    p1 = request.form['password']
    # get 2nd passworkd entry
    p2 = request.form['confirmPass']
     # get date of birth
    # dob = request.form['dob']
    # print dob

    # validate first name and last name fields are not empty
    if len(firstName) < 1 or len(lastName) < 1:
        flash('first name or last name can not be empty!')
        notValid = True
    
    # validate there are no numbers in name
    if hasNum(firstName) or hasNum(lastName):
        flash('first name or last name must not contain numbers!')
        notValid = True
        
    # validate that email is not empty
    if len(email) < 1:
        flash('email must not be empty!')
        notValid = True
        
    # validate email is valid
    if not matchEmail(email):
        flash('email is not valid!')
        notValid = True
        
    # validate password fields are not empty
    if len(p1) < 1 or len(p2) < 1:
        flash('password fields can not be empty')
        notValid = True

    # validate password fields are not empty
    if len(p1) < 9 or len(p2) < 9:
        flash('passwords must be greater than 8 characters')
        notValid = True

    # validate password entries are the same
    if p1 != p2:
        flash('password entries do not match!')
        notValid = True

    # validate password has at least one uppercase and numeric value
    if hasNum(p1) == False or hasUpper(p1) == False:
        flash('password must have at least one uppercase character and one numeric character!')
        notValid = True 

    # validate date of birth is not empty
    # if dob < 1:
        # flash('dob must not be empty')
        # notValid = True
    
    # validate date of birth is from past
    # d = datetime.datetime.now()
    # today = str(d.year) + '-' + str(d.month) + '-' + str(d.day)
    # print today
    # if dob > today:
    #     flash('date of birth is not valid!')
    #     notValid = True

    if notValid:
        return redirect('/')
    else:
        # if data is valid then insert data into database
        hashpass = md5.new(p1).hexdigest()    # get hash of password            
        query = "INSERT INTO users (firstName, lastName,  email, password, created_at, updated_at) VALUES(:user_first_name, :user_last_name, :user_email, :user_pass, NOW(), NOW())"
        data = {
            'user_first_name': firstName,
            'user_last_name': lastName,
            'user_email': email,
            'user_pass': hashpass
        }
        val = mysql.query_db(query, data)

        query ="select * from users where email='{}' and password='{}'".format(email,  hashpass)    
        session['user'] = mysql.query_db(query)
        return redirect('/success')

@app.route('/login', methods=['POST'])
def login():
    user_email = request.form['email']
    user_pass = request.form['pass']
    hashed_pass = md5.new(user_pass).hexdigest()    # get hash of password
    query ="select * from users where email='{}' and password='{}'".format(user_email,  hashed_pass)
    result = mysql.query_db(query)
   
    if ( len(result) > 0 ):  # if  the result is not empty save the users data in a session cookie
        session['user'] = result[0] # setting the session['user] cookie with all user data
        return redirect('/success')
    else:
        message = 'Incorrect email/password combination'
        flash (message)
        return redirect('/')

@app.route('/success')
def user():
    return render_template('confirmation.html', user=session['user'])

def hasNum(someStr):
    return any(char.isdigit() for char in someStr)

def matchEmail(e):
    return bool(re.search(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$', e))

def hasUpper(p):
    return ( any(x.isupper() for x in p) )

app.run(debug=True)
