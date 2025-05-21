import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, redirect, session, flash
from flask_socketio import SocketIO
from datetime import datetime
from functools import wraps
from flask import get_flashed_messages
from werkzeug.security import check_password_hash, generate_password_hash
from conexao import conectar
from pytz import timezone
from flask_wtf import CSRFProtect

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "chave_padrao_insegura")
csrf = CSRFProtect(app)
socketio = SocketIO(app, async_mode='eventlet')

def registrar_log(tipo, campo=None, valor_antigo=None, valor_novo=None, chamado_id=None):
    try:
        conn = conectar()
        cursor = conn.cursor()

        # Obter ID do usuário logado
        usuario_nome = session.get("usuario")
        cursor.execute("SELECT id FROM usuarios WHERE usuario = %s", (usuario_nome,))
        resultado = cursor.fetchone()
        usuario_id = resultado[0] if resultado else None

        # Gerar data/hora em horário de Brasília
        fuso_brasilia = timezone("America/Sao_Paulo")
        agora = datetime.now(fuso_brasilia).replace(tzinfo=None)

        # Gerar mensagem de texto legível
        if tipo == "comentario":
            acao = f"Comentário adicionado: {valor_novo}"
        elif campo and valor_antigo and valor_novo:
            acao = f"Alterou {campo} de \"{valor_antigo}\" para \"{valor_novo}\""
        elif tipo == "criado":
            acao = f"Criado chamado"
        elif tipo == "atribuicao":
            acao = f"Atribuído para {valor_novo}"
        else:
            acao = tipo.capitalize()

        # Inserir log estruturado
        cursor.execute("""
            INSERT INTO log_acoes (
                usuario_id, chamado_id, tipo, campo, valor_antigo, valor_novo, acao, data_hora
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            usuario_id, chamado_id, tipo, campo, valor_antigo, valor_novo, acao, agora
        ))

        conn.commit()

    except Exception as e:
        print(f"[ERRO] ao registrar log: {e}")
    finally:
        conn.close()

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

def tec_or_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "usuario" not in session or int(session.get("is_admin", 0)) not in (1, 2):
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

@app.route("/redefinir_senha", methods=["GET", "POST"])
def redefinir_senha():
    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        nova = request.form.get("nova_senha", "")
        confirmar = request.form.get("confirmar_senha", "")

        if not usuario or not nova or not confirmar:
            flash("Preencha todos os campos.")
            return redirect("/redefinir_senha")

        if nova != confirmar:
            flash("As senhas não coincidem.")
            return redirect("/redefinir_senha")

        nova_hash = generate_password_hash(nova, method="scrypt")

        try:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("UPDATE usuarios SET senha_hash = %s WHERE usuario = %s", (nova_hash, usuario))
            if cursor.rowcount == 0:
                flash("Usuário não encontrado.")
            else:
                conn.commit()
                flash("Senha redefinida com sucesso!")
        except Exception as e:
            conn.rollback()
            flash("Erro ao redefinir senha.")
            print(f"Erro: {e}")
        finally:
            conn.close()

        return redirect("/redefinir_senha")

    return render_template("redefinir_senha.html")

# --- NOVA ROTA: Cadastrar Usuário ---
@app.route("/cadastrar_usuario", methods=["GET", "POST"])
@login_required
@admin_required
def cadastrar_usuario():
    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        senha = request.form.get("senha", "")
        confirmar = request.form.get("confirmar_senha", "")
        is_admin = int(request.form.get("is_admin", 0))


        if not usuario or not senha or not confirmar:
            flash("Todos os campos são obrigatórios.")
            return redirect("/cadastrar_usuario")

        if senha != confirmar:
            flash("As senhas não coincidem.")
            return redirect("/cadastrar_usuario")

        senha_hash = generate_password_hash(senha, method="scrypt")

        try:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO usuarios (usuario, senha_hash, is_admin) VALUES (%s, %s, %s)", (usuario, senha_hash, is_admin))
            conn.commit()
            flash("Usuário cadastrado com sucesso!")
        except Exception as e:
            conn.rollback()
            flash("Erro ao cadastrar usuário. Talvez o nome já exista.")
            print(f"Erro: {e}")
        finally:
            conn.close()
        return redirect("/cadastrar_usuario")

    return render_template("cadastrar_usuario.html", titulo_pagina="Cadastro Usuário")

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

            if session["is_admin"] == 1:
                return redirect("/")
            elif session["is_admin"] == 2:
                return redirect("/")
            else:
                return redirect("/")
        else:
            erro = "Usuário ou senha inválidos!"

    return render_template("login.html", erro=erro)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/")
@login_required
def home():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, responsavel_atendimento, data, cliente, empresa, status, relato, prioridade, origem, tipo_maquina, porta_ssh, responsavel_acao, descricao_acao, horario
        FROM chamados
        WHERE status NOT IN ('Resolvido', 'Fechado', 'Arquivado')
        ORDER BY
            CASE prioridade
                WHEN 'Crítica' THEN 1
                WHEN 'Alta' THEN 2
                WHEN 'Média' THEN 3
                WHEN 'Baixa' THEN 4
            END,
            id DESC
        LIMIT 20
    """)

    chamados_abertos = [dict(zip((
        "id", "responsavel_atendimento", "data", "cliente", "empresa", "status",
        "relato", "prioridade", "origem", "tipo_maquina", "porta_ssh",
        "responsavel_acao", "descricao_acao", "horario"
    ), row)) for row in cursor.fetchall()]

    conn.close()
    return render_template("index.html", chamados_abertos=chamados_abertos, titulo_pagina="Chamados em andamento")

