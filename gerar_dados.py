# backend/gerar_dados.py
import os
import sqlite3
import random
import datetime as dt

# Caminho robusto para o banco na mesma pasta deste arquivo
DB_PATH = os.path.join(os.path.dirname(__file__), "vendas.db")

# Catálogo simples de produtos com preço-base (em R$)
PRODUTOS = [
    ("Notebook Pro", 4500.00),
    ("Headset Gamer", 350.00),
    ("Mouse Wireless", 120.00),
    ("Teclado Mecânico", 280.00),
    ("Monitor 27\" 144Hz", 1800.00),
    ("Cadeira Ergonômica", 950.00),
    ("Webcam HD", 200.00),
    ("SSD 1TB", 520.00),
]

def criar_schema(con):
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,       -- formato ISO: YYYY-MM-DD
            produto TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            valor REAL NOT NULL
        )
    """)
    con.commit()

def zerar_tabela(con):
    # Limpa a tabela para evitar duplicação quando você repopular
    cur = con.cursor()
    cur.execute("DELETE FROM vendas")
    con.commit()

def sazonalidade(mes: int) -> float:
    # Mais vendas em novembro/dezembro, um pouco mais em junho/julho,
    # e um pouco menos em janeiro/fevereiro
    if mes in (11, 12):
        return 1.7
    if mes in (6, 7):
        return 1.2
    if mes in (1, 2):
        return 0.8
    return 1.0

def gerar_datas_aleatorias(inicio: dt.date, fim: dt.date, n: int):
    # Gera n datas uniformemente ao longo do intervalo
    dias = (fim - inicio).days
    for _ in range(n):
        offset = random.randint(0, dias)
        yield inicio + dt.timedelta(days=offset)

def gerar_registros(con, n=2500):
    cur = con.cursor()
    hoje = dt.date.today()
    inicio = dt.date(2015, 1, 1)

    for d in gerar_datas_aleatorias(inicio, hoje, n):
        produto, preco = random.choice(PRODUTOS)

        # Quantidade base com pesos (1 é mais comum)
        qtd_base = random.choices([1, 2, 3, 4, 5], weights=[50, 25, 12, 8, 5])[0]
        fator = sazonalidade(d.month)

        # Ajusta quantidade por sazonalidade + pequeno ruído
        qtd = max(1, int(round(qtd_base * fator + random.random())))

        # Valor com variação de ±10% em cima de (qtd * preço)
        valor = round(qtd * preco * (0.9 + random.random() * 0.2), 2)

        cur.execute(
            "INSERT INTO vendas (data, produto, quantidade, valor) VALUES (?,?,?,?)",
            (d.isoformat(), produto, qtd, valor),
        )

    con.commit()

if __name__ == "__main__":
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    try:
        criar_schema(con)
        zerar_tabela(con)
        gerar_registros(con, n=2500)
        con.execute("CREATE INDEX IF NOT EXISTS idx_vendas_data ON vendas(data)")
        con.commit()
        print("✅ Banco populado com vendas de 2015 até hoje em:", DB_PATH)
    finally:
        con.close()
