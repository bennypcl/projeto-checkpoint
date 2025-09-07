import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
from datetime import datetime

# Imports necessários para o novo gerador de PDF
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm

class TelaRelatorioVendas:
    def __init__(self, master, lista_de_vendas_global):
        self.master = master
        self.lista_de_vendas_global = lista_de_vendas_global
        self.janela_relatorio = None
    
    def mostrar_janela(self):
        """Cria e exibe a janela de relatório de vendas."""
        if self.janela_relatorio and tk.Toplevel.winfo_exists(self.janela_relatorio):
            self.janela_relatorio.lift()
            self._filtrar_vendas()
            return
        
        self.janela_relatorio = tk.Toplevel(self.master)
        self.janela_relatorio.title("Relatório de Vendas")
        self.janela_relatorio.state('zoomed')

        frame_principal = ttk.Frame(self.janela_relatorio, padding=10)
        frame_principal.pack(fill=BOTH, expand=True)
        frame_principal.rowconfigure(1, weight=1)
        frame_principal.columnconfigure(0, weight=1)

        # --- Filtros (Topo) ---
        frame_filtros = ttk.Frame(frame_principal)
        frame_filtros.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        ttk.Label(frame_filtros, text="Visualizar:", font="-weight bold").pack(side=LEFT, padx=(0, 5))
        
        if self.lista_de_vendas_global:
            vendedores_com_venda = sorted(list(set(v['vendedor'] for v in self.lista_de_vendas_global)))
            opcoes_filtro = ["Mostrar Tudo"] + vendedores_com_venda
        else:
            opcoes_filtro = ["Mostrar Tudo"]
        
        self.cmb_filtro = ttk.Combobox(frame_filtros, values=opcoes_filtro, state="readonly")
        self.cmb_filtro.pack(side=LEFT)
        self.cmb_filtro.set("Mostrar Tudo")
        self.cmb_filtro.bind("<<ComboboxSelected>>", self._filtrar_vendas)

        # --- NOVO: Botão para Gerar PDF Completo (Pedido 2) ---
        btn_pdf = ttk.Button(frame_filtros, text="Baixar PDF do Relatório", command=self.gerar_relatorio_completo_pdf, bootstyle=PRIMARY)
        btn_pdf.pack(side=RIGHT)

        # --- Área Rolável ---
        canvas = tk.Canvas(frame_principal, highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame_principal, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas, padding=10)

        # Definimos as colunas na grade principal com a nova coluna para Desconto
        self.scrollable_frame.columnconfigure(0, weight=3) # Cliente
        self.scrollable_frame.columnconfigure(1, weight=3) # Produtos
        self.scrollable_frame.columnconfigure(2, weight=2) # Pagamento
        self.scrollable_frame.columnconfigure(3, weight=2) # Desconto (NOVO)

        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas_frame_id = canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_frame_id, width=e.width))
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.grid(row=1, column=0, sticky="nsew")
        scrollbar.grid(row=1, column=1, sticky="ns")

        self._popular_relatorio(self.lista_de_vendas_global)

    def _popular_relatorio(self, dados_das_vendas):
        """Cria e exibe os dados da venda diretamente na grade principal para alinhamento perfeito."""
        
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        row_counter = 0
        for venda in dados_das_vendas:
            # --- Monta os blocos de texto ---
            cliente = venda.get('cliente', {})
            if not cliente or not cliente.get('cpf'):
                texto_cliente = "Cliente não identificado"
            else:
                info_list = [cliente.get('nome', 'N/A')]
                if cliente.get('cpf'): info_list.append(cliente.get('cpf'))
                if cliente.get('telefone'): info_list.append(cliente.get('telefone'))
                if cliente.get('nascimento'): info_list.append(cliente.get('nascimento'))
                texto_cliente = "\n".join(info_list)

            texto_produtos = "\n".join(venda['produtos'])
            texto_pagamentos = "\n".join([f"- {forma}: R$ {valor:.2f}" for forma, valor in venda['pagamentos']])
            
            # LÓGICA CONDICIONAL PARA O DESCONTO
            desconto_info = venda.get('desconto', '')
            if desconto_info:
                cabecalho_desconto = "Desconto"
                valor_desconto = desconto_info
            else:
                cabecalho_desconto = ""
                valor_desconto = ""

            # --- Adiciona os elementos na grade principal ---
            ttk.Label(self.scrollable_frame, text=f"Venda por: {venda['vendedor']}", font="-weight bold").grid(row=row_counter, column=0, columnspan=4, sticky="w", pady=(15, 5))
            row_counter += 1

            ttk.Label(self.scrollable_frame, text="Cliente", font="-weight bold").grid(row=row_counter, column=0, sticky="nw")
            ttk.Label(self.scrollable_frame, text="Produtos", font="-weight bold").grid(row=row_counter, column=1, sticky="nw")
            ttk.Label(self.scrollable_frame, text="Pagamento", font="-weight bold").grid(row=row_counter, column=2, sticky="nw")
            ttk.Label(self.scrollable_frame, text=cabecalho_desconto, font="-weight bold").grid(row=row_counter, column=3, sticky="nw")
            row_counter += 1

            ttk.Label(self.scrollable_frame, text=texto_cliente, justify=LEFT).grid(row=row_counter, column=0, sticky="nw", pady=(5,0), padx=(0,10))
            ttk.Label(self.scrollable_frame, text=texto_produtos, justify=LEFT).grid(row=row_counter, column=1, sticky="nw", pady=(5,0), padx=10)
            ttk.Label(self.scrollable_frame, text=texto_pagamentos, justify=LEFT).grid(row=row_counter, column=2, sticky="nw", pady=(5,0), padx=10)
            ttk.Label(self.scrollable_frame, text=valor_desconto, justify=LEFT).grid(row=row_counter, column=3, sticky="nw", pady=(5,0), padx=10)
            row_counter += 1

            ttk.Label(self.scrollable_frame, text=f"TOTAL DA COMPRA: R$ {venda['total']:.2f}", font="-weight bold").grid(row=row_counter, column=2, columnspan=2, sticky="e", pady=5)
            row_counter += 1

            ttk.Separator(self.scrollable_frame, orient=HORIZONTAL).grid(row=row_counter, column=0, columnspan=4, sticky="ew", pady=15)
            row_counter += 1

    def _filtrar_vendas(self, event=None):
        """Limpa e repopula o relatório com base no filtro selecionado."""
        # Esta função agora só chama _popular_relatorio, que já limpa o frame.
        selecao = self.cmb_filtro.get()
        if selecao == "Mostrar Tudo":
            dados_filtrados = self.lista_de_vendas_global
        else:
            dados_filtrados = [v for v in self.lista_de_vendas_global if v['vendedor'] == selecao]
        self._popular_relatorio(dados_filtrados)

    def gerar_relatorio_completo_pdf(self):
        """Gera um PDF A4 com todas as vendas visíveis no relatório."""
        selecao = self.cmb_filtro.get()
        if selecao == "Mostrar Tudo":
            dados_para_pdf = self.lista_de_vendas_global
            titulo_filtro = "Todas as Vendas"
        else:
            dados_para_pdf = [v for v in self.lista_de_vendas_global if v['vendedor'] == selecao]
            titulo_filtro = f"Vendas por: {selecao}"

        if not dados_para_pdf:
            messagebox.showwarning("Atenção", "Nenhuma venda para gerar no relatório.", parent=self.janela_relatorio)
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"relatorio_vendas_{timestamp}.pdf"

        try:
            doc = SimpleDocTemplate(nome_arquivo, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []

            # Título
            story.append(Paragraph("Relatório de Vendas", styles['h1']))
            story.append(Paragraph(f"Filtro Aplicado: {titulo_filtro}", styles['h3']))
            story.append(Spacer(1, 1*cm))

            for venda in dados_para_pdf:
                # Formata os dados para o PDF
                cliente = venda.get('cliente', {})
                if not cliente or not cliente.get('cpf'):
                    texto_cliente = "Cliente não identificado"
                else:
                    info_list = [f"<b>Cliente:</b> {cliente.get('nome', 'N/A')}"]
                    if cliente.get('cpf'): info_list.append(f"<b>CPF:</b> {cliente.get('cpf')}")
                    if cliente.get('telefone'): info_list.append(f"<b>Telefone:</b> {cliente.get('telefone')}")
                    if cliente.get('nascimento'): info_list.append(f"<b>Nascimento:</b> {cliente.get('nascimento')}")
                    texto_cliente = "<br/>".join(info_list)
                
                texto_produtos = "<br/>".join(venda['produtos'])
                texto_pagamentos = "<br/>".join([f"- {forma}: R$ {valor:.2f}" for forma, valor in venda['pagamentos']])
                texto_desconto = venda.get('desconto', 'N/A')
                
                # Monta a tabela para o card
                dados_tabela = [
                    [Paragraph(f"<b>Venda por: {venda['vendedor']}</b> | Data: {venda['data']}", styles['Normal'])],
                    [Paragraph(texto_cliente, styles['Normal']), Paragraph(texto_produtos, styles['Normal']), Paragraph(texto_pagamentos, styles['Normal']), Paragraph(texto_desconto, styles['Normal'])],
                    ['', '', '', Paragraph(f"<b>TOTAL: R$ {venda['total']:.2f}</b>", styles['Normal'])]
                ]
                
                tabela = Table(dados_tabela, colWidths=[5*cm, 5*cm, 4*cm, 3*cm])
                tabela.setStyle(TableStyle([
                    ('BOX', (0,0), (-1,-1), 1, colors.grey),
                    ('GRID', (0,1), (-1,-2), 0.5, colors.lightgrey),
                    ('SPAN', (0,0), (-1,0)), # Título da venda ocupa a linha toda
                    ('ALIGN', (0,0), (-1,0), 'CENTER'),
                    ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
                    ('VALIGN', (0,1), (-1,-1), 'TOP'),
                    ('ALIGN', (3,2), (3,2), 'RIGHT'), # Alinha o total à direita
                    ('BOTTOMPADDING', (0,0), (-1,-1), 12),
                    ('TOPPADDING', (0,0), (-1,-1), 6),
                ]))
                
                story.append(tabela)
                story.append(Spacer(1, 0.5*cm))

            doc.build(story)
            messagebox.showinfo("Sucesso", f"Relatório gerado com sucesso!\nSalvo como: {nome_arquivo}", parent=self.janela_relatorio)

        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao gerar o PDF: {e}", parent=self.janela_relatorio)