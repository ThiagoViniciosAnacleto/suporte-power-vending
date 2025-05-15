import sqlite3

usuario = input("Digite o nome do usuário para tornar admin: ")

conn = sqlite3.connect("usuarios.db")
cursor = conn.cursor()
cursor.execute("UPDATE usuarios SET is_admin = 1 WHERE usuario = ?", (usuario,))
if cursor.rowcount == 0:
    print("Usuário não encontrado.")
else:
    print(f"Usuário '{usuario}' agora é administrador.")
conn.commit()
conn.close()
