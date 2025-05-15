from flask import Flask, render_template, request, redirect, session
from datetime import datetime
from functools import wraps
from flask import flash, get_flashed_messages
import sqlite3
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.secret_key = "suporte2025"

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "usuario" not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # is_admin pode vir como int (1) ou str ('1')
        if "usuario" not in session or int(session.get("is_admin", 0)) != 1:
            return redirect("/dashboard")
        return f(*args, **kwargs)
    return decorated_function

@app.route("/login", methods=["GET", "POST"])
def login():
    erro = None
    if request.method == "POST":
        usuario = request.form["usuario"]
        senha = request.form["senha"]

        conn = sqlite3.connect("usuarios.db")
        cursor = conn.cursor()
        cursor.execute("SELECT senha_hash, is_admin FROM usuarios WHERE usuario = ?", (usuario,))
        resultado = cursor.fetchone()
        conn.close()

        if resultado and check_password_hash(resultado[0], senha):
            session["usuario"] = usuario
            # Garante que sempre armazene int (e não bytes ou string)
            session["is_admin"] = int(resultado[1]) if resultado[1] is not None else 0
            # Redireciona para home (admin) ou dashboard (user comum)
            if session["is_admin"] == 1:
                return redirect("/")
            else:
                return redirect("/dashboard")
        else:
            erro = "Usuário ou senha inválidos!"
    return render_template("login.html", erro=erro)

@app.route("/logout")
def logout():
    session.pop("usuario", None)
    session.pop("is_admin", None)
    return redirect("/login")

# Home (menu/admin): só para admin
@app.route("/")
@login_required
@admin_required
def home():
    return render_template("index.html")

# Criar chamado: só para admin
@app.route("/novo", methods=["GET", "POST"])
@login_required
@admin_required
def criar_chamado():
    if request.method == "POST":
        responsavel_atendimento = request.form["responsavel_atendimento"]
        data = request.form["data"] or datetime.now().strftime("%d/%m/%Y")
        horario = request.form["horario"] or datetime.now().strftime("%H:%M")
        cliente = request.form["cliente"]
        empresa = request.form["empresa"]
        porta_ssh = request.form["porta_ssh"]
        tipo_maquina = request.form["tipo_maquina"]
        relato = request.form["relato"]
        prioridade = request.form["prioridade"]
        origem = request.form["origem"]
        tipo_acao = request.form["tipo_acao"]
        responsavel_acao = request.form["responsavel_acao"]
        descricao_acao = request.form["descricao_acao"]
        status = request.form["status"]

        conn = sqlite3.connect("chamados.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO chamados (
                responsavel_atendimento, data, horario, cliente, empresa,
                porta_ssh, tipo_maquina, relato, prioridade, origem,
                tipo_acao, responsavel_acao, descricao_acao, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            responsavel_atendimento, data, horario, cliente, empresa,
            porta_ssh, tipo_maquina, relato, prioridade, origem,
            tipo_acao, responsavel_acao, descricao_acao, status
        ))
        conn.commit()
        conn.close()

        flash("Chamado aberto com sucesso!")
        return redirect("/")
    return render_template("criar_chamado.html")


# Dashboard: todos usuários logados podem acessar
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

if __name__ == "__main__":
    app.run(debug=True)
