import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog
from tkinter import simpledialog

class TelaMenu:
    def __init__(self, janela):
        self.janela = janela
        self.dados_originais = [] # Lista para armazenar todos os dados lidos do arquivo

    def menu(self):
        # --- Esta parte permanece inalterada ---
        self.tpl_menu = tk.Toplevel(self.janela)
        self.tpl_menu.geometry('1400x500')

        self.mnu_principal = tk.Menu(self.tpl_menu)

        self.mnu_inventario = tk.Menu(self.mnu_principal, tearoff=0)
        self.mnu_principal.add_cascade(label='Inventário', menu=self.mnu_inventario)
        self.mnu_inventario.add_command(label='Rotativo', command=self.interacao_inventario)

        self.mnu_pt_vendas = tk.Menu(self.mnu_principal, tearoff=0)
        self.mnu_principal.add_cascade(label='Ponto de Venda', menu=self.mnu_pt_vendas)
        self.mnu_pt_vendas.add_command(label='Nova Venda')
        self.mnu_pt_vendas.add_command(label='Ver Vendas')

        self.mnu_configuracao = tk.Menu(self.mnu_principal, tearoff=0)
        self.mnu_principal.add_cascade(label='Configurações', menu=self.mnu_configuracao)
        self.mnu_configuracao.add_command(label='Temas', command=self.mudar_tema)

        self.tpl_menu.config(menu=self.mnu_principal)

        # Frame principal para os widgets do inventário
        # Usaremos um frame principal para facilitar a limpeza se necessário,
        # embora a lógica atual limpe apenas os widgets dentro dele.
        self.frm_principal_inventario = ttk.Frame(self.tpl_menu)
        self.frm_principal_inventario.pack(fill=BOTH, expand=True, padx=10, pady=10) # Ocupa o espaço disponível

        # Chama a função para configurar a interface do inventário imediatamente
        self.interacao_inventario()

    def interacao_inventario(self):
        # Limpa widgets anteriores *dentro* do frame principal do inventário, se já existirem
        for widget in self.frm_principal_inventario.winfo_children():
            widget.destroy()

        # --- Configuração da Interface do Inventário ---

        # Frame para o botão de Upload (organização)
        frm_upload = ttk.Frame(self.frm_principal_inventario)
        frm_upload.pack(pady=10) # Espaçamento vertical

        # Label e Botão para Upload
        self.lbl_ad_arquivo = ttk.Label(frm_upload, text='Adicione o Arquivo de Inventário:')
        self.lbl_ad_arquivo.grid(row=0, column=0, padx=5)

        self.btn_ad_arquivo = ttk.Button(frm_upload, text='Upload Arquivo (.txt)', command=self.upp_arquivo)
        self.btn_ad_arquivo.grid(row=0, column=1, padx=5)

        # Frame para o Treeview e Scrollbar (organização)
        frm_treeview = ttk.Frame(self.frm_principal_inventario)
        frm_treeview.pack(fill=BOTH, expand=True, pady=(0, 10)) # Ocupa espaço, com margem inferior

        # Treeview
        colunas = ("col1", "col2", "col3", "col4", "col5", "col6")
        self.tvw_inventario = ttk.Treeview(frm_treeview, columns=colunas, show="headings", height=15) # Altura inicial

        # Configuração da tag para destacar linhas "pdv"
        self.tvw_inventario.tag_configure("sigla_afd", background="lightblue") # Cor vermelha clara

        # Define os nomes e larguras (opcional) das colunas
        self.tvw_inventario.heading("col1", text="Nome")
        self.tvw_inventario.column("col1", width=250)
        self.tvw_inventario.heading("col2", text="Categoria")
        self.tvw_inventario.column("col2", width=150)
        self.tvw_inventario.heading("col3", text="Tamanho/Capacidade")
        self.tvw_inventario.column("col3", width=150)
        self.tvw_inventario.heading("col4", text="Preço")
        self.tvw_inventario.column("col4", width=100, anchor=E) # Alinha à direita (E=East)
        self.tvw_inventario.heading("col5", text="Estoque")
        self.tvw_inventario.column("col5", width=100, anchor=CENTER) # Alinha ao centro
        self.tvw_inventario.heading("col6", text="Est.Real")
        self.tvw_inventario.column("col6", width=100, anchor=CENTER)

        # Adiciona Scrollbar Vertical ao Treeview
        scrollbar_y = ttk.Scrollbar(frm_treeview, orient="vertical", command=self.tvw_inventario.yview)
        self.tvw_inventario.configure(yscrollcommand=scrollbar_y.set)

        # Posiciona o Treeview e a Scrollbar usando grid dentro do frm_treeview
        self.tvw_inventario.grid(row=0, column=0, sticky="nsew") # Ocupa todo o espaço do grid
        scrollbar_y.grid(row=0, column=1, sticky="ns") # Ocupa altura total

        # Configura o frm_treeview para expandir a coluna 0 (onde está o Treeview)
        frm_treeview.grid_rowconfigure(0, weight=1)
        frm_treeview.grid_columnconfigure(0, weight=1)


        # Associa o evento de duplo clique à função de edição
        self.tvw_inventario.bind("<Double-1>", self.editar_celula)

        # Frame para os botões de filtro (organização)
        frm_filtros = ttk.Frame(self.frm_principal_inventario)
        frm_filtros.pack(pady=10)

        self.lbl_visual = ttk.Label(frm_filtros, text="Filtrar por tipo:")
        self.lbl_visual.grid(row=0, column=0, padx=5, pady=5)

        # Botões de Filtro - usam lambda para passar o critério para a função filtrar_treeview
        self.btn_todos = ttk.Button(frm_filtros, text="Mostrar Todos", command=lambda: self.filtrar_treeview(None)) # Botão para limpar filtro
        self.btn_todos.grid(row=0, column=1, padx=5)

        self.btn_camisa = ttk.Button(frm_filtros, text="Capas", command=lambda: self.filtrar_treeview("Capa"))
        self.btn_camisa.grid(row=0, column=2, padx=5)

        self.btn_meia = ttk.Button(frm_filtros, text="Meia", command=lambda: self.filtrar_treeview("Meia"))
        self.btn_meia.grid(row=0, column=3, padx=5)

        self.btn_pdv = ttk.Button(frm_filtros, text="PDV", command=lambda: self.filtrar_treeview("pdv"))
        self.btn_pdv.grid(row=0, column=4, padx=5)

        # Atualiza a exibição inicial (caso já haja dados carregados anteriormente)
        self.filtrar_treeview(None)

    def upp_arquivo(self):
        caminho_arquivo = filedialog.askopenfilename(
            title="Selecione um Arquivo",
            filetypes=[("Arquivos de texto", "*.txt"), ("Todos os arquivos", "*.*")]
        )

        if caminho_arquivo:
            self.dados_originais = [] # Limpa dados antigos antes de carregar novos
            try:
                with open(caminho_arquivo, "r", encoding="utf-8") as file:
                    linhas = file.readlines()

                for linha in linhas:
                    dados = [campo.strip() for campo in linha.split(";")] # Remove espaços extras
                    if len(dados) >= 5:
                        while len(dados) < 6:
                            dados.append("") # Garante 6 colunas
                        self.dados_originais.append(dados) # Adiciona à lista principal

                # Após carregar, atualiza o Treeview para mostrar todos os dados
                self.filtrar_treeview(None)

            except Exception as e:
                tk.messagebox.showerror("Erro de Leitura", f"Não foi possível ler o arquivo:\n{e}")


    def filtrar_treeview(self, criterio=None):
        # Garante que o Treeview exista antes de tentar manipular
        if not hasattr(self, "tvw_inventario"):
            return

        # 1. Limpa o Treeview atual
        for item in self.tvw_inventario.get_children():
            self.tvw_inventario.delete(item)

        # 2. Repopula o Treeview com base nos dados_originais e no critério
        for dados in self.dados_originais:
            mostrar = False
            tags_aplicar = () # Tags a serem aplicadas na linha

            # Verifica se a linha atual contém "pdv" no nome (coluna 0) para aplicar a tag
            # Faz a verificação aqui para aplicar a tag mesmo quando não está filtrando por "pdv"
            if len(dados) > 0 and "pdv" in dados[0].lower():
                 tags_aplicar = ("sigla_afd",)

            # Lógica de filtragem
            if criterio is None: # Mostrar todos
                mostrar = True
            elif criterio == "Capa" and len(dados) > 1 and criterio.lower() in dados[0].lower(): # Filtra por Categoria (coluna 1) - Case Insensitive
                mostrar = True
            elif criterio == "Meia" and len(dados) > 1 and criterio.lower() in dados[0].lower(): # Filtra por Categoria (coluna 1) - Case Insensitive
                mostrar = True
            elif criterio == "pdv": # Filtra por Nome (coluna 0) - Case Insensitive
                # A tag já foi definida acima, aqui só decidimos se mostramos a linha
                if len(dados) > 0 and criterio.lower() in dados[0].lower():
                    mostrar = True


            # Se a linha passou no filtro, insere no Treeview com as tags corretas
            if mostrar:
                self.tvw_inventario.insert("", "end", values=dados, tags=tags_aplicar)


    def editar_celula(self, event):
        # --- Esta função permanece inalterada ---
        item_id = self.tvw_inventario.focus() # Pega o ID do item (linha) focado
        if not item_id: # Se nada estiver focado, não faz nada
            return

        coluna_id = self.tvw_inventario.identify_column(event.x) # Identifica a coluna clicada (ex: '#1', '#2'...)

        # Verifica se o clique foi na coluna 6 ('#6')
        if coluna_id == "#6":
            valores_atuais = list(self.tvw_inventario.item(item_id, "values")) # Pega todos os valores da linha como lista
            valor_atual_col6 = valores_atuais[5] # Pega o valor específico da 6ª coluna (índice 5)

            # Abre diálogo para obter o novo valor
            novo_valor = simpledialog.askstring("Editar Estoque Real",
                                                "Digite o novo valor:",
                                                initialvalue=valor_atual_col6,
                                                parent=self.tpl_menu) # Define a janela pai

            # Se o usuário inseriu um valor (não cancelou)
            if novo_valor is not None:
                valores_atuais[5] = novo_valor # Atualiza o valor na lista
                self.tvw_inventario.item(item_id, values=valores_atuais) # Atualiza a linha no Treeview

                # --- Opcional: Atualizar self.dados_originais ---
                # Para manter a consistência, seria bom atualizar a lista original também.
                # Isso requer encontrar o item correspondente em self.dados_originais.
                # Pode ser um pouco mais complexo se a ordem não for garantida ou se houver duplicatas.
                # Uma forma simples (se a ordem for mantida e não houver exclusões diretas no treeview):
                try:
                    index = self.tvw_inventario.index(item_id) # Pega o índice visual no Treeview *filtrado*
                    # ATENÇÃO: Isso só funciona corretamente se o Treeview não estiver filtrado
                    # ou se você tiver uma maneira de mapear o item_id de volta ao índice original.
                    # Uma abordagem mais robusta seria buscar pelos dados únicos (ex: nome+categoria+tamanho)
                    # em self.dados_originais.
                    # Exemplo de busca (simplificado, assume nome é único na lista original):
                    nome_item = valores_atuais[0]
                    for i, original_data in enumerate(self.dados_originais):
                         if original_data[0] == nome_item: # Encontra pelo nome (pode precisar de critério melhor)
                             self.dados_originais[i][5] = novo_valor
                             break # Para após encontrar
                except Exception as e:
                     print(f"Aviso: Não foi possível atualizar dados_originais - {e}")
                     # Implementar lógica de mapeamento mais robusta se necessário


    def mudar_tema(self):
        # --- Esta função permanece inalterada ---
        print("alo") # Mensagem de depuração
        self.tpl_temas = tk.Toplevel(self.janela)
        self.tpl_temas.title('Alteração de Tema')
        self.tpl_temas.geometry("300x200") # Tamanho razoável
        self.tpl_temas.resizable(False, False) # Impede redimensionamento
        self.tpl_temas.transient(self.janela) # Mantém sobre a janela principal
        self.tpl_temas.grab_set() # Impede interação com outras janelas

        self.temas = {
            'Claro': 'united', # Exemplo de tema claro
            'Escuro': 'darkly', # Exemplo de tema escuro (solar é outra opção)
            'Cyborg': 'cyborg', # Outro escuro
            'Vapor': 'vaporwave' # Outro tema
         } # Temas disponíveis

        frm_temas = ttk.Frame(self.tpl_temas, padding=20) # Padding interno
        frm_temas.pack(expand=True, fill=BOTH) # Ocupa todo o espaço da janela Toplevel

        lbl_tema = ttk.Label(frm_temas, text='Escolha o Tema:')
        lbl_tema.pack(pady=(0, 5)) # Espaço abaixo

        # Usa state='readonly' para impedir digitação, forçando seleção
        self.cbx_tema = ttk.Combobox(frm_temas, values=list(self.temas.keys()), state='readonly')
        # Tenta pré-selecionar o tema atual
        try:
             tema_atual_real = self.janela.style.theme_use()
             for nome, real in self.temas.items():
                 if real == tema_atual_real:
                     self.cbx_tema.set(nome)
                     break
             if not self.cbx_tema.get(): # Se não encontrou, seleciona o primeiro
                 self.cbx_tema.current(0)
        except:
             self.cbx_tema.current(0) # Seleciona o primeiro em caso de erro

        self.cbx_tema.pack(fill=X, pady=5) # Ocupa largura, espaço vertical

        frm_botoes = ttk.Frame(frm_temas)
        # Centraliza os botões usando pack com side=LEFT/RIGHT e expand=True em um frame vazio no meio
        frm_botoes.pack(side=BOTTOM, fill=X, pady=(10, 0)) # Cola na parte inferior

        btn_concluir = ttk.Button(frm_botoes, text='Concluir', command=self.confirmar_mudanca_tema, bootstyle=SUCCESS)
        btn_concluir.pack(side=RIGHT, padx=5)

        btn_cancelar = ttk.Button(frm_botoes, text='Cancelar', command=self.tpl_temas.destroy, bootstyle=SECONDARY)
        btn_cancelar.pack(side=RIGHT, padx=5)


    def confirmar_mudanca_tema(self):
        # --- Esta função permanece inalterada ---
        tema_visivel = self.cbx_tema.get()
        if tema_visivel in self.temas:
            tema_real = self.temas[tema_visivel]
            try:
                self.janela.style.theme_use(tema_real)
                # Tenta aplicar o tema à janela do menu também, se existir
                if hasattr(self, 'tpl_menu') and self.tpl_menu.winfo_exists():
                     ttk.Style().theme_use(tema_real) # Reaplicar globalmente pode ser necessário
                self.tpl_temas.destroy() # Fecha a janela de seleção
            except tk.TclError:
                 tk.messagebox.showwarning("Erro de Tema", f"Não foi possível aplicar o tema '{tema_real}'. Pode não estar instalado.")
        else:
             tk.messagebox.showwarning("Seleção Inválida", "Por favor, selecione um tema válido.")


# # Código para iniciar a aplicação (exemplo)
# if __name__ == "__main__":
#     # Use ttkbootstrap Window para aplicar o tema inicial
#     # root = tk.Tk() # Tkinter padrão
#     root = ttk.Window(themename="united") # Inicia com um tema ttkbootstrap
#     root.title("Sistema Principal")
#     root.geometry("400x300")

#     # Esconde a janela principal inicial se você só quer mostrar o menu
#     # root.withdraw()

#     app_menu = TelaMenu(root)

#     # Botão na janela principal para abrir o menu (exemplo)
#     btn_abrir_menu = ttk.Button(root, text="Abrir Menu Principal", command=app_menu.menu)
#     btn_abrir_menu.pack(pady=50)

#     root.mainloop()