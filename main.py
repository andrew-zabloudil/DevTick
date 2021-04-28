from flask import Flask, render_template, redirect, url_for, flash, abort, request
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
import os
import re
from functools import wraps
from dotenv import load_dotenv
from datetime import datetime as dt
from forms import CreateTicketForm, EditTicketForm, CreateProjectForm, LoginForm, RegisterForm, AddUserForm
load_dotenv()


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("FLASK_SECRET_KEY")

bootstrap = Bootstrap(app)
ckeditor = CKEditor(app)

uri = os.getenv("DATABASE_URL", "sqlite:///devtick.db")
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)


class AssociatedUser(db.Model):
    __tablename__ = 'associated_users'
    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id'), primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey(
        'projects.id'), primary_key=True)
    user_role = db.Column(db.String(10), nullable=False)
    user = relationship("User", back_populates="invited_projects")
    project = relationship("Project", back_populates="invited_users")


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    created_projects = relationship("Project", back_populates="creator")
    created_tickets = relationship("Ticket", back_populates="creator")
    invited_projects = relationship("AssociatedUser", back_populates="user")


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


db.create_all()


def is_admin(project_id):
    association = AssociatedUser.query.filter_by(
        project_id=project_id).filter_by(user_id=current_user.id).first()
    return association.user_role == "Admin"


def is_editor(project_id):
    association = AssociatedUser.query.filter_by(
        project_id=project_id).filter_by(user_id=current_user.id).first()
    return association.user_role == "Editor"


def is_viewer(project_id):
    association = AssociatedUser.query.filter_by(
        project_id=project_id).filter_by(user_id=current_user.id).first()
    return association.user_role == "Viewer"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def associated_user(f):
    @wraps(f)
    def decorated_function(project_id, *args, **kwargs):
        project = Project.query.get(project_id)
        if not current_user.id == project.creator_id:
            for user in project.invited_users:
                if current_user.id == user.id:
                    return f(project_id, *args, **kwargs)
            return abort(403)
        else:
            return f(project_id, *args, **kwargs)
    return decorated_function


@app.route('/')
def home():
    return render_template('index.html')


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
                flash('Logged in successfully.')
                return redirect(url_for('home'))
            else:
                flash('Incorrect Password')
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


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


@app.route('/project/<int:project_id>')
@associated_user
def project(project_id):
    project = Project.query.get(project_id)
    return render_template('project.html', project=project)


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


@app.route('/project/<int:project_id>/edit-user/<int:user_id>', methods=["GET", "POST"])
@login_required
@associated_user
def edit_user(project_id, user_id):
    user = User.query.get(user_id)
    project = Project.query.get(project_id)
    association = AssociatedUser.query.filter_by(
        project=project).filter_by(user=user).first()
    form = AddUserForm(
        email=user.email
    )
    if form.validate_on_submit():
        new_role = form.role.data
        association.user_role = new_role
        db.session.commit()
        return redirect(url_for('project', project_id=project_id))
    return render_template('add_user.html', form=form)


if __name__ == "__main__":
    app.run(debug=True)
