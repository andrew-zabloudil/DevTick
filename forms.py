from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField
from wtforms.validators import DataRequired, URL, Email
import email_validator
from flask_ckeditor import CKEditorField

# WTForm


class CreateProjectForm(FlaskForm):
    name = StringField("Project Name", validators=[DataRequired()])
    summary = StringField("Summary", validators=[DataRequired()])
    description = CKEditorField(
        "Full Description", validators=[DataRequired()])
    submit = SubmitField("Create Project")


ticket_categories = [
    ('bug', 'Bug'), ('pf', 'Planned Feature'), ('ud', 'Update')]

user_categories = [
    ('viewer', 'Viewer'), ('editor', 'Editor'), ('admin', 'Admin')
]


class CreateTicketForm(FlaskForm):
    name = StringField("Ticket Name", validators=[DataRequired()])
    summary = StringField("Summary", validators=[DataRequired()])
    description = CKEditorField(
        "Full Description", validators=[DataRequired()])
    category = SelectField(u'Category', choices=ticket_categories)
    submit = SubmitField("Create Ticket")


class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField("Sign Me Up!")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class AddUserForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    role = SelectField(u'Category', choices=user_categories)
    submit = SubmitField("Add User")


# class CommentForm(FlaskForm):
#     comment = CKEditorField("Comment", validators=[DataRequired()])
#     submit = SubmitField("Submit Comment")
