import os
import sqlite3
import psycopg2
from dotenv import load_dotenv

load_dotenv()

MODO = os.getenv("MODO", "DEV")

def conectar():
    if MODO == "PROD":
        return psycopg2.connect(
            host=os.getenv("DB_HOST"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            port=os.getenv("DB_PORT", 5432)
        )
    else:
        return sqlite3.connect("chamados.db")
