from flask import Flask, render_template, request, redirect, url_for
import psycopg2
import os
from datetime import datetime

app = Flask(__name__)

# Conecta ao banco de dados
def get_db_connection():
    db_url = os.getenv('DATABASE_URL', 'dbname=leads user=postgres password=postgres host=localhost')
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    return psycopg2.connect(db_url, sslmode='require')

# Cria a tabela se não existir
def create_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            origem VARCHAR(100) NOT NULL,
            data_contato DATE NOT NULL,
            observacao TEXT,
            status VARCHAR(50) NOT NULL
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

@app.before_first_request
def initialize():
    create_table()

@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM leads ORDER BY id DESC')
    leads = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', leads=leads)

@app.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar():
    if request.method == 'POST':
        nome = request.form['nome']
        origem = request.form['origem']
        data_contato = datetime.strptime(request.form['data_contato'], '%Y-%m-%d').date()
        observacao = request.form['observacao']
        status = request.form['status']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO leads (nome, origem, data_contato, observacao, status)
            VALUES (%s, %s, %s, %s, %s)
        ''', (nome, origem, data_contato, observacao, status))
        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for('index'))

    return render_template('cadastrar.html')

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == 'POST':
        nome = request.form['nome']
        origem = request.form['origem']
        data_contato = datetime.strptime(request.form['data_contato'], '%Y-%m-%d').date()
        observacao = request.form['observacao']
        status = request.form['status']

        cur.execute('''
            UPDATE leads
            SET nome=%s, origem=%s, data_contato=%s, observacao=%s, status=%s
            WHERE id=%s
        ''', (nome, origem, data_contato, observacao, status, id))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('index'))

    cur.execute('SELECT * FROM leads WHERE id = %s', (id,))
    lead = cur.fetchone()
    cur.close()
    conn.close()
    return render_template('editar.html', lead=lead)

@app.route('/excluir/<int:id>', methods=['POST'])
def excluir(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM leads WHERE id = %s', (id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)



