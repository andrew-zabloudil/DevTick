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
    submit = SubmitField("Submit Project")


ticket_categories = [
    ('Bug', 'Bug'), ('Planned Feature', 'Planned Feature'), ('Update', 'Update')]

ticket_statuses = [
    ("Open", "Open"), ("Closed", "Closed")
]

user_categories = [
    ('Viewer', 'Viewer'), ('Editor', 'Editor'), ('Admin', 'Admin')
]


class CreateTicketForm(FlaskForm):
    name = StringField("Ticket Name", validators=[DataRequired()])
    summary = StringField("Summary", validators=[DataRequired()])
    description = CKEditorField(
        "Full Description", validators=[DataRequired()])
    category = SelectField(u'Category', choices=ticket_categories)
    submit = SubmitField("Create Ticket")


class EditTicketForm(FlaskForm):
    name = StringField("Ticket Name", validators=[DataRequired()])
    summary = StringField("Summary", validators=[DataRequired()])
    description = CKEditorField(
        "Full Description", validators=[DataRequired()])
    category = SelectField(u'Category', choices=ticket_categories)
    status = SelectField(u'Status', choices=ticket_statuses)
    submit = SubmitField("Edit Ticket")


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
    role = SelectField(u'Role', choices=user_categories)
    submit = SubmitField("Submit")


# class CommentForm(FlaskForm):
#     comment = CKEditorField("Comment", validators=[DataRequired()])
#     submit = SubmitField("Submit Comment")
