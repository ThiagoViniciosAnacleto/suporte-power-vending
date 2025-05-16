import sqlite3
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# Conexão com os bancos SQLite
sqlite_usuarios = sqlite3.connect("usuarios.db")
sqlite_chamados = sqlite3.connect("chamados.db")

cursor_u = sqlite_usuarios.cursor()
cursor_c = sqlite_chamados.cursor()

# Conexão com o PostgreSQL
postgres = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASS"),
    port=os.getenv("DB_PORT")
)
pg = postgres.cursor()

# Criação das tabelas no PostgreSQL
pg.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    usuario TEXT,
    senha_hash TEXT,
    is_admin INTEGER
);
""")

pg.execute("""
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
);
""")

# Limpa dados anteriores para evitar duplicação
pg.execute("DELETE FROM usuarios")
pg.execute("DELETE FROM chamados")

# Inserir usuários
cursor_u.execute("SELECT usuario, senha_hash, is_admin FROM usuarios")
for row in cursor_u.fetchall():
    pg.execute("INSERT INTO usuarios (usuario, senha_hash, is_admin) VALUES (%s, %s, %s)", row)

# Inserir chamados (ignorando o ID do SQLite e deixando o PostgreSQL gerar um novo)
cursor_c.execute("SELECT * FROM chamados")
for row in cursor_c.fetchall():
    pg.execute("""
        INSERT INTO chamados (
            responsavel_atendimento, data, horario, cliente, empresa,
            porta_ssh, tipo_maquina, relato, prioridade, origem,
            tipo_acao, responsavel_acao, descricao_acao, status
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, row[1:])  # Pula o ID (index 0)

postgres.commit()
postgres.close()
sqlite_usuarios.close()
sqlite_chamados.close()

print("✅ Migração concluída com sucesso.")
