from flask import Flask, render_template, redirect, url_for, flash, abort
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
from datetime import datetime as dt
from forms import CreateTicketForm, CreateProjectForm, LoginForm, RegisterForm
load_dotenv()


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("FLASK_SECRET_KEY")

bootstrap = Bootstrap(app)
ckeditor = CKEditor(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    created_projects = relationship("Project", back_populates="creator")
    created_tickets = relationship("Ticket", back_populates="creator")
    invited_projects = relationship("Project", back_populates="invited_users")


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    summary = db.Column(db.String(250), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    time = db.Column(db.String(50), nullable=False)
    tags = db.Column(db.String(500))
    tickets = relationship("Ticket", back_populates="project")
    creator = relationship("User", back_populates="projects")
    invited_userse = relationship("User", back_populates="invited_projects")


class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    summary = db.Column(db.String(250), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    time = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(10), nullable=False)
    tags = db.Column(db.String(500))
    project = relationship("Project", back_populates="tickets")
    creator = relationship("User", back_populates="tickets")


db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/create-project', methods=["GET", "POST"])
def create_project():
    form = CreateProjectForm()
    if form.validate_on_submit():
        new_project = Project(
            name=form.name.data,
            summary=form.summary.data,
            description=form.description.data,
            time=dt.now(),
            tags="",
        )
        db.session.add(new_project)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('create_project.html', form=form)


@app.route('/create-ticket', methods=["GET", "POST"])
def create_ticket():
    form = CreateTicketForm()
    if form.validate_on_submit():
        new_ticket = Ticket(
            name=form.name.data,
            summary=form.summary.data,
            description=form.description.data,
            time=dt.now(),
            category=form.category.data,
            status="Open",
            project_id=1,
        )
        db.session.add(new_ticket)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('create_ticket.html', form=form)


@app.route('/project/<int:project_id>')
def project(project_id):
    return render_template('project.html', id=project_id)


if __name__ == "__main__":
    app.run(debug=True)
