from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

# Pega URL do banco, padrão sqlite local
db_url = os.getenv('DATABASE_URL', 'sqlite:///leads.db')

# Corrige o prefixo para sqlalchemy aceitar
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Lead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    origem = db.Column(db.String(100), nullable=False)
    data_contato = db.Column(db.Date, nullable=False)
    observacao = db.Column(db.Text)
    status = db.Column(db.String(50), nullable=False)

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/')
def index():
    leads = Lead.query.all()
    return render_template('index.html', leads=leads)

@app.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar():
    if request.method == 'POST':
        nome = request.form['nome']
        origem = request.form['origem']
        data_contato = datetime.strptime(request.form['data_contato'], '%Y-%m-%d').date()
        observacao = request.form['observacao']
        status = request.form['status']

        novo_lead = Lead(nome=nome, origem=origem, data_contato=data_contato, observacao=observacao, status=status)
        db.session.add(novo_lead)
        db.session.commit()

        return redirect(url_for('index'))

    return render_template('cadastrar.html')

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    lead = Lead.query.get_or_404(id)

    if request.method == 'POST':
        lead.nome = request.form['nome']
        lead.origem = request.form['origem']
        lead.data_contato = datetime.strptime(request.form['data_contato'], '%Y-%m-%d').date()
        lead.observacao = request.form['observacao']
        lead.status = request.form['status']

        db.session.commit()
        return redirect(url_for('index'))

    return render_template('editar.html', lead=lead)

@app.route('/excluir/<int:id>', methods=['POST'])
def excluir(id):
    lead = Lead.query.get_or_404(id)
    db.session.delete(lead)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


