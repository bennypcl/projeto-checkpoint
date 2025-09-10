from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import datetime
import os

# --- Função Principal ---
def gerar_relatorio_pdf(divergencias, negativados, pdvs, nome_arquivo=None):
    """
    Gera um relatório PDF com seções para Divergências, Negativados e PDVs.
    """
    if nome_arquivo is None:
        data_str = datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        nome_arquivo = f"relatorio_inventario_{data_str}.pdf"

    doc = SimpleDocTemplate(nome_arquivo, pagesize=A4)
    elementos = []
    
    # Adiciona o Logo e o Título Principal
    _adicionar_cabecalho(elementos)

    # --- Cria uma seção para cada tipo de dado ---
    # Seção de Divergências (formato especial com cálculo)
    if divergencias:
        _criar_secao_divergencias(elementos, divergencias)

    # Seções de Negativados e PDVs (formato padrão)
    if negativados:
        _criar_secao_padrao(elementos, "Produtos Negativados", negativados)
        
    if pdvs:
        _criar_secao_padrao(elementos, "Produtos PDV", pdvs)

    doc.build(elementos)
    return nome_arquivo

# --- Funções Auxiliares ---
def _adicionar_cabecalho(elementos):
    """Adiciona o logo e o título ao documento."""
    styles = getSampleStyleSheet()
    caminho_logo = os.path.join(os.path.dirname(__file__), "..", "imagens", "Checkpoint_completo_sfundo.png")
    
    try:
        logo = Image(caminho_logo, width=500, height=100)
        elementos.append(logo)
    except Exception as e:
        print(f"Erro ao carregar logo: {e}")

    titulo = Paragraph("Relatório de Inventário", styles["Title"])
    elementos.append(titulo)
    elementos.append(Spacer(1, 12))

def _criar_secao_divergencias(elementos, dados):
    """Cria a tabela específica para as divergências, com cálculo."""
    styles = getSampleStyleSheet()
    elementos.append(Paragraph("Produtos com Divergência", styles['h2']))
    elementos.append(Spacer(1, 12))

    # Prepara os dados com o cálculo da diferença
    tabela_dados = [["Produto", "Esperado", "Contado", "Diferença"]]
    for item in dados:
        try:
            esperado = int(item[4])
            contado = int(item[5])
            diferenca = contado - esperado
            tabela_dados.append([
                item[2], # Descrição
                str(esperado),
                str(contado),
                f"{diferenca:+}" # Sinal de + ou -
            ])
        except (ValueError, TypeError, IndexError):
            continue

    # Cria e estiliza a tabela
    tabela = Table(tabela_dados, colWidths=[200, 80, 80, 80])
    _aplicar_estilo_tabela(tabela, len(tabela_dados))
    elementos.append(tabela)
    elementos.append(Spacer(1, 24))

def _criar_secao_padrao(elementos, titulo_secao, dados):
    """Cria uma tabela padrão para Negativados e PDVs."""
    styles = getSampleStyleSheet()
    elementos.append(Paragraph(titulo_secao, styles['h2']))
    elementos.append(Spacer(1, 12))

    # Prepara os dados para a tabela
    tabela_dados = [["Ref", "SKU", "Descrição", "Estoque"]]
    for item in dados:
        try:
            tabela_dados.append([
                item[0], # Ref
                item[1], # SKU
                item[2], # Descrição
                str(item[4])  # Estoque
            ])
        except IndexError:
            continue
    
    # Cria e estiliza a tabela
    tabela = Table(tabela_dados, colWidths=[60, 100, 200, 60])
    _aplicar_estilo_tabela(tabela, len(tabela_dados))
    elementos.append(tabela)
    elementos.append(Spacer(1, 24))

def _aplicar_estilo_tabela(tabela, num_linhas):
    """Aplica um estilo visual padrão a uma tabela."""
    estilo = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#003366")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (2, 1), (2, -1), 'LEFT'), # Alinha a descrição à esquerda
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ])
    tabela.setStyle(estilo)

    # Aplica cores alternadas nas linhas
    for i in range(1, num_linhas):
        cor = colors.whitesmoke if i % 2 == 0 else colors.lightgrey
        tabela.setStyle([('BACKGROUND', (0, i), (-1, i), cor)])