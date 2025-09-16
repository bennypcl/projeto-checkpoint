create database CHECKPOINT;
use CHECKPOINT;

-- TABELA DE USUÁRIOS/FUNCIONÁRIOS:
create table usuarios (
	usu_id int auto_increment primary key,
    usu_cargo enum('Gerente', 'Vendedor(a)') not null,
    usu_nome varchar(100) not null,
    usu_cpf char(11) unique not null
); 
select * from usuarios;
desc usuarios;

-- TABELA DE CLIENTES: Armazena informações dos clientes.
create table clientes (
	cli_id int auto_increment primary key,
    cli_cpf char(11) unique not null,
    cli_nome varchar(100) not null,
    cli_data_nascimento date,
    cli_email varchar(100) unique, -- UNIQUE → Garante que não existam emails repetidos no banco de dados.
    cli_ddd char(2),
    cli_telefone varchar(9),
    cli_cep char(8),
    cli_rua varchar(255),
    cli_bairro varchar(150),
    cli_numero varchar(10),
    cli_complemento varchar(255),
    cli_uf char(2),
    cli_cidade varchar(100),
    cli_data_cadastro timestamp default current_timestamp -- TIMESTAMP → Tipo de dado que armazena data e hora (formato YYYY-MM-DD HH:MI:SS). DEFAULT CURRENT_TIMESTAMP → Se nenhum valor for inserido, o MySQL preenche automaticamente com a data e hora atuais.
);

-- TABELA DE PRODUTOS: Armazena os produtos disponíveis para venda.
create table produtos (
	pro_id int auto_increment primary key,
    pro_ref varchar(5) not null,
    pro_sku varchar(5) not null,
    pro_descricao varchar(255) not null,
    pro_tam varchar(10) not null,
    pro_cor varchar(100) not null,
    pro_quant int not null,
    pro_valor decimal(10,2) not null
);
select * from produtos;
desc produtos;

-- TABELA DE PEDIDOS: Registra cada pedido realizado.
create table pedidos (
	ped_id int auto_increment primary key,
    cli_id int,
    ped_data timestamp default current_timestamp,
    ped_total decimal(10,2) not null,
    usu_id int not null,
    foreign key (cli_id) references clientes(cli_id) on delete set null,
    foreign key (usu_id) references usuarios(usu_id)
);
select * from pedidos;
desc pedidos;

-- TABELA DE ITENS DO PEDIDO: Relaciona os produtos comprados em cada pedido.
create table itens_pedido (
	item_id int auto_increment primary key,
    ped_id int not null,
    pro_id int not null,
    item_quant int not null,
    item_valor_unitario decimal(10,2) not null,
    foreign key (ped_id) references pedidos(ped_id) on delete cascade,
    foreign key (pro_id) references produtos(pro_id)
);
select * from itens_pedido;
desc itens_pedido;

-- TABELA DE PAGAMENTOS (REGISTRO GERAL): Guarda todos os pagamentos, independentemente do tipo.
create table pagamentos (
	pag_id int auto_increment primary key,
    ped_id int not null,
    pag_metodo enum('Débito', 'Crédito', 'Pix', 'Dinheiro') not null,
    pag_valor decimal(10,2) not null,
    foreign key (ped_id) references pedidos(ped_id) on delete cascade
);
select * from pagamentos;
desc pagamentos;

-- TABELA PARA PAGAMENTO COM CARTÃO DE DÉBITO
create table debito (
	pag_id int primary key,
    deb_tipo_cartao enum('Visa', 'Mastercard', 'Elo', 'American Express', 'Outro') not null,
    foreign key (pag_id) references pagamentos(pag_id) on delete cascade
);
select * from debito;
desc debito;

-- TABELA PARA PAGAMENTO COM CARTÃO DE CRÉDITO
create table credito (
	pag_id int primary key,
	cre_tipo_cartao enum('Visa', 'Mastercard', 'Elo', 'American Express', 'Outro') not null,
    cre_parcelas int check (cre_parcelas between 1 and 6) not null,
    foreign key (pag_id) references pagamentos(pag_id)
);
select * from credito;
desc credito;

-- TABELA PARA PAGAMENTO COM PIX
create table pix (
	pag_id int primary key,
    pix_chave varchar(255) not null,
    foreign key (pag_id) references pagamentos(pag_id) on delete cascade
); 
select * from pix;
desc pix;

-- TABELA PARA PAGAMENTO EM DINHEIRO
create table dinheiro (
	pag_id int primary key,
    din_troco decimal(10,2) not null,
    foreign key (pag_id) references pagamentos(pag_id) on delete cascade
);
select * from dinheiro;
desc dinheiro;

-- TABELA PARA TEMAS
create table temas (
    tema_id int auto_increment primary key,
    tema_nome varchar(100) not null,
    valor varchar(55)
);
select * from temas;
desc temas;

insert into temas (tema_nome, valor) values
('united', 'escuro'),
('solar', 'claro');

ALTER TABLE produtos ADD COLUMN pro_caminho_imagem VARCHAR(255);

INSERT INTO produtos (pro_ref, pro_sku, pro_descricao, pro_tam, pro_cor, pro_quant, pro_valor, pro_caminho_imagem) 
VALUES ('P0001', 'S0001', 'Camisetas Batman pdv', 'M', 'Indefinida', 10, 89.90, 'imagens_produtos/batman_camiseta.jpg');

INSERT INTO produtos (pro_ref, pro_sku, pro_descricao, pro_tam, pro_cor, pro_quant, pro_valor, pro_caminho_imagem) 
VALUES ('P0002', 'S0002', 'Caneca Star Wars', '350ml', 'Indefinida', 0, 49.90, 'imagens_produtos/caneca_star_wars.jpg');

