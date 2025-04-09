import sqlite3
import os

def conectar():
    caminho = os.path.join(os.path.dirname(__file__), r"..\banco_dados\checkp.db")
    conexao = sqlite3.connect(caminho)
    return conexao
