import sqlite3
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

# Conexão com o SQLite local
sqlite_conn = sqlite3.connect("chamados.db")
sqlite_cursor = sqlite_conn.cursor()

# Conexão com o PostgreSQL da Railway
pg_conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASS"),
    port=os.getenv("DB_PORT")
)
pg_cursor = pg_conn.cursor()

# Criação da tabela no PostgreSQL (ajuste conforme sua estrutura real)
pg_cursor.execute("""
    CREATE TABLE IF NOT EXISTS chamados (
        id SERIAL PRIMARY KEY,
        responsavel_atendimento TEXT,
        data TEXT,
        horario TEXT,
        cliente TEXT,
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

# Buscar todos os registros do SQLite
sqlite_cursor.execute("SELECT * FROM chamados")
dados = sqlite_cursor.fetchall()

# Inserir os dados no PostgreSQL
for row in dados:
    pg_cursor.execute("""
        INSERT INTO chamados (
            id, responsavel_atendimento, data, horario, cliente, empresa,
            porta_ssh, tipo_maquina, relato, prioridade, origem,
            tipo_acao, responsavel_acao, descricao_acao, status
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, row)

# Finalizar
pg_conn.commit()
sqlite_conn.close()
pg_conn.close()

print("Migração concluída com sucesso!")
