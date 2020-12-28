from flask import flash, render_template, abort, redirect, url_for, request, jsonify
from app import *
from . import post
from .models import Post, Comment
from app.user.models import User
from .forms import  NewPost, CommentForm


@post.route('/post')
def index():
	page = request.args.get('page', 1, type=int)
	posts = Post.query.order_by(Post.id.desc()).paginate(page = page, per_page = 5, error_out = True)
	# Url variables for the pagination
	next_url = url_for('post.index', page=posts.next_num) \
	if posts.has_next else None
	prev_url = url_for('post.index', page=posts.prev_num) \
    if posts.has_prev else None

	for post in posts.items:
		user = User.get_by_id(post.posted_by)
		post.username = user.username
	return render_template("post/index.html", posts = posts.items, next_url = next_url, prev_url = prev_url)

@post.route("/post/new", methods = ["POST", "GET"])
@login_required
def new():
	form = NewPost()
	if form.validate_on_submit():
		new_post = Post(title = form.title.data, body = form.body.data, posted_by = current_user.id)
		new_post.save()
		flash('Post created')
		return redirect(url_for("post.index"))
	return render_template("post/new.html", form = form)

@post.route("/post/edit/<int:post_id>", methods = ["POST", "GET"])
@login_required
def edit(post_id):
	post = Post.query.get(post_id)
	if current_user.id == post.posted_by:
		form = NewPost(obj=post) #obj=post so that way the content of the post appears in the form
		if post is None:
			#In case that the user try to edit a post that doesn't exist
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
				flash('Post edited')
				return redirect(url_for("post.index"))
	else:
		flash("You aren't the post user")
		return redirect(url_for("post.index"))

	return render_template("post/edit.html", post = post, form = form)

@post.route("/post/show/<string:slug>", methods = ["POST", "GET"])
def show(slug):
	post = Post.get_by_slug(slug)
	if post is None:
		abort(404, description="No post was found with the given ID")
	user = User.get_by_id(post.posted_by)
	post.username = user.username
	page = request.args.get('page', 1, type=int)
	comments = Comment.query.filter_by(post_id = post.id).order_by(Comment.id.desc()).paginate(page = page, per_page = 5, error_out = True)
	for comment in comments.items:
		user = User.get_by_id(comment.user_id)
		# I don't want to store this elements in the database but I need them in the front end
		comment.username = user.username
		# Email needed for the user's avatar
		comment.email = user.email
	# Url variables for the pagination
	next_url = url_for('post.show', slug = post.title_slug, page=comments.next_num) \
	if comments.has_next else None
	prev_url = url_for('post.show', slug = post.title_slug, page=comments.prev_num) \
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
			return render_template("post/show.html", post = post, form = form, comments = comments.items, next_url = next_url, prev_url = prev_url)
			
	return render_template("post/show.html", post = post, form = form, comments = comments.items, next_url = next_url, prev_url = prev_url)


@post.route("/post/delete/<int:post_id>")
@login_required
def delete(post_id):
	post = Post.query.get(post_id)
	if current_user.id == post.posted_by or current_user.admin:
		if post is None:
			abort(404, description="No Post was Found with the given ID")
		#To delete all post's comments with it
		comments = Comment.query.filter_by(post_id = post.id).all()
		for comment in comments:
			db.session.delete(comment)
		db.session.delete(post)
		try:
			db.session.commit()
			flash('Post deleted')
		except:
			db.session.rollback()
	else:
		flash("You aren't the post user")
	return redirect(url_for('post.index'))

@app.route("/delete_comment/<int:comment_id>")
def delete_comment(comment_id):
	comment = Comment.query.get(comment_id)
	post = Post.get_by_id(comment.post_id)
	if current_user.id == comment.user_id or current_user.admin:
		if comment is None:
			abort(404, description="No comment was found with the given ID")
		db.session.delete(comment)
		try:
			db.session.commit()
			flash('Comment deleted')
		except:
			db.session.rollback()
	else:
		flash("You aren't the comment user")
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

@app.route("/comment_like/<int:comment_id>/<action>")
@login_required
def comment_like(comment_id, action):
    comment = Comment.query.filter_by(id = comment_id).first_or_404()
    if action == 'like':
        current_user.like_comment(comment)
        db.session.commit()
    if action == 'unlike':
        current_user.unlike_comment(comment)
        db.session.commit()
    return redirect(request.referrer)