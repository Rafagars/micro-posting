from flask import Flask, render_template, abort
from forms import SignUpForm, LoginForm, NewPost
from flask import session, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = '8b9373cb34f0296e4330d2216356b8981fcc2f27021812aa'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///micro-post.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = "login"


"""Model for User"""
class User(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key = True)
	username = db.Column(db.String, unique = True)
	email = db.Column(db.String, unique = True)
	password = db.Column(db.String)
	post = db.relationship('Post', backref = 'user')
	liked = db.relationship('PostLike',
                         foreign_keys='PostLike.user_id',
                         backref='user', lazy='dynamic')
	
	def like_post(self, post):
		if not self.has_liked_post(post):
			like = PostLike(user_id = self.id, post_id = post.id)
			db.session.add(like)
			
	def unlike_post(self, post):
		if self.has_liked_post(post):
			PostLike.query.filter_by(
				user_id = self.id,
				post_id = post.id
			).delete()
   
	def has_liked_post(self, post):
		return PostLike.query.filter(
			PostLike.user_id == self.id,
			PostLike.post_id == post.id
		).count() > 0
 
	def set_password(self, password):
		self.password = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password, password)

	def save(self):
		if not self.id:
			db.session.add(self)
		db.session.commit()

	@staticmethod
	def get_by_id(id):
		return User.query.get(id)

	@staticmethod
	def get_by_email(email):
		return User.query.filter_by(email = email).first()

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

@login_manager.user_loader
def load_user(user_id):
	return User.get_by_id(user_id)

@app.route('/')
def index():
	posts = Post.query.order_by(Post.id.desc()).all()
	return render_template("home.html", posts = posts)

@app.route("/login", methods = ["POST", "GET"])
def login():
	if current_user.is_authenticated:
		redirect(url_for('index'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.get_by_email(form.email.data)
		if user is not None and user.check_password(form.password.data):
			login_user(user, remember = form.remember_me.data)
			next_page = request.args.get('next')
			if not next_page or url_parse(next_page).netloc != '':
				next_page = url_for('index')
			return redirect(next_page)
	return render_template('login.html', form = form)

@app.route("/signup", methods = ["POST", "GET"])
def signup():
	if current_user.is_authenticated:
		redirect(url_for('index'))
	form = SignUpForm()
	message = None
	if form.validate_on_submit():
		username = form.username.data
		email = form.email.data
		password = form.password.data

		#Comprobamos que no hay un usuario con ese email
		user = User.get_by_email(email)
		if user is not None:
			message = f'El email {email} ya esta en uso'
		else:
			#Creamos el usuario y lo guardamos
			user = User(username = username, email = email)
			user.set_password(password)
			user.save()
			#Dejamos al usuario logueado
			login_user(user, remember = True)
			next_page = request.args.get('next', None)
			if not next_page or url_parse(next_page).netloc != '':
				next_page = url_for('index')
			return redirect(next_page)
	return render_template('Signup.html', form = form, message = message)


@app.route("/logout")
def logout():
	logout_user()
	return redirect(url_for('index'))

@app.route("/post", methods = ["POST", "GET"])
@login_required
def post():
	form = NewPost()
	if form.validate_on_submit():
		new_post = Post(title = form.title.data, body = form.body.data, posted_by = current_user.id)
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
@login_required
def edit_post(post_id):
	form = NewPost()
	post = Post.query.get(post_id)
	if post is None:
		abort(404, description="No Post was found with the given ID")
	if form.validate_on_submit():
		post.title = form.title.data
		post.body = form.body.data
		post.posted_by = current_user.id
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
@login_required
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

@app.route("/like/<int:post_id>/<action>")
@login_required
def like_action(post_id, action):
    post = Post.query.filter_by(id = post_id).first_or_404()
    if action == 'like':
        current_user.like_post(post)
        db.session.commit()
    if action == 'unlike':
        current_user.unlike_post(post)
        db.session.commit()
    return redirect(request.referrer)

@app.route("/user")
@login_required
def show_user():
	posts = Post.query.filter_by(posted_by = current_user.id )
	return render_template("ShowUser.html", posts = posts)

if __name__=='__main__':
	app.run(debug=True, host="0.0.0.0", port=3000)