@app.route("/novo", methods=["GET", "POST"])
@login_required
@tec_or_admin_required
def criar_chamado():
    fuso_brasilia = timezone("America/Sao_Paulo")
    agora = datetime.now(fuso_brasilia)

    if request.method == "POST":
        campos = (
            "responsavel_atendimento", "data", "horario", "cliente", "empresa", "porta_ssh",
            "tipo_maquina", "relato", "prioridade", "origem",
            "responsavel_acao", "descricao_acao", "status"
        )
        dados = [request.form.get(c, "") or agora.strftime("%d/%m/%Y" if c == "data" else "%H:%M" if c == "horario" else "") for c in campos]

        try:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute(f"""
                INSERT INTO chamados ({', '.join(campos)})
                VALUES ({', '.join(['%s'] * len(campos))})
            """, dados)
            conn.commit()
            flash("Chamado aberto com sucesso!")
        except Exception as e:
            conn.rollback()
            flash("Erro ao criar chamado.")
            print(f"Erro ao inserir chamado: {e}")
        finally:
            conn.close()
        return redirect("/")

    # GET: carrega dados necessários para o formulário
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT nome FROM empresas ORDER BY nome")
    lista_empresas = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT modelo FROM maquinas ORDER BY modelo")
    lista_maquinas = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT usuario FROM usuarios WHERE is_admin IN (1, 2) ORDER BY usuario")
    lista_usuarios = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT nome FROM origens ORDER BY nome")
    lista_origens = [row[0] for row in cursor.fetchall()]

    conn.close()

    return render_template(
        "criar_chamado.html",
        usuario_logado=session.get("usuario"),
        data_atual=agora.strftime("%Y-%m-%d"),
        hora_atual=agora.strftime("%H:%M"),
        lista_empresas=lista_empresas,
        lista_maquinas=lista_maquinas,
        lista_usuarios=lista_usuarios,
        lista_origens=lista_origens,  # 👈 necessário para o select de origem
        titulo_pagina="Criar Chamado"
    )


