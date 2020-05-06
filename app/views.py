from app import app, db
from app.models import User, Post, PostLike, Comment, CommentLike
from app.forms import SignUpForm, LoginForm, NewPost, EditUser, CommentForm
from flask import Flask, render_template, abort, redirect, url_for, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
	return User.get_by_id(user_id)

@app.route('/')
def index():
	page = request.args.get('page', 1, type=int)
	posts = Post.query.order_by(Post.id.desc()).paginate(page = page, per_page = 5, error_out = True)
	next_url = url_for('index', page=posts.next_num) \
	if posts.has_next else None
	prev_url = url_for('index', page=posts.prev_num) \
    if posts.has_prev else None

	for post in posts.items:
		user = User.get_by_id(post.posted_by)
		post.username = user.username
	return render_template("home.html", posts = posts.items, next_url = next_url, prev_url = prev_url)

@app.route("/login", methods = ["POST", "GET"])
def login():
	if current_user.is_authenticated:
		redirect(url_for('index'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.get_by_email(form.email.data.capitalize())
		#Checks if user exists and then checks user's password
		if user is not None and user.check_password(form.password.data):
			login_user(user, remember = form.remember_me.data)
			next_page = request.args.get('next')
			if not next_page or url_parse(next_page).netloc != '':
				next_page = url_for('index')
			return redirect(next_page)
		else:
			message = "Sorry, wrong email or pasword" 
			return(render_template('login.html', form = form, message = message))
	return render_template('login.html', form = form)

@app.route("/signup", methods = ["POST", "GET"])
def signup():
	if current_user.is_authenticated:
		redirect(url_for('index'))
	form = SignUpForm()
	message = None
	if form.validate_on_submit():
		username = form.username.data.capitalize()
		email = form.email.data.capitalize()
		password = form.password.data

		#Check if other user has this email or username
		user_email = User.get_by_email(email)
		user_name = User.query.filter_by(username = username).first()
		if user_email is not None or user_name is not None:
			if user_email is not None:
				message = f'The email {email} already registered'
			else:
				message = f'Username {username} already taken'
		else:
			#Create user and save it
			user = User(username = username, email = email)
			user.set_password(password)
			user.save()
			#Log in the user
			login_user(user, remember = True)
			next_page = request.args.get('next', None)
			if not next_page or url_parse(next_page).netloc != '':
				next_page = url_for('index')
			return redirect(next_page)
	return render_template('Signup.html', form = form, message = message)


@app.route("/logout")
@login_required
def logout():
	logout_user()
	return redirect(url_for('index'))

@app.route("/new_post", methods = ["POST", "GET"])
@login_required
def new_post():
	form = NewPost()
	if form.validate_on_submit():
		new_post = Post(title = form.title.data, body = form.body.data, posted_by = current_user.id)
		new_post.save()
		return redirect(url_for("index"))
	return render_template("NewPost.html", form = form)

@app.route("/edit_post/<int:post_id>", methods = ["POST", "GET"])
@login_required
def edit_post(post_id):
	post = Post.query.get(post_id)
	form = NewPost(obj=post)
	if post is None:
		abort(404, description="No Post was found with the given ID")
	if form.validate_on_submit():
		post.title = form.title.data
		post.body = form.body.data
		post.posted_by = current_user.id
		try:
			db.session.commit()
		except:
			db.session.rollback()
			return render_template("EditPost.html", post = post, form = form, message = "Error editing the Post")
		finally:
			db.session.close()
			return redirect(url_for("index"))

	return render_template("EditPost.html", post = post, form = form)

@app.route("/post/<string:slug>", methods = ["POST", "GET"])
def show_post(slug):
	post = Post.get_by_slug(slug)
	if post is None:
		abort(404, description="No post was found with the given ID")
	user = User.get_by_id(post.posted_by)
	post.username = user.username
	page = request.args.get('page', 1, type=int)
	comments = Comment.query.order_by(Comment.id.desc()).paginate(page = page, per_page = 5, error_out = True)
	for comment in comments.items:
		user = User.get_by_id(comment.user_id)
		comment.username = user.username
		comment.email = user.email
	next_url = url_for('show_post', slug = post.title_slug, page=comments.next_num) \
	if comments.has_next else None
	prev_url = url_for('show_post', slug = post.title_slug, page=comments.prev_num) \
    if comments.has_prev else None
	form = CommentForm()
	if form.validate_on_submit():
		comment = Comment(body = form.body.data, post_id = post.id, user_id = current_user.id)
		db.session.add(comment)
		try:
			db.session.commit()
			return redirect(post.public_url())
		except:
			db.session.rollback()
			return render_template("ShowPost.html", post = post, form = form, comments = comments.items, next_url = next_url, prev_url = prev_url)
			
	return render_template("ShowPost.html", post = post, form = form, comments = comments.items, next_url = next_url, prev_url = prev_url)


@app.route("/delete_post/<int:post_id>")
@login_required
def delete_post(post_id):
	post = Post.query.get(post_id)
	if post is None:
		abort(404, description="No Post was Found with the given ID")
	comments = Comment.query.filter_by(post_id = post.id).all()
	for comment in comments:
		db.session.delete(comment)
	db.session.delete(post)
	try:
		db.session.commit()
	except:
		db.session.rollback()
	return redirect(url_for('index'))

@app.route("/delete_comment/<int:comment_id>")
def delete_comment(comment_id):
	comment = Comment.query.get(comment_id)
	post = Post.get_by_id(comment.post_id)
	if comment is None:
		abort(404, description="No comment was found with the given ID")
	db.session.delete(comment)
	try:
		db.session.commit()
	except:
		db.session.rollback()
	return redirect(post.public_url())

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

@app.route("/user/<username>")
def show_user(username):
	user = User.query.filter_by(username = username).first()
	page = request.args.get('page', 1, type=int)
	posts = Post.query.filter_by(posted_by = user.id).order_by(Post.id.desc()).paginate(page = page, per_page = 5, error_out = True)
	next_url = url_for('show_user', username = user.username, page=posts.next_num) \
	if posts.has_next else None
	prev_url = url_for('show_user', username = user.username, page=posts.prev_num) \
    if posts.has_prev else None
	return render_template("ShowUser.html", posts = posts.items, user = user, next_url = next_url, prev_url = prev_url)

@app.route("/edit_user/<int:user_id>", methods = ['POST', 'GET'])
@login_required
def edit_user(user_id):
	form = EditUser()
	if form.validate_on_submit():
		user = User.get_by_id(user_id)
		if user.check_password(form.current_password.data):
			user.set_password(form.new_password.data)
			user.save()
			return redirect(url_for('index'))
		else:
			message = "That's not your current password"
			return render_template("EditUser.html", form = form, message = message)
	return render_template("EditUser.html", form = form)

