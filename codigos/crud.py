from conexao import conectar
from tkinter import messagebox

# USUÁRIOS 

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
        messagebox.showerror("Erro na comunicação de dados", f"Falha ao inserir usuário: {e}")
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
        messagebox.showerror("Erro na comunicação de dados", f"Falha ao listar usuários: {e}")
        return []
        
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# CLIENTES 

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
        messagebox.showerror("Erro na comunicação de dados", f"Falha ao inserir cliente: {e}")
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
        messagebox.showerror("Erro na comunicação de dados", f"Falha ao listar clientes: {e}")
        return []
        
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# PRODUTOS 

def inserir_produto(ref, sku, descricao, tam, bipe, valor, caminho_imagem=None):
    """Insere um novo produto na tabela 'produtos' com a nova estrutura."""
    try:
        conn = conectar()
        if not conn: return False

        cursor = conn.cursor()
        sql = """
            INSERT INTO produtos 
            (pro_ref, pro_sku, pro_descricao, pro_tam, pro_bipe, pro_valor, pro_caminho_imagem)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        sku = sku if sku else None
        bipe = bipe if bipe else None
        valor = float(valor.replace(',', '.')) if valor else None

        valores = (ref, sku, descricao, tam, bipe, valor, caminho_imagem)
        cursor.execute(sql, valores)
        conn.commit()
        return True

    except Exception as e:
        messagebox.showerror("Erro na comunicação de dados", f"Falha ao inserir produto: {e}")
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
        messagebox.showerror("Erro na comunicação de dados", f"Falha ao listar produtos: {e}")
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
        cursor.execute("SELECT * FROM clientes WHERE cli_cpf = %s", (cpf,))
        cliente = cursor.fetchone() # fetchone() pega só um resultado
        return cliente
        
    except Exception as e:
        messagebox.showerror("Erro na comunicação de dados", f"Falha ao buscar cliente: {e}")
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
        messagebox.showerror("Erro na comunicação de dados", f"Falha ao atualizar cliente: {e}")
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
        messagebox.showerror("Erro na comunicação de dados", f"Falha ao buscar produto: {e}")
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

        # insere na tabela PEDIDOS
        cli_id = dados_venda['cliente'].get('id')
        usu_id = dados_venda['vendedor_id']
        desconto_info = dados_venda.get('desconto', '') # Pega a info do desconto

        sql_pedido = "INSERT INTO pedidos (cli_id, ped_total, usu_id, ped_desconto_info) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql_pedido, (cli_id, dados_venda['total'], usu_id, desconto_info))
        id_do_pedido = cursor.lastrowid

        # insere na tabela ITENS_PEDIDO
        sql_itens = "INSERT INTO itens_pedido (ped_id, pro_id, item_quant, item_valor_unitario) VALUES (%s, %s, %s, %s)"
        for produto in dados_venda['produtos_obj']:
            valores_item = (id_do_pedido, produto['id'], 1, produto['preco'])
            cursor.execute(sql_itens, valores_item)

        # insere na tabela PAGAMENTOS e nas tabelas de DETALHES
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
        messagebox.showerror("Erro na comunicação de dados", f"Falha ao salvar a venda: {e}")
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
        messagebox.showerror("Erro na comunicação de dados", f"Falha ao listar produtos: {e}")
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
        
        #  LÓGICA DE FILTRO DINÂMICO 
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
                SELECT p.pro_descricao, p.pro_sku, p.pro_tam, ip.item_valor_unitario
                FROM itens_pedido ip
                JOIN produtos p ON ip.pro_id = p.pro_id
                WHERE ip.ped_id = %s
            """
            cursor.execute(sql_itens, (venda['ped_id'],))
            itens = cursor.fetchall()
            
            lista_produtos_formatada = []
            for item in itens:
                # Garante que SKU e Tam sejam textos, mesmo se forem nulos no banco
                sku = item.get('pro_sku') or 'N/A'
                tam = item.get('pro_tam') or 'N/A'
                
                info_str = f"{item['pro_descricao']} (SKU: {sku}, Tam: {tam})"
                
                if item['item_valor_unitario'] < 0:
                    lista_produtos_formatada.append(f"[DEVOLUÇÃO] {info_str}")
                else:
                    lista_produtos_formatada.append(info_str)
            venda['produtos'] = lista_produtos_formatada

            # Busca os pagamentos do pedido
            sql_pagamentos = "SELECT pag_metodo, pag_valor FROM pagamentos WHERE ped_id = %s"
            cursor.execute(sql_pagamentos, (venda['ped_id'],))
            pagamentos = cursor.fetchall()
            venda['pagamentos'] = [(p['pag_metodo'], p['pag_valor']) for p in pagamentos]

            # Organiza os dados do cliente em um sub-dicionário
            venda['cliente'] = {
                'nome': venda.pop('cli_nome') or 'N/A',
                'cpf': venda.pop('cli_cpf') or '',
                'telefone': venda.pop('cli_telefone') or '',
                'nascimento': venda.pop('cli_data_nascimento')
            }
            if venda['cliente']['nascimento']:
                venda['cliente']['nascimento'] = venda['cliente']['nascimento'].strftime("%d/%m/%Y")
            else:
                venda['cliente']['nascimento'] = ''
            
            venda['ped_data'] = venda['ped_data'].strftime("%d/%m/%Y %H:%M")
            venda['desconto'] = venda.pop('ped_desconto_info') or ''

        return vendas

    except Exception as e:
        messagebox.showerror("Erro na comunicação de dados", f"Falha ao buscar relatório de vendas: {e}")
        return []
        
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# INVENTÁRIO 

