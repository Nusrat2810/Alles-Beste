from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
#from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, template_folder="views")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'thisisakey'
db = SQLAlchemy(app)


questions = (('Tisch'),('Laptop'),('Wohnung'),('Handy'))
options = (('der'),('die'),('das'),('die - PL'))
correct_answer = (('der'),('der'),('die'),('das'))

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True )
    name = db.Column(db.String(100), nullable = False )
    email = db.Column(db.String(100), unique = True )
    password = db.Column(db.String(15))

    def __init__(self,name,email,password):
        self.name = name
        self.email = email
        self.password = password

    def check_password(self,stored_password,password):
        self.password = password
        self.stored_password = stored_password

        check = check_password_hash(self.stored_password, self.password)

        return check

    
with app.app_context():
    db.create_all()


@app.route("/")
def home():
    if 'name' in session:
        user = User.query.filter_by(email=session['email']).first()
        return render_template("index.html", user=user)
    else:
        return render_template("login.html", error="login first")

@app.route("/login", methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(user.password, password ):
            session['name'] = user.name
            session['email'] = user.email
            session['password'] = user.password

            return redirect('/')
        else:
            return render_template("login.html", error="Invalid User")


    else:
        return render_template("login.html")

@app.route("/register", methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        not_hashed_password = request.form['password']
        password = generate_password_hash(not_hashed_password)


        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        return redirect('/login')
    
    else:
        return render_template("register.html")
    

@app.route("/profile")
def profile():
    if session['name']:
        user = User.query.filter_by(email=session['email']).first()
        return render_template("profile.html", user=user)
    else:
        return render_template("login.html", error="login first")
    



@app.route("/logout")
def logout():
    session.pop('email')
    return redirect('/login')

@app.route("/vocabulary")
def vocabulary():
    noun = {
        'die Wohnung' : 'Wohnungen','das Handy':'Handys', 'die Sache':'Sachen'
    }
    return render_template("vocabulary.html", noun=noun)


@app.route("/grammer")
def grammer():
    return render_template("grammer.html")

@app.route("/quiz",  methods = ['GET', 'POST'])
def quiz():
    score = 0
    if request.method == 'POST':
        selected_options = request.form.getlist('options')
        for i in range(len(selected_options)):
            if selected_options[i] == correct_answer[i]:
                score += 1

        return render_template('test.html', test = score)

    else:
     return render_template("quiz.html", content = [questions,options])



if(__name__ == '__main__'):
    app.run(debug=True)
