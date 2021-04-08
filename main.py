from flask import Flask, render_template, redirect, url_for, flash, abort
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_sqlalchemy import SQLAlchemy
from forms import CreateTicketForm
import os
from dotenv import load_dotenv
from datetime import datetime as dt

load_dotenv()


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("FLASK_SECRET_KEY")

bootstrap = Bootstrap(app)
ckeditor = CKEditor(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)


class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    summary = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(512), nullable=False)
    time = db.Column(db.String(50), nullable=False)


db.create_all()


@app.route('/')
def home():
    return 'Hello, World!'


@app.route('/create-ticket', methods=["GET", "POST"])
def create_ticket():
    form = CreateTicketForm()
    if form.validate_on_submit():
        new_ticket = Ticket(
            name=form.name.data,
            summary=form.summary.data,
            description=form.description.data,
            time=dt.now()
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
