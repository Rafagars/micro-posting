from flask import Flask, render_template, abort
from forms import SignUpForm, LoginForm
from flask import session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = '8b9373cb34f0296e4330d2216356b8981fcc2f27021812aa'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///micro-post.db'
db = SQLAlchemy(app)

"""Model for User"""
class User(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	username = db.Column(db.String, unique = True)
	email = db.Column(db.String, unique = True)
	password = db.Column(db.String)
	post = db.relationship('Post', backref = 'user')

"""Model for Post"""
class Post(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	title = db.Column(db.String)
	body = db.Column(db.Text)
	posted_by = db.Column(db.Integer, db.ForeignKey('user.id'))

db.create_all()

# Commit changes in the session
try:
    db.session.commit()
except Exception as e: 
    db.session.rollback()
finally:
    db.session.close()

@app.route('/')
def index():
	return render_template("home.html")

@app.route("/signup", methods = ["POST", "GET"])
def signup():
	form = SignUpForm()
	if form.validate_on_submit():
		new_user = User(full_name = form.full_name.data, email = form.email.data, password = form.password.data)
		db.session.add(new_user)
		try:
			db.session.commit()
		except Exception as e:
			print (e)
			db.session.rollback()
			return render_template("Signup.html", form = form, message = "This Email already exists in the system! Please Login instead.")
		finally:
			db.session.close()
		return render_template("home.html", message = "Successfully signed up")
	return render_template("Signup.html", form = form )

@app.route("/login", methods = ["POST", "GET"])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email = form.email.data, password = form.password.data).first()
		if user is None:
			return render_template("login.html", form = form, message = "Wrong Credentials. Please Try Again.")
		else:
			session['user'] = user.id
			return render_template("home.html", message = "Successfully Logged in")
	return render_template("login.html", form = form)

@app.route("/logout")
def logout():
	if 'user' in session:
		session.pop('user')
	return redirect(url_for('index', _scheme='https', _external=True))

if __name__=='__main__':
	app.run(debug=True)