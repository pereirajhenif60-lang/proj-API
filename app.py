import os
from flask import Flask, request, jsonify, render_template, redirect, url_for

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), "templates"))

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

def adicionar_despesa(descricao, valor, categoria):
    global proximo_id
    despesa = {
        "id": proximo_id,
        "descricao": descricao,
        "valor": valor,
        "categoria": categoria or "Sem categoria"
    }
    despesas.append(despesa)
    proximo_id += 1
    return despesa

def agrupar_por_categoria():
    grupos = {}
    for despesa in despesas:
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
    grupos = agrupar_por_categoria()
    if categoria_selecionada:
        grupos = [g for g in grupos if g["nome"] == categoria_selecionada]

    total = sum(d["valor"] for d in despesas)
    return render_template(
        'index.html',
        despesas=despesas,
        total=total,
        categorias=categorias_disponiveis,
        grupos=grupos,
        categoria_selecionada=categoria_selecionada
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

    if categoria == "Outros":
        categoria = dados.get("categoria_outra", "").strip() or "Outros"

    adicionar_despesa(descricao, valor, categoria)

    if request.is_json:
        return jsonify(despesas[-1]), 201

    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
