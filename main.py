from flask import Flask, render_template, redirect, url_for, flash, abort
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_sqlalchemy import SQLAlchemy
from forms import CreateTicketForm
import os
from dotenv import load_dotenv

load_dotenv()


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("FLASK_SECRET_KEY")

bootstrap = Bootstrap(app)
ckeditor = CKEditor(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)


class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    summary = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(512), nullable=False)
    time = db.Column(db.String(50), nullable=False)


@app.route('/')
def home():
    return 'Hello, World!'


@app.route('/create-ticket')
def create_ticket():
    form = CreateTicketForm()
    return render_template('create_ticket.html', form=form)


@app.route('/project/<int:project_id>')
def project(project_id):
    return render_template('project.html', id=project_id)


if __name__ == "__main__":
    app.run(debug=True)
