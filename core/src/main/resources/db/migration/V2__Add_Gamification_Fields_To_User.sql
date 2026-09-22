-- V2: Adiciona campos de Gamification e Concorrência na tabela de Usuários

ALTER TABLE tb_user ADD eco_coins_balance NUMBER(19, 2) DEFAULT 0.0 NOT NULL;
ALTER TABLE tb_user ADD total_co2_saved NUMBER(19, 4) DEFAULT 0.0 NOT NULL;
ALTER TABLE tb_user ADD version NUMBER(19, 0) DEFAULT 0 NOT NULL;
