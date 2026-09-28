-- V6__Seed_Gamification_Data.sql
-- Inserindo os dados de Mock exatos solicitados pelo Frontend para testes de UI

-- 1. Tenant (EcoCorp S.A.)
INSERT INTO tb_tenant (external_id, company_name, cnpj, subscription_plan, is_active, total_carbon_saved)
VALUES ('tnt-eco-corp-1234', 'EcoCorp S.A.', '98765432000199', 'ENTERPRISE', 1, 1.4);

-- 2. Departamentos
INSERT INTO tb_department (tenant_id, name) VALUES ((SELECT id FROM tb_tenant WHERE cnpj = '98765432000199'), 'Engenharia de Software');
INSERT INTO tb_department (tenant_id, name) VALUES ((SELECT id FROM tb_tenant WHERE cnpj = '98765432000199'), 'Marketing');
INSERT INTO tb_department (tenant_id, name) VALUES ((SELECT id FROM tb_tenant WHERE cnpj = '98765432000199'), 'Recursos Humanos');
INSERT INTO tb_department (tenant_id, name) VALUES ((SELECT id FROM tb_tenant WHERE cnpj = '98765432000199'), 'Comercial');

-- 3. Usuários (Com Hash de Senha Mock 'senha123')
-- Willian Arakaki (Você)
INSERT INTO tb_user (tenant_id, external_id, full_name, email, password_hash, role_type, is_active, department_id, eco_coins_balance, total_co2_saved, streak_days, user_level)
VALUES (
    (SELECT id FROM tb_tenant WHERE cnpj = '98765432000199'),
    'usr-will-1234',
    'Willian Arakaki',
    'willian.arakaki@empresa.com.br',
    '$2a$10$C/zB.0.xX2Y1c9i2hB3s0.d9Sj6X5X5x.9X.8/0vY5Z5jZ5zZ.O',
    'ADMIN_RH',
    1,
    (SELECT id FROM tb_department WHERE name = 'Engenharia de Software' AND tenant_id = (SELECT id FROM tb_tenant WHERE cnpj = '98765432000199')),
    1495.0,
    24.5,
    12,
    2
);

-- João Silva
INSERT INTO tb_user (tenant_id, external_id, full_name, email, password_hash, role_type, is_active, department_id, eco_coins_balance)
VALUES (
    (SELECT id FROM tb_tenant WHERE cnpj = '98765432000199'),
    'usr-joao-1234',
    'João Silva',
    'joao.silva@empresa.com.br',
    '$2a$10$C/zB.0.xX2Y1c9i2hB3s0.d9Sj6X5X5x.9X.8/0vY5Z5jZ5zZ.O',
    'EMPLOYEE',
    1,
    (SELECT id FROM tb_department WHERE name = 'Marketing' AND tenant_id = (SELECT id FROM tb_tenant WHERE cnpj = '98765432000199')),
    320.0
);

-- Maria Souza
INSERT INTO tb_user (tenant_id, external_id, full_name, email, password_hash, role_type, is_active, department_id, eco_coins_balance)
VALUES (
    (SELECT id FROM tb_tenant WHERE cnpj = '98765432000199'),
    'usr-maria-1234',
    'Maria Souza',
    'maria.souza@empresa.com.br',
    '$2a$10$C/zB.0.xX2Y1c9i2hB3s0.d9Sj6X5X5x.9X.8/0vY5Z5jZ5zZ.O',
    'EMPLOYEE',
    1,
    (SELECT id FROM tb_department WHERE name = 'Recursos Humanos' AND tenant_id = (SELECT id FROM tb_tenant WHERE cnpj = '98765432000199')),
    850.0
);

-- 4. Medalhas (Badges)
INSERT INTO tb_badge (name, description, icon_url) VALUES ('Estrela ESG', 'Destacou-se em ações ambientais', '/assets/badges/estrela-esg.png');
INSERT INTO tb_badge (name, description, icon_url) VALUES ('10 Dias de Fogo', 'Manteve ofensiva de 10 dias consecutivos', '/assets/badges/10-dias-fogo.png');

-- Atribuindo Medalhas ao Willian
INSERT INTO tb_user_badge (user_id, badge_id)
VALUES (
    (SELECT id FROM tb_user WHERE email = 'willian.arakaki@empresa.com.br'),
    (SELECT id FROM tb_badge WHERE name = 'Estrela ESG')
);

INSERT INTO tb_user_badge (user_id, badge_id)
VALUES (
    (SELECT id FROM tb_user WHERE email = 'willian.arakaki@empresa.com.br'),
    (SELECT id FROM tb_badge WHERE name = '10 Dias de Fogo')
);

-- 5. Catálogo do Marketplace (Rewards)
INSERT INTO tb_reward (tenant_id, title, cost_points, is_active) VALUES ((SELECT id FROM tb_tenant WHERE cnpj = '98765432000199'), 'Cupom iFood R$30', 1500.0, 1);
INSERT INTO tb_reward (tenant_id, title, cost_points, is_active) VALUES ((SELECT id FROM tb_tenant WHERE cnpj = '98765432000199'), 'Ingresso Cinemark', 3000.0, 1);
INSERT INTO tb_reward (tenant_id, title, cost_points, is_active) VALUES ((SELECT id FROM tb_tenant WHERE cnpj = '98765432000199'), 'Day-Pass WeWork', 5000.0, 1);
INSERT INTO tb_reward (tenant_id, title, cost_points, is_active) VALUES ((SELECT id FROM tb_tenant WHERE cnpj = '98765432000199'), '1 Day-Off (Folga)', 15000.0, 1);

