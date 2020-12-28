from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, BooleanField
from wtforms.validators import InputRequired, Email, EqualTo

class SignUpForm(FlaskForm):
	username = StringField('Username', validators = [InputRequired()])
	email = StringField('Email', validators = [InputRequired(), Email()])
	password = PasswordField('Password', validators = [InputRequired()])
	confirm_password = PasswordField('Confirm Password', validators = [InputRequired(), EqualTo('password')])

	submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
	email = StringField('Email', validators = [InputRequired(), Email()])
	password = PasswordField('Password', validators = [InputRequired()])
	remember_me = BooleanField('Remember me')

	submit = SubmitField('Login')