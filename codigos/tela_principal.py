import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog
from tkinter import simpledialog
from tkinter import messagebox
# Assume que 'temas.py' existe e contém a classe GerenciadorTema
# from temas import GerenciadorTema # Descomente se necessário

# Classe placeholder caso 'temas.py' não esteja disponível para teste
class GerenciadorTema:
    def __init__(self, janela):
        self.janela = janela
    # Adicione métodos se a classe original tiver mais funcionalidades usadas

class TelaMenu:
    def __init__(self, janela):
        self.janela = janela
        # Lista principal para armazenar dados do arquivo TXT
        # Estrutura: [iid, ref, sku, desc, tam, quant, valor, est_real]
        # self.gerenciador_tema = GerenciadorTema(self.janela) # Descomente se usar a classe real
        self.dados_originais = []
        # Contador para gerar IDs únicos para novos itens adicionados manualmente
        self.novo_item_contador = 0

        # --- NÃO HÁ MAIS CONFIGURAÇÃO DE BANCO DE DADOS ---

        # --- FUNÇÕES DE BANCO DE DADOS REMOVIDAS ---
        # conectar_db, desconectar_db, executar_query, carregar_produtos_do_banco,
        # atualizar_quantidade_produto foram removidos.

    def menu(self):
        # --- Configuração do Menu Toplevel ---
        self.tpl_menu = tk.Toplevel(self.janela)
        self.tpl_menu.geometry('1400x800')
        self.tpl_menu.title("Controle de Inventário")

        self.mnu_principal = tk.Menu(self.tpl_menu)

        self.mnu_inventario = tk.Menu(self.mnu_principal, tearoff=0)
        self.mnu_principal.add_cascade(label='Inventário', menu=self.mnu_inventario)
        self.mnu_inventario.add_command(label='Recarregar Interface', command=self.interacao_inventario)

        self.mnu_pt_vendas = tk.Menu(self.mnu_principal, tearoff=0)
        self.mnu_principal.add_cascade(label='Ponto de Venda', menu=self.mnu_pt_vendas)
        self.mnu_pt_vendas.add_command(label='Nova Venda', command=self.abrir_ponto_venda)

        self.mnu_configuracao = tk.Menu(self.mnu_principal, tearoff=0)
        self.mnu_principal.add_cascade(label='Configurações', menu=self.mnu_configuracao)
        self.mnu_configuracao.add_command(label='Temas', command=self.mudar_tema)

        self.tpl_menu.config(menu=self.mnu_principal)

        # Frame principal
        self.frm_principal_inventario = ttk.Frame(self.tpl_menu)
        self.frm_principal_inventario.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Chama a configuração da interface do inventário ao abrir o menu
        self.interacao_inventario()

    def abrir_ponto_venda(self):
        # Função placeholder para abrir o ponto de venda
        try:
            print("Abrindo PDV (funcionalidade a ser implementada/conectada)...")
            messagebox.showinfo("Em Construção", "A funcionalidade Ponto de Venda ainda não está conectada nesta versão.", parent=self.tpl_menu)
        except ImportError:
            messagebox.showerror("Erro", "Não foi possível encontrar o módulo 'tela_ponto_venda'.", parent=self.tpl_menu)
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir o Ponto de Venda:\n{e}", parent=self.tpl_menu)

    def interacao_inventario(self):
        """Configura a interface do inventário (focada em TXT)."""
        for widget in self.frm_principal_inventario.winfo_children():
            widget.destroy()

        # --- Frame Controle (Upload TXT) ---
        frm_controle = ttk.Frame(self.frm_principal_inventario)
        frm_controle.pack(pady=10, fill=X, anchor='n')

        self.btn_ad_arquivo = ttk.Button(frm_controle, text='Carregar Inventário (.txt)', command=self.upp_arquivo)
        self.btn_ad_arquivo.pack(side=LEFT, padx=5)

        # --- Frame Treeview ---
        frm_treeview = ttk.Frame(self.frm_principal_inventario)
        frm_treeview.pack(fill=BOTH, expand=True, pady=(0, 10))

        colunas_visiveis = ("ref", "sku", "desc", "tam", "preco", "est", "est_real")
        self.tvw_inventario = ttk.Treeview(frm_treeview, columns=colunas_visiveis, show="headings", height=15)

        # --- Tags ---
        self.tvw_inventario.tag_configure("sigla_pdv", background="yellow")
        self.tvw_inventario.tag_configure("zerado", background="lightgray")
        self.tvw_inventario.tag_configure("negativado", background="gray", foreground="white")
        self.tvw_inventario.tag_configure("diferente", background="red", foreground="white")
        self.tvw_inventario.tag_configure("igual", background="lightgreen")

        # --- Cabeçalhos e Larguras ---
        self.tvw_inventario.heading("ref", text="Ref")
        self.tvw_inventario.column("ref", width=70, anchor=CENTER)
        self.tvw_inventario.heading("sku", text="SKU")
        self.tvw_inventario.column("sku", width=70, anchor=CENTER)
        self.tvw_inventario.heading("desc", text="Descrição")
        self.tvw_inventario.column("desc", width=300)
        self.tvw_inventario.heading("tam", text="Tam/Cap")
        self.tvw_inventario.column("tam", width=100)
        self.tvw_inventario.heading("preco", text="Preço")
        self.tvw_inventario.column("preco", width=80, anchor=E)
        self.tvw_inventario.heading("est", text="Estoque")
        self.tvw_inventario.column("est", width=100, anchor=CENTER)
        self.tvw_inventario.heading("est_real", text="Est. Real")
        self.tvw_inventario.column("est_real", width=100, anchor=CENTER)

        # --- Scrollbar ---
        scrollbar_y = ttk.Scrollbar(frm_treeview, orient="vertical", command=self.tvw_inventario.yview)
        self.tvw_inventario.configure(yscrollcommand=scrollbar_y.set)
        self.tvw_inventario.grid(row=0, column=0, sticky="nsew")
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        frm_treeview.grid_rowconfigure(0, weight=1)
        frm_treeview.grid_columnconfigure(0, weight=1)

        # --- Bind Duplo Clique ---
        self.tvw_inventario.bind("<Double-1>", self.editar_celula)

        # --- Frame Filtros e Ações ---
        frm_filtros_acoes = ttk.Frame(self.frm_principal_inventario)
        frm_filtros_acoes.pack(pady=10, fill=X, anchor='s')
        # Configurar colunas para expandir igualmente
        frm_filtros_acoes.columnconfigure((0, 1, 2, 3), weight=1)

        # --- Botão Adicionar Produto --- (Linha 0)
        self.lbl_acao = ttk.Label(frm_filtros_acoes, text="Ações:")
        self.lbl_acao.grid(row=0, column=0, padx=5, pady=5, sticky=W)
        self.btn_add_produto = ttk.Button(frm_filtros_acoes, text="Adicionar Novo Produto", command=self.adicionar_produto)
        # Ocupa mais colunas para centralizar melhor ou dar espaço
        self.btn_add_produto.grid(row=0, column=1, columnspan=3, padx=5, pady=5, sticky=EW)

        # --- Botões de Filtro --- (Linha 1 e seguintes)
        self.lbl_visual = ttk.Label(frm_filtros_acoes, text="Filtrar Lista:")
        self.lbl_visual.grid(row=1, column=0, padx=5, pady=5, sticky=W)

        # Filtros gerais (Linha 2)
        self.btn_todos = ttk.Button(frm_filtros_acoes, text="Mostrar Todos", command=lambda: self.filtrar_treeview(None))
        self.btn_todos.grid(row=2, column=0, padx=5, pady=3, sticky=EW)
        self.btn_pdv = ttk.Button(frm_filtros_acoes, text="PDV", command=lambda: self.filtrar_treeview(("descricao", "pdv")))
        self.btn_pdv.grid(row=2, column=1, padx=5, pady=3, sticky=EW)
        self.btn_negativos = ttk.Button(frm_filtros_acoes, text="Negativados", command=lambda: self.filtrar_treeview(("quantidade", "<0")))
        self.btn_negativos.grid(row=2, column=2, padx=5, pady=3, sticky=EW)
        self.btn_zerados = ttk.Button(frm_filtros_acoes, text="Zerados", command=lambda: self.filtrar_treeview(("quantidade", "0")))
        self.btn_zerados.grid(row=2, column=3, padx=5, pady=3, sticky=EW)

        # Novos Filtros por Descrição (Linha 3)
        self.btn_camisetas = ttk.Button(frm_filtros_acoes, text="Camisetas", command=lambda: self.filtrar_treeview(("descricao", "Camiseta"))) # Assume 'Camiseta' na descrição
        self.btn_camisetas.grid(row=3, column=0, padx=5, pady=3, sticky=EW)
        self.btn_meias = ttk.Button(frm_filtros_acoes, text="Meias", command=lambda: self.filtrar_treeview(("descricao", "Meia"))) # Assume 'Meia' na descrição
        self.btn_meias.grid(row=3, column=1, padx=5, pady=3, sticky=EW)
        self.btn_bones = ttk.Button(frm_filtros_acoes, text="Bonés", command=lambda: self.filtrar_treeview(("descricao", "Boné"))) # Assume 'Boné' na descrição
        self.btn_bones.grid(row=3, column=2, padx=5, pady=3, sticky=EW)
        self.btn_copos = ttk.Button(frm_filtros_acoes, text="Copos", command=lambda: self.filtrar_treeview(("descricao", "Copo"))) # Assume 'Copo' na descrição
        self.btn_copos.grid(row=3, column=3, padx=5, pady=3, sticky=EW)

        # Exibe o Treeview com dados atuais (se houver) ou vazio
        self.filtrar_treeview(None)


    def upp_arquivo(self):
        """Abre um arquivo TXT, lê os dados e atualiza o Treeview."""
        caminho_arquivo = filedialog.askopenfilename(
            title="Selecione o Arquivo de Inventário (.txt)",
            filetypes=[("Arquivos de texto", "*.txt"), ("Todos os arquivos", "*.*")],
            parent=self.tpl_menu
        )
        if not caminho_arquivo: return

        print(f"DEBUG: Carregando arquivo: {caminho_arquivo}")
        self.dados_originais = []
        self.novo_item_contador = 0
        linhas_com_erro = 0
        try:
            with open(caminho_arquivo, "r", encoding="utf-8") as file:
                for i, linha in enumerate(file):
                    linha = linha.strip()
                    if not linha: continue

                    campos = [campo.strip() for campo in linha.split(";")]

                    if len(campos) == 6:
                        ref, sku, desc, tam, quant_str, valor_str = campos
                    else:
                        print(f"AVISO: Linha {i+1} ignorada - esperado 6 campos, encontrado {len(campos)}: {linha}")
                        linhas_com_erro += 1
                        continue

                    try: quant = int(quant_str)
                    except ValueError: quant = 0; print(f"AVISO: Linha {i+1} - Quantidade inválida '{quant_str}', usando 0.")
                    try: valor = float(valor_str.replace(',', '.'))
                    except ValueError: valor = 0.0; print(f"AVISO: Linha {i+1} - Valor inválido '{valor_str}', usando 0.0.")

                    iid = f"file_{i+1}"
                    self.dados_originais.append([iid, ref, sku, desc, tam, quant, valor, ""])

            if linhas_com_erro > 0:
                messagebox.showwarning("Aviso de Leitura",
                                     f"{linhas_com_erro} linha(s) no arquivo TXT foram ignoradas devido a formato incorreto.",
                                     parent=self.tpl_menu)

            self.filtrar_treeview(None)
            print(f"DEBUG: Arquivo TXT carregado ({len(self.dados_originais)} itens processados).")

        except FileNotFoundError:
            messagebox.showerror("Erro de Arquivo", f"Arquivo não encontrado:\n{caminho_arquivo}", parent=self.tpl_menu)
        except Exception as e:
            messagebox.showerror("Erro de Leitura", f"Não foi possível ler o arquivo:\n{e}", parent=self.tpl_menu)


    def adicionar_produto(self):
        """Coleta dados do usuário e adiciona uma nova linha ao inventário (em memória)."""
        ref = simpledialog.askstring("Novo Item", "Referência (Ref):", parent=self.tpl_menu)
        if ref is None: return
        sku = simpledialog.askstring("Novo Item", f"SKU para Ref '{ref}':", parent=self.tpl_menu)
        if sku is None: return
        desc = simpledialog.askstring("Novo Item", "Descrição:", parent=self.tpl_menu)
        if desc is None: return
        tam = simpledialog.askstring("Novo Item", "Tamanho/Capacidade:", parent=self.tpl_menu)
        if tam is None: return
        quant_str = simpledialog.askstring("Novo Item", "Quantidade em Estoque:", parent=self.tpl_menu)
        if quant_str is None: return
        valor_str = simpledialog.askstring("Novo Item", "Preço Unitário (ex: 12.99):", parent=self.tpl_menu)
        if valor_str is None: return

        try: quant = int(quant_str)
        except ValueError:
            messagebox.showerror("Erro de Entrada", "Quantidade inválida. Insira um número inteiro.", parent=self.tpl_menu)
            return
        try: valor = float(valor_str.replace(',', '.'))
        except ValueError:
            messagebox.showerror("Erro de Entrada", "Preço inválido. Insira um número (use '.' como separador decimal).", parent=self.tpl_menu)
            return

        self.novo_item_contador += 1
        iid = f"new_{self.novo_item_contador}"
        nova_linha = [iid, ref.strip(), sku.strip(), desc.strip(), tam.strip(), quant, valor, ""]
        self.dados_originais.append(nova_linha)
        self.filtrar_treeview(None)

        try:
            if self.tvw_inventario.exists(iid):
                self.tvw_inventario.selection_set(iid)
                self.tvw_inventario.focus(iid)
                self.tvw_inventario.see(iid)
            else:
                print(f"Debug: Novo item {iid} adicionado, mas não visível (filtro ativo?).")
        except IndexError: pass

        messagebox.showinfo("Sucesso", "Novo item adicionado à lista em memória.", parent=self.tpl_menu)


    def filtrar_treeview(self, criterio_tupla=None):
        """Filtra o Treeview com base nos dados em self.dados_originais e um critério."""
        if not hasattr(self, "tvw_inventario"):
            print("DEBUG: Treeview não inicializado, filtro abortado.")
            return

        for item in self.tvw_inventario.get_children():
            self.tvw_inventario.delete(item)

        mapa_coluna_indice = {
            "ref": 1, "sku": 2, "descricao": 3, "tam": 4,
            "quantidade": 5, "valor": 6, "est_real": 7
        }
        coluna_filtrar = None
        valor_buscar = None
        comparacao_especial = None

        if criterio_tupla:
            try:
                coluna_filtrar, valor_buscar = criterio_tupla
                if coluna_filtrar == "quantidade":
                    if valor_buscar == "<0": comparacao_especial = "negativo"
                    elif valor_buscar == "0": comparacao_especial = "zero"
            except ValueError:
                print("AVISO: Critério de filtro inválido, mostrando todos.")
                criterio_tupla = None

        for item_data in self.dados_originais:
            if len(item_data) < 8: continue

            iid, ref, sku, desc, tam, quant, valor, est_real = item_data

            # --- Lógica de Tags ---
            tags_aplicar = []
            if "pdv" in str(desc).lower(): tags_aplicar.append("sigla_pdv")
            if isinstance(quant, int):
                if quant == 0: tags_aplicar.append("zerado")
                elif quant < 0: tags_aplicar.append("negativado")

            # Aplica tags de comparação APENAS se Est.Real foi preenchido
            if str(est_real).strip():
                try: comparacao_igual = (int(quant) == int(est_real))
                except (ValueError, TypeError): comparacao_igual = (str(quant).strip() == str(est_real).strip())

                # Adiciona APENAS a tag de comparação ('igual' ou 'diferente')
                # sobrescrevendo qualquer tag de comparação anterior implicitamente
                # pois estamos reconstruindo as tags do zero aqui no filtro.
                if not comparacao_igual:
                    tags_aplicar.append("diferente")
                else:
                    tags_aplicar.append("igual")
            # Se est_real estiver vazio, NENHUMA tag de comparação ('igual'/'diferente') é adicionada.

            # --- Lógica de Filtragem ---
            mostrar = False
            if criterio_tupla is None:
                mostrar = True
            else:
                idx = mapa_coluna_indice.get(coluna_filtrar)
                if idx is not None and idx < len(item_data):
                    valor_coluna = str(item_data[idx]).lower().strip()
                    valor_buscar_lower = str(valor_buscar).lower().strip()

                    if comparacao_especial == "negativo":
                        try: mostrar = (int(item_data[idx]) < 0)
                        except: pass
                    elif comparacao_especial == "zero":
                        try: mostrar = (int(item_data[idx]) == 0)
                        except: pass
                    # Filtro padrão para descrição e outros campos de texto
                    elif coluna_filtrar == "descricao":
                         # Busca exata (ignorando case) para os filtros específicos
                         # Ajuste se precisar de busca parcial ( 'in' )
                         # Para busca parcial: if valor_buscar_lower in valor_coluna:
                         if valor_buscar_lower == valor_coluna or valor_buscar_lower in valor_coluna.split(): # Verifica se contém a palavra
                              mostrar = True
                         # Ou, se a descrição contiver o termo buscado:
                         elif valor_buscar_lower in valor_coluna:
                              mostrar = True

                    elif valor_buscar_lower in valor_coluna: # Filtro padrão para outras colunas
                        mostrar = True

            # --- Insere no Treeview ---
            if mostrar:
                preco_fmt = f"{valor:.2f}" if isinstance(valor, (int, float)) else str(valor)
                valores_display = (ref, sku, desc, tam, preco_fmt, quant, est_real)
                try:
                    self.tvw_inventario.insert("", "end", iid=iid, values=valores_display, tags=tuple(tags_aplicar))
                except tk.TclError as e:
                    print(f"Erro Tkinter ao inserir iid '{iid}': {e}")


    def editar_celula(self, event):
        """Permite editar 'Est. Real', compara com 'Estoque', atualiza APENAS
           a tag de comparação ('igual'/'diferente') e salva em self.dados_originais."""

        item_iid = self.tvw_inventario.focus()
        if not item_iid: return

        coluna_id_str = self.tvw_inventario.identify_column(event.x)

        if coluna_id_str == "#7": # Coluna "Est. Real"
            try:
                valores_atuais_tv = list(self.tvw_inventario.item(item_iid, "values"))
                tags_atuais_tv = list(self.tvw_inventario.item(item_iid, "tags"))

                idx_ref = 0
                idx_sku = 1
                idx_est = 5
                idx_est_real = 6

                valor_estoque_str = str(valores_atuais_tv[idx_est]).strip()
                valor_est_real_atual_str = str(valores_atuais_tv[idx_est_real]).strip()

                novo_valor_est_real = simpledialog.askstring(
                    "Editar Estoque Real (Contagem)",
                    f"Item Ref: {valores_atuais_tv[idx_ref]} SKU: {valores_atuais_tv[idx_sku]}\n"
                    f"Estoque (Arquivo): {valor_estoque_str}\n\n"
                    f"Digite a quantidade contada:",
                    initialvalue=valor_est_real_atual_str,
                    parent=self.tpl_menu
                )

                if novo_valor_est_real is not None:
                    novo_valor_est_real = novo_valor_est_real.strip()

                    # --- ATUALIZA self.dados_originais ---
                    indice_original = -1
                    for i, data in enumerate(self.dados_originais):
                        if data[0] == item_iid:
                            indice_original = i
                            break
                    if indice_original != -1:
                        self.dados_originais[indice_original][7] = novo_valor_est_real
                        print(f"DEBUG: Dados originais atualizados iid {item_iid}. Novo Est.Real: '{novo_valor_est_real}'")
                    else:
                        print(f"AVISO: iid {item_iid} não encontrado em self.dados_originais.")


                    # --- Atualiza Treeview Visualmente ---
                    valores_atuais_tv[idx_est_real] = novo_valor_est_real

                    # Recalcula APENAS as tags de comparação
                    # 1. Mantém todas as tags existentes EXCETO 'igual' e 'diferente'
                    tags_finais = [tag for tag in tags_atuais_tv if tag not in ("diferente", "igual")]
                    print(f"DEBUG: Tags mantidas (antes da nova comparação): {tags_finais}") # Debug

                    # 2. Realiza a nova comparação
                    try: comparacao_igual = (int(valor_estoque_str) == int(novo_valor_est_real))
                    except (ValueError, TypeError): comparacao_igual = (valor_estoque_str == novo_valor_est_real)

                    # 3. Adiciona SOMENTE a nova tag de comparação ('igual' ou 'diferente')
                    if not comparacao_igual:
                        tags_finais.append("diferente")
                        print("DEBUG: Adicionando tag 'diferente'") # Debug
                    else:
                        tags_finais.append("igual")
                        print("DEBUG: Adicionando tag 'igual'") # Debug

                    # 4. Atualiza o item no Treeview
                    self.tvw_inventario.item(item_iid, values=tuple(valores_atuais_tv), tags=tuple(tags_finais))
                    print(f"DEBUG: Tags finais aplicadas ao iid {item_iid}: {tags_finais}") # Debug

            except (tk.TclError, IndexError) as e:
                messagebox.showerror("Erro de Interface", f"Não foi possível ler/atualizar dados do item:\n{e}", parent=self.tpl_menu)
            except Exception as e:
                messagebox.showerror("Erro Inesperado", f"Ocorreu um erro na edição:\n{e}", parent=self.tpl_menu)

    # --- Funções de Tema (mudar_tema, confirmar_mudanca_tema) ---
    def mudar_tema(self):
        self.tpl_temas = tk.Toplevel(self.janela)
        self.tpl_temas.title('Alteração de Tema')
        self.tpl_temas.geometry("300x200")
        self.tpl_temas.resizable(False, False)
        self.tpl_temas.transient(self.janela)
        self.tpl_temas.grab_set()

        self.temas = {
            'Claro': 'united', 'Escuro': 'darkly',
            'Cyborg': 'cyborg', 'Vapor': 'vapor'
        }

        frm_temas = ttk.Frame(self.tpl_temas, padding=20)
        frm_temas.pack(expand=True, fill=BOTH)
        lbl_tema = ttk.Label(frm_temas, text='Escolha o Tema:')
        lbl_tema.pack(pady=(0, 5))
        self.cbx_tema = ttk.Combobox(frm_temas, values=list(self.temas.keys()), state='readonly')
        try:
            tema_atual_real = ttk.Style().theme_use()
            tema_selecionado = False
            for nome_visivel, nome_real in self.temas.items():
                if nome_real == tema_atual_real:
                    self.cbx_tema.set(nome_visivel); tema_selecionado = True; break
            if not tema_selecionado: self.cbx_tema.current(0)
        except Exception: self.cbx_tema.current(0)
        self.cbx_tema.pack(fill=X, pady=5)
        frm_botoes = ttk.Frame(frm_temas)
        frm_botoes.pack(side=BOTTOM, fill=X, pady=(10, 0))
        btn_concluir = ttk.Button(frm_botoes, text='Aplicar', command=self.confirmar_mudanca_tema, bootstyle=SUCCESS)
        btn_concluir.pack(side=RIGHT, padx=5)
        btn_cancelar = ttk.Button(frm_botoes, text='Cancelar', command=self.tpl_temas.destroy, bootstyle=SECONDARY)
        btn_cancelar.pack(side=RIGHT, padx=5)

    def confirmar_mudanca_tema(self):
        tema_visivel = self.cbx_tema.get()
        if tema_visivel in self.temas:
            tema_real = self.temas[tema_visivel]
            try:
                ttk.Style().theme_use(tema_real)
                self.tpl_temas.destroy()
                print(f"DEBUG: Tema alterado para '{tema_real}'.")
            except tk.TclError as e:
                messagebox.showwarning("Erro de Tema", f"Não foi possível aplicar o tema '{tema_real}'.\nDetalhe: {e}", parent=self.tpl_temas)
        else:
            messagebox.showwarning("Seleção Inválida", "Selecione um tema válido.", parent=self.tpl_temas)