SELECT * FROM pedidos;

ALTER TABLE pedidos ADD COLUMN ped_desconto_info VARCHAR(50);

-- CLIENTES OFICIAIS:

SET SQL_SAFE_UPDATES = 0; -- EXECUTAR SEMPRE ANTES DE LIMPAR TABELAS -----------------------
DELETE FROM clientes;
ALTER TABLE clientes AUTO_INCREMENT = 1;
SET SQL_SAFE_UPDATES = 1; -- EXECUTAR SEMPRE DEPOIS DE LIMPAR TABELAS -----------------------

SHOW VARIABLES LIKE 'secure_file_priv';

LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/clientes.csv' 
INTO TABLE clientes 
CHARACTER SET utf8mb4 
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"' 
LINES TERMINATED BY '\r\n' 
IGNORE 1 ROWS 
(cli_cpf, cli_nome, cli_ddd, cli_telefone, @cli_data_nascimento) 
SET cli_data_nascimento = NULLIF(@cli_data_nascimento, '');

SELECT * FROM clientes;

-- INVENTÁRIOS:

-- TABELA MESTRE PARA REGISTRAR CADA INVENTÁRIO
CREATE TABLE inventarios (
    inv_id INT AUTO_INCREMENT PRIMARY KEY,
    inv_data_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    inv_data_finalizacao TIMESTAMP NULL,
    inv_status ENUM('Em Andamento', 'Finalizado', 'Cancelado') NOT NULL
);

-- TABELA DE DETALHES PARA GUARDAR CADA ITEM CONTADO EM UM INVENTÁRIO
CREATE TABLE inventario_itens (
    item_inv_id INT AUTO_INCREMENT PRIMARY KEY,
    inv_id INT NOT NULL,
    pro_id INT NOT NULL,
    quantidade_sistema INT NOT NULL,
    quantidade_contada INT,
    FOREIGN KEY (inv_id) REFERENCES inventarios(inv_id) ON DELETE CASCADE,
    FOREIGN KEY (pro_id) REFERENCES produtos(pro_id)
);

select * from inventarios;
select * from inventario_itens;

ALTER TABLE inventario_itens 
MODIFY COLUMN pro_id INT NULL,
ADD COLUMN item_sku VARCHAR(255),
ADD COLUMN item_ref VARCHAR(255),
ADD COLUMN item_descricao VARCHAR(255),
ADD COLUMN item_tam VARCHAR(255),
ADD COLUMN item_valor DECIMAL(10,2);

-- CORREÇÃO DE PRODUTOS:

ALTER TABLE produtos
    -- Removendo COR e QUANTIDADE
    DROP COLUMN pro_cor,
    DROP COLUMN pro_quant,
    
    ADD COLUMN pro_bipe VARCHAR(50) NULL UNIQUE AFTER pro_tam,

    -- REF e SKU para TEXTO com tamanho maior
    MODIFY COLUMN pro_ref VARCHAR(50) NOT NULL,
    MODIFY COLUMN pro_sku VARCHAR(50) NULL,

    -- Aumenta o tamanho do Tamanho/Capacidade e o torna opcional
    MODIFY COLUMN pro_tam VARCHAR(50) NULL,

    -- Torna o Valor opcional
    MODIFY COLUMN pro_valor DECIMAL(10,2) NULL;

select * from produtos;

-- Funcionárias reais:

-- PROCURAR O COISO DE DESTRAVAR A SEGURANÇA --

DELETE FROM credito;
DELETE FROM itens_pedido;
DELETE FROM pagamentos;
DELETE FROM pedidos;
DELETE FROM usuarios WHERE usu_nome != 'Troca';

ALTER TABLE pedidos AUTO_INCREMENT = 1;
ALTER TABLE itens_pedido AUTO_INCREMENT = 1;
ALTER TABLE pagamentos AUTO_INCREMENT = 1;
ALTER TABLE usuarios AUTO_INCREMENT = 1;

-- TRAVAR A SEGURANÇA DE NOVO --

SELECT 'Limpeza definitiva concluída com sucesso!' AS status;

insert into usuarios (usu_cargo, usu_nome, usu_cpf) values
('Gerente', 'JENNIFER SILVA SOMBRA', '05230937211'),
('Vendedor(a)', 'ANA CÉLIA DE SOUZA DA SILVA', '04605059202'),
('Vendedor(a)', 'MARIA VITÓRIA RODRIGUES ARAÚJO', '09329324209'),
('Vendedor(a)', 'NIZIA ESTELA SILVA ARAÚJO', '05268006231');

UPDATE usuarios 
SET usu_nome = 'TROCA' 
WHERE usu_cpf = '00000000000';

-- PRODUTOS REAIS (TESTE):
delete from inventario_itens;
DELETE FROM produtos;

LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/produtos1.csv' 
INTO TABLE produtos 
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS
(pro_ref, @pro_sku, pro_descricao, @pro_tam, @pro_bipe, @pro_valor, @pro_caminho_imagem)
SET 
    pro_sku = NULLIF(@pro_sku, ''),
    pro_tam = NULLIF(@pro_tam, ''),
    pro_bipe = NULLIF(@pro_bipe, ''),
    pro_valor = NULLIF(@pro_valor, ''),
    pro_caminho_imagem = NULLIF(@pro_caminho_imagem, '');

-- --------------------------------------------------------

SELECT * FROM inventarios;
delete from produtos where pro_descricao = "TESTE";