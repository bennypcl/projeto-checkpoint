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

insert into usuarios (usu_cargo, usu_nome, usu_cpf) values
('Gerente', 'Ana Costa', '12345678901'),
('Vendedor(a)', 'Carlos Silva', '23456789012'),
('Vendedor(a)', 'Juliana Souza', '34567890123'),
('Vendedor(a)', 'Fernanda Rocha', '56789012345');

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

-- INSERTS de clientes, 30 clientes com CPFs válidos
insert into clientes (cli_cpf, cli_nome, cli_ddd, cli_telefone, cli_data_nascimento) values 
    ("92746111002", "Ana Clara Mendes", "11", "912345678", "1995-03-14"),
    ("81352780066", "Carlos Eduardo Silva", "21", "998765432", "1987-07-22"),
    ("67425397048", "Beatriz Lima Souza", "31", "987654321", "1992-10-09"),
    ("53287154010", "Lucas Henrique Almeida", "41", "998811122", "1985-12-01"),
    ("17896573008", "Juliana Ferreira Costa", "51", "985203344", "1990-05-25"),
    ("30276469005", "Rafael Gomes Pereira", "61", "993456677", "1988-01-17"),
    ("62358041091", "Mariana Rocha Martins", "71", "997778899", "1996-11-12"),
    ("41593226003", "Thiago Oliveira Ramos", "85", "996543210", "1984-06-03"),
    ("31248019090", "Camila Barros Dias", "95", "991234567", "1993-02-28"),
    ("28974187074", "Pedro Henrique Castro", "62", "987123345", "1989-08-30"),
    ("40918236020", "Larissa Souza Pinto", "27", "997891122", "1991-09-19"),
    ("13924875001", "Felipe Teixeira Moura", "84", "999874455", "1983-05-11"),
    ("61479043013", "Natália Ribeiro Franco", "91", "994567788", "1994-04-06"),
    ("30654928027", "Gabriel Monteiro Lira", "98", "996789900", "1990-03-13"),
    ("47136512006", "Amanda Nogueira Dantas", "83", "993215566", "1992-07-04"),
    ("21769854094", "Vinícius Castro Neves", "65", "997124412", "1986-10-15"),
    ("59043167009", "Isabela Fernandes Melo", "82", "998657789", "1997-02-08"),
    ("70481230080", "Diego Antunes Vieira", "92", "991123434", "1982-12-23"),
    ("36529411058", "Tatiane Lopes Silva", "13", "999007788", "1990-06-16"),
    ("23450996045", "Bruno César Tavares", "11", "988762233", "1987-04-20"),
    ("59137282034", "Fernanda Dias Luz", "43", "991003344", "1993-09-10"),
    ("84261709007", "Matheus Azevedo Cunha", "71", "993234455", "1991-01-07"),
    ("73482065096", "Bruna Cavalcanti Reis", "31", "996775566", "1996-11-13"),
    ("38591741023", "Ricardo Lima Bastos", "85", "999906677", "1984-03-02"),
    ("63047238055", "Aline Martins Queiroz", "27", "992138899", "1995-08-18"),
    ("51063890012", "André Luiz Costa", "41", "998761122", "1989-05-29"),
    ("30487162080", "Patrícia Rocha Vieira", "61", "993345567", "1990-10-21"),
    ("48591037061", "Henrique Fonseca Braga", "91", "997778899", "1986-06-06"),
    ("24983760003", "Elaine Bezerra Lima", "51", "988123345", "1992-04-14"),
    ("71234829050", "Murilo Andrade Pires", "11", "996007788", "1988-07-26");

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