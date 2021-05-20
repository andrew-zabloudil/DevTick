# Import Flask modules
from flask import Flask, redirect, url_for, request
from flask_admin import Admin
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_login import LoginManager, current_user
from flask_talisman import Talisman

# Import OS-related Modules
import os
from dotenv import load_dotenv

# Import Admin Views
from blueprints.admin.admin import AdminIndexView, DevTickModelView

# Import Models
from models import db, AssociatedUser, User, Project, Ticket

# Import Blueprints
from blueprints.general.general import general_blueprint
from blueprints.auth.auth import auth_blueprint
from blueprints.projects.projects import projects_blueprint


# Loads environment file
load_dotenv()

# Configures website security protocols for the Talisman extension.
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

# Creates Database URI
uri = os.getenv("DATABASE_URL", "sqlite:///devtick.db")
# Ensures uri begins with postgresql:// to match current standard
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)


# Creates login manager for the Flask app
login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    # Loads user from database to the login manager
    return User.query.get(int(user_id))


# Helper functions to confirm a user's role for permissions
def is_creator(project_id):
    # Checks if current user is the project's creator
    project = Project.query.get(project_id)
    return current_user.id == project.creator_id


def is_admin(project_id):
    # Checks if current user has the admin role on the project
    if not is_creator(project_id):
        association = AssociatedUser.query.filter_by(
            project_id=project_id).filter_by(user_id=current_user.id).first()
        return association.user_role == "Admin"


def is_editor(project_id):
    # Checks if current user has the editor role on the project
    if not is_creator(project_id):
        association = AssociatedUser.query.filter_by(
            project_id=project_id).filter_by(user_id=current_user.id).first()
        return association.user_role == "Editor"


def is_viewer(project_id):
    # Checks if current user has the viewer role on the project
    if not is_creator(project_id):
        association = AssociatedUser.query.filter_by(
            project_id=project_id).filter_by(user_id=current_user.id).first()
        return association.user_role == "Viewer"


app = Flask(__name__)


def configure_app():
    # Creates Flask app
    app.config['SECRET_KEY'] = os.getenv("FLASK_SECRET_KEY")

    app.register_blueprint(general_blueprint)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(projects_blueprint)

    # Configures Bootstrap and CKEditor for the app.
    bootstrap = Bootstrap(app)
    ckeditor = CKEditor(app)
    talisman = Talisman(app, content_security_policy=csp)

    # Configures the database
    app.config['SQLALCHEMY_DATABASE_URI'] = uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    with app.app_context():
        db.create_all()

    # Initializes the login manager for the app
    login_manager.init_app(app)

    # Adds views to the admin panel
    admin = Admin(app, name='DevTickAdmin', index_view=AdminIndexView())
    admin.add_view(DevTickModelView(User, db.session))
    admin.add_view(DevTickModelView(Project, db.session))
    admin.add_view(DevTickModelView(AssociatedUser, db.session))
    admin.add_view(DevTickModelView(Ticket, db.session))

    # Sets jinja globals for the user permission helper functions so they can be called from templates
    app.jinja_env.globals.update(is_creator=is_creator)
    app.jinja_env.globals.update(is_admin=is_admin)
    app.jinja_env.globals.update(is_editor=is_editor)
    app.jinja_env.globals.update(is_viewer=is_viewer)

    # Runs the app
    app.run(debug=True)


# Runs the app
if __name__ == "__main__":
    configure_app()
