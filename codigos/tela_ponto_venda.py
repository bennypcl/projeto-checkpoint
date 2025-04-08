import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox, simpledialog
import re
from tela_principal import TelaMenu


#colocar um botão de voltar no pdv
#melhorar a exibição do resumo da venda
#scrollbar || aumentar tamanho da tela

#CORRIGIR CHAMADA DA TELA PRINCIPAL NO COISO DO VENDEDOR


class TelaPontoVenda:
    def __init__(self, janela):
        self.janela = janela
        self.vendedor_selecionado = None
        self.dados_cliente = {}
        self.produtos = []
        self.total_compra = 0.0
        self.valor_restante = 0.0
        self.pagamentos = []
        self.vendedores = ["Andressa", "Nízia", "Vitória"]
        self.bandeiras = ["Visa", "MasterCard", "Elo", "Amex"]

        self.frame_atual = None
        self.tela_selecao_vendedor()

    def limpar_frame(self):
        if self.frame_atual:
            self.frame_atual.destroy()

    def tela_selecao_vendedor(self):
        self.vendedor_selecionado = None
        self.dados_cliente = {}
        self.produtos = []
        self.total_compra = 0.0
        self.valor_restante = 0.0
        self.pagamentos = []

        self.limpar_frame()
        self.frame_atual = ttk.Frame(self.janela)
        self.frame_atual.pack(fill="both", expand=True)

        # Container central dentro do frame
        container = ttk.Frame(self.frame_atual)
        container.grid(row=0, column=0)
        self.frame_atual.columnconfigure(0, weight=1)
        self.frame_atual.rowconfigure(0, weight=1)

        # Conteúdo centralizado
        ttk.Label(container, text="Selecione o Vendedor", font=("Arial", 16)).grid(row=0, column=0, columnspan=2, pady=(0, 10))

        self.cmb_vendedor = ttk.Combobox(container, values=self.vendedores, state="readonly")
        self.cmb_vendedor.grid(row=1, column=0, columnspan=2, pady=10)

        ttk.Button(container, text="Avançar", command=self.validar_vendedor).grid(row=2, column=1, padx=5, pady=10)


    def validar_vendedor(self):
        if not self.cmb_vendedor.get():
            messagebox.showerror("Erro", "Selecione um vendedor para continuar.")
            return
        self.vendedor_selecionado = self.cmb_vendedor.get()
        self.tela_cadastro_cliente()

    def tela_cadastro_cliente(self):
        self.limpar_frame()
        self.frame_atual = ttk.Frame(self.janela)
        self.frame_atual.pack(padx=20, pady=20)

        ttk.Label(self.frame_atual, text="Cadastro do Cliente", font=("Arial", 16)).grid(row=0, column=0, columnspan=2, pady=10)

        self.label_cpf = ttk.Label(self.frame_atual, text="CPF:")
        self.label_cpf.grid(row=1, column=0, padx=(0, 10), pady=5, sticky="e")
        self.entry_cpf = ttk.Entry(self.frame_atual)
        self.entry_cpf.grid(row=1, column=1, pady=5, sticky="w")
        self.entry_cpf.bind("<FocusOut>", self.validar_campos_cliente)

        self.label_nome = ttk.Label(self.frame_atual, text="Nome:")
        self.label_nome.grid(row=2, column=0, padx=(0, 10), pady=5, sticky="e")
        self.entry_nome = ttk.Entry(self.frame_atual)
        self.entry_nome.grid(row=2, column=1, pady=5, sticky="w")

        self.label_telefone = ttk.Label(self.frame_atual, text="Telefone:")
        self.label_telefone.grid(row=3, column=0, padx=(0, 10), pady=5, sticky="e")
        self.entry_telefone = ttk.Entry(self.frame_atual)
        self.entry_telefone.grid(row=3, column=1, pady=5, sticky="w")

        self.label_nascimento = ttk.Label(self.frame_atual, text="Data de Nascimento:")
        self.label_nascimento.grid(row=4, column=0, padx=(0, 10), pady=5, sticky="e")
        self.entry_nascimento = ttk.Entry(self.frame_atual)
        self.entry_nascimento.grid(row=4, column=1, pady=5, sticky="w")

        btn_voltar = ttk.Button(self.frame_atual, text="Voltar", command=self.tela_selecao_vendedor)
        btn_voltar.grid(row=5, column=0, pady=10)

        btn_continuar = ttk.Button(self.frame_atual, text="Continuar", command=self.verificar_dados_cliente)
        btn_continuar.grid(row=5, column=1, pady=10)


    def validar_cpf(self, cpf):
        cpf = re.sub(r'\D', '', cpf)
        if len(cpf) != 11 or cpf == cpf[0] * 11:
            return False
        soma1 = sum(int(cpf[i]) * (10 - i) for i in range(9))
        dig1 = (soma1 * 10 % 11) % 10
        soma2 = sum(int(cpf[i]) * (11 - i) for i in range(10))
        dig2 = (soma2 * 10 % 11) % 10
        return cpf[-2:] == f"{dig1}{dig2}"

    def validar_campos_cliente(self, event=None):
        cpf = self.entry_cpf.get().strip()
        nome = self.entry_nome.get().strip()
        tel = self.entry_telefone.get().strip()
        nasc = self.entry_nascimento.get().strip()

        if any([cpf, nome, tel, nasc]):
            if not cpf or not self.validar_cpf(cpf):
                messagebox.showerror("Erro", "CPF inválido.")
                self.entry_cpf.focus_set()
                return False
            if not nome:
                messagebox.showerror("Erro", "Insira o nome.")
                self.entry_nome.focus_set()
                return False
        return True

    def verificar_dados_cliente(self):
        if not self.validar_campos_cliente():
            return
        self.dados_cliente = {
            "cpf": self.entry_cpf.get(),
            "nome": self.entry_nome.get(),
            "telefone": self.entry_telefone.get(),
            "nascimento": self.entry_nascimento.get()
        }
        self.tela_venda()

    def tela_venda(self):
        self.limpar_frame()
        self.frame_atual = ttk.Frame(self.janela)
        self.frame_atual.pack(fill=BOTH, expand=True)

        container_esquerda = ttk.Frame(self.frame_atual)
        container_direita = ttk.Frame(self.frame_atual)
        container_esquerda.pack(side=LEFT, fill=BOTH, expand=True, padx=10, pady=10)
        container_direita.pack(side=RIGHT, fill=BOTH, expand=True, padx=10, pady=10)

        ttk.Label(container_esquerda, text="Adicionar Produto").pack()
        self.entry_produto = ttk.Entry(container_esquerda)
        self.entry_produto.pack()
        self.entry_produto.insert(0, "Produto")

        # Frame para os botões lado a lado
        botoes_frame = ttk.Frame(container_esquerda)
        botoes_frame.pack(pady=5)

        self.btn_adicionar = ttk.Button(botoes_frame, text="Adicionar Produto", command=self.adicionar_produto)
        self.btn_adicionar.pack(side="left", padx=5)

        self.btn_remover = ttk.Button(botoes_frame, text="Remover Produto", command=self.remover_produto)
        self.btn_remover.pack(side="left", padx=5)

        self.lista = tk.Listbox(container_esquerda, width=40)
        self.lista.pack(pady=10)

        ttk.Label(container_esquerda, text="Total da Compra:").pack()
        self.total_label = ttk.Label(container_esquerda, text="R$ 0.00")
        self.total_label.pack()

        ttk.Label(container_esquerda, text="Valor Restante:").pack()
        self.valor_editavel = ttk.Entry(container_esquerda)
        self.valor_editavel.insert(0, "0.00")
        self.valor_editavel.pack()

        ttk.Label(container_direita, text="Forma de Pagamento").pack(pady=10)

        ttk.Button(container_direita, text="Dinheiro", command=self.pagamento_dinheiro).pack(pady=5)
        ttk.Button(container_direita, text="Débito", command=self.pagamento_debito).pack(pady=5)
        ttk.Button(container_direita, text="Crédito", command=self.pagamento_credito).pack(pady=5)
        ttk.Button(container_direita, text="Pix", command=self.pagamento_pix).pack(pady=5)

        ttk.Button(container_direita, text="Limpar Pagamentos", command=self.limpar_pagamentos).pack(pady=10)

        self.pagamentos_label = ttk.Label(container_direita, text="Pagamentos:")
        self.pagamentos_label.pack(pady=10)

        self.btn_finalizar = ttk.Button(container_direita, text="Finalizar Venda", command=self.finalizar_venda)
        self.btn_finalizar.pack(pady=20)

        ttk.Button(container_direita, text="Voltar", command=self.tela_cadastro_cliente).pack()

    def atualizar_total(self):
        self.total_label.config(text=f"R$ {self.total_compra:.2f}")
        self.valor_restante = self.total_compra
        self.valor_editavel.delete(0, tk.END)
        self.valor_editavel.insert(0, f"{self.valor_restante:.2f}")

    def adicionar_produto(self):
        produto = self.entry_produto.get()
        if produto:
            self.lista.insert(tk.END, produto)
            self.total_compra += 10
            self.atualizar_total()
    
    def remover_produto(self):
        selecionado = self.lista.curselection()
        if selecionado:
            self.lista.delete(selecionado[0])
            self.total_compra -= 10
            self.atualizar_total()
            self.limpar_pagamentos()


    def obter_valor_restante(self):
        try:
            return float(self.valor_editavel.get())
        except ValueError:
            return 0.0

    def registrar_pagamento(self, forma, valor):
        self.pagamentos.append((forma, valor))
        self.exibir_pagamentos()
        
        self.valor_restante -= valor
        self.valor_restante = max(self.valor_restante, 0.0)

        self.valor_editavel.delete(0, tk.END)
        self.valor_editavel.insert(0, f"{self.valor_restante:.2f}")


    def exibir_pagamentos(self):
        texto = "Pagamentos:\n"
        for forma, valor in self.pagamentos:
            texto += f"{forma}: R$ {valor:.2f}\n"
        self.pagamentos_label.config(text=texto)

    def limpar_pagamentos(self):
        self.pagamentos = []
        self.valor_restante = self.total_compra
        self.valor_editavel.delete(0, tk.END)
        self.valor_editavel.insert(0, f"{self.valor_restante:.2f}")
        self.exibir_pagamentos()


    def pagamento_dinheiro(self):
        valor = self.obter_valor_restante()
        if valor > 0:
            self.registrar_pagamento("Dinheiro", valor)

    def pagamento_debito(self):
        top = tk.Toplevel(self.janela)
        top.title("Débito")
        ttk.Label(top, text="Selecione a bandeira:").pack(pady=5)
        cmb = ttk.Combobox(top, values=self.bandeiras, state="readonly")
        cmb.pack(pady=5)

        def confirmar():
            bandeira = cmb.get()
            if bandeira:
                valor = self.obter_valor_restante()
                if valor > 0:
                    self.registrar_pagamento(f"Débito ({bandeira})", valor)
                    top.destroy()

        ttk.Button(top, text="Confirmar", command=confirmar).pack(pady=10)

    def pagamento_credito(self):
        top = tk.Toplevel(self.janela)
        top.title("Crédito")
        ttk.Label(top, text="Selecione a bandeira:").pack(pady=5)
        cmb = ttk.Combobox(top, values=self.bandeiras, state="readonly")
        cmb.pack(pady=5)

        ttk.Label(top, text="Número de parcelas (1 a 6):").pack(pady=5)
        spin = ttk.Spinbox(top, from_=1, to=6)
        spin.pack(pady=5)

        def confirmar():
            bandeira = cmb.get()
            parcelas = spin.get()
            if bandeira and parcelas:
                valor = self.obter_valor_restante()
                if valor > 0:
                    self.registrar_pagamento(f"Crédito {parcelas}x ({bandeira})", valor)
                    top.destroy()

        ttk.Button(top, text="Confirmar", command=confirmar).pack(pady=10)

    def pagamento_pix(self):
        valor = self.obter_valor_restante()
        if valor > 0:
            self.registrar_pagamento("Pix", valor)

    def finalizar_venda(self):
        if self.total_compra <= 0 or self.lista.size() == 0:
            messagebox.showwarning("Venda inválida", "Nenhum produto adicionado.")
            return

        if self.obter_valor_restante() > 0:
            messagebox.showerror("Erro", "Ainda há valor pendente de pagamento.")
            return

        self.itens_venda = self.lista.get(0, tk.END)
        
        print("Venda registrada:", {
            "itens": self.itens_venda,
            "total": self.total_compra,
            "pagamentos": self.pagamentos
        })
        
        self.tela_resumo_venda()


    def tela_resumo_venda(self):
        self.limpar_frame()
        self.frame_atual = ttk.Frame(self.janela)
        self.frame_atual.pack(padx=20, pady=20, fill=BOTH, expand=True)

        ttk.Label(self.frame_atual, text="Resumo da Venda", font=("Arial", 16)).pack(pady=10)

        ttk.Label(self.frame_atual, text=f"Vendedor: {self.vendedor_selecionado}").pack(pady=2)
        ttk.Label(self.frame_atual, text=f"Cliente: {self.dados_cliente.get('nome', '---')}").pack(pady=2)
        ttk.Label(self.frame_atual, text=f"CPF: {self.dados_cliente.get('cpf', '---')}").pack(pady=2)

        ttk.Label(self.frame_atual, text="Produtos:").pack(pady=5)
        produtos_list = tk.Listbox(self.frame_atual, height=5)
        produtos_list.pack()
        for p in self.itens_venda:
            produtos_list.insert(tk.END, p)

        ttk.Label(self.frame_atual, text="Pagamentos:").pack(pady=5)
        pagamentos_list = tk.Listbox(self.frame_atual, height=5)
        pagamentos_list.pack()
        for forma, valor in self.pagamentos:
            pagamentos_list.insert(tk.END, f"{forma}: R$ {valor:.2f}")

        ttk.Label(self.frame_atual, text=f"Total Pago: R$ {self.total_compra:.2f}", font=("Arial", 12, "bold")).pack(pady=10)

        ttk.Button(self.frame_atual, text="Nova Venda", command=self.tela_selecao_vendedor).pack(pady=10)