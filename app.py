from flask import Flask, render_template, abort
from forms import SignUpForm, LoginForm, NewPost
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
	likes = db.relationship('PostLike', backref='post', lazy='dynamic')
 
""" Model for Likes """
class PostLike(db.Model):
    __tablename__ = 'post_like'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

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
	posts = Post.query.all()
	return render_template("home.html", posts = posts)

@app.route("/signup", methods = ["POST", "GET"])
def signup():
	form = SignUpForm()
	if form.validate_on_submit():
		new_user = User(username = form.username.data, email = form.email.data, password = form.password.data)
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
	return redirect(url_for('index'))

@app.route("/post", methods = ["POST", "GET"])
def post():
	form = NewPost()
	if form.validate_on_submit():
		new_post = Post(title = form.title.data, body = form.body.data, posted_by = session['user'])
		db.session.add(new_post)
		try:
			db.session.commit()
		except Exception as e:
			print(e)
			db.session.rollback()
			return render_template("NewPost.html", form = form, message = "Error creating the Post")
		finally:
			db.session.close()
			return redirect(url_for("index"))
	return render_template("NewPost.html", form = form)

@app.route("/edit_post/<int:post_id>", methods = ["POST", "GET"])
def edit_post(post_id):
	form = NewPost()
	post = Post.query.get(post_id)
	if post is None:
		abort(404, description="No Post was found with the given ID")
	if form.validate_on_submit():
		post.title = form.title.data
		post.body = form.body.data
		post.posted_by = session['user']
		try:
			db.session.commit()
		except Exception as e:
			db.session.rollback()
			return render_template("EditPost.html", post = post, form = form, message = "Error editing the Post")
		finally:
			db.session.close()
			return redirect(url_for("index"))

	return render_template("EditPost.html", post = post, form = form)


@app.route("/delete_post/<int:post_id>")
def delete_post(post_id):
	post = Post.query.get(post_id)
	if post is None:
		abort(404, description="No Post was Found with the given ID")
	db.session.delete(post)
	try:
		db.session.commit()
	except Exception as e:
		db.session.rollback()
	return redirect(url_for('index'))

@app.route("/like/<int:post_id>")
def like(post_id):
    liked = PostLike.query.filter(
		PostLike.user_id == session['user'],
		PostLike.post_id == post_id
	).count()
    
    if liked == 0:
        like = PostLike(user_id = session['user'], post_id = post_id)
        db.session.add(like)
    else:
        PostLike.query.filter_by(
			user_id = session['user'],
			post_id = post_id
		).delete()
    
    db.session.commit()
    
    return redirect(url_for('index'))
if __name__=='__main__':
	app.run(debug=True, host="0.0.0.0", port=3000)