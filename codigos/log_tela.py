import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, simpledialog, Toplevel, StringVar
from PIL import Image, ImageTk
from conexao import conectar
import crud
import os

from temas import GerenciadorTema
from tela_ponto_venda import TelaPontoVenda
from relatorio_pdf import gerar_relatorio_pdf
from visualizar_treeviews import Consultas
from tela_relatorio_vendas import TelaRelatorioVendas

class Tela:
    def __init__(self, master):
        self.janela = master
        self.janela.title('Checkpoint')
        self.janela.state('zoomed')

        self.vendas_realizadas = []
        self.mapa_imagens = {}
        self.imagem_tk = None
        self.frm_imagem_display = None

        self._is_formatting = False
        self.user_var = tk.StringVar()
        self.senha_var = tk.StringVar()

        self.log = ttk.Frame(self.janela, width=200, height=300)
        self.log.place(relx=0.5, rely=0.5, anchor="center")
        
        self.lbl_user = ttk.Label(self.log, text='Usuário:                     ', font=("Arial", 14))
        self.lbl_user.grid(row=0, column=0, columnspan=2, sticky="w")
        
        self.user_ent = tk.Entry(self.log, textvariable=self.user_var)
        self.user_ent.grid(row=1, column=0, columnspan=2, pady=5, ipady=5, ipadx=14, sticky='EW')
        self.user_ent.focus_set()
        self.user_var.trace_add('write', 
            lambda *args: self._formatar_para_maiusculo(self.user_var, self.user_ent))

        self.lbl_senha = ttk.Label(self.log, text='Senha:', font=("Arial", 14))
        self.lbl_senha.grid(row=2, column=0, sticky="w")
        
        # CONECTANDO O CAMPO DE SENHA À VARIÁVEL
        self.ent_senha = tk.Entry(self.log, show="*", textvariable=self.senha_var)
        self.ent_senha.grid(row=3, column=0, columnspan=2, pady=5, ipady=5, ipadx=14, sticky='EW')

        # OBSERVADOR (TRACE) PARA A SENHA
        self.senha_var.trace_add('write',
            lambda *args: self._formatar_para_maiusculo(self.senha_var, self.ent_senha))
        
        self.btn_entrar = tk.Button(self.log, text='Entrar', bg='darkblue', fg='white', font=("Arial", 14), command=self.autentica)
        self.btn_entrar.grid(row=4, column=0, columnspan=2, pady=10)
        self.janela.bind('<Return>', self.autentica)
        
        self.dados_originais = []
        self.novo_item_contador = 0
        self.gerenciador_tema = GerenciadorTema(self.janela)
        self.tela_relatorio_vendas = TelaRelatorioVendas(self.janela)
        self.tela_consulta = Consultas(self.janela)
        self.tela_venda = TelaPontoVenda(self.janela, self.vendas_realizadas, self.tela_consulta)
        self.relatorio = gerar_relatorio_pdf

    def carregar_mapa_de_imagens(self):
        self.mapa_imagens.clear()
        try:
            conn = conectar()
            if conn:
                cursor = conn.cursor()
                query = "SELECT pro_ref, pro_caminho_imagem FROM produtos WHERE pro_caminho_imagem IS NOT NULL AND pro_caminho_imagem != ''"
                cursor.execute(query)
                for pro_ref, pro_caminho_imagem in cursor:
                    self.mapa_imagens[pro_ref] = pro_caminho_imagem
                print(f"Mapa de imagens carregado com {len(self.mapa_imagens)} item(s).")
        except Exception as e:
            messagebox.showerror("Erro de Banco de Dados", f"Não foi possível carregar as imagens dos produtos: {e}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()

    def _formatar_para_maiusculo(self, string_var, entry_widget):
        # Se a função já estiver em execução, não faz nada (evita loop infinito)
        if self._is_formatting:
            return

        self._is_formatting = True  # Avisa que a formatação começou
        
        texto = string_var.get()
        texto_maiusculo = texto.upper()
        string_var.set(texto_maiusculo)
        
        # Move o cursor para o final, verificando se o widget ainda existe
        if entry_widget.winfo_exists():
            entry_widget.after(1, lambda: entry_widget.icursor(len(texto_maiusculo)))

        self._is_formatting = False # Avisa que a formatação terminou

    def autentica(self, event=None):
        # Lendo os valores das StringVars
        usuario = self.user_var.get()
        senha = self.senha_var.get()

        # Como os campos já forçam para maiúsculo, a verificação fica simples
        if usuario == "ADM" and senha == "ADM":
            self.carregar_mapa_de_imagens()
            self.menu()
            self.janela.unbind('<Return>')
        else:
            messagebox.showwarning("Atenção!", "Verificar credenciais.")

    def menu(self):
        self.log.destroy()
        self.tpl_menu = self.janela
        self.tpl_menu.title("Controle de Inventário")
        self.mnu_principal = tk.Menu(self.tpl_menu)
        self.mnu_inventario = tk.Menu(self.mnu_principal, tearoff=0); self.mnu_principal.add_cascade(label='Inventário', menu=self.mnu_inventario)
        self.mnu_inventario.add_command(label='Recarregar Interface', command=self.interacao_inventario)
        self.mnu_pt_vendas = tk.Menu(self.mnu_principal, tearoff=0); self.mnu_principal.add_cascade(label='Ponto de Venda', menu=self.mnu_pt_vendas)
        self.mnu_pt_vendas.add_command(label='Nova Venda', command=self.tela_venda.iniciar_pdv)
        self.mnu_configuracao = tk.Menu(self.mnu_principal, tearoff=0); self.mnu_principal.add_cascade(label='Configurações', menu=self.mnu_configuracao)
        self.mnu_configuracao.add_command(label='Temas', command=self.gerenciador_tema.mudar_tema)
        self.mnu_relatorios = tk.Menu(self.mnu_principal, tearoff=0); self.mnu_principal.add_cascade(label='Relatórios', menu=self.mnu_relatorios)
        self.mnu_relatorios.add_command(label='Divergências', command=self.abrir_tela_relatorio)
        self.mnu_relatorios.add_command(label='Vendas', command=self.tela_relatorio_vendas.mostrar_janela)

        self.mnu_treeviews = tk.Menu(self.mnu_principal, tearoff=0)
        self.mnu_principal.add_cascade(label='Consultas', menu=self.mnu_treeviews)
        self.mnu_treeviews.add_command(label='Funcionários', command=self.tela_consulta.visualizar_usuarios)
        self.mnu_treeviews.add_command(label='Clientes', command=self.tela_consulta.visualizar_clientes)
        self.mnu_treeviews.add_command(label='Produtos', command=self.tela_consulta.visualizar_produtos)
        self.tpl_menu.config(menu=self.mnu_principal)
        self.frm_principal_inventario = ttk.Frame(self.tpl_menu)
        self.frm_principal_inventario.pack(fill=BOTH, expand=True, padx=10, pady=10)
        self.interacao_inventario()

    def interacao_inventario(self):
        for widget in self.frm_principal_inventario.winfo_children():
            widget.destroy()

        self.frm_principal_inventario.columnconfigure(0, weight=3)
        self.frm_principal_inventario.columnconfigure(1, weight=1)
        self.frm_principal_inventario.rowconfigure(0, weight=1)

        frm_controles_e_lista = ttk.Frame(self.frm_principal_inventario)
        frm_controles_e_lista.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        frm_controles_e_lista.rowconfigure(1, weight=1)
        frm_controles_e_lista.columnconfigure(0, weight=1)
        
        frm_controle = ttk.Frame(frm_controles_e_lista); frm_controle.grid(row=0, column=0, sticky="ew", pady=(10,0))
        self.btn_ad_arquivo = ttk.Button(frm_controle, text='Carregar Inventário (.txt)', command=self.upp_arquivo); self.btn_ad_arquivo.pack(side=LEFT, padx=5)
        self.btn_ad_contagem = ttk.Button(frm_controle, text='Conta Est. por SKU', command=self.contar_sku); self.btn_ad_contagem.pack(side=RIGHT, padx=5)
        self.modificador_var = tk.IntVar(value=1)
        self.spn_modificador = ttk.Spinbox(frm_controle, from_=1, to=10, textvariable=self.modificador_var, width=2); self.spn_modificador.pack(side=RIGHT, padx=2.5)
        self.ent_ad_contagem = ttk.Entry(frm_controle); self.ent_ad_contagem.pack(side=RIGHT, padx=2.5)
        self.ent_ad_contagem.bind('<Return>', self.contar_sku)

        
        frm_treeview = ttk.Frame(frm_controles_e_lista); frm_treeview.grid(row=1, column=0, sticky="nsew", pady=10); frm_treeview.rowconfigure(0, weight=1); frm_treeview.columnconfigure(0, weight=1)
        colunas = ("ref", "sku", "desc", "tam", "preco", "est", "est_real")
        self.tvw_inventario = ttk.Treeview(frm_treeview, columns=colunas, show="headings", height=15)
        
        self.tvw_inventario.tag_configure("sigla_pdv", background="yellow")
        self.tvw_inventario.tag_configure("zerado", background="lightgray")
        self.tvw_inventario.tag_configure("diferente", background="red", foreground="white")
        self.tvw_inventario.tag_configure("igual", background="lightgreen")
        # Tags compostas foram removidas para simplificar, a lógica de múltiplas tags já cobre isso
        
        self.tvw_inventario.heading("ref", text="Ref"); self.tvw_inventario.column("ref", width=70, anchor=CENTER)
        self.tvw_inventario.heading("sku", text="SKU"); self.tvw_inventario.column("sku", width=70, anchor=CENTER)
        self.tvw_inventario.heading("desc", text="Descrição"); self.tvw_inventario.column("desc", width=300)
        self.tvw_inventario.heading("tam", text="Tam/Cap"); self.tvw_inventario.column("tam", width=100)
        self.tvw_inventario.heading("preco", text="Preço"); self.tvw_inventario.column("preco", width=80, anchor=E)
        self.tvw_inventario.heading("est", text="Estoque"); self.tvw_inventario.column("est", width=100, anchor=CENTER)
        self.tvw_inventario.heading("est_real", text="Est. Real"); self.tvw_inventario.column("est_real", width=100, anchor=CENTER)
        scrollbar_y = ttk.Scrollbar(frm_treeview, orient="vertical", command=self.tvw_inventario.yview)
        self.tvw_inventario.configure(yscrollcommand=scrollbar_y.set)
        self.tvw_inventario.grid(row=0, column=0, sticky="nsew"); scrollbar_y.grid(row=0, column=1, sticky="ns")

        # AÇÕES
        frm_filtros_acoes = ttk.Frame(frm_controles_e_lista)
        frm_filtros_acoes.grid(row=2, column=0, sticky="ew", pady=(0, 10), padx=5)
        frm_filtros_acoes.columnconfigure(0, weight=1)
        frm_acoes = ttk.Frame(frm_filtros_acoes); frm_acoes.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        frm_acoes.columnconfigure(1, weight=1)
        self.lbl_acao = ttk.Label(frm_acoes, text="Ações:"); self.lbl_acao.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.btn_add_produto = ttk.Button(frm_acoes, text="Adicionar Novo Produto", command=self.adicionar_produto); self.btn_add_produto.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        
        # FILTROS
        frm_filtros = ttk.Frame(frm_filtros_acoes); frm_filtros.grid(row=1, column=0, sticky="ew")
        self.lbl_visual = ttk.Label(frm_filtros, text="Filtrar Lista:"); self.lbl_visual.pack(side=TOP, anchor="w", padx=5, pady=5)
        frm_botoes_grid = ttk.Frame(frm_filtros); frm_botoes_grid.pack(fill=X, expand=True); frm_botoes_grid.columnconfigure(tuple(range(4)), weight=1)
        self.btn_todos = ttk.Button(frm_botoes_grid, text="Mostrar Todos", command=lambda: self.filtrar_treeview(None)); self.btn_todos.grid(row=0, column=0, padx=5, pady=3, sticky='ew')
        self.btn_pdv = ttk.Button(frm_botoes_grid, text="PDV", command=lambda: self.filtrar_treeview(("descricao", "pdv"))); self.btn_pdv.grid(row=0, column=1, padx=5, pady=3, sticky='ew')
        self.btn_negativos = ttk.Button(frm_botoes_grid, text="Negativados", command=lambda: self.filtrar_treeview(("quantidade", "<0"))); self.btn_negativos.grid(row=0, column=2, padx=5, pady=3, sticky='ew')
        self.btn_zerados = ttk.Button(frm_botoes_grid, text="Zerados", command=lambda: self.filtrar_treeview(("quantidade", "0"))); self.btn_zerados.grid(row=0, column=3, padx=5, pady=3, sticky='ew')
        self.btn_camisetas = ttk.Button(frm_botoes_grid, text="Camisetas", command=lambda: self.filtrar_treeview(("descricao", "Camiseta"))); self.btn_camisetas.grid(row=1, column=0, padx=5, pady=3, sticky='ew')
        self.btn_meias = ttk.Button(frm_botoes_grid, text="Meias", command=lambda: self.filtrar_treeview(("descricao", "Meia"))); self.btn_meias.grid(row=1, column=1, padx=5, pady=3, sticky='ew')
        self.btn_bones = ttk.Button(frm_botoes_grid, text="Bonés", command=lambda: self.filtrar_treeview(("descricao", "Boné"))); self.btn_bones.grid(row=1, column=2, padx=5, pady=3, sticky='ew')
        self.btn_copos = ttk.Button(frm_botoes_grid, text="Copos", command=lambda: self.filtrar_treeview(("descricao", "Copo"))); self.btn_copos.grid(row=1, column=3, padx=5, pady=3, sticky='ew')

        self.frm_imagem_display = ttk.Frame(self.frm_principal_inventario)
        self.frm_imagem_display.grid(row=0, column=1, sticky="nsew", pady=(10,0))
        self.frm_imagem_display.columnconfigure(0, weight=1); self.frm_imagem_display.rowconfigure(0, weight=1)
        self.lbl_imagem_produto = ttk.Label(self.frm_imagem_display, text="Selecione um produto", anchor="center", relief="solid", padding=5)
        self.lbl_imagem_produto.grid(row=0, column=0, sticky="nsew")

        self.tvw_inventario.bind("<Double-1>", self.editar_celula)
        self.tvw_inventario.bind('<<TreeviewSelect>>', self.mostrar_imagem_selecionada)
        
        self.filtrar_treeview(None)
    
    def abrir_tela_relatorio(self):
        if not self.dados_originais:
            messagebox.showwarning("Zero arquivos", "É necessário subir um arquivo para gerar o relatório de divergências.")
        else: self.tela_relatorio()

    def mostrar_imagem_selecionada(self, event=None):
        selecao = self.tvw_inventario.selection()
        if not selecao:
            self.lbl_imagem_produto.config(image='', text="Selecione um produto")
            return

        item_iid = selecao[0]
        try:
            ref_produto = self.tvw_inventario.item(item_iid, "values")[0]
        except IndexError:
            return

        caminho_relativo = self.mapa_imagens.get(ref_produto)
        if caminho_relativo:
            try:
                script_dir = os.path.dirname(__file__)
                caminho_absoluto = os.path.join(script_dir, caminho_relativo)
                img_pil = Image.open(caminho_absoluto)
                largura_painel = self.frm_imagem_display.winfo_width()
                altura_painel = self.frm_imagem_display.winfo_height()
                if largura_painel <= 1 or altura_painel <= 1:
                    largura_painel, altura_painel = 250, 250
                img_pil.thumbnail((largura_painel, altura_painel))
                self.imagem_tk = ImageTk.PhotoImage(img_pil)
                self.lbl_imagem_produto.config(image=self.imagem_tk, text="")
            except Exception as e:
                self.lbl_imagem_produto.config(image='', text=f"Erro ao carregar\nimagem: {e}")
        else:
            self.lbl_imagem_produto.config(image='', text="Produto sem imagem\ncadastrada no banco.")

    def _gerar_e_finalizar_relatorio(self):
        """
        Chama a geração do PDF, exibe uma mensagem de sucesso
        e fecha a janela de relatório.
        """
        # 1. Verifica se há dados para gerar o relatório
        if not self.divergencias and not self.negativados and not self.pdvs:
            messagebox.showwarning("Sem Dados", "Não há dados para gerar o relatório.", parent=self.tpl_relatorios)
            return

        try:
            # 2. Chama a função que gera o PDF e captura o nome do arquivo
            # self.relatorio é o seu gerar_relatorio_pdf
            nome_arquivo = self.relatorio(self.divergencias, self.negativados, self.pdvs)

            # 3. Exibe a mensagem de sucesso
            messagebox.showinfo("Sucesso", f"Relatório salvo com sucesso como:\n{nome_arquivo}")

            # 4. Fecha a janela de relatório
            self.tpl_relatorios.destroy()

        except Exception as e:
            messagebox.showerror("Erro ao Gerar PDF", f"Ocorreu um erro ao criar o arquivo PDF:\n{e}", parent=self.tpl_relatorios)

    def gerar_relatorio(self):
        if not self.divergencias:
            messagebox.showwarning("Aviso", "Nenhuma divergência encontrada.")
            return

        nome_arquivo = gerar_relatorio_pdf(self.divergencias)
        messagebox.showinfo("Relatório gerado", f"Relatório salvo como:\n{nome_arquivo}")
    
    def tela_relatorio(self):
        self.tpl_relatorios = tk.Toplevel(self.tpl_menu)
        self.tpl_relatorios.title("Relatório de Divergências")

        self.frm_principal_relDivergencia = ttk.Frame(self.tpl_relatorios, padding=10)
        self.frm_principal_relDivergencia.pack(fill=BOTH, expand=True)

        self.divergencias = []
        self.negativados = []
        self.pdvs = []

        def criar_treeview(rotulo, dados):
            ttk.Label(self.frm_principal_relDivergencia, text=rotulo, font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(10, 0))

            frame_tv = ttk.Frame(self.frm_principal_relDivergencia)
            frame_tv.pack(fill=BOTH, expand=True)

            colunas = ("ref", "sku", "desc", "tam", "est", "est_real")
            tree = ttk.Treeview(frame_tv, columns=colunas, show="headings", height=8)

            # Configura colunas
            for col, txt, width, align in [
                ("ref", "Ref", 70, CENTER),
                ("sku", "SKU", 70, CENTER),
                ("desc", "Descrição", 300, "w"),
                ("tam", "Tam/Cap", 100, CENTER),
                ("est", "Estoque", 100, CENTER),
                ("est_real", "Est. Real", 100, CENTER)
            ]:
                tree.heading(col, text=txt)
                tree.column(col, width=width, anchor=align)

            # Scrollbar vertical
            scrollbar_y = ttk.Scrollbar(frame_tv, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=scrollbar_y.set)

            # Layout
            tree.grid(row=0, column=0, sticky="nsew")
            scrollbar_y.grid(row=0, column=1, sticky="ns")
            frame_tv.rowconfigure(0, weight=1)
            frame_tv.columnconfigure(0, weight=1)

            # Inserção de dados
            for item in dados:
                tree.insert("", "end", values=item)

            return tree


        # --- Classificação dos dados ---
        for item in self.dados_originais:
            if len(item) < 8:
                continue

            iid, ref, sku, desc, tam, est, _, est_real = item

            desc_lower = str(desc).lower()
            est_str = str(est).strip()
            est_real_str = str(est_real).strip()

            # Verificações
            is_pdv = "pdv" in desc_lower
            is_negativado = False
            is_divergente = False
            try:
                est_int = int(est)
                est_real_int = int(est_real) if est_real_str else None
                is_negativado = est_int < 0
                is_divergente = est_real_str and (est_int != est_real_int)
            except:
                is_divergente = est_real_str and (est_str != est_real_str)

            valores = (ref, sku, desc, tam, est, est_real)

            if is_divergente:
                self.divergencias.append(valores)
            if is_negativado:
                self.negativados.append(valores)
            if is_pdv:
                self.pdvs.append(valores)

        # --- Cria Treeviews ---
        if self.divergencias:
            self.tvw_divergencias = criar_treeview("Produtos com divergência", self.divergencias)
        if self.negativados:
            self.tvw_negativados = criar_treeview("Produtos negativados", self.negativados)
        if self.pdvs:
            self.tvw_pdvs = criar_treeview("Produtos PDV", self.pdvs)

        # --- Botão PDF ---
        ttk.Button(
            self.frm_principal_relDivergencia,
            text="Gerar Relatório PDF",
            command=self._gerar_e_finalizar_relatorio).pack(pady=(20, 0))

    def upp_arquivo(self):
        caminho_arquivo = filedialog.askopenfilename(title="Selecione o Arquivo de Inventário (.txt)", filetypes=[("Arquivos de texto", "*.txt")])
        if not caminho_arquivo: return
        self.dados_originais.clear()
        try:
            with open(caminho_arquivo, "r", encoding="utf-8") as f:
                for i, linha in enumerate(f):
                    linha = linha.strip()
                    if not linha: continue
                    campos = [campo.strip() for campo in linha.split(';')]
                    if len(campos) == 6:
                        ref, sku, desc, tam, quant_str, valor_str = campos
                        try:
                            quant = int(quant_str)
                            valor = float(valor_str.replace(',', '.'))
                            iid = f"file_{i}"
                            self.dados_originais.append([iid, ref, sku, desc, tam, quant, valor, ""])
                        except ValueError:
                            print(f"AVISO: Linha {i+1} ignorada - valor/quantidade inválido: {linha}")
                            continue
            self.filtrar_treeview(None)
        except Exception as e:
            messagebox.showerror("Erro de Leitura", f"Não foi possível ler o arquivo:\n{e}")

    def adicionar_produto(self):

        top = Toplevel(self.janela)
        top.title("Adicionar Novo Produto ao Inventário")
        top.geometry("400x480")
        top.resizable(False, False)
        top.transient(self.janela)
        top.grab_set()

        # --- Variáveis de controle ---
        sku_var = StringVar()
        ref_var = StringVar()
        desc_var = StringVar()
        tam_var = StringVar()
        cor_var = StringVar()
        preco_var = StringVar()
        quant_var = StringVar()

        def _buscar_sku():
            sku = sku_var.get().strip()
            if not sku:
                messagebox.showwarning("SKU Inválido", "Por favor, digite um SKU.", parent=top)
                return

            from crud import listar_produto_especifico
            produto_encontrado = listar_produto_especifico(sku)

            if produto_encontrado:
                messagebox.showinfo("Produto Encontrado", f"O produto '{produto_encontrado['pro_descricao']}' será adicionado.", parent=top)
                
                self.novo_item_contador += 1
                iid = f"new_{self.novo_item_contador}"

                self.dados_originais.append([
                    iid,
                    produto_encontrado.get('pro_ref', ''),
                    produto_encontrado.get('pro_sku', sku),
                    produto_encontrado.get('pro_descricao', ''),
                    produto_encontrado.get('pro_tam', ''),
                    produto_encontrado.get('pro_quant', 0),
                    produto_encontrado.get('pro_valor', 0.0),
                    ""
                ])
                self.filtrar_treeview(None)
                top.destroy()
            else:
                messagebox.showinfo("Produto Não Encontrado", "SKU não existe. Preencha os dados manualmente.", parent=top)
                manual_frame.pack(fill='x', expand=True, padx=10, pady=10)
                entry_sku.config(state='disabled')
                btn_buscar.config(state='disabled')
        
        def _adicionar_manualmente():
            """
            Coleta os dados, insere no DB usando SUA função, e atualiza o Treeview.
            """
            try:
                # Coleta os dados dos campos
                ref = ref_var.get().strip()
                sku = sku_var.get().strip()
                desc = desc_var.get().strip()
                tam = tam_var.get().strip()
                cor = cor_var.get().strip()
                preco = float(preco_var.get().replace(',', '.'))
                quant = int(quant_var.get())

                if not all([ref, sku, desc]):
                    messagebox.showerror("Campos Vazios", "Referência, SKU e Descrição são obrigatórios.", parent=top)
                    return

                from crud import inserir_produto
                sucesso_db = inserir_produto(ref, sku, desc, tam, cor, quant, preco)

                if sucesso_db:
                    self.novo_item_contador += 1
                    iid = f"new_{self.novo_item_contador}"
                    
                    self.dados_originais.append([iid, ref, sku, desc, tam, quant, preco, ""])
                    self.filtrar_treeview(None)
                    
                    messagebox.showinfo("Sucesso", "Produto adicionado ao inventário e salvo no banco de dados.", parent=top)
                    top.destroy()

            except ValueError:
                messagebox.showerror("Erro de Valor", "Verifique se 'Preço' e 'Quantidade' são números válidos.", parent=top)
            except Exception as e:
                messagebox.showerror("Erro Inesperado", f"Ocorreu um erro: {e}", parent=top)

        # --- Montagem da Interface ---
        busca_frame = ttk.Frame(top, padding=10)
        busca_frame.pack(fill='x', padx=10, pady=10)
        ttk.Label(busca_frame, text="Digite o SKU do produto:").pack(fill='x')
        entry_sku = ttk.Entry(busca_frame, textvariable=sku_var)
        entry_sku.pack(fill='x', pady=5)
        entry_sku.focus_set()
        btn_buscar = ttk.Button(busca_frame, text="Buscar no Banco de Dados", command=_buscar_sku)
        btn_buscar.pack(pady=5)
        
        manual_frame = ttk.LabelFrame(top, text="Cadastro Manual")
        
        ttk.Label(manual_frame, text="Referência:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        ttk.Entry(manual_frame, textvariable=ref_var).grid(row=0, column=1, sticky='ew', padx=5, pady=2)
        
        ttk.Label(manual_frame, text="Descrição:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        ttk.Entry(manual_frame, textvariable=desc_var).grid(row=1, column=1, sticky='ew', padx=5, pady=2)

        ttk.Label(manual_frame, text="Tamanho:").grid(row=2, column=0, sticky='w', padx=5, pady=2)
        ttk.Entry(manual_frame, textvariable=tam_var).grid(row=2, column=1, sticky='ew', padx=5, pady=2)
        
        ttk.Label(manual_frame, text="Cor:").grid(row=3, column=0, sticky='w', padx=5, pady=2)
        ttk.Entry(manual_frame, textvariable=cor_var).grid(row=3, column=1, sticky='ew', padx=5, pady=2)

        ttk.Label(manual_frame, text="Quantidade (Estoque):").grid(row=4, column=0, sticky='w', padx=5, pady=2)
        ttk.Entry(manual_frame, textvariable=quant_var).grid(row=4, column=1, sticky='ew', padx=5, pady=2)
        
        ttk.Label(manual_frame, text="Preço (R$):").grid(row=5, column=0, sticky='w', padx=5, pady=2)
        ttk.Entry(manual_frame, textvariable=preco_var).grid(row=5, column=1, sticky='ew', padx=5, pady=2)
        
        manual_frame.columnconfigure(1, weight=1)

        btn_adicionar = ttk.Button(manual_frame, text="Adicionar ao Inventário", command=_adicionar_manualmente)
        btn_adicionar.grid(row=6, column=0, columnspan=2, pady=10)

    def filtrar_treeview(self, criterio_tupla=None):
        self.tvw_inventario.delete(*self.tvw_inventario.get_children())
        
        for item_data in self.dados_originais:
            mostrar = True
            if criterio_tupla:
                coluna, valor_busca = criterio_tupla
                idx_map = {"descricao": 3, "quantidade": 5}
                idx = idx_map.get(coluna)
                
                if idx is not None:
                    if coluna == "quantidade":
                        try:
                            quant_item = int(item_data[idx])
                            if valor_busca == "<0" and quant_item >= 0: mostrar = False
                            if valor_busca == "0" and quant_item != 0: mostrar = False
                        except (ValueError, IndexError): mostrar = False
                    elif valor_busca.lower() not in str(item_data[idx]).lower():
                        mostrar = False

            if mostrar:
                # Extrai todos os dados da lista
                iid, ref, sku, desc, tam, quant, valor, est_real = item_data
                
                # Inicia a lista de tags a serem aplicadas
                tags_aplicar = []
                
                # Lógica para tags de status (PDV, Zerado, Negativado)
                if "pdv" in str(desc).lower():
                    tags_aplicar.append("sigla_pdv")
                
                # A tag "diferente" (vermelha) tem prioridade sobre zerado/negativado
                if quant < 0:
                    tags_aplicar.append("diferente") # Negativo é sempre uma divergência
                elif quant == 0:
                    tags_aplicar.append("zerado")

                # Lógica para tags de comparação (Diferente, Igual)
                if str(est_real).strip():
                    try:
                        comparacao_igual = (int(quant) == int(est_real))
                    except (ValueError, TypeError):
                        comparacao_igual = (str(quant) == str(est_real))
                    
                    if not comparacao_igual:
                        # Se já não for vermelho por ser negativo, aplica a cor
                        if "diferente" not in tags_aplicar:
                             tags_aplicar.append("diferente")
                    else:
                        tags_aplicar.append("igual")

                valores_display = (ref, sku, desc, tam, f"{valor:.2f}", quant, est_real)
                self.tvw_inventario.insert("", "end", iid=iid, values=valores_display, tags=tuple(tags_aplicar))

    def editar_celula(self, event):
        item_iid = self.tvw_inventario.focus()
        coluna_id_str = self.tvw_inventario.identify_column(event.x)
        if not item_iid or coluna_id_str != "#7": return
        
        try:
            valores_atuais = list(self.tvw_inventario.item(item_iid, "values"))
            novo_valor = simpledialog.askinteger("Editar Estoque Real", "Digite a quantidade contada:", initialvalue=valores_atuais[5])

            if novo_valor is not None:
                for i, data in enumerate(self.dados_originais):
                    if data[0] == item_iid:
                        self.dados_originais[i][7] = novo_valor
                        break
                
                # Recarrega a treeview para que a lógica de cores seja reaplicada
                self.filtrar_treeview(None)
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro na edição: {e}")

    # Função de contar digitando somente o SKU
    def contar_sku(self, event=None):
        # Pega o SKU do campo de entrada, remove espaços e o converte para maiúsculo
        sku_a_contar = self.ent_ad_contagem.get().strip().upper()

        if not sku_a_contar:
            return  # Não faz nada se o campo estiver vazio

        produto_encontrado = False
        # Itera sobre a lista de dados para encontrar o produto
        for i, item_data in enumerate(self.dados_originais):
            # posição SKU
            if item_data[2] == sku_a_contar:
                
                # posição conta estoque
                est_real_atual = item_data[7]

                valor_a_somar = self.modificador_var.get()
                
                # Tenta converter para inteiro e somar 1. Se falhar (ex: campo vazio), começa com 1.
                try:
                    nova_quantidade = int(est_real_atual) + valor_a_somar
                except (ValueError, TypeError):
                    nova_quantidade = valor_a_somar
                
                # Atualiza a quantidade na sua lista de dados principal
                self.dados_originais[i][7] = nova_quantidade
                
                produto_encontrado = True
                iid_do_item = item_data[0] # Pega o iid do item para poder selecioná-lo
                break # Para o loop assim que encontrar o produto

        # Se o produto foi encontrado...
        if produto_encontrado:
            # 5. Recarrega a Treeview para mostrar a atualização e aplicar as cores
            self.filtrar_treeview(None)
            
            # Limpa o campo de entrada para a próxima contagem
            self.ent_ad_contagem.delete(0, "end")
            
            # Opcional: Seleciona e foca no item que foi atualizado na tabela
            if iid_do_item in self.tvw_inventario.get_children():
                self.tvw_inventario.selection_set(iid_do_item)
                self.tvw_inventario.see(iid_do_item)

        # Se não encontrou...
        else:
            messagebox.showwarning("SKU não encontrado", f"O SKU '{sku_a_contar}' não foi localizado no inventário carregado.")
            self.ent_ad_contagem.delete(0, "end")

if __name__ == "__main__":
    janela = ttk.Window(themename='united')
    app = Tela(janela)
    janela.mainloop()