@app.route("/editar/<int:id>", methods=["GET", "POST"])
@login_required
@tec_or_admin_required
def editar_chamado(id):
    conn = conectar()
    cursor = conn.cursor()

    if request.method == "POST":
        # Buscar dados antigos
        cursor.execute("SELECT * FROM chamados WHERE id = %s", (id,))
        dados_antigos = cursor.fetchone()
        campos_completos = [
            "id", "responsavel_atendimento", "data", "horario", "cliente", "empresa",
            "porta_ssh", "tipo_maquina", "relato", "prioridade", "origem", "responsavel_acao", "descricao_acao", "status"
        ]
        chamado_antigo = dict(zip(campos_completos, dados_antigos))

        # Preparar atualização
        campos = (
            "responsavel_atendimento", "data", "horario", "cliente", "empresa", "porta_ssh",
            "tipo_maquina", "relato", "prioridade", "origem",
            "responsavel_acao", "descricao_acao", "status"
        )

        # 🔒 Verificação: impedir finalização sem ação realizada
        status = request.form.get("status", "").strip()
        descricao_acao = request.form.get("descricao_acao", "").strip()
        if status in ["Fechado", "Resolvido"] and not descricao_acao:
            flash("Para finalizar um chamado, é obrigatório informar a ação realizada.")
            conn.close()
            return redirect(f"/editar/{id}")

        dados = [request.form[c] for c in campos]
        dados.append(id)

        cursor.execute(f"""
            UPDATE chamados SET {', '.join(f"{c}=%s" for c in campos)} WHERE id=%s
        """, dados)
        conn.commit()

        # Comparar alterações
        dados_novos = {campo: request.form[campo] for campo in campos}
        mudancas = []
        for campo in dados_novos:
            antigo = chamado_antigo[campo]
            novo = dados_novos[campo]
            if str(antigo) != str(novo):
                mudancas.append(f"{campo} ({antigo} → {novo})")

        if mudancas:
            for campo in dados_novos:
                antigo = chamado_antigo[campo]
                novo = dados_novos[campo]
                if str(antigo) != str(novo):
                    registrar_log(
                        tipo=campo,
                        campo=campo,
                        valor_antigo=str(antigo),
                        valor_novo=str(novo),
                        chamado_id=id
                    )
        else:
            registrar_log(
                tipo="edicao",
                campo=None,
                valor_antigo=None,
                valor_novo=None,
                chamado_id=id
            )
        conn.close()

        flash("Chamado atualizado com sucesso!")
        return redirect("/listar")

    # BLOCO GET
    cursor.execute("SELECT * FROM chamados WHERE id = %s", (id,))
    chamado = cursor.fetchone()

    if not chamado:
        conn.close()
        flash("Chamado não encontrado.")
        return redirect("/")

    campos = [
        "id", "responsavel_atendimento", "data", "horario", "cliente", "empresa",
        "porta_ssh", "tipo_maquina", "relato", "prioridade", "origem", "responsavel_acao", "descricao_acao", "status"
    ]
    chamado_dict = dict(zip(campos, chamado))

    # Buscar listas
    cursor.execute("SELECT nome FROM origens ORDER BY nome")
    lista_origens = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT nome FROM empresas ORDER BY nome")
    lista_empresas = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT modelo FROM maquinas ORDER BY modelo")
    lista_maquinas = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT usuario FROM usuarios ORDER BY usuario")
    lista_usuarios = [row[0] for row in cursor.fetchall()]

    cursor.execute("""
        SELECT log_acoes.acao, log_acoes.data_hora, usuarios.usuario
        FROM log_acoes
        JOIN usuarios ON log_acoes.usuario_id = usuarios.id
        WHERE log_acoes.chamado_id = %s
        ORDER BY log_acoes.data_hora DESC
    """, (id,))
    historico_logs = cursor.fetchall()

    conn.close()

    return render_template("editar_chamado.html",
                            chamado=chamado_dict,
                            lista_empresas=lista_empresas,
                            lista_origens=lista_origens,
                            lista_maquinas=lista_maquinas,
                            lista_usuarios=lista_usuarios,
                            historico_logs=historico_logs,
                            titulo_pagina="Editar Chamado")


