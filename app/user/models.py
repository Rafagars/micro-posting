from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5

from app import db
from app.post.models import Like, PostLike, CommentLike


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    admin = db.Column(db.Boolean, default=False)
    post = db.relationship('Post', backref='user')
    liked = db.relationship('Like',
                            foreign_keys='Like.user_id',
                            backref='user', lazy='dynamic')

    def like(self, type, content):
        if type == 'post':
            if not self.has_liked(content):
                like = PostLike(user_id=self.id, post_id=content.id)
                db.session.add(like)
        elif type == 'comment':
            if not self.has_liked(None, content):
                like = CommentLike(user_id=self.id, comment_id=content.id)
                db.session.add(like)

    def unlike(self, type, content):
        if type == 'post':
            if self.has_liked(content):
                like = db.session.query(PostLike).filter(
                    PostLike.user_id == self.id,
                    PostLike.post_id == content.id
                ).first()
                db.session.delete(like)
        elif type == 'comment':
            if self.has_liked(None, content):
                like = db.session.query(CommentLike).filter(
                    CommentLike.user_id == self.id,
                    CommentLike.comment_id == content.id
                ).first()
                db.session.delete(like)
        db.session.commit()

    # Only one function to check is the user already liked the post or comment
    def has_liked(self, post=None, comment=None):
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
        return User.query.filter_by(email=email).first()
