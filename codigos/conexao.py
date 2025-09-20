import mysql.connector
from mysql.connector import errorcode
from tkinter import messagebox

def conectar():
    """
    Função para conectar ao banco de dados.
    Retorna o objeto de conexão ou None em caso de falha.
    """
    try:
        conexao = mysql.connector.connect(
            host='localhost',       # ou o IP do servidor de banco de dados
            user='root',     # usuário do MySQL
            password='root',   # senha do MySQL
            database='CHECKPOINT'   # nome do banco de dados
        )
        return conexao
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            messagebox.showerror("Erro de Conexão", "Acesso negado. Por favor, reinicie o computador e tente abrir o programa novamente.\nSe o erro persistir, contate o suporte técnico.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            messagebox.showerror("Erro de Conexão", "Não foi possível acessar os dados do sistema.\nPor favor, reinicie o computador e tente abrir o programa novamente.\nSe o erro persistir, contate o suporte técnico.")
        else:
            messagebox.showerror("Erro de Conexão", f"Ocorreu um erro: {err}.\nPor favor, reinicie o programa e tente novamente. Se o problema persistir, contate o suporte técnico.")
        return None