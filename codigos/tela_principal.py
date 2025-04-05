import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import simpledialog

class TelaMenu:
    def __init__(self, janela):
        self.janela = janela

    def menu(self):
        self.tpl_menu = tk.Toplevel(self.janela)  # Cria uma nova janela (filha da principal)
        self.tpl_menu.geometry('1400x500')  # Define o tamanho da nova janela

        self.mnu_principal = tk.Menu(self.tpl_menu)  # Cria o menu principal da janela

        # Menu "Inventário"
        self.mnu_inventario = tk.Menu(self.mnu_principal, tearoff=0)  # Cria submenu sem linha destacada
        self.mnu_principal.add_cascade(label='Inventário', menu=self.mnu_inventario)  # Adiciona o submenu ao menu principal
        self.mnu_inventario.add_command(label='Rotativo', command=self.interacao_inventario)  # Adiciona um item ao submenu que chama a função correspondente

        # Menu "Ponto de Venda"
        self.mnu_pt_vendas = tk.Menu(self.mnu_principal, tearoff=0)  # Cria submenu de ponto de vendas
        self.mnu_principal.add_cascade(label='Ponto de Venda', menu=self.mnu_pt_vendas)  # Adiciona ao menu principal
        self.mnu_pt_vendas.add_command(label='Nova Venda')  # Item de menu sem ação ainda
        self.mnu_pt_vendas.add_command(label='Ver Vendas')  # Outro item sem ação ainda

        # Menu "Configurações"
        self.mnu_configuracao = tk.Menu(self.mnu_principal, tearoff=0)  # Cria submenu de configurações
        self.mnu_principal.add_cascade(label='Configurações', menu=self.mnu_configuracao)  # Adiciona ao menu principal

        self.tpl_menu.config(menu=self.mnu_principal)  # Aplica o menu na janela

        # Frame do Inventário
        self.frm_inventario = ttk.Frame(self.tpl_menu)  # Cria um frame onde os widgets do inventário ficarão organizados
        self.frm_inventario.pack()  # Adiciona o frame à janela

    def interacao_inventario(self):  # Função chamada ao clicar em "Rotativo" no menu
        for widget in self.frm_inventario.winfo_children():  # Percorre todos os widgets filhos do frame
            widget.destroy()  # Remove todos eles para evitar sobreposição

        # Label
        self.lbl_ad_arquivo = ttk.Label(self.frm_inventario, text='Adicione o Arquivo')  # Cria uma label informativa
        self.lbl_ad_arquivo.pack()  # Adiciona a label ao frame

        # Botão para Upload
        self.btn_ad_arquivo = ttk.Button(self.frm_inventario, text='Upload', command=self.upp_arquivo)  # Cria botão para carregar arquivo
        self.btn_ad_arquivo.pack()  # Adiciona o botão ao frame

        # Treeview
        colunas = ("col1", "col2", "col3", "col4", "col5", "col6")  # Define os identificadores das colunas da tabela
        self.tvw_inventario = ttk.Treeview(self.frm_inventario, columns=colunas, show="headings")  # Cria a Treeview sem a coluna de ícones ("headings" exibe apenas os títulos)

        # Define os nomes visíveis para cada coluna da Treeview
        self.tvw_inventario.heading("col1", text="Nome")
        self.tvw_inventario.heading("col2", text="Categoria")
        self.tvw_inventario.heading("col3", text="Tamanho/Capacidade")
        self.tvw_inventario.heading("col4", text="Preço")
        self.tvw_inventario.heading("col5", text="Estoque")
        self.tvw_inventario.heading("col6", text="Est.Real")

        self.tvw_inventario.pack(pady=5)  # Adiciona a tabela ao frame com um pequeno espaço acima e abaixo

        self.tvw_inventario.bind("<Double-1>", self.editar_celula)  # Associa o evento de duplo clique à função de edição (em qualquer linha, mas editará apenas a coluna 6)

    def upp_arquivo(self):  # Função chamada ao clicar no botão Upload
        caminho_arquivo = filedialog.askopenfilename(
            title="Selecione um Arquivo",
            filetypes=[("Arquivos de texto", "*.txt"), ("Todos os arquivos", "*.*")]
        )  # Abre uma janela para o usuário selecionar um arquivo .txt

        if caminho_arquivo:  # Se um arquivo foi selecionado
            with open(caminho_arquivo, "r", encoding="utf-8") as file:
                linhas = file.readlines()  # Lê todas as linhas do arquivo

            # Garante que o Treeview já foi criado antes de tentar inserir dados
            if hasattr(self, "tvw_inventario"):
                for item in self.tvw_inventario.get_children():  # Remove todos os itens atualmente exibidos
                    self.tvw_inventario.delete(item)

                for linha in linhas:
                    dados = linha.strip().split(";")  # Separa os dados da linha por ponto e vírgula
                    if len(dados) >= 5:  # Se houver ao menos 5 colunas
                        while len(dados) < 6:
                            dados.append("")  # Preenche com vazio se faltar a 6ª coluna
                        self.tvw_inventario.insert("", "end", values=(dados[0], dados[1], dados[2], dados[3], dados[4], dados[5]))  # Insere os dados como uma nova linha na Treeview

    def editar_celula(self, event):  # Função para editar o valor da 6ª coluna (Est.Real) ao clicar duas vezes
        cedula_valor = self.tvw_inventario.focus()  # Pega o item (linha) que foi clicado
        cedula = self.tvw_inventario.identify_column(event.x)  # Identifica a coluna clicada (ex: '#1', '#2'...)
        cedula = cedula.replace('#', '')  # Remove o símbolo '#' da frente

        if cedula == "6":  # Se a coluna clicada for a de índice 6 (coluna "Est.Real")
            at_cd_valor = self.tvw_inventario.item(cedula_valor, "values")[5]  # Pega o valor atual da 6ª coluna
            nv_cd_valor = simpledialog.askstring("Editar", "Novo valor:", initialvalue=at_cd_valor)  # Abre uma caixinha de diálogo para o usuário digitar o novo valor
            if nv_cd_valor is not None:  # Se o usuário não cancelou
                values = list(self.tvw_inventario.item(cedula_valor, "values"))  # Pega todos os valores da linha
                values[5] = nv_cd_valor  # Substitui o valor da 6ª coluna pelo novo
                self.tvw_inventario.item(cedula_valor, values=values)  # Atualiza os valores da linha no Treeview