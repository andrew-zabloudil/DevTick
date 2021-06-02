from flask import Blueprint, render_template, redirect, url_for, abort, request, current_app
from flask_login import login_required, current_user
from flask_sqlalchemy import SQLAlchemy

from functools import wraps
from datetime import datetime as dt

from forms import CreateProjectForm, CreateTicketForm, EditTicketForm, AddUserForm
from models import db, AssociatedUser, User, Project, Ticket

projects_blueprint = Blueprint(
    'projects', __name__, static_folder='static', template_folder='templates')


def is_creator(project_id):
    project = Project.query.get(project_id)
    return current_user.id == project.creator_id


def is_admin(project_id):
    if not is_creator(project_id):
        association = AssociatedUser.query.filter_by(
            project_id=project_id).filter_by(user_id=current_user.id).first()
        return association.user_role == "Admin"

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


# Route for displaying a project
@projects_blueprint.route('/project/<int:project_id>', methods=["GET", "POST"])
@associated_user
def project(project_id):
    project = Project.query.get(project_id)
    return render_template('project.html', project=project)


# Route for creating a new project
@projects_blueprint.route('/create-project', methods=["GET", "POST"])
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
        return redirect(url_for('general.home'))
    return render_template('create_project.html', form=form)


# Route for editing a project's information
@projects_blueprint.route('/project/<int:project_id>/edit-project/', methods=["GET", "POST"])
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
        return redirect(url_for("projects.project", project_id=project_id))
    return render_template("create_project.html", form=form)


@projects_blueprint.route('/project/<int:project_id>/delete-project/', methods=["GET", "POST"])
@login_required
@admin_only
def delete_project(project_id):
    project = Project.query.get(project_id)
    db.session.delete(project)
    db.session.commit()
    return redirect(url_for('general.home'))

# Route for creating a new ticket on a project


@projects_blueprint.route('/project/<int:project_id>/create-ticket', methods=["GET", "POST"])
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
        return redirect(url_for('projects.project', project_id=project_id))
    return render_template('create_ticket.html', form=form)


# Route for editing the fields on a ticket
@projects_blueprint.route('/project/<int:project_id>/edit-ticket/<int:ticket_id>', methods=["GET", "POST"])
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
        return redirect(url_for("projects.project", project_id=project_id))
    return render_template("create_ticket.html", form=form)


# Route for adding a new user to a project
@projects_blueprint.route('/project/<int:project_id>/add-user', methods=["GET", "POST"])
@login_required
@admin_only
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
        return redirect(url_for('projects.project', project_id=project_id))
    return render_template('add_user.html', form=form)


# Route for removing a user from a project
@projects_blueprint.route('/project/<int:project_id>/remove-user/<int:user_id>')
@login_required
@admin_only
def remove_user(project_id, user_id):
    user = User.query.get(user_id)
    project = Project.query.get(project_id)
    association = AssociatedUser.query.filter_by(
        project=project).filter_by(user=user).first()
    db.session.delete(association)
    db.session.commit()
    return redirect(url_for('projects.project', project_id=project_id))


# Route for editing a user's role on a project
@projects_blueprint.route('/project/<int:project_id>/edit-user/<int:user_id>', methods=["POST"])
@login_required
@admin_only
def edit_user(project_id, user_id):
    user = User.query.get(user_id)
    project = Project.query.get(project_id)
    association = AssociatedUser.query.filter_by(
        project=project).filter_by(user=user).first()
    new_role = request.form["edit-role"]
    association.user_role = new_role
    db.session.commit()
    return redirect(url_for('projects.project', project_id=project_id))
