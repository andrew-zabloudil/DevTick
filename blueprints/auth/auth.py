from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, LoginManager, login_required, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, User
from forms import LoginForm, RegisterForm


auth_blueprint = Blueprint('auth', __name__, template_folder='templates')


# Route for the login page
@auth_blueprint.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not user:
            flash("There is no account associated with that email address.")
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('general.home'))
            else:
                flash('Incorrect Password')
    return render_template('login.html', form=form)


# Route for logging out a user
@auth_blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('general.home'))


# Route for registering a new user
@auth_blueprint.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(
            form.password.data,
            method="pbkdf2:sha256",
            salt_length=8
        )
        new_user = User(
            name=form.name.data,
            email=form.email.data,
            password=hashed_password,
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        flash('Registered successully. You have been logged in.')
        return redirect(url_for('general.home'))
    return render_template('register.html', form=form)
