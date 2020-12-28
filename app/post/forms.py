from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, BooleanField
from wtforms.validators import InputRequired, Email, EqualTo

class NewPost(FlaskForm):
	title = TextAreaField('Title', validators = [InputRequired()], render_kw = {"rows": 1, "cols": 60})
	body = TextAreaField('Body', render_kw={"rows": 10, "cols": 60})

	submit = SubmitField('Post')


class CommentForm(FlaskForm):
	body = TextAreaField('Body', validators = [InputRequired()], render_kw={"rows": 5, "cols": 60})

	submit = SubmitField('Comment')