from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import InputRequired, Email, EqualTo

class SignUpForm(FlaskForm):
	full_name = StringField('Username', validators = [InputRequired()])
	email = StringField('Email', validators = [InputRequired(), Email()])
	password = PasswordField('Password', validators = [InputRequired()])
	confirm_password = PasswordField('Confirm Password', validators = [InputRequired(), EqualTo('password')])

	submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
	email = StringField('Email', validators = [InputRequired(), Email()])
	password = PasswordField('Password', validators = [InputRequired()])
	
	submit = SubmitField('Login')

class NewPost(FlaskForm):
	title = StringField('Title', validators = [InputRequired()])
	body = TextAreaField('Body')

	submit = SubmitField('Post')