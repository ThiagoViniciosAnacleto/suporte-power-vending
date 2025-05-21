from datetime import date, timedelta
from conexao import conectar

def gerar_chamados_recorrentes():
    conn = conectar()
    cur = conn.cursor()

    hoje = date.today()
    print(f"🔍 Executando para data: {hoje}")

    # Busca os chamados recorrentes agendados para hoje
    cur.execute("""
        SELECT id, cliente, empresa, porta_ssh, tipo_maquina, relato,
               prioridade, origem, responsavel_atendimento,
               responsavel_acao, frequencia
        FROM chamados_recorrentes
        WHERE ativo = TRUE AND proxima_execucao = %s
    """, (hoje,))
    recorrentes = cur.fetchall()

    print(f"📋 Chamados recorrentes encontrados: {len(recorrentes)}")

    for r in recorrentes:
        (
            id_rec, cliente, empresa, porta_ssh, tipo_maquina, relato,
            prioridade, origem, responsavel_atend, responsavel_acao, frequencia
        ) = r

        # Criação do chamado automático
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
            "00:01",  # horário fixo para chamados automáticos
            cliente,
            empresa,
            porta_ssh,
            tipo_maquina,
            relato,
            prioridade,
            origem,
            responsavel_acao
        ))

        # Atualiza a próxima execução conforme a frequência
        if frequencia == 'diaria':
            nova_data = hoje + timedelta(days=1)
        elif frequencia == 'semanal':
            nova_data = hoje + timedelta(weeks=1)
        elif frequencia == 'mensal':
            nova_data = hoje.replace(day=1) + timedelta(days=32)
            nova_data = nova_data.replace(day=1)
        else:
            nova_data = hoje  # fallback de segurança

        cur.execute("""
            UPDATE chamados_recorrentes
            SET proxima_execucao = %s
            WHERE id = %s
        """, (nova_data, id_rec))

        print(f"✅ Chamado criado a partir do modelo ID {id_rec}, próxima execução em {nova_data}")

    conn.commit()
    cur.close()
    conn.close()
    print("🎉 Geração de chamados recorrentes concluída!")

# Executar manualmente
if __name__ == '__main__':
    gerar_chamados_recorrentes()
