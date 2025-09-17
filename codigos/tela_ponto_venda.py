import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox, simpledialog
import re
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from datetime import datetime
from reportlab.lib.units import cm
from crud import (
    buscar_cliente_por_cpf, 
    inserir_cliente, 
    atualizar_cliente, 
    buscar_produto_por_sku, 
    salvar_venda_completa,
    buscar_produto_por_sku_ou_bipe
)
from crud import listar_usuarios

class TelaPontoVenda:
    def __init__(self, master, vendas_realizadas_ref, tela_consulta, callback_venda_finalizada=None):
        self.master = master
        self.lista_de_vendas_global = vendas_realizadas_ref
        self.tela_consulta_ref = tela_consulta # Guarda a referência
        self.callback_venda_finalizada = callback_venda_finalizada
        self.janela_pdv = None
        self.vendedor_selecionado = None
        self.dados_cliente = {}
        self.produtos = []
        self.total_compra = 0.0
        self.valor_restante = 0.0
        self.pagamentos = []
        self.produtos_na_venda = []
        self.vendedores = []
        self.bandeiras = ["Visa", "MasterCard", "Elo", "Amex"]

        self.frame_atual = None

        # --- Variáveis com Trace para Formatação Automática ---
        self._is_formatting = False # Variável de controle para evitar loops
        self._nome_trace_set = False # Controle para garantir que o trace do nome seja criado só uma vez
        self._produto_trace_set = False # Controle para garantir que o trace do produto seja criado só uma vez
        self._cpf_trace_set = False # Novo controle para o CPF
        self._telefone_trace_set = False # Novo controle para o Telefone
        
        self.cpf_var = tk.StringVar()
        self.telefone_var = tk.StringVar()
        self.nome_var = tk.StringVar()
        self.produto_var = tk.StringVar()

        # --- Novas Variáveis de Controle para a Tela de Venda ---
        self.imprimir_ticket_var = tk.BooleanVar(value=False) # Checkbox já vem marcado
        self.tipo_desconto_var = tk.StringVar(value="%")     # Para os RadioButtons de desconto
        self.desconto_aplicado_valor = 0.0                   # Guarda o valor do desconto
        self.desconto_aplicado_info = ""                     # Guarda o texto do desconto

        self._editando_cliente = False
        self.modo_manipulacao = "adicionar"
        self.vendedor_selecionado_id = None

    def abrir_consulta_produtos(self):
        """Chama a tela de seleção de produtos e passa a janela-mãe e a função de callback."""
        self.tela_consulta_ref.selecionar_produto(
            parent=self.janela_pdv, 
            callback=self.produto_selecionado_callback
        )

    def produto_selecionado_callback(self, sku):
        """Função que é chamada pela tela de consulta quando um produto é selecionado."""
        self.produto_var.set(sku)
        self.entry_produto.focus_set()
        self.entry_produto.icursor(END)

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
        # Limpeza de dados da venda anterior
        self.vendedor_selecionado = None
        self.vendedor_selecionado_id = None
        self.dados_cliente = {}
        self.produtos = []
        self.total_compra = 0.0
        self.valor_restante = 0.0
        self.pagamentos = []
        self.produtos_na_venda = []
        self.imprimir_ticket_var.set(False)
        self.tipo_desconto_var.set("%")
        self.desconto_aplicado_valor = 0.0
        self.desconto_aplicado_info = ""
        self._editando_cliente = False
        self.modo_manipulacao = "adicionar"

        # Limpeza das StringVars dos campos de texto
        if hasattr(self, 'cpf_var'):
            self.cpf_var.set("")
            self.nome_var.set("")
            self.telefone_var.set("")

        self.limpar_frame()
        self.frame_atual = ttk.Frame(self.janela_pdv)
        self.frame_atual.pack(fill="both", expand=True)

        # Container central dentro do frame
        container = ttk.Frame(self.frame_atual)
        container.grid(row=0, column=0, padx=50, pady=50)
        self.frame_atual.columnconfigure(0, weight=1)
        self.frame_atual.rowconfigure(0, weight=1)

        # Conteúdo centralizado
        ttk.Label(container, text="Selecione o Vendedor", font=("Arial", 16)).grid(row=0, column=0, columnspan=2, pady=(0, 10))

        #Busca os vendedores do banco de dados
        self.lista_de_usuarios_completa = listar_usuarios() # Guarda a lista completa
        # Extrai apenas os nomes para mostrar no Combobox
        self.vendedores = [u['usu_nome'] for u in self.lista_de_usuarios_completa]
        self.cmb_vendedor = ttk.Combobox(container, values=self.vendedores, state="readonly")
        self.cmb_vendedor.grid(row=1, column=0, columnspan=2, pady=10)
        ttk.Button(container, text="Avançar", command=self.validar_vendedor).grid(row=2, column=0, columnspan=2, pady=10)

    def validar_vendedor(self):
        nome_vendedor = self.cmb_vendedor.get()
        if not nome_vendedor:
            messagebox.showerror("Erro", "Selecione um vendedor para continuar.")
            return
        self.vendedor_selecionado = nome_vendedor

        # Procura o ID do vendedor na lista completa
        for usuario in self.lista_de_usuarios_completa:
            if usuario['usu_nome'] == nome_vendedor:
                self.vendedor_selecionado_id = usuario['usu_id']
                break

        if self.vendedor_selecionado == "TROCA":
            self.modo_manipulacao = "devolver"
        else:
            self.modo_manipulacao = "adicionar"

        self.tela_cadastro_cliente()

    def _validar_dia_mes(self, valor_digitado):
        """Impede a digitação de caracteres não numéricos."""
        return valor_digitado.isdigit() or valor_digitado == ""

    def _formatar_data_focus_out(self, event, max_val):
        """Formata o valor com zero à esquerda e valida o limite ao sair do campo."""
        widget = event.widget
        texto = widget.get()
        if texto.isdigit():
            valor = int(texto)
            if valor > max_val:
                widget.set(max_val)
            elif valor < 1:
                widget.set(f"{1:02d}")
            else:
                widget.set(f"{valor:02d}")

    def _formatar_para_maiusculo(self, string_var, entry_widget):
        # Se a função já estiver em execução, não faz nada (evita loop infinito)
        if self._is_formatting:
            return

        self._is_formatting = True  # Avisa que a formatação começou
        
        texto = string_var.get()
        texto_maiusculo = texto.upper()
        string_var.set(texto_maiusculo)
        
        # Move o cursor para o final
        entry_widget.after(1, lambda: entry_widget.icursor(len(texto_maiusculo)) if entry_widget.winfo_exists() else None)

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
        self.entry_cpf.after(1, lambda: self.entry_cpf.icursor(len(formatado)) if self.entry_cpf.winfo_exists() else None)

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
        self.entry_telefone.after(1, lambda: self.entry_telefone.icursor(len(formatado)) if self.entry_telefone.winfo_exists() else None)

    def tela_cadastro_cliente(self):
        self.limpar_frame()
        
        self.frame_atual = ttk.Frame(self.janela_pdv)
        self.frame_atual.pack(fill="both", expand=True)

        self.frame_atual.columnconfigure(0, weight=1)
        self.frame_atual.rowconfigure(0, weight=1)

        container = ttk.Frame(self.frame_atual)
        container.grid(row=0, column=0)

        ttk.Label(container, text=f"{self.vendedor_selecionado}", font=("Arial", 10, "italic")).grid(
            row=0, column=0, columnspan=2, pady=(0, 20), sticky="w")

        ttk.Label(container, text="Cadastro do Cliente", font=("Arial", 16, "bold")).grid(
            row=1, column=0, columnspan=2, pady=(0, 15))

        # Campo CPF
        ttk.Label(container, text="CPF:").grid(row=2, column=0, padx=5, pady=8, sticky="e")
        self.entry_cpf = ttk.Entry(container, width=30, textvariable=self.cpf_var)
        self.entry_cpf.grid(row=2, column=1, padx=5, pady=8)
        self.entry_cpf.focus_set()
        self.entry_cpf.bind("<FocusOut>", self._ao_sair_do_cpf)

        # Ativa o trace para o CPF
        if not self._cpf_trace_set:
            self.cpf_var.trace_add('write', self.formatar_cpf)
            self._cpf_trace_set = True

        # Campo Nome
        ttk.Label(container, text="Nome:").grid(row=3, column=0, padx=5, pady=8, sticky="e")
        self.entry_nome = ttk.Entry(container, width=30, textvariable=self.nome_var)
        self.entry_nome.grid(row=3, column=1, padx=5, pady=8)

        # Ativa o trace para o Nome
        if not self._nome_trace_set:
            self.nome_var.trace_add('write', 
                lambda *args: self._formatar_para_maiusculo(self.nome_var, self.entry_nome))
            self._nome_trace_set = True

        # Campo Telefone
        ttk.Label(container, text="Telefone:").grid(row=4, column=0, padx=5, pady=8, sticky="e")
        self.entry_telefone = ttk.Entry(container, width=30, textvariable=self.telefone_var)
        self.entry_telefone.grid(row=4, column=1, padx=5, pady=8)

        # Ativa o trace para o Telefone
        if not self._telefone_trace_set:
            self.telefone_var.trace_add('write', self.formatar_telefone)
            self._telefone_trace_set = True

        # Campos de Data de Nascimento com Spinbox
        ttk.Label(container, text="Data de Nascimento:").grid(row=5, column=0, padx=5, pady=8, sticky="e")
        
        frame_nascimento = ttk.Frame(container)
        frame_nascimento.grid(row=5, column=1, padx=5, pady=8, sticky="w")
        
        # Registra a função de validação
        vcmd = (self.janela_pdv.register(self._validar_dia_mes), '%P')

        # Spinbox para o Dia, com validação e formatação
        self.spin_dia = ttk.Spinbox(frame_nascimento, from_=1, to=31, width=4,
                                    validate='key', validatecommand=vcmd)
        self.spin_dia.pack(side="left", padx=(0, 5))
        self.spin_dia.bind("<FocusOut>", lambda e: self._formatar_data_focus_out(e, 31))
        
        # Spinbox para o Mês, com validação e formatação
        self.spin_mes = ttk.Spinbox(frame_nascimento, from_=1, to=12, width=4,
                                    validate='key', validatecommand=vcmd)
        self.spin_mes.pack(side="left", padx=5)
        self.spin_mes.bind("<FocusOut>", lambda e: self._formatar_data_focus_out(e, 12))

        # Spinbox para o Ano
        self.spin_ano = ttk.Spinbox(frame_nascimento, from_=1920, to=2024, width=6)
        self.spin_ano.pack(side="left")

        # Frame para os botões de ação
        frame_botoes = ttk.Frame(container)
        frame_botoes.grid(row=6, column=0, columnspan=2, pady=(20, 0))
        btn_voltar = ttk.Button(frame_botoes, text="Voltar", command=self.voltar_do_cadastro_cliente, bootstyle=(SECONDARY, OUTLINE))
        btn_voltar.pack(side="left", padx=10)
        btn_continuar = ttk.Button(frame_botoes, text="Continuar", command=self.verificar_dados_cliente)
        btn_continuar.pack(side="left", padx=10)

    def _ao_sair_do_cpf(self, event=None):
        """Chamado quando o usuário sai do campo CPF para buscar o cliente."""
        cpf = self.cpf_var.get()
        cpf_numeros = "".join(filter(str.isdigit, cpf))

        if len(cpf_numeros) == 11:
            cliente_existente = buscar_cliente_por_cpf(cpf_numeros)

            if cliente_existente:
                self.nome_var.set(cliente_existente.get('cli_nome', ''))
                
                # Formata o telefone (DDD + numero)
                ddd = cliente_existente.get('cli_ddd', '')
                tel = cliente_existente.get('cli_telefone', '')
                if ddd and tel:
                    self.telefone_var.set(f"({ddd}) {tel}")

                # Preenche a data de nascimento
                data_nasc = cliente_existente.get('cli_data_nascimento')
                if data_nasc:
                    # Formata a data do banco (YYYY-MM-DD) para o formato dos Spinboxes
                    dia = data_nasc.strftime('%d')
                    mes = data_nasc.strftime('%m')
                    ano = data_nasc.strftime('%Y')
                    self.spin_dia.set(dia)
                    self.spin_mes.set(mes)
                    self.spin_ano.set(ano)

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
        cpf_numeros = "".join(filter(str.isdigit, self.cpf_var.get()))
        nome = self.nome_var.get()
        tel_formatado = self.telefone_var.get()
        
        # Extrai DDD e Telefone
        tel_numeros = "".join(filter(str.isdigit, tel_formatado))
        ddd = tel_numeros[:2] if len(tel_numeros) >= 2 else ""
        telefone = tel_numeros[2:] if len(tel_numeros) > 2 else ""

        # Monta a data no formato do banco (YYYY-MM-DD)
        data_nasc_formatada = None
        if self.spin_dia.get() and self.spin_mes.get() and self.spin_ano.get():
            data_nasc_formatada = f"{self.spin_ano.get()}-{self.spin_mes.get()}-{self.spin_dia.get()}"

        # Salva os dados na memória para usar na venda
        self.dados_cliente = {
            "cpf": cpf_numeros, "nome": nome, "telefone": tel_formatado, 
            "nascimento": f"{self.spin_dia.get()}/{self.spin_mes.get()}/{self.spin_ano.get()}" if data_nasc_formatada else ""
        }

        # Lógica de salvar/atualizar no banco
        if cpf_numeros and nome: # Só salva se tiver CPF e Nome
            cliente_existente = buscar_cliente_por_cpf(cpf_numeros)
            if cliente_existente:
                # Se existe, atualiza
                atualizar_cliente(cpf_numeros, nome, data_nasc_formatada, ddd, telefone)
                self.dados_cliente['id'] = cliente_existente['cli_id'] # Guarda o ID
            else:
                # Se não existe, insere
                inserir_cliente(cpf=cpf_numeros, nome=nome, data_nascimento=data_nasc_formatada, ddd=ddd, telefone=telefone)
                # Idealmente, após inserir, você buscaria o cliente de novo para pegar o ID
                novo_cliente = buscar_cliente_por_cpf(cpf_numeros)
                if novo_cliente:
                    self.dados_cliente['id'] = novo_cliente['cli_id']

        self.tela_venda()

    def aplicar_desconto(self):
        if self.desconto_aplicado_valor > 0:
            messagebox.showwarning("Atenção", "Um desconto já foi aplicado a esta venda.", parent=self.janela_pdv)
            return

        tipo = self.tipo_desconto_var.get()
        try:
            valor_desconto_str = self.entry_desconto.get().replace(",", ".")
            valor_desconto = float(valor_desconto_str)
        except ValueError:
            messagebox.showerror("Erro", "Valor de desconto inválido.", parent=self.janela_pdv)
            return

        if valor_desconto <= 0:
            messagebox.showerror("Erro", "O valor do desconto deve ser maior que zero.", parent=self.janela_pdv)
            return

        total_original = self.total_compra
        
        if tipo == "%":
            if valor_desconto > 100:
                messagebox.showerror("Erro", "O desconto em porcentagem não pode ser maior que 100%.", parent=self.janela_pdv)
                return
            self.desconto_aplicado_valor = total_original * (valor_desconto / 100)
            self.desconto_aplicado_info = f"{valor_desconto}%"
        else: # tipo == "R$"
            if valor_desconto > total_original:
                messagebox.showerror("Erro", "O desconto em valor não pode ser maior que o total da compra.", parent=self.janela_pdv)
                return
            self.desconto_aplicado_valor = valor_desconto
            self.desconto_aplicado_info = f"R$ {valor_desconto:.2f}"
            
        # Atualiza os totais e a tela
        self.atualizar_total()

        # Desativa os campos de desconto para evitar múltiplos descontos
        self.entry_desconto.config(state="disabled")
        self.btn_aplicar_desconto.config(state="disabled")

    def editar_cliente(self):
        """Prepara para editar/adicionar um cliente e navega para a tela de cadastro."""
        self._editando_cliente = True

        # PASSO 1: Navega para a tela e CRIA os novos widgets
        self.tela_cadastro_cliente()

        # PASSO 2: AGORA que os widgets da tela de cadastro já existem, nós os preenchemos
        if self.dados_cliente:
            # Preenche os campos de texto
            self.cpf_var.set(self.dados_cliente.get("cpf", ""))
            self.nome_var.set(self.dados_cliente.get("nome", ""))
            self.telefone_var.set(self.dados_cliente.get("telefone", ""))
            
            # Preenche os campos de data de nascimento
            data_nasc_str = self.dados_cliente.get("nascimento", "")
            if data_nasc_str:
                try:
                    dia, mes, ano = data_nasc_str.split('/')
                    # Define o valor diretamente nos widgets
                    self.spin_dia.set(dia)
                    self.spin_mes.set(mes)
                    self.spin_ano.set(ano)
                except (ValueError, AttributeError):
                    print(f"Aviso: Formato de data inválido em dados_cliente: {data_nasc_str}")

    def voltar_do_cadastro_cliente(self):
        """Decide para qual tela voltar com base no modo de edição."""
        if self._editando_cliente:
            self.tela_venda() # Se estava editando, volta para a venda
        else:
            self.tela_selecao_vendedor() # Se era um novo cadastro, volta para o início

    def _atualizar_estilo_botoes_modo(self):
        """Muda a aparência dos botões para indicar o modo ativo."""
        # Define o estilo padrão (contorno) para todos
        self.btn_adicionar.config(bootstyle=OUTLINE)
        self.btn_remover_por_nome.config(bootstyle=OUTLINE)
        self.btn_devolver.config(bootstyle=OUTLINE)

        # Define o estilo sólido para o botão do modo ativo
        if self.modo_manipulacao == "adicionar":
            self.btn_adicionar.config(bootstyle=PRIMARY)
        elif self.modo_manipulacao == "remover":
            self.btn_remover_por_nome.config(bootstyle=PRIMARY)
        elif self.modo_manipulacao == "devolver":
            self.btn_devolver.config(bootstyle=PRIMARY)

    def set_modo_adicionar(self):
        self.modo_manipulacao = "adicionar"
        self._atualizar_estilo_botoes_modo()
        self.entry_produto.focus_set()

    def set_modo_remover(self):
        self.modo_manipulacao = "remover"
        self._atualizar_estilo_botoes_modo()
        self.entry_produto.focus_set()

    def set_modo_devolver(self):
        # Apenas permite o modo de devolução se o vendedor for "Troca"
        if self.vendedor_selecionado == "TROCA":
            self.modo_manipulacao = "devolver"
            self._atualizar_estilo_botoes_modo()
            self.entry_produto.focus_set()
        else:
            messagebox.showwarning("Acesso Negado", "Apenas o vendedor 'TROCA' pode processar devoluções.", parent=self.janela_pdv)

    def processar_produto_entry(self):
        """Executa a ação correta com base no modo de manipulação ativo."""
        if self.modo_manipulacao == "adicionar":
            self.adicionar_produto()
        elif self.modo_manipulacao == "remover":
            self.remover_produto()
        elif self.modo_manipulacao == "devolver":
            self.devolver_produto()

    def tela_venda(self):
        self.limpar_frame()
        self.frame_atual = ttk.Frame(self.janela_pdv)
        self.frame_atual.pack(fill=BOTH, expand=True, padx=10, pady=10)

        self.frame_atual.columnconfigure(0, weight=1) 
        self.frame_atual.rowconfigure(0, weight=1)    

        container_esquerda = ttk.Frame(self.frame_atual)
        container_direita = ttk.Frame(self.frame_atual, width=450)        
        container_esquerda.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        container_direita.grid(row=0, column=1, sticky="ns", padx=(10, 0))
        container_direita.grid_propagate(False)

        # --- PAINEL ESQUERDO: PRODUTOS E TOTAL ---
        container_esquerda.rowconfigure(2, weight=1) # A lista de produtos agora está na linha 2
        container_esquerda.columnconfigure(0, weight=1)

        # Seção de Informações do Cliente
        frame_cliente_info = ttk.LabelFrame(container_esquerda, text="Dados do Cliente")
        frame_cliente_info.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        frame_cliente_info.columnconfigure(0, weight=1)

        # Verifica se um cliente já foi cadastrado para esta venda
        if self.dados_cliente and self.dados_cliente.get("cpf"):
            # Se sim, mostra os dados e o botão de editar
            info_cliente = f"Nome: {self.dados_cliente.get('nome', '')}\nCPF: {self.dados_cliente.get('cpf', '')}"
            ttk.Label(frame_cliente_info, text=info_cliente, justify="left").grid(row=0, column=0, sticky="w", padx=5, pady=5)
            
            btn_editar_cliente = ttk.Button(frame_cliente_info, text="Editar", command=self.editar_cliente)
            btn_editar_cliente.grid(row=0, column=1, sticky="e", padx=5, pady=5)
        else:
            # Se não, mostra apenas o botão para cadastrar
            btn_cadastrar_cliente = ttk.Button(frame_cliente_info, text="Cadastrar Cliente", command=self.editar_cliente)
            btn_cadastrar_cliente.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        # Frame para os botões e entrada de produto
        frame_manipula_produto = ttk.LabelFrame(container_esquerda, text="Manipular Produtos")
        frame_manipula_produto.grid(row=1, column=0, sticky="ew", pady=(0,10))
        frame_manipula_produto.columnconfigure(0, weight=1)

        # Frame para os botões de ação do produto
        frame_botoes_produto = ttk.Frame(frame_manipula_produto)
        frame_botoes_produto.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        frame_botoes_produto.columnconfigure((0,1,2), weight=1)

        self.btn_adicionar = ttk.Button(frame_botoes_produto, text="Adicionar", command=self.set_modo_adicionar)
        self.btn_adicionar.grid(row=0, column=0, sticky="ew", padx=2)
        
        self.btn_remover_por_nome = ttk.Button(frame_botoes_produto, text="Remover", command=self.set_modo_remover)
        self.btn_remover_por_nome.grid(row=0, column=1, sticky="ew", padx=2)

        estado_devolver = "normal" if self.vendedor_selecionado == "TROCA" else "disabled"
        self.btn_devolver = ttk.Button(frame_botoes_produto, text="Devolver", command=self.set_modo_devolver, state=estado_devolver)
        self.btn_devolver.grid(row=0, column=2, sticky="ew", padx=2)
        
        # Frame para a entrada do produto
        frame_entry_produto = ttk.Frame(frame_manipula_produto)
        frame_entry_produto.grid(row=1, column=0, sticky="ew", padx=5, pady=(0,5))
        frame_entry_produto.columnconfigure(1, weight=1)
        
        ttk.Label(frame_entry_produto, text="Produto:").grid(row=0, column=0, padx=(0, 5))
        self.entry_produto = ttk.Entry(frame_entry_produto, textvariable=self.produto_var)
        self.entry_produto.grid(row=0, column=1, sticky="ew")
        self.entry_produto.focus_set()        
        self.entry_produto.bind("<Return>", self.processar_produto_event)

        btn_consulta = ttk.Button(frame_entry_produto, text="...", command=self.abrir_consulta_produtos, width=3)
        btn_consulta.grid(row=0, column=2, padx=(5,0), pady=5)
        
        if not self._produto_trace_set:
            self.produto_var.trace_add('write', lambda *args: self._formatar_para_maiusculo(self.produto_var, self.entry_produto))
            self._produto_trace_set = True

        # Chama a função para definir o estilo inicial dos botões
        self._atualizar_estilo_botoes_modo()
        
        # Seção da Lista de Produtos (agora na linha 2)
        frame_lista_produtos = ttk.Frame(container_esquerda)
        frame_lista_produtos.grid(row=2, column=0, sticky="nsew")
        frame_lista_produtos.rowconfigure(0, weight=1)
        frame_lista_produtos.columnconfigure(0, weight=1)
        colunas = ('produto', 'codigo', 'tamanho', 'preco')
        self.tvw_produtos = ttk.Treeview(frame_lista_produtos, columns=colunas, show='headings')
        self.tvw_produtos.heading('produto', text='Produto')
        self.tvw_produtos.heading('codigo', text='Código')
        self.tvw_produtos.heading('tamanho', text='Tamanho')
        self.tvw_produtos.heading('preco', text='Preço')
        self.tvw_produtos.column('preco', width=80, anchor="e")
        self.tvw_produtos.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(frame_lista_produtos, orient="vertical", command=self.tvw_produtos.yview)
        self.tvw_produtos.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Seção de Totais
        frame_totais = ttk.Frame(container_esquerda)
        frame_totais.grid(row=4, column=0, sticky="ew", pady=(10, 0))
        frame_totais.columnconfigure(1, weight=1)
        
        ttk.Label(frame_totais, text="Subtotal:").grid(row=0, column=0, sticky="w")
        self.subtotal_label = ttk.Label(frame_totais, text="R$ 0.00")
        self.subtotal_label.grid(row=0, column=1, sticky="e")
        
        ttk.Label(frame_totais, text="Desconto:").grid(row=1, column=0, sticky="w")
        self.desconto_label = ttk.Label(frame_totais, text="R$ 0.00")
        self.desconto_label.grid(row=1, column=1, sticky="e")

        ttk.Label(frame_totais, text="Total da Compra:", font=("Arial", 14, "bold")).grid(row=2, column=0, sticky="w", pady=(5,0))
        self.total_label = ttk.Label(frame_totais, text="R$ 0.00", font=("Arial", 14, "bold"))
        self.total_label.grid(row=2, column=1, sticky="e", pady=(5,0))

        # PAINEL DIREITO: PAGAMENTOS E AÇÕES
        container_direita.columnconfigure(0, weight=1)
        container_direita.rowconfigure(3, weight=1)
        
        ttk.Label(container_direita, text=f"Vendedor(a): {self.vendedor_selecionado}", font=("Arial", 9, "italic")).grid(row=0, column=0, sticky="w")
        ttk.Label(container_direita, text="Valor a Pagar:", font=("Arial", 12)).grid(row=1, column=0, sticky="w", pady=(10,5))
        self.valor_editavel = ttk.Entry(container_direita, font=("Arial", 14), justify="right")
        self.valor_editavel.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        self.valor_editavel.insert(0, "0.00")
        self.valor_editavel.bind("<FocusIn>", lambda event: self.valor_editavel.icursor(tk.END))
        
        frame_formas_pagamento = ttk.Frame(container_direita)
        frame_formas_pagamento.grid(row=3, column=0, sticky="new")
        frame_formas_pagamento.columnconfigure((0, 1), weight=1)
        ttk.Button(frame_formas_pagamento, text="Dinheiro", command=self.pagamento_dinheiro).grid(row=0, column=0, sticky="ew", padx=2, pady=2)
        ttk.Button(frame_formas_pagamento, text="Débito", command=self.pagamento_debito).grid(row=0, column=1, sticky="ew", padx=2, pady=2)
        ttk.Button(frame_formas_pagamento, text="Crédito", command=self.pagamento_credito).grid(row=1, column=0, sticky="ew", padx=2, pady=2)
        ttk.Button(frame_formas_pagamento, text="Pix", command=self.pagamento_pix).grid(row=1, column=1, sticky="ew", padx=2, pady=2)

        # Frame para detalhes de pagamento dinâmico
        self.frame_detalhes_pagamento = ttk.Frame(container_direita)
        self.frame_detalhes_pagamento.grid(row=4, column=0, sticky="ew", pady=5)

        #Frame de desconto
        frame_desconto = ttk.LabelFrame(container_direita, text="Aplicar Desconto")
        frame_desconto.grid(row=5, column=0, sticky="ew", pady=10)
        frame_desconto.columnconfigure(1, weight=1)

        # Atribuindo os RadioButtons a variáveis para poder desabilitá-los
        self.radio_pct = ttk.Radiobutton(frame_desconto, text="%", variable=self.tipo_desconto_var, value="%")
        self.radio_pct.grid(row=0, column=0, sticky="w", padx=10, pady=(2,0))
        
        self.radio_rs = ttk.Radiobutton(frame_desconto, text="R$", variable=self.tipo_desconto_var, value="R$")
        self.radio_rs.grid(row=1, column=0, sticky="w", padx=10, pady=(0,2))

        self.entry_desconto = ttk.Entry(frame_desconto)
        self.entry_desconto.grid(row=0, column=1, sticky="ew", padx=5, pady=5, rowspan=2)
        
        self.btn_aplicar_desconto = ttk.Button(frame_desconto, text="Aplicar", command=self.aplicar_desconto)
        self.btn_aplicar_desconto.grid(row=0, column=2, sticky="ew", padx=(0,5), pady=5, rowspan=2)

        self.btn_limpar_desconto = ttk.Button(frame_desconto, text="Limpar", command=self.limpar_desconto, bootstyle=(SECONDARY, OUTLINE))
        self.btn_limpar_desconto.grid(row=0, column=3, sticky="ew", padx=(0,5), pady=5, rowspan=2)

        if self.vendedor_selecionado == "TROCA":
            # Desabilita todos os widgets dentro do frame de desconto
            self.radio_pct.config(state="disabled")
            self.radio_rs.config(state="disabled")
            self.entry_desconto.config(state="disabled")
            self.btn_aplicar_desconto.config(state="disabled")
            self.btn_limpar_desconto.config(state="disabled")

        frame_resumo_pagamentos = ttk.Frame(container_direita)
        frame_resumo_pagamentos.grid(row=6, column=0, sticky="ew", pady=(10,5))
        frame_resumo_pagamentos.columnconfigure(0, weight=1)
        ttk.Label(frame_resumo_pagamentos, text="Pagamentos Realizados:").grid(row=0, column=0, sticky="w")
        self.lista_pagamentos = tk.Listbox(frame_resumo_pagamentos, height=4)
        self.lista_pagamentos.grid(row=1, column=0, sticky="ew")
        ttk.Button(frame_resumo_pagamentos, text="Limpar Pagamentos", command=self.limpar_pagamentos, bootstyle=(SECONDARY, OUTLINE)).grid(row=2, column=0, sticky="ew", pady=(5,0))
        self.label_troco = ttk.Label(frame_resumo_pagamentos, text="", bootstyle="info", font=("Arial", 12, "bold"))
        self.label_troco.grid(row=3, column=0, sticky="e", pady=(5,0))

        # Opções com Checkbox
        frame_opcoes_finais = ttk.Frame(container_direita)
        frame_opcoes_finais.grid(row=7, column=0, sticky="ew", pady=5)
        chk_imprimir = ttk.Checkbutton(frame_opcoes_finais, text="Imprimir Ticket de Troca", variable=self.imprimir_ticket_var)
        chk_imprimir.pack()

        # Seção de Ações Finais
        frame_acoes = ttk.Frame(container_direita)
        frame_acoes.grid(row=8, column=0, sticky="ew", pady=(10, 0))
        frame_acoes.columnconfigure((0, 1), weight=1)
        ttk.Button(frame_acoes, text="CANCELAR VENDA", command=self.tela_selecao_vendedor, bootstyle=SECONDARY).grid(row=0, column=0, sticky="ew", padx=(0, 5), ipady=10)
        self.btn_finalizar = ttk.Button(frame_acoes, text="FINALIZAR VENDA", command=self.finalizar_venda)
        self.btn_finalizar.grid(row=0, column=1, sticky="ew", padx=(5, 0), ipady=10)

        # Garante que, ao voltar da edição do cliente, o estado da venda seja reaplicado na tela.

        # 1. Re-exibe os produtos que já estão na memória
        self.exibir_produtos()

        # 2. Re-exibe os pagamentos que já foram feitos
        self.exibir_pagamentos()

        # 3. RECALCULA E ATUALIZA TODOS OS TOTAIS E O VALOR A PAGAR
        self.atualizar_total()

        # 4. Se já houver pagamentos, desativa novamente o campo de desconto
        if self.pagamentos:
            self.entry_desconto.config(state="disabled")
            self.btn_aplicar_desconto.config(state="disabled")

    def atualizar_total(self):
        subtotal = 0.0
        for produto in self.produtos_na_venda:
            subtotal += produto['preco']
        
        self.total_compra = subtotal - self.desconto_aplicado_valor

        # Atualiza os labels na tela
        self.subtotal_label.config(text=f"R$ {subtotal:.2f}")
        self.desconto_label.config(text=f"- R$ {self.desconto_aplicado_valor:.2f} ({self.desconto_aplicado_info})")
        self.total_label.config(text=f"R$ {self.total_compra:.2f}")

        # Recalcula o valor restante com base nos pagamentos já feitos
        total_pago = sum(p['valor'] for p in self.pagamentos)
        self.valor_restante = self.total_compra - total_pago
        
        self.valor_editavel.delete(0, tk.END)
        self.valor_editavel.insert(0, f"{self.valor_restante:.2f}")

    def adicionar_produto(self):
        self._limpar_pagamentos_e_descontos_se_necessario()

        sku_digitado = self.produto_var.get()
        if not sku_digitado:
            return

        produto_db = buscar_produto_por_sku_ou_bipe(sku_digitado)
        
        if produto_db:
            novo_produto = {
                'id': produto_db['pro_id'], # Guarda o ID do produto
                'nome': produto_db['pro_descricao'],
                'codigo': produto_db['pro_sku'],
                'bipe': produto_db.get('pro_bipe'),
                'tamanho': produto_db['pro_tam'],
                'preco': float(produto_db['pro_valor'])
            }
            self.produtos_na_venda.append(novo_produto)
            self.exibir_produtos()
            self.atualizar_total()
            self.produto_var.set("")
        else:
            messagebox.showerror("Erro", f"Produto com SKU '{sku_digitado}' não encontrado.", parent=self.janela_pdv)
    
    def processar_produto_event(self, event=None):
        """Função chamada pelo evento da tecla Enter para executar a ação do modo atual."""
        self.processar_produto_entry()

    def remover_produto(self):
        """Remove um produto da venda pelo SKU ou Bipe digitado."""
        self._limpar_pagamentos_e_descontos_se_necessario()

        codigo_para_remover = self.produto_var.get().strip().upper()
        
        if not codigo_para_remover:
            messagebox.showwarning("Atenção", "Digite o SKU ou Bipe do produto a ser removido.", parent=self.janela_pdv)
            return

        produto_encontrado = None
        # Procura o produto na lista da venda atual pelo SKU ou Bipe
        for produto in self.produtos_na_venda:
            sku_do_produto = produto.get('codigo', '').upper()
            bipe_do_produto = str(produto.get('bipe', '')).upper() # str() para tratar caso o bipe seja None

            if sku_do_produto == codigo_para_remover or bipe_do_produto == codigo_para_remover:
                produto_encontrado = produto
                break
        
        if produto_encontrado:
            self.produtos_na_venda.remove(produto_encontrado)
            messagebox.showinfo("Sucesso", f"Produto com código '{codigo_para_remover}' removido.", parent=self.janela_pdv)
        else:
            messagebox.showerror("Erro", f"Produto com código '{codigo_para_remover}' não encontrado na venda atual.", parent=self.janela_pdv)
            
        # Atualiza a tela
        self.exibir_produtos()
        self.atualizar_total()
        self.produto_var.set("")

    def devolver_produto(self):
        """Busca um produto no banco pelo SKU e o adiciona como devolução."""
        self._limpar_pagamentos_e_descontos_se_necessario()

        sku_devolvido = self.produto_var.get().strip().upper()
        if not sku_devolvido:
            messagebox.showwarning("Atenção", "Digite o SKU do produto a ser devolvido.", parent=self.janela_pdv)
            return

        # Busca o produto no banco de dados para pegar suas informações reais
        produto_db = buscar_produto_por_sku_ou_bipe(sku_devolvido)

        if produto_db:
            # Pega o preço real do produto do banco de dados
            preco = float(produto_db['pro_valor'])

            # Cria o dicionário do produto devolvido com preço negativo
            produto_devolvido = {
                'id': produto_db['pro_id'],
                'nome': f"[DEVOLUÇÃO] {produto_db['pro_descricao']}",
                'codigo': produto_db['pro_sku'],
                'tamanho': produto_db['pro_tam'],
                'preco': -preco # O preço é negativo para abater do subtotal
            }
            
            self.produtos_na_venda.append(produto_devolvido)
            
            # Apenas atualizamos a tela
            self.exibir_produtos()
            self.atualizar_total()
            self.produto_var.set("")
        else:
            messagebox.showerror("Erro", f"Produto com SKU '{sku_devolvido}' não encontrado.", parent=self.janela_pdv)

    def obter_valor_restante(self):
        try:
            return float(self.valor_editavel.get())
        except ValueError:
            return 0.0

    def registrar_pagamento(self, forma, valor, detalhes={}):
        """Registra um pagamento como um dicionário, incluindo detalhes."""
        self.pagamentos.append({
            "forma": forma,
            "valor": valor,
            "detalhes": detalhes
        })
        self.exibir_pagamentos()

        self.valor_restante -= valor
        self.valor_restante = max(self.valor_restante, 0.0)

        self.valor_editavel.delete(0, tk.END)
        self.valor_editavel.insert(0, f"{self.valor_restante:.2f}")

        if hasattr(self, 'entry_desconto'):
            self.entry_desconto.config(state="disabled")
            self.btn_aplicar_desconto.config(state="disabled")

    def exibir_produtos(self):
        # Limpa o treeview antes de preencher
        for i in self.tvw_produtos.get_children():
            self.tvw_produtos.delete(i)
        
        # Preenche o treeview com os dados da nossa lista em memória
        for produto in self.produtos_na_venda:
            self.tvw_produtos.insert('', tk.END, values=(
                produto['nome'],
                produto['codigo'],
                produto['tamanho'],
                f"{produto['preco']:.2f}"
            ))

    def exibir_pagamentos(self):
        self.lista_pagamentos.delete(0, tk.END)
        for pag in self.pagamentos:
            texto = f"- {pag['forma']}: R$ {pag['valor']:.2f}"
            detalhes = pag.get('detalhes', {})
            if pag['forma'] == 'Crédito':
                texto += f" ({detalhes.get('parcelas')}x {detalhes.get('bandeira')})"
            elif pag['forma'] == 'Débito':
                texto += f" ({detalhes.get('bandeira')})"
            self.lista_pagamentos.insert(tk.END, texto)

    def limpar_pagamentos(self):
        self.pagamentos = []
        self.valor_restante = self.total_compra
        self.valor_editavel.delete(0, tk.END)
        self.valor_editavel.insert(0, f"{self.valor_restante:.2f}")
        self.exibir_pagamentos()
        self.label_troco.config(text="")
        self._limpar_detalhes_pagamento() # Limpa os detalhes do cartão

        if self.desconto_aplicado_valor == 0 and hasattr(self, 'entry_desconto'):
            self.entry_desconto.config(state="normal")
            self.btn_aplicar_desconto.config(state="normal")
    
    def _limpar_pagamentos_e_descontos_se_necessario(self):
        """Verifica se existem pagamentos ou descontos e os limpa, avisando o usuário."""
        if self.pagamentos or self.desconto_aplicado_valor > 0:
            self.limpar_desconto()
            self.limpar_pagamentos()

    def limpar_desconto(self):
        # Só faz algo se um desconto estiver ativo
        if self.desconto_aplicado_valor > 0:
            self.desconto_aplicado_valor = 0.0
            self.desconto_aplicado_info = ""
            
            # Recalcula o total e atualiza a tela
            self.atualizar_total()
            
            # SÓ reativa os campos se NENHUM pagamento foi feito
            if not self.pagamentos:
                self.entry_desconto.config(state="normal")
                self.entry_desconto.delete(0, tk.END)
                self.btn_aplicar_desconto.config(state="normal")
            
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
        self._limpar_detalhes_pagamento()
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
        troco = 0.0

        if valor_pago >= valor_restante:
            troco = valor_pago - valor_restante
            self.calcular_troco(valor_pago, valor_restante)
            detalhes_pagamento = {"troco": troco}
            self.registrar_pagamento("Dinheiro", valor_restante, detalhes_pagamento)
        else:
            self.label_troco.config(text="")
            self.registrar_pagamento("Dinheiro", valor_pago) # Pagamento parcial, sem detalhes
    
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
        if round(valor_pago, 2) > round(self.valor_restante, 2):
            messagebox.showerror("Erro", f"O valor do pagamento (R$ {valor_pago:.2f}) não pode ser maior que o valor restante (R$ {self.valor_restante:.2f}).", parent=self.janela_pdv)
            return

        # 2. Limpa o frame de detalhes e desenha a nova interface
        self._limpar_detalhes_pagamento()
        
        ttk.Label(self.frame_detalhes_pagamento, text="Bandeira:").pack(side=LEFT, padx=5)
        cmb = ttk.Combobox(self.frame_detalhes_pagamento, values=self.bandeiras, state="readonly", width=15)
        cmb.pack(side=LEFT, padx=5)

        def confirmar():
            bandeira = cmb.get()
            if bandeira:
                detalhes_pagamento = {"bandeira": bandeira}
                self.registrar_pagamento("Débito", valor_pago, detalhes_pagamento)
                self._limpar_detalhes_pagamento()

        ttk.Button(self.frame_detalhes_pagamento, text="Confirmar", command=confirmar).pack(side=LEFT, padx=5)

    def pagamento_credito(self):
        # 1. Pega e valida o valor
        valor_str = self.valor_editavel.get()
        try:
            valor_pago = float(valor_str.replace(",", "."))
        except ValueError:
            messagebox.showerror("Erro", "Valor de pagamento inválido.", parent=self.janela_pdv)
            return

        if valor_pago <= 0:
            messagebox.showerror("Erro", "O valor do pagamento deve ser maior que zero.", parent=self.janela_pdv)
            return
        if round(valor_pago, 2) > round(self.valor_restante, 2):
            messagebox.showerror("Erro", f"O valor do pagamento (R$ {valor_pago:.2f}) não pode ser maior que o valor restante (R$ {self.valor_restante:.2f}).", parent=self.janela_pdv)
            return

        # 2. Limpa o frame de detalhes e desenha a nova interface
        self._limpar_detalhes_pagamento()

        ttk.Label(self.frame_detalhes_pagamento, text="Bandeira:").pack(side=LEFT, padx=5)
        cmb = ttk.Combobox(self.frame_detalhes_pagamento, values=self.bandeiras, state="readonly", width=12)
        cmb.pack(side=LEFT, padx=5)

        ttk.Label(self.frame_detalhes_pagamento, text="Parcelas:").pack(side=LEFT, padx=5)
        spin = ttk.Spinbox(self.frame_detalhes_pagamento, from_=1, to=6, width=5)
        spin.pack(side=LEFT, padx=5)

        def confirmar():
            bandeira = cmb.get()
            parcelas = spin.get()
            if bandeira and parcelas:
                detalhes_pagamento = {"bandeira": bandeira, "parcelas": int(parcelas)}
                self.registrar_pagamento("Crédito", valor_pago, detalhes_pagamento)
                self._limpar_detalhes_pagamento()

        ttk.Button(self.frame_detalhes_pagamento, text="Confirmar", command=confirmar).pack(side=LEFT, padx=5)

    def pagamento_pix(self):
        self._limpar_detalhes_pagamento()
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
        if round(valor_pago, 2) > round(self.valor_restante, 2):
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

            # Bloco do Produto
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

            c.line(0.5*cm, 1.4*cm, largura_recibo - 0.5*cm, 1.4*cm)
            c.setFont("Helvetica-Oblique", 7)
            c.drawCentredString(largura_recibo / 2.0, 0.9*cm, "NÃO É DOCUMENTO FISCAL")
            c.setFont("Helvetica-Oblique", 7)
            c.drawCentredString(largura_recibo / 2.0, 0.5*cm, "Válido para trocas em até 30 dias da data da compra.")

            c.save()
            return True

        except Exception as e:
            print(f"ERRO ao gerar PDF para o item {item_para_troca['nome']}: {e}")
            return False

    def finalizar_venda(self):
        # Validações iniciais (se há produtos e se a conta foi paga)
        if self.total_compra < 0 or not self.produtos_na_venda:
            messagebox.showwarning("Venda inválida", "Nenhum produto adicionado.", parent=self.janela_pdv)
            return

        if self.valor_restante > 0.009: 
            messagebox.showerror("Erro", "Ainda há valor pendente de pagamento.", parent=self.janela_pdv)
            return

        # Monta um dicionário completo com os dados da venda para o banco de dados
        dados_da_venda = {
            "vendedor_id": self.vendedor_selecionado_id,
            "cliente": self.dados_cliente,
            "total": self.total_compra,
            "produtos_obj": self.produtos_na_venda, # Passa a lista completa de objetos de produto
            "pagamentos": self.pagamentos,
            "desconto": self.desconto_aplicado_info
            # O ID da venda e a data serão gerados pelo banco de dados
        }
        
        # Chama a função do CRUD para salvar tudo no banco de dados
        if salvar_venda_completa(dados_da_venda):
            # Se a venda foi salva com sucesso no banco...
            messagebox.showinfo("Sucesso", "Venda realizada!", parent=self.janela_pdv)
            # CALLBACK PARA ATUALIZAR O INVENTÁRIO:
            if self.callback_venda_finalizada:
                self.callback_venda_finalizada(self.produtos_na_venda)
            
            # Gera os tickets de troca, se o checkbox estiver marcado
            if self.imprimir_ticket_var.get():
                data_atual = datetime.now().strftime("%d/%m/%Y")
                
                # Gerando os múltiplos PDFs dos tickets de troca
                for produto in self.produtos_na_venda:
                    if produto['preco'] > 0: # Não gera ticket para devoluções
                        item_info = {
                            'nome': produto['nome'],
                            'codigo': produto['codigo'],
                            'tamanho': produto['tamanho']
                        }
                        self.gerar_ticket_troca_pdf(item_info, self.vendedor_selecionado, data_atual)
            
            # Prepara os itens para a tela de resumo
            self.itens_venda = [p['nome'] for p in self.produtos_na_venda]
            
            # Navega para a tela de resumo da venda
            self.tela_resumo_venda()
        else:
            # Se a função do CRUD retornar False, significa que houve um erro
            messagebox.showerror("Falha", "Não foi possível salvar a venda. Tente novamente.")
    
    def tela_resumo_venda(self):
        self.limpar_frame()
        self.frame_atual = ttk.Frame(self.janela_pdv)
        self.frame_atual.pack(padx=20, pady=20, fill=BOTH, expand=True)

        ttk.Label(self.frame_atual, text="Resumo da Venda", font=("Arial", 16)).pack(pady=10)

        ttk.Label(self.frame_atual, text=f"Vendedor: {self.vendedor_selecionado}").pack(pady=2, anchor="w")
        ttk.Label(self.frame_atual, text=f"Cliente: {self.dados_cliente.get('nome', '---')}").pack(pady=2, anchor="w")
        ttk.Label(self.frame_atual, text=f"CPF: {self.dados_cliente.get('cpf', '---')}").pack(pady=2, anchor="w")

        ttk.Label(self.frame_atual, text="Produtos:", font=("Arial", 12, "bold")).pack(pady=5, anchor="w")
        produtos_list = tk.Listbox(self.frame_atual, height=5)
        produtos_list.pack(fill=X, expand=True) # Melhorado para preencher o espaço
        for p in self.itens_venda:
            produtos_list.insert(tk.END, p)

        ttk.Label(self.frame_atual, text="Pagamentos:", font=("Arial", 12, "bold")).pack(pady=5, anchor="w")
        pagamentos_list = tk.Listbox(self.frame_atual, height=3)
        pagamentos_list.pack(fill=X, expand=True)

        for pag in self.pagamentos:
            texto = f"- {pag['forma']}: R$ {pag['valor']:.2f}"
            detalhes = pag.get('detalhes', {})
            if pag['forma'] == 'Crédito':
                texto += f" ({detalhes.get('parcelas')}x {detalhes.get('bandeira')})"
            elif pag['forma'] == 'Débito':
                texto += f" ({detalhes.get('bandeira')})"
            pagamentos_list.insert(tk.END, texto)

        ttk.Label(self.frame_atual, text=f"Total Pago: R$ {self.total_compra:.2f}", font=("Arial", 12, "bold")).pack(pady=10, anchor="w")

        ttk.Button(self.frame_atual, text="Nova Venda", command=self.tela_selecao_vendedor).pack(pady=10) # Para iniciar uma nova venda, abre outra janela de PDV ou reinicia a atual
        ttk.Button(self.frame_atual, text="Fechar PDV", command=self.janela_pdv.destroy).pack(pady=5) # Adicionado botão para fechar apenas o PDV

    def _limpar_detalhes_pagamento(self):
        """Função auxiliar para limpar o frame de detalhes."""
        for widget in self.frame_detalhes_pagamento.winfo_children():
            widget.destroy()