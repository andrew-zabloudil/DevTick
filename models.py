from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin


db = SQLAlchemy()


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
