from flask import Flask, render_template
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
def home():
    return 'Hello, World!'


@app.route('/project/<int:project_id>')
def project(project_id):
    return render_template('project.html', id=project_id)


if __name__ == "__main__":
    app.run(debug=True)
