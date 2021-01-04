from flask import url_for
from slugify import slugify
from sqlalchemy import exc
from hashlib import md5
import datetime

from app import db

class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String)
    title_slug = db.Column(db.String, unique = True, nullable = False)
    body = db.Column(db.Text)
    posted_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created = db.Column(db.DateTime, default = datetime.datetime.now)
    likes = db.relationship('PostLike', backref='post', lazy='dynamic', primaryjoin="Post.id == PostLike.post_id")
    comments = db.relationship('Comment', backref='post', lazy = 'dynamic')

    def save(self):
        if not self.id:
            db.session.add(self)
        if not self.title_slug:
            self.title_slug = slugify(self.title)

        saved = False
        count = 0
        #In case that a post with the same title exist
        while not saved:
            try:
                db.session.commit()
                saved = True
            except exc.IntegrityError:
                count += 1
                self.title_slug = f'{slugify(self.title)}-{count}'
                # To avoid a server error
                db.session.rollback()
                db.session.add(self)
                db.session.flush()

    def public_url(self):
        return url_for('post.show', slug=self.title_slug)

    @staticmethod
    def get_by_id(id):
        return Post.query.get(id)

    @staticmethod
    def get_by_slug(slug):
        return Post.query.filter_by(title_slug = slug).first()

""" Model for Comments """
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    body = db.Column(db.Text)
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

class Like(db.Model):
    __tablename__ = 'like'
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    type = db.Column(db.String(10))

    __mapper_args__={
        'polymorphic_identity': 'like',
        'polymorphic_on': type
    }

class PostLike(Like):
    __tablename__= 'post_like'
    id = db.Column(db.Integer, db.ForeignKey('like.id', ondelete='CASCADE'), primary_key = True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

    __mapper_args__ = {
        'polymorphic_identity': 'post',
    }

""" Model for Comment Likes """
class CommentLike(Like):
    __tablename__ = 'comment_like'
    id = db.Column(db.Integer, db.ForeignKey('like.id', ondelete='CASCADE'), primary_key=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'))

    __mapper_args__={
        'polymorphic_identity': 'comment'
    }