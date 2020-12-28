from app import *
from . import session
from flask_login import current_user
from app.user.models import User
from .forms import SignUpForm, LoginForm
from flask import flash, render_template, abort, redirect, url_for, request, jsonify
from werkzeug.urls import url_parse
import os


@session.route("/login", methods = ["POST", "GET"])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('post.index'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.get_by_email(form.email.data.capitalize())
		#Checks if user exists and then checks user's password
		if user is not None and user.check_password(form.password.data):
			login_user(user, remember = form.remember_me.data)
			next_page = request.args.get('next')
			if not next_page or url_parse(next_page).netloc != '':
				next_page = url_for('post.index')
			flash('Welcome back')
			return redirect(next_page)
		else:
			message = "Sorry, wrong email or pasword" 
			return(render_template('session/login.html', form = form, message = message))
	return render_template('session/login.html', form = form)

@session.route("/signup", methods = ["POST", "GET"])
def signup():
	if current_user.is_authenticated:
		return redirect(url_for('post.index'))
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
			if user.id == 1: 
				user.admin = True
				db.session.commit()
			#Log in the user
			login_user(user, remember = True)
			next_page = request.args.get('next', None)
			if not next_page or url_parse(next_page).netloc != '':
				next_page = url_for('post.index')
			flash('Welcome to Micro-Posting')
			return redirect(next_page)
	return render_template('session/Signup.html', form = form, message = message)

@session.route("/logout")
@login_required
def logout():
	logout_user()
	return redirect(url_for('post.index'))