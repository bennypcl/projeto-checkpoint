-- ===================================================================
-- SCRIPT DE CRIAÇÃO DO BANCO DE DADOS CHECKPOINT (VERSÃO FINAL)
-- Este script cria o banco de dados e suas tabelas em seu estado final.
-- ===================================================================

-- Passo 1: Apaga o banco de dados antigo (se existir) e cria um novo.
DROP DATABASE IF EXISTS CHECKPOINT;
CREATE DATABASE CHECKPOINT;
USE CHECKPOINT;

-- ===================================================================
-- SEÇÃO 1: CRIAÇÃO DAS TABELAS
-- As tabelas são criadas em uma ordem que respeita as dependências
-- de chaves estrangeiras.
-- ===================================================================

-- Tabela de Usuários (Funcionários)
CREATE TABLE usuarios (
    usu_id INT AUTO_INCREMENT PRIMARY KEY,
    usu_cargo ENUM('Gerente', 'Vendedor(a)') NOT NULL,
    usu_nome VARCHAR(100) NOT NULL,
    usu_cpf CHAR(11) UNIQUE NOT NULL
);

-- Tabela de Clientes
CREATE TABLE clientes (
    cli_id INT AUTO_INCREMENT PRIMARY KEY,
    cli_cpf CHAR(11) UNIQUE NOT NULL,
    cli_nome VARCHAR(100) NOT NULL,
    cli_data_nascimento DATE,
    cli_email VARCHAR(100) UNIQUE,
    cli_ddd CHAR(2),
    cli_telefone VARCHAR(9),
    cli_cep CHAR(8),
    cli_rua VARCHAR(255),
    cli_bairro VARCHAR(150),
    cli_numero VARCHAR(10),
    cli_complemento VARCHAR(255),
    cli_uf CHAR(2),
    cli_cidade VARCHAR(100),
    cli_data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Produtos (versão final consolidada)
CREATE TABLE produtos (
    pro_id INT AUTO_INCREMENT PRIMARY KEY,
    pro_ref VARCHAR(50) NOT NULL,
    pro_sku VARCHAR(50) NULL,
    pro_descricao VARCHAR(255) NOT NULL,
    pro_tam VARCHAR(50) NULL,
    pro_bipe VARCHAR(50) NULL UNIQUE,
    pro_valor DECIMAL(10,2) NULL,
    pro_caminho_imagem VARCHAR(255)
);

-- Tabela de Pedidos (versão final consolidada)
CREATE TABLE pedidos (
    ped_id INT AUTO_INCREMENT PRIMARY KEY,
    cli_id INT,
    ped_data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ped_total DECIMAL(10,2) NOT NULL,
    usu_id INT NOT NULL,
    ped_desconto_info VARCHAR(50),
    FOREIGN KEY (cli_id) REFERENCES clientes(cli_id) ON DELETE SET NULL,
    FOREIGN KEY (usu_id) REFERENCES usuarios(usu_id)
);

-- Tabela de Itens do Pedido
CREATE TABLE itens_pedido (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    ped_id INT NOT NULL,
    pro_id INT NOT NULL,
    item_quant INT NOT NULL,
    item_valor_unitario DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (ped_id) REFERENCES pedidos(ped_id) ON DELETE CASCADE,
    FOREIGN KEY (pro_id) REFERENCES produtos(pro_id)
);

-- Tabela de Pagamentos (Registro Geral)
CREATE TABLE pagamentos (
    pag_id INT AUTO_INCREMENT PRIMARY KEY,
    ped_id INT NOT NULL,
    pag_metodo ENUM('Débito', 'Crédito', 'Pix', 'Dinheiro') NOT NULL,
    pag_valor DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (ped_id) REFERENCES pedidos(ped_id) ON DELETE CASCADE
);

-- Tabelas para os tipos de pagamento
CREATE TABLE debito (
    pag_id INT PRIMARY KEY,
    deb_tipo_cartao ENUM('Visa', 'Mastercard', 'Elo', 'American Express', 'Outro') NOT NULL,
    FOREIGN KEY (pag_id) REFERENCES pagamentos(pag_id) ON DELETE CASCADE
);

CREATE TABLE credito (
    pag_id INT PRIMARY KEY,
    cre_tipo_cartao ENUM('Visa', 'Mastercard', 'Elo', 'American Express', 'Outro') NOT NULL,
    cre_parcelas INT CHECK (cre_parcelas BETWEEN 1 AND 6) NOT NULL,
    FOREIGN KEY (pag_id) REFERENCES pagamentos(pag_id) ON DELETE CASCADE
);

CREATE TABLE pix (
    pag_id INT PRIMARY KEY,
    pix_chave VARCHAR(255) NOT NULL,
    FOREIGN KEY (pag_id) REFERENCES pagamentos(pag_id) ON DELETE CASCADE
);

CREATE TABLE dinheiro (
    pag_id INT PRIMARY KEY,
    din_troco DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (pag_id) REFERENCES pagamentos(pag_id) ON DELETE CASCADE
);

-- Tabela de Temas
CREATE TABLE temas (
    tema_id INT AUTO_INCREMENT PRIMARY KEY,
    tema_nome VARCHAR(100) NOT NULL,
    valor VARCHAR(55)
);

-- Tabela Mestre de Inventários
CREATE TABLE inventarios (
    inv_id INT AUTO_INCREMENT PRIMARY KEY,
    inv_data_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    inv_data_finalizacao TIMESTAMP NULL,
    inv_status ENUM('Em Andamento', 'Finalizado', 'Cancelado') NOT NULL
);

-- Tabela de Itens de Inventário (versão final consolidada)
CREATE TABLE inventario_itens (
    item_inv_id INT AUTO_INCREMENT PRIMARY KEY,
    inv_id INT NOT NULL,
    pro_id INT NULL,
    quantidade_sistema INT NOT NULL,
    quantidade_contada INT,
    item_sku VARCHAR(255),
    item_ref VARCHAR(255),
    item_descricao VARCHAR(255),
    item_tam VARCHAR(255),
    item_valor DECIMAL(10,2),
    FOREIGN KEY (inv_id) REFERENCES inventarios(inv_id) ON DELETE CASCADE,
    FOREIGN KEY (pro_id) REFERENCES produtos(pro_id)
);

-- ===================================================================
-- SEÇÃO 2: INSERÇÃO DE DADOS INICIAIS E PADRÕES
-- ===================================================================

-- Inserção de temas padrão
INSERT INTO temas (tema_nome, valor) VALUES
('united', 'escuro'),
('solar', 'claro');

-- Inserção de funcionárias
INSERT INTO usuarios (usu_cargo, usu_nome, usu_cpf) VALUES
('Gerente', 'JENNIFER SILVA SOMBRA', '05230937211'),
('Vendedor(a)', 'ANA CÉLIA DE SOUZA DA SILVA', '04605059202'),
('Vendedor(a)', 'MARIA VITÓRIA RODRIGUES ARAÚJO', '09329324209'),
('Vendedor(a)', 'NIZIA ESTELA SILVA ARAÚJO', '05268006231');

-- Inserção do usuário especial para Trocas
INSERT INTO usuarios (usu_nome, usu_cpf, usu_cargo) VALUES ('TROCA', '00000000000', 'Vendedor(a)');

SELECT 'Estrutura do banco e dados iniciais criados com sucesso!' AS status;

-- ===================================================================
-- SEÇÃO 3: CARGA DE DADOS EXTERNOS (COM LIMPEZA)
-- Execute os blocos abaixo conforme a necessidade de importar dados.
--
-- !! ATENÇÃO !!
-- O comando LOAD DATA INFILE requer que a variável global
-- 'secure_file_priv' do MySQL esteja configurada para permitir
-- o acesso à pasta onde os arquivos .csv estão localizados.
-- ===================================================================

-- ----- BLOCO PARA IMPORTAR CLIENTES -----
-- 1. Desabilita o modo de atualização segura para permitir o DELETE sem WHERE.
SET SQL_SAFE_UPDATES = 0;
-- 2. Limpa todos os registros existentes na tabela de clientes.
DELETE FROM clientes;
-- 3. Reinicia o contador de ID para que os novos registros comecem do 1.
ALTER TABLE clientes AUTO_INCREMENT = 1;
-- 4. Reabilita o modo de atualização segura.
SET SQL_SAFE_UPDATES = 1;

-- 5. Carrega os dados do arquivo CSV para a tabela.
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/clientes.csv'
INTO TABLE clientes
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS
(cli_cpf, cli_nome, cli_ddd, cli_telefone, @cli_data_nascimento)
SET cli_data_nascimento = NULLIF(@cli_data_nascimento, '');

SELECT 'Importação de CLIENTES finalizada.' AS status;


-- ----- BLOCO PARA IMPORTAR PRODUTOS -----
-- 1. Desabilita o modo de atualização segura.
-- ----- BLOCO PARA IMPORTAR PRODUTOS (CORRIGIDO SEM IGNORE 1 ROWS) -----
-- 1. Desabilita o modo de atualização segura.
SET SQL_SAFE_UPDATES = 0;
-- 2. Limpa tabelas que dependem de 'produtos' e a própria tabela 'produtos'.
DELETE FROM inventario_itens;
DELETE FROM itens_pedido;
DELETE FROM produtos;
-- 3. Reinicia os contadores de ID.
ALTER TABLE inventario_itens AUTO_INCREMENT = 1;
ALTER TABLE itens_pedido AUTO_INCREMENT = 1;
ALTER TABLE produtos AUTO_INCREMENT = 1;
-- 4. Reabilita o modo de atualização segura.
SET SQL_SAFE_UPDATES = 1;

-- 5. Carrega os dados do arquivo CSV para a tabela.
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/produtos1.csv'
INTO TABLE produtos
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
-- A LINHA "IGNORE 1 ROWS" FOI REMOVIDA DAQUI
(pro_ref, @pro_sku, pro_descricao, @pro_tam, @pro_bipe, @pro_valor, @pro_caminho_imagem)
SET
    pro_sku = NULLIF(@pro_sku, ''),
    pro_tam = NULLIF(@pro_tam, ''),
    pro_bipe = NULLIF(@pro_bipe, ''),
    pro_valor = NULLIF(@pro_valor, ''),
    pro_caminho_imagem = NULLIF(@pro_caminho_imagem, '');

SELECT 'Importação de PRODUTOS finalizada.' AS status;