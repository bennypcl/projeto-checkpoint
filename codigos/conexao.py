import sqlite3

def conectar():
    conexao = sqlite3.connect(r"C:\Users\André Gustavo Castro\OneDrive\Documentos\CHECKPOINT\projeto-checkpoint\banco_dados\checkp.db")
    return conexao
