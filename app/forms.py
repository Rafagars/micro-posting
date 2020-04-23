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

class NewPost(FlaskForm):
	title = TextAreaField('Title', validators = [InputRequired()], render_kw = {"rows": 1, "cols": 60})
	body = TextAreaField('Body', render_kw={"rows": 10, "cols": 60})

	submit = SubmitField('Post')

class EditUser(FlaskForm):
	current_password = PasswordField('Current Password', validators = [InputRequired()])
	new_password = PasswordField('New Password', validators = [InputRequired()])
	confirm_password = PasswordField('Confirm New Password', validators = [InputRequired()])

	submit = SubmitField('Change')

class CommentForm(FlaskForm):
	body = TextAreaField('Body', render_kw={"rows": 5, "cols": 60})

	submit = SubmitField('Comment')