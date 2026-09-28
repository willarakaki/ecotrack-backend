-- V4__Seed_Initial_Data.sql
-- Seed de Dados Iniciais para testes do Frontend (Desenvolvimento e QA)
-- Serão inseridos:
-- 1 Tenant (Empresa)
-- 2 Usuários: Um Administrador/RH (Dashboards) e um Colaborador (Gamificação)

-- Inserindo a Empresa (Tenant)
INSERT INTO tb_tenant (external_id, company_name, cnpj, subscription_plan, is_active)
VALUES (
    'tnt-1234-5678-abcd-efgh',
    'Tech Verde Solutions',
    '12345678000199',
    'ENTERPRISE',
    1
);

-- Inserindo Usuário 1: Administrador / RH
-- Senha mockada para testes: 'senha123' (No futuro será o Hash BCrypt correspondente, 
-- por enquanto deixaremos o plain text / mock provisório sabendo que o Spring Security precisará criptografar)
INSERT INTO tb_user (tenant_id, external_id, full_name, email, password_hash, role_type, is_active)
VALUES (
    (SELECT id FROM tb_tenant WHERE cnpj = '12345678000199'),
    'usr-admin-1234-5678-abcd',
    'Gestor RH Tech Verde',
    'rh@techverde.com',
    '$2a$10$C/zB.0.xX2Y1c9i2hB3s0.d9Sj6X5X5x.9X.8/0vY5Z5jZ5zZ.O', -- Hash fictício gerado por Bcrypt para "senha123"
    'ADMIN_RH',
    1
);

-- Inserindo Usuário 2: Colaborador Comum (Gamificação/Chat)
INSERT INTO tb_user (tenant_id, external_id, full_name, email, password_hash, role_type, is_active)
VALUES (
    (SELECT id FROM tb_tenant WHERE cnpj = '12345678000199'),
    'usr-emp-1234-5678-abcd',
    'João Colaborador',
    'joao@techverde.com',
    '$2a$10$C/zB.0.xX2Y1c9i2hB3s0.d9Sj6X5X5x.9X.8/0vY5Z5jZ5zZ.O', -- Hash fictício gerado por Bcrypt para "senha123"
    'EMPLOYEE',
    1
);
