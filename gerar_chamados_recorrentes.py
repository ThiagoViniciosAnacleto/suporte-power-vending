from datetime import date, timedelta
from conexao import conectar

def gerar_chamados_recorrentes():
    conn = conectar()
    cur = conn.cursor()

    hoje = date.today()

    # Buscar modelos recorrentes com execução para hoje
    cur.execute("""
        SELECT id, cliente, empresa, porta_ssh, tipo_maquina, relato,
               prioridade, origem, responsavel_atendimento,
               responsavel_acao, frequencia, proxima_execucao
        FROM chamados_recorrentes
        WHERE ativo = TRUE AND proxima_execucao = %s
    """, (hoje,))
    recorrentes = cur.fetchall()

    for r in recorrentes:
        (
            id_rec, cliente, empresa, porta_ssh, tipo_maquina, relato,
            prioridade, origem, responsavel_atend, responsavel_acao,
            frequencia, _  # ignoramos a data porque já usamos
        ) = r

        # Inserir novo chamado completo na tabela chamados
        cur.execute("""
            INSERT INTO chamados (
                responsavel_atendimento, data, horario,
                cliente, empresa, porta_ssh, tipo_maquina,
                relato, prioridade, origem, responsavel_acao,
                status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'Aberto')
        """, (
            responsavel_atend,
            hoje.strftime('%Y-%m-%d'),
            "00:01",  # horário padrão
            cliente,
            empresa,
            porta_ssh,
            tipo_maquina,
            relato,
            prioridade,
            origem,
            responsavel_acao
        ))

        # Calcular próxima data
        nova_data = hoje
        if frequencia == 'diaria':
            nova_data += timedelta(days=1)
        elif frequencia == 'semanal':
            nova_data += timedelta(weeks=1)
        elif frequencia == 'mensal':
            if hoje.month == 12:
                nova_data = hoje.replace(year=hoje.year + 1, month=1)
            else:
                nova_data = hoje.replace(month=hoje.month + 1)

        # Atualizar proxima_execucao
        cur.execute("""
            UPDATE chamados_recorrentes
            SET proxima_execucao = %s
            WHERE id = %s
        """, (nova_data, id_rec))

    conn.commit()
    cur.close()
    conn.close()
    print("Chamados recorrentes gerados com sucesso!")

# Execução direta (apenas se for rodado como script)
if __name__ == '__main__':
    gerar_chamados_recorrentes()