@app.route("/historico/<int:id>")
@login_required
def historico_chamado(id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT tipo, campo, valor_antigo, valor_novo, acao, data_hora, usuarios.usuario
        FROM log_acoes
        JOIN usuarios ON log_acoes.usuario_id = usuarios.id
        WHERE log_acoes.chamado_id = %s
        ORDER BY log_acoes.data_hora DESC
    """, (id,))
    registros = cursor.fetchall()
    conn.close()

    logs = [
        (formatar_acao_log(tipo, campo, valor_antigo, valor_novo, acao), data_hora, usuario)
        for tipo, campo, valor_antigo, valor_novo, acao, data_hora, usuario in registros
    ]

    return render_template("historico_chamado.html", logs=logs, chamado_id=id, titulo_pagina=f"Histórico do Chamado #{id}")

# Dicionário de nomes legíveis para campos no log
NOMES_CAMPOS = {
    "horario": "o horário",
    "data": "a data",
    "status": "o status",
    "prioridade": "a prioridade",
    "descricao_acao": "a ação realizada",
    "origem": "a origem do problema",
    "relato": "o relato do cliente",
    "cliente": "o cliente",
    "responsavel_atendimento": "o responsável",
    "empresa": "a empresa",
    "porta_ssh": "a porta SSH",
    "tipo_maquina": "o tipo de máquina"
}

# Dicionário de ícones por campo
ICONE_CAMPO = {
    "prioridade": "📌",
    "status": "🔄",
    "descricao_acao": "🛠️",
    "origem": "🛠️",
    "relato": "📝",
    "cliente": "🧑",
    "empresa": "🏢",
    "porta_ssh": "🔐",
    "tipo_maquina": "⚙️",
    "responsavel_atendimento": "👷",
}

def formatar_acao_log(tipo, campo, valor_antigo, valor_novo, acao):
    nome_legivel = NOMES_CAMPOS.get(campo, campo)
    icone = ICONE_CAMPO.get(campo, "📋")

    if tipo == "prioridade":
        return f"📌 Alterou a prioridade de \"{valor_antigo}\" para \"{valor_novo}\""
    
    elif tipo == "status":
        return f"🔄 Alterou o status de \"{valor_antigo}\" para \"{valor_novo}\""

    elif tipo == "comentario":
        return f"📝 Comentário: \"{valor_novo}\""

    elif tipo == "atribuicao":
        return f"👤 Atribuído para {valor_novo}"

    elif tipo == "criado":
        return f"🆕 Chamado criado"

    # Fallback: usa nome legível do campo e ícone específico
    if valor_antigo and valor_novo:
        return f"{icone} Alterou {nome_legivel} de \"{valor_antigo}\" para \"{valor_novo}\""

    return f"{icone} {acao or 'Ação registrada'}"

@app.route("/listar")
@login_required
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

    return render_template("lista_chamados.html", titulo_pagina="Chamados", chamados=chamados, total_geral=total_geral, total_filtrados=len(chamados), **filtros)

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
        titulo_pagina="Dashboard",
        total_chamados=total_chamados,
        chamados_por_status=chamados_por_status,
        chamados_por_prioridade=chamados_por_prioridade,
        chamados_por_empresa=chamados_por_empresa
    )
    
@socketio.on('solicitar_atualizacao')
def atualizar_dashboard():
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
    
    socketio.emit('dashboard_update', {
    'total': total_chamados,
    'status': chamados_por_status,
    'prioridade': chamados_por_prioridade,
    'empresas': chamados_por_empresa
})

@app.route("/cadastrar_empresa", methods=["GET", "POST"])
@login_required
@tec_or_admin_required
def cadastrar_empresa():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        if nome:
            try:
                conn = conectar()
                cursor = conn.cursor()

                cursor.execute("SELECT id FROM empresas WHERE nome = %s", (nome,))
                if cursor.fetchone():
                    flash("Empresa já cadastrada!")
                    return redirect("/cadastrar_empresa")

                cursor.execute("INSERT INTO empresas (nome) VALUES (%s)", (nome,))
                conn.commit()
                flash("Empresa cadastrada com sucesso!")
            except Exception as e:
                conn.rollback()
                flash("Erro ao cadastrar empresa.")
                print(f"Erro: {e}")
            finally:
                conn.close()
        return redirect("/cadastrar_empresa")
    return render_template("cadastrar_empresa.html", titulo_pagina="Cadastrar Empresa")

@app.route("/cadastrar_maquina", methods=["GET", "POST"])
@login_required
@tec_or_admin_required
def cadastrar_maquina():
    if request.method == "POST":
        modelo = request.form.get("modelo", "").strip()
        if modelo:
            try:
                conn = conectar()
                cursor = conn.cursor()

                cursor.execute("SELECT id FROM maquinas WHERE modelo = %s", (modelo,))
                if cursor.fetchone():
                    flash("Máquina já cadastrada!")
                    return redirect("/cadastrar_maquina")

                cursor.execute("INSERT INTO maquinas (modelo) VALUES (%s)", (modelo,))
                conn.commit()
                flash("Máquina cadastrada com sucesso!")
            except Exception as e:
                conn.rollback()
                flash("Erro ao cadastrar máquina.")
                print(f"Erro: {e}")
            finally:
                conn.close()
        return redirect("/cadastrar_maquina")
    return render_template("cadastrar_maquina.html", titulo_pagina="Cadastrar Máquina")

# --- GERENCIAR USUÁRIOS ---
@app.route("/gerenciar_usuarios")
@login_required
@admin_required
def gerenciar_usuarios():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, usuario, is_admin FROM usuarios ORDER BY id")
    usuarios = [dict(zip(["id", "usuario", "is_admin"], row)) for row in cursor.fetchall()]
    conn.close()
    return render_template("alterar_privilegio.html", usuarios=usuarios, titulo_pagina="Gerenciar Usuários")

@app.route("/alterar_privilegio/<int:id>", methods=["POST"])
@login_required
@admin_required
def alterar_privilegio(id):
    novo_nivel = request.form.get("novo_nivel")
    if novo_nivel is None:
        flash("Privilégio inválido.")
        return redirect("/gerenciar_usuarios")

    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("UPDATE usuarios SET is_admin = %s WHERE id = %s", (int(novo_nivel), id))
        conn.commit()
        flash("Privilégio atualizado com sucesso!")
    except Exception as e:
        conn.rollback()
        flash("Erro ao atualizar privilégio.")
        print(f"Erro: {e}")
    finally:
        conn.close()

    return redirect("/gerenciar_usuarios")

if __name__ == "__main__":
    import eventlet
    import eventlet.wsgi
    socketio.run(app, debug=True, host="0.0.0.0", port=8080)