import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk #importando a biblioteca - necessário em todos os arquivos que mexem na interface -.
from ttkbootstrap.constants import *
from tela_principal import TelaMenu #importando a classe da tela principal que chamei de menu. Podem mudar o nome, mas alterem as chamadas corretamente para não haver erros.

class Tela: #iniciando a classe.
    def __init__(self, master):
        self.janela = master
        self.janela.title('Checkpoint')

        self.janela.geometry("450x450") # definindo o tamanho da tela ao ser gerada. Meramente estética.

        self.tela_principal = TelaMenu (self.janela) #tras a classe TelaMenu do arquivo 'tela_principal' para esta classe, ligando as duas .

        self.log = ttk.Frame(janela, width=200, height=300,) #inicio um frame pra comportar os elementos da tela de login. Usei por que acho que fica mais organizado, mas não é necessário.
        self.log.place(relx=0.5, rely=0.5, anchor="center") #printando o frame. Usei o ".place" por sugestão do gpt. aparentemente ele só pode ser centralizado se usar esse place. 

    # Adicionando elementos no frame:
        self.lbl_user = ttk.Label(self.log, text='Usuário:                                 ', font = ("Arial", 14)) # iniciei a label e usei essa quantidade de espaços pra ficar mais bonito visualmente.
        self.lbl_user.grid(row=0, column=0, columnspan=2, sticky="w") # posicionando a label
        self.user_ent = tk.Entry(self.log) # iniciando a entrada para receber a senha
        self.user_ent.grid(row=1, column=0, columnspan=2, pady=5, ipady=5, ipadx=14, sticky='EW') # posicionando essa entrada
        # TODOS OS COMPONENTES DAQUI PRA FRENTE SEGUEM ESSE PADRÃO. CASO ALGO MUDE, EU COMENTO NA HORA.

        self.lbl_senha = ttk.Label(self.log, text = 'Senha:', font = ("Arial", 14))
        self.lbl_senha.grid(row=2, column=0, sticky="w")
        self.ent_senha = tk.Entry(self.log, show="*")
        self.ent_senha.grid(row=3, column=0, columnspan=2, pady=5, ipady=5, ipadx=14, sticky='EW')

        self.btn_entrar = tk.Button(self.log, text='Entrar', bg='darkblue', fg='white', font = ("Arial", 14), command=self.autentica) #chama a classe TelaMenu a partir da interação com o botão.
        self.btn_entrar.grid(row=4, column=0, columnspan=2, pady=10)

    def autentica(self):
        if self.user_ent.get() == "adm" and self.ent_senha.get() == "adm":
            self.tela_principal.menu()
        else:
            messagebox.showwarning("Atenção!","Verificar credenciais.")

# os comandos  abaixo fazem parte do loop da tela, que é usado pra iniciar a tela. N sei explicar, mas só sei fazer assim.
janela = ttk.Window(themename='united')
app = Tela(janela)
janela.mainloop()