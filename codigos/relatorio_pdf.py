# relatorio_pdf.py
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import datetime
import os

def gerar_relatorio_pdf(divergencias=None, negativados=None, pdvs=None):
    caminho_logo = os.path.join(os.path.dirname(__file__), "..", "imagens", "Checkpoint_completo_sfundo.png")
    data_str = datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    nome_arquivo = f"relatorio_inventario_{data_str}.pdf"
    doc = SimpleDocTemplate(nome_arquivo, pagesize=A4)
    elementos = []
    styles = getSampleStyleSheet()

    try:
        logo = Image(caminho_logo, width=400, height=80)
        elementos.append(logo)
    except Exception as e:
        print(f"Erro ao carregar logo: {e}")

    elementos.append(Paragraph("Relatório de Inventário", styles["Title"]))
    elementos.append(Spacer(1, 12))

    def adicionar_tabela(titulo, dados):
        if not dados:
            return
        elementos.append(Paragraph(titulo, styles["Heading2"]))
        elementos.append(Spacer(1, 6))
        cabecalho = ["Ref", "SKU", "Descrição", "Tam/Cap", "Estoque", "Est. Real"]
        tabela = Table([cabecalho] + list(dados), colWidths=[50, 50, 200, 60, 60, 60])
        estilo = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#003366")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ])
        for i in range(1, len(dados)+1):
            cor = colors.whitesmoke if i % 2 == 0 else colors.lightgrey
            estilo.add('BACKGROUND', (0, i), (-1, i), cor)

        tabela.setStyle(estilo)
        elementos.append(tabela)
        elementos.append(Spacer(1, 12))

    adicionar_tabela("Produtos com divergência", divergencias)
    adicionar_tabela("Produtos negativados", negativados)
    adicionar_tabela("Produtos PDV", pdvs)

    doc.build(elementos)
    return nome_arquivo
