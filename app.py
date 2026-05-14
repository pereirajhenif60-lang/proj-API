import os
import json
from flask import Flask, request, jsonify, render_template, redirect, url_for

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), "templates"))

DATA_FILE = os.path.join(os.path.dirname(__file__), "despesas.json")

despesas = []
proximo_id = 1
categorias_disponiveis = [
    "Moradia",
    "Alimentação",
    "Transporte",
    "Saúde",
    "Lazer",
    "Educação",
    "cartão",
    "Outros"
]
meses_disponiveis = [
    "Janeiro", "Fevereiro", "Março", "Abril",
    "Maio", "Junho", "Julho", "Agosto",
    "Setembro", "Outubro", "Novembro", "Dezembro"
]

def carregar_despesas():
    global despesas, proximo_id
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            despesas = data.get("despesas", [])
            proximo_id = data.get("proximo_id", 1)

def salvar_despesas():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({"despesas": despesas, "proximo_id": proximo_id}, f, ensure_ascii=False, indent=2)

def adicionar_despesa(descricao, valor, categoria, mes):
    global proximo_id
    despesa = {
        "id": proximo_id,
        "descricao": descricao,
        "valor": valor,
        "categoria": categoria or "Sem categoria",
        "mes": mes or "Sem mês"
    }
    despesas.append(despesa)
    proximo_id += 1
    salvar_despesas()
    return despesa

def filtrar_despesas(categoria=None, mes=None):
    resultado = despesas
    if categoria:
        resultado = [d for d in resultado if d["categoria"] == categoria]
    if mes:
        resultado = [d for d in resultado if d["mes"] == mes]
    return resultado

def agrupar_por_categoria(despesas_filtradas):
    grupos = {}
    for despesa in despesas_filtradas:
        chave = despesa["categoria"] or "Sem categoria"
        grupos.setdefault(chave, []).append(despesa)

    ordem = [c for c in categorias_disponiveis if c in grupos]
    extras = [c for c in grupos if c not in ordem]
    return [
        {"nome": cat, "despesas": grupos[cat], "total": sum(d["valor"] for d in grupos[cat])}
        for cat in ordem + extras
    ]

@app.route('/')
def home():
    categoria_selecionada = request.args.get('categoria')
    mes_selecionado = request.args.get('mes')

    despesas_filtradas = filtrar_despesas(categoria_selecionada, mes_selecionado)
    grupos = agrupar_por_categoria(despesas_filtradas)
    total = sum(d["valor"] for d in despesas_filtradas)

    return render_template(
        'index.html',
        despesas=despesas_filtradas,
        total=total,
        categorias=categorias_disponiveis,
        meses=meses_disponiveis,
        grupos=grupos,
        categoria_selecionada=categoria_selecionada,
        mes_selecionado=mes_selecionado
    )

@app.route('/despesas', methods=['GET'])
def get_despesas():
    return jsonify(despesas)

@app.route('/despesas', methods=['POST'])
def post_despesas():
    if request.is_json:
        dados = request.get_json()
    else:
        dados = request.form

    descricao = dados.get("descricao", "").strip()
    valor = float(dados.get("valor", 0))
    categoria = dados.get("categoria", "").strip()
    mes = dados.get("mes", "").strip()

    if categoria == "Outros":
        categoria = dados.get("categoria_outra", "").strip() or "Outros"

    adicionar_despesa(descricao, valor, categoria, mes)

    return redirect(url_for(
        'home',
        categoria=request.args.get('categoria'),
        mes=request.args.get('mes')
    ))

@app.route('/despesas/excluir/<int:despesa_id>', methods=['POST'])
def excluir_despesa(despesa_id):
    global despesas
    despesas = [d for d in despesas if d["id"] != despesa_id]
    salvar_despesas()
    return redirect(url_for(
        'home',
        categoria=request.args.get('categoria'),
        mes=request.args.get('mes')
    ))

@app.route('/despesas/limpar', methods=['POST'])
def limpar_despesas():
    global despesas, proximo_id
    despesas = []
    proximo_id = 1
    salvar_despesas()
    return redirect(url_for('home'))

carregar_despesas()

if __name__ == '__main__':
    app.run(debug=True)
