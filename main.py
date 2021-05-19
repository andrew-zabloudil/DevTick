from flask import Flask, render_template, redirect, url_for, flash, abort, request
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from flask_talisman import Talisman

from sqlalchemy.orm import relationship
from forms import CreateTicketForm, EditTicketForm, CreateProjectForm, LoginForm, RegisterForm, AddUserForm
from werkzeug.security import generate_password_hash, check_password_hash

import os
import re
from functools import wraps
from dotenv import load_dotenv
from datetime import datetime as dt


# Loads environment file
load_dotenv()

# Creates Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("FLASK_SECRET_KEY")

# Configures Bootstrap and CKEditor for the app.
bootstrap = Bootstrap(app)
ckeditor = CKEditor(app)

# Configures website security through Talisman extension.
csp = {
    'default-src': [
        '\'self\'',
        "'unsafe-inline'",
        '*.fontawesome.com',
        'cdn.ckeditor.com',
        'cdnjs.cloudflare.com'
    ],
    'script-src': [
        '\'self\'',
        "'unsafe-inline'",
        '*.fontawesome.com',
        'cdn.ckeditor.com',
        'cdnjs.cloudflare.com'
    ]
}
talisman = Talisman(app, content_security_policy=csp)

# Creates Database
uri = os.getenv("DATABASE_URL", "sqlite:///devtick.db")
# Ensures uri begins with postgresql:// to match current standard
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Creates login manager for the Flask app
login_manager = LoginManager()
login_manager.init_app(app)


# Database model for tracking users associated with a project
class AssociatedUser(db.Model):
    __tablename__ = 'associated_users'
    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id'), primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey(
        'projects.id'), primary_key=True)
    user_role = db.Column(db.String(10), nullable=False)
    user = relationship("User", back_populates="invited_projects")
    project = relationship("Project", back_populates="invited_users")


# Database model for users
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    created_projects = relationship("Project", back_populates="creator")
    created_tickets = relationship("Ticket", back_populates="creator")
    invited_projects = relationship("AssociatedUser", back_populates="user")


