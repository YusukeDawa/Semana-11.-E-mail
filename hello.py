import os
import sys
from threading import Thread
from flask import Flask, render_template, session, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail, Message

import requests
from datetime import datetime

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['API_KEY'] = os.environ.get('API_KEY')
app.config['API_URL'] = os.environ.get('API_URL')
app.config['API_FROM'] = os.environ.get('API_FROM')

app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]'
app.config['FLASKY_ADMIN'] = os.environ.get('FLASKY_ADMIN')

bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)


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


#def send_simple_message():
def send_simple_message(to, subject, newUser):
    print('Enviando mensagem (POST)...', file=sys.stderr)
    print('URL: ' + str(app.config['API_URL']), file=sys.stderr)
    print('api: ' + str(app.config['API_KEY']), file=sys.stderr)
    print('from: ' + str(app.config['API_FROM']), file=sys.stderr)
    print('to: ' + str(to), file=sys.stderr)
    print('subject: ' + str(app.config['FLASKY_MAIL_SUBJECT_PREFIX']) + ' ' + subject, file=sys.stderr)
    print('text: ' + "Novo usuário cadastrado: " + newUser, file=sys.stderr)

    resposta = requests.post(app.config['API_URL'], 
                             auth=("api", app.config['API_KEY']), data={"from": app.config['API_FROM'], 
                                                                        "to": to, 
                                                                        "subject": app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + ' ' + subject, 
                                                                        "text": "Novo usuário cadastrado: " + newUser})
    #resposta = requests.post("https://api.mailgun.net/v3/sandboxac1a400f6f814141b8b87a5c3d287cc5.mailgun.org/messages", auth=("api", "d234f37ea61bf5659d81c3b8da3b7a89-911539ec-8316a90b"), data={"from": "fabio.teixeira@ifsp.edu.br", "to": ["fabio.teixeira@ifsp.edu.br", "flaskaulasweb@zohomail.com"], "subject": "Mensagem enviada por meio do Mailgun - " + datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), "text": "Testing some Mailgun awesomeness!"})
    print('Enviando mensagem (Resposta)...' + str(resposta) + ' - ' + datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), file=sys.stderr)
    return resposta


class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


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
            print('Verificando FLASKY_ADMIN', flush=True)
            if app.config['FLASKY_ADMIN']:                
                print('Enviando mensagem...', file=sys.stderr)
                
                print('FLASKY_ADMIN: ' + str(app.config['FLASKY_ADMIN']), file=sys.stderr)
                print('URL: ' + str(app.config['API_URL']), file=sys.stderr)
                print('api: ' + str(app.config['API_KEY']), file=sys.stderr)
                print('from: ' + str(app.config['API_FROM']), file=sys.stderr)
                print('to: ' + str([app.config['FLASKY_ADMIN'], "flaskaulasweb@zohomail.com"]), file=sys.stderr)
                print('subject: ' + str(app.config['FLASKY_MAIL_SUBJECT_PREFIX']), file=sys.stderr)
                print('text: ' + "Novo usuário cadastrado: " + form.name.data, file=sys.stderr)

                print('URL: ' + str(app.config['API_URL']), file=sys.stderr)
                send_simple_message([app.config['FLASKY_ADMIN'], "flaskaulasweb@zohomail.com"], 'Novo usuário', form.name.data)
                #send_simple_message()
        else:
            session['known'] = True
        session['name'] = form.name.data
        return redirect(url_for('index'))
    return render_template('index.html', form=form, name=session.get('name'),
                           known=session.get('known', False))