# conexao.py
import mysql.connector
from mysql.connector import errorcode
from tkinter import messagebox

def conectar():
    """
    Função para conectar ao banco de dados MySQL.
    Retorna o objeto de conexão ou None em caso de falha.
    """
    try:
        conexao = mysql.connector.connect(
            host='localhost',       # Ou o IP do seu servidor de banco de dados
            user='root',     # Seu usuário do MySQL
            password='root',   # Sua senha do MySQL
            database='CHECKPOINT'   # O nome do banco de dados que você criou
        )
        return conexao
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            messagebox.showerror("Erro de Conexão", "Acesso negado. Verifique seu usuário e senha do MySQL.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            messagebox.showerror("Erro de Conexão", "O banco de dados 'CHECKPOINT' não foi encontrado.")
        else:
            messagebox.showerror("Erro de Conexão", f"Ocorreu um erro: {err}")
        return None