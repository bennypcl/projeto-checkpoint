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

insert into produtos (pro_ref, pro_sku, pro_descricao, pro_tam, pro_cor, pro_quant, pro_valor)
values
('0VKSL', 'XPSL4', 'Pin Thanos', 'UN', 'Amarelo', 55, 19.90),
('0M6RS', 'NHE0G', 'Camiseta Goku', 'GG', 'Vermelho', 30, 79.90),
('0M6RS', '8A63F', 'Camiseta Goku', 'G', 'Vermelho', 30, 79.90),
('0M6RS', 'Z4E1U', 'Camiseta Goku', 'P', 'Vermelho', 30, 79.90),
('1XOJ3', 'U1JN9', 'Camiseta Batman', 'GG', 'Cinza', 62, 69.90),
('1XOJ3', '0H1CF', 'Camiseta Batman', 'P', 'Cinza', 62, 69.90),
('1XOJ3', 'S39L3', 'Camiseta Batman', 'G', 'Cinza', 62, 69.90),
('1XOJ3', 'F5DI0', 'Camiseta Batman', 'M', 'Cinza', 62, 69.90),
('JEY3D', '965NX', 'Pin Batman', 'UN', 'Amarelo', 89, 9.90),
('X633A', 'A24G7', 'Camiseta Naruto', 'P', 'Branco', 22, 69.90),
('X633A', '5H1WL', 'Camiseta Naruto', 'GG', 'Branco', 22, 69.90),
('X633A', 'NV69C', 'Camiseta Naruto', 'G', 'Branco', 22, 69.90),
('VW5JT', '0TLUF', 'Camiseta Darth Vader', 'GG', 'Preto', 57, 79.90),
('VW5JT', 'WEXQB', 'Camiseta Darth Vader', 'M', 'Preto', 57, 79.90),
('20SMS', 'R9OBN', 'Caneca Sailor Moon', 'UN', 'Azul', 89, 39.90),
('X3M3W', '219WD', 'Caneca Batman', 'UN', 'Verde', 55, 39.90),
('A0937', 'PCSMI', 'Garrafa Superman', 'UN', 'Azul', 92, 49.90),
('5K7JY', 'X5GOS', 'Pin Sailor Moon', 'UN', 'Azul', 28, 19.90),
('FXTRB', 'AF1Y2', 'Garrafa Yoda', 'UN', 'Verde', 57, 49.90),
('CGTR3', 'Y7TU1', 'Garrafa Goku', 'UN', 'Branco', 21, 59.90),
('4IB83', 'KI10B', 'Pin Goku', 'UN', 'Roxo', 70, 19.90),
('3WBNJ', 'VNIFS', 'Garrafa Homem Aranha', 'UN', 'Cinza', 70, 64.90),
('OCUPA', 'TCO33', 'Caneca Sailor Moon', 'UN', 'Cinza', 86, 39.90),
('CXX8E', 'QTWTU', 'Pin Homem Aranha', 'UN', 'Vermelho', 72, 19.90),
('K6WO8', 'ZFUVX', 'Garrafa Superman', 'UN', 'Amarelo', 36, 64.90),
('4GA99', 'YXLVB', 'Pin Mulher Maravilha', 'UN', 'Vermelho', 87, 9.90),
('B3SPH', '8PMOP', 'Caneca Homem Aranha', 'UN', 'Azul', 11, 34.90),
('ZJIK4', 'K5R9J', 'Camiseta Batman', 'M', 'Verde', 67, 89.90),
('ZJIK4', 'O959Y', 'Camiseta Batman', 'GG', 'Verde', 67, 89.90),
('ZJIK4', '17ZAB', 'Camiseta Batman', 'P', 'Verde', 67, 89.90),
('TE0TS', 'S3X17', 'Pin Darth Vader', 'UN', 'Vermelho', 26, 19.90),
('9PN8Q', 'Q4OH4', 'Camiseta Darth Vader', 'GG', 'Verde', 17, 89.90),
('9PN8Q', 'TU099', 'Camiseta Darth Vader', 'G', 'Verde', 17, 89.90),
('9PN8Q', 'RK4MR', 'Camiseta Darth Vader', 'M', 'Verde', 17, 89.90),
('9PN8Q', 'QKF40', 'Camiseta Darth Vader', 'P', 'Verde', 17, 89.90),
('EPSM8', 'N3XE7', 'Camiseta Homem Aranha', 'P', 'Amarelo', 99, 69.90),
('EPSM8', '18FWI', 'Camiseta Homem Aranha', 'G', 'Amarelo', 99, 69.90),
('EPSM8', 'VYTFJ', 'Camiseta Homem Aranha', 'GG', 'Amarelo', 99, 69.90),
('LE3P8', 'C9GU1', 'Camiseta Harry Potter', 'M', 'Verde', 57, 89.90),
('LE3P8', 'Y1HLR', 'Camiseta Harry Potter', 'GG', 'Verde', 57, 89.90),
('LE3P8', 'J3PD4', 'Camiseta Harry Potter', 'G', 'Verde', 57, 89.90),
('UWEL6', '0NCZH', 'Camiseta Sailor Moon', 'G', 'Amarelo', 38, 89.90),
('UWEL6', '360J2', 'Camiseta Sailor Moon', 'P', 'Amarelo', 38, 89.90),
('UWEL6', '2QRDZ', 'Camiseta Sailor Moon', 'GG', 'Amarelo', 38, 89.90),
('PWPI8', 'RXDDP', 'Pin Deadpool', 'UN', 'Azul', 47, 9.90),
('QRSNR', 'ZUG8W', 'Camiseta Goku', 'P', 'Cinza', 13, 69.90),
('QRSNR', 'TLY88', 'Camiseta Goku', 'G', 'Cinza', 13, 69.90),
('KD27P', 'F80X3', 'Camiseta Yoda', 'P', 'Vermelho', 18, 89.90),
('KD27P', 'S3A45', 'Camiseta Yoda', 'GG', 'Vermelho', 18, 89.90),
('KD27P', 'QRGDW', 'Camiseta Yoda', 'G', 'Vermelho', 18, 89.90),
('KD27P', 'UNSSA', 'Camiseta Yoda', 'M', 'Vermelho', 18, 89.90),
('HDBVS', 'A11VH', 'Caneca Superman', 'UN', 'Verde', 99, 29.90),
('MD8LW', 'OG2CJ', 'Pin Homem Aranha', 'UN', 'Vermelho', 50, 19.90),
('3H4XH', 'HDUFP', 'Camiseta Darth Vader', 'P', 'Verde', 69, 69.90),
('3H4XH', '9NHCP', 'Camiseta Darth Vader', 'G', 'Verde', 69, 69.90),
('31LOS', 'IS92I', 'Camiseta Mulher Maravilha', 'M', 'Cinza', 46, 79.90),
('31LOS', 'R6H0N', 'Camiseta Mulher Maravilha', 'P', 'Cinza', 46, 79.90),
('31LOS', 'S9TO9', 'Camiseta Mulher Maravilha', 'GG', 'Cinza', 46, 79.90),
('31LOS', 'Y5UNM', 'Camiseta Mulher Maravilha', 'G', 'Cinza', 46, 79.90),
('JQJVD', '1RMI9', 'Garrafa Harry Potter', 'UN', 'Branco', 42, 64.90),
('TPQK4', '3F415', 'Camiseta Homem Aranha', 'M', 'Azul', 38, 79.90),
('TPQK4', 'TM2QP', 'Camiseta Homem Aranha', 'GG', 'Azul', 38, 79.90),
('TPQK4', '66XPC', 'Camiseta Homem Aranha', 'P', 'Azul', 38, 79.90),
('CHZUS', '9R1BD', 'Camiseta Darth Vader', 'M', 'Preto', 16, 69.90),
('CHZUS', 'PBNKV', 'Camiseta Darth Vader', 'G', 'Preto', 16, 69.90),
('CHZUS', '4CZXT', 'Camiseta Darth Vader', 'P', 'Preto', 16, 69.90),
('CHZUS', '1Z36P', 'Camiseta Darth Vader', 'GG', 'Preto', 16, 69.90),
('LS2NZ', '79N0M', 'Pin Harry Potter', 'UN', 'Verde', 37, 19.90),
('41660', 'V2XY6', 'Garrafa Luffy', 'UN', 'Verde', 37, 64.90),
('LU775', '61Z4C', 'Caneca Darth Vader', 'UN', 'Amarelo', 39, 39.90),
('C920J', 'QFDI6', 'Pin Capitão América', 'UN', 'Amarelo', 67, 19.90),
('GCHQG', 'EP0CP', 'Pin Superman', 'UN', 'Branco', 61, 9.90),
('UXQMA', 'QSTT8', 'Garrafa Batman', 'UN', 'Cinza', 86, 49.90),
('QUZ4P', 'OKLZW', 'Pin Deadpool', 'UN', 'Cinza', 49, 19.90),
('YGRC6', '9CMAP', 'Garrafa Batman', 'UN', 'Azul', 54, 49.90),
('LXI3Q', 'Q3STW', 'Caneca Capitão América', 'UN', 'Roxo', 85, 39.90),
('LHH4N', '80BZ4', 'Garrafa Batman', 'UN', 'Vermelho', 44, 64.90),
('Z1KTM', 'M12Q6', 'Camiseta Mulher Maravilha', 'GG', 'Cinza', 30, 79.90),
('Z1KTM', 'CM1H5', 'Camiseta Mulher Maravilha', 'M', 'Cinza', 30, 79.90),
('Z1KTM', 'JDTV4', 'Camiseta Mulher Maravilha', 'P', 'Cinza', 30, 79.90),
('3J06V', '382VA', 'Camiseta Yoda', 'GG', 'Verde', 17, 79.90),
('3J06V', 'CT2K6', 'Camiseta Yoda', 'P', 'Verde', 17, 79.90),
('3J06V', '17C9R', 'Camiseta Yoda', 'M', 'Verde', 17, 79.90),
('90J9S', 'DLSPN', 'Caneca Goku', 'UN', 'Branco', 60, 34.90),
('IWSMP', '2FM14', 'Camiseta Deadpool', 'GG', 'Amarelo', 59, 89.90),
('IWSMP', '62G25', 'Camiseta Deadpool', 'P', 'Amarelo', 59, 89.90),
('IWSMP', '4Z0CS', 'Camiseta Deadpool', 'M', 'Amarelo', 59, 89.90),
('4HVFP', 'MXXFS', 'Caneca Homem de Ferro', 'UN', 'Branco', 38, 39.90),
('ZEBOP', '96BRN', 'Pin Homem de Ferro', 'UN', 'Branco', 48, 9.90),
('JVFLU', 'EVK1Y', 'Pin Thanos', 'UN', 'Branco', 30, 19.90),
('OTPBV', 'O390N', 'Camiseta Naruto', 'GG', 'Azul', 97, 89.90),
('OTPBV', '6Q1I2', 'Camiseta Naruto', 'G', 'Azul', 97, 89.90),
('OTPBV', 'AQ0K6', 'Camiseta Naruto', 'M', 'Azul', 97, 89.90),
('UY0WR', 'QVQ5D', 'Garrafa Thanos', 'UN', 'Roxo', 52, 59.90),
('7B9RY', 'CISMO', 'Caneca Deadpool', 'UN', 'Vermelho', 49, 39.90),
('NDM65', 'OE0V0', 'Pin Naruto', 'UN', 'Preto', 69, 19.90),
('DEX9Z', 'S26I5', 'Camiseta Homem Aranha', 'GG', 'Preto', 84, 69.90),
('DEX9Z', 'QAR20', 'Camiseta Homem Aranha', 'P', 'Preto', 84, 69.90),
('DEX9Z', 'Q800Y', 'Camiseta Homem Aranha', 'G', 'Preto', 84, 69.90),
('DEX9Z', 'Z1XQT', 'Camiseta Homem Aranha', 'M', 'Preto', 84, 69.90);

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

INSERT INTO usuarios (usu_cargo, usu_nome, usu_cpf) VALUES ('Vendedor(a)', 'Troca', '00000000000');