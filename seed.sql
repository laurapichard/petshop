-- ============================================================
-- PET SHOP AMIGO FIEL - Dados de teste (DML)
-- Execute após o schema.sql
-- ============================================================

INSERT INTO cliente (nome, telefone, email, endereco) VALUES
('Ana Maria Silva', '(82) 99881-1234', 'ana.silva@email.com', 'Rua das Flores, 105 - Centro'),
('Carlos Eduardo Souza', '(82) 99123-4567', 'carlos.souza@email.com', 'Av. Brasil, 450 - Bairro Novo'),
('Mariana Oliveira', '(82) 98765-4321', 'mariana.oliveira@email.com', 'Rua São Pedro, 88 - Jardim Petrópolis'),
('Roberto Alves Santos', '(82) 99332-1100', 'roberto.alves@email.com', 'Praça da Matriz, 12 - Centro'),
('Fernanda Costa', '(82) 98112-9988', 'fernanda.costa@email.com', 'Rua do Sol, 302 - Alto do Cruzeiro');

INSERT INTO pet (nome, especie, raca, data_nascimento, codigo_cliente) VALUES
('Thor', 'Cachorro', 'Labrador', '2021-03-15', 1),
('Mel', 'Gato', 'Persa', '2022-07-02', 1),
('Rex', 'Cachorro', 'Vira-lata', '2019-11-20', 2),
('Luna', 'Gato', 'Siamês', '2020-05-10', 3),
('Bidu', 'Cachorro', 'Poodle', '2023-01-08', 4),
('Nina', 'Cachorro', 'Shih Tzu', '2022-09-25', 5);

INSERT INTO funcionario (nome, cargo, telefone) VALUES
('João Pedro Ferreira', 'Tosador', '(82) 98877-6655'),
('Beatriz Lima Mendes', 'Atendente', '(82) 99988-7766'),
('Lucas Gabriel Santos', 'Veterinário', '(82) 98711-2233'),
('Camila Rodrigues', 'Gerente', '(82) 99654-3210');

INSERT INTO servico (nome, descricao, preco, duracao_minutos) VALUES
('Banho', 'Banho completo com produtos hipoalergênicos', 45.00, 40),
('Tosa Higiênica', 'Tosa das regiões íntimas, patas e focinho', 30.00, 25),
('Tosa Completa', 'Tosa completa do pelo conforme padrão da raça', 70.00, 60),
('Hidratação', 'Hidratação capilar para pelos ressecados', 35.00, 30),
('Corte de Unhas', 'Corte e lixamento das unhas', 15.00, 10),
('Consulta Veterinária', 'Avaliação clínica geral com veterinário', 90.00, 30);

INSERT INTO atendimento (numero_atendimento, data_atendimento, horario, valor_total, codigo_pet, codigo_funcionario) VALUES
(1, '2026-08-25', '09:00:00', 75.00, 1, 1),
(2, '2026-08-25', '10:30:00', 45.00, 2, 2),
(3, '2026-08-26', '14:00:00', 100.00, 3, 3),
(4, '2026-08-27', '11:15:00', 85.00, 4, 1),
(5, '2026-08-28', '16:00:00', 45.00, 5, 2),
(6, '2026-08-29', '09:30:00', 105.00, 6, 1);

INSERT INTO item_atendimento (numero_atendimento, codigo_servico, preco_praticado) VALUES
(1, 1, 45.00), (1, 5, 15.00), (1, 2, 15.00),
(2, 1, 45.00),
(3, 6, 90.00), (3, 5, 10.00),
(4, 1, 45.00), (4, 4, 35.00), (4, 5, 5.00),
(5, 1, 45.00),
(6, 3, 70.00), (6, 1, 35.00);

-- Ajusta as sequências, pois os IDs foram informados manualmente
SELECT setval(pg_get_serial_sequence('atendimento', 'numero_atendimento'), (SELECT MAX(numero_atendimento) FROM atendimento));
