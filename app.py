import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, redirect, session, flash
from datetime import datetime
from functools import wraps
from flask import get_flashed_messages
from werkzeug.security import check_password_hash
from conexao import conectar

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "chave_padrao_insegura")

# --- MIDDLEWARES ---
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
        if "usuario" not in session or int(session.get("is_admin", 0)) != 1:
            return redirect("/dashboard")
        return f(*args, **kwargs)
    return decorated_function

# --- ROTAS ---
@app.route("/login", methods=["GET", "POST"])
def login():
    erro = None
    if request.method == "POST":
        usuario = request.form["usuario"]
        senha = request.form["senha"]

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT senha_hash, is_admin FROM usuarios WHERE usuario = %s", (usuario,))
        resultado = cursor.fetchone()
        conn.close()

        if resultado and check_password_hash(resultado[0], senha):
            session["usuario"] = usuario
            session["is_admin"] = int(resultado[1]) if resultado[1] is not None else 0
            return redirect("/") if session["is_admin"] == 1 else redirect("/dashboard")
        else:
            erro = "Usuário ou senha inválidos!"
    return render_template("login.html", erro=erro)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/")
@login_required
@admin_required
def home():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, responsavel_atendimento, data, cliente, empresa, status, relato, prioridade, origem, tipo_maquina, porta_ssh, tipo_acao, responsavel_acao, descricao_acao, horario
        FROM chamados
        WHERE status = 'Aberto'
        ORDER BY id DESC
        LIMIT 8
    """)
    chamados_abertos = [dict(zip((
        "id", "responsavel_atendimento", "data", "cliente", "empresa", "status",
        "relato", "prioridade", "origem", "tipo_maquina", "porta_ssh", "tipo_acao",
        "responsavel_acao", "descricao_acao", "horario"
    ), row)) for row in cursor.fetchall()]
    conn.close()
    return render_template("index.html", chamados_abertos=chamados_abertos)

@app.route("/novo", methods=["GET", "POST"])
@login_required
@admin_required
def criar_chamado():
    if request.method == "POST":
        campos = (
            "responsavel_atendimento", "data", "horario", "cliente", "empresa", "porta_ssh",
            "tipo_maquina", "relato", "prioridade", "origem", "tipo_acao",
            "responsavel_acao", "descricao_acao", "status"
        )
        dados = [request.form.get(c, "") or datetime.now().strftime("%d/%m/%Y" if c == "data" else "%H:%M" if c == "horario" else "") for c in campos]

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(f"""
            INSERT INTO chamados ({', '.join(campos)})
            VALUES ({', '.join(['%s'] * len(campos))})
        """, dados)
        conn.commit()
        conn.close()

        flash("Chamado aberto com sucesso!")
        return redirect("/")
    return render_template("criar_chamado.html")

@app.route("/editar/<int:id>", methods=["GET", "POST"])
@login_required
@admin_required
def editar_chamado(id):
    conn = conectar()
    cursor = conn.cursor()

    if request.method == "POST":
        campos = (
            "responsavel_atendimento", "data", "horario", "cliente", "empresa", "porta_ssh",
            "tipo_maquina", "relato", "prioridade", "origem", "tipo_acao",
            "responsavel_acao", "descricao_acao", "status"
        )
        dados = [request.form[c] for c in campos]
        dados.append(id)

        cursor.execute(f"""
            UPDATE chamados SET {', '.join(f"{c}=%s" for c in campos)} WHERE id=%s
        """, dados)

        conn.commit()
        conn.close()

        flash("Chamado atualizado com sucesso!")
        return redirect("/listar")

    cursor.execute("SELECT * FROM chamados WHERE id = %s", (id,))
    chamado = cursor.fetchone()
    conn.close()

    if not chamado:
        flash("Chamado não encontrado.")
        return redirect("/")

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
    filtros = {
        "status": request.args.get("status", "todos"),
        "empresa": request.args.get("empresa", "").strip(),
        "responsavel": request.args.get("responsavel", "").strip(),
        "cliente": request.args.get("cliente", "").strip(),
        "data_inicio": request.args.get("data_inicio", "").strip(),
        "data_fim": request.args.get("data_fim", "").strip()
    }

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM chamados")
    total_geral = cursor.fetchone()[0]

    sql = "SELECT id, responsavel_atendimento, data, cliente, empresa, status FROM chamados WHERE 1=1"
    params = []

    if filtros["status"] != "todos":
        sql += " AND status = %s"
        params.append(filtros["status"])
    if filtros["empresa"]:
        sql += " AND empresa ILIKE %s"
        params.append(f"%{filtros['empresa']}%")
    if filtros["responsavel"]:
        sql += " AND responsavel_atendimento ILIKE %s"
        params.append(f"%{filtros['responsavel']}%")
    if filtros["cliente"]:
        sql += " AND cliente ILIKE %s"
        params.append(f"%{filtros['cliente']}%")
    if filtros["data_inicio"]:
        sql += " AND data >= %s"
        params.append(filtros["data_inicio"])
    if filtros["data_fim"]:
        sql += " AND data <= %s"
        params.append(filtros["data_fim"])

    sql += " ORDER BY id DESC"
    cursor.execute(sql, params)
    chamados = [dict(zip(("id", "responsavel_atendimento", "data", "cliente", "empresa", "status"), row)) for row in cursor.fetchall()]
    conn.close()

    return render_template("lista_chamados.html", chamados=chamados, total_geral=total_geral, total_filtrados=len(chamados), **filtros)

@app.route('/excluir/<int:id>', methods=['POST'])
@login_required
@admin_required
def excluir_chamado(id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM chamados WHERE id = %s', (id,))
    conn.commit()
    conn.close()
    flash("Chamado excluído!")
    return redirect('/listar')

@app.route("/dashboard")
@login_required
def dashboard():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM chamados')
    total_chamados = cursor.fetchone()[0]

    cursor.execute('SELECT status, COUNT(*) FROM chamados GROUP BY status')
    chamados_por_status = {status: count for status, count in cursor.fetchall()}

    cursor.execute('SELECT prioridade, COUNT(*) FROM chamados GROUP BY prioridade')
    chamados_por_prioridade = {prioridade: count for prioridade, count in cursor.fetchall()}

    cursor.execute('SELECT empresa, COUNT(*) FROM chamados GROUP BY empresa ORDER BY COUNT(*) DESC LIMIT 5')
    chamados_por_empresa = {empresa: count for empresa, count in cursor.fetchall()}

    conn.close()
    return render_template("dashboard.html",
        total_chamados=total_chamados,
        chamados_por_status=chamados_por_status,
        chamados_por_prioridade=chamados_por_prioridade,
        chamados_por_empresa=chamados_por_empresa
    )

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
