from flask import Flask, flash, redirect, render_template, request, session, abort, url_for
import pyrebase
from config import FIREBASE_CONFIG, SECRET_KEY
from forms import LoginForm, SignUpForm
from wtforms import Form, StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email


app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY

firebase = pyrebase.initialize_app(FIREBASE_CONFIG)
auth = firebase.auth()
db = firebase.database()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login/', methods=['GET', 'POST'])
def login():
    loginform = LoginForm()
    if request.method == 'POST' and loginform.validate():
        data = {
            u"email": request.form['email'],
            u"password": request.form['password']
        }
        try:
            user = auth.sign_in_with_email_and_password(data["email"], data["password"])
        except:
            return render_template('login.html', form = loginform, wrong = "Either your email or password were incorrect.")
        email = request.form['email'].replace('@', '').replace('.', '')
        session["email"] = email
        db_data = db.child(session.get("email", None)).get().val()
        session["name"] = db_data["name"]
        return redirect(url_for("patient_dashboard"))
    return render_template('login.html', form = loginform, wrong = "")

@app.route('/signup/', methods=['GET', 'POST'])
def signup():
    signupform = SignUpForm()
    if request.method == 'POST' and signupform.validate():
        data = {
            u"name": request.form['name'],
            u"email": request.form['email'],
            u"password": request.form['password']
        }
        try:
            user = auth.create_user_with_email_and_password(data["email"], data["password"])
        except:
            return render_template('signup.html', form = signupform, wrong = "Either your email or password were incorrect.")
        db_data = {
            u"name": request.form['name'],
            u"email": request.form['email'],
        }
        email = request.form['email'].replace('@', '').replace('.', '')
        db.child(email).set(db_data)
        key = db.child(email).child("posts").push({
            u"title": u"Example Post",
            u"date": u"10/30/2019",
            u"content": u"You can write out your thoughts and feelings here!",
        })        
        db.child(email).child("posts").child(key["name"]).child("comments").push({
            u"name":u"Name [Therapist]",
            u"title": u"Example Comment",
            u"content": u"Your therapist can comment here!"
        })
        session["email"] = email
        session["name"] = data["name"]
        return redirect(url_for("patient_dashboard"))
        

    return render_template('signup.html', form = signupform, wrong = "")

@app.route('/dash/') 
def patient_dashboard():
    if (not session.get("email", None)):
        return redirect(url_for('index'))
    details = getPosts(session.get("email", None))
    return render_template('patientdashboard.html', name = session.get("name", None),
                           length   = details[0], 
                           titles   = details[1], 
                           dates    = details[2], 
                           content  = details[3])

@app.route('/new/')
def new_post():
    if (not session.get("email", None)):
        return redirect(url_for('index'))

def getPosts(email):
    data = db.child(email).child("posts").get().val()
    titles = []
    dates = []
    content = []
    for k in data:
        try:
            t = data[k]['title']
            d = data[k]['date']
            c = data[k]['content']
            titles.append(t)
            dates.append(d)
            content.append(c)
        except:
            pass
    return [len(titles), titles[::-1], dates[::-1], content[::-1]]

if __name__ == "__main__":
    app.run()