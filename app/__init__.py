from flask import Flask, render_template, abort, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_moment import Moment
from flask_share import Share
from flask_login import LoginManager
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///micro-post.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
moment = Moment(app)
share = Share(app)

db.init_app(app)
migrate.init_app(app, db)

from .post import post
from .user import user
from .session import session


app.register_blueprint(post)
app.register_blueprint(user)
app.register_blueprint(session)

login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = "session.login"

from app.user.models import User

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)


@app.route('/')
def home():
	if current_user.is_authenticated:
		return redirect(url_for('post.index'))
	return render_template("home.html")

db.create_all()

# Commit changes in the session
try:
    db.session.commit()
except: 
    db.session.rollback()
finally:
    db.session.close()
