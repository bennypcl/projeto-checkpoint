import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttkb
from conexao import conectar
from crud import listar_produtos, listar_clientes
from ttkbootstrap.constants import *
import os
from PIL import Image, ImageTk

class Consultas:
    def __init__(self, master, mapa_imagens): # Adicionado mapa_imagens
        self.master = master
        self.mapa_imagens = mapa_imagens # Salva o mapa
        self.imagem_tk = None
        self.janela_selecao_produto = None
        self._callback_selecao = None
        self._is_formatting = False

    def _criar_janela_selecao_produto(self, parent):
        top = tk.Toplevel(parent)
        top.title("Consultar e Selecionar Produto")
        top.geometry("1100x700")
        top.transient(parent)
        top.columnconfigure(0, weight=3); top.columnconfigure(1, weight=1)
        top.rowconfigure(0, weight=1)

        # --- Frame da Esquerda (Lista) ---
        frame_esquerda = ttk.Frame(top); frame_esquerda.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        frame_esquerda.rowconfigure(1, weight=1); frame_esquerda.columnconfigure(0, weight=1)

        frame_busca = ttk.Frame(frame_esquerda); frame_busca.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        ttk.Label(frame_busca, text="Buscar:").pack(side=LEFT, padx=(0, 5))
        search_var = tk.StringVar(); entry_busca = ttk.Entry(frame_busca, textvariable=search_var)
        entry_busca.pack(fill=X, expand=True); entry_busca.focus_set()
        entry_busca.bind("<KeyRelease>", lambda event: _filtrar_produtos())

        frame_tree = ttk.Frame(frame_esquerda); frame_tree.grid(row=1, column=0, sticky="nsew")
        frame_tree.rowconfigure(0, weight=1); frame_tree.columnconfigure(0, weight=1)
        colunas = ('ref', 'sku', 'descricao', 'tamanho', 'preco')
        tree = ttk.Treeview(frame_tree, columns=colunas, show="headings")
        tree.grid(row=0, column=0, sticky="nsew")
        tree.heading('ref', text='Referência'); tree.column('ref', width=80); tree.heading('sku', text='SKU'); tree.column('sku', width=80); tree.heading('descricao', text='Descrição'); tree.column('descricao', width=300); tree.heading('tamanho', text='Tamanho'); tree.column('tamanho', width=80, anchor="center"); tree.heading('preco', text='Preço'); tree.column('preco', width=80, anchor="e")
        scrollbar = ttk.Scrollbar(frame_tree, orient="vertical", command=tree.yview); tree.configure(yscrollcommand=scrollbar.set); scrollbar.grid(row=0, column=1, sticky="ns")

        # --- Frame da Direita (Imagem) ---
        frame_direita = ttk.Frame(top, padding=10)
        frame_direita.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=10)
        frame_direita.rowconfigure(0, weight=1); frame_direita.columnconfigure(0, weight=1)
        lbl_imagem = ttk.Label(frame_direita, text="Selecione um produto", anchor="center", relief="solid")
        lbl_imagem.grid(row=0, column=0, sticky="nsew")

        # --- Lógica e Botões ---
        produtos_completos = listar_produtos()
        def _filtrar_produtos(event=None):
            termo_busca = search_var.get().upper(); tree.delete(*tree.get_children())
            for prod in produtos_completos:
                if (termo_busca in str(prod.get('pro_sku', '')).upper() or termo_busca in str(prod.get('pro_descricao', '')).upper() or termo_busca in str(prod.get('pro_ref', '')).upper()):
                    tree.insert('', END, values=(prod['pro_ref'], prod['pro_sku'], prod['pro_descricao'], prod['pro_tam'], f"{prod.get('pro_valor'):.2f}" if prod.get('pro_valor') is not None else "0.00"))
        _filtrar_produtos()

        # Vincula a seleção da lista à nova função de mostrar imagem
        tree.bind('<<TreeviewSelect>>', lambda e: self._mostrar_imagem_selecionada_consulta(e, tree, 0, lbl_imagem))

        frame_botoes = ttk.Frame(frame_esquerda); frame_botoes.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        def confirmar_selecao():
            selecionado = tree.selection();
            if not selecionado: return
            sku_selecionado = tree.item(selecionado[0])['values'][1]
            if self._callback_selecao: self._callback_selecao(sku_selecionado)
            top.grab_release(); top.withdraw()
        btn_selecionar = ttk.Button(frame_botoes, text="Selecionar", command=confirmar_selecao, bootstyle=PRIMARY); btn_selecionar.pack(side=RIGHT, padx=5)
        def cancelar_selecao(): top.grab_release(); top.withdraw()
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
        colunas_visiveis = ("Cargo", "Nome", "CPF")

        # Esconder a coluna 'ID'
        tree = ttk.Treeview(janela_usuarios, columns=colunas, show="headings", displaycolumns=colunas_visiveis)

        for col in colunas_visiveis:
            tree.heading(col, text=col)
            if col == "Nome":
                tree.column(col, anchor="w", width=250) # Alinha o nome à esquerda
            else:
                tree.column(col, anchor="center", width=120)

        for linha in dados:
            tree.insert("", "end", values=linha)

        tree.pack(fill="both", expand=True, padx=10, pady=10)

    def visualizar_clientes(self):
        janela_clientes = ttkb.Toplevel(self.master)
        janela_clientes.title("Visualizar Clientes")
        janela_clientes.state('zoomed')

        # --- Frame de Busca ---
        frame_busca = ttk.Frame(janela_clientes, padding=(10, 10, 10, 0))
        frame_busca.pack(fill=X)
        ttk.Label(frame_busca, text="Buscar:").pack(side=LEFT, padx=(0, 5))

        search_var = tk.StringVar()
        entry_busca = ttk.Entry(frame_busca, textvariable=search_var)
        entry_busca.pack(fill=X, expand=True)
        entry_busca.focus_set()
        search_var.trace_add('write',
            lambda *args: self._formatar_para_maiusculo(search_var, entry_busca))

        # --- Frame do Treeview ---
        frame_tree = ttk.Frame(janela_clientes)
        frame_tree.pack(fill="both", expand=True, padx=10, pady=10)

        colunas = ("CPF", "Nome", "Telefone", "Nascimento")
        tree = ttk.Treeview(frame_tree, columns=colunas, show="headings")

        tree.heading("CPF", text="CPF"); tree.column("CPF", anchor="center", width=140)
        tree.heading("Nome", text="Nome"); tree.column("Nome", anchor="w", width=300)
        tree.heading("Telefone", text="Telefone"); tree.column("Telefone", anchor="center", width=150)
        tree.heading("Nascimento", text="Data de Nascimento"); tree.column("Nascimento", anchor="center", width=150)

        tree.pack(side=LEFT, fill="both", expand=True)
        scrollbar = ttk.Scrollbar(frame_tree, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill="y")
        
        clientes_completos = listar_clientes()

        def _filtrar_clientes(event=None):
            termo_busca = search_var.get()
            termo_busca_numeros = "".join(filter(str.isdigit, termo_busca))
            tree.delete(*tree.get_children())

            for cliente in clientes_completos:
                #Formatação
                cpf_raw = str(cliente.get('cli_cpf', ''))
                cpf_formatado = f"{cpf_raw[:3]}.{cpf_raw[3:6]}.{cpf_raw[6:9]}-{cpf_raw[9:]}" if len(cpf_raw) == 11 else cpf_raw
                
                ddd = str(cliente.get('cli_ddd', ''))
                tel = str(cliente.get('cli_telefone', ''))
                telefone_formatado = ""
                if ddd and tel:
                    if len(tel) == 9:
                        telefone_formatado = f"({ddd}) {tel[:5]}-{tel[5:]}"
                    else:
                        telefone_formatado = f"({ddd}) {tel[:4]}-{tel[4:]}"

                data_nasc_obj = cliente.get('cli_data_nascimento')
                data_nasc_formatada = data_nasc_obj.strftime('%d/%m/%Y') if data_nasc_obj else ""
                
                nome_original = str(cliente.get('cli_nome', ''))
                telefone_numeros = ddd + tel

                if (termo_busca in nome_original or
                    (termo_busca_numeros and termo_busca_numeros in cpf_raw) or
                    (termo_busca_numeros and termo_busca_numeros in telefone_numeros)):
                    
                    valores = (
                        cpf_formatado,
                        nome_original,
                        telefone_formatado,
                        data_nasc_formatada
                    )
                    tree.insert("", "end", values=valores)
        
        entry_busca.bind("<KeyRelease>", _filtrar_clientes)
        _filtrar_clientes()

    def visualizar_produtos(self):
        janela_produtos = ttkb.Toplevel(self.master)
        janela_produtos.title("Visualizar Produtos")
        janela_produtos.state('zoomed')
        janela_produtos.columnconfigure(0, weight=3); janela_produtos.columnconfigure(1, weight=1)
        janela_produtos.rowconfigure(0, weight=1)

        # --- Frame da Esquerda (Lista) ---
        frame_esquerda = ttk.Frame(janela_produtos)
        frame_esquerda.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        frame_esquerda.rowconfigure(1, weight=1); frame_esquerda.columnconfigure(0, weight=1)
        
        frame_busca = ttk.Frame(frame_esquerda, padding=(0, 0, 0, 10)); frame_busca.grid(row=0, column=0, sticky="ew")
        ttk.Label(frame_busca, text="Buscar:").pack(side=LEFT, padx=(0, 5))
        search_var = tk.StringVar(); entry_busca = ttk.Entry(frame_busca, textvariable=search_var)
        entry_busca.pack(fill=X, expand=True); entry_busca.focus_set()
        entry_busca.bind("<KeyRelease>", lambda e: _filtrar_visualizacao())

        frame_tree = ttk.Frame(frame_esquerda); frame_tree.grid(row=1, column=0, sticky="nsew")
        frame_tree.rowconfigure(0, weight=1); frame_tree.columnconfigure(0, weight=1)
        
        colunas = ("ID", "Ref", "SKU", "Descrição", "Tamanho", "Valor")
        colunas_visiveis = ("Ref", "SKU", "Descrição", "Tamanho", "Valor")

        # Esconder a coluna 'ID'
        tree = ttk.Treeview(frame_tree, columns=colunas, show="headings", displaycolumns=colunas_visiveis)
        tree.grid(row=0, column=0, sticky="nsew")

        for col in colunas_visiveis:
            tree.heading(col, text=col)
            if col == "Descrição": tree.column(col, anchor="w", width=300)
            else: tree.column(col, anchor="center", width=80)
            
        scrollbar = ttk.Scrollbar(frame_tree, orient="vertical", command=tree.yview); tree.configure(yscrollcommand=scrollbar.set); scrollbar.grid(row=0, column=1, sticky="ns")

        # --- Frame da Direita (Imagem) ---
        frame_direita = ttk.Frame(janela_produtos, padding=10)
        frame_direita.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=10)
        frame_direita.rowconfigure(0, weight=1); frame_direita.columnconfigure(0, weight=1)
        lbl_imagem = ttk.Label(frame_direita, text="Selecione um produto", anchor="center", relief="solid")
        lbl_imagem.grid(row=0, column=0, sticky="nsew")

        produtos_completos = listar_produtos()
        def _filtrar_visualizacao(event=None):
            termo_busca = search_var.get().upper(); tree.delete(*tree.get_children())
            for prod in produtos_completos:
                if (termo_busca in str(prod.get('pro_ref', '')).upper() or termo_busca in str(prod.get('pro_sku', '')).upper() or termo_busca in str(prod.get('pro_descricao', '')).upper() or termo_busca in str(prod.get('pro_bipe', '')).upper()):
                    valores = (prod['pro_id'], prod.get('pro_ref', ''), prod.get('pro_sku', ''), prod.get('pro_descricao', ''), prod.get('pro_tam', ''), prod.get('pro_valor')); 
                    tree.insert("", "end", values=valores)
        _filtrar_visualizacao()
        
        tree.bind('<<TreeviewSelect>>', lambda e: self._mostrar_imagem_selecionada_consulta(e, tree, 1, lbl_imagem))

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

    def _formatar_para_maiusculo(self, string_var, entry_widget):
        if self._is_formatting:
            return
        self._is_formatting = True
        
        texto = string_var.get()
        texto_maiusculo = texto.upper()
        string_var.set(texto_maiusculo)
        
        if entry_widget.winfo_exists():
            entry_widget.after(1, lambda: entry_widget.icursor(len(texto_maiusculo)))

        self._is_formatting = False

    def _mostrar_imagem_selecionada_consulta(self, event, treeview, ref_column_index, image_label):
        selecao = treeview.selection()
        if not selecao: return

        item_iid = selecao[0]
        try:
            # Pega a referência da coluna correta
            ref_produto = treeview.item(item_iid, "values")[ref_column_index]
        except IndexError:
            return

        caminho_relativo = self.mapa_imagens.get(ref_produto)
        if caminho_relativo:
            try:
                # O caminho parte da pasta 'codigos'
                script_dir = os.path.dirname(__file__)
                caminho_absoluto = os.path.join(script_dir, caminho_relativo)

                img_pil = Image.open(caminho_absoluto)
                img_pil.thumbnail((250, 250)) # Define um tamanho máximo para a imagem
                self.imagem_tk = ImageTk.PhotoImage(img_pil)
                image_label.config(image=self.imagem_tk, text="")
            except Exception:
                image_label.config(image='', text="Erro ao carregar\nimagem.")
        else:
            image_label.config(image='', text="Produto sem imagem\ncadastrada.")

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
