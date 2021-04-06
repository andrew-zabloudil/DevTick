from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)


class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    summary = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(512), nullable=False)
    time = db.Column(db.String(50), nullable=False)


@app.route('/')
def projects():
    return 'Hello, World!'
