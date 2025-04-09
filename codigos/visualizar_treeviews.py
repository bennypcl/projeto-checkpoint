import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttkb
from conexao_banco import conectar

class Consultas:
    def __init__(self, master):
        self.master = master

    def visualizar_usuarios(self):
        # Conecta ao banco
        conexao = conectar()
        if conexao is None:
            return
        cursor = conexao.cursor()
        try:
            cursor.execute("SELECT usu_id, usu_cargo, usu_nome, usu_cpf FROM usuarios")
            dados = cursor.fetchall()
        except Exception as e:
            print(f"Erro ao executar a consulta de usuários: {e}")
            return
        finally:
            if cursor:
                cursor.close()
            if conexao and conexao.is_connected():
                conexao.close()

        # Cria janela Toplevel
        janela_usuarios = ttkb.Toplevel(self.master, title="Visualizar Usuários", themename="flatly")
        janela_usuarios.geometry("700x400")

        # Define colunas
        colunas = ("ID", "Cargo", "Nome", "CPF")

        tree = ttk.Treeview(janela_usuarios, columns=colunas, show="headings")

        for col in colunas:
            tree.heading(col, text=col)
            tree.column(col, anchor="center")

        # Inserir dados
        for linha in dados:
            tree.insert("", "end", values=linha)

        tree.pack(fill="both", expand=True)

    def visualizar_clientes(self):
        # Conecta ao banco
        conexao = conectar()
        if conexao is None:
            return
        cursor = conexao.cursor()
        try:
            cursor.execute("SELECT cli_id, cli_nome, cli_cpf, cli_email FROM clientes")
            dados = cursor.fetchall()
        except Exception as e:
            print(f"Erro ao executar a consulta de clientes: {e}")
            return
        finally:
            if cursor:
                cursor.close()
            if conexao and conexao.is_connected():
                conexao.close()

        # Cria janela Toplevel
        janela_clientes = ttkb.Toplevel(self.master, title="Visualizar Clientes", themename="flatly")
        janela_clientes.geometry("800x500")

        # Define colunas (selecione as colunas que você quer visualizar)
        colunas = ("ID", "Nome", "CPF", "Email")

        tree = ttk.Treeview(janela_clientes, columns=colunas, show="headings")

        for col in colunas:
            tree.heading(col, text=col)
            tree.column(col, anchor="center")

        # Inserir dados
        for linha in dados:
            tree.insert("", "end", values=linha)

        tree.pack(fill="both", expand=True)

    def visualizar_produtos(self):
        conexao = conectar()
        if conexao is None:
            return
        cursor = conexao.cursor()
        try:
            cursor.execute("SELECT pro_id, pro_ref, pro_sku, pro_descricao, pro_quant, pro_valor FROM produtos")
            dados = cursor.fetchall()
        except Exception as e:
            print(f"Erro ao executar a consulta de produtos: {e}")
            return
        finally:
            if cursor:
                cursor.close()
            if conexao and conexao.is_connected():
                conexao.close()

        janela_produtos = ttkb.Toplevel(self.master, title="Visualizar Produtos", themename="flatly")
        janela_produtos.geometry("900x500")

        colunas = ("ID", "Ref", "SKU", "Descrição", "Quantidade", "Valor")

        tree = ttk.Treeview(janela_produtos, columns=colunas, show="headings")

        for col in colunas:
            tree.heading(col, text=col)
            tree.column(col, anchor="center")

        for linha in dados:
            tree.insert("", "end", values=linha)

        tree.pack(fill="both", expand=True)

    def visualizar_pedidos(self):
        conexao = conectar()
        if conexao is None:
            return
        cursor = conexao.cursor()
        try:
            cursor.execute("""
                SELECT
                    p.ped_id AS ID,
                    c.cli_nome AS Cliente,
                    u.usu_nome AS Vendedor,
                    p.ped_data AS Data,
                    p.ped_total AS Total
                FROM pedidos p
                LEFT JOIN clientes c ON p.cli_id = c.cli_id
                INNER JOIN usuarios u ON p.usu_id = u.usu_id
            """)
            dados = cursor.fetchall()
        except Exception as e:
            print(f"Erro ao executar a consulta de pedidos: {e}")
            return
        finally:
            if cursor:
                cursor.close()
            if conexao and conexao.is_connected():
                conexao.close()

        janela_pedidos = ttkb.Toplevel(self.master, title="Visualizar Pedidos", themename="flatly")
        janela_pedidos.geometry("1000x600")

        colunas = ("ID", "Cliente", "Vendedor", "Data", "Total")

        tree = ttk.Treeview(janela_pedidos, columns=colunas, show="headings")

        for col in colunas:
            tree.heading(col, text=col)
            tree.column(col, anchor="center")

        for linha in dados:
            tree.insert("", "end", values=linha)

        tree.pack(fill="both", expand=True)

    def visualizar_itens_pedido(self):
        conexao = conectar()
        if conexao is None:
            return
        cursor = conexao.cursor()
        try:
            cursor.execute("""
                SELECT
                    ip.item_id AS ID,
                    p.ped_id AS PedidoID,
                    prod.pro_descricao AS Produto,
                    ip.item_quant AS Quantidade,
                    ip.item_valor_unitario AS ValorUnitario
                FROM itens_pedido ip
                INNER JOIN pedidos p ON ip.ped_id = p.ped_id
                INNER JOIN produtos prod ON ip.pro_id = prod.pro_id
            """)
            dados = cursor.fetchall()
        except Exception as e:
            print(f"Erro ao executar a consulta de itens do pedido: {e}")
            return
        finally:
            if cursor:
                cursor.close()
            if conexao and conexao.is_connected():
                conexao.close()

        janela_itens_pedido = ttkb.Toplevel(self.master, title="Visualizar Itens do Pedido", themename="flatly")
        janela_itens_pedido.geometry("900x500")

        colunas = ("ID", "Pedido ID", "Produto", "Quantidade", "Valor Unitário")

        tree = ttk.Treeview(janela_itens_pedido, columns=colunas, show="headings")

        for col in colunas:
            tree.heading(col, text=col)
            tree.column(col, anchor="center")

        for linha in dados:
            tree.insert("", "end", values=linha)

        tree.pack(fill="both", expand=True)

    def visualizar_pagamentos(self):
        conexao = conectar()
        if conexao is None:
            return
        cursor = conexao.cursor()
        try:
            cursor.execute("""
                SELECT
                    pag_id AS ID,
                    ped_id AS PedidoID,
                    pag_metodo AS Metodo,
                    pag_valor AS Valor
                FROM pagamentos
            """)
            dados = cursor.fetchall()
        except Exception as e:
            print(f"Erro ao executar a consulta de pagamentos: {e}")
            return
        finally:
            if cursor:
                cursor.close()
            if conexao and conexao.is_connected():
                conexao.close()

        janela_pagamentos = ttkb.Toplevel(self.master, title="Visualizar Pagamentos", themename="flatly")
        janela_pagamentos.geometry("700x400")

        colunas = ("ID", "Pedido ID", "Método", "Valor")

        tree = ttk.Treeview(janela_pagamentos, columns=colunas, show="headings")

        for col in colunas:
            tree.heading(col, text=col)
            tree.column(col, anchor="center")

        for linha in dados:
            tree.insert("", "end", values=linha)

        tree.pack(fill="both", expand=True)

    def visualizar_temas(self):
        conexao = conectar()
        if conexao is None:
            return
        cursor = conexao.cursor()
        try:
            cursor.execute("SELECT tema_id AS ID, tema_nome AS Nome, valor AS Valor FROM temas")
            dados = cursor.fetchall()
        except Exception as e:
            print(f"Erro ao executar a consulta de temas: {e}")
            return
        finally:
            if cursor:
                cursor.close()
            if conexao and conexao.is_connected():
                conexao.close()

        janela_temas = ttkb.Toplevel(self.master, title="Visualizar Temas", themename="flatly")
        janela_temas.geometry("400x300")

        colunas = ("ID", "Nome", "Valor")

        tree = ttk.Treeview(janela_temas, columns=colunas, show="headings")

        for col in colunas:
            tree.heading(col, text=col)
            tree.column(col, anchor="center")

        for linha in dados:
            tree.insert("", "end", values=linha)

        tree.pack(fill="both", expand=True)

# Para testar este módulo diretamente:
if __name__ == "__main__":
    root = ttkb.Window(themename="flatly")
    app = Consultas(root)

    btn_usuarios = ttk.Button(root, text="Visualizar Usuários", command=app.visualizar_usuarios)
    btn_usuarios.pack(pady=5)

    btn_clientes = ttk.Button(root, text="Visualizar Clientes", command=app.visualizar_clientes)
    btn_clientes.pack(pady=5)

    btn_produtos = ttk.Button(root, text="Visualizar Produtos", command=app.visualizar_produtos)
    btn_produtos.pack(pady=5)

    btn_pedidos = ttk.Button(root, text="Visualizar Pedidos", command=app.visualizar_pedidos)
    btn_pedidos.pack(pady=5)

    btn_itens_pedido = ttk.Button(root, text="Visualizar Itens do Pedido", command=app.visualizar_itens_pedido)
    btn_itens_pedido.pack(pady=5)

    btn_pagamentos = ttk.Button(root, text="Visualizar Pagamentos", command=app.visualizar_pagamentos)
    btn_pagamentos.pack(pady=5)

    btn_temas = ttk.Button(root, text="Visualizar Temas", command=app.visualizar_temas)
    btn_temas.pack(pady=5)

    