# Database model for projects
class Project(db.Model):
    __tablename__ = "projects"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    summary = db.Column(db.String(250), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    time = db.Column(db.String(50), nullable=False)
    tickets = relationship("Ticket", back_populates="project")
    creator_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    creator = relationship("User", back_populates="created_projects")
    invited_users = relationship("AssociatedUser", back_populates="project")


# Database model for tickets
class Ticket(db.Model):
    __tablename__ = "tickets"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    summary = db.Column(db.String(250), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    time = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(10), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"))
    project = relationship("Project", back_populates="tickets")
    creator_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    creator = relationship("User", back_populates="created_tickets")


# Creates all database tables
db.create_all()


class AdminIndexView(AdminIndexView):
    # Creates Admin model views
    def is_accessible(self):
        if current_user.is_authenticated:
            return current_user.id == 1
        else:
            return False

    # Redirects user to login page
    def inaccessible_callback(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('login', next=request.url))


class DevTickModelView(ModelView):

    column_exclude_list = ('password')
    column_display_pk = True
    # Makes the admin view only accessible by the user with id of 0

    def is_accessible(self):
        if current_user.is_authenticated:
            return current_user.id == 1
        else:
            return False

    # Redirects user to login page
    def inaccessible_callback(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('login', next=request.url))


admin = Admin(app, name='DevTickAdmin', index_view=AdminIndexView())
admin.add_view(DevTickModelView(User, db.session))
admin.add_view(DevTickModelView(Project, db.session))
admin.add_view(DevTickModelView(AssociatedUser, db.session))
admin.add_view(DevTickModelView(Ticket, db.session))
# Helper functions to confirm a user's role for permissions


def is_creator(project_id):
    project = Project.query.get(project_id)
    return current_user.id == project.creator_id


def is_admin(project_id):
    if not is_creator(project_id):
        association = AssociatedUser.query.filter_by(
            project_id=project_id).filter_by(user_id=current_user.id).first()
        return association.user_role == "Admin"


def is_editor(project_id):
    if not is_creator(project_id):
        association = AssociatedUser.query.filter_by(
            project_id=project_id).filter_by(user_id=current_user.id).first()
        return association.user_role == "Editor"


def is_viewer(project_id):
    if not is_creator(project_id):
        association = AssociatedUser.query.filter_by(
            project_id=project_id).filter_by(user_id=current_user.id).first()
        return association.user_role == "Viewer"


# Sets jinja globals for the user permission helper functions so they can be called from templates
app.jinja_env.globals.update(is_creator=is_creator)
app.jinja_env.globals.update(is_admin=is_admin)
app.jinja_env.globals.update(is_editor=is_editor)
app.jinja_env.globals.update(is_viewer=is_viewer)


# Loads user from database to the login manager
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Decorator which checks if a user is associated with a project
def associated_user(f):
    @wraps(f)
    def decorated_function(project_id, *args, **kwargs):
        if not is_creator(project_id):
            association = AssociatedUser.query.filter_by(
                project_id=project_id).filter_by(user_id=current_user.id).first()
            if association:
                return f(project_id, *args, **kwargs)
            return abort(403)
        else:
            return f(project_id, *args, **kwargs)
    return decorated_function


# Decorator which limits access to only users with Creator or Admin roles
def admin_only(f):
    @wraps(f)
    def decorated_function(project_id, *args, **kwargs):
        if is_creator(project_id) or is_admin(project_id):
            return f(project_id, *args, **kwargs)
        return abort(403)
    return decorated_function


# Route for the home page
@app.route('/')
def home():
    return render_template('index.html')


# Route for the login page
@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not user:
            flash("There is no account associated with that email address.")
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('home'))
            else:
                flash('Incorrect Password')
    return render_template('login.html', form=form)


# Route for logging out a user
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


# Route for registering a new user
@app.route('/register', methods=["GET", "POST"])
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
        return redirect(url_for('home'))
    return render_template('register.html', form=form)


# Route for creating a new project
@app.route('/create-project', methods=["GET", "POST"])
@login_required
def create_project():
    form = CreateProjectForm()
    if form.validate_on_submit():
        new_project = Project(
            name=form.name.data,
            summary=form.summary.data,
            description=form.description.data,
            time=dt.now(),
            creator=current_user
        )
        db.session.add(new_project)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('create_project.html', form=form)


# Route for editing a project's information
@app.route('/project/<int:project_id>/edit-project/', methods=["GET", "POST"])
@login_required
@associated_user
def edit_project(project_id):
    project = Project.query.get(project_id)
    form = CreateProjectForm(
        name=project.name,
        summary=project.summary,
        description=project.description
    )
    if form.validate_on_submit():
        project.name = form.name.data
        project.summary = form.summary.data
        project.description = form.description.data
        db.session.commit()
        return redirect(url_for("project", project_id=project_id))
    return render_template("create_project.html", form=form)


# Route for creating a new ticket on a project
@app.route('/project/<int:project_id>/create-ticket', methods=["GET", "POST"])
@login_required
@associated_user
def create_ticket(project_id):
    form = CreateTicketForm()
    if form.validate_on_submit():
        new_ticket = Ticket(
            name=form.name.data,
            summary=form.summary.data,
            description=form.description.data,
            time=dt.now(),
            category=form.category.data,
            status="Open",
            project_id=project_id,
            creator=current_user
        )
        db.session.add(new_ticket)
        db.session.commit()
        return redirect(url_for('project', project_id=project_id))
    return render_template('create_ticket.html', form=form)


# Route for editing the fields on a ticket
@app.route('/project/<int:project_id>/edit-ticket/<int:ticket_id>', methods=["GET", "POST"])
@login_required
@associated_user
def edit_ticket(project_id, ticket_id):
    ticket = Ticket.query.get(ticket_id)
    form = EditTicketForm(
        name=ticket.name,
        summary=ticket.summary,
        description=ticket.description,
        category=ticket.category,
        status=ticket.status
    )
    if form.validate_on_submit():
        ticket.name = form.name.data
        ticket.summary = form.summary.data
        ticket.description = form.description.data
        ticket.category = form.category.data
        ticket.status = form.status.data
        db.session.commit()
        return redirect(url_for("project", project_id=project_id))
    return render_template("create_ticket.html", form=form)


# Route for displaying a project
@app.route('/project/<int:project_id>', methods=["GET", "POST"])
@associated_user
def project(project_id):
    project = Project.query.get(project_id)
    return render_template('project.html', project=project)


# Route for adding a new user to a project
@app.route('/project/<int:project_id>/add-user', methods=["GET", "POST"])
@login_required
@associated_user
def add_user(project_id):
    form = AddUserForm()
    if form.validate_on_submit():
        user_to_add = User.query.filter_by(email=form.email.data).first()
        project = Project.query.get(project_id)
        user_role = form.role.data
        new_association = AssociatedUser(
            user=user_to_add,
            project=project,
            user_role=user_role
        )
        db.session.add(new_association)
        db.session.commit()
        return redirect(url_for('project', project_id=project_id))
    return render_template('add_user.html', form=form)


# Route for removing a user from a project
@app.route('/project/<int:project_id>/remove-user/<int:user_id>')
@login_required
@associated_user
def remove_user(project_id, user_id):
    user = User.query.get(user_id)
    project = Project.query.get(project_id)
    association = AssociatedUser.query.filter_by(
        project=project).filter_by(user=user).first()
    db.session.delete(association)
    db.session.commit()
    return redirect(url_for('project', project_id=project_id))


# Route for editing a user's role on a project
@app.route('/project/<int:project_id>/edit-user/<int:user_id>', methods=["POST"])
@login_required
@associated_user
@admin_only
def edit_user(project_id, user_id):
    user = User.query.get(user_id)
    project = Project.query.get(project_id)
    association = AssociatedUser.query.filter_by(
        project=project).filter_by(user=user).first()
    new_role = request.form["edit-role"]
    association.user_role = new_role
    db.session.commit()
    return redirect(url_for('project', project_id=project_id))


# Runs the app
if __name__ == "__main__":
    app.run()
