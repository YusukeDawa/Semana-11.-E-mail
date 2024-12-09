import os
from flask import Flask, render_template, request, redirect, flash
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy

# Configuração da aplicação
app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua-chave-secreta-aleatoria'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'  # Alterar para o banco que estiver usando
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.mailgun.org'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAILGUN_USERNAME')  # Buscar de variáveis de ambiente
app.config['MAIL_PASSWORD'] = os.environ.get('MAILGUN_PASSWORD')  # Buscar de variáveis de ambiente
app.config['MAIL_DEFAULT_SENDER'] = 'flaskaulasweb@zohomail.com'

# Inicialização das extensões
db = SQLAlchemy(app)
mail = Mail(app)

# Modelo de Usuário
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), default='User')

# Rota principal
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form.get('name')
        send_email = request.form.get('send_email')

        if not name:
            flash('Por favor, insira um nome.', 'danger')
            return redirect('/')

        # Adicionar usuário ao banco de dados
        user = User(name=name)
        db.session.add(user)
        db.session.commit()

        # Enviar e-mail se solicitado
        if send_email:
            msg = Message(
                subject="Novo usuário cadastrado",
                recipients=["flaskaulasweb@zohomail.com"],
                body=f"O usuário {name} foi cadastrado no sistema."
            )
            try:
                mail.send(msg)
                flash('E-mail enviado com sucesso!', 'success')
            except Exception as e:
                flash(f'Erro ao enviar e-mail: {str(e)}', 'danger')

        flash('Usuário cadastrado com sucesso!', 'success')
        return redirect('/')

    # Recuperar todos os usuários para exibição
    users = User.query.all()
    return render_template('index.html', users=users)



# Comando para inicializar o banco de dados
@app.cli.command('init-db')
def init_db():
    """Inicializa o banco de dados."""
    db.create_all()
    print("Banco de dados inicializado.")

# Executar o servidor
if __name__ == '__main__':
    app.run(debug=True)
