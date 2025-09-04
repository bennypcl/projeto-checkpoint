import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttkb
from conexao import conectar

class Consultas:
    def __init__(self, master):
        self.master = master

    def visualizar_usuarios(self):
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
            cursor.close()
            conexao.close()

        janela_usuarios = tk.Toplevel(self.master)
        janela_usuarios.geometry("700x600")
        janela_usuarios.title("Visualizar Funcionários")

        colunas = ("ID", "Cargo", "Nome", "CPF")
        tree = ttk.Treeview(janela_usuarios, columns=colunas, show="headings")

        for col in colunas:
            tree.heading(col, text=col)
            tree.column(col, anchor="center")

        for linha in dados:
            tree.insert("", "end", values=linha)

        tree.pack(fill="both", expand=True)

    def visualizar_clientes(self):
        conexao = conectar()
        if conexao is None:
            return
        cursor = conexao.cursor()
        try:
            cursor.execute("SELECT cli_id, cli_nome, cli_cpf, cli_data_nascimento FROM clientes")
            dados = cursor.fetchall()
        except Exception as e:
            print(f"Erro ao executar a consulta de clientes: {e}")
            return
        finally:
            cursor.close()
            conexao.close()

        janela_clientes = ttkb.Toplevel(self.master)
        janela_clientes.title("Visualizar Clientes")
        janela_clientes.geometry("800x500")

        colunas = ("ID", "Nome", "CPF", "Data de Nascimento")
        tree = ttk.Treeview(janela_clientes, columns=colunas, show="headings")

        for col in colunas:
            tree.heading(col, text=col)
            tree.column(col, anchor="center")

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
            cursor.close()
            conexao.close()

        janela_produtos = ttkb.Toplevel(self.master)
        janela_produtos.title("Visualizar Produtos")
        janela_produtos.geometry("900x700")

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
                    p.ped_id,
                    c.cli_nome,
                    u.usu_nome,
                    p.ped_data,
                    p.ped_total
                FROM pedidos p
                LEFT JOIN clientes c ON p.cli_id = c.cli_id
                INNER JOIN usuarios u ON p.usu_id = u.usu_id
            """)
            dados = cursor.fetchall()
        except Exception as e:
            print(f"Erro ao executar a consulta de pedidos: {e}")
            return
        finally:
            cursor.close()
            conexao.close()
        janela_pedidos = ttkb.Toplevel(self.master)
        janela_pedidos.title("Visualizar Pedidos")
        janela_pedidos.geometry("1000x800")

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
                    ip.item_id,
                    p.ped_id,
                    prod.pro_descricao,
                    ip.item_quant,
                    ip.item_valor_unitario
                FROM itens_pedido ip
                INNER JOIN pedidos p ON ip.ped_id = p.ped_id
                INNER JOIN produtos prod ON ip.pro_id = prod.pro_id
            """)
            dados = cursor.fetchall()
        except Exception as e:
            print(f"Erro ao executar a consulta de itens do pedido: {e}")
            return
        finally:
            cursor.close()
            conexao.close()

        janela_itens_pedido = ttkb.Toplevel(self.master)
        janela_itens_pedido.title("Visualizar Itens dos Pedidos")
        janela_itens_pedido.geometry("900x700")

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
                    pag_id,
                    ped_id,
                    pag_metodo,
                    pag_valor
                FROM pagamentos
            """)
            dados = cursor.fetchall()
        except Exception as e:
            print(f"Erro ao executar a consulta de pagamentos: {e}")
            return
        finally:
            cursor.close()
            conexao.close()

        janela_pagamentos = ttkb.Toplevel(self.master)
        janela_pagamentos.title("Visualizar Pagamentos")
        janela_pagamentos.geometry("700x600")

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
            cursor.execute("SELECT tema_id, tema_nome, valor FROM temas")
            dados = cursor.fetchall()
        except Exception as e:
            print(f"Erro ao executar a consulta de temas: {e}")
            return
        finally:
            cursor.close()
            conexao.close()

        janela_temas = ttkb.Toplevel(self.master)
        janela_temas.title("Visualizar Temas")
        janela_temas.geometry("400x400")

        colunas = ("ID", "Nome", "Valor")
        tree = ttk.Treeview(janela_temas, columns=colunas, show="headings")

        for col in colunas:
            tree.heading(col, text=col)
            tree.column(col, anchor="center")

        for linha in dados:
            tree.insert("", "end", values=linha)

        tree.pack(fill="both", expand=True)

# Execução de testes
# if __name__ == "__main__":
#     root = ttkb.Window(themename="flatly")
#     app = Consultas(root)

#     ttk.Button(root, text="Visualizar Usuários", command=app.visualizar_usuarios).pack(pady=5)
#     ttk.Button(root, text="Visualizar Clientes", command=app.visualizar_clientes).pack(pady=5)
#     ttk.Button(root, text="Visualizar Produtos", command=app.visualizar_produtos).pack(pady=5)
#     ttk.Button(root, text="Visualizar Pedidos", command=app.visualizar_pedidos).pack(pady=5)
#     ttk.Button(root, text="Visualizar Itens do Pedido", command=app.visualizar_itens_pedido).pack(pady=5)
#     ttk.Button(root, text="Visualizar Pagamentos", command=app.visualizar_pagamentos).pack(pady=5)
#     ttk.Button(root, text="Visualizar Temas", command=app.visualizar_temas).pack(pady=5)

#     root.mainloop()
