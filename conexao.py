import os
import psycopg2
from dotenv import load_dotenv

# Mesmo esquema de detecção de ambiente
env_file = ".env.dev" if os.getenv("MODO") == "DEV" else ".env"
load_dotenv(env_file)

def conectar():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        port=os.getenv("DB_PORT", 5432),
        sslmode=os.getenv("SSL_MODE", "require")
    )
