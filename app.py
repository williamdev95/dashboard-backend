# backend/app.py
from flask import Flask, jsonify, request
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Permite que o frontend acesse o backend

# --------------------------
# Conexão com o banco
# --------------------------
def conectar_banco():
    return sqlite3.connect("vendas.db")

# --------------------------
# Rota: listar todas as vendas
# --------------------------
@app.route("/vendas", methods=["GET"])
def listar_vendas():
    con = conectar_banco()
    cur = con.cursor()
    cur.execute("SELECT * FROM vendas ORDER BY data DESC")
    vendas = cur.fetchall()
    con.close()

    vendas_json = []
    for venda in vendas:
        vendas_json.append({
            "id": venda[0],
            "data": venda[1],      # agora temos datas
            "produto": venda[2],
            "quantidade": venda[3],
            "valor": venda[4]
        })
    return jsonify({"status": "sucesso", "dados": vendas_json})

# --------------------------
# Rota: total de vendas por produto
# --------------------------
@app.route("/total_por_produto", methods=["GET"])
def total_por_produto():
    con = conectar_banco()
    cur = con.cursor()
    cur.execute("""
        SELECT produto, SUM(valor) as total
        FROM vendas
        GROUP BY produto
    """)
    resultados = cur.fetchall()
    con.close()

    dados = [{"produto": r[0], "total": r[1]} for r in resultados]
    return jsonify(dados)
# --------------------------
# Rota para filtrar vendas por período
# --------------------------
@app.route("/filtro", methods=["GET"])
def filtro():
    from flask import request  # garante que o request esteja disponível

    inicio = request.args.get("inicio")  # esperado YYYY-MM-DD
    fim = request.args.get("fim")        # esperado YYYY-MM-DD

    con = conectar_banco()
    cur = con.cursor()
    cur.execute("""
        SELECT * FROM vendas
        WHERE date(data) BETWEEN date(?) AND date(?)
        ORDER BY date(data) DESC
    """, (inicio, fim))
    vendas = cur.fetchall()
    con.close()

    vendas_json = [{
        "id": v[0],
        "data": v[1],
        "produto": v[2],
        "quantidade": v[3],
        "valor": v[4]
    } for v in vendas]

    return jsonify({"status": "sucesso", "dados": vendas_json})
# --------------------------
# Rota: resumo geral
# --------------------------
@app.route("/resumo", methods=["GET"])
def resumo():
    con = conectar_banco()
    cur = con.cursor()

    # Total de vendas
    cur.execute("SELECT COUNT(*) FROM vendas")
    total_vendas = cur.fetchone()[0]

    # Produtos distintos
    cur.execute("SELECT COUNT(DISTINCT produto) FROM vendas")
    produtos = cur.fetchone()[0]

    # Receita total
    cur.execute("SELECT SUM(valor) FROM vendas")
    receita = cur.fetchone()[0] or 0

    con.close()

    return jsonify({
        "total_vendas": total_vendas,
        "produtos": produtos,
        "receita": receita
    })

# --------------------------
# Rota: vendas por período (filtro de datas)
# --------------------------
@app.route("/vendas/periodo", methods=["GET"])
def vendas_por_periodo():
    data_inicio = request.args.get("inicio")
    data_fim = request.args.get("fim")

    con = conectar_banco()
    cur = con.cursor()
    cur.execute("""
        SELECT * FROM vendas
        WHERE date(data) BETWEEN date(?) AND date(?)
    """, (data_inicio, data_fim))
    vendas = cur.fetchall()
    con.close()

    vendas_json = []
    for venda in vendas:
        vendas_json.append({
            "id": venda[0],
            "data": venda[1],
            "produto": venda[2],
            "quantidade": venda[3],
            "valor": venda[4]
        })
    return jsonify({"status": "sucesso", "dados": vendas_json})
@app.route("/")
def home():
    return "Backend funcionando!"


# --------------------------
# Inicialização do servidor
# --------------------------
if __name__ == "__main__":
    app.run(debug=True)