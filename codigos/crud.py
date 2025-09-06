# crud.py
from conexao import conectar
from tkinter import messagebox

# ====================== USUÁRIOS ======================

def inserir_usuario(cargo, nome, cpf):
    """Insere um novo usuário na tabela 'usuarios'."""
    try:
        conn = conectar()
        if not conn: return False
        
        cursor = conn.cursor()
        sql = "INSERT INTO usuarios (usu_cargo, usu_nome, usu_cpf) VALUES (%s, %s, %s)"
        valores = (cargo, nome, cpf)
        cursor.execute(sql, valores)
        conn.commit()
        return True
        
    except Exception as e:
        messagebox.showerror("Erro de Banco de Dados", f"Falha ao inserir usuário: {e}")
        return False
        
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def listar_usuarios():
    """Lista todos os usuários."""
    try:
        conn = conectar()
        if not conn: return []
        
        cursor = conn.cursor(dictionary=True) # dictionary=True para facilitar o acesso por nome de coluna
        cursor.execute("SELECT * FROM usuarios")
        usuarios = cursor.fetchall()
        return usuarios
        
    except Exception as e:
        messagebox.showerror("Erro de Banco de Dados", f"Falha ao listar usuários: {e}")
        return []
        
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# ====================== CLIENTES ======================

def inserir_cliente(cpf, nome, data_nascimento=None, email=None, ddd=None, telefone=None, cep=None, rua=None, bairro=None, numero=None, complemento=None, uf=None, cidade=None):
    """Insere um novo cliente na tabela 'clientes'."""
    try:
        conn = conectar()
        if not conn: return False
        
        cursor = conn.cursor()
        sql = """
            INSERT INTO clientes 
            (cli_cpf, cli_nome, cli_data_nascimento, cli_email, cli_ddd, cli_telefone, cli_cep, cli_rua, cli_bairro, cli_numero, cli_complemento, cli_uf, cli_cidade)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        valores = (cpf, nome, data_nascimento, email, ddd, telefone, cep, rua, bairro, numero, complemento, uf, cidade)
        cursor.execute(sql, valores)
        conn.commit()
        return True

    except Exception as e:
        messagebox.showerror("Erro de Banco de Dados", f"Falha ao inserir cliente: {e}")
        return False

    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


def listar_clientes():
    """Lista todos os clientes."""
    try:
        conn = conectar()
        if not conn: return []
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM clientes")
        clientes = cursor.fetchall()
        return clientes
        
    except Exception as e:
        messagebox.showerror("Erro de Banco de Dados", f"Falha ao listar clientes: {e}")
        return []
        
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# ====================== PRODUTOS ======================

def inserir_produto(ref, sku, descricao, tam, cor, quant, valor):
    """Insere um novo produto na tabela 'produtos'."""
    try:
        conn = conectar()
        if not conn: return False
        
        cursor = conn.cursor()
        sql = """
            INSERT INTO produtos 
            (pro_ref, pro_sku, pro_descricao, pro_tam, pro_cor, pro_quant, pro_valor)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        valores = (ref, sku, descricao, tam, cor, quant, valor)
        cursor.execute(sql, valores)
        conn.commit()
        return True

    except Exception as e:
        messagebox.showerror("Erro de Banco de Dados", f"Falha ao inserir produto: {e}")
        return False

    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def listar_produtos():
    """Lista todos os produtos."""
    try:
        conn = conectar()
        if not conn: return []
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM produtos")
        produtos = cursor.fetchall()
        return produtos
        
    except Exception as e:
        messagebox.showerror("Erro de Banco de Dados", f"Falha ao listar produtos: {e}")
        return []
        
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()