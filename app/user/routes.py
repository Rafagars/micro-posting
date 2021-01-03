from flask import render_template, request
from flask_login import current_user, login_required
from . import user
from app.post.models import Post
from .models import User
from .forms import EditUser


@user.route("/user/<username>")
def show(username):
    user = User.query.filter_by(username=username).first()
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(posted_by=user.id).order_by(Post.id.desc()).paginate(page=page, per_page=5,
                                                                                      error_out=True)
    # Url variables for the pagination
    next_url = url_for('user.show', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('user.show', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    return render_template("user/show.html", posts=posts.items, user=user, next_url=next_url, prev_url=prev_url)


@user.route("/user/edit/<int:user_id>", methods=['POST', 'GET'])
@login_required
def edit(user_id):
    form = None
    if current_user.id == user_id:
        form = EditUser()
        if form.validate_on_submit():
            user = User.get_by_id(user_id)
            if user.check_password(form.current_password.data):
                user.set_password(form.new_password.data)
                user.save()
                flash('Password changed succesfully')
                return redirect(url_for('post.index'))
            else:
                message = "That's not your current password"
                return render_template("user/edit.html", form=form, message=message)
    else:
        flash("You can't change other user's password")
        redirect(url_for('post.index'))
    return render_template("user/edit.html", form=form)
