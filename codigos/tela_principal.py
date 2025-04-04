import tkinter as ttk
from tkinter import filedialog # biblioteca necessaria para a importação de arquivos
class TelaMenu:
    def __init__(self, janela):
        self.janela = janela

    def menu(self):
        self.tpl_menu = ttk.Toplevel(self.janela) # Inicia uma nova tela a partir do botão da tela de login.
        self.tpl_menu.geometry('700x700')

        self.mnu_principal = ttk.Menu(self.tpl_menu) # criando uma barra de menu que vai receber elementos como inventario, e outros. Atenção: em caso de mudança, tomar cuidado pois o menu só aparece na tela quanado com os seus elementos, seja um ou mais.

        # Adicionando o menu "Inventário" á barra:
        self.mnu_inventario = ttk.Menu(self.mnu_principal, tearoff=0) # gerando um "botão" na barra de menu
        self.mnu_principal.add_cascade(label= 'Inventário', menu=self.mnu_inventario) # dando um nome e adicionando uma label a esse "botão"
        self.mnu_inventario.add_command(label= 'Rotativo', command=self.interacao_inventario) # adicionando uma opção de interação que aparece ao clicar no "botão" do menu que serve como um comando para que quando clique nessa opção, apareça um frame que permite fazer upload de um arquivo

        # Adicionando o menu "Ponto de vendas":
        self.mnu_pt_vendas = ttk.Menu(self.mnu_principal, tearoff=0)
        self.mnu_principal.add_cascade(label = 'Ponto de Venda', menu=self.mnu_pt_vendas)
        self.mnu_pt_vendas.add_command(label = 'Nova Venda')
        self.mnu_pt_vendas.add_command(label ='Ver Vendas')

        # adicionando o menu "Configurações" á barra:
        self.mnu_configuracao = ttk.Menu(self.mnu_principal, tearoff=0)
        self.mnu_principal.add_cascade(label = 'Configurações')

        self.tpl_menu.config(menu=self.mnu_principal) #Mostrando a barra do menu na tela.

        # Frame do Inventário:
        self.frm_inventario = ttk.Frame(self.tpl_menu) # Criando o frame na tela tpl_menu. Ele está na tela menu, mas os componentes de dentro do frame apenas aparecem quando o usuário interagir com o menu.

        self.frm_inventario.pack() # mostrando o frame na tela.

    def interacao_inventario(self): # inicia uma função para mostrar o frame apenas ao interagir com o menu. Cada um dos elementos do menu precisa de um desses para serem independentes(até onde eu sei).
        # as duas linhas abaixo verificam se é a primeira vez que o frame é chamado. se não for, ele destroi o frame anterior e tras um novo.
        for widget in self.frm_inventario.winfo_children():
            widget.destroy()
        # Iniciando o frame de interação relativo ao menu Inventario:

        
        # Adicionando elementos no frame:
        self.lbl_ad_arquivo = ttk.Label(self.frm_inventario, text= 'Adicione o Arquivo') # label
        self.lbl_ad_arquivo.pack() # mostrando a label

        self.btn_ad_arquivo = ttk.Button(self.frm_inventario, text= 'Upload', command= self.upp_arquivo) # botão com comando para carregar um arquivo da máquina
        self.btn_ad_arquivo.pack() # mostrando o botão

    def upp_arquivo(self):
        caminho_arquivo = filedialog.askopenfilename(
            title= "Selecione um Arquivo", 
            filetypes= [("Todos os arquivos", "*.*"), ("Arquivos de texto", "*.txt"), ("Imagens", "*.png;*.jpg;*.jpeg")]
        )
