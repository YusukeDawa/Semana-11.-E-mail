import os

app.config['SECRET_KEY'] = 'sua-chave-secreta-aleatoria'
app.config['WTF_CSRF_ENABLED'] = True

class Config:
    SECRET_KEY = 'sua-chave-secreta-aleatoria'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'  # Exemplo de URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.mailgun.org'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = None  # Substituir por os.environ.get('MAILGUN_USERNAME')
    MAIL_PASSWORD = None  # Substituir por os.environ.get('MAILGUN_PASSWORD')
    MAIL_DEFAULT_SENDER = 'seuemail@exemplo.com'
