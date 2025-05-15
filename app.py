from flask import Flask, render_template, request, redirect
from datetime import datetime

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        numero_chamado = request.form["numero_chamado"]
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

        # Garante data/hora automática se campos estiverem vazios
        if not data:
            data = datetime.now().strftime("%d/%m/%Y")
        if not horario:
            horario = datetime.now().strftime("%H:%M")

        with open("atendimentos.txt", "a", encoding="utf-8") as f:
            f.write(f"Número do Chamado: {numero_chamado}\n")
            f.write(f"Responsável pelo Atendimento: {responsavel_atendimento}\n")
            f.write(f"Data: {data}\n")
            f.write(f"Horário: {horario}\n")
            f.write(f"Cliente: {cliente}\n")
            f.write(f"Empresa: {empresa}\n")
            f.write(f"Porta SSH: {porta_ssh}\n")
            f.write(f"Tipo da Máquina: {tipo_maquina}\n")
            f.write(f"Relato/Solicitação: {relato}\n")
            f.write(f"Prioridade: {prioridade}\n")
            f.write(f"Origem do Caso: {origem}\n")
            f.write(f"Tipo de Ação: {tipo_acao}\n")
            f.write(f"Responsável pela Ação: {responsavel_acao}\n")
            f.write(f"Ação Realizada: {descricao_acao}\n")
            f.write(f"Status do Caso: {status}\n")
            f.write("-" * 60 + "\n\n")

        return redirect("/")  # redireciona após salvar

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
