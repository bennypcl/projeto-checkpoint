from conexao import conectar

# ====================== USUÁRIOS ======================

def inserir_usuario(nome, login, senha, nivel_acesso):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO usuarios (nome, login, senha, nivel_acesso)
        VALUES (?, ?, ?, ?)
    """, (nome, login, senha, nivel_acesso))
    conn.commit()
    conn.close()

def listar_usuarios():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios")
    usuarios = cursor.fetchall()
    conn.close()
    return usuarios

# ====================== CLIENTES ======================

def inserir_cliente(nome, telefone, email, endereco):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO clientes (nome, telefone, email, endereco)
        VALUES (?, ?, ?, ?)
    """, (nome, telefone, email, endereco))
    conn.commit()
    conn.close()

def listar_clientes():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientes")
    clientes = cursor.fetchall()
    conn.close()
    return clientes

# ====================== PRODUTOS ======================

def inserir_produto(nome, preco, estoque):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO produtos (nome, preco, estoque)
        VALUES (?, ?, ?)
    """, (nome, preco, estoque))
    conn.commit()
    conn.close()

def listar_produtos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos")
    produtos = cursor.fetchall()
    conn.close()
    return produtos
