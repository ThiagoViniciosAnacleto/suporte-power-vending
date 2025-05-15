import sqlite3

conn = sqlite3.connect("chamados.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS chamados (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    responsavel_atendimento TEXT NOT NULL,
    data TEXT,
    horario TEXT,
    cliente TEXT NOT NULL,
    empresa TEXT,
    porta_ssh TEXT,
    tipo_maquina TEXT,
    relato TEXT,
    prioridade TEXT,
    origem TEXT,
    tipo_acao TEXT,
    responsavel_acao TEXT,
    descricao_acao TEXT,
    status TEXT
)
""")

conn.commit()
conn.close()
print("Tabela 'chamados' criada com sucesso.")
