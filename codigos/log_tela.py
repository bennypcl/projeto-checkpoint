# log_tela.py (Versão com cores corrigidas no carregamento)
import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, simpledialog
from PIL import Image, ImageTk
from conexao import conectar
import os

from temas import GerenciadorTema
from tela_ponto_venda import TelaPontoVenda
from relatorio_pdf import gerar_relatorio_pdf
from visualizar_treeviews import Consultas

class Tela:
    def __init__(self, master):
        self.janela = master
        self.janela.title('Checkpoint')
        self.janela.state('zoomed')

        self.mapa_imagens = {}
        self.imagem_tk = None
        self.frm_imagem_display = None

        self.log = ttk.Frame(self.janela, width=200, height=300)
        self.log.place(relx=0.5, rely=0.5, anchor="center")
        self.lbl_user = ttk.Label(self.log, text='Usuário:                     ', font=("Arial", 14)); self.lbl_user.grid(row=0, column=0, columnspan=2, sticky="w")
        self.user_ent = tk.Entry(self.log); self.user_ent.grid(row=1, column=0, columnspan=2, pady=5, ipady=5, ipadx=14, sticky='EW'); self.user_ent.focus_set()
        self.lbl_senha = ttk.Label(self.log, text='Senha:', font=("Arial", 14)); self.lbl_senha.grid(row=2, column=0, sticky="w")
        self.ent_senha = tk.Entry(self.log, show="*"); self.ent_senha.grid(row=3, column=0, columnspan=2, pady=5, ipady=5, ipadx=14, sticky='EW')
        self.btn_entrar = tk.Button(self.log, text='Entrar', bg='darkblue', fg='white', font=("Arial", 14), command=self.autentica); self.btn_entrar.grid(row=4, column=0, columnspan=2, pady=10)
        self.janela.bind('<Return>', self.autentica)
        
        self.dados_originais = []
        self.novo_item_contador = 0
        self.gerenciador_tema = GerenciadorTema(self.janela)
        self.tela_venda = TelaPontoVenda(self.janela)
        self.tela_consulta = Consultas(self.janela)
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

    def autentica(self, event=None):
        if self.user_ent.get() == "adm" and self.ent_senha.get() == "adm":
            self.carregar_mapa_de_imagens()
            self.menu()
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
        self.mnu_treeviews = tk.Menu(self.mnu_principal, tearoff=0); self.mnu_principal.add_cascade(label='Consultas', menu=self.mnu_treeviews)
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

        frm_filtros_acoes = ttk.Frame(frm_controles_e_lista)
        frm_filtros_acoes.grid(row=2, column=0, sticky="ew", pady=(0, 10), padx=5)
        frm_filtros_acoes.columnconfigure(0, weight=1)
        frm_acoes = ttk.Frame(frm_filtros_acoes); frm_acoes.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        frm_acoes.columnconfigure(1, weight=1)
        self.lbl_acao = ttk.Label(frm_acoes, text="Ações:"); self.lbl_acao.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.btn_add_produto = ttk.Button(frm_acoes, text="Adicionar Novo Produto", command=self.adicionar_produto); self.btn_add_produto.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
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
        ref = simpledialog.askstring("Novo Produto", "Referência:")
        if not ref: return
        sku = simpledialog.askstring("Novo Produto", "SKU:")
        if not sku: return
        desc = simpledialog.askstring("Novo Produto", "Descrição:")
        quant = simpledialog.askinteger("Novo Produto", "Quantidade:")
        valor = simpledialog.askfloat("Novo Produto", "Valor:")
        tam = simpledialog.askstring("Novo Produto", "Tamanho:")
        self.novo_item_contador += 1
        iid = f"new_{self.novo_item_contador}"
        self.dados_originais.append([iid, ref, sku, desc, tam, quant, valor, ""])
        self.filtrar_treeview(None)

    # --- FUNÇÃO ATUALIZADA COM LÓGICA DE TAGS/CORES CORRIGIDA ---
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

    def abrir_tela_relatorio(self):
        messagebox.showinfo("Relatório", "Função de relatório a ser implementada.")

if __name__ == "__main__":
    janela = ttk.Window(themename='united')
    app = Tela(janela)
    janela.mainloop()