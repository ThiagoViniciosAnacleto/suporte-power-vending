import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

def autenticar_master(usuario, senha):
    conn = sqlite3.connect("usuarios.db")
    cursor = conn.cursor()
    cursor.execute("SELECT senha_hash, is_admin FROM usuarios WHERE usuario = ?", (usuario,))
    resultado = cursor.fetchone()
    conn.close()
    if resultado and resultado[1] == 1:
        return check_password_hash(resultado[0], senha)
    return False

print("=== AUTENTICAÇÃO DO ADMINISTRADOR ===")
usuario_master = input("Usuário do administrador: ")
senha_master = input("Senha do administrador: ")

if not autenticar_master(usuario_master, senha_master):
    print("Acesso negado. Você não tem permissão para cadastrar usuários.")
    exit()

print("\n=== CADASTRO DE NOVO USUÁRIO ===")
usuario = input("Novo usuário: ")
senha = input("Senha do novo usuário: ")
is_admin = input("Este usuário será administrador? (s/n): ").strip().lower() == "s"

conn = sqlite3.connect("usuarios.db")
cursor = conn.cursor()
senha_hash = generate_password_hash(senha)

try:
    cursor.execute(
        "INSERT INTO usuarios (usuario, senha_hash, is_admin) VALUES (?, ?, ?)",
        (usuario, senha_hash, int(is_admin))
    )
    print(f"Usuário '{usuario}' criado com sucesso! (Admin: {is_admin})")
except sqlite3.IntegrityError:
    print("Usuário já existe!")

conn.commit()
conn.close()