def criar_novo_inventario(lista_produtos_do_arquivo):
    """Cria um novo registro de inventário e TODOS os seus itens, conhecidos ou não."""
    conn = None
    try:
        conn = conectar()
        if not conn: return None
        cursor = conn.cursor()
        conn.start_transaction()

        cursor.execute("INSERT INTO inventarios (inv_status) VALUES ('Em Andamento')")
        id_inventario_ativo = cursor.lastrowid

        sql_item = """
            INSERT INTO inventario_itens 
            (inv_id, pro_id, quantidade_sistema, item_ref, item_sku, item_descricao, item_tam, item_valor) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        for produto_data in lista_produtos_do_arquivo:
            ref, sku, desc, tam, quant, valor = produto_data[1], produto_data[2], produto_data[3], produto_data[4], produto_data[5], produto_data[6]
            
            cursor.execute("SELECT pro_id FROM produtos WHERE pro_sku = %s", (sku,))
            resultado_produto = cursor.fetchone()
            
            if resultado_produto:
                # Se o produto existe, salva o pro_id e deixa os campos de texto nulos
                pro_id = resultado_produto[0]
                cursor.execute(sql_item, (id_inventario_ativo, pro_id, quant, None, None, None, None, None))
            else:
                # Se o produto NÃO existe, salva pro_id como NULL e guarda os dados do arquivo
                cursor.execute(sql_item, (id_inventario_ativo, None, quant, ref, sku, desc, tam, valor))

        conn.commit()
        return id_inventario_ativo

    except Exception as e:
        if conn: conn.rollback()
        messagebox.showerror("na comunicação de dados", f"Falha ao criar novo inventário: {e}")
        return None
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def atualizar_contagem_item(id_inventario, sku_produto, nova_quantidade):
    """Atualiza a quantidade contada de um item, funcionando para produtos conhecidos (com pro_id) e desconhecidos (sem pro_id)."""
    try:
        conn = conectar()
        if not conn: return False
        cursor = conn.cursor()

        # Tenta encontrar um pro_id para o SKU.
        cursor.execute("SELECT pro_id FROM produtos WHERE pro_sku = %s", (sku_produto,))
        resultado_produto = cursor.fetchone()

        if resultado_produto:
            # Se o produto tem pro_id, atualiza usando o pro_id.
            pro_id = resultado_produto[0]
            sql = """
                UPDATE inventario_itens 
                SET quantidade_contada = %s 
                WHERE inv_id = %s AND pro_id = %s
            """
            cursor.execute(sql, (nova_quantidade, id_inventario, pro_id))
        else:
            # Se o produto não tem pro_id, atualiza usando o item_sku.
            sql = """
                UPDATE inventario_itens 
                SET quantidade_contada = %s 
                WHERE inv_id = %s AND item_sku = %s AND pro_id IS NULL
            """
            cursor.execute(sql, (nova_quantidade, id_inventario, sku_produto))

        conn.commit()
        
        if cursor.rowcount > 0:
            return True
        else:
            # Isso pode acontecer se o SKU não for encontrado nem em produtos nem em inventario_itens
            print(f"AVISO: Nenhuma linha atualizada para o SKU {sku_produto} no inventário {id_inventario}.")
            return False

    except Exception as e:
        messagebox.showerror("na comunicação de dados", f"Falha ao atualizar contagem: {e}")
        return False
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def finalizar_inventario_db(id_inventario):
    """Muda o status do inventário para 'Finalizado'."""
    try:
        conn = conectar()
        if not conn: return False
        cursor = conn.cursor()
        sql = "UPDATE inventarios SET inv_status = 'Finalizado', inv_data_finalizacao = NOW() WHERE inv_id = %s"
        cursor.execute(sql, (id_inventario,))
        conn.commit()
        return True
    except Exception as e:
        messagebox.showerror("Erro na comunicação de dados", f"Falha ao finalizar inventário: {e}")
        return False
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def cancelar_inventario_db(id_inventario):
    """Apaga um registro de inventário e todos os seus itens."""
    try:
        conn = conectar()
        if not conn: return False
        cursor = conn.cursor()
        sql = "DELETE FROM inventarios WHERE inv_id = %s"
        cursor.execute(sql, (id_inventario,))
        conn.commit()
        return True
    except Exception as e:
        messagebox.showerror("Erro na comunicação de dados", f"Falha ao cancelar inventário: {e}")
        return False
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def buscar_inventario_em_andamento():
    """Busca um inventário em andamento e retorna seus dados, tratando itens conhecidos e desconhecidos."""
    conn = None
    try:
        conn = conectar()
        if not conn: return None
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT inv_id FROM inventarios WHERE inv_status = 'Em Andamento' LIMIT 1")
        inventario_ativo = cursor.fetchone()

        if not inventario_ativo:
            return None

        inv_id = inventario_ativo['inv_id']

        # Query que usa COALESCE para pegar os dados da tabela produtos OU da tabela inventario_itens
        sql_itens = """
            SELECT 
                COALESCE(p.pro_ref, ii.item_ref) AS pro_ref,
                COALESCE(p.pro_sku, ii.item_sku) AS pro_sku,
                COALESCE(p.pro_descricao, ii.item_descricao) AS pro_descricao,
                COALESCE(p.pro_tam, ii.item_tam) AS pro_tam,
                COALESCE(p.pro_valor, ii.item_valor) AS pro_valor,
                ii.quantidade_sistema,
                ii.quantidade_contada
            FROM inventario_itens ii
            LEFT JOIN produtos p ON ii.pro_id = p.pro_id
            WHERE ii.inv_id = %s
        """
        cursor.execute(sql_itens, (inv_id,))
        itens_do_inventario = cursor.fetchall()

        return {
            "id_inventario": inv_id,
            "itens": itens_do_inventario
        }

    except Exception as e:
        messagebox.showerror("Erro na comunicação de dados", f"Falha ao buscar inventário em andamento: {e}")
        return None
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def listar_inventarios_finalizados(data_inicio=None, data_fim=None):
    """Busca no banco uma lista de todos os inventários com status 'Finalizado'."""
    conn = None
    try:
        conn = conectar()
        if not conn: return []
        cursor = conn.cursor(dictionary=True)

        params = []
        sql = "SELECT inv_id, inv_data_inicio, inv_data_finalizacao FROM inventarios WHERE inv_status = 'Finalizado'"

        if data_inicio:
            sql += " AND DATE(inv_data_inicio) >= %s"
            params.append(data_inicio)
        if data_fim:
            sql += " AND DATE(inv_data_finalizacao) <= %s"
            params.append(data_fim)
        
        sql += " ORDER BY inv_data_inicio DESC"

        cursor.execute(sql, tuple(params))
        inventarios = cursor.fetchall()
        return inventarios

    except Exception as e:
        messagebox.showerror("Erro na comunicação de dados", f"Falha ao listar inventários finalizados: {e}")
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def buscar_detalhes_inventario(inv_id):
    """Busca todos os itens de um inventário específico pelo seu ID."""
    conn = None
    try:
        conn = conectar()
        if not conn: return {}
        cursor = conn.cursor(dictionary=True)
        
        sql = """
            SELECT 
                COALESCE(p.pro_ref, ii.item_ref) AS ref,
                COALESCE(p.pro_sku, ii.item_sku) AS sku,
                COALESCE(p.pro_descricao, ii.item_descricao) AS `desc`,
                COALESCE(p.pro_tam, ii.item_tam) AS tam,
                ii.quantidade_sistema AS est,
                ii.quantidade_contada AS est_real
            FROM inventario_itens ii
            LEFT JOIN produtos p ON ii.pro_id = p.pro_id
            WHERE ii.inv_id = %s
        """
        cursor.execute(sql, (inv_id,))
        itens = cursor.fetchall()
        return itens

    except Exception as e:
        messagebox.showerror("Erro na comunicação de dados", f"Falha ao buscar detalhes do inventário: {e}")
        return {}
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def adicionar_item_ao_inventario(id_inventario, sku_produto):
    """Adiciona um único produto a um inventário já em andamento."""
    try:
        conn = conectar()
        if not conn: return False
        cursor = conn.cursor()

        # Primeiro busca o pro_id do produto que já deve existir na tabela 'produtos'
        cursor.execute("SELECT pro_id, pro_ref, pro_descricao, pro_tam, pro_valor FROM produtos WHERE pro_sku = %s", (sku_produto,))
        produto = cursor.fetchone()

        if not produto:
            messagebox.showerror("Erro na comunicação de dados", f"Não foi possível encontrar o produto com SKU {sku_produto} para adicionar ao inventário.")
            return False

        pro_id, ref, desc, tam, valor = produto

        # Adiciona o item ao inventário com quantidade de sistema 0
        sql_item = """
            INSERT INTO inventario_itens
            (inv_id, pro_id, quantidade_sistema, item_ref, item_sku, item_descricao, item_tam, item_valor)
            VALUES (%s, %s, 0, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql_item, (id_inventario, pro_id, ref, sku_produto, desc, tam, valor))
        conn.commit()
        return True

    except Exception as e:
        messagebox.showerror("Erro na comunicação de dados", f"Falha ao adicionar item ao inventário: {e}")
        return False
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def buscar_produto_por_sku_ou_bipe(codigo):
    """
    Busca um produto pelo SKU ou pelo Bipe (código de barras).
    Retorna os dados do produto se encontrar, ou None se não encontrar.
    """
    if not codigo:
        return None
    try:
        conn = conectar()
        if not conn: return None
        cursor = conn.cursor(dictionary=True)
        
        # A query agora busca em duas colunas
        sql = "SELECT * FROM produtos WHERE pro_sku = %s OR pro_bipe = %s"
        
        # Passa o mesmo código para os dois parâmetros
        cursor.execute(sql, (codigo, codigo))
        
        produto = cursor.fetchone()
        return produto
    except Exception as e:
        messagebox.showerror("Erro na comunicação de dados", f"Falha ao buscar produto por código: {e}")
        return None
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def atualizar_caminho_imagem_produto(ref_produto, caminho_imagem):
    """Atualiza o campo pro_caminho_imagem de um produto específico."""
    try:
        conn = conectar()
        if not conn: return False
        cursor = conn.cursor()
        sql = "UPDATE produtos SET pro_caminho_imagem = %s WHERE pro_ref = %s"
        cursor.execute(sql, (caminho_imagem, ref_produto))
        conn.commit()
        return True
    except Exception as e:
        messagebox.showerror("Erro na comunicação de dados", f"Falha ao atualizar caminho da imagem: {e}")
        return False
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def decrementar_estoque_item_inventario(id_inventario, sku_produto):
    """
    Decrementa em 1 a quantidade_sistema e, se não for nula, a quantidade_contada
    de um item específico no inventário ativo.
    """
    try:
        conn = conectar()
        if not conn: return False
        cursor = conn.cursor()

        # Descobre o pro_id para produtos conhecidos
        cursor.execute("SELECT pro_id FROM produtos WHERE pro_sku = %s", (sku_produto,))
        resultado_produto = cursor.fetchone()

        if resultado_produto:
            # Se o produto é conhecido, atualiza usando o pro_id
            pro_id = resultado_produto[0]
            sql = """
                UPDATE inventario_itens
                SET
                    quantidade_sistema = quantidade_sistema - 1,
                    quantidade_contada = IF(quantidade_contada IS NOT NULL, quantidade_contada - 1, NULL)
                WHERE inv_id = %s AND pro_id = %s
            """
            cursor.execute(sql, (id_inventario, pro_id))
        else:
            # Se o produto é desconhecido, atualiza usando o item_sku
            sql = """
                UPDATE inventario_itens
                SET
                    quantidade_sistema = quantidade_sistema - 1,
                    quantidade_contada = IF(quantidade_contada IS NOT NULL, quantidade_contada - 1, NULL)
                WHERE inv_id = %s AND item_sku = %s AND pro_id IS NULL
            """
            cursor.execute(sql, (id_inventario, sku_produto))
        
        conn.commit()
        return True
    except Exception as e:
        messagebox.showerror("Erro na comunicação de dados", f"Falha ao decrementar estoque do item: {e}")
        return False
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def incrementar_estoque_item_inventario(id_inventario, sku_produto):
    """
    Incrementa em 1 a quantidade_sistema e, se não for nula, a quantidade_contada
    de um item específico no inventário ativo (usado para devoluções).
    """
    try:
        conn = conectar()
        if not conn: return False
        cursor = conn.cursor()

        # Descobre o pro_id para produtos conhecidos
        cursor.execute("SELECT pro_id FROM produtos WHERE pro_sku = %s", (sku_produto,))
        resultado_produto = cursor.fetchone()

        if resultado_produto:
            # Se o produto é CONHECIDO, atualiza usando o pro_id
            pro_id = resultado_produto[0]
            sql = """
                UPDATE inventario_itens
                SET
                    quantidade_sistema = quantidade_sistema + 1,
                    quantidade_contada = IF(quantidade_contada IS NOT NULL, quantidade_contada + 1, NULL)
                WHERE inv_id = %s AND pro_id = %s
            """
            cursor.execute(sql, (id_inventario, pro_id))
        else:
            # Se o produto é DESCONHECIDO, atualiza usando o item_sku
            sql = """
                UPDATE inventario_itens
                SET
                    quantidade_sistema = quantidade_sistema + 1,
                    quantidade_contada = IF(quantidade_contada IS NOT NULL, quantidade_contada + 1, NULL)
                WHERE inv_id = %s AND item_sku = %s AND pro_id IS NULL
            """
            cursor.execute(sql, (id_inventario, sku_produto))
        
        conn.commit()
        return True
    except Exception as e:
        messagebox.showerror("Erro na comunicação de dados", f"Falha ao incrementar estoque do item: {e}")
        return False
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()