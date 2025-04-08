from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import datetime
import os

def gerar_relatorio_pdf(dados, nome_arquivo=None):
    caminho_logo = os.path.join(os.path.dirname(__file__), "..\imagens\Checkpoint_completo_sfundo.png")
    if nome_arquivo is None:
        data_str = datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        nome_arquivo = f"relatorio_divergencias_{data_str}.pdf"

    doc = SimpleDocTemplate(nome_arquivo, pagesize=A4)
    elementos = []
    styles = getSampleStyleSheet()

    try:
        logo = Image(caminho_logo, width=500, height=100)
        elementos.append(logo)
    except Exception as e:
        print(f"Erro ao carregar logo: {e}")

    titulo = Paragraph("Relatório de Divergências de Inventário", styles["Title"])
    elementos.append(titulo)
    elementos.append(Spacer(1, 12))

    tabela_dados = [["Produto", "Esperado", "Contado", "Diferença"]]
    for item in dados:
        diferenca = item["contado"] - item["esperado"]
        tabela_dados.append([
            item["produto"],
            str(item["esperado"]),
            str(item["contado"]),
            f"{diferenca:+}"
        ])

    tabela = Table(tabela_dados, colWidths=[200, 80, 80, 80])
    estilo = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#003366")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ])
    tabela.setStyle(estilo)

    for i in range(1, len(tabela_dados)):
        cor = colors.whitesmoke if i % 2 == 0 else colors.lightgrey
        tabela.setStyle([('BACKGROUND', (0, i), (-1, i), cor)])

    elementos.append(tabela)
    doc.build(elementos)

    return nome_arquivo
