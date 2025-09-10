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

def buscar_cliente_por_cpf(cpf):
    """Busca um cliente pelo CPF e retorna seus dados, ou None se não encontrar."""
    try:
        conn = conectar()
        if not conn: return None
        
        cursor = conn.cursor(dictionary=True)
        # Usamos %s para evitar SQL Injection
        cursor.execute("SELECT * FROM clientes WHERE cli_cpf = %s", (cpf,))
        cliente = cursor.fetchone() # fetchone() pega apenas um resultado
        return cliente
        
    except Exception as e:
        messagebox.showerror("Erro de Banco de Dados", f"Falha ao buscar cliente: {e}")
        return None
        
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def atualizar_cliente(cpf, nome, data_nascimento, ddd, telefone):
    """Atualiza os dados de um cliente existente com base no CPF."""
    try:
        conn = conectar()
        if not conn: return False
        cursor = conn.cursor()
        sql = """
            UPDATE clientes 
            SET cli_nome = %s, cli_data_nascimento = %s, cli_ddd = %s, cli_telefone = %s
            WHERE cli_cpf = %s
        """
        valores = (nome, data_nascimento, ddd, telefone, cpf)
        cursor.execute(sql, valores)
        conn.commit()
        return True
    except Exception as e:
        messagebox.showerror("Erro de BD", f"Falha ao atualizar cliente: {e}")
        return False
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def buscar_produto_por_sku(sku):
    """Busca um produto pelo SKU e retorna seus dados."""
    try:
        conn = conectar()
        if not conn: return None
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM produtos WHERE pro_sku = %s", (sku.upper(),))
        produto = cursor.fetchone()
        return produto
    except Exception as e:
        messagebox.showerror("Erro de BD", f"Falha ao buscar produto: {e}")
        return None
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# No arquivo crud.py

def salvar_venda_completa(dados_venda):
    conn = None
    try:
        conn = conectar()
        if not conn: return False
        cursor = conn.cursor()
        conn.start_transaction()

        # 1. Insere na tabela PEDIDOS (continua igual)
        cli_id = dados_venda['cliente'].get('id')
        usu_id = dados_venda['vendedor_id']
        sql_pedido = "INSERT INTO pedidos (cli_id, ped_total, usu_id) VALUES (%s, %s, %s)"
        cursor.execute(sql_pedido, (cli_id, dados_venda['total'], usu_id))
        id_do_pedido = cursor.lastrowid

        # 2. Insere na tabela ITENS_PEDIDO (continua igual)
        sql_itens = "INSERT INTO itens_pedido (ped_id, pro_id, item_quant, item_valor_unitario) VALUES (%s, %s, %s, %s)"
        for produto in dados_venda['produtos_obj']:
            if produto['preco'] > 0:
                valores_item = (id_do_pedido, produto['id'], 1, produto['preco'])
                cursor.execute(sql_itens, valores_item)

        # 3. Insere na tabela PAGAMENTOS e nas tabelas de DETALHES
        for pag in dados_venda['pagamentos']:
            if pag['valor'] <= 0: continue # Ignora créditos de devolução

            # Insere o pagamento geral
            sql_pagamento = "INSERT INTO pagamentos (ped_id, pag_metodo, pag_valor) VALUES (%s, %s, %s)"
            cursor.execute(sql_pagamento, (id_do_pedido, pag['forma'], pag['valor']))
            id_do_pagamento = cursor.lastrowid # Pega o ID do pagamento que acabamos de inserir

            # Agora, insere os detalhes na tabela específica
            detalhes = pag.get('detalhes', {})
            if pag['forma'] == 'Crédito':
                sql_credito = "INSERT INTO credito (pag_id, cre_tipo_cartao, cre_parcelas) VALUES (%s, %s, %s)"
                cursor.execute(sql_credito, (id_do_pagamento, detalhes.get('bandeira'), detalhes.get('parcelas')))
            
            elif pag['forma'] == 'Débito':
                sql_debito = "INSERT INTO debito (pag_id, deb_tipo_cartao) VALUES (%s, %s)"
                cursor.execute(sql_debito, (id_do_pagamento, detalhes.get('bandeira')))
            
            elif pag['forma'] == 'Pix':
                # Por enquanto, salva uma chave de exemplo, pois não temos o campo na tela
                sql_pix = "INSERT INTO pix (pag_id, pix_chave) VALUES (%s, %s)"
                cursor.execute(sql_pix, (id_do_pagamento, 'CHAVE_PIX_DA_LOJA'))
            
            elif pag['forma'] == 'Dinheiro':
                troco = detalhes.get('troco', 0.0)
                sql_dinheiro = "INSERT INTO dinheiro (pag_id, din_troco) VALUES (%s, %s)"
                cursor.execute(sql_dinheiro, (id_do_pagamento, troco))
        conn.commit()
        return True

    except Exception as e:
        if conn:
            conn.rollback()
        messagebox.showerror("Erro de BD", f"Falha ao salvar a venda: {e}")
        return False
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()