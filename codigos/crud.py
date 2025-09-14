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

def salvar_venda_completa(dados_venda):
    conn = None
    try:
        conn = conectar()
        if not conn: return False
        cursor = conn.cursor()
        conn.start_transaction()

        # 1. Insere na tabela PEDIDOS (com a nova coluna de desconto)
        cli_id = dados_venda['cliente'].get('id')
        usu_id = dados_venda['vendedor_id']
        desconto_info = dados_venda.get('desconto', '') # Pega a info do desconto

        sql_pedido = "INSERT INTO pedidos (cli_id, ped_total, usu_id, ped_desconto_info) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql_pedido, (cli_id, dados_venda['total'], usu_id, desconto_info))
        id_do_pedido = cursor.lastrowid

        # 2. Insere na tabela ITENS_PEDIDO
        sql_itens = "INSERT INTO itens_pedido (ped_id, pro_id, item_quant, item_valor_unitario) VALUES (%s, %s, %s, %s)"
        for produto in dados_venda['produtos_obj']:
            valores_item = (id_do_pedido, produto['id'], 1, produto['preco'])
            cursor.execute(sql_itens, valores_item)

        # 3. Insere na tabela PAGAMENTOS e nas tabelas de DETALHES
        for pag in dados_venda['pagamentos']:
            if pag['valor'] <= 0: continue
            sql_pagamento = "INSERT INTO pagamentos (ped_id, pag_metodo, pag_valor) VALUES (%s, %s, %s)"
            cursor.execute(sql_pagamento, (id_do_pedido, pag['forma'], pag['valor']))
            id_do_pagamento = cursor.lastrowid
            
            detalhes = pag.get('detalhes', {})
            if pag['forma'] == 'Crédito':
                sql_credito = "INSERT INTO credito (pag_id, cre_tipo_cartao, cre_parcelas) VALUES (%s, %s, %s)"
                cursor.execute(sql_credito, (id_do_pagamento, detalhes.get('bandeira'), detalhes.get('parcelas')))
            elif pag['forma'] == 'Débito':
                sql_debito = "INSERT INTO debito (pag_id, deb_tipo_cartao) VALUES (%s, %s)"
                cursor.execute(sql_debito, (id_do_pagamento, detalhes.get('bandeira')))
            elif pag['forma'] == 'Pix':
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

def listar_produto_especifico(pro_sku):
    """Lista um produto específico a partir do SKU"""
    try:
        conn = conectar()
        if not conn: return []
        
        cursor = conn.cursor(dictionary=True)
        query = ("SELECT * FROM produtos where pro_sku = %s")
        cursor.execute(query, (pro_sku,))
        produto = cursor.fetchone()
        return produto
        
    except Exception as e:
        messagebox.showerror("Erro de Banco de Dados", f"Falha ao listar produtos: {e}")
        return []
        
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def buscar_vendas_para_relatorio(vendedor=None, data_inicio=None, data_fim=None):
    """Busca e monta um relatório de vendas, com filtros opcionais."""
    conn = None
    try:
        conn = conectar()
        if not conn: return []
        
        cursor = conn.cursor(dictionary=True)
        
        # --- LÓGICA DE FILTRO DINÂMICO ---
        params = []
        sql_base = """
            SELECT 
                p.ped_id, p.ped_data, p.ped_total, p.ped_desconto_info,
                u.usu_nome AS vendedor,
                c.cli_nome, c.cli_cpf, c.cli_telefone, c.cli_data_nascimento
            FROM pedidos p
            JOIN usuarios u ON p.usu_id = u.usu_id
            LEFT JOIN clientes c ON p.cli_id = c.cli_id
            WHERE 1=1
        """
        
        if vendedor and vendedor != "Mostrar Tudo":
            sql_base += " AND u.usu_nome = %s"
            params.append(vendedor)
        
        if data_inicio:
            sql_base += " AND DATE(p.ped_data) >= %s"
            params.append(data_inicio)
        
        if data_fim:
            sql_base += " AND DATE(p.ped_data) <= %s"
            params.append(data_fim)
            
        sql_base += " ORDER BY p.ped_data DESC"
        
        cursor.execute(sql_base, tuple(params))
        vendas = cursor.fetchall()
        
        for venda in vendas:
            sql_itens = """
                SELECT p.pro_descricao, ip.item_valor_unitario
                FROM itens_pedido ip
                JOIN produtos p ON ip.pro_id = p.pro_id
                WHERE ip.ped_id = %s
            """
            cursor.execute(sql_itens, (venda['ped_id'],))
            itens = cursor.fetchall()
            
            # Formata a lista de produtos, adicionando [DEVOLUÇÃO] se o preço for negativo
            lista_produtos_formatada = []
            for item in itens:
                if item['item_valor_unitario'] < 0:
                    lista_produtos_formatada.append(f"[DEVOLUÇÃO] {item['pro_descricao']}")
                else:
                    lista_produtos_formatada.append(item['pro_descricao'])
            venda['produtos'] = lista_produtos_formatada

            # Busca os pagamentos do pedido
            sql_pagamentos = "SELECT pag_metodo, pag_valor FROM pagamentos WHERE ped_id = %s"
            cursor.execute(sql_pagamentos, (venda['ped_id'],))
            pagamentos = cursor.fetchall()
            venda['pagamentos'] = [(p['pag_metodo'], p['pag_valor']) for p in pagamentos]

            # Organiza os dados do cliente em um sub-dicionário
            venda['cliente'] = {
                'nome': venda.pop('cli_nome') or 'N/A', # Usa 'N/A' se o nome for nulo
                'cpf': venda.pop('cli_cpf') or '',
                'telefone': venda.pop('cli_telefone') or '',
                'nascimento': venda.pop('cli_data_nascimento')
            }
            # Formata a data de nascimento para texto, se ela existir
            if venda['cliente']['nascimento']:
                venda['cliente']['nascimento'] = venda['cliente']['nascimento'].strftime("%d/%m/%Y")
            else:
                venda['cliente']['nascimento'] = '' # Garante que seja uma string vazia
            
            # Formata a data do pedido
            venda['ped_data'] = venda['ped_data'].strftime("%d/%m/%Y %H:%M")
            # Renomeia a chave do desconto para corresponder ao esperado pela interface
            venda['desconto'] = venda.pop('ped_desconto_info') or ''

        return vendas

    except Exception as e:
        messagebox.showerror("Erro de Banco de Dados", f"Falha ao buscar relatório de vendas: {e}")
        return []
        
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()