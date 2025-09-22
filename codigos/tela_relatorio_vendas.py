import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from ttkbootstrap.widgets import DateEntry #
from crud import buscar_vendas_para_relatorio, listar_usuarios 

class TelaRelatorioVendas:
    def __init__(self, master):
        self.master = master
        self.janela_relatorio = None

    def mostrar_janela(self):
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
        frame_filtros = ttk.LabelFrame(frame_principal, text="Filtros", padding=10)
        frame_filtros.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        ttk.Label(frame_filtros, text="Vendedor:").pack(side=LEFT, padx=(0, 5))
        vendedores = [u['usu_nome'] for u in listar_usuarios()]
        opcoes_filtro = ["Mostrar Tudo"] + sorted(vendedores)
        self.cmb_filtro = ttk.Combobox(frame_filtros, values=opcoes_filtro, state="readonly")
        self.cmb_filtro.pack(side=LEFT, padx=(0, 15))
        self.cmb_filtro.set("Mostrar Tudo")
        
        ttk.Label(frame_filtros, text="De:").pack(side=LEFT, padx=(0, 5))
        self.date_inicio = DateEntry(frame_filtros, bootstyle=PRIMARY, dateformat="%d/%m/%Y")
        self.date_inicio.pack(side=LEFT, padx=(0, 10))

        ttk.Label(frame_filtros, text="Até:").pack(side=LEFT, padx=(0, 5))
        self.date_fim = DateEntry(frame_filtros, bootstyle=PRIMARY, dateformat="%d/%m/%Y")
        self.date_fim.pack(side=LEFT, padx=(0, 20))
        
        btn_buscar = ttk.Button(frame_filtros, text="Buscar", command=self._filtrar_vendas, bootstyle=PRIMARY)
        btn_buscar.pack(side=LEFT)
        
        # --- Área Rolável (Com a correção) ---
        canvas = tk.Canvas(frame_principal, highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame_principal, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas, padding=10)
        self.scrollable_frame.columnconfigure(0, weight=3)
        self.scrollable_frame.columnconfigure(1, weight=4)
        self.scrollable_frame.columnconfigure(2, weight=3)
        self.scrollable_frame.columnconfigure(3, weight=2)
        
        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas_frame_id = canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # --- INÍCIO DA CORREÇÃO: LÓGICA PARA ROLAGEM COM O MOUSE ---
        def _on_mousewheel(event):
            # No Windows, event.delta é um múltiplo de 120. A divisão ajusta a velocidade.
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        # Vincula o evento da roda do mouse à função de rolagem
        self.scrollable_frame.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        self.scrollable_frame.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))
        # --- FIM DA CORREÇÃO ---
        
        canvas.grid(row=1, column=0, sticky="nsew")
        scrollbar.grid(row=1, column=1, sticky="ns")
        
        # --- Rodapé ---
        frame_rodape = ttk.LabelFrame(frame_principal, text="Resumo do Relatório", padding=10)
        frame_rodape.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        self.lbl_total_vendas = ttk.Label(frame_rodape, text="Total de Vendas: 0", font="-weight bold")
        self.lbl_total_vendas.pack(side=LEFT, padx=10)
        self.lbl_valor_arrecadado = ttk.Label(frame_rodape, text="Valor Arrecadado: R$ 0.00", font="-weight bold")
        self.lbl_valor_arrecadado.pack(side=LEFT, padx=10)
        
        btn_pdf = ttk.Button(frame_rodape, text="Baixar PDF do Relatório", command=self.gerar_relatorio_completo_pdf)
        btn_pdf.pack(side=RIGHT, padx=10)

        self._filtrar_vendas()

    def _filtrar_vendas(self, event=None):
        """Coleta os filtros da tela, busca no banco e manda popular o relatório."""
        vendedor = self.cmb_filtro.get()
        
        data_inicio_br = self.date_inicio.entry.get()
        data_fim_br = self.date_fim.entry.get()
        
        #Converte a data pro bd
        data_inicio_sql = datetime.strptime(data_inicio_br, "%d/%m/%Y").strftime("%Y-%m-%d")
        data_fim_sql = datetime.strptime(data_fim_br, "%d/%m/%Y").strftime("%Y-%m-%d")

        # Busca os dados no banco de dados com os filtros e datas já formatadas
        self.dados_filtrados = buscar_vendas_para_relatorio(vendedor, data_inicio_sql, data_fim_sql)
        
        # Popula a tela com os dados encontrados
        self._popular_relatorio(self.dados_filtrados)

    def _popular_relatorio(self, dados_das_vendas):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        row_counter = 0
        for venda in dados_das_vendas:
            cliente = venda.get('cliente', {})
            if not cliente.get('cpf'):
                texto_cliente = "Cliente não identificado"
            else:
                info_list = [
                    cliente.get('nome', 'N/A'),
                    cliente.get('cpf', ''),
                    cliente.get('telefone', ''),
                    cliente.get('nascimento', '')
                ]
                texto_cliente = "\n".join(filter(None, info_list)) # remove strings vazias

            texto_produtos = "\n".join(venda['produtos'])
            texto_pagamentos = "\n".join([f"- {forma}: R$ {valor:.2f}" for forma, valor in venda['pagamentos']])
            
            desconto_info = venda.get('desconto', '')
            cabecalho_desconto = "Desconto" if desconto_info else ""
            valor_desconto = desconto_info

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
            ttk.Label(self.scrollable_frame, text=f"TOTAL DA COMPRA: R$ {venda['ped_total']:.2f}", font="-weight bold").grid(row=row_counter, column=2, columnspan=2, sticky="e", pady=5)
            row_counter += 1
            ttk.Separator(self.scrollable_frame, orient=HORIZONTAL).grid(row=row_counter, column=0, columnspan=4, sticky="ew", pady=15)
            row_counter += 1

        # Atualiza o rodapé com os totais do filtro atual
        total_arrecadado = sum(v['ped_total'] for v in dados_das_vendas)
        self.lbl_total_vendas.config(text=f"Total de Vendas: {len(dados_das_vendas)}")
        self.lbl_valor_arrecadado.config(text=f"Valor Arrecadado: R$ {total_arrecadado:.2f}")

    def gerar_relatorio_completo_pdf(self):
        dados_para_pdf = self.dados_filtrados
        
        # Define o título do PDF com base nos filtros aplicados
        vendedor_selecionado = self.cmb_filtro.get()
        data_inicio = self.date_inicio.entry.get()
        data_fim = self.date_fim.entry.get()
        
        titulo_filtro = f"Vendedor: {vendedor_selecionado} | Período: {data_inicio} a {data_fim}"

        if not dados_para_pdf:
            messagebox.showwarning("Atenção", "Nenhuma venda encontrada para o relatório.", parent=self.janela_relatorio)
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"relatorio_vendas_{timestamp}.pdf"

        try:
            doc = SimpleDocTemplate(nome_arquivo, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []

            story.append(Paragraph("Relatório de Vendas", styles['h1']))
            story.append(Paragraph(f"Filtro Aplicado: {titulo_filtro}", styles['h3']))
            story.append(Spacer(1, 1*cm))

            for venda in dados_para_pdf:
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
                texto_desconto = venda.get('desconto', '')
                
                data_formatada = venda['ped_data']
                
                dados_tabela = [
                    [Paragraph(f"<b>Venda por: {venda['vendedor']}</b> | Data: {data_formatada}", styles['Normal'])],
                    [Paragraph(texto_cliente, styles['Normal']), Paragraph(texto_produtos, styles['Normal']), Paragraph(texto_pagamentos, styles['Normal']), Paragraph(texto_desconto, styles['Normal'])],
                    ['', '', '', Paragraph(f"<b>TOTAL: R$ {venda['ped_total']:.2f}</b>", styles['Normal'])]
                ]
                
                tabela = Table(dados_tabela, colWidths=[5*cm, 5*cm, 4*cm, 3*cm])
                tabela.setStyle(TableStyle([
                    ('BOX', (0,0), (-1,-1), 1, colors.grey),
                    ('GRID', (0,1), (-1,-2), 0.5, colors.lightgrey),
                    ('SPAN', (0,0), (-1,0)),
                    ('ALIGN', (0,0), (-1,0), 'CENTER'),
                    ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
                    ('VALIGN', (0,1), (-1,-1), 'TOP'),
                    ('ALIGN', (3,2), (3,2), 'RIGHT'),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 12),
                    ('TOPPADDING', (0,0), (-1,-1), 6),
                ]))
                
                story.append(tabela)
                story.append(Spacer(1, 0.5*cm))

            doc.build(story)
            messagebox.showinfo("Sucesso", f"Relatório gerado com sucesso!\nSalvo como: {nome_arquivo}", parent=self.janela_relatorio)

        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao gerar o PDF: {e}.\nTente novamente.", parent=self.janela_relatorio)