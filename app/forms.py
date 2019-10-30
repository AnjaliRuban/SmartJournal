from wtforms import Form, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email

class LoginForm(Form):
    email = StringField("Email")
    password = PasswordField("Password") 
    submit = SubmitField("Login")

class SignUpForm(Form):
    email = StringField("Email")
    password = PasswordField("Password")
    name = StringField("Name")
    submit = SubmitField("Sign Up")

