import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox, simpledialog
import re
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from datetime import datetime
from reportlab.lib.units import cm

#scrollbar || aumentar tamanho da tela

#colocar os botões de voltar/cancelar
#tirar o "Vendedor: " (deixar só o nome)


class TelaPontoVenda:
    def __init__(self, master):
        self.master = master # Recebe a janela principal como master
        self.janela_pdv = None # Janela Toplevel para o PDV
        self.vendedor_selecionado = None
        self.dados_cliente = {}
        self.produtos = []
        self.total_compra = 0.0
        self.valor_restante = 0.0
        self.pagamentos = []
        self.vendedores = ["Andressa", "Nízia", "Vitória"]
        self.bandeiras = ["Visa", "MasterCard", "Elo", "Amex"]

        self.frame_atual = None

        # --- Variáveis com Trace para Formatação Automática ---
        self._is_formatting = False # Variável de controle para evitar loops
        self._nome_trace_set = False # Controle para garantir que o trace do nome seja criado só uma vez
        self._produto_trace_set = False # Controle para garantir que o trace do produto seja criado só uma vez
        
        # Apenas criamos as StringVars aqui
        self.cpf_var = tk.StringVar()
        self.cpf_var.trace_add('write', self.formatar_cpf)

        self.telefone_var = tk.StringVar()
        self.telefone_var.trace_add('write', self.formatar_telefone)
        
        self.nome_var = tk.StringVar()
        self.produto_var = tk.StringVar()

    def limpar_frame(self):
        if self.frame_atual:
            self.frame_atual.destroy()

    def iniciar_pdv(self):
        """Cria a janela Toplevel para o ponto de venda e inicia o fluxo."""
        if self.janela_pdv is None or not tk.Toplevel.winfo_exists(self.janela_pdv):
            self.janela_pdv = tk.Toplevel(self.master)
            self.janela_pdv.title("Ponto de Venda")
            self.janela_pdv.state('zoomed')
            self.tela_selecao_vendedor()
        else:
            self.janela_pdv.lift() # Se já existir, traz para frente

    def tela_selecao_vendedor(self):
        self.vendedor_selecionado = None
        self.dados_cliente = {}
        self.produtos = []
        self.total_compra = 0.0
        self.valor_restante = 0.0
        self.pagamentos = []

        if hasattr(self, 'cpf_var'):
            self.cpf_var.set("")
        if hasattr(self, 'nome_var'):
            self.nome_var.set("")
        if hasattr(self, 'telefone_var'):
            self.telefone_var.set("")

        self.limpar_frame()
        self.frame_atual = ttk.Frame(self.janela_pdv) # Usar self.janela_pdv
        self.frame_atual.pack(fill="both", expand=True)

        # Container central dentro do frame
        container = ttk.Frame(self.frame_atual)
        container.grid(row=0, column=0, padx=50, pady=50)
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

    def _formatar_para_maiusculo(self, string_var, entry_widget):
        # Se a função já estiver em execução, não faz nada (evita loop infinito)
        if self._is_formatting:
            return

        self._is_formatting = True  # Avisa que a formatação começou
        
        texto = string_var.get()
        texto_maiusculo = texto.upper()
        string_var.set(texto_maiusculo)
        
        # Move o cursor para o final
        entry_widget.after(1, lambda: entry_widget.icursor(len(texto_maiusculo)))

        self._is_formatting = False # Avisa que a formatação terminou

    def formatar_cpf(self, *args):
        texto = self.cpf_var.get()
        numeros = "".join(filter(str.isdigit, texto))
        numeros = numeros[:11]
        
        formatado = ""
        if len(numeros) > 9:
            formatado = f"{numeros[:3]}.{numeros[3:6]}.{numeros[6:9]}-{numeros[9:]}"
        elif len(numeros) > 6:
            formatado = f"{numeros[:3]}.{numeros[3:6]}.{numeros[6:]}"
        elif len(numeros) > 3:
            formatado = f"{numeros[:3]}.{numeros[3:]}"
        else:
            formatado = numeros
            
        callback_name = self.cpf_var.trace_info()[0][1]
        self.cpf_var.trace_remove('write', callback_name)
        self.cpf_var.set(formatado)
        self.cpf_var.trace_add('write', self.formatar_cpf)
        self.entry_cpf.after(1, lambda: self.entry_cpf.icursor(len(formatado))) #cursor sempre no final

    def formatar_telefone(self, *args):
        texto = self.telefone_var.get()
        numeros = "".join(filter(str.isdigit, texto))
        numeros = numeros[:11]
        
        formatado = ""
        if len(numeros) > 10:
            formatado = f"({numeros[:2]}) {numeros[2:7]}-{numeros[7:]}"
        elif len(numeros) > 6:
            # Corrigindo uma pequena falha na máscara para números com 10 dígitos
            formatado = f"({numeros[:2]}) {numeros[2:6]}-{numeros[6:]}" 
        elif len(numeros) > 2:
            formatado = f"({numeros[:2]}) {numeros[2:]}"
        elif len(numeros) > 0:
            formatado = f"({numeros[:2]}"
        else:
            formatado = numeros

        callback_name = self.telefone_var.trace_info()[0][1]
        self.telefone_var.trace_remove('write', callback_name)
        self.telefone_var.set(formatado)
        self.telefone_var.trace_add('write', self.formatar_telefone)
        self.entry_telefone.after(1, lambda: self.entry_telefone.icursor(len(formatado)))

    def tela_cadastro_cliente(self):
        self.limpar_frame()
        
        self.frame_atual = ttk.Frame(self.janela_pdv)
        self.frame_atual.pack(fill="both", expand=True)

        self.frame_atual.columnconfigure(0, weight=1)
        self.frame_atual.rowconfigure(0, weight=1)

        container = ttk.Frame(self.frame_atual)
        container.grid(row=0, column=0)

        ttk.Label(container, text=f"Vendedor: {self.vendedor_selecionado}", font=("Arial", 10, "italic")).grid(
            row=0, column=0, columnspan=2, pady=(0, 20), sticky="w")

        ttk.Label(container, text="Cadastro do Cliente", font=("Arial", 16, "bold")).grid(
            row=1, column=0, columnspan=2, pady=(0, 15))

        # Campos do Formulário CONECTADOS às StringVars
        ttk.Label(container, text="CPF:").grid(row=2, column=0, padx=5, pady=8, sticky="e")
        # Conecta o campo de CPF à self.cpf_var
        self.entry_cpf = ttk.Entry(container, width=30, textvariable=self.cpf_var)
        self.entry_cpf.grid(row=2, column=1, padx=5, pady=8)
        self.entry_cpf.focus_set()

        ttk.Label(container, text="Nome:").grid(row=3, column=0, padx=5, pady=8, sticky="e")
        # Conecta o campo de Nome à self.nome_var
        self.entry_nome = ttk.Entry(container, width=30, textvariable=self.nome_var)
        self.entry_nome.grid(row=3, column=1, padx=5, pady=8)

        # Ativa o trace para o nome do cliente APENAS UMA VEZ
        if not self._nome_trace_set:
            self.nome_var.trace_add('write', 
                lambda *args: self._formatar_para_maiusculo(self.nome_var, self.entry_nome))
            self._nome_trace_set = True

        ttk.Label(container, text="Telefone:").grid(row=4, column=0, padx=5, pady=8, sticky="e")
        # Conecta o campo de Telefone à self.telefone_var
        self.entry_telefone = ttk.Entry(container, width=30, textvariable=self.telefone_var)
        self.entry_telefone.grid(row=4, column=1, padx=5, pady=8)

        # Campos de Data de Nascimento com Spinbox
        # (Não precisam de validação extra, pois já são numéricos por natureza)
        ttk.Label(container, text="Data de Nascimento:").grid(row=5, column=0, padx=5, pady=8, sticky="e")
        
        frame_nascimento = ttk.Frame(container)
        frame_nascimento.grid(row=5, column=1, padx=5, pady=8, sticky="w")
        
        self.spin_dia = ttk.Spinbox(frame_nascimento, from_=1, to=31, width=4)
        self.spin_dia.pack(side="left", padx=(0, 5))
        
        self.spin_mes = ttk.Spinbox(frame_nascimento, from_=1, to=12, width=4)
        self.spin_mes.pack(side="left", padx=5)

        self.spin_ano = ttk.Spinbox(frame_nascimento, from_=1920, to=2024, width=6)
        self.spin_ano.pack(side="left")

        # Frame para os botões de ação
        frame_botoes = ttk.Frame(container)
        frame_botoes.grid(row=6, column=0, columnspan=2, pady=(20, 0))

        btn_voltar = ttk.Button(frame_botoes, text="Voltar", command=self.tela_selecao_vendedor)
        btn_voltar.pack(side="left", padx=10)

        btn_continuar = ttk.Button(frame_botoes, text="Continuar", command=self.verificar_dados_cliente)
        btn_continuar.pack(side="left", padx=10)

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

        if any([cpf, nome, tel]):
            if not cpf or not self.validar_cpf(cpf):
                messagebox.showerror("Erro", "CPF inválido.", parent=self.janela_pdv)
                self.entry_cpf.focus_set()
                return False
            if not nome:
                messagebox.showerror("Erro", "Insira o nome.", parent=self.janela_pdv)
                self.entry_nome.focus_set()
                return False
        return True

    def verificar_dados_cliente(self):
        if not self.validar_campos_cliente():
            return
        
        # Pega os valores dos 3 Spinboxes de data
        dia = self.spin_dia.get()
        mes = self.spin_mes.get()
        ano = self.spin_ano.get()
        
        # Verifica se a data foi preenchida antes de formatar
        data_nascimento_formatada = ""
        if dia and mes and ano:
            data_nascimento_formatada = f"{dia}/{mes}/{ano}"

        self.dados_cliente = {
            "cpf": self.entry_cpf.get(),
            "nome": self.entry_nome.get(),
            "telefone": self.entry_telefone.get(),
            "nascimento": data_nascimento_formatada
        }
        self.tela_venda()

    def tela_venda(self):
        self.limpar_frame()
        self.frame_atual = ttk.Frame(self.janela_pdv)
        self.frame_atual.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # --- ESTRUTURA PRINCIPAL: DOIS PAINÉIS (Esquerda e Direita) ---
        self.frame_atual.columnconfigure(0, weight=2) # Painel esquerdo (produtos) será maior
        self.frame_atual.columnconfigure(1, weight=1) # Painel direito (pagamentos) menor
        self.frame_atual.rowconfigure(0, weight=1)    # Linha única que se expande verticalmente

        container_esquerda = ttk.Frame(self.frame_atual)
        container_direita = ttk.Frame(self.frame_atual)
        container_esquerda.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        container_direita.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        # --- PAINEL ESQUERDO: PRODUTOS E TOTAL ---
        container_esquerda.rowconfigure(1, weight=1) # Faz a lista de produtos expandir
        container_esquerda.columnconfigure(0, weight=1)

        # Seção de Adicionar Produto
        frame_add_produto = ttk.Frame(container_esquerda)
        frame_add_produto.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        frame_add_produto.columnconfigure(1, weight=1)
        
        ttk.Label(frame_add_produto, text="Produto:").grid(row=0, column=0, padx=(0, 5))
        self.entry_produto = ttk.Entry(frame_add_produto, textvariable=self.produto_var)
        self.entry_produto.grid(row=0, column=1, sticky="ew")
        self.entry_produto.focus_set()
        self.entry_produto.bind("<Return>", self.adicionar_produto_event)

        # Ativa o trace para o nome do produto APENAS UMA VEZ
        if not self._produto_trace_set:
            self.produto_var.trace_add('write', 
                lambda *args: self._formatar_para_maiusculo(self.produto_var, self.entry_produto))
            self._produto_trace_set = True

        self.btn_adicionar = ttk.Button(frame_add_produto, text="Adicionar", command=self.adicionar_produto)
        self.btn_adicionar.grid(row=0, column=2, padx=(5, 0))

        # Seção da Lista de Produtos (usando Treeview para um visual melhor)
        frame_lista_produtos = ttk.Frame(container_esquerda)
        frame_lista_produtos.grid(row=1, column=0, sticky="nsew")
        frame_lista_produtos.rowconfigure(0, weight=1)
        frame_lista_produtos.columnconfigure(0, weight=1)

        # ADICIONAMOS 'codigo' e 'tamanho' mas vamos exibi-los
        colunas = ('produto', 'codigo', 'tamanho', 'preco')
        self.tvw_produtos = ttk.Treeview(frame_lista_produtos, columns=colunas, show='headings')
        self.tvw_produtos.heading('produto', text='Produto')
        self.tvw_produtos.heading('codigo', text='Código')
        self.tvw_produtos.heading('tamanho', text='Tamanho')
        self.tvw_produtos.heading('preco', text='Preço')
        self.tvw_produtos.column('preco', width=80, anchor="e")
        self.tvw_produtos.grid(row=0, column=0, sticky="nsew")
        
        # Scrollbar para a lista de produtos
        scrollbar = ttk.Scrollbar(frame_lista_produtos, orient="vertical", command=self.tvw_produtos.yview)
        self.tvw_produtos.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.btn_remover = ttk.Button(container_esquerda, text="Remover Produto Selecionado", command=self.remover_produto)
        self.btn_remover.grid(row=2, column=0, sticky="ew", pady=(10, 0))

        # Seção de Totais
        frame_totais = ttk.Frame(container_esquerda)
        frame_totais.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        frame_totais.columnconfigure(1, weight=1)
        
        ttk.Label(frame_totais, text="Total da Compra:", font=("Arial", 14, "bold")).grid(row=0, column=0, sticky="w")
        self.total_label = ttk.Label(frame_totais, text="R$ 0.00", font=("Arial", 14, "bold"))
        self.total_label.grid(row=0, column=1, sticky="e")

        # --- PAINEL DIREITO: PAGAMENTOS E AÇÕES (VERSÃO AJUSTADA) ---
        container_direita.columnconfigure(0, weight=1)
        container_direita.rowconfigure(2, weight=1) # Faz o resumo de pagamentos expandir

        # Seção de Entrada de Valor e Formas de Pagamento
        ttk.Label(container_direita, text="Valor a Pagar:", font=("Arial", 12)).grid(row=0, column=0, sticky="w", pady=(0,5))
        self.valor_editavel = ttk.Entry(container_direita, font=("Arial", 14), justify="right")
        self.valor_editavel.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        self.valor_editavel.insert(0, "0.00")
        
        frame_formas_pagamento = ttk.Frame(container_direita)
        frame_formas_pagamento.grid(row=2, column=0, sticky="nsew")
        frame_formas_pagamento.columnconfigure((0, 1), weight=1)

        ttk.Button(frame_formas_pagamento, text="Dinheiro", command=self.pagamento_dinheiro).grid(row=0, column=0, sticky="ew", padx=2, pady=2)
        ttk.Button(frame_formas_pagamento, text="Débito", command=self.pagamento_debito).grid(row=0, column=1, sticky="ew", padx=2, pady=2)
        ttk.Button(frame_formas_pagamento, text="Crédito", command=self.pagamento_credito).grid(row=1, column=0, sticky="ew", padx=2, pady=2)
        ttk.Button(frame_formas_pagamento, text="Pix", command=self.pagamento_pix).grid(row=1, column=1, sticky="ew", padx=2, pady=2)

        # Seção de Resumo de Pagamentos
        frame_resumo_pagamentos = ttk.Frame(container_direita)
        frame_resumo_pagamentos.grid(row=3, column=0, sticky="ew", pady=(10,5))
        frame_resumo_pagamentos.columnconfigure(0, weight=1)
        
        ttk.Label(frame_resumo_pagamentos, text="Pagamentos Realizados:").grid(row=0, column=0, sticky="w")
        self.lista_pagamentos = tk.Listbox(frame_resumo_pagamentos, height=4)
        self.lista_pagamentos.grid(row=1, column=0, sticky="ew")

        # 1: Botão "Limpar Pagamentos" movido para baixo da lista
        ttk.Button(frame_resumo_pagamentos, text="Limpar Pagamentos", command=self.limpar_pagamentos, bootstyle=(WARNING, OUTLINE)).grid(row=2, column=0, sticky="ew", pady=(5,0))
        
        # 3: Cor do troco alterada para azul (bootstyle="info")
        self.label_troco = ttk.Label(frame_resumo_pagamentos, text="", bootstyle="info", font=("Arial", 12, "bold"))
        self.label_troco.grid(row=3, column=0, sticky="e", pady=(5,0))
        
        # Seção de Ações Finais
        frame_acoes = ttk.Frame(container_direita)
        frame_acoes.grid(row=4, column=0, sticky="ew", pady=(20, 0))
        # 2: Configura 2 colunas de mesmo peso para os botões lado a lado
        frame_acoes.columnconfigure((0, 1), weight=1)

        ttk.Button(frame_acoes, text="Voltar (Cancelar Venda)", command=self.tela_selecao_vendedor, bootstyle=SECONDARY).grid(row=0, column=0, sticky="ew", padx=(0, 5), ipady=10)

        self.btn_finalizar = ttk.Button(frame_acoes, text="FINALIZAR VENDA", command=self.finalizar_venda)
        self.btn_finalizar.grid(row=0, column=1, sticky="ew", padx=(5, 0), ipady=10)

    def atualizar_total(self):
        self.total_label.config(text=f"R$ {self.total_compra:.2f}")
        self.valor_restante = self.total_compra
        self.valor_editavel.delete(0, tk.END)
        self.valor_editavel.insert(0, f"{self.valor_restante:.2f}")

    def adicionar_produto(self):
        produto_nome = self.entry_produto.get()
        if produto_nome:
            preco = 10.00 # Preço fixo para exemplo
            
            # SIMULAÇÃO de código e tamanho
            codigo_simulado = f"SKU-{len(self.tvw_produtos.get_children()) + 100}"
            tamanho_simulado = "M"

            # Inserimos os 4 valores no Treeview
            self.tvw_produtos.insert('', tk.END, values=(produto_nome, codigo_simulado, tamanho_simulado, f"{preco:.2f}"))
            
            self.total_compra += preco
            self.atualizar_total()
            self.entry_produto.delete(0, tk.END)
    
    def adicionar_produto_event(self, event=None):
        """Função chamada pelo evento da tecla Enter para evitar problemas com argumentos."""
        self.adicionar_produto()

    def remover_produto(self):
        selecionado = self.tvw_produtos.selection()
        if selecionado:
            item = self.tvw_produtos.item(selecionado[0])
            # O preço agora é o quarto item (índice 3)
            preco_str = item['values'][3] 
            preco = float(preco_str)
            
            self.total_compra -= preco
            self.tvw_produtos.delete(selecionado[0])
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
        self.lista_pagamentos.delete(0, tk.END) # Limpa a lista antes de adicionar
        texto_pagamentos = "Pagamentos:\n"
        for forma, valor in self.pagamentos:
            self.lista_pagamentos.insert(tk.END, f"{forma}: R$ {valor:.2f}")
        # A linha abaixo que atualizava o label foi removida pois agora usamos a Listbox
        # self.pagamentos_label.config(text=texto_pagamentos)

    def limpar_pagamentos(self):
        self.pagamentos = []
        self.valor_restante = self.total_compra
        self.valor_editavel.delete(0, tk.END)
        self.valor_editavel.insert(0, f"{self.valor_restante:.2f}")
        self.exibir_pagamentos()
        self.label_troco.config(text="")

    def calcular_troco(self, valor_pago, valor_restante):
        troco = valor_pago - valor_restante

        # Print de diagnóstico final para termos 100% de certeza do valor
        print(f">>> DEBUG: Dentro de calcular_troco. Valor do troco calculado: {troco}")

        if troco > 0:
            texto_troco = f"Troco: R$ {troco:.2f}"
            self.label_troco.config(text=texto_troco)
        else:
            self.label_troco.config(text="")
        
        # Comando para forçar a atualização visual da janela do PDV
        self.janela_pdv.update_idletasks()


    def pagamento_dinheiro(self):
        valor_str = self.valor_editavel.get()

        try:
            valor_pago = float(valor_str.replace(",", "."))
        except ValueError:
            messagebox.showerror("Erro", "Digite um valor numérico válido.", parent=self.janela_pdv)
            return

        if valor_pago <= 0:
            messagebox.showerror("Erro", "Digite um valor maior que zero.", parent=self.janela_pdv)
            return

        valor_restante = self.valor_restante

        if valor_pago >= valor_restante:
            self.calcular_troco(valor_pago, valor_restante)
            self.registrar_pagamento("Dinheiro", valor_restante)
        else:
            self.label_troco.config(text="")
            self.registrar_pagamento("Dinheiro", valor_pago)


    def pagamento_debito(self):
        # 1. Pega e valida o valor ANTES de abrir a nova janela
        valor_str = self.valor_editavel.get()
        try:
            valor_pago = float(valor_str.replace(",", "."))
        except ValueError:
            messagebox.showerror("Erro", "Valor de pagamento inválido.", parent=self.janela_pdv)
            return

        if valor_pago <= 0:
            messagebox.showerror("Erro", "O valor do pagamento deve ser maior que zero.", parent=self.janela_pdv)
            return
        if valor_pago > self.valor_restante:
            messagebox.showerror("Erro", f"O valor do pagamento (R$ {valor_pago:.2f}) não pode ser maior que o valor restante (R$ {self.valor_restante:.2f}).", parent=self.janela_pdv)
            return

        # 2. Abre a janela para selecionar a bandeira
        top = tk.Toplevel(self.janela_pdv)
        top.title("Débito")
        ttk.Label(top, text="Selecione a bandeira:").pack(pady=5)
        cmb = ttk.Combobox(top, values=self.bandeiras, state="readonly")
        cmb.pack(pady=5)

        def confirmar():
            bandeira = cmb.get()
            if bandeira:
                # 3. Usa o 'valor_pago' que foi validado anteriormente
                self.registrar_pagamento(f"Débito ({bandeira})", valor_pago)
                top.destroy()

        ttk.Button(top, text="Confirmar", command=confirmar).pack(pady=10)

    def pagamento_credito(self):
        # 1. Pega e valida o valor ANTES de abrir a nova janela
        valor_str = self.valor_editavel.get()
        try:
            valor_pago = float(valor_str.replace(",", "."))
        except ValueError:
            messagebox.showerror("Erro", "Valor de pagamento inválido.", parent=self.janela_pdv)
            return

        if valor_pago <= 0:
            messagebox.showerror("Erro", "O valor do pagamento deve ser maior que zero.", parent=self.janela_pdv)
            return
        if valor_pago > self.valor_restante:
            messagebox.showerror("Erro", f"O valor do pagamento (R$ {valor_pago:.2f}) não pode ser maior que o valor restante (R$ {self.valor_restante:.2f}).", parent=self.janela_pdv)
            return

        # 2. Abre a janela para selecionar bandeira e parcelas
        top = tk.Toplevel(self.janela_pdv)
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
                # 3. Usa o 'valor_pago' que foi validado anteriormente
                self.registrar_pagamento(f"Crédito {parcelas}x ({bandeira})", valor_pago)
                top.destroy()

        ttk.Button(top, text="Confirmar", command=confirmar).pack(pady=10)

    def pagamento_pix(self):
        # 1. Pega o valor do campo de texto, igual no pagamento_dinheiro
        valor_str = self.valor_editavel.get()
        try:
            valor_pago = float(valor_str.replace(",", "."))
        except ValueError:
            messagebox.showerror("Erro", "Valor de pagamento inválido.", parent=self.janela_pdv)
            return

        # 2. Validações importantes
        if valor_pago <= 0:
            messagebox.showerror("Erro", "O valor do pagamento deve ser maior que zero.", parent=self.janela_pdv)
            return
        # Impede que se pague via pix um valor maior que o devido
        if valor_pago > self.valor_restante:
            messagebox.showerror("Erro", f"O valor do pagamento (R$ {valor_pago:.2f}) não pode ser maior que o valor restante (R$ {self.valor_restante:.2f}).", parent=self.janela_pdv)
            return
        
        # 3. Registra o pagamento com o valor que foi digitado
        self.registrar_pagamento("Pix", valor_pago)

    def gerar_ticket_troca_pdf(self, item_para_troca, vendedor, data_compra):
        """Gera um PDF de Ticket de Troca para UM ÚNICO item."""
        
        nome_produto_safe = "".join([c for c in item_para_troca['nome'] if c.isalnum()]).strip() or "item"
        timestamp = datetime.now().strftime("%H%M%S")
        nome_arquivo = f"ticket_troca_{data_compra.replace('/', '-')}_{nome_produto_safe}_{timestamp}.pdf"

        try:
            largura_recibo = 7 * cm
            altura_recibo = 8 * cm
            c = canvas.Canvas(nome_arquivo, pagesize=(largura_recibo, altura_recibo))
            
            c.setFont("Helvetica-Bold", 12)
            c.drawCentredString(largura_recibo / 2.0, altura_recibo - 1*cm, "Ticket de Troca")

            c.setFont("Helvetica", 8)
            c.drawString(0.5*cm, altura_recibo - 2*cm, f"Data: {data_compra}")
            c.drawString(0.5*cm, altura_recibo - 2.5*cm, f"Vendedor: {vendedor}")

            c.line(0.5*cm, altura_recibo - 2.8*cm, largura_recibo - 0.5*cm, altura_recibo - 2.8*cm)

            posicao_y_atual = altura_recibo - 3.5*cm
            espaco_entre_linhas = 0.5*cm
            espaco_entre_blocos = 1*cm

            # Bloco do Produto (continua igual)
            c.setFont("Helvetica-Bold", 8)
            c.drawString(0.5*cm, posicao_y_atual, "Produto")
            posicao_y_atual -= espaco_entre_linhas
            c.setFont("Helvetica", 8)
            c.drawString(0.5*cm, posicao_y_atual, item_para_troca['nome'])
            posicao_y_atual -= espaco_entre_blocos

            # --- NOVO BLOCO COMBINADO DE CÓDIGO E TAMANHO ---
            # Cabeçalho na mesma linha
            c.setFont("Helvetica-Bold", 8)
            c.drawString(0.5*cm, posicao_y_atual, "Código")
            c.drawString(3.5*cm, posicao_y_atual, "Tamanho")
            posicao_y_atual -= espaco_entre_linhas

            # Valores na mesma linha, alinhados com o cabeçalho
            c.setFont("Helvetica", 8)
            c.drawString(0.5*cm, posicao_y_atual, item_para_troca['codigo'])
            c.drawString(3.5*cm, posicao_y_atual, item_para_troca['tamanho'])
            # --- FIM DO NOVO BLOCO ---

            c.setFont("Helvetica-Oblique", 7)
            c.drawCentredString(largura_recibo / 2.0, 0.5*cm, "Válido para trocas em até 30 dias da data da compra.")

            c.save()
            return True

        except Exception as e:
            print(f"ERRO ao gerar PDF para o item {item_para_troca['nome']}: {e}")
            return False

    def finalizar_venda(self):
        if self.total_compra <= 0 or not self.tvw_produtos.get_children():
            messagebox.showwarning("Venda inválida", "Nenhum produto adicionado.", parent=self.janela_pdv)
            return

        if self.valor_restante > 0:
            messagebox.showerror("Erro", "Ainda há valor pendente de pagamento.", parent=self.janela_pdv)
            return

        # Pega a data UMA VEZ antes do loop
        data_atual = datetime.now().strftime("%d/%m/%Y")
        
        itens_gerados_sucesso = 0
        total_itens = len(self.tvw_produtos.get_children())

        # Loop para gerar um PDF para cada item na lista
        for item_id in self.tvw_produtos.get_children():
            valores = self.tvw_produtos.item(item_id)['values']
            item_info = {
                'nome': valores[0],
                'codigo': valores[1],
                'tamanho': valores[2]
            }
            
            # Chama a função de gerar PDF para o item atual
            if self.gerar_ticket_troca_pdf(item_info, self.vendedor_selecionado, data_atual):
                itens_gerados_sucesso += 1

        # Mostra UMA ÚNICA mensagem de resumo no final
        if itens_gerados_sucesso == total_itens:
            messagebox.showinfo("Sucesso", f"{itens_gerados_sucesso} Ticket(s) de Troca gerados com sucesso!", parent=self.janela_pdv)
        else:
            messagebox.showwarning("Atenção", f"Venda finalizada, mas apenas {itens_gerados_sucesso} de {total_itens} Tickets de Troca foram gerados. Verifique o console para erros.", parent=self.janela_pdv)

        # Coleta os itens para a tela de resumo da venda (apenas nomes)
        self.itens_venda = []
        for item_id in self.tvw_produtos.get_children():
            self.itens_venda.append(self.tvw_produtos.item(item_id)['values'][0])
        
        print("Venda registrada:", {
            "itens": self.itens_venda,
            "total": self.total_compra,
            "pagamentos": self.pagamentos
        })

        self.tela_resumo_venda()

    def tela_resumo_venda(self):
        self.limpar_frame()
        self.frame_atual = ttk.Frame(self.janela_pdv) # Usar self.janela_pdv
        self.frame_atual.pack(padx=20, pady=20, fill=BOTH, expand=True)

        ttk.Label(self.frame_atual, text="Resumo da Venda", font=("Arial", 16)).pack(pady=10)

        ttk.Label(self.frame_atual, text=f"Vendedor: {self.vendedor_selecionado}").pack(pady=2, anchor="w")
        ttk.Label(self.frame_atual, text=f"Cliente: {self.dados_cliente.get('nome', '---')}").pack(pady=2, anchor="w")
        ttk.Label(self.frame_atual, text=f"CPF: {self.dados_cliente.get('cpf', '---')}").pack(pady=2, anchor="w")

        ttk.Label(self.frame_atual, text="Produtos:", font=("Arial", 12, "bold")).pack(pady=5, anchor="w")
        produtos_list = tk.Listbox(self.frame_atual, height=5)
        produtos_list.pack()
        for p in self.itens_venda:
            produtos_list.insert(tk.END, p)

        ttk.Label(self.frame_atual, text="Pagamentos:", font=("Arial", 12, "bold")).pack(pady=5, anchor="w")
        pagamentos_list = tk.Listbox(self.frame_atual, height=5)
        pagamentos_list.pack()
        for forma, valor in self.pagamentos:
            pagamentos_list.insert(tk.END, f"{forma}: R$ {valor:.2f}")

        ttk.Label(self.frame_atual, text=f"Total Pago: R$ {self.total_compra:.2f}", font=("Arial", 12, "bold")).pack(pady=10, anchor="w")

        ttk.Button(self.frame_atual, text="Nova Venda", command=self.tela_selecao_vendedor).pack(pady=10) # Para iniciar uma nova venda, abre outra janela de PDV ou reinicia a atual
        ttk.Button(self.frame_atual, text="Fechar PDV", command=self.janela_pdv.destroy).pack(pady=5) # Adicionado botão para fechar apenas o PDV