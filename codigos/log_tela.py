import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, simpledialog, Toplevel, StringVar
from PIL import Image, ImageTk
from conexao import conectar
import crud
import os
import shutil
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
        self.itens_pendentes_cadastro = []

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
        
        self.ent_senha = tk.Entry(self.log, show="*", textvariable=self.senha_var)
        self.ent_senha.grid(row=3, column=0, columnspan=2, pady=5, ipady=5, ipadx=14, sticky='EW')

        # OBSERVADOR PARA A SENHA
        self.senha_var.trace_add('write',
            lambda *args: self._formatar_para_maiusculo(self.senha_var, self.ent_senha))
        
        self.btn_entrar = tk.Button(self.log, text='Entrar', bg='darkblue', fg='white', font=("Arial", 14), command=self.autentica)
        self.btn_entrar.grid(row=4, column=0, columnspan=2, pady=10)
        self.janela.bind('<Return>', self.autentica)
        
        self.dados_originais = []
        self.novo_item_contador = 0
        self.gerenciador_tema = GerenciadorTema(self.janela)
        self.tela_relatorio_vendas = TelaRelatorioVendas(self.janela)
        self.tela_consulta = Consultas(self.janela, self.mapa_imagens)
        self.tela_venda = TelaPontoVenda(self.janela, self.vendas_realizadas, self.tela_consulta, callback_venda_finalizada=self.atualizar_estoque_pos_venda)
        self.relatorio = gerar_relatorio_pdf

        self.inventario_iniciado = False
        self.inventario_modificado = False
        self.id_inventario_ativo = None
        self.ultimo_filtro_botao = None
        self.search_var_inventario = tk.StringVar()
        self.sku_contagem_var = tk.StringVar()

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
            messagebox.showerror("Erro ao carregar a imagem", f"Não foi possível carregar as imagens dos produtos: {e}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()

    def _formatar_para_maiusculo(self, string_var, *args):
        if self._is_formatting:
            return
        self._is_formatting = True

        texto_atual = string_var.get()
        string_var.set(texto_atual.upper())

        self._is_formatting = False

    def autentica(self, event=None):
        # Lendo os valores das StringVars
        usuario = self.user_var.get()
        senha = self.senha_var.get()

        if usuario == "ADM" and senha == "ADM":
            self.carregar_mapa_de_imagens()
            self.menu()
            self.janela.unbind('<Return>')
            self._carregar_inventario_pendente()
        else:
            messagebox.showwarning("Autenticação falhou", "Usuário ou senha incorretos.")

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
        self.mnu_relatorios.add_command(label='Inventários', command=self.abrir_tela_lista_inventarios)
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
        self.btn_cancelar_inventario = ttk.Button(frm_controle, text='Cancelar Inventário', command=self.cancelar_inventario, bootstyle=SECONDARY)
        self.btn_cancelar_inventario.pack(side=LEFT, padx=5)
        self.btn_finalizar_inventario = ttk.Button(frm_controle, text='Finalizar Inventário', command=self.finalizar_inventario, bootstyle=PRIMARY)
        self.btn_finalizar_inventario.pack(side=LEFT, padx=5)
        
        self.btn_ad_contagem = ttk.Button(frm_controle, text='Conta Est. por SKU', command=self.contar_sku); self.btn_ad_contagem.pack(side=RIGHT, padx=5)
        self.modificador_var = tk.IntVar(value=1)
        self.spn_modificador = ttk.Spinbox(frm_controle, from_=1, to=10, textvariable=self.modificador_var, width=2); self.spn_modificador.pack(side=RIGHT, padx=2.5)

        self.ent_ad_contagem = ttk.Entry(frm_controle, textvariable=self.sku_contagem_var)
        self.ent_ad_contagem.pack(side=RIGHT, padx=2.5)
        self.ent_ad_contagem.bind('<Return>', self.contar_sku)
        self.sku_contagem_var.trace_add('write',
            lambda *args: self._formatar_para_maiusculo(self.sku_contagem_var, self.ent_ad_contagem))

        
        frm_treeview = ttk.Frame(frm_controles_e_lista); frm_treeview.grid(row=1, column=0, sticky="nsew", pady=10); frm_treeview.rowconfigure(0, weight=1); frm_treeview.columnconfigure(0, weight=1)
        colunas = ("ref", "sku", "desc", "tam", "preco", "est", "est_real")
        self.tvw_inventario = ttk.Treeview(frm_treeview, columns=colunas, show="headings", height=15)
        
        self.tvw_inventario.tag_configure("zerado", background="lightgrey")
        self.tvw_inventario.tag_configure("diferente", background="red")
        self.tvw_inventario.tag_configure("negativado", background="red")
        self.tvw_inventario.tag_configure("sigla_pdv", background="yellow")
        self.tvw_inventario.tag_configure("igual", background="lightgreen")
        
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
        self.btn_pdv = ttk.Button(frm_botoes_grid, text="Produtos PDV", command=lambda: self.filtrar_treeview(("descricao", "pdv"))); self.btn_pdv.grid(row=0, column=1, padx=5, pady=3, sticky='ew')
        self.btn_negativos = ttk.Button(frm_botoes_grid, text="Negativados", command=lambda: self.filtrar_treeview(("quantidade", "<0"))); self.btn_negativos.grid(row=0, column=2, padx=5, pady=3, sticky='ew')
        self.btn_zerados = ttk.Button(frm_botoes_grid, text="Zerados", command=lambda: self.filtrar_treeview(("quantidade", "0"))); self.btn_zerados.grid(row=0, column=3, padx=5, pady=3, sticky='ew')
        self.btn_camisetas = ttk.Button(frm_botoes_grid, text="Camisetas", command=lambda: self.filtrar_treeview(("descricao", "Camiseta"))); self.btn_camisetas.grid(row=1, column=0, padx=5, pady=3, sticky='ew')
        self.btn_meias = ttk.Button(frm_botoes_grid, text="Meias", command=lambda: self.filtrar_treeview(("descricao", "Meia"))); self.btn_meias.grid(row=1, column=1, padx=5, pady=3, sticky='ew')
        self.btn_bones = ttk.Button(frm_botoes_grid, text="Bonés", command=lambda: self.filtrar_treeview(("descricao", "Bone"))); self.btn_bones.grid(row=1, column=2, padx=5, pady=3, sticky='ew')
        self.btn_copos = ttk.Button(frm_botoes_grid, text="Mixes", command=lambda: self.filtrar_treeview(("descricao", ["Copo", "Garrafa", "Caneca"]))); self.btn_copos.grid(row=1, column=3, padx=5, pady=3, sticky='ew')

        self.frm_imagem_display = ttk.Frame(self.frm_principal_inventario)
        self.frm_imagem_display.grid(row=0, column=1, sticky="nsew", pady=(10,0))
        self.frm_imagem_display.columnconfigure(0, weight=1); self.frm_imagem_display.rowconfigure(0, weight=1)
        self.lbl_imagem_produto = ttk.Label(self.frm_imagem_display, text="Selecione um produto", anchor="center", relief="solid", padding=5)
        self.lbl_imagem_produto.grid(row=0, column=0, sticky="nsew")

        self.tvw_inventario.bind("<Double-1>", self.editar_celula)
        self.tvw_inventario.bind('<<TreeviewSelect>>', self.mostrar_imagem_selecionada)

        self._atualizar_estado_botoes_inventario()
        
        self.filtrar_treeview(None)
    
    def abrir_tela_relatorio(self, inventario_id=None):
        # Se não tiver o id, usa o inventário . Se for tiver, usa o histórico.
        dados_para_relatorio = []
        if inventario_id:
            dados_para_relatorio = crud.buscar_detalhes_inventario(inventario_id)
        else:
            if not self.dados_originais:
                messagebox.showwarning("Sem Dados", "Nenhum inventário ativo carregado para gerar o relatório.")
                return
            for item in self.dados_originais:
                dados_para_relatorio.append({
                    "ref": item[1], "sku": item[2], "desc": item[3], "tam": item[4], 
                    "est": item[5], "est_real": item[7]
                })

        self.tela_relatorio(dados_para_relatorio) 

    def mostrar_imagem_selecionada(self, event=None):
        selecionado = self.tvw_inventario.selection()
        if not selecionado: return

        item_iid = selecionado[0]
        try:
            ref_produto = self.tvw_inventario.item(item_iid, "values")[0]
        except IndexError:
            return

        caminho_relativo = self.mapa_imagens.get(ref_produto)
        
        if caminho_relativo:
            try:
                script_dir = os.path.dirname(__file__)
                caminho_absoluto = os.path.join(script_dir, caminho_relativo)
                
                imagem_pil = Image.open(caminho_absoluto)
                imagem_pil.thumbnail((250, 250))
                
                self.imagem_tk = ImageTk.PhotoImage(imagem_pil)                
                self.lbl_imagem_produto.config(image=self.imagem_tk, text="")
                self.lbl_imagem_produto.image = self.imagem_tk

            except FileNotFoundError:
                self.lbl_imagem_produto.config(image='', text="Imagem não encontrada.")
            except Exception as e:
                print(f"Erro ao processar imagem: {e}")
                self.lbl_imagem_produto.config(image='', text="Erro ao carregar\nimagem.")
        else:
            self.lbl_imagem_produto.config(image='', text="Produto sem imagem\ncadastrada no banco.")

    def _gerar_e_finalizar_relatorio(self):
        """
        Chama a geração do PDF, exibe uma mensagem de sucesso
        e fecha a janela de relatório.
        """
        # verifica se há dados para gerar o relatório
        if not self.divergencias and not self.negativados and not self.pdvs:
            messagebox.showwarning("Sem Dados", "Não há dados para gerar o relatório.", parent=self.tpl_relatorios)
            return

        try:
            nome_arquivo = self.relatorio(self.divergencias, self.negativados, self.pdvs, self.zerados)
            messagebox.showinfo("Sucesso", f"Relatório salvo com sucesso como:\n{nome_arquivo}")
            self.tpl_relatorios.destroy()

        except Exception as e:
            messagebox.showerror("Erro ao Gerar PDF", f"Ocorreu um erro ao criar o arquivo PDF:\n{e}", parent=self.tpl_relatorios)

    def gerar_relatorio(self):
        if not self.divergencias:
            messagebox.showwarning("Aviso", "Nenhuma divergência encontrada.")
            return

        nome_arquivo = gerar_relatorio_pdf(self.divergencias)
        messagebox.showinfo("Relatório gerado", f"Relatório salvo como:\n{nome_arquivo}")
    
    def tela_relatorio(self, dados_inventario):
        self.tpl_relatorios = tk.Toplevel(self.tpl_menu)
        self.tpl_relatorios.title("Relatório de Divergências")
        self.tpl_relatorios.state('zoomed')

        self.frm_principal_relDivergencia = ttk.Frame(self.tpl_relatorios, padding=10)
        self.frm_principal_relDivergencia.pack(fill=BOTH, expand=True)

        self.divergencias = []
        self.negativados = []
        self.pdvs = []
        self.zerados = []

        def criar_treeview(rotulo, dados):
            ttk.Label(self.frm_principal_relDivergencia, text=rotulo, font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(10, 0))
            frame_tv = ttk.Frame(self.frm_principal_relDivergencia)
            frame_tv.pack(fill=BOTH, expand=True)

            colunas = ("ref", "sku", "desc", "tam", "est", "est_real")
            tree = ttk.Treeview(frame_tv, columns=colunas, show="headings", height=5)

            for col, txt, width, align in [("ref", "Ref", 70, CENTER),("sku", "SKU", 70, CENTER),("desc", "Descrição", 300, "w"),("tam", "Tam/Cap", 100, CENTER),("est", "Estoque", 100, CENTER),("est_real", "Est. Real", 100, CENTER)]: 
                tree.heading(col, text=txt); tree.column(col, width=width, anchor=align)
            scrollbar_y = ttk.Scrollbar(frame_tv, orient="vertical", command=tree.yview)

            tree.configure(yscrollcommand=scrollbar_y.set)
            tree.grid(row=0, column=0, sticky="nsew"); scrollbar_y.grid(row=0, column=1, sticky="ns")
            frame_tv.rowconfigure(0, weight=1)
            frame_tv.columnconfigure(0, weight=1)
            for item in dados: 
                tree.insert("", "end", values=item)
            return tree

        for item in dados_inventario:
            ref, sku, desc, tam = item['ref'], item['sku'], item['desc'], item['tam']
            est, est_real = item['est'], item['est_real']

            desc_lower = str(desc).lower()
            est_str = str(est).strip()

            est_real_str = str(est_real).strip() if est_real is not None else ""

            is_pdv = "pdv" in desc_lower
            is_negativado = False
            is_divergente = False
            is_zerado = False

            try:
                est_int = int(est)
                est_real_int = int(est_real) if est_real_str else None
                is_negativado = est_int < 0
                is_zerado = est_int == 0
                is_divergente = est_real_str != "" and (est_int != est_real_int)
            except (ValueError, TypeError):
                is_divergente = est_real_str != "" and (est_str != est_real_str)

            valores = (ref, sku, desc, tam, est, est_real_str)

            if is_divergente: self.divergencias.append(valores)
            if is_negativado: self.negativados.append(valores)
            if is_pdv: self.pdvs.append(valores)
            if is_zerado: self.zerados.append(valores)

        # --- Cria os Treeviews ---
        if self.divergencias: self.tvw_divergencias = criar_treeview("Produtos com divergência", self.divergencias)
        if self.negativados: self.tvw_negativados = criar_treeview("Produtos negativados", self.negativados)
        if self.zerados: self.tvw_zerados = criar_treeview("Produtos zerados", self.zerados)
        if self.pdvs: self.tvw_pdvs = criar_treeview("Produtos PDV", self.pdvs)
        
        ttk.Button(self.frm_principal_relDivergencia, text="Gerar Relatório PDF", command=self._gerar_e_finalizar_relatorio).pack(pady=(20, 0))

    def upp_arquivo(self):
        caminho_arquivo = filedialog.askopenfilename(title="Selecione o Arquivo de Inventário (.txt)", filetypes=[("Arquivos de texto", "*.txt")])
        if not caminho_arquivo: return

        self.dados_originais.clear()
        self.inventario_iniciado = False
        self.itens_pendentes_cadastro.clear() # Limpa a lista de pendentes
        
        try:
            produtos_do_banco = crud.listar_produtos()
            sku_map = {(p['pro_ref'], p['pro_tam']): p['pro_sku'] for p in produtos_do_banco if p['pro_ref'] and p['pro_tam']}
            
            dados_validados = []
            
            with open(caminho_arquivo, "r", encoding="utf-8") as f:
                for i, linha in enumerate(f):
                    linha = linha.strip()
                    if not linha: continue
                    
                    try:
                        campos = [campo.strip() for campo in linha.split(';')]
                        ref, desc, tam, quant_str, valor_str = campos[:5]
                        sku = sku_map.get((ref, tam))

                        item_data = {
                            'ref': ref, 'sku': sku, 'desc': desc, 'tam': tam, 
                            'quant': int(quant_str), 'valor': float(valor_str.replace(',', '.'))
                        }

                        if sku: # Se o produto JÁ EXISTE no banco
                            iid = f"file_{i}"
                            dados_validados.append([iid, item_data['ref'], item_data['sku'], item_data['desc'], 
                                                    item_data['tam'], item_data['quant'], item_data['valor'], ""])
                        else: # Se o produto NÃO EXISTE
                            self.itens_pendentes_cadastro.append(item_data)
                    except (ValueError, IndexError):
                        print(f"AVISO: Linha {i+1} ignorada - formato inválido: {linha}")
                        continue
            
            if not dados_validados and not self.itens_pendentes_cadastro:
                messagebox.showerror("Nenhum Item", "O arquivo está vazio ou não contém itens.", parent=self.janela)
                return

            self.id_inventario_ativo = crud.criar_novo_inventario(dados_validados)
            
            if self.id_inventario_ativo:
                self.dados_originais = dados_validados
                self.inventario_iniciado = True
                self.filtrar_treeview(None)
                self._atualizar_estado_botoes_inventario()

                if self.itens_pendentes_cadastro:
                    self._abrir_janela_cadastro_pendentes()
            else:
                messagebox.showerror("Erro Crítico", "Não foi possível criar a sessão de inventário.", parent=self.janela)

        except Exception as e:
            messagebox.showerror("Erro de Leitura", f"Não foi possível processar o arquivo: {e}")

    def adicionar_produto(self):
        top = Toplevel(self.janela)
        top.title("Adicionar Produto")
        top.geometry("450x550")
        top.resizable(False, False)
        top.grab_set()

        # --- Variáveis de controle ---
        sku_var, ref_var, desc_var, tam_var, preco_var, bipe_var = StringVar(), StringVar(), StringVar(), StringVar(), StringVar(), StringVar()
        caminho_imagem_var = StringVar(value="Nenhuma imagem selecionada.")
        imagem_selecionada = {'path': None} # Dicionário para guardar o caminho da imagem original

        # --- Função para o botão de selecionar imagem ---
        def _selecionar_imagem():
            caminho = filedialog.askopenfilename(
                title="Selecione a imagem do produto",
                filetypes=[("Arquivos de Imagem", "*.png *.jpg *.jpeg *.gif *.bmp")]
            )
            if caminho:
                imagem_selecionada['path'] = caminho
                nome_arquivo = os.path.basename(caminho)
                caminho_imagem_var.set(nome_arquivo)

        # --- Lógica de busca e adição ---
        def _buscar_sku():
            if not self.inventario_iniciado:
                messagebox.showerror("Ação Inválida", "Você só pode adicionar um produto já existente a um inventário ativo.\n\nPara cadastrar um produto novo, use o cadastro manual.", parent=top)
                return
            sku_ou_bipe = sku_var.get().strip()

            if not sku_ou_bipe:
                messagebox.showwarning("Código Inválido", "Por favor, digite um SKU ou Bipe.", parent=top)
                return
            produto_encontrado = crud.buscar_produto_por_sku_ou_bipe(sku_ou_bipe)

            if produto_encontrado:
                self.novo_item_contador += 1
                iid = f"new_{self.novo_item_contador}"
                self.dados_originais.append([ iid, produto_encontrado.get('pro_ref', ''), produto_encontrado.get('pro_sku', sku_ou_bipe), produto_encontrado.get('pro_descricao', ''), produto_encontrado.get('pro_tam', ''), 0, produto_encontrado.get('pro_valor', 0.0), "" ])
                sku_real = produto_encontrado['pro_sku']
                crud.adicionar_item_ao_inventario(self.id_inventario_ativo, sku_real)
                self.filtrar_treeview(None)
                
                messagebox.showinfo("Sucesso", f"'{produto_encontrado['pro_descricao']}' adicionado ao inventário.", parent=top)
                top.destroy()
            else:
                messagebox.showinfo("Produto Não Encontrado", "Código não existe! Preencha os dados manualmente para cadastrar um novo produto.", parent=top)
                manual_frame.pack(fill='x', expand=True, padx=10, pady=10)
                entry_sku.config(state='disabled')
                btn_buscar.config(state='disabled')
        
        def _adicionar_manualmente():
            try:
                #Coleta todos os dados da interface
                ref = ref_var.get().strip()
                sku = sku_var.get().strip()
                desc = desc_var.get().strip()
                tam = tam_var.get().strip()
                bipe = bipe_var.get().strip()
                preco = preco_var.get().strip()

                if not all([ref, sku, desc, tam, bipe, preco]):
                    messagebox.showerror("Campos Obrigatórios", "Todos os campos devem ser preenchidos para cadastrar um novo produto.", parent=top)
                    return

                caminho_imagem_db = None #Inicia o caminho da imagem como nulo

                # Bloco de Manipulação da Imagem
                if imagem_selecionada['path']:
                    caminho_origem = imagem_selecionada['path']
                    _, extensao = os.path.splitext(caminho_origem)
                    novo_nome_arquivo = f"{ref}{extensao}"

                    caminho_relativo_db = os.path.join("imagens_produtos", novo_nome_arquivo)

                    script_dir = os.path.dirname(__file__)
                    caminho_destino_abs = os.path.join(script_dir, caminho_relativo_db)

                    os.makedirs(os.path.dirname(caminho_destino_abs), exist_ok=True)
                    shutil.copy(caminho_origem, caminho_destino_abs) 
                    caminho_imagem_db = caminho_relativo_db

                # Bloco de Inserção no Banco
                sucesso_db = crud.inserir_produto(ref, sku, desc, tam, bipe, preco, caminho_imagem_db)

                if sucesso_db:
                    # Se salvou no banco, atualiza o resto da aplicação
                    if caminho_imagem_db:
                        self.mapa_imagens[ref] = caminho_imagem_db

                    msg_sucesso = f"'{desc}' cadastrado com sucesso!"

                    if self.inventario_iniciado:
                        self.novo_item_contador += 1
                        iid = f"new_{self.novo_item_contador}"
                        preco_float = float(preco.replace(',', '.')) if preco else 0.0
                        self.dados_originais.append([iid, ref, sku, desc, tam, 0, preco_float, ""])
                        crud.adicionar_item_ao_inventario(self.id_inventario_ativo, sku)
                        self.filtrar_treeview(None)
                        msg_sucesso += "\nE adicionado ao inventário atual."

                    messagebox.showinfo("Sucesso", msg_sucesso, parent=top)
                    top.destroy()

            except Exception as e:
                messagebox.showerror("Erro Inesperado", f"Ocorreu um erro ao salvar o produto: {e}", parent=top)

        # --- Montagem da Interface ---
        busca_frame = ttk.Frame(top, padding=10)
        busca_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(busca_frame, text="Digite o SKU ou Bipe para adicionar produto existente:").pack(fill='x')
        entry_sku = ttk.Entry(busca_frame, textvariable=sku_var)
        entry_sku.pack(fill='x', pady=5); entry_sku.focus_set()
        entry_sku.bind("<KeyRelease>", lambda event: self._formatar_para_maiusculo(sku_var))
        
        btn_buscar = ttk.Button(busca_frame, text="Buscar e Adicionar ao Inventário", command=_buscar_sku)
        btn_buscar.pack(pady=5)
        
        manual_frame = ttk.LabelFrame(top, text="Cadastrar Novo Produto")
        manual_frame.columnconfigure(1, weight=1)
        
        ttk.Label(manual_frame, text="Referência:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        entry_ref = ttk.Entry(manual_frame, textvariable=ref_var); entry_ref.grid(row=0, column=1, sticky='ew', padx=5, pady=2)
        entry_ref.bind("<KeyRelease>", lambda event: self._formatar_para_maiusculo(ref_var))

        ttk.Label(manual_frame, text="SKU:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        ttk.Entry(manual_frame, textvariable=sku_var).grid(row=1, column=1, sticky='ew', padx=5, pady=2)
        
        ttk.Label(manual_frame, text="Descrição:").grid(row=2, column=0, sticky='w', padx=5, pady=2)
        entry_desc = ttk.Entry(manual_frame, textvariable=desc_var); entry_desc.grid(row=2, column=1, sticky='ew', padx=5, pady=2)
        entry_desc.bind("<KeyRelease>", lambda event: self._formatar_para_maiusculo(desc_var))

        ttk.Label(manual_frame, text="Tamanho:").grid(row=3, column=0, sticky='w', padx=5, pady=2)
        entry_tam = ttk.Entry(manual_frame, textvariable=tam_var); entry_tam.grid(row=3, column=1, sticky='ew', padx=5, pady=2)
        entry_tam.bind("<KeyRelease>", lambda event: self._formatar_para_maiusculo(tam_var))
        
        ttk.Label(manual_frame, text="Bipe (Cód. Barras):").grid(row=4, column=0, sticky='w', padx=5, pady=2)
        entry_bipe = ttk.Entry(manual_frame, textvariable=bipe_var); entry_bipe.grid(row=4, column=1, sticky='ew', padx=5, pady=2)
        entry_bipe.bind("<KeyRelease>", lambda event: self._formatar_para_maiusculo(bipe_var))
        
        ttk.Label(manual_frame, text="Preço (R$):").grid(row=5, column=0, sticky='w', padx=5, pady=2)
        ttk.Entry(manual_frame, textvariable=preco_var).grid(row=5, column=1, sticky='ew', padx=5, pady=2)

        # --- BLOCO PARA IMAGEM ---
        ttk.Label(manual_frame, text="Imagem:").grid(row=6, column=0, sticky='w', padx=5, pady=5)
        frame_imagem = ttk.Frame(manual_frame)
        frame_imagem.grid(row=6, column=1, sticky='ew', padx=5, pady=2)
        ttk.Button(frame_imagem, text="Selecionar Imagem...", command=_selecionar_imagem).pack(side=LEFT)
        ttk.Label(frame_imagem, textvariable=caminho_imagem_var, wraplength=200).pack(side=LEFT, padx=5)

        btn_adicionar = ttk.Button(manual_frame, text="Salvar Novo Produto", command=_adicionar_manualmente)
        btn_adicionar.grid(row=7, column=0, columnspan=2, pady=10)

        if not self.inventario_iniciado:
            manual_frame.pack(fill='x', expand=True, padx=10, pady=10)
            btn_buscar.config(state='disabled')
            entry_sku.config(state='disabled')
            top.title("Cadastrar Novo Produto")

    def filtrar_treeview(self, criterio_tupla=None):
        self.ultimo_filtro_botao = criterio_tupla # Movemos a linha para fora do 'if'
        
        self.tvw_inventario.delete(*self.tvw_inventario.get_children())

        for item_data in self.dados_originais:
            # --- Bloco de Filtros (Botões e Busca por Texto) ---
            mostrar = True
            if self.ultimo_filtro_botao:
                coluna, valor_busca = self.ultimo_filtro_botao
                idx_map = {"descricao": 3, "quantidade": 5, "est_real": 7}
                idx = idx_map.get(coluna)
                if idx is not None:
                    if coluna == "quantidade":
                        try:
                            quant_item = int(item_data[idx])
                            if valor_busca == "<0" and quant_item >= 0: mostrar = False
                            if valor_busca == "0" and quant_item != 0: mostrar = False
                        except (ValueError, IndexError):
                            mostrar = False
                    elif coluna == "est_real":
                        if valor_busca == "vazio" and str(item_data[idx]).strip() != "":
                            mostrar = False
                    elif isinstance(valor_busca, list):
                        item_texto = str(item_data[idx]).lower()
                        if not any(palavra.lower() in item_texto for palavra in valor_busca): mostrar = False
                    else:
                        if valor_busca.lower() not in str(item_data[idx]).lower(): mostrar = False
            
            pesquisa_ok = True
            termo_busca = self.search_var_inventario.get().lower().strip()
            if termo_busca:
                ref, sku, desc = item_data[1], item_data[2], item_data[3]
                if not (termo_busca in str(ref).lower() or termo_busca in str(sku).lower() or termo_busca in str(desc).lower()):
                    pesquisa_ok = False
            
            if mostrar and pesquisa_ok:
                iid, ref, sku, desc, tam, quant, valor, est_real = item_data
                tags_aplicar = []
                # Condições de estado da contagem
                is_divergente = False
                is_igual = False
                est_real_str = str(est_real).strip()
                
                if est_real_str: # Se uma contagem foi feita
                    try:
                        comparacao_igual = (int(quant) == int(est_real))
                    except (ValueError, TypeError):
                        comparacao_igual = (str(quant) == est_real_str)
                    
                    if comparacao_igual:
                        is_igual = True
                    else:
                        is_divergente = True

                # Tags de cor com PRIORIDADE
                if is_divergente:
                    tags_aplicar.append('diferente') # Vermelho (Máxima prioridade)
                elif is_igual:
                    tags_aplicar.append('igual')     # Verde
                elif quant < 0:
                    tags_aplicar.append('negativado')# Vermelho (estoque do sistema negativado)
                elif quant == 0:
                    tags_aplicar.append('zerado')    # Cinza

                # Tag PDV
                if "pdv" in str(desc).lower():
                    tags_aplicar.append("sigla_pdv") # Amarelo

                valor_formatado = f"{valor:.2f}" if valor is not None else ""
                valores_display = (ref, sku, desc, tam, valor_formatado, quant, est_real)
                
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
                        sku_do_item = self.dados_originais[i][2]
                        crud.atualizar_contagem_item(self.id_inventario_ativo, sku_do_item, novo_valor)
                        self.inventario_modificado = True #Inventário foi modificado
                        break
                
                # Recarrega a treeview para que a lógica de cores seja reaplicada
                self.filtrar_treeview(None)
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro na edição: {e}")

    def contar_sku(self, event=None):
        codigo_digitado = self.sku_contagem_var.get().strip()
        if not codigo_digitado:
            return

        produto_db = crud.buscar_produto_por_sku_ou_bipe(codigo_digitado)

        if not produto_db:
            messagebox.showwarning("Não encontrado", f"Produto com código '{codigo_digitado}' não localizado.")
            self.ent_ad_contagem.delete(0, "end")
            return

        # Pega o SKU "oficial" do produto encontrado no banco
        sku_a_contar = produto_db['pro_sku']

        produto_encontrado_na_lista = False
        iid_do_item = None
        # Procura o SKU na lista do inventário carregado
        for i, item_data in enumerate(self.dados_originais):
            if item_data[2] == sku_a_contar:
                est_real_atual = item_data[7]
                valor_a_somar = self.modificador_var.get()

                try:
                    nova_quantidade = int(est_real_atual) + valor_a_somar
                except (ValueError, TypeError):
                    nova_quantidade = valor_a_somar

                self.dados_originais[i][7] = nova_quantidade
                self.inventario_modificado = True
                crud.atualizar_contagem_item(self.id_inventario_ativo, sku_a_contar, nova_quantidade)

                produto_encontrado_na_lista = True
                iid_do_item = item_data[0]
                break

        if produto_encontrado_na_lista:
            self.filtrar_treeview(None)
            self.ent_ad_contagem.delete(0, "end")
            if iid_do_item in self.tvw_inventario.get_children():
                self.tvw_inventario.selection_set(iid_do_item)
                self.tvw_inventario.see(iid_do_item)
        else:
            messagebox.showwarning("Não encontrado", f"O produto '{sku_a_contar}' existe, mas não faz parte deste inventário.")
            self.ent_ad_contagem.delete(0, "end")

    def finalizar_inventario(self):
        # VERIFICAÇÃO DE ITENS PENDENTES DE CADASTRO
        if self.itens_pendentes_cadastro:
            messagebox.showwarning("Cadastro Pendente", 
                                   f"Existem {len(self.itens_pendentes_cadastro)} produto(s) que não foram cadastrados na base de dados.\n\n"
                                   "É necessário cadastrá-los antes de finalizar o inventário.", 
                                   parent=self.janela)
            self._abrir_janela_cadastro_pendentes()
            return # Impede a continuação da finalização

        if not self.inventario_iniciado:
            return
        
        itens_pendentes = [item for item in self.dados_originais if str(item[7]).strip() == ""]
        
        decisao_usuario = "finalizar"
        
        if itens_pendentes:
            decisao_usuario = self._dialogo_inventario_incompleto(len(itens_pendentes))

        if decisao_usuario == "finalizar":
            if crud.finalizar_inventario_db(self.id_inventario_ativo):
                messagebox.showinfo("Sucesso", "Inventário finalizado e salvo no histórico de inventários.", parent=self.janela)
                self.dados_originais.clear()
                self.inventario_iniciado = False
                self.inventario_modificado = False
                self.id_inventario_ativo = None
                self.filtrar_treeview(None)
                self._atualizar_estado_botoes_inventario()
        
        elif decisao_usuario == "ver_pendentes":
            self.filtrar_treeview(("est_real", "vazio"))

    def _atualizar_estado_botoes_inventario(self):
        if self.inventario_iniciado:
            # Se tem inventário ativo, desabilita o Carregar e habilita os outros
            self.btn_ad_arquivo.config(state="disabled")
            self.btn_finalizar_inventario.config(state="normal")
            self.btn_cancelar_inventario.config(state="normal")
        else:
            # Se não tem inventário, habilita o Carregar e desabilita os outros
            self.btn_ad_arquivo.config(state="normal")
            self.btn_finalizar_inventario.config(state="disabled")
            self.btn_cancelar_inventario.config(state="disabled")

    def cancelar_inventario(self):
        if not self.inventario_iniciado:
            return

        resposta = messagebox.askyesno(
            "Cancelar Inventário",
            "Você tem certeza que deseja cancelar o inventário atual?\nTodas as alterações feitas serão perdidas.",
            parent=self.janela
        )

        if resposta:
            # Chama a função do CRUD para apagar do banco
            if crud.cancelar_inventario_db(self.id_inventario_ativo):
                # Se apagou com sucesso, limpa a interface e os status
                self.dados_originais.clear()
                self.inventario_iniciado = False
                self.inventario_modificado = False
                self.id_inventario_ativo = None 
                self.filtrar_treeview(None)
                self._atualizar_estado_botoes_inventario()

    def _carregar_inventario_pendente(self):
        dados_inventario = crud.buscar_inventario_em_andamento()

        if dados_inventario:
            self.id_inventario_ativo = dados_inventario['id_inventario']
            self.inventario_iniciado = True
            self.dados_originais.clear()

            # Recria a lista self.dados_originais com os dados do banco
            for i, item in enumerate(dados_inventario['itens']):
                iid = f"db_{i}"
                self.dados_originais.append([
                    iid,
                    item['pro_ref'],
                    item['pro_sku'],
                    item['pro_descricao'],
                    item['pro_tam'],
                    item['quantidade_sistema'],
                    item['pro_valor'],
                    item['quantidade_contada'] if item['quantidade_contada'] is not None else ""
                ])
            
            self.inventario_modificado = any(item['quantidade_contada'] is not None for item in dados_inventario['itens'])
            self.filtrar_treeview(None)
            self._atualizar_estado_botoes_inventario()

    def abrir_tela_lista_inventarios(self):
        top = Toplevel(self.janela)
        top.title("Histórico de Inventários Finalizados")
        top.state('zoomed')
        #top.transient(self.janela)
        top.grab_set()

        frame_filtros = ttk.LabelFrame(top, text="Filtrar por Data de Finalização", padding=10)
        frame_lista = ttk.Frame(top)
        frame_acoes = ttk.Frame(top, padding=(10, 10, 10, 10))

        # Filtros
        
        ttk.Label(frame_filtros, text="De:").pack(side=LEFT, padx=(0, 5))
        date_inicio = ttk.DateEntry(frame_filtros, bootstyle=PRIMARY, dateformat="%d/%m/%Y")
        date_inicio.pack(side=LEFT, padx=(0, 10))
        ttk.Label(frame_filtros, text="Até:").pack(side=LEFT, padx=(0, 5))
        date_fim = ttk.DateEntry(frame_filtros, bootstyle=PRIMARY, dateformat="%d/%m/%Y")
        date_fim.pack(side=LEFT, padx=(0, 20))

        def _buscar_e_popular():
            for item in tree.get_children(): tree.delete(item)
            from datetime import datetime
            data_inicio_br = date_inicio.entry.get(); data_fim_br = date_fim.entry.get()
            data_i = datetime.strptime(data_inicio_br, "%d/%m/%Y").strftime("%Y-%m-%d")
            data_f = datetime.strptime(data_fim_br, "%d/%m/%Y").strftime("%Y-%m-%d")
            lista_inventarios = crud.listar_inventarios_finalizados(data_i, data_f)
            for inv in lista_inventarios:
                data_inicio_fmt = inv['inv_data_inicio'].strftime('%d/%m/%Y %H:%M')
                data_fim_fmt = inv['inv_data_finalizacao'].strftime('%d/%m/%Y %H:%M') if inv.get('inv_data_finalizacao') else "N/A"
                nome_inventario = f"Inventário - {data_fim_fmt}"
                tree.insert("", END, iid=inv['inv_id'], values=(nome_inventario, data_inicio_fmt, data_fim_fmt))
        
        btn_buscar = ttk.Button(frame_filtros, text="Buscar", command=_buscar_e_popular, bootstyle=PRIMARY)
        btn_buscar.pack(side=LEFT)

        # frame da lista
        colunas = ("nome", "inicio", "fim")
        tree = ttk.Treeview(frame_lista, columns=colunas, show="headings", selectmode="extended")
        tree.heading("nome", text="Nome"); tree.column("nome", width=300)
        tree.heading("inicio", text="Data de Início"); tree.column("inicio", width=200, anchor=CENTER)
        tree.heading("fim", text="Data de Finalização"); tree.column("fim", width=200, anchor=CENTER)
        
        scrollbar = ttk.Scrollbar(frame_lista, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)
        tree.pack(fill=BOTH, expand=True, side=LEFT)

        def _abrir_relatorio_selecionado(event):
            selecionado = tree.selection()
            if not selecionado: return
            id_inventario = selecionado[0]
            top.destroy()
            self.abrir_tela_relatorio(id_inventario)

        tree.bind("<Double-1>", _abrir_relatorio_selecionado)

        # Frame de ação
        def _apagar_inventario_selecionado():
            selecionados = tree.selection()
            if not selecionados:
                messagebox.showwarning("Nenhuma Seleção", "Por favor, selecione ao menos um inventário para apagar.", parent=top)
                return
            msg = "Você tem certeza que deseja apagar permanentemente o inventário selecionado?"
            if len(selecionados) > 1:
                msg = f"Você tem certeza que deseja apagar permanentemente os {len(selecionados)} inventários selecionados?"
            resposta = messagebox.askyesno("Confirmar Exclusão", f"{msg}\n\nEsta ação não pode ser desfeita.", parent=top)
            if resposta:
                sucessos = 0
                for inv_id in selecionados:
                    if crud.cancelar_inventario_db(inv_id):
                        sucessos += 1
                messagebox.showinfo("Operação Concluída", f"{sucessos} inventário(s) apagado(s) com sucesso.", parent=top)
                _buscar_e_popular()

        btn_apagar = ttk.Button(frame_acoes, text="Apagar Inventário(s) Selecionado(s)", command=_apagar_inventario_selecionado, bootstyle=DANGER)
        btn_apagar.pack(side=RIGHT) # Empacota o botão DENTRO do frame_acoes

        # Junta os frames principais
        frame_filtros.pack(fill=X, padx=10, pady=(10,0))
        frame_acoes.pack(fill=X, side=BOTTOM, padx=10, pady=(0,10))
        frame_lista.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Popula a lista inicialmente
        lista_inicial = crud.listar_inventarios_finalizados()
        for inv in lista_inicial:
            data_inicio_fmt = inv['inv_data_inicio'].strftime('%d/%m/%Y %H:%M')
            data_fim_fmt = inv['inv_data_finalizacao'].strftime('%d/%m/%Y %H:%M') if inv.get('inv_data_finalizacao') else "N/A"
            nome_inventario = f"Inventário - {data_fim_fmt}"
            tree.insert("", END, iid=inv['inv_id'], values=(nome_inventario, data_inicio_fmt, data_fim_fmt))

    def _dialogo_inventario_incompleto(self, contagem_pendentes):
        self._dialogo_resultado = None
        
        dialog = Toplevel(self.janela)
        dialog.title("Atenção: Inventário Incompleto")
        dialog.geometry("450x200")
        dialog.resizable(False, False)
        dialog.transient(self.janela)
        dialog.grab_set()

        # centraliza a janela
        dialog.update_idletasks() 

        main_x = self.janela.winfo_x()
        main_y = self.janela.winfo_y()
        main_width = self.janela.winfo_width()
        main_height = self.janela.winfo_height()

        dialog_width = dialog.winfo_width()
        dialog_height = dialog.winfo_height()

        pos_x = main_x + (main_width // 2) - (dialog_width // 2)
        pos_y = main_y + (main_height // 2) - (dialog_height // 2)
        
        dialog.geometry(f"+{pos_x}+{pos_y}")

        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=BOTH, expand=True)

        main_frame.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)

        mensagem = f"Existem {contagem_pendentes} produto(s) que ainda não foram contados.\n\nO que você deseja fazer?"
        
        ttk.Label(main_frame, text=mensagem, wraplength=400, justify=CENTER).grid(row=0, column=0)
        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=1, column=0, pady=(20, 0))

        def _acao(resultado):
            self._dialogo_resultado = resultado
            dialog.destroy()

        ttk.Button(btn_frame, text="Finalizar Mesmo Assim", command=lambda: _acao("finalizar"), bootstyle=PRIMARY).pack(side=LEFT, padx=5)
        ttk.Button(btn_frame, text="Ver Itens Pendentes", command=lambda: _acao("ver_pendentes"), bootstyle=INFO).pack(side=LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=lambda: _acao("cancelar"), bootstyle=SECONDARY).pack(side=LEFT, padx=5)
        
        self.janela.wait_window(dialog)
        return self._dialogo_resultado

    def atualizar_estoque_pos_venda(self, produtos_da_transacao):
        """
        Callback chamado após uma venda. Verifica cada item:
        - Se o preço for positivo (venda), decrementa o estoque.
        - Se o preço for negativo (devolução), incrementa o estoque.
        """
        if not self.inventario_iniciado:
            return

        for produto_transacao in produtos_da_transacao:
            sku = produto_transacao['codigo']
            preco = produto_transacao['preco']

            # Encontra o item correspondente na lista do inventário
            for i, item_inventario in enumerate(self.dados_originais):
                if item_inventario[2] == sku:
                    
                    # Lógica para Venda (preço > 0)
                    if preco > 0:
                        crud.decrementar_estoque_item_inventario(self.id_inventario_ativo, sku)
                        self.dados_originais[i][5] -= 1 # Atualiza Estoque na tela
                        est_real_str = str(self.dados_originais[i][7]).strip()
                        if est_real_str:
                            self.dados_originais[i][7] = int(est_real_str) - 1 # Atualiza Est. Real na tela

                    # Lógica para Devolução (preço < 0)
                    elif preco < 0:
                        crud.incrementar_estoque_item_inventario(self.id_inventario_ativo, sku)
                        self.dados_originais[i][5] += 1 # Atualiza Estoque na tela
                        est_real_str = str(self.dados_originais[i][7]).strip()
                        if est_real_str:
                            self.dados_originais[i][7] = int(est_real_str) + 1 
                    
                    break # Para o loop interno qnd achar o produto
        
        # Atualiza a tabela na tela para mostrar os novos valores
        self.filtrar_treeview(None)
        
    def _abrir_janela_cadastro_pendentes(self):
        if not self.itens_pendentes_cadastro:
            return

        dialog = Toplevel(self.janela)
        dialog.title("Itens Pendentes de Cadastro")
        dialog.transient(self.janela)
        dialog.grab_set()
        dialog.geometry("600x650")

        # --- Variáveis de Estado da Janela ---
        estado = {
            "indice_atual": 0,
            "total_itens": len(self.itens_pendentes_cadastro),
            "inseridos": 0,
            "caminho_imagem": None
        }

        # --- StringVars para os campos do formulário ---
        ref_var, sku_var, desc_var, tam_var, bipe_var, preco_var = StringVar(), StringVar(), StringVar(), StringVar(), StringVar(), StringVar()
        caminho_imagem_var = StringVar(value="Nenhuma imagem selecionada.")

        # --- Funções Internas da Janela ---
        def atualizar_contador():
            lbl_contador.config(text=f"{estado['inseridos']}/{estado['total_itens']} Inseridos")

        def _validar_apenas_numeros(valor_digitado):
            return valor_digitado.isdigit() or valor_digitado == ""

        def mostrar_item_atual():
            if not self.itens_pendentes_cadastro or estado['indice_atual'] >= len(self.itens_pendentes_cadastro):
                messagebox.showinfo("Concluído", "Todos os itens pendentes foram processados.", parent=dialog)
                dialog.destroy()
                return

            item_atual = self.itens_pendentes_cadastro[estado['indice_atual']]
            
            ref_var.set(item_atual.get('ref', ''))
            sku_var.set(item_atual.get('sku') or '')
            desc_var.set(item_atual.get('desc', ''))
            tam_var.set(item_atual.get('tam', ''))
            preco_var.set(str(item_atual.get('valor', '0.0')))
            bipe_var.set('')
            caminho_imagem_var.set("Nenhuma imagem selecionada.")
            estado['caminho_imagem'] = None

        def selecionar_imagem_pendente():
            caminho = filedialog.askopenfilename(filetypes=[("Arquivos de Imagem", "*.png *.jpg *.jpeg")])
            if caminho:
                estado['caminho_imagem'] = caminho
                caminho_imagem_var.set(os.path.basename(caminho))

        def adicionar_item_atual():
            ref = ref_var.get().strip()
            sku = sku_var.get().strip()
            desc = desc_var.get().strip()
            tam = tam_var.get().strip()
            bipe = bipe_var.get().strip()
            preco_str = preco_var.get().strip()

            if not all([ref, sku, desc, tam, bipe, preco_str]):
                messagebox.showerror("Campos Obrigatórios", "Todos os campos com * devem ser preenchidos.", parent=dialog)
                return
            
            if not sku.isdigit():
                messagebox.showerror("Formato Inválido", "O campo SKU deve conter apenas números.", parent=dialog)
                return

            if not estado['caminho_imagem']:
                messagebox.showerror("Imagem Obrigatória", "É obrigatório selecionar uma imagem para o produto.", parent=dialog)
                return
            
            try:
                float(preco_str.replace(',', '.'))
            except ValueError:
                messagebox.showerror("Formato Inválido", "O valor do campo 'Preço' não é um número válido.", parent=dialog)
                return

            resposta = messagebox.askyesno("Confirmar Ação", 
                                           "Esta ação não pode ser desfeita. Deseja continuar e salvar o produto na base de dados?",
                                           parent=dialog)
            if not resposta:
                return

            try:
                caminho_imagem_db = None
                if estado['caminho_imagem']:
                    _, extensao = os.path.splitext(estado['caminho_imagem'])
                    novo_nome_arquivo = f"{ref}{extensao}"
                    caminho_relativo_db = os.path.join("imagens_produtos", novo_nome_arquivo)
                    caminho_destino_abs = os.path.join(os.path.dirname(__file__), caminho_relativo_db)
                    os.makedirs(os.path.dirname(caminho_destino_abs), exist_ok=True)
                    shutil.copy(estado['caminho_imagem'], caminho_destino_abs)
                    caminho_imagem_db = caminho_relativo_db
                
                sucesso = crud.inserir_produto(ref, sku, desc, tam, bipe, preco_str, caminho_imagem_db)
                
                if sucesso:
                    self.itens_pendentes_cadastro.pop(estado['indice_atual'])
                    estado['inseridos'] += 1
                    atualizar_contador()
                    mostrar_item_atual()
                
            except Exception as e:
                messagebox.showerror("Erro ao Salvar", f"Não foi possível salvar o produto: {e}", parent=dialog)
        
        main_frame = ttk.Frame(dialog, padding=15)
        main_frame.pack(fill=BOTH, expand=True)
        main_frame.columnconfigure(1, weight=1)

        vcmd_numeros = (dialog.register(_validar_apenas_numeros), '%P')

        ttk.Label(main_frame, text=f"{estado['total_itens']} produtos do arquivo não foram encontrados...", wraplength=550).grid(row=0, column=0, columnspan=2, pady=(0,5))
        ttk.Label(main_frame, text="Deseja inseri-los agora ou depois? ...").grid(row=1, column=0, columnspan=2, pady=(0,15))
        lbl_contador = ttk.Label(main_frame, text="", font="-weight bold")
        lbl_contador.grid(row=2, column=0, columnspan=2, pady=(0,15))
        
        form_frame = ttk.LabelFrame(main_frame, text="Dados do Produto")
        form_frame.grid(row=3, column=0, columnspan=2, sticky="ew")
        form_frame.columnconfigure(1, weight=1)
        
        ttk.Label(form_frame, text="Referência*:").grid(row=0, column=0, sticky="e", padx=5, pady=4)
        ttk.Entry(form_frame, textvariable=ref_var, state="readonly").grid(row=0, column=1, sticky="ew", padx=5)

        ttk.Label(form_frame, text="Descrição*:").grid(row=1, column=0, sticky="e", padx=5, pady=4)
        ttk.Entry(form_frame, textvariable=desc_var, state="readonly").grid(row=1, column=1, sticky="ew", padx=5)
        
        ttk.Label(form_frame, text="Tamanho*:").grid(row=2, column=0, sticky="e", padx=5, pady=4)
        ttk.Entry(form_frame, textvariable=tam_var, state="readonly").grid(row=2, column=1, sticky="ew", padx=5)

        ttk.Label(form_frame, text="Preço (R$)*:").grid(row=3, column=0, sticky="e", padx=5, pady=4)
        ttk.Entry(form_frame, textvariable=preco_var).grid(row=3, column=1, sticky="ew", padx=5)

        ttk.Label(form_frame, text="SKU*:").grid(row=4, column=0, sticky="e", padx=5, pady=4)
        entry_sku = ttk.Entry(form_frame, textvariable=sku_var, validate='key', validatecommand=vcmd_numeros)
        entry_sku.grid(row=4, column=1, sticky="ew", padx=5)

        ttk.Label(form_frame, text="Bipe*:").grid(row=5, column=0, sticky="e", padx=5, pady=4)
        entry_bipe = ttk.Entry(form_frame, textvariable=bipe_var, validate='key', validatecommand=vcmd_numeros)
        entry_bipe.grid(row=5, column=1, sticky="ew", padx=5)
        
        ttk.Label(form_frame, text="Imagem*:").grid(row=6, column=0, sticky="e", padx=5, pady=4)
        img_frame = ttk.Frame(form_frame)
        img_frame.grid(row=6, column=1, sticky="ew", padx=5)
        ttk.Button(img_frame, text="Carregar Imagem...", command=selecionar_imagem_pendente).pack(side=LEFT)
        ttk.Label(img_frame, textvariable=caminho_imagem_var).pack(side=LEFT, padx=5)

        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=(20,0))
        
        ttk.Button(btn_frame, text="Lembrar Depois", command=dialog.destroy, bootstyle=(SECONDARY, OUTLINE)).pack(side=LEFT, padx=10, ipady=5)
        ttk.Button(btn_frame, text="Adicionar", command=adicionar_item_atual, bootstyle=PRIMARY).pack(side=RIGHT, padx=10, ipady=5)
        
        atualizar_contador()
        mostrar_item_atual()

if __name__ == "__main__":
    janela = ttk.Window(themename='united')
    app = Tela(janela)
    janela.mainloop()