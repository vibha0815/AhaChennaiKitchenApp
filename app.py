from functools import wraps

from flask import Flask, render_template, flash, request, redirect, url_for, session, logging
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from wtforms.validators import  DataRequired, Length
from passlib.hash import sha256_crypt


app = Flask(__name__)

#initialize mysql
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Ilamma90!'
app.config['MYSQL_DB'] = 'ahaChennaiKitchen'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql =  MySQL(app)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/Contact')
def Contact():
    return render_template('Contact.html')


class RegisterForm(Form):
    name = StringField('Name', validators= [DataRequired(), Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message ='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')
    mobile_number = StringField('Mobile_no', [validators.length(min=10, max=11)])


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))
        mobile_number = form.mobile_number.data
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users(name, email, username, password, mobile_number) VALUES(%s, %s, %s, %s, %s)", (name, email, username, password, mobile_number))

        # lets commit to DB
        mysql.connection.commit()

        #close
        cur.close()

        flash('You have registered into the AhaChennai kitchen','success')
        redirect(url_for('index'))

    return render_template('register.html', form=form)

#User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # get username details
        username = request.form['username']
        password_candidate = request.form['password']
        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])
       # get stored hash
        if result > 0:
            data = cur.fetchone()
            password = data['password']
     # compare the two passwords
            if sha256_crypt.verify(password_candidate, password):
                #passed
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard') )
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)

            #close connection
            cur.close()
    else:
        error = 'Username not found'
        return render_template('login.html', error=error)

    return render_template('login.html')

#check if user is logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

#Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.secret_key='vibha'
    app.run(debug=True)