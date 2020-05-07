from flask import url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from slugify import slugify
from sqlalchemy import exc
from hashlib import md5
import datetime

from app import db
from app import app

#### MODELS ########

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
	comment_liked = db.relationship('CommentLike',
								foreign_keys='CommentLike.user_id',
								backref='user', lazy='dynamic')
	
	def like_post(self, post):
		if not self.has_liked(post):
			like = PostLike(user_id = self.id, post_id = post.id)
			db.session.add(like)
			
	def unlike_post(self, post):
		if self.has_liked(post):
			PostLike.query.filter_by(
				user_id = self.id,
				post_id = post.id
			).delete()

	def like_comment(self, comment):
		if not self.has_liked(None, comment):
			like = CommentLike(user_id = self.id, comment_id = comment.id)
			db.session.add(like)

	def unlike_comment(self, comment):
		if self.has_liked(None ,comment):
			CommentLike.query.filter_by(
				user_id = self.id,
				comment_id = comment.id
			).delete()
   
	def has_liked(self, post = None, comment = None):
		if post != None:
			return PostLike.query.filter(
				PostLike.user_id == self.id,
				PostLike.post_id == post.id
			).count() > 0
		if comment != None:
			return CommentLike.query.filter(
				CommentLike.user_id == self.id,
				CommentLike.comment_id == comment.id
			).count() > 0

	def avatar(self, size):
		digest = md5(self.email.lower().encode('utf-8')).hexdigest()
		return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)
 
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
	title_slug = db.Column(db.String, unique = True, nullable = False)
	body = db.Column(db.Text)
	posted_by = db.Column(db.Integer, db.ForeignKey('user.id'))
	created = db.Column(db.DateTime, default = datetime.datetime.now)
	likes = db.relationship('PostLike', backref='post', lazy='dynamic')
	comments = db.relationship('Comment', backref='post', lazy = 'dynamic')

	def save(self):
		if not self.id:
			db.session.add(self)
		if not self.title_slug:
			self.title_slug = slugify(self.title)

		saved = False
		count = 0
		while not saved:
			try:
				db.session.commit()
				saved = True
			except exc.IntegrityError:
				count += 1
				self.title_slug = f'{slugify(self.title)}-{count}'
				db.session.rollback()
				db.session.add(self)
				db.session.flush()

	def public_url(self):
		return url_for('show_post', slug=self.title_slug)

	@staticmethod
	def get_by_id(id):
		return Post.query.get(id)

	@staticmethod
	def get_by_slug(slug):
		return Post.query.filter_by(title_slug = slug).first()
 
""" Model for Post Likes """
class PostLike(db.Model):
    __tablename__ = 'post_like'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))


""" Model for Comments """
class Comment(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	body = db.Column(db.String)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
	created = db.Column(db.DateTime, default = datetime.datetime.now)
	likes = db.relationship('CommentLike', backref='comment', lazy='dynamic')

	def avatar(self, size):
		digest = md5(self.email.lower().encode('utf-8')).hexdigest()
		return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

	def save(self):
		if not self.id:
			db.session.add(self)
		db.session.commit()

""" Model for Comment Likes """
class CommentLike(db.Model):
	__tablename__ = 'comment_like'
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'))

db.create_all()

# Commit changes in the session
try:
    db.session.commit()
except: 
    db.session.rollback()
finally:
    db.session.close()