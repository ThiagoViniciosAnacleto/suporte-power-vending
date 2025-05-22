-- Popular empresas
INSERT INTO empresas (nome) VALUES
('Cenci'),
('Nortel'),
('Horsch'),
('Seco Tools'),
('2S'),
('Frontiere'),
('Nexeed do Brasil'),
('Dimensional'),
('Time Machine'),
('Wurth'),
('TKK'),
('Escola Moranguinho'),
('Jor Machines'),
('Usiminas'),
('Mazaj'),
('Wtec'),
('Hinty'),
('Sayerlack'),
('Light Food'),
('Redumax'),
('AutoSupply'),
('Scania'),
('CTC'),
('WonderBox'),
('Hexion'),
('ProntoLight'),
('Agco'),
('Selaria Faísca'),
('Procoat'),
('Liberty Telecom'),
('Sandra Queiroz'),
('Neobetel'),
('Fardas Uniformes')
ON CONFLICT (nome) DO NOTHING;

-- Popular máquinas
INSERT INTO maquinas (modelo) VALUES
('Storage'),
('Stockage'),
('Carrossel'),
('Smart Slim'),
('Locker')
ON CONFLICT (modelo) DO NOTHING;

-- Popular origens do problema
INSERT INTO origens_problema (nome) VALUES
('Eletrônico'),
('Rede'),
('Instalação'),
('Sistema Storage'),
('Sistema Externo'),
('Sistema Slim'),
('Sistema Embarcado'),
('Comercial'),
('Mecânico'),
('Refrigeração'),
('Elétrico'),
('Stone'),
('Outros')
ON CONFLICT (nome) DO NOTHING;
