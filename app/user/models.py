from flask import url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from slugify import slugify
from sqlalchemy import exc
from hashlib import md5
import datetime

from app import db
from app.post.models import PostLike, CommentLike

class User(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key = True)
	username = db.Column(db.String, unique = True)
	email = db.Column(db.String, unique = True)
	password = db.Column(db.String)
	admin = db.Column(db.Boolean, default = False)
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

	#Since has_liked is for posts and comment, we specified that the post as None		
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
   
   	#Only one function to check is the user already liked the post or comment
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