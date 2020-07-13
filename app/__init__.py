from flask import Flask 
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_moment import Moment
from flask_socketio import SocketIO
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///micro-post.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
socketio = SocketIO()
socketio.init_app(app)
moment = Moment(app)

from app import models

from app import views

