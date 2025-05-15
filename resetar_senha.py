import sqlite3
from werkzeug.security import generate_password_hash

usuario = input("Qual usuário deseja redefinir a senha? ")
nova_senha = input("Digite a NOVA senha: ")

conn = sqlite3.connect("usuarios.db")
cursor = conn.cursor()
senha_hash = generate_password_hash(nova_senha)

cursor.execute("UPDATE usuarios SET senha_hash = ? WHERE usuario = ?", (senha_hash, usuario))
if cursor.rowcount == 0:
    print("Usuário não encontrado.")
else:
    print("Senha redefinida com sucesso!")

conn.commit()
conn.close()
