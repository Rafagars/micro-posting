from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, HiddenField
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
	
	submit = SubmitField('Login')

class NewPost(FlaskForm):
	title = StringField('Title', validators = [InputRequired()])
	body = TextAreaField('Body')
	user_id = HiddenField(validators= [InputRequired()])

	submit = SubmitField('Post')