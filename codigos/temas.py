import tkinter as tk
from tkinter import ttk, messagebox
from ttkbootstrap.constants import SUCCESS, SECONDARY
from tkinter.constants import BOTH, X, BOTTOM, RIGHT
import configparser
class GerenciadorTema:
    def __init__(self, janela):
        self.janela = janela

    def mudar_tema(self):
        print("alo")
        self.tpl_temas = tk.Toplevel(self.janela)
        self.tpl_temas.title('Alteração de Tema')
        self.tpl_temas.geometry("300x200")
        self.tpl_temas.resizable(False, False)
        self.tpl_temas.transient(self.janela)
        self.tpl_temas.grab_set()

        self.temas = {
            'Claro': 'united',
            'Escuro': 'darkly'
        }

        frm_temas = ttk.Frame(self.tpl_temas, padding=20)
        frm_temas.pack(expand=True, fill=BOTH)

        lbl_tema = ttk.Label(frm_temas, text='Escolha o Tema:')
        lbl_tema.pack(pady=(0, 5))

        self.cbx_tema = ttk.Combobox(frm_temas, values=list(self.temas.keys()), state='readonly')
        try:
            tema_atual_real = self.janela.style.theme_use()
            for nome, real in self.temas.items():
                if real == tema_atual_real:
                    self.cbx_tema.set(nome)
                    break
            if not self.cbx_tema.get():
                self.cbx_tema.current(0)
        except:
            self.cbx_tema.current(0)

        self.cbx_tema.pack(fill=X, pady=5)

        frm_botoes = ttk.Frame(frm_temas)
        frm_botoes.pack(side=BOTTOM, fill=X, pady=(10, 0))

        btn_concluir = ttk.Button(frm_botoes, text='Concluir', command=self.confirmar_mudanca_tema, bootstyle=SUCCESS)
        btn_concluir.pack(side=RIGHT, padx=5)

        btn_cancelar = ttk.Button(frm_botoes, text='Cancelar', command=self.tpl_temas.destroy, bootstyle=SECONDARY)
        btn_cancelar.pack(side=RIGHT, padx=5)

    def confirmar_mudanca_tema(self):
        tema_visivel = self.cbx_tema.get()
        if tema_visivel in self.temas:
            tema_real = self.temas[tema_visivel]
            try:
                self.janela.style.theme_use(tema_real)
                
                # Salva o tema escolhido no arquivo de configuração
                config = configparser.ConfigParser()
                config['CONFIGURACAO'] = {'tema': tema_real}
                with open('config.ini', 'w') as configfile:
                    config.write(configfile)
                
                # Fecha a janela de temas após a confirmação
                self.tpl_temas.destroy()

            except tk.TclError:
                messagebox.showwarning("Erro de Tema", f"Não foi possível aplicar o tema '{tema_real}'. Pode não estar instalado.")
        else:
            messagebox.showwarning("Seleção Inválida", "Por favor, selecione um tema válido.")
