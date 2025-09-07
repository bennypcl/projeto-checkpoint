import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

class TelaRelatorioVendas:
    def __init__(self, master, lista_de_vendas_global):
        self.master = master
        self.lista_de_vendas_global = lista_de_vendas_global # Guarda a referência
        self.janela_relatorio = None

    def mostrar_janela(self):
        """Cria e exibe a janela de relatório de vendas."""
        if self.janela_relatorio and tk.Toplevel.winfo_exists(self.janela_relatorio):
            self.janela_relatorio.lift()
            # Adicionado para recarregar os dados caso a janela seja reaberta
            self._filtrar_vendas() 
            return
        
        self.janela_relatorio = tk.Toplevel(self.master)
        self.janela_relatorio.title("Relatório de Vendas")
        self.janela_relatorio.state('zoomed')

        # --- Frame Principal ---
        frame_principal = ttk.Frame(self.janela_relatorio, padding=10)
        frame_principal.pack(fill=BOTH, expand=True)
        frame_principal.rowconfigure(1, weight=1)
        frame_principal.columnconfigure(0, weight=1)

        # --- Filtros (Topo) ---
        frame_filtros = ttk.Frame(frame_principal)
        frame_filtros.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        ttk.Label(frame_filtros, text="Visualizar:", font="-weight bold").pack(side=LEFT, padx=(0, 5))
        
        #Pega a lista de vendedores que fizeram vendas DA LISTA REAL
        if self.lista_de_vendas_global:
            vendedores_com_venda = sorted(list(set(v['vendedor'] for v in self.lista_de_vendas_global)))
            opcoes_filtro = ["Mostrar Tudo"] + vendedores_com_venda
        else:
            opcoes_filtro = ["Mostrar Tudo"]
        
        self.cmb_filtro = ttk.Combobox(frame_filtros, values=opcoes_filtro, state="readonly")
        self.cmb_filtro.pack(side=LEFT)
        self.cmb_filtro.set("Mostrar Tudo")
        self.cmb_filtro.bind("<<ComboboxSelected>>", self._filtrar_vendas)

        # --- Área Rolável para os Cards (com lógica de responsividade) ---
        canvas = tk.Canvas(frame_principal, highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame_principal, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.columnconfigure(0, weight=1)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas_frame_id = canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_frame_id, width=e.width))
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.grid(row=1, column=0, sticky="nsew")
        scrollbar.grid(row=1, column=1, sticky="ns")

        # Popula o relatório com os dados da lista real
        self._popular_relatorio(self.lista_de_vendas_global)

    def _carregar_vendas(self):
        """Preenche o Treeview principal com os dados de vendas REAIS."""
        # Limpa o treeview antes de carregar
        for i in self.tvw_vendas.get_children():
            self.tvw_vendas.delete(i)
            
        total_arrecadado = 0
        # USA A LISTA GLOBAL
        for venda in self.lista_de_vendas_global:
            valor_formatado = f"R$ {venda['total']:.2f}"
            
            self.tvw_vendas.insert('', END, iid=venda['id'], values=(
                venda['id'],
                venda['data'],
                venda['vendedor'],
                venda['cliente'].get('nome', 'N/A'), # Pega o nome do dicionário do cliente
                valor_formatado
            ))
            total_arrecadado += venda['total']
        
        self.lbl_total_vendas.config(text=f"Total de Vendas: {len(self.lista_de_vendas_global)}")
        self.lbl_valor_arrecadado.config(text=f"Valor Arrecadado: R$ {total_arrecadado:.2f}")

    def _filtrar_vendas(self, event=None):
        """Limpa e repopula o relatório com base no filtro selecionado."""
        selecao = self.cmb_filtro.get()
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if selecao == "Mostrar Tudo":
            dados_filtrados = self.lista_de_vendas_global
        else:
            # USA A LISTA GLOBAL
            dados_filtrados = [v for v in self.lista_de_vendas_global if v['vendedor'] == selecao]
        
        self._popular_relatorio(dados_filtrados)

    def _popular_relatorio(self, dados_das_vendas):
        """Cria e exibe os 'cards' de venda na área rolável."""
        for i, venda in enumerate(dados_das_vendas):
            card = ttk.LabelFrame(self.scrollable_frame, text=f" Venda por: {venda['vendedor']} ", padding=15)
            card.grid(row=i, column=0, padx=10, pady=10, sticky="ew")

            card.columnconfigure(1, weight=1)
            card.columnconfigure(2, weight=1)

            cliente = venda['cliente']
            texto_cliente = (
                f"Cliente: {cliente['nome']}\n"
                f"CPF: {cliente['cpf']}\n"
                f"Telefone: {cliente['telefone']}\n"
                f"Nascimento: {cliente['nascimento']}"
            )
            texto_produtos = "\n".join(venda['produtos'])
            texto_pagamentos = "\n".join([f"- {forma}: R$ {valor:.2f}" for forma, valor in venda['pagamentos']])

            # Aumentando o padx para dar mais espaço interno
            ttk.Label(card, text=texto_cliente, justify=LEFT).grid(row=0, column=0, sticky="nw", rowspan=2, padx=(0,20))
            ttk.Label(card, text="Produtos:", font="-weight bold").grid(row=0, column=1, sticky="nw")
            ttk.Label(card, text=texto_produtos, justify=LEFT).grid(row=1, column=1, sticky="nw")
            
            ttk.Label(card, text="Pagamento:", font="-weight bold").grid(row=0, column=2, sticky="nw")
            ttk.Label(card, text=texto_pagamentos, justify=LEFT).grid(row=1, column=2, sticky="nw")

            ttk.Separator(card, orient=HORIZONTAL).grid(row=2, column=0, columnspan=3, sticky="ew", pady=10)
            ttk.Label(card, text=f"TOTAL DA COMPRA: R$ {venda['total']:.2f}", font="-weight bold").grid(row=3, column=2, sticky="e")