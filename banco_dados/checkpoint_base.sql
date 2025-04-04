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
select * from clientes;
desc clientes;

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