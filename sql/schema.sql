
-- Tabela: usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    usuario TEXT UNIQUE,
    senha_hash TEXT,
    is_admin INTEGER
);

-- Tabela: empresas
CREATE TABLE IF NOT EXISTS empresas (
    id SERIAL PRIMARY KEY,
    nome TEXT UNIQUE NOT NULL
);

-- Tabela: maquinas
CREATE TABLE IF NOT EXISTS maquinas (
    id SERIAL PRIMARY KEY,
    modelo TEXT UNIQUE NOT NULL
);

-- Tabela: origens_problema
CREATE TABLE IF NOT EXISTS origens_problema (
    id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    nome TEXT UNIQUE NOT NULL
);

-- Tabela: chamados
CREATE TABLE IF NOT EXISTS chamados (
    id SERIAL PRIMARY KEY,
    responsavel_atendimento TEXT,
    data TEXT,
    horario TEXT,
    cliente TEXT,
    empresa TEXT,
    porta_ssh TEXT,
    tipo_maquina TEXT,
    relato TEXT,
    prioridade TEXT,
    origem TEXT,
    responsavel_acao TEXT,
    descricao_acao TEXT,
    status TEXT
);

-- Tabela: chamados_recorrentes
CREATE TABLE IF NOT EXISTS chamados_recorrentes (
    id SERIAL PRIMARY KEY,
    cliente TEXT NOT NULL,
    empresa TEXT,
    porta_ssh TEXT,
    tipo_maquina TEXT,
    relato TEXT NOT NULL,
    prioridade TEXT,
    origem TEXT,
    responsavel_atendimento TEXT,
    responsavel_acao TEXT,
    descricao_acao TEXT,
    frequencia TEXT CHECK (frequencia = ANY (ARRAY['diaria', 'semanal', 'mensal'])),
    proxima_execucao DATE NOT NULL,
    ativo BOOLEAN DEFAULT true
);

-- Tabela: log_acoes
CREATE TABLE IF NOT EXISTS log_acoes (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER,
    acao TEXT NOT NULL,
    chamado_id INTEGER,
    data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tipo TEXT,
    campo TEXT,
    valor_antigo TEXT,
    valor_novo TEXT,
    CONSTRAINT log_acoes_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);
