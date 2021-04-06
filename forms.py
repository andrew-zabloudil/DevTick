from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, URL, Email
from flask_ckeditor import CKEditorField

# WTForm


class CreateTicketForm(FlaskForm):
    name = StringField("Ticket Name", validators=[DataRequired()])
    summary = StringField("Summary", validators=[DataRequired()])
    description = CKEditorField(
        "Full Description", validators=[DataRequired()])
    submit = SubmitField("Create Ticket")

# Template to be used later for user registration.
# class RegisterForm(FlaskForm):
#     email = StringField("Email", validators=[DataRequired(), Email()])
#     password = PasswordField("Password", validators=[DataRequired()])
#     name = StringField("Name", validators=[DataRequired()])
#     submit = SubmitField("Sign Me Up!")


# class LoginForm(FlaskForm):
#     email = StringField("Email", validators=[DataRequired(), Email()])
#     password = PasswordField("Password", validators=[DataRequired()])
#     submit = SubmitField("Let Me In!")


# class CommentForm(FlaskForm):
#     comment = CKEditorField("Comment", validators=[DataRequired()])
#     submit = SubmitField("Submit Comment")
