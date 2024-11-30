import os
from flask import Flask, render_template, session, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail, Message

from datetime import datetime

# Setup base directory for SQLite database
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# API and mail configurations (environment variables)
app.config['API_KEY'] = os.environ.get('MY_API_KEY')
app.config['API_URL'] = os.environ.get('MY_API_URL')
app.config['MAIL_FROM'] = os.environ.get('MY_MAIL_FROM')
app.config['FLASKY_ADMIN'] = os.environ.get('FLASKY_ADMIN')

# Mailgun SMTP configuration
app.config['MAIL_SERVER'] = 'smtp.mailgun.org'
app.config['MAIL_PORT'] = 587  # or 465 for SSL
app.config['MAIL_USE_TLS'] = True  # Enable TLS
app.config['MAIL_USE_SSL'] = False  # Disable SSL
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')  # Mailgun SMTP username
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')  # Mailgun SMTP password
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MY_MAIL_FROM')  # Default email address for sending


bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)

# Database models
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username


# Flask-WTF Form for user input
class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')


# Function to send email using Flask-Mail
def send_email(subject, recipient, body):
    msg = Message(subject=subject, recipients=[recipient])
    msg.body = body
    try:
        mail.send(msg)
        print(f"Email sent successfully to {recipient}")
    except Exception as e:
        print(f"Error sending email: {str(e)}")


# Main route to handle form submissions and user registration
@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            db.session.commit()
            session['known'] = False

            # Check if admin email is set
            if app.config['FLASKY_ADMIN']:
                send_email(
                    subject="Novo usuário cadastrado",
                    recipient=app.config['FLASKY_ADMIN'],
                    body=f"Novo usuário cadastrado: {form.name.data}"
                )

        else:
            session['known'] = True
        session['name'] = form.name.data
        return redirect(url_for('index'))
    return render_template('index.html', form=form, name=session.get('name'),
                           known=session.get('known', False))

def send_simple_message():
  	return requests.post(
  		"https://api.mailgun.net/v3/sandbox99a4b39ab33e4fa4805049dc53fa79ba.mailgun.org/messages",
  		auth=("api", "YOUR_API_KEY"),
  		data={"from": "Excited User <postmaster@sandbox99a4b39ab33e4fa4805049dc53fa79ba.mailgun.org>",
  			"to": ["aoliveiramoraes1112@gmail.com", "postmaster@sandbox99a4b39ab33e4fa4805049dc53fa79ba.mailgun.org"],
  			"subject": "Hello",
  			"text": "Testing some Mailgun awesomeness!"})


# Shell context for accessing models in the Python shell
@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)


# Error handling
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(debug=True)
