-- ============================================================
-- PET SHOP AMIGO FIEL - DDL (PostgreSQL)
-- Convertido do modelo MySQL do projeto. A tabela USUARIO é
-- adicionada para permitir login no sistema.
-- Execute: psql -U postgres -d petshop_amigo_fiel -f schema.sql
-- ============================================================

DROP TABLE IF EXISTS item_atendimento, atendimento, usuario, funcionario, servico, pet, cliente CASCADE;

CREATE TABLE cliente (
    codigo_cliente SERIAL PRIMARY KEY,
    nome           VARCHAR(100) NOT NULL,
    telefone       VARCHAR(20),
    email          VARCHAR(100),
    endereco       VARCHAR(200)
);

CREATE TABLE pet (
    codigo_pet      SERIAL PRIMARY KEY,
    nome            VARCHAR(80) NOT NULL,
    especie         VARCHAR(30) NOT NULL,
    raca            VARCHAR(60),
    data_nascimento DATE,
    codigo_cliente  INT NOT NULL REFERENCES cliente (codigo_cliente)
                    ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE funcionario (
    codigo_funcionario SERIAL PRIMARY KEY,
    nome               VARCHAR(100) NOT NULL,
    cargo              VARCHAR(50) NOT NULL,
    telefone           VARCHAR(20)
);

-- Conta de acesso ao sistema, ligada a um funcionário
CREATE TABLE usuario (
    codigo_usuario     SERIAL PRIMARY KEY,
    login              VARCHAR(50) NOT NULL UNIQUE,
    senha_hash         VARCHAR(255) NOT NULL,
    codigo_funcionario INT NOT NULL UNIQUE REFERENCES funcionario (codigo_funcionario)
                       ON DELETE CASCADE
);

CREATE TABLE servico (
    codigo_servico  SERIAL PRIMARY KEY,
    nome            VARCHAR(100) NOT NULL,
    descricao       TEXT,
    preco           NUMERIC(10, 2) NOT NULL CHECK (preco >= 0),
    duracao_minutos INT NOT NULL DEFAULT 30 CHECK (duracao_minutos > 0)
);

CREATE TABLE atendimento (
    numero_atendimento SERIAL PRIMARY KEY,
    data_atendimento   DATE NOT NULL,
    horario            TIME NOT NULL,
    valor_total        NUMERIC(10, 2) NOT NULL DEFAULT 0.00 CHECK (valor_total >= 0),
    codigo_pet         INT NOT NULL REFERENCES pet (codigo_pet)
                       ON DELETE RESTRICT ON UPDATE CASCADE,
    codigo_funcionario INT NOT NULL REFERENCES funcionario (codigo_funcionario)
                       ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE item_atendimento (
    numero_atendimento INT NOT NULL REFERENCES atendimento (numero_atendimento)
                       ON DELETE CASCADE ON UPDATE CASCADE,
    codigo_servico     INT NOT NULL REFERENCES servico (codigo_servico)
                       ON DELETE RESTRICT ON UPDATE CASCADE,
    preco_praticado    NUMERIC(10, 2) NOT NULL CHECK (preco_praticado >= 0),
    PRIMARY KEY (numero_atendimento, codigo_servico)
);
