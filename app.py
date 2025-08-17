from flask import Flask, render_template, request, redirect, url_for
import json
import os
from datetime import datetime

app = Flask(__name__)
ARQUIVO_LEADS = "leads.json"

def carregar_leads():
    if not os.path.exists(ARQUIVO_LEADS):
        return []
    with open(ARQUIVO_LEADS, "r") as f:
        return json.load(f)

def salvar_leads(leads):
    with open(ARQUIVO_LEADS, "w") as f:
        json.dump(leads, f, indent=4)

@app.template_filter('format_data')
def format_data(value):
    try:
        dt = datetime.strptime(value, "%Y-%m-%d")
        return dt.strftime("%d/%m/%Y")
    except Exception:
        return value

@app.route("/", methods=["GET", "POST"])
def index():
    leads = carregar_leads()

    # Pegando filtros da query string (GET) ou formulário (POST)
    if request.method == "POST":
        origem = request.form.get("origem", "").strip().lower()
        status = request.form.get("status", "").strip()
        data_inicio = request.form.get("data_inicio", "")
        data_fim = request.form.get("data_fim", "")

        def filtro(lead):
            if origem and origem not in lead["origem"].lower():
                return False
            if status and lead["status"] != status:
                return False
            # Filtro data contato >= data_inicio
            if data_inicio:
                try:
                    lead_date = datetime.strptime(lead["data_contato"], "%Y-%m-%d")
                    inicio_date = datetime.strptime(data_inicio, "%Y-%m-%d")
                    if lead_date < inicio_date:
                        return False
                except:
                    return False
            # Filtro data contato <= data_fim
            if data_fim:
                try:
                    lead_date = datetime.strptime(lead["data_contato"], "%Y-%m-%d")
                    fim_date = datetime.strptime(data_fim, "%Y-%m-%d")
                    if lead_date > fim_date:
                        return False
                except:
                    return False
            return True

        leads = list(filter(filtro, leads))

    else:
        # Se for GET, usa valores vazios para filtros
        origem = ""
        status = ""
        data_inicio = ""
        data_fim = ""

    return render_template("index.html", leads=leads, origem=origem, status=status, data_inicio=data_inicio, data_fim=data_fim)

@app.route("/cadastrar", methods=["GET", "POST"])
def cadastrar():
    if request.method == "POST":
        nome = request.form["nome"]
        origem = request.form["origem"]
        data_contato = request.form["data_contato"]
        observacao = request.form["observacao"]
        status = request.form["status"]
        leads = carregar_leads()
        leads.append({
            "nome": nome,
            "origem": origem,
            "data_contato": data_contato,
            "observacao": observacao,
            "status": status
        })
        salvar_leads(leads)
        return redirect(url_for("index"))
    return render_template("cadastrar.html")

@app.route("/editar/<int:index>", methods=["GET", "POST"])
def editar(index):
    leads = carregar_leads()
    if index < 0 or index >= len(leads):
        return "Lead não encontrado", 404
    
    if request.method == "POST":
        leads[index]["nome"] = request.form["nome"]
        leads[index]["origem"] = request.form["origem"]
        leads[index]["data_contato"] = request.form["data_contato"]
        leads[index]["observacao"] = request.form["observacao"]
        leads[index]["status"] = request.form["status"]
        salvar_leads(leads)
        return redirect(url_for("index"))
    
    lead = leads[index]
    return render_template("editar.html", lead=lead, index=index)

@app.route("/excluir/<int:index>", methods=["POST"])
def excluir(index):
    leads = carregar_leads()
    if index < 0 or index >= len(leads):
        return "Lead não encontrado", 404
    leads.pop(index)
    salvar_leads(leads)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
































