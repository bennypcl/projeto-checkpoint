import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttkb
from conexao import conectar
from crud import listar_produtos
from ttkbootstrap.constants import *

class Consultas:
    def __init__(self, master):
        self.master = master # Referência à janela principal (log_tela)
        self.janela_selecao_produto = None
        self._callback_selecao = None

    def _criar_janela_selecao_produto(self, parent):
        """Função interna para criar a interface da janela de seleção apenas uma vez."""
        top = tk.Toplevel(parent)
        top.title("Consultar e Selecionar Produto")
        top.geometry("800x600")
        top.transient(parent)

        # Treeview para mostrar os produtos
        colunas = ('sku', 'descricao', 'tamanho', 'preco', 'quant')
        tree = ttk.Treeview(top, columns=colunas, show="headings")
        tree.pack(fill=BOTH, expand=True, padx=10, pady=10)

        tree.heading('sku', text='SKU')
        tree.column('sku', width=100)
        tree.heading('descricao', text='Descrição')
        tree.column('descricao', width=350)
        
        tree.heading('tamanho', text='Tamanho')
        tree.column('tamanho', width=80, anchor="center")        
        tree.heading('preco', text='Preço')
        tree.column('preco', width=100, anchor="e")
        tree.heading('quant', text='Estoque')
        tree.column('quant', width=100, anchor="center")

        # Popula o Treeview com dados do banco
        produtos = listar_produtos()
        for prod in produtos:
            tree.insert('', END, values=(
                prod['pro_sku'], 
                prod['pro_descricao'], 
                prod['pro_tam'],
                f"{prod['pro_valor']:.2f}", 
                prod['pro_quant']
            ))

        def confirmar_selecao():
            selecionado = tree.selection()
            if not selecionado: return
            sku_selecionado = tree.item(selecionado[0])['values'][0]
            if self._callback_selecao:
                self._callback_selecao(sku_selecionado)
            top.grab_release()
            top.withdraw()

        def cancelar_selecao():
            top.grab_release()
            top.withdraw()

        frame_botoes = ttk.Frame(top)
        frame_botoes.pack(fill=X, padx=10, pady=5)
        btn_selecionar = ttk.Button(frame_botoes, text="Selecionar", command=confirmar_selecao, bootstyle=PRIMARY)
        btn_selecionar.pack(side=RIGHT, padx=5)
        ttk.Button(frame_botoes, text="Cancelar", command=cancelar_selecao, bootstyle=(SECONDARY, OUTLINE)).pack(side=RIGHT)
        tree.bind("<Double-1>", lambda event: btn_selecionar.invoke())
        top.protocol("WM_DELETE_WINDOW", cancelar_selecao)
        return top

    def selecionar_produto(self, parent, callback):
        """Abre a janela de seleção, criando-a se necessário."""
        self._callback_selecao = callback

        if self.janela_selecao_produto is None or not tk.Toplevel.winfo_exists(self.janela_selecao_produto):
            self.janela_selecao_produto = self._criar_janela_selecao_produto(parent) # Passa o parent adiante
        else:
            self.janela_selecao_produto.deiconify()
            self.janela_selecao_produto.lift()

        self.janela_selecao_produto.grab_set()

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
            cursor.execute("SELECT pro_id, pro_ref, pro_sku, pro_descricao, pro_tam, pro_quant, pro_valor FROM produtos")
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

        colunas = ("ID", "Ref", "SKU", "Descrição", "Tamanho", "Quantidade", "Valor")
        tree = ttk.Treeview(janela_produtos, columns=colunas, show="headings")

        for col in colunas:
            tree.heading(col, text=col)
            # Ajuste para a coluna Descrição ser maior
            if col == "Descrição":
                tree.column(col, anchor="w", width=300)
            else:
                tree.column(col, anchor="center", width=100)


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
