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

@app.route("/editar/<int:id>", methods=["GET", "POST"])
@login_required
@admin_required
def editar_chamado(id):
    conn = sqlite3.connect("chamados.db")
    cursor = conn.cursor()

    if request.method == "POST":
        responsavel_atendimento = request.form["responsavel_atendimento"]
        data = request.form["data"]
        horario = request.form["horario"]
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

        cursor.execute("""
            UPDATE chamados SET
                responsavel_atendimento=?, data=?, horario=?, cliente=?, empresa=?,
                porta_ssh=?, tipo_maquina=?, relato=?, prioridade=?, origem=?,
                tipo_acao=?, responsavel_acao=?, descricao_acao=?, status=?
            WHERE id=?
        """, (
            responsavel_atendimento, data, horario, cliente, empresa,
            porta_ssh, tipo_maquina, relato, prioridade, origem,
            tipo_acao, responsavel_acao, descricao_acao, status, id
        ))

        conn.commit()
        conn.close()

        flash("Chamado atualizado com sucesso!")
        return redirect("/")

    # Método GET: buscar chamado pelo ID
    cursor.execute("SELECT * FROM chamados WHERE id = ?", (id,))
    chamado = cursor.fetchone()
    conn.close()

    if not chamado:
        flash("Chamado não encontrado.")
        return redirect("/")

    # Mapear os campos da tupla para nomes do formulário
    campos = [
        "id", "responsavel_atendimento", "data", "horario", "cliente", "empresa",
        "porta_ssh", "tipo_maquina", "relato", "prioridade", "origem",
        "tipo_acao", "responsavel_acao", "descricao_acao", "status"
    ]
    chamado_dict = dict(zip(campos, chamado))

    return render_template("editar_chamado.html", chamado=chamado_dict)

@app.route("/listar")
@login_required
@admin_required
def listar_chamados():
    status_filtro = request.args.get("status", "todos")
    empresa_filtro = request.args.get("empresa", "").strip()

    conn = sqlite3.connect("chamados.db")
    cursor = conn.cursor()

    sql = "SELECT id, responsavel_atendimento, data, cliente, empresa, status FROM chamados WHERE 1=1"
    params = []

    # Filtro de status
    if status_filtro != "todos":
        sql += " AND status = ?"
        params.append(status_filtro)

    # Filtro de empresa
    if empresa_filtro:
        sql += " AND empresa LIKE ?"
        params.append(f"%{empresa_filtro}%")

    sql += " ORDER BY id DESC"

    cursor.execute(sql, params)
    chamados = [
        dict(
            id=row[0],
            responsavel_atendimento=row[1],
            data=row[2],
            cliente=row[3],
            empresa=row[4],
            status=row[5]
        )
        for row in cursor.fetchall()
    ]
    conn.close()
    return render_template("lista_chamados.html", chamados=chamados, status_filtro=status_filtro, empresa_filtro=empresa_filtro)



# Dashboard: todos usuários logados podem acessar
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

if __name__ == "__main__":
    app.run(debug=True)
